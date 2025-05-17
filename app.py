import streamlit as st
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- CSS Styling ---
# Função para carregar o CSS
def load_css(file_name="style.css"):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS '{file_name}' não encontrado. Certifique-se de que está na mesma pasta do script.")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

# Carrega o CSS
load_css()
# --- Streamlit App Layout ---

st.set_page_config(page_title="Baú de Receitas - Forja de Receitas Épicas", layout="centered") # centered or wide

st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True)



# Cabeçalho principal da aplicação
st.title("⚔️ Baú de Receitas ⚔️")

st.markdown("""
Bem-vindo ao Baú de Receitas! Entre na **Forja de Fórmulas Épicas**!
Informe os ingredientes que você possui em seu inventário, e nossos Mestres Culinários Alquimistas conjurarão uma receita exclusiva para você.
""")
st.markdown("---")

# Container principal da Forja
# O CSS .main > div.block-container já estiliza este container principal.
# with st.container(): # Pode adicionar outro container se precisar de mais aninhamento e estilo específico.

st.header("🔥 A Forja de Fórmulas Épicas 🔥")

# --- User Input ---
st.subheader("📜 Ingredientes em Seu Inventário:")
ingredients = st.text_area(
    "Digite os ingredientes que você tem, separados por vírgula (ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha...)",
    height=100,
    placeholder="Ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha..."
)

# Variável de sessão para controlar a exibição da mensagem inicial
if 'recipe_generated_once' not in st.session_state:
    st.session_state.recipe_generated_once = False
if 'current_recipe' not in st.session_state:
    st.session_state.current_recipe = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None


# --- Button to trigger the process ---
if st.button("✨ FORJAR RECEITA! ✨"): # O CSS cuidará da centralização e estilo.
    st.session_state.recipe_generated_once = True
    st.session_state.current_recipe = None # Limpa receita anterior
    st.session_state.error_message = None # Limpa erro anterior

    if not ingredients:
        st.warning("Você esqueceu de listar os ingredientes do seu inventário!")
        st.session_state.error_message = "Você esqueceu de listar os ingredientes!"
    elif client is None: # Mocked as True, so this won't hit with mocks
        st.error("Erro na conexão com os grandes mestres alquimistas (Google API Key). Verifique as configurações.")
        st.session_state.error_message = "Erro de configuração dos mestres alquimistas."
    else:
        st.success(f"Excelente! Os alquimistas começarão a forjar uma receita com: **{ingredients}**")

        recipe_post_content = ""
        with st.status("🔮 Conjurando sua fórmula mágica...", expanded=True) as status_ui:
            try:
                buscador_agent = create_agente_buscador()
                planejador_agent = create_agente_planejador()
                redator_agent = create_agente_redator()

                status_ui.update(label="Passo 1: Vasculhando tomos antigos por receitas compatíveis...", state="running")
                searched_recipes = call_agent(buscador_agent, f"Tópico: {ingredients} \n")
                if "Error during agent run" in searched_recipes: raise Exception(searched_recipes)
                status_ui.update(label="Passo 1 Concluído: Pergaminhos encontrados!", state="complete")

                status_ui.update(label="Passo 2: Decifrando e planejando a receita principal...", state="running")
                recipe_plan = call_agent(planejador_agent, f"Tópico:{ingredients}\nLançamentos buscados: {searched_recipes}")
                if "Error during agent run" in recipe_plan: raise Exception(recipe_plan)
                status_ui.update(label="Passo 2 Concluído: Plano da receita traçado!", state="complete")

                status_ui.update(label="Passo 3: Transcrevendo o encantamento... digo, o tutorial da receita...", state="running")
                recipe_post_content = call_agent(redator_agent, f"Tópico: {ingredients}\nPlano de post: {recipe_plan}")
                if "Error during agent run" in recipe_post_content: raise Exception(recipe_post_content)
                status_ui.update(label="Passo 3 Concluído: A fórmula mágica está pronta!", state="complete")
                
                st.session_state.current_recipe = recipe_post_content
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
    # Mensagem de erro já exibida pelo st.error() ou st.warning()
    # Mas podemos adicionar um placeholder se quisermos
    st.info("Aguardando novos ingredientes para uma nova tentativa de forja...")
elif not st.session_state.recipe_generated_once:
    st.info(
        """
        Sua receita épica aparecerá aqui após a forja!
        Prepare seus utensílios e acenda o fogo do dragão!
        """
    )
else: # Foi clicado, mas houve erro de input ou a receita está vazia por algum motivo
    if not st.session_state.error_message : # Se não há mensagem de erro específica, mas não há receita
         st.info("Os ventos da magia estão parados... Insira ingredientes para começar a forja!")


# Adicionando um "rodapé" simples
st.markdown("---")
st.markdown("""
<div class="footer-custom" style="text-align: center;">
    <p>&copy; 2025 Baú de Ingrediente. Todos os direitos reservados. Forjado com Magia e Aproveitamento.</p>
    <p>
        <a href="#">Política de Privacidade</a> |
        <a href="#">Termos de Uso</a>
    </p>
</div>
""", unsafe_allow_html=True)
