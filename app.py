import streamlit as st
from groq import Groq
import uuid
import sqlite3

st.set_page_config(
    page_title="AI Chat", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BAZANI YARATISH VA TEKSHIRISH ---
def init_db():
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            device_id TEXT,
            chat_id TEXT,
            role TEXT,
            content TEXT
        )
    ''')
    
    conn.commit()
    return conn

db_conn = init_db()

# --- QURILMANI ANIQLASH ---
if "device" not in st.query_params:
    st.query_params["device"] = str(uuid.uuid4())
current_device_id = st.query_params["device"]

def get_all_chats(conn, device_id):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM messages WHERE device_id = ?", (device_id,))
    rows = cursor.fetchall()
    chats = {}
    for row in rows:
        cid = row[0]
        cursor.execute("SELECT role, content FROM messages WHERE device_id = ? AND chat_id = ?", (device_id, cid))
        messages = [{"role": r[0], "content": r[1]} for r in cursor.fetchall()]
        chats[cid] = messages
    return chats

def save_message(conn, device_id, chat_id, role, content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (device_id, chat_id, role, content) VALUES (?, ?, ?, ?)", (device_id, chat_id, role, content))
    conn.commit()

def delete_chat_from_db(conn, device_id, chat_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE device_id = ? AND chat_id = ?", (device_id, chat_id))
    conn.commit()

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

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY topilmadi! Iltimos Streamlit Secrets bo'limini tekshiring.")
else:
    client = Groq(api_key=api_key)

    # --- CHAP PANEL ---
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_chat_id = str(uuid.uuid4())
            st.rerun()
        
        st.divider()

        chats = get_all_chats(db_conn, current_device_id)
        chat_ids = list(chats.keys())
        
        if "current_chat_id" not in st.session_state:
            st.session_state.current_chat_id = chat_ids[0] if chat_ids else str(uuid.uuid4())

        for i, cid in enumerate(chat_ids):
            chat_history = chats[cid]
            chat_title = chat_history[0]["content"][:18] + "..." if chat_history else f"Chat {i+1}"
            
            c1, c2 = st.columns([0.75, 0.25])
            with c1:
                if st.button(chat_title, key=f"open_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{cid}", use_container_width=True):
                    delete_chat_from_db(db_conn, current_device_id, cid)
                    st.session_state.current_chat_id = str(uuid.uuid4())
                    st.rerun()

    # --- ASOSIY CHAT OYNASI ---
    current_chat_id = st.session_state.current_chat_id
    current_messages = get_all_chats(db_conn, current_device_id).get(current_chat_id, [])

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
        save_message(db_conn, current_device_id, current_chat_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[{"role": m["role"], "content": m["content"]} for m in current_messages] + [{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    bot_reply = response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"Error: {e}"

                st.markdown(bot_reply)
                save_message(db_conn, current_device_id, current_chat_id, "assistant", bot_reply)
        
        st.rerun()
