import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwpFOajmybhmOZ9i07z66a2Ac14LTgH3BvJiOuMXU1EhkDnciKWN6X87nWk_G0W8vWE/exec"
TELEGRAM_BOT_TOKEN = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
TELEGRAM_CHAT_ID = "6283768537"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Error sending Telegram message: {e}")

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
        st.error(f"Error fetching user data: {e}")
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
        st.error(f"Error adding new user: {e}")
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

# ======== New functions to manage progress (check/uncheck) ========

def get_progress(username, subject, lecture_num, version):
    # Query Google Script for progress
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
        if text == "TRUE":
            return True
        elif text == "FALSE":
            return False
        else:
            return False
    except Exception as e:
        st.error(f"Error fetching progress: {e}")
        return False

def update_progress(username, subject, lecture_num, version, completed):
    # Send update request to Google Script
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

# ========== The rest of your existing login and signup code below ==========

def login_page():
    # ... keep your existing login_page() code unchanged ...

    # (This part is omitted here for brevity, keep your current code as is)

def forgot_password_page():
    # ... keep your existing forgot_password_page() code unchanged ...

    # (This part is omitted here for brevity, keep your current code as is)
