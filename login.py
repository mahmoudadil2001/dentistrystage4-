import streamlit as st
import requests
import re
import streamlit.components.v1 as components

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyC1_kj-yAWT_wzQx3BGerNxAyDxZiRO7eoQmk11ywBwiPEv8nWy2_VuoIzcvTR3w2T/exec"

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

# ----

# Component لقراءة توكن من localStorage وإرساله للبايثون
def get_token_from_local_storage():
    token = components.html(
        """
        <script>
        const streamlitDoc = window.parent.document;
        window.onload = () => {
            const token = localStorage.getItem('login_token') || '';
            // إرسال القيمة إلى Streamlit عبر window.parent.postMessage
            window.parent.postMessage({funcName: 'sendToken', token: token}, '*');
        }
        </script>
        """,
        height=0,
        width=0,
        scrolling=False,
    )
    # streamlit لا يمكنه التقاط الرسالة مباشرة، نستخدم st.experimental_get_query_params لتخزين مؤقت
    # ولكن هنا سنعتمد على trick في session_state بعد إعادة تشغيل الصفحة
    # الحل البديل هو استخدام streamlit-javascript أو external package لكن هذا أبسط مثال
    return None

def main_project_page(user):
    st.title("مرحبا بك في مشروعك الأساسي")
    st.write(f"مرحباً {user['full_name']}، هذه هي صفحتك الخاصة بالمشروع.")
    # ضع هنا كود مشروعك الكامل

    if st.button("تسجيل خروج"):
        st.session_state.clear()
        # إزالة التوكن من localStorage عبر JS
        components.html(
            """
            <script>
            localStorage.removeItem('login_token');
            </script>
            """,
            height=0,
        )
        st.rerun()

def login_page():
    if "login_token" not in st.session_state:
        st.session_state.login_token = None

    # استدعاء الـ component لجلب التوكن من localStorage
    get_token_from_local_storage()

    # لو التوكن موجود في session_state نفحصه
    if st.session_state.login_token:
        user = get_user_data(st.session_state.login_token)
        if user:
            main_project_page(user)
            return
        else:
            st.session_state.login_token = None
            # إزالة التوكن من localStorage أيضاً
            components.html(
                """
                <script>
                localStorage.removeItem('login_token');
                </script>
                """,
                height=0,
            )

    if "mode" not in st.session_state:
        st.session_state.mode = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.get("logged_in"):
        user = {
            "username": st.session_state.get('user_name'),
            "full_name": st.session_state.get('user_full_name')
        }
        main_project_page(user)
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
                    st.session_state.login_token = user['username']
                    # تخزين التوكن في localStorage
                    components.html(
                        f"""
                        <script>
                        localStorage.setItem('login_token', '{user['username']}');
                        </script>
                        """,
                        height=0,
                    )
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

    # باقي أوضاع التسجيل واستعادة كلمة المرور كما لديك ...

if __name__ == "__main__":
    login_page()
