import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import unicodedata
from datetime import datetime, timedelta
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
        "eduardo": hash_password("FITEC@2024")
    }
    
    # Gerar hash da senha inserida
    hash_input_password = hash_password(password)
    
    # Verificar se o usuário existe e se a senha corresponde ao hash
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
    return "black"

# --------------------------
# Função para Carregar Dados
# --------------------------

@st.cache_data
def get_custom_data():
    """Carregar dados CSV personalizados a partir do link no GitHub."""
    csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
    try:
        df = pd.read_csv(csv_url, delimiter=';', on_bad_lines='skip')
        df = normalize_column_names(df)  # Normalizar os nomes das colunas
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')  # Garantir que a coluna 'data' seja datetime
        df = df.dropna(subset=['data'])  # Remover linhas com datas inválidas
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
# Função para Calcular Pontos Restantes por Imagem
# --------------------------

def calculate_statistics_per_image(name_df):
    """Calcula os Pontos Restantes por imagem e a porcentagem de progresso para o nome selecionado."""
    
    # Filtrar dados por imagem e evitar duplicidade ao somar
    image_df = name_df.drop_duplicates(subset=['imagem'])
    
    # Verificar se há imagens disponíveis
    if image_df.empty:
        return [], [], image_df
    
    # Listas para armazenar informações
    pontos_restantes_list = []
    progresso_list = []
    
    for _, row in image_df.iterrows():
        pontos_realizados = row['numero_de_pontos']
        meta_pontos = row['pontos_por_imagem']
        
        # Calcular os pontos restantes e o progresso
        pontos_restantes = meta_pontos - pontos_realizados if meta_pontos > pontos_realizados else 0
        progresso = (pontos_realizados / meta_pontos) * 100 if meta_pontos > 0 else 0
        
        pontos_restantes_list.append(pontos_restantes)
        progresso_list.append(progresso)
    
    return pontos_restantes_list, progresso_list, image_df

# --------------------------
# Função de Exibição de Estatísticas por Nome e Imagem
# --------------------------

def display_name_statistics(name_df):
    """Exibe KPIs para o nome selecionado, utilizando 'pontos_por_imagem'."""
    
    # Calcular Pontos Restantes e Progresso por Imagem
    pontos_restantes_list, progresso_list, image_df = calculate_statistics_per_image(name_df)
    
    if not pontos_restantes_list or not progresso_list:
        st.warning("⚠️ Não há dados disponíveis para exibir estatísticas.")
        return
    
    # Garantir que os índices não ultrapassem os limites
    for i, row in image_df.iterrows():
        if i >= len(pontos_restantes_list) or i >= len(progresso_list):
            continue  # Pular caso o índice seja inválido
        
        st.subheader(f"Imagem: {row['imagem']}")
        
        col1_name, col2_name, col3_name = st.columns(3)
        
        # Exibir as métricas para cada imagem individualmente
        col1_name.metric("Pontos Totais da Imagem", f"{row['numero_de_pontos']:.0f}")
        col2_name.metric("Progresso", f"{progresso_list[i]:.2f}%")
        col3_name.metric("Pontos Restantes", f"{pontos_restantes_list[i]:.0f}")

# --------------------------
# Função para Calcular Estatísticas Gerais
# --------------------------

def calculate_statistics(df):
    """Calcula estatísticas gerais, diárias e projeção de meta."""
    # Agrupar os dados por data e somar os pontos feitos no mesmo dia
    df_daily = df.groupby(df['data'].dt.date)['numero_de_pontos'].sum().reset_index()
    df_daily.columns = ['data', 'total_pontos']

    # Progresso da meta
    meta = 101457
    total_pontos = df['numero_de_pontos'].sum()  # Somando todos os pontos sem filtragem para garantir a soma correta
    pontos_restantes = meta - total_pontos if meta > total_pontos else 0
    percentual_atingido = (total_pontos / meta) * 100 if meta > 0 else 0

    # Projeção de término
    dias_totais = (df_daily['data'].max() - df_daily['data'].min()).days
    media_pontos_diaria = total_pontos / dias_totais if dias_totais > 0 else 0
    dias_necessarios = pontos_restantes / media_pontos_diaria if media_pontos_diaria > 0 else float('inf')
    data_projecao_termino = datetime.today() + timedelta(days=int(dias_necessarios))

    return df_daily, total_pontos, pontos_restantes, percentual_atingido, dias_necessarios, media_pontos_diaria, data_projecao_termino

# --------------------------
# Função de Exibição de Gráficos e Estatísticas
# --------------------------

def display_chart(df, key=None):
    """Exibe gráfico interativo do número de pontos ao longo do tempo, suavizado com uma média móvel de 7 dias."""
    st.header('📊 Evolução do Número de Pontos ao Longo do Tempo (Suavizado)')
    st.markdown("---")

    df['numero_de_pontos_smooth'] = df['numero_de_pontos'].rolling(window=7, min_periods=1).mean()

    fig = px.line(df, x='data', y='numero_de_pontos_smooth', markers=True, title="Evolução do Número de Pontos (Suavização: 7 dias)", template='ggplot2')
    fig.update_layout(xaxis_title="Data", yaxis_title="Número de Pontos Suavizado", hovermode="x unified", 
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=set_text_color())

    # Atribua um `key` único ao gráfico
    st.plotly_chart(fig, use_container_width=True, key=key)

# --------------------------
# Dashboard Principal
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
    # Carregar os dados
    # --------------------------
    
    st.image(logo_url, width=150, use_column_width=False)
    
    with st.spinner('Carregando dados...'):
        data_df = get_custom_data()

    if not data_df.empty:
        # Filtros na Barra Lateral
        unique_names = data_df['nome'].unique().tolist()
        selected_names = st.sidebar.multiselect("Selecione Nome(s)", unique_names, default=unique_names)
        start_date = st.sidebar.date_input('Data Inicial', datetime.today() - timedelta(days=30))
        end_date = st.sidebar.date_input('Data Final', datetime.today())

        # Certifique-se de que a coluna 'data' está no formato datetime e remova valores ausentes
        data_df['data'] = pd.to_datetime(data_df['data'], errors='coerce')
        data_df = data_df.dropna(subset=['data'])

        # Filtros de data (convertidos para datetime)
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filtrar dados pela data e nome
        filtered_df = data_df[(data_df['data'] >= start_date) & (data_df['data'] <= end_date)]
        if selected_names:
            filtered_df = filtered_df[filtered_df['nome'].isin(selected_names)]  # Filtrar pelos nomes

        # Calcular estatísticas
        df_daily, total_pontos, pontos_restantes, percentual_atingido, dias_necessarios, media_pontos_diaria, data_projecao_termino = calculate_statistics(filtered_df)

        # KPIs no topo
        col1, col2, col3 = st.columns(3)
        col1.metric("Pontos Realizados", total_pontos)  # Usar o valor correto aqui
        col2.metric("Progresso da Meta", f"{percentual_atingido:.2f}%")
        col3.metric("Pontos Restantes", pontos_restantes)

        # Tabs para Visão Geral e Estatísticas por Nome
        tab1, tab2 = st.tabs(["📊 Visão Geral", "📋 Estatísticas por Nome"])

        # ---- Aba 1: Visão Geral ----
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                display_meta_progress(total_pontos, pontos_restantes, percentual_atingido)
                display_basic_stats_daily(df_daily, df_daily['total_pontos'].std())

            with col2:
                display_chart(filtered_df, key="chart_visao_geral")
                display_goal_projection(dias_necessarios, data_projecao_termino)

        # ---- Aba 2: Estatísticas por Nome ----
        with tab2:
            for idx, name in enumerate(selected_names):
                st.subheader(f"Estatísticas de {name}")
                
                name_df = filtered_df[filtered_df['nome'] == name]
                
                if not name_df.empty:
                    # Exibir KPIs por imagem
                    display_name_statistics(name_df)

                    # Exibir o gráfico para o nome
                    display_chart(name_df, key=f"chart_{name}_{idx}")

                else:
                    st.warning(f"⚠️ Não foram encontrados dados para {name}.")
        
        # Exibir links profissionais no rodapé
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; font-size: 14px;">
            <a href="https://scholar.google.com.br/citations?user=XLu_qAIAAAAJ&hl=pt-BR" target="_blank">Google Acadêmico</a> | 
            <a href="https://www.linkedin.com/in/tiago-holanda-082928141/" target="_blank">LinkedIn</a> | 
            <a href="https://github.com/tiagofholanda" target="_blank">GitHub</a> | 
            <a href="http://lattes.cnpq.br/4969639760120080" target="_blank">Lattes</a> | 
            <a href="https://www.researchgate.net/profile/Tiago-Holanda" target="_blank">ResearchGate</a> | 
            <a href="https://publons.com/researcher/3962699/tiago-holanda/" target="_blank">Publons</a> | 
            <a href="https://orcid.org/0000-0001-6898-5027" target="_blank">ORCID</a> | 
            <a href="https://www.scopus.com/authid/detail.uri?authorId=57376293300" target="_blank">Scopus</a>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.error("Os dados não puderam ser carregados.")
