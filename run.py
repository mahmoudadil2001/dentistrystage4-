import streamlit as st
import requests
from orders import main as orders_main  # ملف عرض الأسئلة والمحاضرات

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbycx6K2dBkAytd7QQQkrGkVnGkQUc0Aqs2No55dUDVeUmx8ERwaLqClhF9zhofyzPmY/exec"

def load_css():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to right, #6a11cb, #2575fc);
        }
        .stApp {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .login-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 3rem 2rem;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
            max-width: 500px;
            margin: auto;
            margin-top: 50px;
        }
        input {
            border-radius: 10px !important;
            padding: 10px !important;
        }
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
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return False

def get_user_data(username):
    data = {"action": "get_user_data", "username": username}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
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
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
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
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        return res.text.strip() == "UPDATED"
    except Exception as e:
        st.error(f"خطأ في تحديث كلمة المرور: {e}")
        return False

def login_page():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>تسجيل الدخول</h2>", unsafe_allow_html=True)

    username = st.text_input("اسم المستخدم", key="login_username")
    password = st.text_input("كلمة المرور", type="password", key="login_password")

    if st.button("دخول"):
        if not username or not password:
            st.warning("يرجى ملء جميع الحقول")
        elif check_login(username, password):
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

    if st.button("إنشاء حساب جديد"):
        st.session_state['show_signup'] = True
        st.rerun()
    if st.button("نسيت كلمة المرور؟"):
        st.session_state['show_forgot'] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def signup_page():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>إنشاء حساب جديد</h2>", unsafe_allow_html=True)

    username = st.text_input("اسم المستخدم", key="signup_username")
    password = st.text_input("كلمة المرور", type="password", key="signup_password")
    full_name = st.text_input("الاسم الكامل", key="signup_full_name")
    group = st.text_input("الجروب", key="signup_group")
    phone = st.text_input("رقم الهاتف", key="signup_phone")

    if st.button("تسجيل"):
        if not username or not password or not full_name or not group or not phone:
            st.warning("يرجى ملء جميع الحقول")
        elif add_user(username, password, full_name, group, phone):
            st.success("تم إنشاء الحساب بنجاح ✅")
            st.session_state['show_signup'] = False
            st.rerun()
        else:
            st.error("فشل في إنشاء الحساب")

    if st.button("عودة لتسجيل الدخول"):
        st.session_state['show_signup'] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def forgot_password_page():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>استعادة كلمة المرور</h2>", unsafe_allow_html=True)

    username = st.text_input("اسم المستخدم", key="forgot_username")
    full_name = st.text_input("الاسم الكامل", key="forgot_full_name")

    if st.button("تحقق"):
        user_data = get_user_data(username)
        if user_data and user_data['full_name'].strip().lower() == full_name.strip().lower():
            st.session_state['allow_reset'] = True
            st.success("تم التحقق، أدخل كلمة مرور جديدة")
        else:
            st.error("المعلومات غير صحيحة")

    if st.session_state.get('allow_reset'):
        new_password = st.text_input("كلمة المرور الجديدة", type="password", key="new_pass")
        confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="confirm_pass")

        if st.button("تحديث كلمة المرور"):
            if new_password != confirm_password:
                st.warning("كلمة المرور غير متطابقة")
            elif update_password(username, full_name, new_password):
                st.success("✅ تم تحديث كلمة المرور")
                st.session_state['show_forgot'] = False
                st.session_state['allow_reset'] = False
                st.rerun()
            else:
                st.error("فشل في التحديث")
    if st.button("عودة لتسجيل الدخول"):
        st.session_state['show_forgot'] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    load_css()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False

    if st.session_state['logged_in']:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.rerun()
        orders_main()
    elif st.session_state['show_signup']:
        signup_page()
    elif st.session_state['show_forgot']:
        forgot_password_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
