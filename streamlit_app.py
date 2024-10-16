import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página e tema
st.set_page_config(
    page_title='Dashboard FITec',
    page_icon=':bar_chart:',  # Ícone de gráfico
    layout='wide'  # Definir layout como wide
)

# Função para verificar login
def login(username, password):
    users = {"Projeto": "FITEC_MA", "Eduardo": "FITEC321"}  # Adicione mais usuários conforme necessário
    if username in users and users[username] == password:
        return True
    return False

# Inicializa o estado de login na sessão
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

# Se o usuário não está logado, exibe a tela de login
if not st.session_state['login_status']:
    st.title("Login no Dashboard FITec")
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    
    # Botão de login
    if st.button("🔑 Acessar o Dashboard"):
        with st.spinner("Verificando credenciais..."):
            if login(username, password):
                st.session_state['login_status'] = True
                st.success(f"Bem-vindo, {username}!")
            else:
                st.error("Nome de usuário ou senha incorretos")
else:
    # Se o usuário está logado, exibe o dashboard
    st.sidebar.title("Navegação")
    st.sidebar.markdown("Use os filtros para personalizar os dados:")

    # Botão de logout
    if st.sidebar.button("🔒 Sair do Sistema"):
        st.session_state['login_status'] = False
        st.sidebar.info("Você saiu do sistema.")

    # Funções úteis declaradas
    @st.cache_data
    def get_custom_data():
        """Carregar dados CSV personalizados a partir do link no GitHub."""
        csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
        try:
            df = pd.read_csv(csv_url, delimiter=',', on_bad_lines='skip')
        except FileNotFoundError:
            st.error("O arquivo CSV não foi encontrado. Verifique o URL.")
            return pd.DataFrame()
        except pd.errors.ParserError:
            st.error("Erro ao analisar o arquivo CSV. Verifique a formatação.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return pd.DataFrame()
        return df

    @st.cache_data
    def convert_df(df):
        """Converter DataFrame em CSV para download."""
        return df.to_csv().encode('utf-8')

    def apply_filters(df):
        """Aplicar filtros de data, cidade, número de pontos e imagem."""
        st.sidebar.markdown("### Filtros de Data")
        min_value = df['data'].min().date()
        max_value = df['data'].max().date()
        from_date, to_date = st.sidebar.date_input(
            'Intervalo de datas:',
            [min_value, max_value],
            min_value=min_value,
            max_value=max_value
        )
        from_date = pd.to_datetime(from_date)
        to_date = pd.to_datetime(to_date)
        df = df[(df['data'] >= from_date) & (df['data'] <= to_date)]

        st.sidebar.markdown("### Filtros de Cidades")
        top_cities = df['cidade'].value_counts().index[:3]
        selected_cities = st.sidebar.multiselect(
            'Selecione as cidades:',
            df['cidade'].unique(),
            default=top_cities
        )
        df = df[df['cidade'].isin(selected_cities)]

        if df.empty:
            st.warning("Nenhum dado encontrado para as cidades selecionadas.")
            return df

        st.sidebar.markdown("### Filtro de Número de Pontos")
        min_points = int(df['número de pontos'].min())
        max_points = int(df['número de pontos'].max())
        if min_points < max_points:
            selected_points_range = st.sidebar.slider(
                'Intervalo de "número de pontos":',
                min_value=min_points,
                max_value=max_points,
                value=(min_points, max_points)
            )
            df = df[
                (df['número de pontos'] >= selected_points_range[0]) & 
                (df['número de pontos'] <= selected_points_range[1])
            ]
        else:
            st.info(f'Todos os valores de "número de pontos" são {min_points}. Nenhum intervalo disponível.')

        if df.empty:
            st.warning("Nenhum dado encontrado para o intervalo de pontos selecionado.")
            return df

        st.sidebar.markdown("### Filtro de Imagens")
        top_images = df['imagem'].value_counts().index[:3]
        selected_images = st.sidebar.multiselect(
            'Selecione as imagens:',
            df['imagem'].unique(),
            default=top_images
        )
        df = df[df['imagem'].isin(selected_images)]
        
        if df.empty:
            st.warning("Nenhum dado encontrado para as imagens selecionadas.")
        
        return df

    def display_metrics(df, from_date, to_date):
        """Exibir métricas individuais de número de pontos por imagem."""
        st.header(f'Métricas do Número de pontos em {to_date.strftime("%Y-%m-%d")}', divider='gray')

        cols = st.columns(4)
        for i, image in enumerate(df['imagem'].unique()):
            col = cols[i % len(cols)]
            with col:
                first_row = df[df['data'] == from_date]
                last_row = df[df['data'] == to_date]

                if not first_row.empty and not last_row.empty:
                    if image in first_row['imagem'].values and image in last_row['imagem'].values:
                        first_points = first_row[first_row['imagem'] == image]['número de pontos'].iat[0]
                        last_points = last_row[last_row['imagem'] == image]['número de pontos'].iat[0]
                        growth = f'{last_points / first_points:,.2f}x' if first_points != 0 else 'n/a'
                        delta_color = 'normal'

                        st.metric(
                            label=f'{image} Número de pontos',
                            value=f'{last_points:,.0f}',
                            delta=growth,
                            delta_color=delta_color
                        )
                    else:
                        st.warning(f"A imagem {image} não tem dados para as datas selecionadas.")
                else:
                    st.warning(f"A imagem {image} não tem dados para as datas selecionadas.")

    def display_chart(df):
        """Exibir gráfico interativo do número de pontos ao longo do tempo."""
        st.header('Número de pontos ao longo do tempo :chart_with_upwards_trend:', divider='gray')

        df['número de pontos (média móvel)'] = df['número de pontos'].rolling(window=7).mean()

        fig = px.line(df, x='data', y='número de pontos', color='imagem', markers=True,
                      title="Evolução do Número de Pontos ao Longo do Tempo")
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de Pontos",
            legend_title="Imagem",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig)

    # Carregar os dados
    with st.spinner('Carregando dados...'):
        data_df = get_custom_data()

    if not data_df.empty:
        data_df['data'] = pd.to_datetime(data_df['data'], format='%Y-%m-%d', errors='coerce')
        data_df = data_df.dropna(subset=['data'])

        # Aplicar filtros
        filtered_df = apply_filters(data_df)

        if not filtered_df.empty:
            # Exibir gráfico e métricas
            display_chart(filtered_df)
            from_date = filtered_df['data'].min()
            to_date = filtered_df['data'].max()
            display_metrics(filtered_df, from_date, to_date)

            # Baixar CSV
            csv = convert_df(filtered_df)
            st.download_button(
                label="📥 Baixar dados filtrados",
                data=csv,
                file_name='dados_filtrados.csv',
                mime='text/csv',
            )
    else:
        st.error("Os dados não puderam ser carregados.")
