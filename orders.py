import streamlit as st
import requests
from orders import orders_o, send_to_telegram

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

# 🛡️ تسجيل اسم المستخدم قبل عرض الأسئلة
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() and group.strip():
            st.session_state.user_logged = True
            st.session_state.name = name.strip()
            st.session_state.group = group.strip()
            send_to_telegram(name.strip(), group.strip())
            st.experimental_rerun()
else:
    # ✅ عرض عدد الأونلاين في بطاقة أنيقة
    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.markdown("🟢")
        with col2:
            count = get_online_user_count()
            st.markdown(
                f"""
                <div style="background-color:#f0f8ff;padding:10px;border-radius:12px;
                            box-shadow:0 4px 6px rgba(0,0,0,0.1);width:fit-content;">
                    👥 <b>Online:</b> {count}
                </div>
                """, unsafe_allow_html=True
            )

    # ⏱️ تحديث تلقائي كل 10 ثواني
    st.experimental_rerun()
    st_autorefresh = st.experimental_rerun  # سيُعيد تشغيل الصفحة كل 10 ثواني تلقائيًا

    # 🧠 بقية الأسئلة والمحتوى
    orders_o()
