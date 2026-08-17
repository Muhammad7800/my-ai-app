import streamlit as st
from groq import Groq
import uuid
import sqlite3
import base64

st.set_page_config(
    page_title="AI Vision Chat", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    #MainMenu, footer, .stDeployButton { display: none !important; }
    .block-container {
        padding-bottom: 130px !important;
        max-width: 800px !important;
        padding-top: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY topilmadi!")
else:
    client = Groq(api_key=api_key)

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
            history = chats[cid]
            title = history[0]["content"][:18] + "..." if history else f"Chat {i+1}"
            c1, c2 = st.columns([0.75, 0.25])
            with c1:
                if st.button(title, key=f"open_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{cid}", use_container_width=True):
                    delete_chat_from_db(db_conn, current_device_id, cid)
                    st.session_state.current_chat_id = str(uuid.uuid4())
                    st.rerun()

    current_chat_id = st.session_state.current_chat_id
    current_messages = get_all_chats(db_conn, current_device_id).get(current_chat_id, [])

    if not current_messages:
        st.markdown("<h2 style='text-align: center; margin-top: 15vh;'>AI Vision Chat</h2>", unsafe_allow_html=True)
    else:
        for msg in current_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Rasm yuklash tugmasi va input
    uploaded_file = st.file_uploader("Rasm yuklash (ixtiyoriy)", type=["png", "jpg", "jpeg"])
    prompt = st.chat_input("Xabar yozing...")

    if prompt or uploaded_file:
        user_content = prompt if prompt else "Ushbu rasmni tahlil qilib bering:"
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            # Multimodal format uchun tayyorlash
            content_payload = [
                {"type": "text", "text": user_content},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        else:
            content_payload = user_content

        save_message(db_conn, current_device_id, current_chat_id, "user", user_content)
        with st.chat_message("user"):
            if uploaded_file:
                st.image(uploaded_file, width=250)
            st.markdown(user_content)

        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                try:
                    # Vision model ishlatiladi
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role": "user", "content": content_payload}],
                        temperature=0.7
                    )
                    bot_reply = response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"Xatolik: {e}"

                st.markdown(bot_reply)
                save_message(db_conn, current_device_id, current_chat_id, "assistant", bot_reply)
        st.rerun()
