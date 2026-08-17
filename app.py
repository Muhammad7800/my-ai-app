import streamlit as st
from google import genai
from PIL import Image
import base64

# --- SAHIFA SOZLAMALARI (UI-ni to'liq o'zgartirish) ---
st.set_page_config(page_title="Personal AI Assistant", page_icon="🤖", layout="centered")

# --- CUSTOM CSS (UI-ni 70% o'xshatish va + tugmasini qo'shish) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppHeader {display: none;}
            .stDeployButton {display:none;}
            div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
            div[data-testid="stDecoration"] {visibility: hidden; width: 0px; height: 0px;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            #stDecoration {display:none;}
            
            /* Chat kiritish blokini chiroyli qilish */
            .chat-input-container {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 25px;
                background-color: white;
                margin-top: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            /* Plus tugmasini chiroyli qilish */
            .plus-button-label {
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
                border-radius: 18px;
                border: 1px solid #ccc;
                color: #555;
                background-color: #f8f8f8;
                font-size: 24px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            
            .plus-button-label:hover {
                background-color: #eee;
            }

            /* Yashirin file uploader-ni bosish label-i */
            .stFileUploader label {
                display: none !important;
            }
            
            .stFileUploader > div > button {
                display: none !important;
            }
            
            /* Chat kiritish yozuvini chiroyli qilish */
            [data-testid="stChatInput"] {
                flex-grow: 1;
                border: none !important;
                padding: 0 !important;
            }
            
            /* Chat xabarlarini bloklarini chiroyli qilish */
            .stChatMessage {
                border-radius: 15px !important;
                margin-bottom: 10px !important;
                padding: 10px !important;
            }
            
            div[data-testid="stChatMessage"] div[data-testid="stChatMessageAvatar"] {
                display: none !important;
            }

            [data-testid="stMarkdownContainer"] p {
                margin: 0 !important;
            }
            
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# ------------------------------------------------------------------------------------

# --- LOGO VA SARLAVHA ---
# (Eski sarlavhani o'rniga, faqat logoni qoldiramiz)
st.title("🤖 Personal AI Assistant")

# API kalitni tekshirish
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Kalit kiritilmagan! Streamlit Secrets bo'limiga GEMINI_API_KEY ni kiriting.")
else:
    client = genai.Client(api_key=api_key)

    # Chat xotirasi (sessiya)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tarixdagi xabarlarni ko'rsatish (avatarsiz, sof matn)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image_base64"):
                st.image(base64.b64decode(message["image_base64"]), caption="Biriktirilgan rasm", use_container_width=True)

    # --- CHAT KIRITISH VA PLUS TUGMASI BLOKI ---
    st.divider()
    
    # Kiritish qatorini yaratish (Custom CSS-siz ham st.chat_input o'zi ishlaydi, 
    # lekin bu yerda UI-ni boshqacha qilish va + ni qo'shish uchun CSS ishlatamiz)
    
    # 1. Rasm yuklash maydoni (yashirin)
    uploaded_file = st.file_uploader("Rasmni tanlang", type=["jpg", "jpeg", "png"], key="chat_image_uploader")

    # 2. Plus tugmasi va yozuv maydonini bir qatorga joylashtirish
    # CSS-ni chat inputga ulash uchun maxsus div ishlatamiz
    input_col = st.container()
    
    with input_col:
        # Chat Input (bu avtomatik ravishda pastda turadi, biz faqat UI-ni o'zgartiramiz)
        if prompt := st.chat_input("Savolingizni yozing..."):
            
            # --- YANGI XABARNI TAYYORLASH ---
            # 1. Rasm bormi tekshirish
            img = Image.open(uploaded_file) if uploaded_file else None
            image_base64 = None
            
            if img:
                # Rasmni xotira uchun base64 ga o'tkazish
                uploaded_file.seek(0)
                image_base64 = base64.b64encode(uploaded_file.read()).decode()
            
            # 2. Foydalanuvchi xabarini ko'rsatish
            with st.chat_message("user"):
                st.markdown(prompt)
                if img:
                    st.image(uploaded_file, caption="Siz yuborgan rasm", use_container_width=True)

            # 3. Foydalanuvchi xabarini xotiraga saqlash (rasm base64 kodi bilan birga)
            message_data = {"role": "user", "content": prompt}
            if image_base64:
                message_data["image_base64"] = image_base64
            st.session_state.messages.append(message_data)

            # --- AI JAVOBINI OLISH ---
            with st.chat_message("assistant"):
                with st.spinner("O'ylanmoqda..."):
                    
                    # System instruction: samimiy va ravon javob berish
                    system_instruction = (
                        "Siz aqlli, do'stona va samimiy AI yordamchisiz. "
                        "Foydalanuvchiga aniq, ravon va tushunarli dilda javob bering."
                    )

                    # So'rov tarkibini tayyorlash
                    if img:
                        # Rasm bo'lsa, uni yuborish
                        contents = [prompt, img]
                    else:
                        # Matn bo'lsa, faqat tarixdan matnlarni yuborish
                        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                        contents = history_text

                    # Gemini modelini chaqirish
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents,
                            config={"system_instruction": system_instruction}
                        )
                        ai_response_text = response.text
                        st.markdown(ai_response_text)
                        
                        # AI javobini xotiraga saqlash
                        st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
                        
                    except Exception as e:
                        st.error(f"Xatolik yuz berdi: {str(e)}")

            # --- SOHATNI YANGILASH VA YUKLANGAN RASMNI O'CHIRISH ---
            # (Rasm bir marta yuborilgach, maydon bo'shashi kerak)
            if uploaded_file:
                st.session_state.pop("chat_image_uploader", None)
            st.rerun()

    # --- PLUS TUGMASI LOGIKASINI UI-GA ULANISHI ---
    # Bu qism chat inputidan tashqarida, file_uploader bilan aloqa qilish uchun
    if uploaded_file:
        # Agar rasm yuklangan bo'lsa, chat input maydoni oldiga belgi qo'shish
        st.markdown('<style>[data-testid="stChatInput"] div { display: flex !important; align-items: center !important; gap: 5px !important; } </style>', unsafe_allow_html=True)
        # Plus tugmasini "o'chirib" o'rniga yuborish tugmasini chiroyli ko'rinishga keltiramiz
        st.markdown('<style>.plus-button-label { color: transparent; border: none; background-color: transparent; cursor: default; } </style>', unsafe_allow_html=True)
    else:
        # Rasm yuklanmagan bo'lsa, sof plus tugmasini ko'rsatish (Bu custom CSS yordamida file uploader-ni trigger qiladi)
        # Buni amalga oshirish qiyin, chunki streamlit faqat file_uploader tugmasini beradi.
        # Biz file_uploader tugmasini bosish uchun JS ishlata olmaymiz.
        # Shu sababli, file_uploader-ni sof tugma ko'rinishiga keltirib chat inputga yaqin joylashtiramiz.
        # Bu CSS yuqorida allaqachon .stFileUploader orqali yashirilgan.
        # Foydalanuvchi + ni bosganda aslida ko'rinmaydigan file uploader-ni bosadi.
        
        # CSS orqali + belgisini file uploader ustiga joylashtirish
        st.markdown("""
            <style>
            div[data-testid="stFileUploader"] {
                position: relative;
                width: 40px;
                height: 40px;
                display: inline-block;
                margin-right: 10px;
                margin-top: 10px;
            }
            
            div[data-testid="stFileUploader"] label {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex !important;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: #555;
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                border-radius: 20px;
                cursor: pointer;
                opacity: 1 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            div[data-testid="stFileUploader"] label:hover {
                background-color: #eee;
            }
            div[data-testid="stFileUploader"] label::before {
                content: "+";
                display: block;
            }
            </style>
        """, unsafe_allow_html=True)
