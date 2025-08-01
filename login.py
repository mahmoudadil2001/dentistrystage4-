import streamlit as st
import requests
import re
import uuid
from streamlit_javascript import st_javascript

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/your_deployed_script_url/exec"  # عدّل هنا

def send_telegram_message(message):
    bot_token = "ضع_توكن_البوت"
    chat_id = "ضع_معرف_الشات"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def check_login(username, password):
    res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "check", "username": username, "password": password})
    return res.text.strip() == "TRUE"

def get_user_data(username):
    res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_user_data", "username": username})
    parts = res.text.strip().split(",")
    if len(parts) == 5:
        return {
            "username": parts[0],
            "password": parts[1],
            "full_name": parts[2],
            "group": parts[3],
            "phone": parts[4]
        }
    return None

def add_user(username, password, full_name, group, phone):
    res_all = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}).text.strip()
    if res_all:
        lines = res_all.split("\n")
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                existing_username = parts[0].strip().lower()
                existing_fullname = parts[1].strip().lower()
                if existing_username == username.lower():
                    return "USERNAME_EXISTS"
                if existing_fullname == full_name.lower():
                    return "FULLNAME_EXISTS"

    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "add",
        "username": username,
        "password": password,
        "full_name": full_name,
        "group": group,
        "phone": phone
    })
    return res.text.strip()

def set_session_token(username, token):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "set_session_token",
        "username": username,
        "token": token
    })
    return res.text.strip() == "TOKEN_SAVED"

def get_user_by_token(token):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "get_user_by_token",
        "token": token
    })
    parts = res.text.strip().split(",")
    if len(parts) == 5:
        return {
            "username": parts[0],
            "password": parts[1],
            "full_name": parts[2],
            "group": parts[3],
            "phone": parts[4]
        }
    return None

def validate_iraqi_phone(phone):
    pattern = re.compile(
        r"^(?:"  
        r"(0(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(\+964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(00964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"
        r"|"
        r"(0(1\d{2})\d{7})"
        r")$"
    )
    return bool(pattern.match(phone))

def validate_username(username):
    return bool(username and len(username) <= 10 and re.fullmatch(r"[A-Za-z0-9_.-]+", username))

def validate_full_name(full_name):
    words = full_name.strip().split()
    if len(words) != 3:
        return False
    arabic_pattern = re.compile(r"^[\u0600-\u06FF]+$")
    for w in words:
        if len(w) > 10 or not arabic_pattern.match(w):
            return False
    return True

def validate_password(password):
    return bool(password and 4 <= len(password) <= 16)

def validate_group(group):
    return bool(group and len(group) == 1 and re.fullmatch(r"[A-Za-z]", group))

def save_token_js(token: str):
    js_code = f"localStorage.setItem('session_token', '{token}');"
    st_javascript(js_code)

def get_token_js():
    token = st_javascript("localStorage.getItem('session_token');")
    return token

def login_page():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # محاولة تسجيل الدخول تلقائياً عبر التوكن المحفوظ
    if not st.session_state.logged_in:
        token = get_token_js()
        if token:
            user = get_user_by_token(token)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_data = user

    if st.session_state.logged_in:
        st.header(f"مرحباً بك يا {st.session_state.user_data['full_name']} في صفحة الأسئلة!")
        if st.button("تسجيل خروج"):
            st.session_state.clear()
            # إزالة التوكن من localStorage
            st_javascript("localStorage.removeItem('session_token');")
            st.experimental_rerun()
        return

    st.header("🔑 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        if check_login(username, password):
            user = get_user_data(username)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_data = user

                # توليد توكن جديد وتخزينه في Google Sheets وlocalStorage
                new_token = str(uuid.uuid4())
                set_session_token(username, new_token)
                save_token_js(new_token)

                send_telegram_message(f"✅ تسجيل دخول:\n{user}")
                st.experimental_rerun()
            else:
                st.error("❌ خطأ في جلب بيانات المستخدم")
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

if __name__ == "__main__":
    login_page()
