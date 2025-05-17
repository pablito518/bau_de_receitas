import streamlit as st
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from google import genai
import re
import textwrap
import warnings
# Use st.secrets for API key in Streamlit Cloud
# If running locally, you might still use environment variables or a .env file
# For Streamlit Cloud, the GOOGLE_API_KEY needs to be set in the app secrets
# Instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/secrets-management
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY # Set for google.genai client
except KeyError:
    st.error("API Key not found. Please set the GOOGLE_API_KEY secret in Streamlit Cloud.")
    GOOGLE_API_KEY = None # Prevent further execution if key is missing


# Ensure API key is set before initializing client
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
         st.error(f"Failed to initialize Google GenAI client: {e}")
         client = None # Prevent further execution if client fails

    MODEL_ID = "gemini-2.0-flash" # Or your preferred model ID


    warnings.filterwarnings("ignore")

    # Function to call an agent
    def call_agent(agent: Agent, message_text: str) -> str:
        session_service = InMemorySessionService()
        session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
        runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
        content = types.Content(role="user", parts=[types.Part(text=message_text)])

        final_response = ""
        # Streamlit doesn't handle async iteration directly in this simple flow,
        # but the runner.run method should yield sequentially.
        # We collect all parts into a single response string.
        for event in runner.run(user_id="user1", session_id="session1", new_message=content):
            if event.is_final_response():
                for part in event.content.parts:
                    if part.text is not None:
                        final_response += part.text
                        final_response += "\n" # Add newline between parts if any
        return final_response

    # Function to format text for Markdown display (adapting Colab's to_markdown)
    # We return the formatted string, Streamlit's st.markdown will display it
    def format_markdown_output(text):
        text = text.replace('•', '  *') # Use standard markdown list item
        # Use textwrap for indentation
        indented_text = textwrap.indent(text, '> ', predicate=lambda _: True)
        return indented_text

    ##########################################
    # --- Agent 1: Assistente de cozinha --- #
    ##########################################
    def agente_buscador(topico):
        if not client: return "GenAI client not initialized." # Basic check
        buscador = Agent(
            name="agente_buscador",
            model=MODEL_ID, # Use the defined MODEL_ID
            description="Agente que busca informações no Google",
            tools=[google_search],
            instruction="""
            Você é um cozinheiro assistente de pesquisa. A sua tarefa é usar a ferramenta de busca do google (google_search)
            para recuperar as melhores receitas que contenham somente os ingredientes abaixo, e nada além deles.
            Foque em no máximo 5 receitas relevantes, com base na quantidade e pontuação das avaliações sobre ele.
            Se uma receita tiver poucas avaliações ou avaliações ruins, é possível que ele não seja tão relevante assim e pode ser
            substítuído por outra que tenha mais.
            Após escolher as receitas, utilize o (google_search) para conferir se as receitas
            escolhidas possuem ou não ingredientes além dos indicados abaixo.
            Em caso positivo, elimine estes da lista e apresente uma lista nova.
            Não inclua na lista receitas que sugerem ingredientes adicionais.
            """
        )
        entrada_do_agente_buscador = f"Tópico: {topico} \n"
        #st.info("Chamando Agente 1 (Assistente)...") # Indicate progress
        result = call_agent(buscador, entrada_do_agente_buscador)
        return result

    ################################################
    # --- Agent 2: Cozinheiro --- #
    ################################################
    def agente_planejador(topico, lancamentos_buscados):
        if not client: return "GenAI client not initialized." # Basic check
        cozinheiro = Agent(
            name="agente_planejador",
            model=MODEL_ID, # Use the defined MODEL_ID
            instruction="""
            Você é um cozinheiro especialista em receitas feitas com poucos ingredientes. Com base na lista
            das receitas mais compatíveis buscadas, você deve:
            Você também pode usar usar a ferramenta de pesquisa do google (google_search) para encontrar mais
            informações sobre as receitas e as aprofundar, mas sem alterar as adaptações feitas nas receitas,
            caso haja alguma. Pode, também, sugerir toques adicionais e melhorias com outros ingredientes.
            Ao final, você irá escolher a receita mais relevante entre eles com base nas suas pesquisas
            e retornar essa receita (adaptada, se aplicável), seus pontos mais relevantes, e cuidados ao fazer essa receita.
            Não inclua na lista receitas que sugerem ingredientes adicionais.
            Ao apresentar a receita, não utilize ingredientes adicionais.
            Caso as receitas estejam simples/simplificadas, não adicione mais ingredientes,
            mesmo que a receita original possua tais ingredientes.
            """,
            description="Agente que planeja receitas",
            tools=[google_search]
        )

        entrada_do_agente_planejador = f"Tópico:{topico}\nLançamentos buscados: {lancamentos_buscados}"
        #st.info("Chamando Agente 2 (Cozinheiro)...") # Indicate progress
        result = call_agent(cozinheiro, entrada_do_agente_planejador)
        return result

    ######################################
    # --- Agent 3: Chef --- #
    ######################################
    def agente_redator(topico, plano_de_post):
        if not client: return "GenAI client not initialized." # Basic check
        chef = Agent(
            name="agente_redator",
            model=MODEL_ID, # Use the defined MODEL_ID
            instruction="""
            Você é um Chef de cozinha especializado em fazer explicar receitas passo a passo.
            Você escreve tutoriais para a empresa P&K, a maior escola culinária do Brasil.
            Utilize a receita fornecida e os pontos mais relevantes fornecidos e, com base nisso,
            escreva um passo a passo para um blog sobre o tema indicado.
            Sugira alternativas para os ingredientes, como, por exemplo, a troca de óleo por azeite ou manteiga, se aplicável.
            Você pode usar o (google_search) para detalhar brevemente a história da receita.
            O post deve ser informativo e com linguagem simples. A estrutura deve estar bem dividida e deve ser de fácil compreensão.
            Retorne o post considerando a estrutura:
            ## Título
            ## Introdução
            ## Ingredientes
            ## Modo de Preparo
            ## Dicas
            ## Conclusão
            Não inclua em sua resposta textos que não sejam parte do post.
            """,
            description="Agente redator de tutoriais para blog",
            tools=[google_search]
        )
        entrada_do_agente_redator = f"Tópico: {topico}\nPlano de post: {plano_de_post}"
        #st.info("Chamando Agente 3 (Chef)...") # Indicate progress
        result = call_agent(chef, entrada_do_agente_redator)
        return result

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
        elif not client:
             st.error("Não foi possível iniciar o sistema de agentes. Verifique a configuração da API Key.")
        else:
            st.write(f"Maravilha! Vamos então buscar receitas com {ingredients}")

            # Use st.status to show progress for the entire agent chain
            with st.status("Criando sua receita...", expanded=True) as status:
                try:
                    
                    # --- Call Agent 1 ---
                    status.update(label="Passo 1: Buscando receitas compatíveis...", state="running")
                    searched_recipes = agente_buscador(ingredients)
                    status.update(label="Passo 1 concluído.", state="complete")

                    # --- Display Result 1 ---
                    #st.subheader("📝 Resultado do Agente 1 (Assistente)")
                    #st.markdown(format_markdown_output(searched_recipes))
                    #st.markdown("---") # Horizontal rule

                    # --- Call Agent 2 ---
                    status.update(label="Passo 2: Planejando a receita principal...", state="running")
                    recipe_plan = agente_planejador(ingredients, searched_recipes)
                    status.update(label="Passo 2 concluído.", state="complete")

                    # --- Display Result 2 ---
                    #st.subheader("📝 Resultado do Agente 2 (Cozinheiro)")
                    #st.markdown(format_markdown_output(recipe_plan))
                    #st.markdown("---") # Horizontal rule

                    # --- Call Agent 3 ---
                    status.update(label="Passo 3: Escrevendo o tutorial da receita...", state="running")
                    recipe_post = agente_redator(ingredients, recipe_plan)
                    status.update(label="Passo 3 concluído.", state="complete")

                    # --- Display Result 3 ---
                    st.subheader(" Receita tirada do Baú de receitas! 🍽️")
                    st.markdown(format_markdown_output(recipe_post))
                    st.markdown("---") # Horizontal rule

                    status.update(label="Receita gerada com sucesso!", state="complete") 

                except Exception as e:
                    st.error(f"Ocorreu um erro durante a geração da receita: {e}")
                    status.update(label="Erro na geração da receita.", state="error")

                # This button will appear after the 'with st.status' block finishes
            if recipe_post: # Only show button if a recipe was generated
                # Attempt to extract a filename from the first line of the recipe output
                download_filename = "receita.txt" # Default filename
                try:
                    first_line = recipe_post.strip().split('\n')[0]
                    potential_title = first_line.lstrip('# ').strip() # Remove potential markdown header and strip whitespace

                    if potential_title:
                        # Sanitize the title for use as a filename
                        # Keep alphanumeric, underscore, hyphen. Replace others with underscore.
                        sanitized_title = re.sub(r'[^\w\-]+', '_', potential_title)
                        # Avoid starting/ending with underscore if possible, or multiple underscores
                        sanitized_title = re.sub(r'_+', '_', sanitized_title).strip('_')
                        # Limit length to avoid issues with file systems
                        max_len = 50
                        if len(sanitized_title) > max_len:
                            sanitized_title = sanitized_title[:max_len] # Truncate
                            # Option: add '...' sanitized = sanitized.rstrip('_') + '...'
                        if sanitized_title: # Ensure it's not empty after sanitization
                             download_filename = f"{sanitized_title}.txt"
                        # Else: sanitized_title was empty, use default filename
                    # --- Download Button ---
                    st.download_button(
                        label="Baixar Receita",
                        data=recipe_post, # Provide the raw text content
                        file_name=f"receita_{ingredients.replace(' ', '_')}.txt", # Create a filename based on ingredients
                        mime="text/plain" # Specify the MIME type for a text file
                    )
                except Exception as e:
                    # If any error during title extraction, just use the default filename
                    # st.warning(f"Could not extract a filename from the recipe. Using default name '{download_filename}'. Error: {e}") # Optional: uncomment for debugging title extraction
                    pass # Use default filename

                st.download_button(
                    label="Baixar Receita",
                    data=recipe_post, # Provide the raw text content
                    file_name=download_filename,
                    mime="text/plain" # Specify the MIME type for a text file
                )
