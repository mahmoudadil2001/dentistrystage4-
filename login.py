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

def get_user_data(username):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_user_data", "username": username}, timeout=120)
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

def prepare_authenticator():
    users = get_all_users()
    if not users:
        st.error("لا توجد بيانات مستخدمين")
        return None

    usernames = [user["username"] for user in users]
    names = [user["full_name"] for user in users]
    passwords_plain = [user["password"] for user in users]

    hashed_passwords = stauth.Hasher(passwords_plain).generate()

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

def login_page():
    st.title("تسجيل الدخول")

    authenticator = prepare_authenticator()
    if authenticator is None:
        st.error("حدث خطأ في إعداد نظام التحقق")
        return

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        st.session_state['logged_in'] = True
        st.session_state['user_name'] = username

        authenticator.logout("تسجيل خروج", "sidebar")

        user_data = get_user_data(username)
        if user_data:
            message = (
                f"🔑 تم تسجيل دخول المستخدم:\n"
                f"اسم المستخدم: <b>{user_data['username']}</b>\n"
                f"الاسم الكامل: <b>{user_data['full_name']}</b>\n"
                f"الجروب: <b>{user_data['group']}</b>\n"
                f"رقم الهاتف: <b>{user_data['phone']}</b>"
            )
            send_telegram_message(message)

        st.write(f"مرحباً {name}!")

        from orders import main as orders_main
        orders_main()

    elif authentication_status is False:
        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
    elif authentication_status is None:
        st.warning("يرجى إدخال بيانات تسجيل الدخول")

def forgot_password_page():
    st.title("استعادة كلمة المرور")

    username = st.text_input("اسم المستخدم", key="forgot_username")
    full_name = st.text_input("الاسم الكامل", key="forgot_full_name")

    if 'password_updated' not in st.session_state:
        st.session_state['password_updated'] = False

    if st.button("عودة"):
        st.session_state['password_updated'] = False
        st.session_state['allow_reset'] = False
        st.session_state['show_forgot'] = False
        st.experimental_rerun()

    if st.button("تحقق"):
        if not username.strip() or not full_name.strip():
            st.warning("يرجى ملء اسم المستخدم والاسم الكامل")
            st.session_state['allow_reset'] = False
        else:
            user_data = get_user_data(username)
            if user_data and user_data['full_name'].strip().lower() == full_name.strip().lower():
                st.success("✅ تم التحقق بنجاح، أدخل كلمة مرور جديدة")
                st.session_state['allow_reset'] = True
            else:
                st.error("اسم المستخدم أو الاسم الكامل غير صحيح")
                st.session_state['allow_reset'] = False

    if st.session_state.get('allow_reset', False) and not st.session_state['password_updated']:
        new_password = st.text_input("كلمة المرور الجديدة", type="password", key="new_pass")
        confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="confirm_pass")

        if st.button("تحديث كلمة المرور"):
            if new_password != confirm_password:
                st.warning("كلمة المرور غير متطابقة")
            elif update_password(username, full_name, new_password):
                st.success("✅ تم تحديث كلمة المرور، سجل دخولك الآن")
                st.session_state['password_updated'] = True
                st.session_state['allow_reset'] = False
                st.experimental_rerun()
            else:
                st.error("فشل في تحديث كلمة المرور")
