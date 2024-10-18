import streamlit as st
import pandas as pd
import plotly.express as px

def show_projecao():
    st.title("📈 Projeção de Metas")
    st.write("Acompanhe aqui o progresso atual e veja a projeção para atingir as metas.")

    # Simulação de dados
    dados = pd.DataFrame({
        'data': pd.date_range(start='2023-01-01', periods=30),
        'pontos_projetados': pd.Series(range(30)) * 150
    })

    # Meta e projeção
    meta_total = 10000
    pontos_acumulados = dados['pontos_projetados'].sum()
    pontos_faltantes = meta_total - pontos_acumulados
    progresso = (pontos_acumulados / meta_total) * 100

    # Exibição das métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Meta Total", f"{meta_total:,.0f} pontos")
    with col2:
        st.metric("Pontos Projetados", f"{pontos_acumulados:,.0f} pontos")

    st.subheader(f"Ainda faltam {pontos_faltantes:.0f} pontos para atingir a meta.")

    # Gráfico de projeção
    fig = px.line(dados, x='data', y='pontos_projetados', 
                  title="Projeção de Pontos ao Longo do Tempo",
                  labels={"pontos_projetados": "Pontos Projetados", "data": "Data"},
                  markers=True)
    fig.update_layout(
        title_font=dict(size=22, color='DarkBlue'),
        xaxis_title="Data",
        yaxis_title="Pontos Projetados",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        font=dict(family="Arial", size=14)
    )
    st.plotly_chart(fig)

    # Adiciona o botão para baixar os dados
    st.subheader("Baixar Dados de Projeção")
    
    # Converte o dataframe em CSV para download
    csv = dados.to_csv(index=False).encode('utf-8')

    # Botão para download do CSV
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name='projecao.csv',
        mime='text/csv',
    )
