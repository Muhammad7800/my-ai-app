import streamlit as st
from google import genai
import uuid

st.set_page_config(
    page_title="Gemini AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ---
st.markdown("""
    <style>
    #MainMenu, footer, .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-bottom: 120px !important;
        max-width: 800px !important;
        padding-top: 20px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 92% !important;
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
        margin-top: 12vh;
        margin-bottom: 20px;
        padding: 0 10px;
    }
    .welcome-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4b6cb7, #182848);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #888888;
    }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Kalit kiritilmagan!")
else:
    client = genai.Client(api_key=api_key)

    # Sessiyada chatlar saqlanishini ta'minlash
    if "chats" not in st.session_state:
        initial_id = str(uuid.uuid4())
        st.session_state.chats = {initial_id: []}
        st.session_state.current_chat_id = initial_id
    
    if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]

    # --- CHAP PANEL ---
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        
        if st.button("➕ New Chat", use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = []
            st.session_state.current_chat_id = new_id
            st.rerun()
        
        st.divider()

        chat_ids = list(st.session_state.chats.keys())
        for i, cid in enumerate(chat_ids):
            chat_history = st.session_state.chats[cid]
            if chat_history:
                chat_title = chat_history[0]["content"][:18] + "..."
            else:
                chat_title = f"Chat {i+1} (Empty)"
            
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
                        st.session_state.chats = {new_id: []}
                        st.session_state.current_chat_id = new_id
                    else:
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()

    # --- ASOSIY CHAT OYNASI ---
    current_messages = st.session_state.chats[st.session_state.current_chat_id]

    if not current_messages:
        st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">Hello!</div>
                <div class="welcome-subtitle">How can I help you today?</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for message in current_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask a question...")

    if prompt:
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    full_prompt = f"Detect the language of this text: '{prompt}'. Reply to it naturally and strictly in that exact same language. Do not switch to other languages.\n\nText: {prompt}"
                    
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
