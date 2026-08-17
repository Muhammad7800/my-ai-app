import streamlit as st
from google import genai
import uuid

# Sahifa sozlamalari
st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

# --- CSS DIZAYN ---
st.markdown("""
    <style>
    #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    header {
        visibility: visible !important;
        background: transparent !important;
    }
    .block-container {
        padding-bottom: 110px !important;
        max-width: 750px !important;
    }
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

    # Sessiyalar va tilni boshqarish
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    
    if "current_chat_id" not in st.session_state:
        initial_id = str(uuid.uuid4())
        st.session_state.current_chat_id = initial_id
        st.session_state.chats[initial_id] = []

    # --- YON PANEL (SIDEBAR) ---
    with st.sidebar:
        # Tilni tanlash
        selected_lang = st.selectbox("🌐 Language / Til", ["O'zbekcha", "English"])
        
        # Tilga mos so'zlar lug'ati
        texts = {
            "O'zbekcha": {
                "title": "💬 Chatlar tarixi",
                "new_chat": "➕ Yangi chat",
                "placeholder": "Savolingizni yozing...",
                "thinking": "O'ylamoqda...",
                "empty": "Bo'sh"
            },
            "English": {
                "title": "💬 Chat History",
                "new_chat": "➕ New Chat",
                "placeholder": "Ask a question...",
                "thinking": "Thinking...",
                "empty": "Empty"
            }
        }
        t = texts[selected_lang]

        st.divider()
        st.title(t["title"])
        
        # Yangi chat ochish tugmasi
        if st.button(t["new_chat"], use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()
        
        st.divider()

        # Chatlar tarixi ro'yxati
        chat_ids = list(st.session_state.chats.keys())
        for i, cid in enumerate(chat_ids):
            chat_history = st.session_state.chats[cid]
            if chat_history:
                chat_title = chat_history[0]["content"][:25] + "..."
            else:
                chat_title = f"Chat {i+1} ({t['empty']})"
            
            if st.button(chat_title, key=cid, use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()

    # Joriy chat xabarlari
    current_messages = st.session_state.chats[st.session_state.current_chat_id]

    # Chat tarixini chiqarish
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input (Tanlangan tilga qarab o'zgaradi)
    prompt = st.chat_input(t["placeholder"])

    if prompt:
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t["thinking"]):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=prompt
                    )
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Xatolik: {e}"

                st.markdown(bot_reply)
                current_messages.append({"role": "assistant", "content": bot_reply})
        
        st.rerun()
