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
__all__ = ['client', 'MODEL_ID', 'call_agent', 'format_markdown_output', 'sanitize_filename', 'google_search']