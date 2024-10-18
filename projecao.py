import streamlit as st
import pandas as pd
import plotly.express as px

def show_projecao():
    st.title("Projeção")
    st.write("Aqui você pode ver os dados de projeção.")

    # Exemplo básico de gráfico para a página de Projeção
    data = {
        'Ano': ['2023', '2024', '2025'],
        'Projeção de Crescimento (%)': [10, 15, 20]
    }
    df = pd.DataFrame(data)
    
    fig = px.line(df, x='Ano', y='Projeção de Crescimento (%)', title='Projeção de Crescimento Anual')
    st.plotly_chart(fig)
