import streamlit as st
import os
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


from google import genai
# Ensure API key is set before initializing client
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
         st.error(f"Failed to initialize Google GenAI client: {e}")
         client = None # Prevent further execution if client fails

    MODEL_ID = "gemini-2.0-flash" # Or your preferred model ID

    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search
    from google.genai import types
    from datetime import date
    import textwrap
    # Removed IPython.display imports as they are for notebooks

    import warnings
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
    def agente_buscador(topico, data_de_hoje):
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
        entrada_do_agente_buscador = f"Tópico: {topico} \nData de hoje: {data_de_hoje}"
        st.info("Chamando Agente 1 (Assistente)...") # Indicate progress
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
        st.info("Chamando Agente 2 (Cozinheiro)...") # Indicate progress
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
            """,
            description="Agente redator de tutoriais para blog",
            tools=[google_search]
        )
        entrada_do_agente_redator = f"Tópico: {topico}\nPlano de post: {plano_de_post}"
        st.info("Chamando Agente 3 (Chef)...") # Indicate progress
        result = call_agent(chef, entrada_do_agente_redator)
        return result

    # --- Streamlit App Layout ---
    st.title("🍳 Gerador de Receitas com Sobras")

    st.write("""
    Bem-vindo ao Gerador de Receitas com Sobras!
    Informe os ingredientes que você tem e nossa equipe de agentes culinários criará uma receita exclusiva para você.
    """)

    # --- User Input ---
    topico = st.text_input("❓ Por favor, digite os INGREDIENTES sobre o qual você quer criar a receita (ex: frango cozido desfiado, arroz, ervilha):")

    # --- Button to trigger the process ---
    if st.button("✨ Gerar Receita"):
        if not topico:
            st.warning("Você esqueceu de digitar os ingredientes!")
        elif not client:
             st.error("Não foi possível iniciar o sistema de agentes. Verifique a configuração da API Key.")
        else:
            st.write(f"Maravilha! Vamos então buscar receitas com {topico}")

            # Use st.status to show progress for the entire agent chain
            with st.status("Criando sua receita...", expanded=True) as status:
                try:
                    data_de_hoje = date.today().strftime("%Y-%m-%d") # Get current date

                    # --- Call Agent 1 ---
                    status.update(label="Passo 1: Buscando receitas compatíveis...", state="running")
                    lancamentos_buscados = agente_buscador(topico, data_de_hoje)
                    status.update(label="Passo 1 concluído.", state="complete")

                    # --- Display Result 1 ---
                    st.subheader("📝 Resultado do Agente 1 (Assistente)")
                    st.markdown(format_markdown_output(lancamentos_buscados))
                    st.markdown("---") # Horizontal rule

                    # --- Call Agent 2 ---
                    status.update(label="Passo 2: Planejando a receita principal...", state="running")
                    plano_de_post = agente_planejador(topico, lancamentos_buscados)
                    status.update(label="Passo 2 concluído.", state="complete")

                    # --- Display Result 2 ---
                    st.subheader("📝 Resultado do Agente 2 (Cozinheiro)")
                    st.markdown(format_markdown_output(plano_de_post))
                    st.markdown("---") # Horizontal rule

                    # --- Call Agent 3 ---
                    status.update(label="Passo 3: Escrevendo o tutorial da receita...", state="running")
                    rascunho_de_post = agente_redator(topico, plano_de_post)
                    status.update(label="Passo 3 concluído.", state="complete")

                    # --- Display Result 3 ---
                    st.subheader("📝 Resultado do Agente 3 (Chef)")
                    st.markdown(format_markdown_output(rascunho_de_post))
                    st.markdown("---") # Horizontal rule

                    status.update(label="Receita gerada com sucesso!", state="complete")

                except Exception as e:
                    st.error(f"Ocorreu um erro durante a geração da receita: {e}")
                    status.update(label="Erro na geração da receita.", state="error")