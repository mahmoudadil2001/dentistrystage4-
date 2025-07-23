import streamlit as st
import requests
import streamlit_authenticator as stauth

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyf9rMq1dh71Ib3nWNO7yyhrNCLmHDaYcjElk6E2k_nAEQ3x2KXo-w7q8jZIZgVOZoI/exec"

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"خطأ في إرسال رسالة التليجرام: {e}")

def get_all_users():
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}, timeout=120)
        if res.status_code == 200:
            users = res.json()
            return users
        else:
            st.error(f"فشل في جلب المستخدمين: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"خطأ في جلب المستخدمين: {e}")
        return []

def prepare_authenticator():
    users = get_all_users()
    if not users:
        st.error("لا توجد بيانات مستخدمين")
        return None

    usernames = []
    names = []
    passwords_plain = []

    for user in users:
        if user.get("password") and user.get("username") and user.get("full_name"):
            usernames.append(user["username"])
            names.append(user["full_name"])
            passwords_plain.append(user["password"])

    if not passwords_plain:
        st.error("لا توجد كلمات مرور صحيحة في البيانات")
        return None

    try:
        hasher = stauth.Hasher()
        hashed_passwords = hasher.generate(passwords_plain)
    except Exception as e:
        st.error(f"خطأ في تشفير كلمات المرور: {e}")
        return None

    credentials = {
        "usernames": {}
    }
    for i, username in enumerate(usernames):
        credentials["usernames"][username] = {
            "name": names[i],
            "password": hashed_passwords[i]
        }

    authenticator = stauth.Authenticate(
        credentials,
        "my_cookie_name",
        "my_signature_key",
        cookie_expiry_days=30,
        preauthorized=[],
    )
    return authenticator

# باقي الكود مثل السابق ...
