import streamlit as st
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- CSS Styling ---
css_completo = """
/* Font Imports */
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Inter:wght@400;600&display=swap');

/* Base Body and Streamlit Main Container Styles */
body {
    font-family: 'Inter', sans-serif !important;
    background-color: #120a2b !important; /* Roxo muito escuro, quase preto */
    color: #e0e0e0 !important; /* Texto cinza claro */
}
/* Target Streamlit's main app view container for background */
div[data-testid="stAppViewContainer"] > section:first-of-type {
    background-color: #120a2b !important;
    background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxyZWN0IHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgZmlsbD0iIzEyMGEyYiIvPgogICAgPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iNCIgZmlsbD0iIzNhMnA1YiIgb3BhY2l0eT0iMC42Ii8+CiAgICA8cGF0aCBkPSJNIDAgMCBMIDEwIDEwIEwgMCAyMCBaIiBmaWxsPSIjM2EycDViIiBvcGFjaXR5PSIwLjMiLz4KICAgIDxwYXRoIGQ9Ik0gNDAgMCBMIDMwIDEwIEwgNDAgMjAgWiIgZmlsbD0iIzNhMnA1YiIgb3BhY2l0eT0iMC4zIi8+CiAgICA8cGF0aCBkPSJNIDAgNDAgTCAxMCAzMCBMIDAgMjAgWiIgZmlsbD0iIzNhMnA1YiIgb3BhY2l0eT0iMC4zIi8+CiAgICA8cGF0aCBkPSJNIDQwIDQwIEwgMzAgMzAgTCA0MCAyMCBaIiBmaWxsPSIjM2EycDViIiBvcGFjaXR5PSIwLjMiLz4KPC9zdmc+');
    background-size: 40px 40px !important;
    color: #e0e0e0 !important;
}
.main .block-container {
    font-family: 'Inter', sans-serif !important;
    color: #e0e0e0 !important;
    padding-top: 3rem !important; /* Add some padding from top */
    padding-bottom: 3rem !important;
}

/* General Headings (fallback) and Streamlit specific headings */
h1, h2, h3 {
    font-family: 'Cinzel Decorative', cursive !important;
    color: #ffcc00 !important; /* Dourado mais vibrante */
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
}

div[data-testid="stTitle"] h1, /* Streamlit Title */
header[data-testid="stHeader"] h1 /* Streamlit st.header can also render as h1 sometimes */ {
    font-family: 'Cinzel Decorative', cursive !important;
    color: #ffcc00 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    font-size: 2.8rem !important; /* Ajuste o tamanho conforme necessário */
    text-align: center;
}

header[data-testid="stHeader"] h2 { /* Streamlit Header */
    font-family: 'Cinzel Decorative', cursive !important;
    color: #ffcc00 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    font-size: 2.2rem !important; /* Ajuste o tamanho */
    text-align: center;
    margin-bottom: 1.5rem !important;
}

div[data-testid="stSubheader"] h3 { /* Streamlit Subheader */
    font-family: 'Cinzel Decorative', cursive !important;
    color: #ffdb58 !important; /* Dourado/Bronze from .input-area label */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    font-size: 1.6rem !important; /* from .input-area label and .output-title */
    margin-bottom: 0.75rem !important;
}

/* Text Area for Ingredients */
textarea[data-testid="stTextAreaInput"] {
    font-family: 'Inter', sans-serif !important;
    width: 100% !important;
    padding: 15px !important;
    border: 3px solid #8a2be2 !important; /* Borda roxa mais grossa */
    border-radius: 8px !important;
    background-color: #1a0e33 !important; /* Fundo escuro */
    color: #e0e0e0 !important; /* Texto claro */
    min-height: 120px !important; /* Altura ajustada */
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5) !important; /* Sombra interna mais forte */
    line-height: 1.6 !important;
}
textarea[data-testid="stTextAreaInput"]:focus {
    outline: none !important;
    border-color: #ffcc00 !important; /* Borda dourada no foco */
    box-shadow: inset 0 0 8px rgba(0,0,0,0.6), 0 0 12px rgba(255,204,0,0.6) !important;
}

/* Button Styling (RPG Button) */
div[data-testid="stButton"] > button {
    font-family: 'Cinzel Decorative', cursive !important;
    font-size: 1.2rem !important; /* Um pouco maior */
    font-weight: 700 !important;
    color: #8B4513 !important; /* Cor de texto de pergaminho (Marrom escuro) */
    background: linear-gradient(to bottom, #f0e68c, #e9d98a) !important; /* Gradiente sutil de pergaminho */
    border: none !important;
    padding: 14px 32px !important;
    margin: 15px auto !important; /* Centraliza se o container do botão permitir */
    display: block !important; /* Para que margin auto funcione para centralizar */
    border-radius: 5px !important;
    transition: all 0.2s ease !important;
    box-shadow:
        inset 0 0 10px rgba(0,0,0,0.2), /* Sombra interna sutil */
        0 4px 0 0 #8b4513, /* Sombra marrom inferior (simula borda) */
        0 6px 8px rgba(0,0,0,0.4) !important; /* Sombra externa */
    text-shadow:  1px 1px 0px #422d09 !important; /* Sombra clara no texto */
    cursor: pointer !important;
    width: auto !important; /* Para o botão não ocupar a largura toda por padrão */
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(to bottom, #e9d98a, #f0e68c) !important; /* Inverte o gradiente */
    box-shadow:
        inset 0 0 10px rgba(0,0,0,0.3),
        0 6px 0 0 #8b4513, /* Sombra inferior mais proeminente */
        0 8px 12px rgba(0,0,0,0.6) !important;
    transform: translateY(-3px) !important;
    color: #5a4b3a !important;
}
div[data-testid="stButton"] > button:active {
    box-shadow:
        inset 0 0 10px rgba(0,0,0,0.4),
        0 2px 0 0 #8b4513, /* Sombra menor */
        0 3px 5px rgba(0,0,0,0.3) !important;
    transform: translateY(1px) translateX(1px) !important; /* Efeito de pressionar */
    color: #5a4b3a !important;
}

/* Status Container and Recipe Output Area */
div[data-testid="stStatus"] {
    background-color: #1a0e33 !important; /* Fundo escuro para a área de resultado */
    border: 2px solid #8a2be2 !important; /* Borda roxa */
    border-radius: 8px !important;
    padding: 20px !important;
    margin-top: 20px !important;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.4) !important;
}
/* Text within the status label (e.g., "Criando sua receita...") */
div[data-testid="stStatus"] div[data-baseweb="flex-grid"] > div > div {
    font-family: 'Inter', sans-serif !important;
    color: #e0e0e0 !important;
    font-size: 1.1rem !important;
}


/* Markdown Container for Recipe Text */
div[data-testid="stMarkdownContainer"] {
    font-family: 'Inter', sans-serif !important;
    color: #e0e0e0 !important;
    line-height: 1.8 !important;
    text-align: left !important; /* Garante alinhamento à esquerda para a receita */
}
/* Styling for elements within the recipe markdown */
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] h4,
div[data-testid="stMarkdownContainer"] strong { /* For **Fórmula Mágica:** etc. */
    font-family: 'Cinzel Decorative', cursive !important;
    color: #ffdb58 !important; /* Dourado/Bronze mais suave */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', sans-serif !important;
    color: #e0e0e0 !important;
    margin-bottom: 0.8rem !important;
}
div[data-testid="stMarkdownContainer"] ul,
div[data-testid="stMarkdownContainer"] ol {
    margin-left: 20px !important;
    margin-bottom: 1rem !important;
}
div[data-testid="stMarkdownContainer"] li {
    margin-bottom: 0.4rem !important;
}

/* st.info for initial placeholder text */
div[data-testid="stInfo"] {
    background-color: #2a1a4dCC !important; /* Roxo escuro com um pouco de transparência */
    border: 3px dashed #8a2be2 !important; /* Borda tracejada roxa mais grossa */
    border-radius: 10px !important; /* Cantos mais arredondados */
    padding: 20px !important;
    margin-top: 1.5rem !important; /* Espaço acima */
    box-shadow: inset 0 0 15px rgba(0,0,0,0.3); /* Sombra interna */
    text-align: center !important;
}
div[data-testid="stInfo"] div[data-testid="stMarkdownContainer"] p { /* Targeting paragraph inside st.info's markdown */
    font-family: 'Cinzel Decorative', cursive !important; /* Fonte RPG */
    font-size: 1.2rem !important; /* Tamanho da fonte ajustado */
    color: #ffdb58 !important; /* Cor dourada/Bronze */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important; /* Sombra de texto */
    line-height: 1.6 !important;
}


/* Streamlit's general text (e.g., st.write, st.markdown outside specific components) */
div[data-testid="stMarkdown"] p, div[data-testid="stText"] {
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.8 !important;
    font-size: 1.05rem !important;
}

/* Forja Container - attempt to style the main content block like .forja-container */
/* This will apply to the block containing the main app elements if layout is simple */
.main > div.block-container { /* Usually the first child div in .main */
    max-width: 900px !important;
    margin: 40px auto !important;
    padding: 30px !important;
    background-color: #2a1a4dEE !important; /* Fundo roxo escuro com transparência para ver o SVG */
    border: 4px solid #5e35b1 !important; /* Borda roxa */
    border-radius: 15px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
}

/* Footer (already uses markdown with inline styles, can be enhanced if needed) */
/* The custom HTML footer needs its styles defined if not inline */
.footer-custom p {
    font-family: 'Inter', sans-serif !important;
    color: #808080 !important;
    font-size: 0.9rem !important;
    margin-bottom: 0.5rem !important;
}
.footer-custom a {
    color: #a0a0a0 !important;
    text-decoration: none !important;
    transition: color 0.3s ease !important;
}
.footer-custom a:hover {
    color: #e0e0e0 !important;
    text-decoration: underline !important;
}

/* Ensure hr (markdown ---) has a thematic color */
hr {
    border-top: 2px solid #5e35b1 !important; /* Borda roxa para divisórias */
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Warning and Error messages styling */
div[data-testid="stWarning"] {
    border-left-color: #ffcc00 !important; /* Dourado para aviso */
    background-color: rgba(255, 204, 0, 0.1) !important;
}
div[data-testid="stWarning"] div[role="alert"]{
     color: #ffcc00 !important;
}

div[data-testid="stError"] {
    border-left-color: #ff4c4c !important; /* Vermelho para erro */
    background-color: rgba(255, 76, 76, 0.1) !important;
}
div[data-testid="stError"] div[role="alert"]{
     color: #ff4c4c !important;
}

div[data-testid="stSuccess"] {
    border-left-color: #28a745 !important; /* Verde para sucesso */
    background-color: rgba(40, 167, 69, 0.1) !important;
}
div[data-testid="stSuccess"] div[role="alert"]{
     color: #28a745 !important;
}

/* Download button could use some RPG flair too */
div[data-testid="stDownloadButton"] > button {
    font-family: 'Cinzel Decorative', cursive !important;
    color: #f0e68c !important; /* Texto dourado claro */
    background: linear-gradient(to bottom, #6a5acd, #483d8b) !important; /* Gradiente roxo */
    border: 2px solid #8a2be2 !important; /* Borda roxa */
    padding: 10px 20px !important;
    border-radius: 5px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 0 0 #301934, 0 3px 5px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
    margin-top: 10px !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(to bottom, #483d8b, #6a5acd) !important;
    box-shadow: 0 3px 0 0 #301934, 0 5px 8px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
    color: #fff !important;
}

"""
# --- Streamlit App Layout ---

st.set_page_config(page_title="Baú de Ingrediente - Forja de Receitas Épicas", layout="centered") # centered or wide

st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True)



# Cabeçalho principal da aplicação
st.title("⚔️ Baú de Ingrediente ⚔️")

st.markdown("""
Bem-vindo ao Baú de Ingredientes! Entre na **Forja de Fórmulas Épicas**!
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
    height=120,
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
