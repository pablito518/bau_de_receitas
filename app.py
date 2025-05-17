import streamlit as st
import os
import re # Import regex module for cleaning filename
# from datetime import date # Import if date is needed by agent prompts again
# Import necessary components from utils and agents
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- Inject Custom CSS for Styling ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Inter:wght@400;600&display=swap');

/* Apply styles to the main body and container */
body {
    font-family: 'Inter', sans-serif; /* Inter for general text */
    background-color: #120a2b; /* Dark purple background */
    color: #e0e0e0; /* Light gray text */
    line-height: 1.8;
    /* Add a background texture/image if you have one available and can host it */
    /* background-image: url('your-background-image-url.jpg'); */
    background-size: cover;
    background-attachment: fixed;
}

/* Target Streamlit's main container to ensure background covers the app area */
.stApp {
    background-color: #120a2b; /* Same dark purple background */
    background-image: url('https://i.imgur.com/xxxxx.jpg'); /* Replace with your background image URL if using one */
    background-size: cover;
    background-attachment: fixed;
}


/* Apply Cinzel Decorative to titles/headers - targeting Streamlit generated classes */
/* These selectors might need updates with Streamlit versions */
h1, h2, h3, h4, h5, h6, .css-10trblm.e16z1upr0 { /* .css-... class is a common Streamlit H1, prone to change */
    font-family: 'Cinzel Decorative', cursive;
    color: #f0d9b5; /* Light gold/parchment color for headings */
    text-shadow: 2px 2px 4px #000000; /* Subtle text shadow */
}

/* Style the main title specifically */
h1 {
    text-align: center;
    margin-bottom: 0.5em;
}


/* Attempt to style native Streamlit elements */

/* Text Input */
.stTextInput > label {
    font-family: 'Cinzel Decorative', cursive; /* Style label */
    color: #f0d9b5; /* Label color */
    font-weight: bold;
}
.stTextInput > div > input {
    background-color: #2a1a4f !important; /* Slightly lighter purple */
    color: #e0e0e0 !important; /* Input text color */
    border: 1px solid #f0d9b5 !important; /* Parchment colored border */
    border-radius: 5px !important;
    padding: 10px !important;
    font-family: 'Inter', sans-serif; /* Use Inter for input text */
}

/* Button */
.stButton > button {
    font-family: 'Cinzel Decorative', cursive !important;
    background-color: #f0d9b5 !important; /* Parchment button color */
    color: #120a2b !important; /* Dark text on button */
    border: none !important;
    border-radius: 5px !important;
    padding: 10px 20px !important;
    margin-top: 10px !important;
    cursor: pointer !important;
    transition: background-color 0.3s ease !important;
    text-transform: uppercase !important;
    font-weight: bold !important;
    box-shadow: 3px 3px 5px rgba(0,0,0,0.5); /* Add shadow */
}
.stButton > button:hover {
    background-color: #e0c9a5 !important; /* Darker parchment on hover */
}

/* Status/Spinner */
.stStatus {
    border-left: 5px solid #f0d9b5 !important; /* Parchment color border */
    padding: 15px !important; /* Increased padding */
    background-color: #2a1a4f !important; /* Slightly lighter purple background */
    border-radius: 5px !important;
    margin-top: 20px !important; /* Increased margin */
    margin-bottom: 20px !important;
    box-shadow: 3px 3px 5px rgba(0,0,0,0.5); /* Add shadow */
}
.stStatus [data-testid="stStatusLabel"] { /* Target the label inside status */
     font-family: 'Cinzel Decorative', cursive !important;
     color: #f0d9b5 !important; /* Parchment color for status label */
     font-weight: bold;
}
/* Text inside the status container uses the default body styles */


/* Style markdown blockquotes (used by format_markdown_output) */
blockquote {
    background-color: #f0d9b51a; /* Semi-transparent parchment tint */
    border-left: 4px solid #f0d9b5; /* Parchment colored border */
    margin: 1.5em 10px; /* Adjust margin */
    padding: 0.5em 10px;
    quotes: "\\201C""\\201D""\\2018""\\2019" ;
    color: #e0e0e0; /* Text color */
    font-style: italic; /* Add italic style */
    border-radius: 0 5px 5px 0; /* Rounded border on the right side */
}

/* Style the horizontal rule */
hr {
    border-top: 1px solid #f0d9b5; /* Parchment color border */
    margin: 2em 0;
}

/* Download Button */
.stDownloadButton > button {
     font-family: 'Cinzel Decorative', cursive !important;
     background-color: #5a3e8a !important; /* A distinct color for download */
     color: #e0e0e0 !important; /* Light text */
     border: none !important;
     border-radius: 5px !important;
     padding: 10px 20px !important;
     margin-top: 10px !important;
     cursor: pointer !important;
     transition: background-color 0.3s ease !important;
     text-transform: uppercase !important;
     font-weight: bold !important;
     box-shadow: 3px 3px 5px rgba(0,0,0,0.5); /* Add shadow */
}
.stDownloadButton > button:hover {
    background-color: #6b4f9b !important; /* Lighter shade on hover */
}


</style>
""", unsafe_allow_html=True)


# --- Rest of your app.py code remains below ---

# Ensure API key is set before initializing client
# This logic remains the same, handled in utils.py
from utils import client, call_agent, format_markdown_output, sanitize_filename
from agents import create_agente_buscador, create_agente_planejador, create_agente_redator


# --- Streamlit App Layout ---
st.title("🍳 Baú de receitas") # Uses styled h1

st.write("""
Bem-vindo ao Baú de receitas!
Informe os ingredientes que você tem e nossa equipe de agentes culinários criará uma receita exclusiva para você.
""") # Uses styled body text


# --- User Input ---
# Uses styled st.text_input
ingredients = st.text_input("❓ Por favor, digite os INGREDIENTES sobre o qual você quer criar a receita (ex: frango cozido desfiado, arroz, ervilha):")

# --- Button to trigger the process ---
# Uses styled st.button
if st.button("✨ Gerar Receita"):
    if not ingredients:
        st.warning("Você esqueceu de digitar os ingredientes!")
    elif client is None: # Check if client initialization failed in utils
         # Error message is already displayed in utils.py
         pass # Do nothing here, error is shown on page load or config issue
    else:
        st.write(f"Maravilha! Vamos então buscar receitas com {ingredients}") # Uses styled body text

        # Initialize variable to store the final output before the status block
        recipe_post = ""
        # Use st.status to show progress for the entire agent chain (uses styled st.status)
        with st.status("Criando sua receita...", expanded=True) as status:
            try:
                # Create agent instances within the process using functions from agents.py
                buscador_agent = create_agente_buscador()
                planejador_agent = create_agente_planejador()
                redator_agent = create_agente_redator()

                # --- Call Agent 1 ---
                status.update(label="Passo 1: Buscando receitas compatíveis...", state="running")
                searched_recipes = call_agent(buscador_agent, f"Tópico: {ingredients} \n")
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


                # --- Display Result 3 ---
                # Uses styled st.subheader and st.markdown (blockquote and hr)
                st.subheader(" Receita tirada do Baú de receitas! 🍽️")
                if recipe_post and "Error during agent run" not in recipe_post:
                    st.markdown(format_markdown_output(recipe_post))
                    st.markdown("---") # Horizontal rule uses styled hr
                else:
                    st.warning("Não foi possível gerar a receita.")


                status.update(label="Receita gerada com sucesso!", state="complete")

            except Exception as e:
                st.error(f"Ocorreu um erro durante a geração da receita: {e}")
                status.update(label="Erro na geração da receita.", state="error")

        # --- Download Button ---
        # Uses styled st.download_button
        if recipe_post and "Error during agent run" not in recipe_post:
            download_filename = f"{sanitize_filename(recipe_post)}.txt"

            st.download_button(
                label="Baixar Receita",
                data=recipe_post,
                file_name=download_filename,
                mime="text/plain"
            )


else: # This block executes if the client could not be initialized in utils.py
     st.warning("Por favor, configure sua Google API Key nas Secrets do Streamlit Cloud para usar esta aplicação.")