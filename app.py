import streamlit as st
from google import genai
from PIL import Image

# Sahifa sozlamalari
st.set_page_config(page_title="Gemini Core", page_icon="⚡", layout="centered")

# Yon menyu (Sidebar) - Custom sozlamalar
with st.sidebar:
    st.title("⚡ Gemini Core")
    st.caption("Shaxsiy Sun'iy Intellekt Yordamchisi")
    st.divider()
    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("⚡ Gemini Core")
st.write("Savollaringizga javob beraman va rasmlarni tahlil qila olaman.")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan! Streamlit Secrets bo'limiga GEMINI_API_KEY ni kiriting.")
else:
    client = genai.Client(api_key=api_key)

    # Chat xotirasi
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tarixdagi xabarlarni ko'rsatish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Rasm yuklash maydoni (ixtiyoriy)
    uploaded_file = st.file_uploader("Rasm biriktirish (ixtiyoriy)", type=["jpg", "jpeg", "png"])
    img = Image.open(uploaded_file) if uploaded_file else None

    if img:
        st.image(img, caption="Biriktirilgan rasm", use_container_width=True)

    # Matn kiritish maydoni
    if prompt := st.chat_input("Savolingizni yozing..."):
        # Foydalanuvchi xabarini ko'rsatish
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # AI javobi
        with st.chat_message("assistant"):
            with st.spinner("O'ylanmoqda..."):
                system_instruction = (
                    "Siz aqlli, samimiy va do'stona AI yordamchisiz. "
                    "Foydalanuvchiga aniq, tushunarli va ravon dilda javob bering."
                )

                # So'rovni tayyorlash
                if img:
                    contents = [prompt, img]
                else:
                    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    contents = history_text

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )

                st.markdown(response.text)

        # AI javobini xotiraga saqlash
        st.session_state.messages.append({"role": "assistant", "content": response.text})
