import streamlit as st
from orders import main as orders_main
from chat import main as chat_main

def main():
    # ضبط القيمة الافتراضية لصفحة العرض (لو غير موجودة)
    if "page" not in st.session_state:
        st.session_state.page = "orders"  # تبدأ بواجهة التسجيل

    # إذا الصفحة الحالية هي "orders" (تسجيل المستخدم)
    if st.session_state.page == "orders":
        orders_main()
    # إذا الصفحة الحالية هي "chat" (الدردشة)
    elif st.session_state.page == "chat":
        chat_main()

if __name__ == "__main__":
    main()
