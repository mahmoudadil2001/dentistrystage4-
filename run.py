import streamlit as st
import requests
from orders import main as orders_main

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxQbmSs3mr6otjCKay3O7chAP8pyyZA6DgWmPkyK5ecae6QCuYQass2YaaZK9dBhffP/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def check_login(username, password):
    data = {
        "action": "check",
        "username": username,
        "password": password
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return False

def add_user(username, password, email, phone):
    data = {
        "action": "add",
        "username": username,
        "password": password,
        "email": email,
        "phone": phone
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        return res.text.strip() == "Added"
    except Exception as e:
        st.error(f"خطأ في تسجيل المستخدم الجديد: {e}")
        return False

def login_page():
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if not username or not password:
            st.warning("يرجى ملء جميع الحقول")
        else:
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = username
                st.experimental_rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    st.markdown("---")
    st.write("ليس لديك حساب؟ سجل هنا:")

    signup_username = st.text_input("اسم المستخدم للتسجيل الجديد", key="signup_username")
    signup_password = st.text_input("كلمة المرور للتسجيل الجديد", type="password", key="signup_password")
    signup_email = st.text_input("البريد الإلكتروني", key="signup_email")
    signup_phone = st.text_input("رقم الهاتف", key="signup_phone")

    if st.button("إنشاء حساب جديد"):
        if not signup_username or not signup_password or not signup_email or not signup_phone:
            st.warning("يرجى ملء جميع حقول التسجيل")
        else:
            if add_user(signup_username, signup_password, signup_email, signup_phone):
                st.success("تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول")
            else:
                st.error("فشل في إنشاء الحساب، حاول مرة أخرى")

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.experimental_rerun()

        orders_main()

if __name__ == "__main__":
    main()
