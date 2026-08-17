import streamlit as st
from google import genai
import uuid

# Sahifa sozlamalari
st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

# --- CSS DIZAYN ---
st.markdown("""
    <style>
    /* Standart header va menyularni yashirish, lekin yon panel (sidebar) tugmasini qoldirish */
    #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Streamlitning o'z menyu tugmasi chiqishi uchun header qismini qisman ko'rsatamiz */
    header {
        visibility: visible !important;
        background: transparent !important;
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

    # Sessiyada chatlar ro'yxati va joriy chat ID saqlash
    if "chats" not in st.session_state:
        st.session_state.chats = {} # {chat_id: [{"role": "...", "content": "..."}, ...]}
    
    if "current_chat_id" not in st.session_state:
        # Boshlang'ich yangi chat ochish
        initial_id = str(uuid.uuid4())
        st.session_state.current_chat_id = initial_id
        st.session_state.chats[initial_id] = []

    # --- YON PANEL (SIDEBAR) - CHATLAR TARIXI ---
    with st.sidebar:
        st.title("💬 Chatlar tarixi")
        
        # Yangi chat ochish tugmasi
        if st.button("➕ Yangi chat", use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()
        
        st.divider()

        # Mavjud chatlar ro'yxatini chiqarish
        chat_ids = list(st.session_state.chats.keys())
        for i, cid in enumerate(chat_ids):
            chat_history = st.session_state.chats[cid]
            # Chat nomini birinchi xabardan yoki "Chat X" deb olish
            if chat_history:
                chat_title = chat_history[0]["content"][:25] + "..."
            else:
                chat_title = f"Chat {i+1} (Bo'sh)"
            
            # Har bir chat uchun tugma
            if st.button(chat_title, key=cid, use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()

    # Joriy chat xabarlarini olish
    current_messages = st.session_state.chats[st.session_state.current_chat_id]

    # Chat tarixini ekranga chiqarish
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input("Ask a question...")

    if prompt:
        # Foydalanuvchi xabarini qo'shish
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini dan javob olish
        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                # Butun chat tarixini Gemini ga yuborish (kontekst saqlanishi uchun)
                formatted_contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in current_messages]
                
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=prompt # yoki formatted_contents
                    )
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Xatolik yuz berdi: {e}"

                st.markdown(bot_reply)
                current_messages.append({"role": "assistant", "content": bot_reply})
        
        st.rerun()
