import streamlit as st
from orders import orders_o, send_to_telegram

# 🛡️ التأكد من أن المستخدم سجل اسمه قبل تشغيل باقي الموقع
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() == "" or group.strip() == "":
            st.warning("يرجى ملء كل الحقول.")
        else:
            send_to_telegram(name, group)
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            st.rerun()
    st.stop()  # لا تكمل تشغيل الموقع

# ✅ الآن فقط بعد تسجيل الاسم، شغل التطبيق الأساسي
orders_o()

# رابط التلي
st.markdown('<div style="display:flex; justify-content:center; margin-top:50px;"><a href="https://t.me/io_620" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">حسابي على التلي<span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;"><svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;"><path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/></svg></span></a></div>', unsafe_allow_html=True)
