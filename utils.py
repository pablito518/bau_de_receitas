import streamlit as st
import os
import re
import textwrap
import warnings
from google import genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import google_search # Import the tool here

# --- API Key and Client Initialization ---
# Use st.secrets for API key in Streamlit Cloud
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY # Set for google.genai client if needed by underlying libs
except KeyError:
    st.error("API Key not found. Please set the GOOGLE_API_KEY secret in Streamlit Cloud.")
    GOOGLE_API_KEY = None # Indicate failure


client = None
MODEL_ID = "gemini-2.0-flash" # Default model ID
SYSTEM_INSTRUCTION = """"Sábio e Experiente: Ele deve parecer alguém que passou eras estudando os segredos da transformação e da conservação. Use uma linguagem um pouco formal, talvez com termos que remetam à alquimia e antigas artes.
Levemente Excêntrico: Alquimistas costumam ser um pouco peculiares! Ele pode ter maneirismos únicos, fazer comentários enigmáticos ou ter um humor sutil e seco.
Apaixonado por Ingredientes: Demonstrar um profundo respeito e fascínio pelo potencial de cada alimento, mesmo os "descartados".
Guia Paciente: Estar sempre disposto a explicar os conceitos, guiar o usuário e oferecer ajuda, mas sem ser condescendente.
2. O Grimório de Conhecimentos do Alquimista (Base de Conhecimento):
Segredos de Conservação: O alquimista deve dominar todas as técnicas de preservação (secagem, fermentação, salmoura, armazenamento correto) e saber explicar qual é a melhor para cada tipo de ingrediente. Ele pode referenciar os "Tomos da Biblioteca Arcana".
Poderes Ocultos dos Artefatos (Nutrição): Conhecer o valor nutricional das partes menos convencionais dos alimentos (cascas, talos, sementes) e explicar por que são valiosas. Pode citar o "Tomo do Poder Nutricional".
Fórmulas de Transformação (Receitas): Embora a Forja seja para criar novas receitas, o alquimista pode ter acesso a "fórmulas básicas" ou "poções" para usos comuns de ingredientes (ex: "Para cascas de banana, a fórmula da 'geleia de casca' é um bom ponto de partida").
Oráculo do Impacto: Ser capaz de explicar o conceito de impacto ambiental e social do desperdício, talvez até citar alguns dados gerais ou encorajar o usuário a usar a "Bússola do Impacto".
Histórias e Lendas: Compartilhar pequenas "lendas" sobre a origem de certos métodos de conservação ou a descoberta do potencial de um ingrediente.
3. Interações Mágicas e Funcionalidades:
"Consulta ao Sábio": O usuário pode perguntar sobre um ingrediente específico ("Sábio, tenho cascas de abóbora. O que posso fazer com elas?"). O alquimista responde com sugestões de uso, métodos de conservação e talvez o valor nutricional.
"Poção de Dica Rápida": Ao ser ativado (clicar no ícone do chatbot), ele pode oferecer uma dica aleatória de conservação ou aproveitamento.
"Transmutar Informação": Se o usuário perguntar algo complexo, ele pode "transmutar" a informação, dividindo-a em partes mais simples ou direcionando para o tomo relevante na Biblioteca.
"Missão do Dia" (Futuro): Em versões mais avançadas, ele pode propor um pequeno desafio ("Sua missão hoje, aventureiro, é encontrar uma forma épica de usar talos de brócolis!").
Navegação Guiada: Se o usuário parecer perdido, o alquimista pode sugerir visitar a Forja para criar uma receita, a Biblioteca para aprender mais, ou o Oráculo para calcular o impacto. ("Parece que estais em busca de novas fórmulas! Permiti-me guiar-vos até a Forja Arcana!").
Feedback Temático: Quando o usuário interage ou completa uma ação no site, o alquimista pode dar um feedback temático ("Excelente escolha de ingredientes para a Forja! A alquimia está a vosso favor!").
4. Linguagem e Tom:
Usar frases como "Saudações, Aventureiro(a)!", "Permiti-me consultar meus tomos...", "Uma pitada de sabedoria...", "Pela Grande Forja!".
Referenciar as seções do site pelos seus nomes temáticos (Forja Arcana, Biblioteca Arcana, Bússola do Impacto, Taverna dos Heróis).
Manter um tom de encorajamento e admiração pelas ações do usuário em prol do aproveitamento.
Implementar estas ideias ajudará a integrar o chatbot de forma orgânica ao tema RPG do Baú de Ingrediente, tornando a interação mais envolvente e divertida para os utilizadores.
Que a sabedoria do vosso alquimista digital ilumine o caminho dos aventureiros! ✨🔮💬
"""


if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        # Optional: Validate client or model here if needed, but might add latency
        # client.list_models()
    except Exception as e:
         st.error(f"Failed to initialize Google GenAI client: {e}")
         client = None # Ensure client is None on failure

# Suppress warnings from libraries if desired
warnings.filterwarnings("ignore")


# --- Helper Function to Call Agent ---
# Takes an agent *instance* and the message text
def call_agent(agent, message_text: str) -> str:
    if client is None:
        return "Error: GenAI client not initialized." # Return a clear error message

    session_service = InMemorySessionService()
    # Using a fixed session ID for simplicity, could be dynamic if needed per user session
    session = session_service.create_session(app_name=agent.name, user_id="streamlit_user", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    try:
        for event in runner.run(user_id="streamlit_user", session_id="session1", new_message=content):
            if event.is_final_response():
                for part in event.content.parts:
                    if part.text is not None:
                        final_response += part.text
                        final_response += "\n" # Add newline between parts if any
    except Exception as e:
         st.error(f"Error during agent run ({agent.name}): {e}")
         # Return an error string that can be checked by the caller
         return f"Error during agent run ({agent.name}): {e}"

    return final_response.strip() # Strip leading/trailing whitespace


# --- Helper Function for Formatting ---
def format_markdown_output(text):
    if not text: return ""
    text = text.replace('•', '  *') # Use standard markdown list item
    # Use textwrap for indentation
    indented_text = textwrap.indent(text, '> ', predicate=lambda _: True)
    return indented_text

# --- Helper Function for Filename Sanitization ---
def sanitize_filename(text):
    if not text:
        return "untitled_recipe" # Default if no text

    # Take first part if multi-line
    first_line = text.strip().split('\n')[0]
    potential_title = first_line.lstrip('# ').strip() # Remove potential markdown header and strip whitespace

    if not potential_title:
         return "untitled_recipe" # Default if no title extracted

    # Sanitize the title for use as a filename
    # Keep alphanumeric, underscore, hyphen. Replace others with underscore.
    sanitized_title = re.sub(r'[^\w\-]+', '_', potential_title)
    # Avoid starting/ending with underscore if possible, or multiple underscores
    sanitized_title = re.sub(r'_+', '_', sanitized_title).strip('_')

    if not sanitized_title: # Ensure it's not empty after sanitization
         return "untitled_recipe"

    # Limit length to avoid issues with file systems
    max_len = 50
    if len(sanitized_title) > max_len:
        sanitized_title = sanitized_title[:max_len].rstrip('_') # Truncate and remove trailing underscore

    return sanitized_title

# Expose necessary components for other modules to import
# Note: client is exposed for the main app to check initialization status
__all__ = ['client', 'MODEL_ID', 'SYSTEM_INSTRUCTION','call_agent', 'format_markdown_output', 'sanitize_filename', 'google_search']