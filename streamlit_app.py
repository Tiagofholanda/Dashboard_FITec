import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import unicodedata
from datetime import datetime
import numpy as np

# --------------------------
# Funções Auxiliares
# --------------------------

def remove_accents(input_str):
    """Remove acentos de uma string."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_column_names(df):
    """Remove acentos e converte os nomes das colunas para minúsculas."""
    df.columns = [remove_accents(col).strip().lower().replace(' ', '_') for col in df.columns]
    return df

def hash_password(password):
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    """Verifica as credenciais do usuário."""
    users = {
        "projeto": hash_password("FITEC_MA"),
        "Eduardo": hash_password("FITEC@2024")
    }
    hash_input_password = hash_password(password)
    if username.lower() in users and users[username.lower()] == hash_input_password:
        return True
    return False

def local_css(file_name):
    """Injeta CSS personalizado no aplicativo Streamlit."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"O arquivo {file_name} não foi encontrado.")

def set_text_color():
    """Define a cor do texto para preto ou branco dependendo do tema."""
    return "black"  # You can adjust this logic for dark/light themes if needed.

# --------------------------
# Adicionando cache para otimizar carregamento de dados
# --------------------------

@st.cache_data
def get_custom_data():
    """Carregar dados CSV personalizados a partir do link no GitHub."""
    csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
    try:
        df = pd.read_csv(csv_url, delimiter=';', on_bad_lines='skip')
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

# --------------------------
# Funções de Exibição de Gráficos e Estatísticas
# --------------------------

def display_chart(df):
    """Exibe gráfico interativo do número de pontos ao longo do tempo, suavizado com uma média móvel de 7 dias."""
    st.header('📊 Evolução do Número de Pontos ao Longo do Tempo (Suavizado)')
    st.markdown("---")

    # Suavizar o gráfico usando média móvel (rolling average) de 7 dias fixo
    df['numero_de_pontos_smooth'] = df['numero_de_pontos'].rolling(window=7, min_periods=1).mean()

    fig = px.line(df, x='data', y='numero_de_pontos_smooth', markers=True, title="Evolução do Número de Pontos (Suavização: 7 dias)", template='plotly_white')
    fig.update_layout(xaxis_title="Data", yaxis_title="Número de Pontos Suavizado", hovermode="x unified", 
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=set_text_color())
    
    st.plotly_chart(fig, use_container_width=True)

def display_basic_stats(df):
    """Exibe um resumo estatístico básico dos dados filtrados, incluindo indicadores de meta."""
    st.header("📈 Estatísticas Básicas")
    st.markdown("---")
    st.write("Aqui estão algumas estatísticas descritivas dos dados:")

    total_registros = len(df)
    media_pontos = df['numero_de_pontos'].mean()
    mediana_pontos = df['numero_de_pontos'].median()
    desvio_padrao = df['numero_de_pontos'].std()
    max_pontos = df['numero_de_pontos'].max()
    min_pontos = df['numero_de_pontos'].min()

    # Exibir métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", total_registros)
    col2.metric("Média de Pontos", f"{media_pontos:,.2f}")
    col3.metric("Desvio Padrão", f"{desvio_padrao:,.2f}")

    st.write(f"**Mediana de Pontos**: {mediana_pontos:,.2f}")
    st.write(f"**Máximo de Pontos**: {max_pontos}")
    st.write(f"**Mínimo de Pontos**: {min_pontos}")

    st.markdown("---")

def display_meta_progress(df):
    """Exibe o progresso da meta de pontos."""
    st.header("🎯 Progresso da Meta de Pontos")
    
    meta = 101457
    total_pontos = df['numero_de_pontos'].sum()
    pontos_restantes = meta - total_pontos if meta > total_pontos else 0
    percentual_atingido = (total_pontos / meta) * 100 if meta > 0 else 0

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    col_meta1.metric("Meta de Pontos", f"{meta:,.0f}")
    col_meta2.metric("Pontos Realizados", f"{total_pontos:,.0f}")
    col_meta3.metric("Pontos Restantes", f"{pontos_restantes:,.0f}")

    st.subheader(f"Percentual Atingido: {percentual_atingido:.2f}%")
    st.progress((percentual_atingido / 100) if percentual_atingido <= 100 else 1.0)

    if pontos_restantes <= 0:
        st.success("🎉 Meta já atingida! A meta foi alcançada com sucesso.")

def display_goal_estimation(df):
    """Calcula e exibe a data estimada para o cumprimento da meta."""
    st.markdown("---")
    st.header("📅 Estimativa de Cumprimento da Meta")

    # Meta fixa de 101.457 pontos
    meta = 101457
    total_pontos = df['numero_de_pontos'].sum()
    pontos_restantes = meta - total_pontos if meta > total_pontos else 0

    # Cálculo da média de pontos diários para projeção, com base nos últimos 14 dias
    recent_df = df.sort_values(by="data").tail(14)  # Últimos 14 dias de dados
    media_pontos_diaria = recent_df['numero_de_pontos'].mean()
    ultima_data = df['data'].max()

    if pontos_restantes > 0 and media_pontos_diaria > 0:
        # Estimar quantos dias úteis serão necessários
        dias_necessarios = pontos_restantes / media_pontos_diaria

        # Melhorar cálculo de dias úteis, adicionando só dias de trabalho (segunda a sexta)
        data_estimativa_cumprimento = np.busday_offset(ultima_data.date(), int(dias_necessarios), roll='forward')
        data_estimativa_cumprimento = pd.to_datetime(data_estimativa_cumprimento)

        # Mostrar mensagem de projeção
        st.subheader(f"📅 Data Estimada para Cumprimento da Meta: {data_estimativa_cumprimento.strftime('%d/%m/%Y')}")
    else:
        # Caso a meta tenha sido atingida ou se a média diária de pontos é muito baixa
        if pontos_restantes <= 0:
            st.success("🎉 Meta já atingida! A meta foi alcançada com sucesso.")
        elif media_pontos_diaria == 0:
            st.warning("⚠ Não houve progresso recente para estimar a data de cumprimento da meta.")
        else:
            st.warning("⚠ A média de pontos por dia é muito baixa para estimar um dado realista de cumprimento da meta.")

# --------------------------
# Configuração da Página
# --------------------------

st.set_page_config(
    page_title='Dashboard FITec',
    page_icon='📊',  # Ícone de gráfico
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': 'Dashboard FITec v1.0'
    }
)

# Injetar CSS personalizado
local_css("styles.css")  # Certifique-se de criar este arquivo com seus estilos

# URL do logotipo 
logo_url = "FITec.svg"

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
    
    # Carregar os dados (com cache)
    with st.spinner('Carregando dados...'):
        data_df = get_custom_data()

    if not data_df.empty:
        # ---- Adicionar Filtro por Múltiplos Nomes ----
        unique_names = data_df['nome'].unique()
        selected_names = st.sidebar.multiselect("Selecione Nome(s)", unique_names, default=unique_names)

        # Filtrar os dados pelos nomes selecionados
        filtered_df = data_df[data_df['nome'].isin(selected_names)]
        
        # Verificar se a coluna 'data' existe no DataFrame
        if 'data' in filtered_df.columns:
            # Converter coluna 'data' para datetime e remover linhas com datas inválidas
            filtered_df['data'] = pd.to_datetime(filtered_df['data'], format='%d/%m/%Y', errors='coerce')
            filtered_df = filtered_df.dropna(subset=['data'])

            # Exibir o Progresso da Meta primeiro
            display_meta_progress(filtered_df)

            # Exibir as Estatísticas Básicas em segundo
            display_basic_stats(filtered_df)

            # Exibir o gráfico de Evolução do Número de Pontos
            display_chart(filtered_df)

            # Exibir a estimativa de cumprimento da meta no final
            display_goal_estimation(filtered_df)

            # Converter DataFrame para CSV
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

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
            st.error("A coluna 'data' não foi encontrada no arquivo CSV.")
    else:
        st.error("Os dados não puderam ser carregados.")
