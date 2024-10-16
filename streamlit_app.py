import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# Definir o layout para o modo wide
st.set_page_config(
    page_title='Dashboard FITec',
    page_icon=':bar_chart:',  # Ícone de gráfico
    layout='wide'  # Ativando o modo wide (tela ampla)
)

# Adicionar o logo da FITec usando SVG via HTML
logo_url = "https://www.fitec.org.br/ProjetoAgro/logo-header.svg"
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <img src="{logo_url}" alt="Logo FITec" style="width:300px;"/>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------------------
# Função para verificar login
def login(username, password):
    users = {"Projeto": "FITEC_MA", "user1": "senha_user1"}
    if username in users and users[username] == password:
        return True
    return False

# Inicializa o estado de login na sessão
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

# Tela de login
if not st.session_state['login_status']:
    st.title("Login no Dashboard FITec")
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    
    # Botão de login
    if st.button("Login"):
        if login(username, password):
            st.session_state['login_status'] = True
            st.success(f"Bem-vindo, {username}!")
        else:
            st.error("Nome de usuário ou senha incorretos")
else:
    # Exibe o dashboard após login
    st.title("Dashboard FITec")
    st.markdown("---")  # Divisor para separação de seções

    # Botão de logout
    if st.button("Logout"):
        st.session_state['login_status'] = False
        st.info("Você saiu do sistema.")

    # -------------------------------------------------------------------------
    # Função para carregar os dados CSV
    @st.cache_data
    def get_custom_data():
        """Carregar dados CSV personalizados a partir do link no GitHub."""
        # Link "raw" do arquivo CSV no GitHub
        csv_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/data/dados.csv"
        try:
            df = pd.read_csv(csv_url, delimiter=',', on_bad_lines='skip')
        except FileNotFoundError:
            st.error("O arquivo CSV não foi encontrado. Verifique o URL.")
            return pd.DataFrame()  # Retornar DataFrame vazio
        except pd.errors.ParserError:
            st.error("Erro ao analisar o arquivo CSV. Verifique a formatação.")
            return pd.DataFrame()  # Retornar DataFrame vazio
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return pd.DataFrame()  # Retornar DataFrame vazio
        return df

    # Carregar os dados
    data_df = get_custom_data()

    if not data_df.empty:
        # Converter a coluna "data" para formato datetime
        data_df['data'] = pd.to_datetime(data_df['data'], format='%Y-%m-%d', errors='coerce')
        data_df = data_df.dropna(subset=['data'])  # Remover linhas com datas inválidas

        # -------------------------------------------------------------------------
        # Seção: Meta e Projeção

        # Disposição em colunas para melhor organização
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Configuração de Meta")
            # Input para o usuário definir uma meta
            meta_pontos = st.number_input("Defina a meta de pontos a ser atingida:", min_value=0, value=101457)

        with col2:
            st.subheader("Métricas de Pontos")
            # Cálculo da média de pontos diários
            media_diaria = data_df['número de pontos'].mean()
            st.write(f"Média de pontos diários atual: {media_diaria:.2f}")

            # Calcular o total de pontos já acumulados
            total_pontos = data_df['número de pontos'].sum()
            st.write(f"Total de pontos acumulados: {total_pontos}")

            # Quantidade de pontos que faltam para atingir a meta
            pontos_restantes = meta_pontos - total_pontos
            st.write(f"Pontos restantes para atingir a meta: {pontos_restantes}")

        st.markdown("---")  # Divisor

        # Projeção de quando a meta será atingida
        if pontos_restantes > 0:
            dias_necessarios = pontos_restantes / media_diaria
            data_termino = data_df['data'].max() + timedelta(days=dias_necessarios)
            st.success(f"Com a média de pontos atual, a meta será atingida em aproximadamente {dias_necessarios:.1f} dias, por volta de {data_termino.strftime('%Y-%m-%d')}")
        else:
            st.success("Parabéns! A meta já foi atingida!")

        # O usuário pode definir uma quantidade de pontos diários diferente para ver uma nova projeção
        nova_media_diaria = st.number_input("Insira uma nova média de pontos diários para projeção:", min_value=1, value=int(media_diaria))

        if pontos_restantes > 0:
            novos_dias_necessarios = pontos_restantes / nova_media_diaria
            nova_data_termino = data_df['data'].max() + timedelta(days=novos_dias_necessarios)
            st.info(f"Com a nova média de {nova_media_diaria} pontos por dia, a meta será atingida em aproximadamente {novos_dias_necessarios:.1f} dias, por volta de {nova_data_termino.strftime('%Y-%m-%d')}")
        else:
            st.success("A meta já foi atingida!")

        # -------------------------------------------------------------------------
        # Seção: Gráfico Interativo

        st.markdown("---")
        st.subheader("Número de pontos ao longo do tempo")

        # Gráfico interativo com Plotly
        fig = px.line(data_df, x='data', y='número de pontos', markers=True,
                      title="Evolução do Número de Pontos ao Longo do Tempo")
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de Pontos",
            legend_title="Imagem",
            hovermode="x unified"
        )
        st.plotly_chart(fig)

        # -------------------------------------------------------------------------
        # Seção: Métricas Individuais para cada Imagem
        st.markdown("---")
        st.subheader(f"Métricas do Número de pontos em {data_df['data'].max().strftime('%Y-%m-%d')}")

        # Disposição das métricas em colunas
        cols = st.columns(4)

        for i, image in enumerate(data_df['imagem'].unique()):
            col = cols[i % len(cols)]
            with col:
                # Filtrar os dados para a imagem
                filtro_imagem = data_df[data_df['imagem'] == image]

                # Verificar se há dados para a imagem antes de acessar
                if not filtro_imagem.empty:
                    pontos_inicial = filtro_imagem.iloc[0]['número de pontos']
                    pontos_final = filtro_imagem.iloc[-1]['número de pontos']

                    # Calcular o crescimento em pontos
                    crescimento = (pontos_final / pontos_inicial) if pontos_inicial != 0 else 0
                    crescimento_texto = f'{crescimento:.2f}x'

                    st.metric(
                        label=f'{image} Número de pontos',
                        value=f'{pontos_final:,.0f}',
                        delta=crescimento_texto
                    )
                else:
                    st.warning(f"Não há dados para a imagem {image}.")
    else:
        st.error("Os dados não puderam ser carregados.")
