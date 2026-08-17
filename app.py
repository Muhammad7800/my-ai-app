import streamlit as st
from google import genai
from PIL import Image
import base64

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
        padding-bottom: 120px !important;
        max-width: 750px !important;
    }

    /* Input va [+] tugmasi turgan umumiy joylashuv (Pastdan 15px tepada) */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 15px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 750px;
        background-color: transparent;
        z-index: 999;
        box-sizing: border-box;
    }

    /* Ustunlarni mukammal vertikal markazga keltirish */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }

    /* Birinchi ustun kengligi */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex: 0 0 50px !important;
        width: 50px !important;
    }
    
    /* Ikkinchi ustun (Chat input) qolgan joyni egallaydi */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex: 1 1 auto !important;
    }

    /* [+] tugmasi uslubi (To'liq ko'rinadigan va chiroyli) */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        background-color: #212121 !important;
        color: #ffffff !important;
        border: 1px solid #3d3d3d !important;
        font-size: 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
    }

    div[data-testid="stPopoverBody"] {
        background-color: #212121 !important;
        border: 1px solid #333333 !important;
        border-radius: 16px !important;
        padding: 12px !important;
    }

    /* Chat inputni chiroyli qilish */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
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

    # Chat tarixini ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=250)

    # Pastki qism: [+] tugmasi va Chat Input yonma-yon
    col1, col2 = st.columns([1, 14])

    with col1:
        with st.popover("+"):
            uploaded_file = st.file_uploader("Rasm yuklang", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    with col2:
        prompt = st.chat_input("Savolingizni yozing...")

    if prompt:
        img = Image.open(uploaded_file) if uploaded_file else None
        image_base64 = base64.b64encode(uploaded_file.read()).decode() if uploaded_file else None

        with st.chat_message("user"):
            st.markdown(prompt)
            if img: st.image(img, width=250)

        st.session_state.messages.append({"role": "user", "content": prompt, "image_base64": image_base64})

        with st.chat_message("assistant"):
            with st.spinner("O'ylamoqda..."):
                contents = [prompt, img] if img else prompt
                response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
