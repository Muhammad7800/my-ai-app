import streamlit as st
from google import genai
from PIL import Image

st.title("Mening AI Yordamchim")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan! Streamlit Secrets bo'limiga GEMINI_API_KEY ni kiriting.")
else:
    client = genai.Client(api_key=api_key)
    
    user_text = st.text_input("Savolingizni xohlagan tilda yozing:")
    uploaded_file = st.file_uploader("Rasm yuklang (ixtiyoriy):", type=["jpg", "png", "jpeg"])

    if st.button("Yuborish"):
        system_instruction = "Siz har qanday tilda javob bera oladigan ko'p tilli yordamchisiz. Foydalanuvchi qaysi tilda murojaat qilsa yoki rasm yuborsa, o'sha tilda javob bering."
        
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Yuklangan rasm", width=300)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[img, user_text if user_text else "Ushbu rasmni tahlil qiling."],
                config={"system_instruction": system_instruction}
            )
        else:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_text,
                config={"system_instruction": system_instruction}
            )
            
        st.write("### AI Javobi:")
        st.write(response.text)
