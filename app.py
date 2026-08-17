import streamlit as st
from google import genai

# Sahifa sozlamalari
st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

# --- CSS DIZAYN ---
st.markdown("""
    <style>
    /* Menyularni yashirish */
    #MainMenu, header, footer, .stAppHeader, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Asosiy kontent pastga yopishmasligi uchun */
    .block-container {
        padding-bottom: 110px !important;
        max-width: 750px !important;
    }

    /* Chat input konteynerini zamonaviy va yaxlit qilish */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 95% !important;
        max-width: 750px !important;
        background-color: #1a1c23 !important;
        border-radius: 16px !important;
        border: 1px solid #333842 !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
        z-index: 999;
        padding: 4px !important;
    }

    /* Ichki elementlarni tozalash va to'g'rilash */
    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
        border: none !important;
    }

    textarea { 
        spellcheck: false !important; 
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# API ni sozlash
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Kalit kiritilmagan!")
else:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input("Savolingizni yozing...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
