import streamlit as st
from google import genai
from PIL import Image
import base64

# Tab sarlavhasi va ikonkasini o'rnatish
st.set_page_config(page_title="Muhammad AI", page_icon="🤖", layout="centered")

# --- TO'LIQ VA YANGILANGAN DIZAYN (CSS) ---
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

    /* Pastdagi yozish qismini cho'zib yubormasdan, ixcham va markazda saqlash */
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

    /* [+] popover tugmasini aniq ko'rinadigan va chiroyli qilish */
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
        margin-bottom: 2px !important;
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

    /* Chat input katagini ixcham qilish */
    div[data-testid="stChatInput"] {
        border-radius: 20px !important;
        min-height: 38px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        font-size: 14px !important;
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

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=220)

    # Pastki qism: [+] popover va chat input
    col1, col2 = st.columns([0.8, 12])

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
        
