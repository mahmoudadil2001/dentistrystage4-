import streamlit as st
from orders import main as orders_main
from chat import main as chat_main

def main():
    # تشغيل صفحة الطلبات أولاً (تسجيل المستخدم)
    orders_main()

    # بعد تسجيل الدخول، عرض زر فتح الدردشة
    if "user_logged" in st.session_state and st.session_state.user_logged:
        if st.button("💬 فتح الدردشة"):
            chat_main()

if __name__ == "__main__":
    main()
