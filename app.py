import streamlit as st
import os
import tempfile
import json
from google.cloud import dialogflow_v2 as dialogflow

service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

# Dialogflow client initialize
client = dialogflow.SessionsClient.from_service_account_info(service_account_info)
# --- Load Google credentials from Streamlit secrets ---
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" not in st.secrets:
    st.error("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON not found in Streamlit secrets.")
    st.stop()

service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
    tmp_file.write(json.dumps(service_account_info).encode())
    tmp_file_path = tmp_file.name

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path

# --- Dialogflow Settings ---
PROJECT_ID = service_account_info["project_id"]
SESSION_ID = "123456"
LANGUAGE_CODE = "en"

def detect_intent_text(project_id, session_id, text, language_code):
    try:
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result.fulfillment_text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="Banking Finance Bot", layout="wide")

# Sidebar
with st.sidebar:
    st.title("Settings")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("<h1 style='text-align:center; color:#2E86C1;'>🏦 Banking & Finance Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Display chat messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; margin:5px 0;">
                <div style="background-color:#DCF8C6; padding:10px 15px; border-radius:15px; max-width:70%; word-wrap:break-word;">
                    {msg['text']}
                </div>
                <img src="https://img.icons8.com/color/48/000000/user-male-circle.png" width="30px" style="margin-left:5px;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-start; margin:5px 0;">
                <img src="https://img.icons8.com/color/48/000000/robot.png" width="30px" style="margin-right:5px;">
                <div style="background-color:#F1F0F0; padding:10px 15px; border-radius:15px; max-width:70%; word-wrap:break-word;">
                    {msg['text']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# User input
user_input = st.text_input("Type your message here...", key="input")

if st.button("Send") and user_input.strip():
    bot_reply = detect_intent_text(PROJECT_ID, SESSION_ID, user_input, LANGUAGE_CODE)
    st.session_state.messages.append({"role": "user", "text": user_input})
    st.session_state.messages.append({"role": "bot", "text": bot_reply})
    st.session_state.input = ""  # clear input after sending
    st.experimental_rerun()

