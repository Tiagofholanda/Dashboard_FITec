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
    return "black"

# --------------------------
# Função para Carregar Dados
# --------------------------

@st.cache_data
def get_custom_data():
    """Carregar dados CSV personalizados a partir do link no GitHub ou de um arquivo local, com fallback de encoding."""
    csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
    local_file_path = "data/dados.csv"  # Fallback para arquivo local
    encodings = ["utf-8", "ISO-8859-1", "latin1", "windows-1252"]  # Lista de encodings comuns

    df = None
    # Tentar carregar o arquivo online
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_url, delimiter=';', encoding=encoding, on_bad_lines='skip')
            st.success(f"Arquivo online carregado com codificação: {encoding}")
            break
        except UnicodeDecodeError:
            st.warning(f"Erro de codificação com {encoding}, tentando próximo.")
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo online com {encoding}: {e}")
            df = None

    # Fallback para o arquivo local
    if df is None:
        for encoding in encodings:
            try:
                df = pd.read_csv(local_file_path, delimiter=';', encoding=encoding, on_bad_lines='skip')
                st.success(f"Arquivo local carregado com codificação: {encoding}")
                break
            except UnicodeDecodeError:
                st.warning(f"Erro de codificação com {encoding}, tentando próximo.")
            except FileNotFoundError:
                st.error("O arquivo CSV local não foi encontrado.")
                return pd.DataFrame()
            except pd.errors.ParserError:
                st.error("Erro ao analisar o arquivo CSV local. Verifique a formatação.")
                return pd.DataFrame()
            except Exception as e:
                st.error(f"Erro ao carregar o arquivo local com {encoding}: {e}")
                return pd.DataFrame()

    if df is None:
        st.error("Não foi possível carregar o arquivo CSV. Verifique a URL ou o caminho do arquivo local.")
        return pd.DataFrame()

    # Processamento dos dados
    try:
        df = normalize_column_names(df)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
            df = df.dropna(subset=['data'])
            st.write("Dados após conversão de datas:", df.head())
        else:
            st.error("A coluna 'data' não foi encontrada no arquivo.")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return pd.DataFrame()

# --------------------------
# Funções de Estatísticas
# --------------------------

def calculate_statistics(df):
    """Calcula estatísticas gerais, diárias e projeção de meta, incluindo a extensão total em km."""
    if df.empty:
        st.warning("DataFrame vazio após os filtros aplicados.")
        return pd.DataFrame(), 0, 0, 0, float('inf'), 0, datetime.today(), 0

    if 'numero_de_pontos' not in df.columns:
        st.error("A coluna 'numero_de_pontos' está ausente no DataFrame.")
        return pd.DataFrame(), 0, 0, 0, float('inf'), 0, datetime.today(), 0

    if df['numero_de_pontos'].isna().all():
        st.error("A coluna 'numero_de_pontos' não contém dados válidos.")
        return pd.DataFrame(), 0, 0, 0, float('inf'), 0, datetime.today(), 0

    # Agrupamento diário
    df_daily = df.groupby(df['data'].dt.date)['numero_de_pontos'].sum().reset_index()
    df_daily.columns = ['data', 'total_pontos']

    # Debug: Mostrar df_daily
    st.write("df_daily após o agrupamento:", df_daily.head())

    if df_daily.empty:
        st.error("df_daily está vazio após o agrupamento.")
        return df_daily, 0, 0, 0, float('inf'), 0, datetime.today(), 0

    if 'total_pontos' not in df_daily.columns:
        st.error("A coluna 'total_pontos' não foi criada corretamente em df_daily.")
        return df_daily, 0, 0, 0, float('inf'), 0, datetime.today(), 0

    # Cálculos de estatísticas
    meta = 101457
    total_pontos = df['numero_de_pontos'].sum()
    pontos_restantes = max(meta - total_pontos, 0)
    percentual_atingido = (total_pontos / meta) * 100 if meta > 0 else 0

    # Calcular dias totais
    dias_totais = (df_daily['data'].max() - df_daily['data'].min()).days
    media_pontos_diaria = total_pontos / dias_totais if dias_totais > 0 else 0
    dias_necessarios = pontos_restantes / media_pontos_diaria if media_pontos_diaria > 0 else float('inf')
    data_projecao_termino = datetime.today() + timedelta(days=int(dias_necessarios))

    # Calcular extensão total em km
    if 'extensao' in df.columns:
        if pd.api.types.is_numeric_dtype(df['extensao']):
            total_line_extension_meters = df['extensao'].sum()
            total_line_extension_km = total_line_extension_meters / 1000
        else:
            st.warning("A coluna 'extensao' não é numérica.")
            total_line_extension_km = 0
    else:
        total_line_extension_km = 0
        st.warning("A coluna 'extensao' não foi encontrada no arquivo CSV.")

    return df_daily, total_pontos, pontos_restantes, percentual_atingido, dias_necessarios, media_pontos_diaria, data_projecao_termino, total_line_extension_km

# --------------------------
# Funções de Exibição de KPIs e Gráficos
# --------------------------

def display_meta_progress(total_pontos, pontos_restantes, percentual_atingido):
    """Exibe métricas de progresso da meta."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Pontos Realizados", total_pontos)
    col2.metric("Progresso da Meta", f"{percentual_atingido:.2f}%")
    col3.metric("Pontos Restantes", pontos_restantes)

def display_basic_stats_daily(df_daily, std_dev):
    """Exibe estatísticas diárias básicas com desvio padrão."""
    if df_daily.empty or 'total_pontos' not in df_daily.columns:
        st.warning("Nenhuma estatística diária disponível para exibição.")
        return
    st.subheader("📅 Estatísticas Diárias")
    st.write(f"Desvio Padrão dos Pontos Diários: {std_dev:.2f}")
    st.line_chart(df_daily.set_index('data')['total_pontos'])

def display_goal_projection(dias_necessarios, data_projecao_termino):
    """Exibe projeção de conclusão da meta."""
    st.subheader("📅 Projeção de Conclusão")
    if dias_necessarios == float('inf'):
        st.write("Não é possível calcular a projeção de conclusão com os dados atuais.")
    else:
        st.write(f"Dias Necessários para Conclusão: {dias_necessarios:.0f}")
        st.write(f"Data Estimada de Conclusão: {data_projecao_termino.strftime('%d/%m/%Y')}")

def display_chart(df, key=None):
    """Exibe gráfico interativo do número de pontos ao longo do tempo, suavizado com uma média móvel de 7 dias."""
    if 'numero_de_pontos' not in df.columns or df['numero_de_pontos'].isna().all():
        st.warning("Não há dados suficientes para exibir o gráfico.")
        return

    df['numero_de_pontos_smooth'] = df['numero_de_pontos'].rolling(window=7, min_periods=1).mean()
    fig = px.line(df, x='data', y='numero_de_pontos_smooth', markers=True, 
                  title="Evolução do Número de Pontos (Suavização: 7 dias)", template='ggplot2')
    fig.update_layout(
        xaxis_title="Data", 
        yaxis_title="Número de Pontos Suavizado", 
        hovermode="x unified", 
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color=set_text_color()
    )
    st.plotly_chart(fig, use_container_width=True, key=key)

# --------------------------
# Dashboard Principal
# --------------------------

st.set_page_config(page_title='Dashboard FITec', page_icon='📊', layout='wide', initial_sidebar_state='expanded')

local_css("styles.css")
logo_url = "FITec.svg"
st.sidebar.image(logo_url, use_column_width=True)
st.sidebar.title("Dashboard FITec")

if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

if not st.session_state['login_status']:
    st.title("Login no Dashboard FITec 📊")
    st.image(logo_url, width=300)
    username = st.text_input("Nome de usuário", key="username")
    password = st.text_input("Senha", type="password", key="password")
    
    if st.button("🔑 Acessar o Dashboard"):
        with st.spinner("Verificando credenciais..."):
            if login(username, password):
                st.session_state['login_status'] = True
                st.success(f"Bem-vindo, {username}!")
            else:
                st.error("Nome de usuário ou senha incorretos")
else:
    st.image(logo_url, width=150, use_column_width=False)
    with st.spinner('Carregando dados...'):
        data_df = get_custom_data()

    if not data_df.empty:
        unique_names = data_df['nome'].unique().tolist()
        selected_names = st.sidebar.multiselect("Selecione Nome(s)", unique_names, default=unique_names)
        start_date = st.sidebar.date_input('Data Inicial', datetime.today() - timedelta(days=30))
        end_date = st.sidebar.date_input('Data Final', datetime.today())

        # Garantir que as datas estão no formato correto
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
        except Exception as e:
            st.error(f"Erro ao converter as datas: {e}")
            st.stop()

        # Filtrar os dados com base nas datas
        filtered_df = data_df[(data_df['data'] >= start_date) & (data_df['data'] <= end_date)]
        st.write("Dados após filtragem por data:", filtered_df.head())

        # Filtrar por nomes selecionados
        if selected_names:
            filtered_df = filtered_df[filtered_df['nome'].isin(selected_names)]
            st.write("Dados após filtragem por nome:", filtered_df.head())

        if filtered_df.empty:
            st.warning("Nenhum dado disponível para os filtros selecionados.")
        else:
            # Calcular estatísticas
            df_daily, total_pontos, pontos_restantes, percentual_atingido, dias_necessarios, media_pontos_diaria, data_projecao_termino, total_line_extension_km = calculate_statistics(filtered_df)
            
            # Verificar se 'total_pontos' está presente antes de calcular o desvio padrão
            if not df_daily.empty and 'total_pontos' in df_daily.columns:
                std_dev = df_daily['total_pontos'].std()
            else:
                std_dev = 0

            # KPIs at the top
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Pontos Realizados", total_pontos)
            col2.metric("Progresso da Meta", f"{percentual_atingido:.2f}%")
            col3.metric("Pontos Restantes", pontos_restantes)
            col4.metric("Extensão Total (km)", f"{total_line_extension_km:.2f}")

            # Tabs for Overview and Name-specific Statistics
            tab1, tab2 = st.tabs(["📊 Visão Geral", "📋 Estatísticas por Nome"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    display_meta_progress(total_pontos, pontos_restantes, percentual_atingido)
                    display_basic_stats_daily(df_daily, std_dev)
                with col2:
                    display_chart(filtered_df, key="chart_visao_geral")
                    display_goal_projection(dias_necessarios, data_projecao_termino)

            with tab2:
                for idx, name in enumerate(selected_names):
                    st.subheader(f"Estatísticas de {name}")
                    name_df = filtered_df[filtered_df['nome'] == name]
                    if not name_df.empty:
                        display_chart(name_df, key=f"chart_{name}_{idx}")
                    else:
                        st.warning(f"⚠️ Não foram encontrados dados para {name}.")

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
