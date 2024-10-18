import streamlit as st
import desempenho  # Script da página Desempenho
import projecao    # Script da página Projeção

# Configuração da página e tema
st.set_page_config(
    page_title='Dashboard FITec',
    page_icon=':bar_chart:',
    layout='wide'
)

# Usar o link direto da logo SVG do repositório GitHub
logo_url = "https://raw.githubusercontent.com/Tiagofholanda/Dashboard_FITec/main/FITec.svg"

# Função para verificar login
def login(username, password):
    users = {"Projeto": "FITEC_MA", "Eduardo": "FITEC321"}
    if username in users and users[username] == password:
        return True
    return False

# Inicializa o estado de login na sessão
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

# Se o usuário não está logado, exibe a tela de login
if not st.session_state['login_status']:
    st.title("Login no Dashboard FITec")
    st.image(logo_url, use_column_width=True)
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")

    # Botão de login
    if st.button("🔑 Acessar o Dashboard"):
        with st.spinner("Verificando credenciais..."):
            if login(username, password):
                st.session_state['login_status'] = True
                st.success(f"Bem-vindo, {username}!")
            else:
                st.error("Nome de usuário ou senha incorretos")
else:
    # Se o usuário está logado, exibe o dashboard
    st.sidebar.image(logo_url, use_column_width=True, width=200)
    st.sidebar.title("Dashboard FITec")
    
    # Menu de navegação
    page = st.sidebar.radio("Ir para:", ["Desempenho", "Projeção"])

    # Carregar o script correto conforme a seleção
    if page == "Desempenho":
        desempenho.show_desempenho()  # Função para exibir Desempenho
    elif page == "Projeção":
        projecao.show_projecao()  # Função para exibir Projeção

    # Botão de logout
    if st.sidebar.button("🔒 Sair do Sistema"):
        st.session_state['login_status'] = False
        st.sidebar.info("Você saiu do sistema.")
