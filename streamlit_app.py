import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import unicodedata
from datetime import datetime

# --------------------------
# Funções Auxiliares
# --------------------------

def remove_accents(input_str):
    """Remove acentos de uma string."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_column_names(df):
    """Remove acentos e converte os nomes das colunas para minúsculas."""
    df.columns = [remove_accents(col).lower().replace(' ', '_') for col in df.columns]
    return df

def hash_password(password):
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    """Verifica as credenciais do usuário."""
    users = {
        "projeto": hash_password("FITEC_MA"),
        "eduardo": hash_password("FITEC321")
    }
    hashed_input_password = hash_password(password)
    if username.lower() in users and users[username.lower()] == hashed_input_password:
        return True
    return False

def local_css(file_name):
    """Injeta CSS personalizado no aplicativo Streamlit."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"O arquivo {file_name} não foi encontrado.")

def display_simple_estimate(df):
    """Exibe uma projeção simples baseada na média de pontos diários para uma data futura específica."""
    st.header("📊 Projeção de Pontos para Datas Específicas")
    st.markdown("---")
    
    # Calcular a média de pontos diária com base nos dados existentes
    media_pontos_diaria = df['numero_de_pontos'].mean()

    # Input para o usuário inserir a data futura
    data_futura = st.date_input("Selecione uma data futura para projeção", value=pd.Timestamp("2024-10-30"))

    # Calcular o número de dias úteis entre a data mais recente no DataFrame e a data futura
    ultima_data = df['data'].max()
    dias_uteis = pd.date_range(start=ultima_data, end=data_futura, freq='B')  # freq='B' considera apenas dias úteis
    num_dias_uteis = len(dias_uteis)
    
    # Calcular a projeção de pontos
    estimativa_pontos = media_pontos_diaria * num_dias_uteis

    # Exibir a média de pontos diários e a projeção de pontos
    col1, col2 = st.columns(2)
    col1.metric("Média de Pontos Diários", f"{media_pontos_diaria:,.2f}")
    col2.metric(f"Estimativa de Pontos em {data_futura.strftime('%Y-%m-%d')}", f"{estimativa_pontos:,.0f} pontos")

    st.markdown(f"Serão considerados **{num_dias_uteis} dias úteis** entre a data atual e {data_futura.strftime('%Y-%m-%d')}.")

def apply_filters(df):
    """Aplica filtro de data ao DataFrame."""
    st.sidebar.markdown("### Filtros de Data")
    min_value = df['data'].min().date()
    max_value = df['data'].max().date()
    from_date, to_date = st.sidebar.date_input('Intervalo de datas:', [min_value, max_value], min_value=min_value, max_value=max_value)
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    df = df[(df['data'] >= from_date) & (df['data'] <= to_date)]

    if df.empty:
        st.warning("Nenhum dado encontrado para o intervalo de datas selecionado.")
    
    return df

def display_basic_stats(df, meta=100000):
    """Exibe um resumo estatístico básico dos dados filtrados, incluindo indicadores de meta."""
    st.header("📈 Estatísticas Básicas")
    st.markdown("---")
    st.write("Aqui estão algumas estatísticas descritivas dos dados filtrados:")

    total_registros = len(df)
    media_pontos = df['numero_de_pontos'].mean()
    mediana_pontos = df['numero_de_pontos'].median()
    desvio_padrao = df['numero_de_pontos'].std()
    max_pontos = df['numero_de_pontos'].max()
    min_pontos = df['numero_de_pontos'].min()

    # Cálculos para a meta
    total_pontos = df['numero_de_pontos'].sum()
    pontos_restantes = meta - total_pontos if meta > total_pontos else 0
    percentual_atingido = (total_pontos / meta) * 100 if meta > 0 else 0

    # Exibir métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", total_registros)
    col2.metric("Média de Pontos", f"{media_pontos:,.2f}")
    col3.metric("Desvio Padrão", f"{desvio_padrao:,.2f}")

    st.write(f"**Mediana de Pontos**: {mediana_pontos:,.2f}")
    st.write(f"**Máximo de Pontos**: {max_pontos}")
    st.write(f"**Mínimo de Pontos**: {min_pontos}")

    st.markdown("---")
    st.header("🎯 Progresso da Meta de Pontos")

    # Exibir indicadores da meta
    col_meta1, col_meta2, col_meta3 = st.columns(3)
    col_meta1.metric("Meta de Pontos", f"{meta:,.0f}")
    col_meta2.metric("Pontos Realizados", f"{total_pontos:,.0f}")
    col_meta3.metric("Pontos Restantes", f"{pontos_restantes:,.0f}")

    # Exibir percentual atingido
    st.subheader(f"Percentual Atingido: {percentual_atingido:.2f}%")
    st.progress((percentual_atingido / 100) if percentual_atingido <= 100 else 1.0)

    if percentual_atingido >= 100:
        st.success("🎉 Meta Alcançada!")
    else:
        st.info("Continue trabalhando para alcançar a meta!")

def display_chart(df):
    """Exibe gráfico interativo do número de pontos ao longo do tempo."""
    st.header('📈 Número de Pontos ao Longo do Tempo')
    st.markdown("---")

    fig = px.line(df, x='data', y='numero_de_pontos', color='imagem', markers=True, title="Evolução do Número de Pontos ao Longo do Tempo", template='plotly_dark')
    fig.update_layout(xaxis_title="Data", yaxis_title="Número de Pontos", legend_title="Imagem", hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    st.plotly_chart(fig, use_container_width=True)

def display_growth_rate_histogram(df):
    """Exibe um histograma da taxa de crescimento diária."""
    st.header("📈 Taxa de Crescimento")
    st.markdown("---")

    df = df.sort_values(by="data")
    df['crescimento_diario_percent'] = df['numero_de_pontos'].pct_change() * 100

    crescimento_medio = df['crescimento_diario_percent'].mean()
    crescimento_total = (df['numero_de_pontos'].iloc[-1] - df['numero_de_pontos'].iloc[0]) / df['numero_de_pontos'].iloc[0] * 100

    st.write(f"Crescimento total no período: **{crescimento_total:.2f}%**")
    st.write(f"Crescimento médio diário: **{crescimento_medio:.2f}%**")
    
    # Exibir histograma da taxa de crescimento diária
    fig = px.histogram(df, x='crescimento_diario_percent', nbins=30, title="Distribuição da Taxa de Crescimento Diário (%)", template='plotly_dark')
    fig.update_layout(xaxis_title="Taxa de Crescimento Diário (%)", yaxis_title="Frequência", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Configuração da Página
# --------------------------

st.set_page_config(
    page_title='Dashboard FITec',
    page_icon='📈',  # Ícone de gráfico
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': 'Dashboard FITec v1.0'
    }
)

# Injetar CSS personalizado
local_css("styles.css")  # Assegure-se de criar este arquivo com seus estilos

# URL do logotipo
logo_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/FITec.svg"

# Exibir logotipo na barra lateral
st.sidebar.image(logo_url, use_column_width=True)
st.sidebar.title("Dashboard FITec")

# Inicializa o estado de login na sessão
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

# --------------------------
# Tela de Login
# --------------------------

if not st.session_state['login_status']:
    st.title("Login no Dashboard FITec 📊")
    st.image(logo_url, width=300)  # Exibe o logo na página principal
    username = st.text_input("Nome de usuário", key="username")
    password = st.text_input("Senha", type="password", key="password")
    
    # Botão de login com ícone
    if st.button("🔑 Acessar o Dashboard"):
        with st.spinner("Verificando credenciais..."):
            if login(username, password):
                st.session_state['login_status'] = True
                st.success(f"Bem-vindo, {username}!")
            else:
                st.error("Nome de usuário ou senha incorretos")
else:
    # --------------------------
    # Dashboard Principal
    # --------------------------

    # Exibe logotipo na página principal também
    st.image(logo_url, width=150, use_column_width=False)
    
    # Função para carregar dados
    @st.cache_data
    def get_custom_data():
        """Carregar dados CSV personalizados a partir do link no GitHub."""
        csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
        try:
            df = pd.read_csv(csv_url, delimiter=',', on_bad_lines='skip')
            df = normalize_column_names(df)  # Normalizar os nomes das colunas
            return df
        except FileNotFoundError:
            st.error("O arquivo CSV não foi encontrado. Verifique o URL.")
            return pd.DataFrame()
        except pd.errors.ParserError:
            st.error("Erro ao analisar o arquivo CSV. Verifique a formatação.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return pd.DataFrame()

    @st.cache_data
    def convert_df(df):
        """Converter DataFrame em CSV para download."""
        return df.to_csv(index=False).encode('utf-8')

    # Carregar os dados
    with st.spinner('Carregando dados...'):
        data_df = get_custom_data()

    if not data_df.empty:
        # Converter coluna 'data' para datetime e remover linhas com datas inválidas
        data_df['data'] = pd.to_datetime(data_df['data'], format='%Y-%m-%d', errors='coerce')
        data_df = data_df.dropna(subset=['data'])

        # Aplicar filtros (apenas filtro de data)
        filtered_df = apply_filters(data_df)

        if not filtered_df.empty:
            # Exibir métricas principais e indicadores da meta
            display_basic_stats(filtered_df, meta=100000)  # Meta definida como 100.000 pontos
            
            # Exibir gráficos principais em abas para organização
            tab1, tab2, tab3 = st.tabs(["Visão Geral", "Análises Complementares", "Projeção de Pontos"])

            with tab1:
                display_chart(filtered_df)

            with tab2:
                display_growth_rate_histogram(filtered_df)
            
            with tab3:
                display_simple_estimate(filtered_df)  # Nova função de estimativa baseada em média

            # Baixar CSV
            csv = convert_df(filtered_df)
            st.download_button(
                label="📥 Baixar dados filtrados",
                data=csv,
                file_name='dados_filtrados.csv',
                mime='text/csv',
            )

            # Exibir links profissionais no rodapé
            st.markdown("---")
            st.markdown(
                """
                <div style="text-align: center; font-size: 14px;">
                <a href="https://scholar.google.com.br/citations?user=XLu_qAIAAAAJ&hl=pt-BR" target="_blank">Google Acadêmico</a> | 
                <a href="https://www.linkedin.com/in/tiago-holanda-082928141/" target="_blank">LinkedIn</a> | 
                <a href="https://github.com/tiagofholanda" target="_blank">GitHub</a> | 
                <a href="http://lattes.cnpq.br/4969639760120080" target="_blank">Lattes</a> | 
                <a href="https://www.researchgate.net/profile/Tiago_Holanda" target="_blank">ResearchGate</a> | 
                <a href="https://publons.com/researcher/3962699/tiago-holanda/" target="_blank">Publons</a> | 
                <a href="https://orcid.org/0000-0001-6898-5027" target="_blank">ORCID</a> | 
                <a href="https://www.scopus.com/authid/detail.uri?authorId=57376293300" target="_blank">Scopus</a>
                </div>
                """, 
                unsafe_allow_html=True
            )

    else:
        st.error("Os dados não puderam ser carregados.")
