import streamlit as st
import requests
import re

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyC1_kj-yAWT_wzQx3BGerNxAyDxZiRO7eoQmk11ywBwiPEv8nWy2_VuoIzcvTR3w2T/exec"

# ----- وظائف API -----
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

# --- توكن في Local Storage باستخدام جافاسكريبت ---
def set_token_js(token):
    js_code = f"""
    <script>
    localStorage.setItem('login_token', '{token}');
    </script>
    """
    st.components.v1.html(js_code)

def get_token_js():
    # لا يمكن جلب localStorage مباشرة من البايثون، نستخدم trick لاحقاً
    return st.session_state.get("login_token", None)

def remove_token_js():
    js_code = """
    <script>
    localStorage.removeItem('login_token');
    </script>
    """
    st.components.v1.html(js_code)

# --- دالة عرض مشروعك الأصلي ---
def main_project_page(user):
    st.title("مرحبا بك في مشروعك الأساسي")
    st.write(f"مرحباً {user['full_name']}، هذه هي صفحتك الخاصة بالمشروع.")
    # هنا ضع كل كود مشروعك
    if st.button("تسجيل خروج"):
        st.session_state.clear()
        remove_token_js()
        st.rerun()

# --- التحقق من التوكن ---
def validate_token(token):
    # ممكن تستخدم التوكن للتحقق بالخادم أو لو كان التوكن هو اسم المستخدم فقط
    # هنا نفترض التوكن هو اسم المستخدم فقط لتبسيط المثال
    user = get_user_data(token)
    return user

def login_page():
    # محاولة جلب التوكن من localStorage عبر JS (محاكاة لأنه لا يمكن جلبه مباشرة)
    if "login_token" not in st.session_state:
        # في حال أول تحميل أو بعد تسجيل خروج
        st.session_state.login_token = None

    # إذا التوكن موجود في session_state
    if st.session_state.login_token:
        user = validate_token(st.session_state.login_token)
        if user:
            # اعرض الصفحة الرئيسية للمشروع مباشرة
            main_project_page(user)
            return
        else:
            # التوكن غير صالح، مسحه
            st.session_state.login_token = None
            remove_token_js()

    # صفحة تسجيل الدخول
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
                    # تخزين التوكن (مثلاً اسم المستخدم) في session_state وlocalStorage
                    st.session_state.logged_in = True
                    st.session_state.user_full_name = user['full_name']
                    st.session_state.user_name = user['username']
                    st.session_state.login_token = user['username']  # التوكن
                    set_token_js(user['username'])
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
        # --- (كود إنشاء حساب جديد كما لديك) ---
        # يمكنك إدراج نفس الكود كما في سكربتك
        st.header("📝 إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم", key="signup_username")
        p = st.text_input("كلمة المرور", type="password", key="signup_password")
        f = st.text_input("الاسم الثلاثي (بالعربي)", key="signup_full_name")
        g = st.text_input("الجروب", key="signup_group")
        ph = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("إنشاء الحساب"):
            # تحقق الحقول كما لديك في السكربت
            # ...
            # مثال مبسط:
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
                    st.error("حدث خطأ أثناء إنشاء الحساب")

        if st.button("🔙 رجوع"):
            st.session_state.mode = "login"
            st.rerun()

    # --- يمكنك استكمال باقي الحالات مثل نسيت كلمة المرور بنفس المنطق ---

if __name__ == "__main__":
    login_page()
