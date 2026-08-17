import streamlit as st
from google import genai
import uuid

# Sahifa sozlamalari (sidebar doim ochiq turishi uchun initial_sidebar_state qo'shildi)
st.set_page_config(
    page_title="Gemini AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        max-width: 800px !important;
        padding-top: 30px !important;
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
    .welcome-container {
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 30px;
    }
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4b6cb7, #182848);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #888888;
    }
    </style>
""", unsafe_allow_html=True)

# API ni sozlash
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Kalit kiritilmagan!")
else:
    client = genai.Client(api_key=api_key)

    # Sessiyalar va chatlar tarixini boshqarish
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    
    if "current_chat_id" not in st.session_state:
        initial_id = str(uuid.uuid4())
        st.session_state.current_chat_id = initial_id
        st.session_state.chats[initial_id] = []

    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "🇬🇧 English"

    languages = {
        "🇬🇧 English": {
            "title": "💬 Chat History",
            "new_chat": "➕ New Chat",
            "placeholder": "Ask a question...",
            "thinking": "Thinking...",
            "empty": "Empty",
            "welcome": "Hello!",
            "subtitle": "How can I help you today?"
        },
        "🇺🇿 O'zbekcha": {
            "title": "💬 Chatlar tarixi",
            "new_chat": "➕ Yangi chat",
            "placeholder": "Savolingizni yozing...",
            "thinking": "O'ylamoqda...",
            "empty": "Bo'sh",
            "welcome": "Salom!",
            "subtitle": "Bugun sizga qanday yordam bera olaman?"
        },
        "🇷🇺 Русский": {
            "title": "💬 История чатов",
            "new_chat": "➕ Новый чат",
            "placeholder": "Введите ваш вопрос...",
            "thinking": "Думает...",
            "empty": "Пусто",
            "welcome": "Привет!",
            "subtitle": "Чем я могу помочь вам сегодня?"
        }
    }

    lang_keys = list(languages.keys())
    t = languages[st.session_state.selected_lang]

    # --- CHAP CHETDAGI PANEL (SIDEBAR) ---
    with st.sidebar:
        current_index = lang_keys.index(st.session_state.selected_lang) if st.session_state.selected_lang in lang_keys else 0
        selected_lang = st.selectbox("🌐 Language / Til", lang_keys, index=current_index)
        if selected_lang != st.session_state.selected_lang:
            st.session_state.selected_lang = selected_lang
            st.rerun()

        st.divider()
        st.markdown(f"### {t['title']}")
        
        # Yangi chat ochish tugmasi
        if st.button(t["new_chat"], use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()
        
        st.divider()

        # Chatlar tarixi ro'yxati va o'chirish imkoniyati
        chat_ids = list(st.session_state.chats.keys())
        for i, cid in enumerate(chat_ids):
            chat_history = st.session_state.chats[cid]
            if chat_history:
                chat_title = chat_history[0]["content"][:18] + "..."
            else:
                chat_title = f"Chat {i+1} ({t['empty']})"
            
            c1, c2 = st.columns([0.75, 0.25])
            with c1:
                if st.button(chat_title, key=f"open_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{cid}", use_container_width=True):
                    del st.session_state.chats[cid]
                    if not st.session_state.chats:
                        new_id = str(uuid.uuid4())
                        st.session_state.chats[new_id] = []
                        st.session_state.current_chat_id = new_id
                    elif st.session_state.current_chat_id == cid:
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()

    # --- ASOSIY CHAT OYNASI ---
    if st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]

    current_messages = st.session_state.chats[st.session_state.current_chat_id]

    # Welcome ekrani yoki chat tarixi
    if not current_messages:
        st.markdown(f"""
            <div class="welcome-container">
                <div class="welcome-title">{t["welcome"]}</div>
                <div class="welcome-subtitle">{t["subtitle"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for message in current_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input(t["placeholder"])

    if prompt:
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t["thinking"]):
                try:
                    full_prompt = f"Detect the language of this text: '{prompt}'. Reply to it naturally and strictly in that exact same language (e.g. if it's Uzbek, reply in Uzbek; if Russian, reply in Russian; if English, reply in English). Do not switch to random languages.\n\nText: {prompt}"
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=full_prompt
                    )
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Error / Xatolik: {e}"

                st.markdown(bot_reply)
                current_messages.append({"role": "assistant", "content": bot_reply})
        
        st.rerun()
