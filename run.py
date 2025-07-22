import streamlit as st
import requests
from orders import main as orders_main

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzAbMUZosZP2-IYLagqCutoa4hdXHszQhLL13fW_fyhYaEpAVrG5f0lokyDS1EWoDqq/exec"

# ✅ تحميل CSS
def load_css():
    st.markdown("""
        <style>
        /* خلفية متدرجة */
        body {
            background: linear-gradient(to right, #6a11cb, #2575fc);
        }

        /* تخصيص صفحة ستريمليت */
        .stApp {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }

        /* كارت تسجيل الدخول */
        .login-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 3rem 2rem;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
            max-width: 400px;
            margin: auto;
            margin-top: 100px;
        }

        /* الحقول */
        input {
            border-radius: 10px !important;
            padding: 10px !important;
        }

        /* زر الدخول */
        div.stButton > button {
            background-color: #ffffff;
            color: #2575fc;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            transition: 0.3s ease-in-out;
        }

        div.stButton > button:hover {
            background-color: #2575fc;
            color: white;
            box-shadow: 0 0 10px white;
        }

        h2, h3, h4, p {
            text-align: center;
        }

        </style>
    """, unsafe_allow_html=True)

# ✅ واجهة تسجيل الدخول
def show_login():
    load_css()

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>👋 مرحبًا بك!</h2>", unsafe_allow_html=True)
    st.markdown("<p>الرجاء تسجيل الدخول للمتابعة</p>", unsafe_allow_html=True)

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        with st.spinner("جار التحقق..."):
            try:
                res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "login", "username": username, "password": password})
                if res.status_code == 200 and res.text.strip() == "success":
                    st.success("تم تسجيل الدخول بنجاح ✅")
                    st.session_state.logged_in = True
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            except:
                st.error("حدث خطأ في الاتصال بالخادم")
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ التطبيق الرئيسي
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        show_login()
    else:
        orders_main()

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    main()
