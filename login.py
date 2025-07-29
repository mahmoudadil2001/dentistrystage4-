import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyliGRttMqNg3WSz3ApBSUiF1mkYp22P1Zqluc0umRzpnrL7zQD5ZrASdvdZqA8WubN/exec"

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

def login_page():
    if "mode" not in st.session_state:
        st.session_state.mode = "login"

    if st.session_state.mode == "login":
        st.header("🔑 تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")

        if st.button("تسجيل الدخول"):
            if check_login(username, password):
                user = get_user_data(username)
                st.success(f"✅ أهلاً {user['full_name']}")
                send_telegram_message(f"✅ تسجيل دخول:\n{user}")
            else:
                st.error("❌ بيانات غير صحيحة")

        if st.button("إنشاء حساب جديد"):
            st.session_state.mode = "signup"
            st.rerun()

        if st.button("نسيت كلمة المرور؟"):
            st.session_state.mode = "forgot"
            st.rerun()

    elif st.session_state.mode == "signup":
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        f = st.text_input("الاسم الكامل")
        g = st.text_input("الجروب")
        ph = st.text_input("رقم الهاتف")

        if st.button("إنشاء الحساب"):
            if not u or not p or not f or not g or not ph:
                st.warning("❗ يرجى ملء جميع الحقول")
            else:
                res = add_user(u, p, f, g, ph)
                if res == "USERNAME_EXISTS":
                    st.error("❌ اسم المستخدم موجود، اختر اسمًا آخر")
                elif res == "ADDED":
                    st.success("✅ تم إنشاء الحساب بنجاح")
                    st.session_state.mode = "login"
                    st.rerun()
                else:
                    st.error("⚠ حدث خطأ أثناء إنشاء الحساب")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    elif st.session_state.mode == "forgot":
        st.header("🔒 استعادة كلمة المرور")
        full_name = st.text_input("✍️ اكتب اسمك الثلاثي")

        if st.button("متابعة"):
            st.session_state.temp_fullname = full_name
            st.session_state.mode = "forgot_last4"
            st.rerun()

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
                st.error("❌ فشل التحديث")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()
