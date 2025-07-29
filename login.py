import streamlit as st
import requests
import re

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwJyx-6Izo4fuxeOq-QEtjHt6OYxbBnZ77PXR6v6LeXvCyV-e0YU1EInXbi16C-Zc8t/exec"

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
    return bool(username) and len(username) <= 10 and re.fullmatch(r"[A-Za-z0-9_.-]+", username)

def validate_full_name(full_name):
    if not full_name:
        return False
    words = full_name.strip().split()
    if len(words) != 3:
        return False
    arabic_pattern = re.compile(r"^[\u0600-\u06FF]+$")
    return all(len(w) <= 10 and arabic_pattern.match(w) for w in words)

def validate_password(password):
    return bool(password) and 4 <= len(password) <= 16

def validate_group(group):
    return bool(re.fullmatch(r"[A-Za-z]", group))

def login_page():
    if "mode" not in st.session_state:
        st.session_state.mode = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_full_name" not in st.session_state:
        st.session_state.user_full_name = ""
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    if st.session_state.logged_in:
        st.header(f"مرحباً بك يا {st.session_state.user_full_name} في صفحة الأسئلة!")
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.user_full_name = ""
            st.session_state.user_name = ""
            st.session_state.mode = "login"
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

    elif st.session_state.mode == "signup":
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم (حتى 10 أحرف)")
        p = st.text_input("كلمة المرور (4-16 حرف)", type="password")
        f = st.text_input("الاسم الثلاثي (بالعربي)")
        g = st.text_input("الجروب (حرف واحد بالإنجليزية)")
        ph = st.text_input("رقم الهاتف")

        if st.button("إنشاء الحساب"):
            if not all([u, p, f, g, ph]):
                st.warning("❗ يرجى ملء جميع الحقول")
            elif not validate_username(u):
                st.error("❌ اسم المستخدم غير صالح")
            elif not validate_password(p):
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")
            elif not validate_full_name(f):
                st.error("❌ الاسم الكامل يجب أن يكون 3 كلمات عربية، كل كلمة ≤ 10 أحرف")
            elif not validate_group(g):
                st.error("❌ الجروب يجب أن يكون حرفًا واحدًا بالإنجليزية")
            elif not validate_iraqi_phone(ph):
                st.error("❌ رقم الهاتف غير صالح")
            else:
                res = add_user(u, p, f, g, ph)
                if res == "USERNAME_EXISTS":
                    st.error("❌ اسم المستخدم موجود مسبقًا")
                elif res == "FULLNAME_EXISTS":
                    st.error("❌ الاسم الكامل موجود مسبقًا")
                elif res == "ADDED":
                    st.success("✅ تم إنشاء الحساب بنجاح")
                    st.session_state.mode = "login"
                    st.rerun()
                else:
                    st.error("⚠ حدث خطأ أثناء إنشاء الحساب")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

if __name__ == "__main__":
    login_page()
