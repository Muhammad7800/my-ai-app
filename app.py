import streamlit as st
from google import genai
from PIL import Image
import base64

st.set_page_config(page_title="Gemini AI", page_icon="⚡", layout="centered")

# --- UI DIZAYNINI O'ZGARTIRISH (CSS) ---
st.markdown("""
    <style>
    /* Streamlit menyulari va sarlavhalarini yashirish */
    #MainMenu, header, footer, .stAppHeader, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Asosiy kontent pastki qismdagi inputga yopib qolmasligi uchun bo'sh joy */
    .block-container {
        padding-bottom: 100px !important;
        max-width: 750px !important;
    }

    /* Pastdagi input va [+] tugmasi turgan qismni ekranning pastiga qadash (fixed) */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 750px;
        background-color: #0e1117;
        padding: 12px 16px;
        z-index: 100;
        box-sizing: border-box;
    }

    /* Popover (+) tugmasini aylanali qilib bezash */
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
        margin-bottom: 2px !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
    }

    /* Popover ichidagi menyuni qorong'i uslubga o'tkazish */
    div[data-testid="stPopoverBody"] {
        background-color: #212121 !important;
        border: 1px solid #333333 !important;
        border-radius: 16px !important;
        padding: 12px !important;
    }

    /* Pastki elementlarni bitta qatorga tekislash */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
        max-width: 750px;
        margin: 0 auto;
    }

    /* Chat input-ni chiroyli qilish */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
    }
    
    textarea {
        spellcheck: false !important;
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

    # Pastki kiritish qatori: [+] Popover tugmasi va Chat Input
    col1, col2 = st.columns([1, 12])

    with col1:
        # [+] tugmasi bosilganda ochiladigan popup menyu
        with st.popover("+"):
            st.markdown("📎 **Fayl biriktirish**")
            uploaded_file = st.file_uploader("Rasm yuklang", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

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
