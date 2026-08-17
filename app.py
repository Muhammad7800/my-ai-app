import streamlit as st
from google import genai

st.set_page_config(page_title="AI Chat", page_icon="🤖")
st.title("🤖 Mening AI Yordamchim")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan! Streamlit Secrets bo'limiga GEMINI_API_KEY ni kiriting.")
else:
    client = genai.Client(api_key=api_key)

    # Chat xotirasini yaratish (sahifa yangilanganda o'chib ketmaydi)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Eski xabarlarni ekranga chiqarish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Foydalanuvchi xabar kiritadigan joy
    if prompt := st.chat_input("Savolingizni yozing..."):
        # Foydalanuvchi xabarini ekranga chiqarish va xotiraga saqlash
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gemini modelidan javob olish
        with st.chat_message("assistant"):
            system_instruction = "Siz do'stona va aqlli AI yordamchisiz. Foydalanuvchi qaysi tilda murojaat qilsa, o'sha tilda ravon va aniq javob bering."
            
            # Barcha chat tarixini Gemini'ga yuborish uchun tayyorlash
            contents = []
            for msg in st.session_state.messages:
                contents.append(f"{msg['role']}: {msg['content']}")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="\n".join(contents),
                config={"system_instruction": system_instruction}
            )

            st.markdown(response.text)

        # AI javobini xotiraga saqlash
        st.session_state.messages.append({"role": "assistant", "content": response.text})
