import streamlit as st
from google import genai
from PIL import Image
import base64

st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

# --- UI DIZAYNINI TO'LIQ MOSLASH (CSS) ---
st.markdown("""
    <style>
    /* Streamlit ortiqcha elementlarini yashirish */
    #MainMenu, header, footer, .stAppHeader, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Pastki kiritish blokini bir qatorga keltirish */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
        background-color: #212121;
        border-radius: 24px;
        padding: 4px 12px;
        border: 1px solid #333;
    }

    /* Chat input foni va chegarasini olib tashlash (blok ichiga singdirish) */
    div[data-testid="stChatInput"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    div[data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* File uploader-ni ixcham '+' tugmachasiga aylantirish */
    div[data-testid="stFileUploader"] {
        width: 38px !important;
        margin-bottom: 6px !important;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        min-height: unset !important;
    }

    div[data-testid="stFileUploader"] label, 
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    div[data-testid="stFileUploader"] button {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        border: none !important;
        background-color: #2f2f2f !important;
        color: #ffffff !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    div[data-testid="stFileUploader"] button:hover {
        background-color: #424242 !important;
    }

    /* Chat xabarlarini bezash */
    .stChatMessage {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

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
                st.image(base64.b64decode(message["image_base64"]), width=250)

    # Pastki qator: [+] tugmasi va Chat Input birga
    col1, col2 = st.columns([1, 15])

    with col1:
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    with col2:
        prompt = st.chat_input("Savolingizni yozing...")

    if prompt:
        img = Image.open(uploaded_file) if uploaded_file else None
        image_base64 = None

        if uploaded_file:
            uploaded_file.seek(0)
            image_base64 = base64.b64encode(uploaded_file.read()).decode()

        # Foydalanuvchi xabari
        with st.chat_message("user"):
            st.markdown(prompt)
            if img:
                st.image(img, width=250)

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
