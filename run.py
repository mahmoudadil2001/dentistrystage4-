import streamlit as st
import requests
from orders import orders_o, send_to_telegram
from streamlit_autorefresh import st_autorefresh  # تأكد من تثبيت المكتبة عبر: pip install streamlit-autorefresh

# 🟢 إعدادات Sendbird
APP_ID = "6EABD2CE-687E-4302-B9A2-6AE2A0C81CDC"
API_TOKEN = "77e4dab0d9568f41dadd61befe71d71405ba0c4d"
CHANNEL_URL = "dentistrystage4"

# 🟢 دالة لجلب عدد المستخدمين الأونلاين
def get_online_user_count():
    url = f"https://api-{APP_ID}.sendbird.com/v3/group_channels/{CHANNEL_URL}"
    headers = {
        "Api-Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("member_count", 0)
        else:
            return "❌ خطأ في الجلب"
    except Exception as e:
        return f"⚠️ {str(e)}"

# ⏳ تحديث تلقائي كل 10 ثواني
count = st_autorefresh(interval=10 * 1000, limit=None, key="online_users_autorefresh")

# 🛡️ تسجيل اسم المستخدم قبل عرض الأسئلة
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() and group.strip():
            st.session_state.user_logged = True
            st.session_state.visitor_name = name.strip()
            st.session_state.visitor_group = group.strip()
            send_to_telegram(name.strip(), group.strip())
            st.experimental_rerun()
else:
    # ✅ عرض عدد الأونلاين في بطاقة أنيقة
    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.markdown("🟢")
        with col2:
            online_count = get_online_user_count()
            st.markdown(
                f"""
                <div style="background-color:#f0f8ff;padding:10px;border-radius:12px;
                            box-shadow:0 4px 6px rgba(0,0,0,0.1);width:fit-content;">
                    👥 <b>Online:</b> {online_count}
                </div>
                """, unsafe_allow_html=True
            )

    # ✅ تشغيل التطبيق الأساسي بعد تسجيل المستخدم
    orders_o()

    # 🔵 زر قناة التلي + جملة تحت الزر
    st.markdown('''
    <div style="display:flex; justify-content:center; margin-top:50px;">
        <a href="https://t.me/dentistryonly0" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">
            قناة التلي
            <span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;">
                <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;">
                    <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2
