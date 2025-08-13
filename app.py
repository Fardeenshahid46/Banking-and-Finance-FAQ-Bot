import streamlit as st
import os
import tempfile
import json
from google.cloud import dialogflow_v2 as dialogflow

# --- Check & load Google Service Account from Streamlit secrets ---
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" not in st.secrets:
    st.error("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON not found in Streamlit secrets.")
    st.stop()

# JSON ko Python dict me convert
service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

# Temporary file banani for credentials
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
    tmp_file.write(json.dumps(service_account_info).encode())
    tmp_file_path = tmp_file.name

# Set env variable for Google API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path

# --- Dialogflow Settings ---
PROJECT_ID = service_account_info["project_id"]
SESSION_ID = "123456"
LANGUAGE_CODE = "en"

def detect_intent_text(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

# --- Streamlit UI ---
st.set_page_config(page_title="Banking Finance Bot", layout="centered")
st.title("🏦 Banking & Finance Chatbot")

user_input = st.text_input("Type your question:")

if st.button("Ask"):
    if user_input.strip():
        bot_reply = detect_intent_text(PROJECT_ID, SESSION_ID, user_input, LANGUAGE_CODE)
        st.success(f"💬 Bot: {bot_reply}")
    else:
        st.warning("Please type something before asking.")
