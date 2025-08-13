import os
import streamlit as st
import json
from google.cloud import dialogflow_v2 as dialogflow

with open("credentials.json", "w") as f:
    f.write(st.secrets["dialogflow"]["credentials"])

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# ---- CONFIG ----
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
PROJECT_ID = "bankingfinancebot-lfrs"
SESSION_ID = "banking-faq-session"

# ---- FUNCTION TO DETECT INTENT ----
def detect_intent_text(project_id, session_id, text, language_code="en"):
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )

    return response.query_result.fulfillment_text

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Banking & Finance FAQ Bot", page_icon="🏦", layout="wide")

# ---- SIDEBAR ----
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("🏦 Banking & Finance Bot")
    st.markdown("""
    **About:**  
    Ask me about banking services, loans, accounts, credit cards, and more!  
    Powered by **Dialogflow ES** & **Streamlit**.
    """)
    st.markdown("---")
    st.info("💡 Tip: Try asking *'What is the interest rate for savings accounts?'*")

# ---- Chat history ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Handle user input ----
def submit():
    user_msg = st.session_state.input_text.strip()
    if user_msg:
        bot_response = detect_intent_text(PROJECT_ID, SESSION_ID, user_msg)
        st.session_state.chat_history.append(("You", user_msg))
        st.session_state.chat_history.append(("Bot", bot_response))
    st.session_state.input_text = ""  # safe clear here

# ---- Chat UI ----
st.markdown("<h2 style='text-align: center; color: #2E86C1;'>💬 Banking & Finance FAQ Chatbot</h2>", unsafe_allow_html=True)

st.text_input("💬 Type your question here:", key="input_text", on_change=submit)

# ---- Display chat ----
for role, text in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"""
        <div style="background-color:#D6EAF8;color:black; padding:10px; border-radius:10px; margin:5px; text-align:right;">
        <b>🧑‍💼 You:</b> {text}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#E8F6F3; color:black; padding:10px; border-radius:10px; margin:5px; text-align:left;">
        <b>🤖 Bot:</b> {text}
        </div>
        """, unsafe_allow_html=True)






