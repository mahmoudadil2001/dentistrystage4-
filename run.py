import streamlit as st
import requests
from orders import main as orders_main

# 🔗 رابط السكربت الخاص بتسجيل الاسم والقروب في Google Sheets
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzAbMUZosZP2-IYLagqCutoa4hdXHszQhLL13fW_fyhYaEpAVrG5f0lokyDS1EWoDqq/exec"

# 🎨 تحميل CSS مخصص لجمالية الواجهة
def load_custom_css():
    st.markdown("""
        <style>
            /* الخلفية */
            body {
                background-color: #f3f4f6;
            }

            /* صندوق تسجيل الدخول */
            .login-container {
                background-color: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
                margin: auto;
            }

            /* العنوان */
            .login-container h2 {
                text-align: center;
                color: #1f2937;
                margin-bottom: 1.5rem;
            }

            /* الحقول */
            .login-container input {
                width: 100%;
                padding: 0.75rem;
                margin-bottom: 1rem;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                font-size: 1rem;
            }

            /* زر الدخول */
            .login-container button {
                background-color: #2563eb;
                color: white;
                width: 100%;
                padding: 0.75rem;
                font-size: 1rem;
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }

            .login-container button:hover {
                background-color: #1e40af;
            }

            /* مركز الصفحة بالكامل */
            .center-page {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 90vh;
            }
        </style>
    """, unsafe_allow_html=True)

# 🟢 إرسال البيانات إلى Google Sheets
def send_data_to_google_sheet(name, group):
    try:
        requests.post(GOOGLE_SCRIPT_URL, data={"name": name, "group": group}, timeout=5)
    except:
        pass

# ✅ واجهة تسجيل الدخول
def show_login():
    load_custom_css()
    st.markdown('<div class="center-page"><div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h2>تسجيل الدخول</h2>", unsafe_allow_html=True)

    name = st.text_input("الاسم الكامل")
    group = st.text_input("المجموعة")

    if st.button("دخول"):
        if name.strip() != "" and group.strip() != "":
            send_data_to_google_sheet(name, group)
            st.session_state.name = name
            st.session_state.group = group
            st.session_state.page = "quiz"
            st.rerun()
        else:
            st.warning("يرجى إدخال الاسم والمجموعة")

    st.markdown('</div></div>', unsafe_allow_html=True)

# 🚀 تشغيل التطبيق
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "quiz":
    orders_main()
