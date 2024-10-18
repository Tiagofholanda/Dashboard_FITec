import streamlit as st
import desempenho  # Módulo para a página de Desempenho
import projecao  # Módulo para a página de Projeção
import mapa  # Módulo para a página de Mapa

# Configuração da página
st.set_page_config(
    page_title="Dashboard FITec",
    page_icon=":bar_chart:",
    layout="wide"
)

# Dicionário de usuários e senhas
USUARIOS = {"Projeto": "FITEC_MA", "Eduardo": "FITEC321"}  # Exemplo de usuários

# Função para verificar login
def login(username, password):
    if username in USUARIOS and USUARIOS[username] == password:
        return True
    return False

# Função para navegação por botões
def navega_por_botoes():
    st.sidebar.title("Navegação")

    # Adiciona a logo na barra lateral
    logo_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/FITec.svg"
    st.sidebar.image(logo_url, use_column_width=True)

    # Botões de navegação com ícones
    desempenho_btn = st.sidebar.button("📊 Desempenho")
    projecao_btn = st.sidebar.button("📈 Projeção")
    mapa_btn = st.sidebar.button("🗺️ Mapa")

    return desempenho_btn, projecao_btn, mapa_btn

# Função para exibir a tela de login
def exibir_tela_login():
    st.title("Login no Dashboard FITec")
    logo_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/FITec.svg"
    st.image(logo_url, use_column_width=false)
    
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("🔑 Acessar"):
        if login(username, password):
            st.session_state['login_status'] = True
            st.success(f"Bem-vindo, {username}!")
        else:
            st.error("Nome de usuário ou senha incorretos.")

# Função principal para controlar a navegação
def main():
    # Verificar se o usuário já está logado
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False
    
    # Se não estiver logado, exibe a tela de login
    if not st.session_state['login_status']:
        exibir_tela_login()
    else:
        # Se o usuário estiver logado, exibe a navegação e o dashboard
        desempenho_btn, projecao_btn, mapa_btn = navega_por_botoes()

        # Lógica de navegação: verifica qual botão foi clicado
        if desempenho_btn:
            desempenho.show_desempenho()  # Exibe a página de Desempenho
        elif projecao_btn:
            projecao.show_projecao()  # Exibe a página de Projeção
        elif mapa_btn:
            mapa.show_mapa()  # Exibe a página de Mapa
        else:
            st.markdown("<h2 style='text-align: center;'>Selecione uma página clicando nos botões na barra lateral.</h2>", unsafe_allow_html=True)

# Estilos personalizados
st.markdown("""
    <style>
        /* Estilo dos botões na barra lateral */
        div.stButton > button:first-child {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            height: 50px;
            width: 100%;
            font-size: 18px;
        }
        div.stButton > button:hover {
            background-color: #45a049;
        }

        /* Estilo geral da página */
        h2 {
            color: #2E86C1;
            font-size: 24px;
        }
        .stProgress > div > div > div {
            background-color: #4CAF50;
        }

        /* Layout da barra lateral */
        .css-1aumxhk {
            background-color: #1B2631;
        }

        /* Personalização do fundo e cores */
        body {
            background-color: #F0F2F6;
        }
    </style>
    """, unsafe_allow_html=True)

# Executa a função principal
if __name__ == "__main__":
    main()
