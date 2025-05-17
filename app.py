import streamlit as st
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- Streamlit App Layout ---
st.set_page_config(page_title="Baú de Ingrediente - Forja de Receitas Épicas", layout="wide")

# Cabeçalho principal da aplicação
st.title("⚔️ Baú de Ingrediente ⚔️")

st.write("""
Bem-vindo ao Baú de Ingredientes! Entre na Forja de Fórmulas Épicas!
Informe os ingredientes que você possui em seu inventário, e nossos Mestres Culinários Alquimistas conjurarão uma receita exclusiva para você.
""")
st.markdown("---")

# Container principal da Forja (semelhante ao .forja-container do HTML)
with st.container():
    st.header("🔥 A Forja de Fórmulas Épicas 🔥")

    # --- User Input ---
    # Semelhante a <label for="ingredientes"> e <textarea id="ingredientes">
    st.subheader("📜 Ingredientes em Seu Inventário:")
    ingredients = st.text_area(
        "Digite os ingredientes que você tem, separados por vírgula (ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha...)",
        height=100, # Altura similar à textarea
        placeholder="Ex: casca de abóbora, talo de brócolis, pão amanhecido, cenoura murcha..."
    )

    # --- Button to trigger the process ---
    # Semelhante a <button class="rpg-button text-xl">FORJAR RECEITA!</button>
    col1, col2, col3 = st.columns([1,2,1]) # Para centralizar o botão
    with col2:
        if st.button("✨ FORJAR RECEITA! ✨", use_container_width=True):
            if not ingredients:
                st.warning("Você esqueceu de listar os ingredientes do seu inventário!")
            elif client is None:
                st.error("Erro na conexão com os grandes mestres alquimistas (Google API Key). Verifique as configurações.")
            else:
                st.success(f"Excelente! Os alquimistas começarão a forjar uma receita com: **{ingredients}**")

                recipe_post = ""
                with st.status("🔮 Conjurando sua fórmula mágica...", expanded=True) as status:
                    try:
                        buscador_agent = create_agente_buscador()
                        planejador_agent = create_agente_planejador()
                        redator_agent = create_agente_redator()

                        status.update(label="Passo 1: Vasculhando tomos antigos por receitas compatíveis...", state="running")
                        searched_recipes = call_agent(buscador_agent, f"Tópico: {ingredients} \n")
                        if "Error during agent run" in searched_recipes: raise Exception(searched_recipes)
                        #st.text(f"Resultado Busca:\n{searched_recipes}") # Debug
                        status.update(label="Passo 1 Concluído: Pergaminhos encontrados!", state="complete")

                        status.update(label="Passo 2: Decifrando e planejando a receita principal...", state="running")
                        recipe_plan = call_agent(planejador_agent, f"Tópico:{ingredients}\nLançamentos buscados: {searched_recipes}")
                        if "Error during agent run" in recipe_plan: raise Exception(recipe_plan)
                        #st.text(f"Resultado Plano:\n{recipe_plan}") # Debug
                        status.update(label="Passo 2 Concluído: Plano da receita traçado!", state="complete")

                        status.update(label="Passo 3: Transcrevendo o encantamento... digo, o tutorial da receita...", state="running")
                        recipe_post = call_agent(redator_agent, f"Tópico: {ingredients}\nPlano de post: {recipe_plan}")
                        if "Error during agent run" in recipe_post: raise Exception(recipe_post)
                        status.update(label="Passo 3 Concluído: A fórmula mágica está pronta!", state="complete")

                        status.update(label="Receita gerada com sucesso!", state="complete", expanded=False)

                    except Exception as e:
                        st.error(f"Um feitiço deu errado durante a conjuração da receita: {e}")
                        status.update(label="Erro na conjuração da receita.", state="error")

                # --- Display Result ---
                # Semelhante ao .output-header e .output-area
                st.subheader("📖 Fórmula Mágica Revelada: 📖")
                if recipe_post and "Error during agent run" not in recipe_post:
                    # Em HTML, o <p id="receita-gerada" class="output-instruction-text"> é substituído.
                    # Aqui, exibimos diretamente a receita.
                    st.markdown(format_markdown_output(recipe_post))
                    st.markdown("---")

                    # --- Download Button ---
                    download_filename = f"{sanitize_filename(recipe_post)}.txt"
                    st.download_button(
                        label="📜 Baixar Pergaminho da Receita",
                        data=recipe_post,
                        file_name=download_filename,
                        mime="text/plain"
                    )
                elif "Error during agent run" in recipe_post:
                     st.warning("Os alquimistas encontraram um problema e não foi possível gerar a receita. Tente ingredientes diferentes.")
                # Se recipe_post estiver vazio (e não for um erro), significa que o processo não chegou a gerar.
                # A mensagem de "erro na conjuração" já teria sido mostrada no bloco except.

        # Se o botão não foi clicado, ou se os ingredientes não foram fornecidos inicialmente,
        # mostrar a instrução inicial da área de output.
        # Isso é um pouco diferente do HTML onde o JS controla a visibilidade.
        # No Streamlit, o estado é reconstruído a cada interação.
        # Para uma correspondência mais próxima, precisaríamos usar st.session_state para
        # controlar a visibilidade deste bloco de forma mais persistente.
        # No entanto, para manter a simplicidade e usar "exclusivamente componentes Streamlit"
        # da forma mais direta, esta abordagem é razoável.
        # Se quisermos exibir a mensagem "Sua receita aparecerá aqui" ANTES do primeiro clique,
        # podemos adicionar um else ao if st.button, mas isso complicaria o estado de quando
        # a receita é gerada ou falha.
        # Uma forma mais simples é exibir a receita (ou erro) quando ela existir,
        # e nada específico se ainda não foi gerada (o subheader "Fórmula Mágica Revelada" já indica a área).

# Adicionando um "rodapé" simples para tentar replicar a estrutura do HTML
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: grey; font-size: 0.9em;">
    <p>&copy; 2025 Baú de Ingrediente. Todos os direitos reservados. Forjado com Magia e Aproveitamento.</p>
    <p>
        <a href="#" style="color: grey; text-decoration: none;">Política de Privacidade</a> |
        <a href="#" style="color: grey; text-decoration: none;">Termos de Uso</a>
    </p>
</div>
""", unsafe_allow_html=True)