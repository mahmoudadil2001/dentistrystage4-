import streamlit as st
from orders import main as orders_main
from chat import main as chat_main

def main():
    # تشغيل واجهة تسجيل المستخدم أولاً
    orders_main()

    # إذا تم تسجيل الدخول، أظهر خيار الدخول إلى الدردشة
    if st.session_state.get("page") == "chat":
        chat_main()

if __name__ == "__main__":
    main()
