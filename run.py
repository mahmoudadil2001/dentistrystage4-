import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import requests
from orders import main as orders_main

cookies = EncryptedCookieManager(prefix="dentistry_", password="your-very-secure-password")
if not cookies.ready():
    cookies.initialize()
    st.stop()

def check_login(username, password):
    # دالة التحقق من بيانات تسجيل الدخول (مثال)
    # هنا تطلب بيانات من google sheet أو أي مصدر بيانات عندك
    return username == "user" and password == "pass"

def get_user_data(username):
    # دالة لجلب بيانات المستخدم (مثال)
    return {"username": username, "full_name": "الاسم الكامل"}

def login_page():
    st.title("تسجيل الدخول")

    username_cookie = None
    password_cookie = None
    if hasattr(cookies, "cookies") and cookies.cookies is not None:
        username_cookie = cookies.cookies.get("username")
        password_cookie = cookies.cookies.get("password")

    # لو الكوكيز فيها بيانات وصحيحة، تسجيل دخول تلقائي
    if not st.session_state.get("logged_in") and username_cookie and password_cookie:
        if check_login(username_cookie, password_cookie):
            user_data = get_user_data(username_cookie)
            st.session_state['logged_in'] = True
            st.session_state['user_name'] = user_data['username']
            st.experimental_rerun()

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    keep_logged = st.checkbox("أبقني مسجلاً")

    if st.button("دخول"):
        if check_login(username, password):
            user_data = get_user_data(username)
            st.session_state['logged_in'] = True
            st.session_state['user_name'] = user_data['username']

            if keep_logged:
                cookies.cookies["username"] = username
                cookies.cookies["password"] = password
                cookies.save()

            st.experimental_rerun()
        else:
            st.error("بيانات تسجيل الدخول خاطئة")

def main():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            cookies.delete("username")
            cookies.delete("password")
            cookies.save()
            st.experimental_rerun()

        orders_main()

if __name__ == "__main__":
    main()
