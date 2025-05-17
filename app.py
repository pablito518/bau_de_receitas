import streamlit as st
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- Streamlit App Layout ---
st.title("🍳 Baú de receitas")

st.write("""
Bem-vindo ao Baú de receitas!
Informe os ingredientes que você tem e nossa equipe de agentes culinários criará uma receita exclusiva para você.
""")

# --- User Input ---
ingredients = st.text_input("❓ Por favor, digite os INGREDIENTES sobre o qual você quer criar a receita (ex: frango cozido desfiado, arroz, ervilha):")

# --- Button to trigger the process ---
if st.button("✨ Gerar Receita"):
    if not ingredients:
        st.warning("Você esqueceu de digitar os ingredientes!")
    elif client is None: # Check if client initialization failed in utils
         # Error message is already displayed in utils.py
         pass # Do nothing here, error is shown on page load or config issue
    else:
        st.write(f"Maravilha! Vamos então buscar receitas com {ingredients}")

        # Initialize variable to store the final output before the status block
        recipe_post = ""
        # Use st.status to show progress for the entire agent chain
        with st.status("Criando sua receita...", expanded=True) as status:
            try:
                # Create agent instances within the process using functions from agents.py
                buscador_agent = create_agente_buscador()
                planejador_agent = create_agente_planejador()
                redator_agent = create_agente_redator()

                # data_de_hoje = date.today().strftime("%Y-%m-%d") # Add back if needed by agent prompts

                # --- Call Agent 1 ---
                status.update(label="Passo 1: Buscando receitas compatíveis...", state="running")
                # Pass the agent instance and input string to call_agent from utils
                searched_recipes = call_agent(buscador_agent, f"Tópico: {ingredients} \n") # Add data_de_hoje if needed
                # Check for error string returned by call_agent
                if "Error during agent run" in searched_recipes: raise Exception(searched_recipes)
                status.update(label="Passo 1 concluído.", state="complete")


                # --- Call Agent 2 ---
                status.update(label="Passo 2: Planejando a receita principal...", state="running")
                 # Pass the agent instance and input string to call_agent from utils
                recipe_plan = call_agent(planejador_agent, f"Tópico:{ingredients}\nLançamentos buscados: {searched_recipes}")
                # Check for error string returned by call_agent
                if "Error during agent run" in recipe_plan: raise Exception(recipe_plan)
                status.update(label="Passo 2 concluído.", state="complete")


                # --- Call Agent 3 ---
                status.update(label="Passo 3: Escrevendo o tutorial da receita...", state="running")
                # Pass the agent instance and input string to call_agent from utils
                recipe_post = call_agent(redator_agent, f"Tópico: {ingredients}\nPlano de post: {recipe_plan}") # Assign output
                # Check for error string returned by call_agent
                if "Error during agent run" in recipe_post: raise Exception(recipe_post)
                status.update(label="Passo 3 concluído.", state="complete")


                # --- Display Result 3 ---
                st.subheader(" Receita tirada do Baú de receitas! 🍽️")
                # Check if content exists AND is not an error message from call_agent
                if recipe_post and "Error during agent run" not in recipe_post:
                    st.markdown(format_markdown_output(recipe_post))
                    st.markdown("---") # Horizontal rule
                else:
                    # Error message is already displayed by call_agent or the check above
                    st.warning("Não foi possível gerar a receita.")


                status.update(label="Receita gerada com sucesso!", state="complete")

            except Exception as e:
                # Catch any errors during the agent chain execution
                st.error(f"Ocorreu um erro durante a geração da receita: {e}")
                status.update(label="Erro na geração da receita.", state="error")

        # --- Download Button ---
        # This button will appear after the 'with st.status' block finishes
        # Only show button if valid recipe content was generated (check recipe_post and ensure it's not an error message)
        if recipe_post and "Error during agent run" not in recipe_post:
            # Use the sanitize_filename function from utils
            download_filename = f"{sanitize_filename(recipe_post)}.txt"

            st.download_button(
                label="Baixar Receita",
                data=recipe_post, # Provide the raw text content
                file_name=download_filename,
                mime="text/plain" # Specify the MIME type for a text file
            )


#else: # This block executes if the client could not be initialized in utils.py
#     st.warning("Por favor, configure sua Google API Key nas Secrets do Streamlit Cloud para usar esta aplicação.")