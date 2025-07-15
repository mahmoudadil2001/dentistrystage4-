import streamlit as st
from orders import orders_o, send_to_telegram

# التحقق هل المستخدم سبق وكتب بياناته
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() == "" or group.strip() == "":
            st.warning("يرجى ملء كل الحقول.")
        else:
            # حفظ الحالة وإرسال البيانات دون إعادة تحميل
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            send_to_telegram(name, group)

# بعد التأكد من أنه سجّل الدخول، نبدأ تشغيل الموقع
if st.session_state.get("user_logged", False):
    orders_o()
