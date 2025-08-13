import streamlit as st
import os
import tempfile
from google.cloud import dialogflow
import json
from datetime import datetime
from google.cloud.dialogflow_v2.types import TextInput, QueryInput

# --- Fix AttrDict serialization issue ---
creds_dict = dict(st.secrets["dialogflow"])  # Convert AttrDict to normal dict
creds_str = creds_dict["credentials"] if "credentials" in creds_dict else json.dumps(creds_dict)
if not isinstance(creds_str, str):
    creds_str = json.dumps(creds_str)

# Save credentials to temporary JSON file
with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp:
    temp.write(creds_str)
    temp_path = temp.name

# Set GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path

# Dialogflow client setup
dialogflow_session_client = dialogflow.SessionsClient() 
PROJECT_ID = json.loads(creds_str)["project_id"]

# --- Page Config ---
st.set_page_config(page_title="💬 Banking FAQ Chatbot", page_icon="💰", layout="centered")

# --- Custom CSS for Attractive UI ---
st.markdown("""
<style>
/* Gradient background */
.stApp {
    background: black;
}

/* Glassmorphism Sidebar */
[data-testid="stSidebar"] {
    background:gray;
    backdrop-filter: blur(8px);
    border-right: 1px solid rgba(0, 0, 0, 0.05);
}

/* Chat bubbles with better text visibility */
.user-bubble {
    background-color: #DCF8C6;
    padding: 12px 18px;
    border-radius: 15px;
    margin: 8px;
    display: inline-block;
    font-size: 16px;
    color: black;
    font-weight: 500;
    animation: fadeIn 0.4s ease-in-out;
}
.bot-bubble {
    background-color: #E8E8E8;
    padding: 12px 18px;
    border-radius: 15px;
    margin: 8px;
    display: inline-block;
    font-size: 16px;
    font-weight: 500;
    color: #000000;
    animation: fadeIn 0.4s ease-in-out;
}

/* Input box visible highlight */
input[type="text"] {
    border: 2px solid #4CAF50 ;
    border-radius: 8px ;
    padding: 10px ;
    font-family: "Roboto", sans-serif;
    font-size: 15px ;
    background-color: #ffffff ;
    color: black;
}

/* Animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(6px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712100.png", width=100)
st.sidebar.title("💬 Banking FAQ Chatbot")
st.sidebar.markdown("Ask me anything about banking & finance. I'm here to help you 24/7! 🚀")
st.sidebar.info("Powered by Dialogflow & Streamlit")

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
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for sender, message, time in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='user-bubble'><b>You:</b> {message} <small style='color:gray;'>⏰ {time}</small></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'><b>Bot:</b> {message} <small style='color:gray;'>⏰ {time}</small></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
# --- Clear Chat Button ---
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.clear()  # sab keys delete
    st.session_state.chat_history = []
    st.session_state["input_text"] = ""
    st.rerun()
