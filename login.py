import streamlit as st
import requests
import re
import random
import string
from streamlit_javascript import st_javascript  # مكتبة لقراءة جافاسكريبت في ستريمليت

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw5p9TJNJQOJ2Qhg58YrH2UkPMhmJDb468zJyiNxZLTM-YagYQW-TLs6VTmGB53MUPm/exec"

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

def generate_token(length=32):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

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

# دوال جافاسكريبت للتعامل مع localStorage
def save_token_js(token, username):
    st.components.v1.html(f"""
    <script>
    localStorage.setItem('login_token', '{token}');
    localStorage.setItem('login_username', '{username}');
    </script>
    """, height=0)

def remove_token_js():
    st.components.v1.html("""
    <script>
    localStorage.removeItem('login_token');
    localStorage.removeItem('login_username');
    </script>
    """, height=0)

def login_page():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # محاولة قراءة التوكن واسم المستخدم من localStorage عبر streamlit_javascript
    token = st_javascript("localStorage.getItem('login_token')")
    username = st_javascript("localStorage.getItem('login_username')")

    # إذا هناك توكن واسم مستخدم، وافترض تسجيل دخول تلقائي
    if not st.session_state.logged_in and token and username:
        user = get_user_data(username)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_data = user
            st.success(f"🔑 تسجيل دخول تلقائي مرحباً بك يا {user['full_name']}")
            show_main_project_page(user)
            return
        else:
            remove_token_js()

    if st.session_state.logged_in:
        show_main_project_page(st.session_state.user_data)
        return

    # إذا لم يكن مسجل دخول أو لا يوجد توكن
    mode = st.session_state.get("mode", "login")

    if mode == "login":
        st.header("🔑 تسجيل الدخول")
        username_input = st.text_input("اسم المستخدم")
        password_input = st.text_input("كلمة المرور", type="password")

        if st.button("تسجيل الدخول"):
            if check_login(username_input, password_input):
                user = get_user_data(username_input)
                if user:
                    token = generate_token()
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    st.session_state.token = token
                    save_token_js(token, user['username'])  # حفظ التوكن واسم المستخدم
                    send_telegram_message(f"✅ تسجيل دخول:\n{user}\nToken: {token}")
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

    elif mode == "signup":
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم", key="signup_username")
        p = st.text_input("كلمة المرور", type="password", key="signup_password")
        f = st.text_input("الاسم الثلاثي (بالعربي)", key="signup_full_name")
        g = st.text_input("الجروب", key="signup_group")
        ph = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("إنشاء الحساب"):
            if not (u and p and f and g and ph):
                st.warning("❗ يرجى ملء جميع الحقول")
            elif not validate_username(u):
                st.error("❌ اسم المستخدم غير صالح (حتى 10 أحرف/أرقام/رموز بدون فراغات)")
            elif not validate_password(p):
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")
            elif not validate_full_name(f):
                st.error("❌ الاسم الكامل يجب أن يكون 3 كلمات بالعربي وكل كلمة ≤ 10 أحرف")
            elif not validate_group(g):
                st.error("❌ الجروب يجب أن يكون حرف واحد بالإنجليزي")
            elif not validate_iraqi_phone(ph):
                st.error("❌ رقم الهاتف غير صالح")
            else:
                res = add_user(u, p, f, g, ph)
                if res == "USERNAME_EXISTS":
                    st.error("❌ اسم المستخدم موجود")
                elif res == "FULLNAME_EXISTS":
                    st.error("❌ الاسم الكامل موجود مسبقًا")
                elif res == "ADDED":
                    st.success("✅ تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول الآن.")
                    st.session_state.signup_username = ""
                    st.session_state.signup_password = ""
                    st.session_state.signup_full_name = ""
                    st.session_state.signup_group = ""
                    st.session_state.signup_phone = ""
                    st.session_state.mode = "login"
                    st.rerun()
                else:
                    st.error("✅ تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول الآن.")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    elif mode == "forgot":
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

    elif mode == "forgot_last4":
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

    elif mode == "reset_password":
        st.success(f"✅ اسم المستخدم: {st.session_state.found_username}")
        new_pass = st.text_input("🔑 أدخل كلمة مرور جديدة", type="password")

        if st.button("حفظ كلمة المرور"):
            if validate_password(new_pass) and update_password(st.session_state.found_username, new_pass):
                st.success("✅ تم تحديث كلمة المرور")
                st.session_state.mode = "login"
                st.rerun()
            else:
                st.error("❌ كلمة المرور يجب أن تكون بين 4 و 16 رمز")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

def show_main_project_page(user):
    st.header(f"مرحباً بك يا {user['full_name']} في صفحة الأسئلة!")
    if st.button("تسجيل خروج"):
        st.session_state.clear()
        remove_token_js()
        st.rerun()

if __name__ == "__main__":
    login_page()
