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

def validate_iraqi_phone(phone):
    pattern = re.compile(
        r"^(?:"  
        r"(0(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"       # محلي 10 أرقام
        r"|"
        r"(\+964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"   # مع +
        r"|"
        r"(00964(750|751|752|753|780|781|770|771|772|773|774|775|760|761|762|763|764|765)\d{7})"  # مع 00
        r"|"
        r"(0(1\d{2})\d{7})"  # الخطوط الأرضية مثل 010xxxxxxx
        r")$"
    )
    return bool(pattern.match(phone))

def validate_username(username):
    # اسم المستخدم كلمة واحدة (لا تحتوي على فراغات) من حروف، أرقام، أو رموز إنجليزية، ولا تزيد عن 10 أحرف
    if not username:
        return False
    if len(username) > 10:
        return False
    # يسمح بأي حرف انجليزي أو رقم أو رموز محددة (مثل _ - .) بدون فراغات
    # يمكن تعديل هذه الصيغة لتسمح برموز أخرى حسب الحاجة
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
        return False
    return True

def validate_full_name(full_name):
    # الاسم الكامل 3 كلمات بالضبط، كل كلمة بالعربي (يوجد حروف عربية فقط)، كل كلمة لا تزيد عن 10 أحرف
    if not full_name:
        return False
    words = full_name.strip().split()
    if len(words) != 3:
        return False
    arabic_pattern = re.compile(r"^[\u0600-\u06FF]+$")  # حروف عربية فقط
    for w in words:
        if len(w) > 10:
            return False
        if not arabic_pattern.match(w):
            return False
    return True

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
        st.write("هنا يمكنك وضع أسئلة وأجوبة المشروع أو أي محتوى آخر.")

        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.user_full_name = ""
            st.session_state.user_name = ""
            st.session_state.mode = "login"
            st.rerun()
        return

    if st.session_state.mode == "login":
        st.header("🔑 تسجيل الدخول")
        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")

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
            if not u or not p or not f or not g or not ph:
                st.warning("❗ يرجى ملء جميع الحقول")
            else:
                if not validate_username(u):
                    st.error("❌ اسم المستخدم غير صالح. كلمة واحدة (أحرف، أرقام، رموز)، حتى 10 أحرف، بدون فراغات")
                elif not validate_full_name(f):
                    st.error("❌ الاسم الكامل غير صالح. يجب أن يحتوي على 3 كلمات عربية، كل كلمة لا تزيد عن 10 أحرف")
                elif not validate_iraqi_phone(ph):
                    st.error("❌ رقم الهاتف غير صالح. الرجاء إدخاله بالشكل الصحيح (مثال: 07701234567 أو +9647701234567).")
                else:
                    res = add_user(u, p, f, g, ph)
                    if res == "USERNAME_EXISTS":
                        st.error("❌ اسم المستخدم موجود، اختر اسمًا آخر")
                    elif res == "FULLNAME_EXISTS":
                        st.error("❌ الاسم الكامل موجود مسبقًا، تحقق من بياناتك أو اتصل بالدعم")
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
        full_name = st.text_input("✍️ اكتب اسمك الثلاثي", key="forgot_fullname")

        if st.button("متابعة"):
            def full_name_exists(name):
                res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_all_users"}).text.strip()
                if res:
                    lines = res.split("\n")
                    for line in lines:
                        parts = line.split(",")
                        if len(parts) >= 2:
                            existing_fullname = parts[1].strip().lower()
                            if existing_fullname == name.strip().lower():
                                return True
                return False

            if not full_name.strip():
                st.warning("❗ الرجاء إدخال الاسم الكامل")
            elif full_name_exists(full_name):
                st.session_state.temp_fullname = full_name
                st.session_state.mode = "forgot_last4"
                st.rerun()
            else:
                st.error("❌ الاسم الكامل غير موجود في النظام، تحقق من بياناتك")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    elif st.session_state.mode == "forgot_last4":
        st.subheader(f"✅ الاسم: {st.session_state.temp_fullname}")
        last4 = st.text_input("📱 اكتب آخر 4 أرقام من رقم هاتفك", key="forgot_last4")

        if st.button("تحقق"):
            username
