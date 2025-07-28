import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwpFOajmybhmOZ9i07z66a2Ac14LTgH3BvJiOuMXU1EhkDnciKWN6X87nWk_G0W8vWE/exec"  # عدل على رابطك الحقيقي

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Error sending telegram message: {e}")

# -- الحسابات --

def check_login(username, password):
    data = {"action": "check", "username": username, "password": password}
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        return res.text.strip() == "TRUE"
    except Exception as e:
        st.error(f"Login check error: {e}")
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
        st.error(f"Error getting user data: {e}")
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
        st.error(f"Error adding user: {e}")
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
        st.error(f"Error updating password: {e}")
        return False

# --- دوال تقدم المحاضرات ---

def get_progress(username, subject, lecture_num, version):
    """
    ترجع True أو False حسب هل تم وضع علامة صح على النسخة المحددة من المحاضرة للمستخدم.
    """
    data = {
        "action": "get_progress",
        "username": username,
        "subject": subject,
        "lecture_num": str(lecture_num),
        "version": version
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        text = res.text.strip()
        return text == "TRUE"
    except Exception as e:
        st.error(f"Error getting progress: {e}")
        return False

def update_progress(username, subject, lecture_num, version, completed):
    """
    تحدث حالة إكمال المحاضرة (صح أو لا) في Google Sheet.
    """
    data = {
        "action": "update_progress",
        "username": username,
        "subject": subject,
        "lecture_num": str(lecture_num),
        "version": version,
        "completed": "TRUE" if completed else "FALSE"
    }
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data=data, timeout=120)
        return res.text.strip() == "UPDATED"
    except Exception as e:
        st.error(f"Error updating progress: {e}")
        return False

# ... باقي كود تسجيل الدخول وغيره كما أرسلته سابقًا ...
