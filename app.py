import streamlit as st
from google import genai
from PIL import Image
import base64

st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    #MainMenu, header, footer, .stAppHeader, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    .block-container {
        padding-bottom: 100px !important;
        max-width: 750px !important;
    }

    /* Input va [+] tugmasini pastdan 15px yuqoriga surish */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 15px; 
        left: 50%;
        transform: translateX(-50%);
        width: 95%;
        max-width: 750px;
        background-color: #0e1117;
        padding: 10px 16px;
        z-index: 999;
        box-sizing: border-box;
    }

    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        background-color: #212121 !important;
        color: #ffffff !important;
        border: 1px solid #3d3d3d !important;
        font-size: 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
        max-width: 750px;
        margin: 0 auto;
    }

    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan!")
else:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), width=250)

    # Ustunlar
    col1, col2 = st.columns([0.8, 12])

    with col1:
        with st.popover("+"):
            uploaded_file = st.file_uploader("Rasm", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

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
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, img] if img else prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
