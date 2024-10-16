import streamlit as st
import pandas as pd

# Defina o título e o ícone que aparecerão na aba do navegador.
st.set_page_config(
    page_title='Dashboard FITec',
    page_icon=':bar_chart:',  # Ícone de gráfico
)

# -------------------------------------------------------------------------
# Funções úteis declaradas

@st.cache_data
def get_custom_data():
    """Carregar dados CSV personalizados a partir do link no GitHub."""
    
    # Link "raw" do arquivo CSV no GitHub
    csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
    
    # Carregar o CSV diretamente do link
    df = pd.read_csv(csv_url)

    return df

# Carregar os dados
data_df = get_custom_data()

# -------------------------------------------------------------------------
# Desenhar a página real

# Defina o título que aparece no topo da página.
'''
# :bar_chart: Dashboard de Dados Personalizados

Explore os dados personalizados do seu arquivo CSV hospedado no GitHub.
'''

# Adicionar algum espaçamento
''

# Converter a coluna "data" para formato datetime, se ainda não estiver
data_df['data'] = pd.to_datetime(data_df['data'], format='%Y-%m-%d')

# Obter o intervalo de datas
min_value = data_df['data'].min().date()
max_value = data_df['data'].max().date()

# Usar um widget para seleção de intervalo de datas
from_date, to_date = st.date_input(
    'Qual intervalo de datas você deseja ver?',
    [min_value, max_value],
    min_value=min_value,
    max_value=max_value
)

# Converter as datas selecionadas de volta para o formato datetime
from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

# Filtrar os dados com base no intervalo de datas selecionado
filtered_df = data_df[
    (data_df['data'] >= from_date) & (data_df['data'] <= to_date)
]

# Permitir que os usuários selecionem as imagens que desejam visualizar
images = filtered_df['imagem'].unique()

if not len(images):
    st.warning("Selecione pelo menos uma imagem")

selected_images = st.multiselect(
    'Quais imagens você gostaria de visualizar?',
    images,
    images[:3]  # Padrão: exibir as primeiras 3 imagens
)

# Filtrar os dados com base nas imagens selecionadas
filtered_df = filtered_df[filtered_df['imagem'].isin(selected_images)]

# Exibir gráfico de linhas para "número de pontos" ao longo do tempo
st.header('Número de pontos ao longo do tempo', divider='gray')

st.line_chart(
    filtered_df,
    x='data',
    y='número de pontos',
    color='imagem',
)

# Exibir métricas individuais para as imagens selecionadas
st.header(f'Métricas do Número de pontos em {to_date.strftime("%Y-%m-%d")}', divider='gray')

cols = st.columns(4)

for i, image in enumerate(selected_images):
    col = cols[i % len(cols)]

    with col:
        first_row = filtered_df[filtered_df['data'] == from_date]
        last_row = filtered_df[filtered_df['data'] == to_date]

        # Verificar se há dados para a imagem na data inicial e final antes de tentar acessar os valores
        if not first_row.empty and not last_row.empty:
            # Verificar se a imagem existe nas duas datas
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
