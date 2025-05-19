import streamlit as st
from google.genai import types
# from datetime import date # Mantido comentado
# Import necessary components from utils and agents
from utils import client, MODEL_ID, SYSTEM_INSTRUCTION # SYSTEM_INSTRUCTION importado de utils
from PIL import Image
import base64

st.set_page_config(page_title="O Oráculo – Baú de Receitas", layout="centered", initial_sidebar_state="collapsed", page_icon="🔮")

# --- CSS Styling ---
def load_css(file_name="style.css"):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo CSS '{file_name}' não encontrado. Algumas estilizações podem não ser aplicadas.") # Mudado para warning
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

# Carrega o CSS (chamado apenas uma vez)
css_completo = load_css()

# --- SVGs --- (mantidos como no seu código)
svg_chatbot_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" viewBox="0 0 256 256"><path d="M128,24a104,104,0,1,0,104,104A104.11,104.11,0,0,0,128,24Zm0,176a72,72,0,1,1,72-72A72.08,72.08,0,0,1,128,200Zm-8-48a8,8,0,0,1,8-8,56,56,0,0,0,56-56,8,8,0,0,1,16,0,72.08,72.08,0,0,1-72,72A8,8,0,0,1,120,152Z"></path></svg>"""
svg_compass_visual = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#ffcc00" viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm51.58,57.79-32,64a4.08,4.08,0,0,1-1.79,1.79l-64,32a4,4,0,0,1-5.37-5.37l32-64a4.08,4.08,0,0,1,1.79-1.79l64-32A4,4,0,0,1,179.58,81.79Z"></path></svg>"""


# --- Streamlit App Layout ---
hide_streamlit_style = """
            <style>
                /* Hide the Streamlit header and menu */
                header {visibility: hidden;}
                /* Optionally, hide the footer */
                .streamlit-footer {display: none;}
                /* Hide your specific div class, replace class name with the one you identified */
                .st-emotion-cache-79elbk {display: none;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Inicia um bloco de código que será exibido na barra lateral
with st.sidebar:
    st.markdown("## ") # Título na sidebar") 
    st.text("")

    if st.button("Forja de Receitas Épicas", use_container_width=True, key="forja_sidebar_button"):
        st.switch_page("app.py")
        
    st.write("")

    if st.button("Biblioteca Arcana", use_container_width=True, key="biblioteca_sidebar_button"):
        st.switch_page("pages/biblioteca.py")
        
    st.write("")
    

    if st.button("O oráculo 🔮", use_container_width=True, key="bussola_sidebar_button"):
        st.switch_page("pages/bussola.py")
        
    st.write("")

st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True)

# Cabeçalho principal da aplicação
st.title("🔮 O oráculo 🔮")
st.markdown("""
Descubra o real impacto do desperdício de alimentos e como suas ações de aproveitamento 
fazem a diferença para o meio ambiente e para combater a fome.""")
st.markdown("---")

# Definição da instrução do sistema para o Alquimista/Oráculo
# Assumindo que SYSTEM_INSTRUCTION é uma string definida em utils.py
system_instruction_text = SYSTEM_INSTRUCTION

# --- Inicialização do Chat e do Histórico na Sessão ---
if "chat_session_object" not in st.session_state:
    chat_config = types.GenerateContentConfig( 
        system_instruction=system_instruction_text
    )
    st.session_state.chat_session_object = client.chats.create(model=MODEL_ID, config=chat_config)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Lógica de Processamento da Resposta da IA (executa em re-runs) ---
if "ai_processing_input_text" in st.session_state and st.session_state.ai_processing_input_text is not None:
    actual_input_for_ai = st.session_state.ai_processing_input_text
    # Consome o input para evitar reprocessamento em re-runs acidentais antes da resposta
    del st.session_state.ai_processing_input_text 

    chat_session = st.session_state.chat_session_object
    try:
        response = chat_session.send_message(actual_input_for_ai)
        ai_response_text = response.text
    except Exception as e:
        ai_response_text = f"Oh, céus! Parece que minhas esferas de vidência encontraram um obstáculo: {e}"
        st.error(f"Erro ao contatar o Oráculo: {e}") # Log de erro mais visível

    # Atualiza a última mensagem (que era o placeholder "pensando")
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "oracle":
        st.session_state.messages[-1]["content"] = ai_response_text
    else:
        # Fallback caso algo inesperado ocorra com a mensagem placeholder
        st.session_state.messages.append({"role": "oracle", "content": ai_response_text})
    
    st.rerun() # Re-run para exibir a resposta final da IA

# --- Interface do Chat ---
st.subheader("🧙‍♂️ Pergunte ao Oráculo:")

chat_display_container = st.container(height=500, border=True)
with chat_display_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

user_input_placeholder = "Desvende os segredos dos ingredientes..."
user_input = st.chat_input(user_input_placeholder, key="oraculo_chat_input")

if user_input:
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Adiciona a mensagem placeholder do Oráculo "pensando"
    thinking_message = "O Oráculo mergulha em profunda consulta aos tomos ancestrais... 🔮"
    st.session_state.messages.append({"role": "oracle", "content": thinking_message})

    # Guarda o input do usuário para ser processado no próximo re-run pela lógica acima
    st.session_state.ai_processing_input_text = user_input
    
    # Força um re-run para exibir a mensagem do usuário e o placeholder "pensando"
    st.rerun()

# Adicionando um "rodapé" simples
st.markdown("---")
st.markdown("""
<div class="footer-custom" style="text-align: center;">
    <p>&copy; 2025 Baú de Receitas. Todos os direitos reservados. Forjado com Magia e Aproveitamento.</p>
</div>
""", unsafe_allow_html=True)
