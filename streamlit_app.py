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

    def display_basic_stats(df):
        """Exibir um resumo estatístico básico dos dados filtrados."""
        st.header("Estatísticas Básicas")
        st.write("Aqui estão algumas estatísticas descritivas dos dados filtrados:")

        total_registros = len(df)
        media_pontos = df['número de pontos'].mean()
        mediana_pontos = df['número de pontos'].median()
        desvio_padrao = df['número de pontos'].std()
        max_pontos = df['número de pontos'].max()
        min_pontos = df['número de pontos'].min()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Registros", total_registros)
        col2.metric("Média de Pontos", f"{media_pontos:,.2f}")
        col3.metric("Mediana de Pontos", f"{mediana_pontos:,.2f}")
        col4.metric("Desvio Padrão", f"{desvio_padrao:,.2f}")

        st.write(f"Máximo de Pontos: {max_pontos}")
        st.write(f"Mínimo de Pontos: {min_pontos}")

    def display_growth_rate(df):
        """Exibir a taxa de crescimento do número de pontos ao longo do tempo."""
        st.header("Taxa de Crescimento")

        df = df.sort_values(by="data")
        df['crescimento diário (%)'] = df['número de pontos'].pct_change() * 100

        crescimento_medio = df['crescimento diário (%)'].mean()
        crescimento_total = (df['número de pontos'].iloc[-1] - df['número de pontos'].iloc[0]) / df['número de pontos'].iloc[0] * 100

        st.write(f"Crescimento total no período: **{crescimento_total:.2f}%**")
        st.write(f"Crescimento médio diário: **{crescimento_medio:.2f}%**")
        
        fig = px.line(df, x='data', y='crescimento diário (%)', title="Crescimento Diário (%)")
        st.plotly_chart(fig)

    def display_histogram(df):
        """Exibir um histograma da distribuição de 'número de pontos'."""
        st.header("Distribuição do Número de Pontos")
        fig = px.histogram(df, x='número de pontos', nbins=30, title="Distribuição do Número de Pontos")
        st.plotly_chart(fig)

    def display_correlation(df):
        """Exibir a correlação entre 'número de pontos' e outras variáveis numéricas."""
        st.header("Correlação entre Variáveis")

        # Selecionar apenas colunas numéricas para calcular a correlação
        df_numeric = df.select_dtypes(include=['float64', 'int64'])

        if df_numeric.shape[1] > 1:  # Verificar se há mais de uma coluna numérica
            corr = df_numeric.corr()
            st.write(corr)
            fig = px.imshow(corr, text_auto=True, title="Matriz de Correlação")
            st.plotly_chart(fig)
        else:
            st.info("Não há variáveis numéricas suficientes para calcular a correlação.")

    def detect_outliers(df):
        """Detectar outliers no número de pontos usando o método IQR."""
        st.header("Outliers no Número de Pontos")

        q1 = df['número de pontos'].quantile(0.25)
        q3 = df['número de pontos'].quantile(0.75)
        iqr = q3 - q1  # Intervalo interquartil

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = df[(df['número de pontos'] < lower_bound) | (df['número de pontos'] > upper_bound)]
        
        if not outliers.empty:
            st.warning(f"Foram encontrados {len(outliers)} outliers.")
            st.dataframe(outliers)
        else:
            st.info("Nenhum outlier detectado.")

    def display_boxplot(df):
        """Exibir um boxplot para o número de pontos."""
        st.header("Boxplot do Número de Pontos")
        fig = px.box(df, x='imagem', y='número de pontos', points="all", title="Boxplot por Imagem")
        st.plotly_chart(fig)

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
            display_basic_stats(filtered_df)
            display_growth_rate(filtered_df)
            display_histogram(filtered_df)
            display_correlation(filtered_df)
            detect_outliers(filtered_df)
            display_boxplot(filtered_df)

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
