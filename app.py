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
        padding-bottom: 160px !important;
        max-width: 750px !important;
    }

    /* Pastki panelni qat'iy fiks qilish */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 15px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 750px;
        background-color: #0e1117;
        padding: 12px 14px;
        border-radius: 20px;
        border: 1px solid #333333;
        z-index: 999;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        box-sizing: border-box;
    }

    /* Ustunlarni bir qatorga tekislash */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        margin-top: 5px;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex: 0 0 45px !important;
        width: 45px !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1 1 auto !important;
    }

    /* [+] tugmasi uslubi */
    div.stButton > button {
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        background-color: #212121 !important;
        color: #ffffff !important;
        border: 1px solid #3d3d3d !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
        color: #ffffff !important;
    }

    /* Chat inputni chiroyli qilish */
    div[data-testid="stChatInput"] {
        position: relative !important;
        bottom: auto !important;
        left: auto !important;
        transform: none !important;
        width: 100% !important;
        background: transparent !important;
        padding: 0 !important;
    }

    div[data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
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
    
    # Fayl yuklash oynasi ochiq/yopiqligini saqlash uchun
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=250)

    # Agar [+] bosilgan bo'lsa, fayl yuklash maydonini ko'rsatish
    uploaded_file = None
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Rasm yuklang", type=["jpg", "jpeg", "png"])

    # Pastki qism: [+] tugmasi va Chat Input yonma-yon
    col1, col2 = st.columns([1, 15])

    with col1:
        if st.button("＋"):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()

    with col2:
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

        # Fayl yuborilgandan keyin uploader'ni yopib qo'yish
        st.session_state.show_uploader = False

        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                contents = [prompt, img] if img else prompt
                response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
