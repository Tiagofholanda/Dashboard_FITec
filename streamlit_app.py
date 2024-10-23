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

def display_goal_projection(df):
    """Calcula e exibe a projeção de quando a meta será atingida."""
    st.markdown("---")
    st.header("📅 Projeção de Quando Vai Terminar")

    # Meta fixa de 101.457 pontos
    meta = 101457
    total_pontos = df['numero_de_pontos'].sum()
    pontos_restantes = meta - total_pontos if meta > total_pontos else 0

    # Cálculo da média de pontos diários para projeção (baseada em todos os dados disponíveis)
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['data'])
    dias_totais = (df['data'].max() - df['data'].min()).days
    media_pontos_diaria = total_pontos / dias_totais if dias_totais > 0 else 0

    # Mesmo se a média de pontos for baixa, calcular a projeção
    if media_pontos_diaria > 0:
        dias_necessarios = pontos_restantes / media_pontos_diaria
    else:
        # Caso não haja progresso significativo, usar um valor padrão de um ponto por dia
        dias_necessarios = pontos_restantes

    # Estimar a data de término
    data_projecao_termino = datetime.today() + timedelta(days=dias_necessarios)

    # Exibir a data estimada de término, independente da média diária
    st.subheader(f"📅 Data Projeção de Término: {data_projecao_termino.strftime('%d/%m/%Y')}")
    st.write(f"**Dias Restantes**: {dias_necessarios:.0f} dias")
    st.write(f"**Média Diária de Pontos**: {media_pontos_diaria:.2f} pontos/dia")

def display_projection_per_image(name_df):
    """Calcula e exibe a projeção de quantos dias serão necessários para atingir 'pontos_por_imagem'."""
    st.markdown("---")
    st.header("📅 Projeção de Quando Vai Terminar (Pontos por Imagem)")

    # Exibir valores da coluna 'pontos_por_imagem' e 'imagem' para depuração
    st.write("Valores de 'imagem' e 'pontos_por_imagem':")
    st.write(name_df[['imagem', 'pontos_por_imagem']])

    # Verificar valores ausentes ou inválidos na coluna 'pontos_por_imagem'
    st.write(name_df['pontos_por_imagem'].isnull().sum(), " valores ausentes")
    st.write(name_df['pontos_por_imagem'].dtype, " tipo de dados")

    # Converter 'pontos_por_imagem' para valores numéricos, substituindo valores não numéricos por NaN
    # Corrigindo formatação de número
    name_df['pontos_por_imagem'] = name_df['pontos_por_imagem'].str.replace('.', '', regex=False)  # Remove pontos de milhar
    name_df['pontos_por_imagem'] = name_df['pontos_por_imagem'].str.replace(',', '.', regex=False)  # Troca vírgula por ponto
    name_df['pontos_por_imagem'] = pd.to_numeric(name_df['pontos_por_imagem'], errors='coerce')

    # Limpar dados, substituindo NaN por zero
    name_df['pontos_por_imagem'].fillna(0, inplace=True)  # Ou outra lógica, como usar a média

    # Exibir novamente os dados após a conversão para garantir que foram convertidos corretamente
    st.write("Dados convertidos de 'pontos_por_imagem':")
    st.write(name_df[['imagem', 'pontos_por_imagem']])

    # Remover duplicatas de imagem, mantendo a primeira ocorrência
    unique_df = name_df.drop_duplicates(subset=['imagem'])

    # Filtrar apenas os registros onde há pontos válidos
    valid_points_df = unique_df[unique_df['pontos_por_imagem'] > 0]

    if valid_points_df.empty:
        st.warning("⚠ Nenhum dado válido de pontos por imagem encontrado.")
        return

    # Meta será o valor de 'pontos_por_imagem' para a primeira imagem única
    meta = valid_points_df['pontos_por_imagem'].iloc[0]
    
    st.write(f"Meta baseada na primeira imagem: {meta} pontos")

    # Calcular a média de pontos por imagem
    media_pontos_por_nome = valid_points_df['pontos_por_imagem'].mean()
    
    # Calcular os dias necessários para atingir a meta
    if media_pontos_por_nome > 0:
        dias_necessarios = meta / media_pontos_por_nome
    else:
        dias_necessarios = float('inf')  # Infinito se a média for zero

    # Estimar a data de término
    data_projecao_termino = datetime.today() + timedelta(days=dias_necessarios)

    # Exibir a data estimada de término, independente da média diária
    st.subheader(f"📅 Data Projeção de Término (Pontos por Imagem): {data_projecao_termino.strftime('%d/%m/%Y')}")
    st.write(f"**Dias Restantes**: {dias_necessarios:.0f} dias")
    st.write(f"**Média Diária de Pontos por Nome**: {media_pontos_por_nome:.2f} pontos/dia")

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
            filtered_df['data'] = pd.to_datetime(filtered_df['data'], format='%d/%m/%Y', errors='coerce')
            filtered_df = filtered_df.dropna(subset=['data'])

            # Criação das abas no dashboard
            tab1, tab2 = st.tabs(["📊 Visão Geral", "📋 Estatísticas por Nome"])

            # ---- Aba 1: Visão Geral ----
            with tab1:
                # Exibir o Progresso da Meta
                display_meta_progress(filtered_df)

                # Exibir as Estatísticas Básicas
                display_basic_stats(filtered_df)

                # Exibir o gráfico de Evolução do Número de Pontos
                display_chart(filtered_df)

                # Exibir a projeção de quando a meta será atingida
                display_goal_projection(filtered_df)

            # ---- Aba 2: Estatísticas por Nome ----
            with tab2:
                for name in selected_names:
                    st.subheader(f"Estatísticas de {name}")
                    name_df = filtered_df[filtered_df['nome'] == name]
                    
                    # Exibir estatísticas individuais para o nome selecionado
                    display_basic_stats(name_df)
                    
                    # Exibir o gráfico de evolução de pontos do nome
                    display_chart(name_df)

                    # Exibir projeção para pontos por imagem
                    display_projection_per_image(name_df)

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
                <a href="https://www.researchgate.net/profile/Tiago-Holanda" target="_blank">ResearchGate</a> | 
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
