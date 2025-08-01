import streamlit as st
import requests
import re
import uuid
from datetime import datetime, timedelta

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyL1fo6kEQG3QmgnPqAVyVG5fuqOx2SSTPYwjKG8nTELY2UX9zqGYxKzMEbGD0dv124/exec"

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

def get_user_by_token(token):
    res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_user_by_token", "token": token})
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

def set_session_token(username, token):
    requests.post(GOOGLE_SCRIPT_URL, data={"action": "set_session_token", "username": username, "token": token})

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

def find_username_by_last4(full_name, last4):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "find_username_by_last4",
        "full_name": full_name,
        "last4": last4
    })
    return res.text.strip()

def update_password(username, new_password):
    res = requests.post(GOOGLE_SCRIPT_URL, data={
        "action": "update_password",
        "username": username,
        "new_password": new_password
    })
    return res.text.strip() == "UPDATED"

# 🔥 استرجاع المستخدم إذا كان عنده session_token محفوظ
def auto_login():
    if "session_token" not in st.session_state:
        cookie_token = st.session_state.get("cookie_token", None)
        if cookie_token:
            user = get_user_by_token(cookie_token)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_full_name = user["full_name"]
                st.session_state.user_name = user["username"]

def login_page():
    if "mode" not in st.session_state:
        st.session_state.mode = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    auto_login()

    if st.session_state.get("logged_in"):
        st.header(f"مرحباً بك يا {st.session_state.get('user_full_name')} في صفحة الأسئلة!")
        if st.button("تسجيل خروج"):
            st.session_state.clear()
            st.success("تم تسجيل الخروج بنجاح")
            st.rerun()
        return

    if st.session_state.mode == "login":
        st.header("🔑 تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")

        if st.button("تسجيل الدخول"):
            if check_login(username, password):
                user = get_user_data(username)
                if user:
                    # ✅ توليد session_token وتخزينه
                    token = str(uuid.uuid4())
                    set_session_token(username, token)
                    st.session_state.cookie_token = token
                    st.session_state.logged_in = True
                    st.session_state.user_full_name = user['full_name']
                    st.session_state.user_name = user['username']
                    send_telegram_message(f"✅ تسجيل دخول:\n{user}")
                    st.rerun()
                else:
                    st.error("❌ خطأ في جلب بيانات المستخدم")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

        if st.button("إنشاء حساب جديد"):
            st.session_state.mode = "signup"
            st.rerun()

        if st.button("نسيت كلمة المرور؟"):
            st.session_state.mode = "forgot"
            st.rerun()

    elif st.session_state.mode == "signup":
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم", key="signup_username")
        p = st.text_input("كلمة المرور", type="password", key="signup_password")
        f = st.text_input("الاسم الثلاثي (بالعربي)", key="signup_full_name")
        g = st.text_input("الجروب", key="signup_group")
        ph = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("إنشاء الحساب"):
            if not (u and p and f and g and ph):
                st.warning("❗ يرجى ملء جميع الحقول")
            else:
                res = add_user(u, p, f, g, ph)
                if res == "USERNAME_EXISTS":
                    st.error("❌ اسم المستخدم موجود")
                elif res == "FULLNAME_EXISTS":
                    st.error("❌ الاسم الكامل موجود مسبقًا")
                elif res == "ADDED":
                    st.success("✅ تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول الآن.")
                    st.session_state.mode = "login"
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ غير متوقع")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    elif st.session_state.mode == "forgot":
        st.header("🔒 استعادة كلمة المرور")
        full_name = st.text_input("✍️ اكتب اسمك الثلاثي")

        if st.button("متابعة"):
            res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}).text.strip()
            found = any(full_name.strip().lower() == line.split(",")[1].strip().lower() for line in res.split("\n"))
            if not full_name.strip():
                st.warning("❗ الرجاء إدخال الاسم الكامل")
            elif found:
                st.session_state.temp_fullname = full_name
                st.session_state.mode = "forgot_last4"
                st.rerun()
            else:
                st.error("❌ الاسم الكامل غير موجود")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    elif st.session_state.mode == "forgot_last4":
        st.subheader(f"✅ الاسم: {st.session_state.temp_fullname}")
        last4 = st.text_input("📱 اكتب آخر 4 أرقام من رقم هاتفك")

        if st.button("تحقق"):
            username = find_username_by_last4(st.session_state.temp_fullname, last4)
            if username != "NOT_FOUND":
                st.session_state.found_username = username
                st.session_state.mode = "reset_password"
                st.rerun()
            else:
                st.error("❌ البيانات غير صحيحة")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "forgot"
            st.rerun()

    elif st.session_state.mode == "reset_password":
        st.success(f"✅ اسم المستخدم: {st.session_state.found_username}")
        new_pass = st.text_input("🔑 أدخل كلمة مرور جديدة", type="password")

        if st.button("حفظ كلمة المرور"):
            if update_password(st.session_state.found_username, new_pass):
                st.success("✅ تم تحديث كلمة المرور")
                st.session_state.mode = "login"
                st.rerun()
            else:
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

if __name__ == "__main__":
    login_page()
