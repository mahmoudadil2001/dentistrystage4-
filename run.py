import streamlit as st
import requests
from orders import main as orders_main

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxQbmSs3mr6otjCKay3O7chAP8pyyZA6DgWmPkyK5ecae6QCuYQass2YaaZK9dBhffP/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def send_to_google_script(name, group):
    data = {"name": name, "group": group}
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data, timeout=5)
        return True
    except Exception as e:
        st.error(f"حدث خطأ في إرسال البيانات: {e}")
        return False

def login_page():
    st.title("تسجيل الدخول")
    name = st.text_input("الاسم")
    group = st.text_input("القروب")

    if st.button("تسجيل الدخول"):
        if not name or not group:
            st.warning("يرجى ملء جميع الحقول")
            return False

        success = send_to_google_script(name, group)
        if success:
            st.session_state['logged_in'] = True
            st.session_state['user_name'] = name
            st.session_state['user_group'] = group
            st.experimental_rerun()
        else:
            st.error("فشل تسجيل الدخول، حاول مرة أخرى")
            return False

def main():
    load_css("styles.css")  # تأكد من وجود الملف في نفس المجلد

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.session_state.pop('user_group', None)
            st.experimental_rerun()

        orders_main()  # عرض المحتوى الأصلي للموقع

if __name__ == "__main__":
    main()
