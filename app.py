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

    # Sessiyalar va chatlar tarixini boshqarish
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    
    if "current_chat_id" not in st.session_state:
        initial_id = str(uuid.uuid4())
        st.session_state.current_chat_id = initial_id
        st.session_state.chats[initial_id] = []

    # --- YON PANEL (SIDEBAR) VA TILLAR ---
    with st.sidebar:
        languages = {
            "🇬🇧 English": {
                "title": "💬 Chat History",
                "new_chat": "➕ New Chat",
                "placeholder": "Ask a question...",
                "thinking": "Thinking...",
                "empty": "Empty"
            },
            "🇺🇿 O'zbekcha": {
                "title": "💬 Chatlar tarixi",
                "new_chat": "➕ Yangi chat",
                "placeholder": "Savolingizni yozing...",
                "thinking": "O'ylamoqda...",
                "empty": "Bo'sh"
            },
            "🇷🇺 Русский": {
                "title": "💬 История чатов",
                "new_chat": "➕ Новый чат",
                "placeholder": "Введите ваш вопрос...",
                "thinking": "Думает...",
                "empty": "Пусто"
            },
            "🇹🇷 Türkçe": {
                "title": "💬 Sohbet Geçmişi",
                "new_chat": "➕ Yeni Sohbet",
                "placeholder": "Bir soru sorun...",
                "thinking": "Düşünüyor...",
                "empty": "Boş"
            },
            "🇮🇹 Italiano": {
                "title": "💬 Cronologia chat",
                "new_chat": "➕ Nuova chat",
                "placeholder": "Fai una domanda...",
                "thinking": "Sto pensando...",
                "empty": "Vuoto"
            },
            "🇪🇸 Español": {
                "title": "💬 Historial de chats",
                "new_chat": "➕ Nuevo chat",
                "placeholder": "Haz una pregunta...",
                "thinking": "Pensando...",
                "empty": "Vacío"
            },
            "🇫🇷 Français": {
                "title": "💬 Historique des chats",
                "new_chat": "➕ Nouveau chat",
                "placeholder": "Posez une question...",
                "thinking": "Réflexion...",
                "empty": "Vide"
            },
            "🇩🇪 Deutsch": {
                "title": "💬 Chat-Verlauf",
                "new_chat": "➕ Neuer Chat",
                "placeholder": "Stellen Sie eine Frage...",
                "thinking": "Denkt nach...",
                "empty": "Leer"
            },
            "🇸🇦 العربية": {
                "title": "💬 سجل المحادثات",
                "new_chat": "➕ دردشة جديدة",
                "placeholder": "اطرح سؤالاً...",
                "thinking": "جاري التفكير...",
                "empty": "فارغ"
            },
            "🇨🇳 中文": {
                "title": "💬 聊天记录",
                "new_chat": "➕ 新建聊天",
                "placeholder": "请输入您的问题...",
                "thinking": "思考中...",
                "empty": "空"
            },
            "🇰🇷 한국어": {
                "title": "💬 대화 기록",
                "new_chat": "➕ 새 대화",
                "placeholder": "질문을 입력하세요...",
                "thinking": "생각 중...",
                "empty": "비어 있음"
            },
            "🇯🇵 日本語": {
                "title": "💬 チャット履歴",
                "new_chat": "➕ 新しいチャット",
                "placeholder": "質問を入力してください...",
                "thinking": "考え中...",
                "empty": "空"
            }
        }

        lang_keys = list(languages.keys())

        if "selected_lang" not in st.session_state:
            st.session_state.selected_lang = "🇬🇧 English"
        
        current_index = lang_keys.index(st.session_state.selected_lang) if st.session_state.selected_lang in lang_keys else 0

        selected_lang = st.selectbox("🌐 Language / Til", lang_keys, index=current_index)
        st.session_state.selected_lang = selected_lang
        t = languages[selected_lang]

        st.divider()
        st.title(t["title"])
        
        # Yangi chat ochish tugmasi
        if st.button(t["new_chat"], use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()
        
        st.divider()

        # Chatlar tarixi ro'yxati va har birini o'chirish imkoniyati
        chat_ids = list(st.session_state.chats.keys())
        for i, cid in enumerate(chat_ids):
            chat_history = st.session_state.chats[cid]
            if chat_history:
                chat_title = chat_history[0]["content"][:20] + "..."
            else:
                chat_title = f"Chat {i+1} ({t['empty']})"
            
            # Har bir chat qatorini ustunlarga bo'lish (Chatni ochish va o'chirish tugmasi uchun)
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                if st.button(chat_title, key=f"open_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"del_{cid}", use_container_width=True):
                    # Chatni o'chirish
                    del st.session_state.chats[cid]
                    # Agar hamma chatlar o'chib ketsa, yangi bo'sh chat ochish
                    if not st.session_state.chats:
                        new_id = str(uuid.uuid4())
                        st.session_state.chats[new_id] = []
                        st.session_state.current_chat_id = new_id
                    elif st.session_state.current_chat_id == cid:
                        # Agar o'chirilgan chat hozir ochilgan bo'lsa, boshqa mavjud chatga o'tish
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()

    # Agar joriy chat ID xatolik tufayli mavjud bo'lmasa, uni to'g'rilash
    if st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]

    # Joriy chat xabarlari
    current_messages = st.session_state.chats[st.session_state.current_chat_id]

    # Chat tarixini chiqarish
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
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=prompt
                    )
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Error / Xatolik: {e}"

                st.markdown(bot_reply)
                current_messages.append({"role": "assistant", "content": bot_reply})
        
        st.rerun()
