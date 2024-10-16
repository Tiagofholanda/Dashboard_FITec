import streamlit as st
import pandas as pd
import plotly.express as px

# Defina o título e o ícone que aparecerão na aba do navegador.
st.set_page_config(
    page_title='Dashboard FITec',
    page_icon=':bar_chart:',  # Ícone de gráfico
)

# Adicionar o logo da FITec usando SVG via HTML
logo_url = "https://www.fitec.org.br/ProjetoAgro/logo-header.svg"

# Usando markdown com HTML para exibir a imagem SVG
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{logo_url}" alt="Logo FITec" style="width:300px;"/>
    </div>
    """,
    unsafe_allow_html=True
)
# -------------------------------------------------------------------------
# Função para verificar login
def login(username, password):
    # Dicionário de usuários e senhas
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
    if st.button("Login"):
        if login(username, password):
            st.session_state['login_status'] = True
            st.success(f"Bem-vindo, {username}!")
        else:
            st.error("Nome de usuário ou senha incorretos")
else:
    # Se o usuário está logado, exibe o dashboard
    st.title("Dashboard FITec")

    # Botão de logout
    if st.button("Logout"):
        st.session_state['login_status'] = False
        st.info("Você saiu do sistema.")
    
    # -------------------------------------------------------------------------
    # Funções úteis declaradas
    @st.cache_data
    def get_custom_data():
        """Carregar dados CSV personalizados a partir do link no GitHub."""
        # Link "raw" do arquivo CSV no GitHub
        csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
        try:
            df = pd.read_csv(csv_url, delimiter=',', on_bad_lines='skip')
        except FileNotFoundError:
            st.error("O arquivo CSV não foi encontrado. Verifique o URL.")
            return pd.DataFrame()  # Retornar DataFrame vazio
        except pd.errors.ParserError:
            st.error("Erro ao analisar o arquivo CSV. Verifique a formatação.")
            return pd.DataFrame()  # Retornar DataFrame vazio
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return pd.DataFrame()  # Retornar DataFrame vazio
        return df

    @st.cache_data
    def convert_df(df):
        """Converter DataFrame em CSV para download."""
        return df.to_csv().encode('utf-8')

    def apply_filters(df):
        """Aplicar filtros de data, cidade, número de pontos e imagem."""
        min_value = df['data'].min().date()
        max_value = df['data'].max().date()
        from_date, to_date = st.date_input(
            'Qual intervalo de datas você deseja ver?',
            [min_value, max_value],
            min_value=min_value,
            max_value=max_value
        )
        from_date = pd.to_datetime(from_date)
        to_date = pd.to_datetime(to_date)
        df = df[(df['data'] >= from_date) & (df['data'] <= to_date)]

        top_cities = df['cidade'].value_counts().index[:3]
        selected_cities = st.multiselect(
            'Selecione as cidades para visualizar:',
            df['cidade'].unique(),
            default=top_cities
        )
        df = df[df['cidade'].isin(selected_cities)]
        
        if df.empty:
            st.warning("Nenhum dado encontrado para as cidades selecionadas.")
            return df

        min_points = int(df['número de pontos'].min())
        max_points = int(df['número de pontos'].max())
        if min_points < max_points:
            selected_points_range = st.slider(
                'Selecione o intervalo de "número de pontos":',
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

        top_images = df['imagem'].value_counts().index[:3]
        selected_images = st.multiselect(
            'Quais imagens você gostaria de visualizar?',
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

                        if pd.isna(first_points):
                            growth = 'n/a'
                            delta_color = 'off'
                        else:
                            growth = f'{last_points / first_points:,.2f}x'
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
        st.header('Número de pontos ao longo do tempo', divider='gray')

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

    # -------------------------------------------------------------------------
    # Carregar os dados
    data_df = get_custom_data()

    if not data_df.empty:
        data_df['data'] = pd.to_datetime(data_df['data'], format='%Y-%m-%d', errors='coerce')
        data_df = data_df.dropna(subset=['data']) 

        filtered_df = apply_filters(data_df)

        if not filtered_df.empty:
            display_chart(filtered_df)
            from_date = filtered_df['data'].min()
            to_date = filtered_df['data'].max()
            display_metrics(filtered_df, from_date, to_date)

            csv = convert_df(filtered_df)
            st.download_button(
                label="Baixar dados filtrados",
                data=csv,
                file_name='dados_filtrados.csv',
                mime='text/csv',
            )
    else:
        st.error("Os dados não puderam ser carregados.")
