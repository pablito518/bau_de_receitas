import streamlit as st
# import re # Not needed directly in app.py anymore
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator

# --- Streamlit App Layout ---
# Use st.title for the main heading
st.title("A FORJA DE FÓRMULAS ÉPICAS")

# Use st.subheader or st.write for the input label
st.subheader("INGREDIENTES EM SEU INVENTÁRIO ( SEPARE POR VÍRGULAS ) :")

# Use st.text_input for the ingredients input box
ingredients = st.text_input(
    label="Ex : casca de abóbora , talo de brócolis , pão amanhecido , cenoura murcha ...",
    label_visibility="collapsed" # Hide the default label, using the subheader above
)

# Use st.button for the "FORJAR RECEITA !" button
# Streamlit buttons have default styling
if st.button("FORJAR RECEITA !"):
    if not ingredients:
        st.warning("Você esqueceu de digitar os ingredientes!")
    elif client is None: # Check if client initialization failed in utils
         # Error message is already displayed in utils.py on load if key is missing
         pass # Do nothing here, error is shown on page load or config issue
    else:
        st.write(f"Maravilha! Vamos então buscar receitas com {ingredients}")

        # Initialize variable to store the final output before the status block
        recipe_post = ""
        # Use st.status for progress indication
        with st.status("Criando sua receita...", expanded=True) as status:
            try:
                # Create agent instances within the process using functions from agents.py
                buscador_agent = create_agente_buscador()
                planejador_agent = create_agente_planejador()
                redator_agent = create_agente_redator()

                # --- Call Agent 1 ---
                status.update(label="Passo 1: Buscando receitas compatíveis...", state="running")
                searched_recipes = call_agent(buscador_agent, f"Tópico: {ingredients} \n") # Add data_de_hoje if needed by agent
                if "Error during agent run" in searched_recipes: raise Exception(searched_recipes)
                status.update(label="Passo 1 concluído.", state="complete")


                # --- Call Agent 2 ---
                status.update(label="Passo 2: Planejando a receita principal...", state="running")
                recipe_plan = call_agent(planejador_agent, f"Tópico:{ingredients}\nLançamentos buscados: {searched_recipes}")
                if "Error during agent run" in recipe_plan: raise Exception(recipe_plan)
                status.update(label="Passo 2 concluído.", state="complete")


                # --- Call Agent 3 ---
                status.update(label="Passo 3: Escrevendo o tutorial da receita...", state="running")
                recipe_post = call_agent(redator_agent, f"Tópico: {ingredients}\nPlano de post: {recipe_plan}") # Assign output
                if "Error during agent run" in recipe_post: raise Exception(recipe_post)
                status.update(label="Passo 3 concluído.", state="complete")


                status.update(label="Receita gerada com sucesso!", state="complete")

            except Exception as e:
                st.error(f"Ocorreu um erro durante a geração da receita: {e}")
                status.update(label="Erro na geração da receita.", state="error")

        # --- Display Result 3 ---
        # Use st.subheader for the output label
        st.subheader("FÓRMULA MÁGICA REVELADA :")

        # Use st.text_area for the recipe output box
        # The content will be the formatted markdown output
        # We set a fixed height to mimic the appearance of a box
        if recipe_post and "Error during agent run" not in recipe_post:
             st.text_area(
                 label="SUA RECEITA ÉPICA APARECERÁ AQUI APÓS A FORJA ! PREPARE SEUS UTENSÍLIOS E ACENDA O FOGO !",
                 value=format_markdown_output(recipe_post), # Display the formatted recipe
                 height=300, # Set a fixed height for the output box
                 label_visibility="collapsed" # Hide the default label
             )
             st.markdown("---") # Standard horizontal rule

             # --- Download Button ---
             # Uses Streamlit's default download button styling
             download_filename = f"{sanitize_filename(recipe_post)}.txt"

             st.download_button(
                 label="Baixar Receita",
                 data=recipe_post,
                 file_name=download_filename,
                 mime="text/plain"
             )

        else:
            # Display the placeholder text in a text area if no recipe is generated
             st.text_area(
                 label="SUA RECEITA ÉPICA APARECERÁ AQUI APÓS A FORJA ! PREPARE SEUS UTENSÍLIOS E ACENDA O FOGO !",
                 value="SUA RECEITA ÉPICA APARECERÁ AQUI APÓS A FORJA ! PREPARE SEUS UTENSÍLIOS E ACENDA O FOGO !",
                 height=300,
                 label_visibility="collapsed"
             )
             st.markdown("---") # Standard horizontal rule


#else: # This block executes if the client could not be initialized in utils.py
  #   st.warning("Por favor, configure sua Google API Key nas Secrets do Streamlit Cloud para usar esta aplicação.")

