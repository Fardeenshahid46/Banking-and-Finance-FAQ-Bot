import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from google.cloud import dialogflow_v2 as dialogflow
from google.cloud.dialogflow_v2.types import TextInput, QueryInput
from google.oauth2 import service_account

# ✅ Load Google Credentials from Streamlit Secrets
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" not in st.secrets:
    st.error("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON not found in Streamlit secrets.")
    st.stop()

google_creds = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

# ✅ Create credentials object
credentials = service_account.Credentials.from_service_account_info(google_creds)
PROJECT_ID = google_creds["project_id"]

# ✅ Dialogflow client
dialogflow_session_client = dialogflow.SessionsClient(credentials=credentials)

# --- Page Config ---
st.set_page_config(page_title="💬 Banking FAQ Chatbot", page_icon="💰", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
.stApp { background: black; }
[data-testid="stSidebar"] { background: gray; }
.user-bubble { background-color: #DCF8C6; padding: 12px 18px; border-radius: 15px; margin: 8px; display: inline-block; font-size: 16px; color: black; font-weight: 500; }
.bot-bubble { background-color: #E8E8E8; padding: 12px 18px; border-radius: 15px; margin: 8px; display: inline-block; font-size: 16px; color: #000000; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712100.png", width=100)
st.sidebar.title("💬 Banking FAQ Chatbot")
st.sidebar.markdown("Ask me anything about banking & finance. I'm here to help you 24/7! 🚀")

# --- Chat State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Title ---
st.markdown("<h2 style='text-align: center; color: #2c3e50;'>💰 Banking FAQ Chatbot</h2>", unsafe_allow_html=True)

# --- Input Box ---
user_input = st.text_input("💡 Type your question here:", key="input_text")

# --- Process Input ---
if user_input:
    st.session_state.chat_history.append(("user", user_input, datetime.now().strftime("%H:%M")))

    session = dialogflow_session_client.session_path(PROJECT_ID, "unique_session_id")
    text_input = TextInput(text=user_input, language_code="en")
    query_input = QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    bot_reply = response.query_result.fulfillment_text

    st.session_state.chat_history.append(("bot", bot_reply, datetime.now().strftime("%H:%M")))

# --- Display Chat History ---
for sender, message, time in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='user-bubble'><b>You:</b> {message} <small style='color:gray;'>⏰ {time}</small></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'><b>Bot:</b> {message} <small style='color:gray;'>⏰ {time}</small></div>", unsafe_allow_html=True)

# --- Clear Chat Button ---
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.session_state["input_text"] = ""
    st.rerun()
