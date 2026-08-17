import streamlit as st
from google import genai
from PIL import Image
import base64
import io

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
        padding-bottom: 140px !important;
        max-width: 750px !important;
    }

    /* Chat inputni pastda fiks qilish va chiroyli dizayn berish */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 95% !important;
        max-width: 750px !important;
        z-index: 999;
    }

    /* [+] tugmasi joylashuvi va uslubi */
    .upload-btn-container {
        position: fixed !important;
        bottom: 22px !important;
        left: calc(50% - 375px + 15px) !important;
        z-index: 1000;
    }

    @media (max-width: 768px) {
        .upload-btn-container {
            left: 20px !important;
        }
    }

    div.stButton > button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        background-color: #212121 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        border-color: #666666 !important;
        color: #ffffff !important;
    }
    
    textarea { spellcheck: false !important; }
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
    
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=250)

    # Fayl yuklash oynasi ochiq bo'lsa chat input tepasida chiqadi
    uploaded_file = None
    if st.session_state.show_uploader:
        st.markdown('<div style="position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); width: 95%; max-width: 750px; background: #1e1e1e; padding: 10px; border-radius: 12px; border: 1px solid #444; z-index: 1000;">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Rasm yuklang", type=["jpg", "jpeg", "png"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Chap tarafdagi [+] tugmasi
    st.markdown('<div class="upload-btn-container">', unsafe_allow_html=True)
    if st.button("＋"):
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Asosiy chat input
    prompt = st.chat_input("Savolingizni yozing...")

    if prompt:
        img = None
        image_base64 = None
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            img = Image.open(io.BytesIO(bytes_data))
            image_base64 = base64.b64encode(bytes_data).decode()

        with st.chat_message("user"):
            st.markdown(prompt)
            if img: st.image(img, width=250)

        st.session_state.messages.append({"role": "user", "content": prompt, "image_base64": image_base64})
        st.session_state.show_uploader = False

        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                contents = [prompt, img] if img else prompt
                response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
