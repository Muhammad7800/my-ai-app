import streamlit as st
from google import genai
from PIL import Image
import base64

# Tab sarlavhasi va ikonkasini o'rnatish
st.set_page_config(page_title="Muhammad AI", page_icon="🤖", layout="centered")

# --- ZAMONAVIY VA IXCHAM DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Streamlit asosiy menyulari va headerlarni yashirish */
    #MainMenu, header, footer, .stAppHeader, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* "Manage app" tugmasini kichraytirib, burchakka yashirish */
    div[class*="viewerBadge"], [data-testid="manage-app-button"] {
        transform: scale(0.65) !important;
        transform-origin: bottom right !important;
        opacity: 0.4 !important;
        transition: opacity 0.3s ease !important;
    }
    div[class*="viewerBadge"]:hover, [data-testid="manage-app-button"]:hover {
        opacity: 1 !important;
    }

    /* Asosiy kontent blokini pastga joylashishga moslash */
    .block-container {
        padding-bottom: 90px !important;
        max-width: 750px !important;
    }

    /* Pastdagi yozish qismini ixcham va markazda saqlash */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 750px;
        background-color: #0e1117;
        padding: 10px 16px;
        z-index: 100;
        box-sizing: border-box;
    }

    /* [+] popover tugmasini chap tarafga chiroyli joylashtirish */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        background-color: #212121 !important;
        color: #ffffff !important;
        border: 1px solid #3d3d3d !important;
        font-size: 22px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 6px !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
    }

    div[data-testid="stPopoverBody"] {
        background-color: #212121 !important;
        border: 1px solid #333333 !important;
        border-radius: 14px !important;
        padding: 10px !important;
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
        max-width: 750px;
        margin: 0 auto;
    }

    /* Chat input katagini ixcham qilish va qizil chiziqni o'chirish */
    div[data-testid="stChatInput"] {
        border-radius: 20px !important;
        min-height: 38px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        font-size: 14px !important;
    }

    textarea {
        spellcheck: false !important;
    }

    /* Boshlang'ich sahifa sarlavhasi dizayni */
    .welcome-container {
        text-align: center;
        margin-top: 25vh;
        color: #e3e3e3;
    }
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# API Kalitini olish
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan! Streamlit Secrets bo'limiga GEMINI_API_KEY ni kiriting.")
else:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Agar chat tarixi bo'sh bo'lsa - Gemini'nikiga o'xshash salomlashish ekrani chiqadi
    if len(st.session_state.messages) == 0:
        st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">Hello, Muhammad</div>
                <div style="font-size: 24px; color: #888888;">What can I help you with today?</div>
            </div>
        """, unsafe_allow_html=True)

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=220)

    # Pastki qism: Chapda [+] popover va o'ngda chat input
    col1, col2 = st.columns([0.6, 11.4])

    with col1:
        with st.popover("+"):
            st.markdown("📎 **Attach file**")
            uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    with col2:
        prompt = st.chat_input("Type a message...")

    if prompt:
        img = Image.open(uploaded_file) if uploaded_file else None
        image_base64 = None

        if uploaded_file:
            uploaded_file.seek(0)
            image_base64 = base64.b64encode(uploaded_file.read()).decode()

        with st.chat_message("user"):
            st.markdown(prompt)
            if img:
                st.image(img, width=220)

        user_msg = {"role": "user", "content": prompt}
        if image_base64:
            user_msg["image_base64"] = image_base64
        st.session_state.messages.append(user_msg)

        # AI Javobi
        with st.chat_message("assistant"):
            with st.spinner("..."):
                system_instruction = "Siz aqlli va do'stona AI yordamchisiz. Qisqa va aniq javob bering."
                
                if img:
                    contents = [prompt, img]
                else:
                    contents = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

        st.rerun()
