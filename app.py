import streamlit as st
import asyncio # <<< ADICIONADO IMPORT
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_assistente, create_agente_cozinheiro, create_agente_chef
from PIL import Image
import base64 # Não parece estar sendo usado, mas mantido se houver uso futuro

st.set_page_config(page_title="Baú de Receitas - Forja de Receitas Épicas", layout="centered", initial_sidebar_state="auto", page_icon="🔥")

# --- CSS Styling ---
def load_css(file_name="style.css"):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS '{file_name}' não encontrado. Certifique-se de que está na mesma pasta do script.")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

css_completo = load_css() # Carrega o CSS

# --- SVGs --- #
# svg_chatbot_icon e svg_compass_visual mantidos como no original, se usados em outro lugar ou pelo CSS.

# --- Streamlit App Layout ---
hide_streamlit_style = """
            <style>
                header {visibility: hidden;}
                .streamlit-footer {display: none;}
                .st-emotion-cache-79elbk {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ")
    st.text("")
    if st.button("Forja de Receitas Épicas", use_container_width=True, key="forja_sidebar_button"):
        st.switch_page("app.py") # Ou apenas recarrega a página se já estiver nela
    st.write("")
    if st.button("Biblioteca Arcana", use_container_width=True, key="biblioteca_sidebar_button"):
        st.switch_page("pages/biblioteca.py")
    st.write("")
    if st.button("O oráculo", use_container_width=True, key="bussola_sidebar_button"):
        st.switch_page("pages/oraculo.py")
    st.write("")

# st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True) # CSS já carregado e aplicado por load_css()

st.title("⚔️ Baú de Receitas ⚔️")
st.markdown("""
Bem-vindo ao Baú de Receitas! Entre na **Forja de Fórmulas Épicas**!
Informe os ingredientes que você possui em seu inventário, e nossos Mestres Culinários Alquimistas conjurarão uma receita exclusiva para você.
""")
st.markdown("---")
st.header("🔥 A Forja de Fórmulas Épicas 🔥")

st.subheader("📜 Ingredientes em Seu Inventário:")
ingredients = st.text_area(
    "Digite os ingredientes que você tem, separados por vírgula (ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha...)",
    height=100,
    placeholder="Ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha..."
)

if 'recipe_generated_once' not in st.session_state:
    st.session_state.recipe_generated_once = False
if 'current_recipe' not in st.session_state:
    st.session_state.current_recipe = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# --- Função Assíncrona para Orquestrar a Forja da Receita ---
async def _forjar_receita_sequencial_async(ingredients_text: str, status_ui_ref):
    """
    Orquestra as chamadas sequenciais aos agentes de forma assíncrona.
    Assume que create_agente_... e call_agent (async) estão definidos e importados.
    """
    buscador_agent = create_agente_assistente()
    planejador_agent = create_agente_cozinheiro()
    redator_agent = create_agente_chef()

    # Passo 1
    status_ui_ref.update(label="Passo 1: Vasculhando tomos antigos por receitas compatíveis...", state="running")
    searched_recipes = await call_agent(buscador_agent, f"Tópico: {ingredients_text} \n")
    # Verifica se call_agent retornou uma string de erro conhecida
    if "Error during agent run" in searched_recipes or "Error: GenAI client not initialized" in searched_recipes:
        raise Exception(f"Falha no Passo 1 (Busca): {searched_recipes}")
    status_ui_ref.update(label="Passo 1 Concluído: Pergaminhos encontrados!", state="complete")

    # Passo 2
    status_ui_ref.update(label="Passo 2: Decifrando e planejando a receita principal...", state="running")
    recipe_plan = await call_agent(planejador_agent, f"Tópico:{ingredients_text}\nLançamentos buscados: {searched_recipes}")
    if "Error during agent run" in recipe_plan or "Error: GenAI client not initialized" in recipe_plan:
        raise Exception(f"Falha no Passo 2 (Planejamento): {recipe_plan}")
    status_ui_ref.update(label="Passo 2 Concluído: Plano da receita traçado!", state="complete")

    # Passo 3
    status_ui_ref.update(label="Passo 3: Transcrevendo o encantamento... digo, o tutorial da receita...", state="running")
    recipe_post_content = await call_agent(redator_agent, f"Tópico: {ingredients_text}\nPlano de post: {recipe_plan}")
    if "Error during agent run" in recipe_post_content or "Error: GenAI client not initialized" in recipe_post_content:
        raise Exception(f"Falha no Passo 3 (Redação): {recipe_post_content}")
    status_ui_ref.update(label="Passo 3 Concluído: A fórmula mágica está pronta!", state="complete")
    
    return recipe_post_content

# --- Button to trigger the process ---
if st.button("✨ FORJAR RECEITA! ✨"):
    st.session_state.recipe_generated_once = True
    st.session_state.current_recipe = None
    st.session_state.error_message = None

    # 'ingredients' é o valor do st.text_area definido acima
    if not ingredients: # Verifica a string diretamente
        st.warning("Você esqueceu de listar os ingredientes do seu inventário!")
        st.session_state.error_message = "Você esqueceu de listar os ingredientes!"
    elif client is None:
        st.error("Erro na conexão com os grandes mestres alquimistas (Google API Key). Verifique as configurações.")
        st.session_state.error_message = "Erro de configuração dos mestres alquimistas."
    else:
        st.success(f"Excelente! Os alquimistas começarão a forjar uma receita com: **{ingredients}**")

        # recipe_post_content = "" # Não é mais necessário aqui
        with st.status("🔮 Conjurando sua fórmula mágica...", expanded=True) as status_ui:
            try:
                # Chama a função orquestradora assíncrona
                # A variável 'ingredients' (string do text_area) é passada diretamente
                final_recipe_content = asyncio.run(
                    _forjar_receita_sequencial_async(ingredients, status_ui)
                )
                st.session_state.current_recipe = final_recipe_content
                status_ui.update(label="Receita gerada com sucesso!", state="complete", expanded=False)

            except Exception as e:
                error_str = f"Um feitiço deu errado durante a conjuração da receita: {e}"
                st.error(error_str)
                st.session_state.error_message = error_str
                status_ui.update(label="Erro na conjuração da receita.", state="error")

# --- Display Result or Initial Placeholder ---
st.subheader("📖 Fórmula Mágica Revelada: 📖")

if st.session_state.current_recipe:
    st.markdown(format_markdown_output(st.session_state.current_recipe))
    st.markdown("---")
    download_filename = f"{sanitize_filename(st.session_state.current_recipe)}.txt"
    st.download_button(
        label="📜 Baixar Pergaminho da Receita",
        data=st.session_state.current_recipe,
        file_name=download_filename,
        mime="text/plain"
    )
elif st.session_state.error_message and st.session_state.error_message != "Você esqueceu de listar os ingredientes!":
    st.info("Aguardando novos ingredientes para uma nova tentativa de forja...")
elif not st.session_state.recipe_generated_once:
    st.info(
        """
        Sua receita épica aparecerá aqui após a forja!
        Prepare seus utensílios e acenda o fogo do dragão!
        """
    )
else:
    if not st.session_state.error_message:
         st.info("Os ventos da magia estão parados... Insira ingredientes para começar a forja!")

st.markdown("---")
st.markdown("""
<div class="footer-custom" style="text-align: center;">
    <p>&copy; 2025 Baú de Receitas. Todos os direitos reservados. Forjado com Magia e Aproveitamento.</p>
</div>
""", unsafe_allow_html=True)

