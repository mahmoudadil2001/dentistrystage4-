import streamlit as st
import requests
import streamlit_authenticator as stauth

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbycx6K2dBkAytd7QQQkrGkVnGkQUc0Aqs2No55dUDVeUmx8ERwaLqClhF9zhofyzPmY/exec"

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

    usernames = [user["username"] for user in users]
    names = [user["full_name"] for user in users]
    passwords_plain = [user["password"] for user in users]

    # تشفير كلمات المرور
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
        "my_cookie_name",   # اسم الكوكي الخاص بك
        "my_signature_key", # مفتاح توقيع (اجعله عشوائي وطويل)
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

        # إرسال رسالة تلغرام عند تسجيل الدخول
        users = get_all_users()
        user_data = next((u for u in users if u["username"] == username), None)
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
