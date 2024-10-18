import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar os dados do arquivo Excel a partir do GitHub
@st.cache_data
def carregar_dados_desempenho():
    # URL do arquivo Excel no GitHub (substitua pelo URL correto)
    url_github = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/planilha%20de%20controle.xlsx"
    try:
        # Carregar o arquivo Excel diretamente da URL do GitHub
        dados = pd.read_excel(url_github)
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo Excel: {e}")
        return pd.DataFrame()

# Função para exibir a página de Desempenho
def show_desempenho():
    st.title("📊 Desempenho Atual")
    st.write("Aqui você pode visualizar o desempenho atual em relação à meta de 100.000 pontos.")

    # Carregar os dados do arquivo Excel
    dados = carregar_dados_desempenho()

    # Verificar se o arquivo foi carregado corretamente
    if dados.empty:
        st.error("Não há dados disponíveis para exibir.")
        return

    # Verificar se as colunas 'número de pontos' e 'data' estão presentes no Excel
    if 'número de pontos' not in dados.columns or 'data' not in dados.columns:
        st.error("As colunas 'número de pontos' ou 'data' não foram encontradas no arquivo Excel.")
        return

    # Converter a coluna 'número de pontos' para números
    dados['número de pontos'] = pd.to_numeric(dados['número de pontos'], errors='coerce')

    # Verificar se há valores nulos na coluna 'número de pontos' e ignorá-los
    if dados['número de pontos'].isnull().sum() > 0:
        st.warning(f"Há {dados['número de pontos'].isnull().sum()} valores nulos na coluna 'número de pontos'. Eles serão ignorados.")
        dados = dados.dropna(subset=['número de pontos'])

    # Calcular os valores de desempenho
    meta_total = 100000  # Meta definida de 100.000 pontos
    pontos_acumulados = dados['número de pontos'].sum()  # Soma os pontos da coluna 'número de pontos'
    pontos_faltantes = meta_total - pontos_acumulados if meta_total > pontos_acumulados else 0  # Quanto falta para atingir a meta
    progresso = (pontos_acumulados / meta_total) * 100 if meta_total > 0 else 0  # Porcentagem de progresso

    # Exibir os cards de desempenho
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Meta Total", f"{meta_total:,.0f} pontos")
    
    with col2:
        st.metric("Pontos Acumulados", f"{pontos_acumulados:,.0f} pontos")
    
    with col3:
        st.metric("Pontos Faltantes", f"{pontos_faltantes:,.0f} pontos")
    
    with col4:
        st.metric("Progresso", f"{progresso:.2f} %")

    # Barra de progresso
    st.progress(int(progresso))

    # Gráfico de desempenho diário (opcional, para visualizar o progresso por dia)
    st.subheader("Desempenho Diário de Pontos")
    desempenho_diario = dados.groupby(dados['data'].dt.date)['número de pontos'].sum().reset_index()
    fig = px.line(desempenho_diario, x='data', y='número de pontos', 
                  title="Desempenho Diário - Total de Pontos por Dia",
                  labels={"número de pontos": "Pontos Diários", "data": "Data"},
                  markers=True)
    st.plotly_chart(fig)

    # Botão para download dos dados de desempenho diário
    csv = desempenho_diario.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar CSV de Desempenho Diário",
        data=csv,
        file_name='desempenho_diario.csv',
        mime='text/csv',
    )
