def login_page():
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم", key="login_username")
    password = st.text_input("كلمة المرور", type="password", key="login_password")

    login_clicked = st.button("دخول")

    if login_clicked:
        if not username or not password:
            st.warning("يرجى ملء جميع الحقول")
        else:
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = username
                st.session_state['just_logged_in'] = True  # علم تسجيل الدخول للتشغيل الآمن
                return True
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    # بقية صفحة التسجيل الجديد كما هي...
    # ...

    return False

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        just_logged_in = login_page()

        # إعادة التشغيل الآمنة فقط مرة واحدة بعد تسجيل الدخول
        if just_logged_in and not st.session_state.get('rerun_done', False):
            st.session_state['rerun_done'] = True
            st.experimental_rerun()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.session_state.pop('rerun_done', None)
            st.experimental_rerun()

        orders_main()
