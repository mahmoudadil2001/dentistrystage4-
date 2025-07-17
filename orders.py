import streamlit as st
import requests
import time

# 🟢 إعدادات Sendbird
APP_ID = "6EABD2CE-687E-4302-B9A2-6AE2A0C81CDC"
API_TOKEN = "77e4dab0d9568f41dadd61befe71d71405ba0c4d"
CHANNEL_URL = "dentistrystage4"

# 🟢 دالة جلب عدد المستخدمين الأونلاين
def get_online_user_count():
    url = f"https://api-{APP_ID}.sendbird.com/v3/group_channels/{CHANNEL_URL}"
    headers = {
        "Api-Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("member_count", 0)
    else:
        return "❌ خطأ في الاتصال"

# 🟢 عرض عدد الأونلاين ببطاقة صغيرة أنيقة
def online_card():
    count = get_online_user_count()
    st.markdown(
        f"""
        <div style='background-color:#f0f2f6;padding:10px 20px;border-radius:12px;box-shadow:2px 2px 5px rgba(0,0,0,0.1);display:inline-block'>
            <span style='font-size:18px;'>👥 المستخدمون الأونلاين: <strong style='color:green'>{count}</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )

# 🟢 التحديث كل 10 ثواني تلقائيًا
def auto_refresh_online_status():
    count_placeholder = st.empty()
    while True:
        with count_placeholder.container():
            online_card()
        time.sleep(10)
        st.rerun()  # إعادة تشغيل الصفحة تلقائيًا

# 🟢 تشغيل المكون في الموقع
if st.session_state.get("user_logged", False):
    online_card()
    # إضافة زر للدردشة (Talk.io أو غيره)
    st.markdown(
        """
        <div style="margin-top: 20px;">
            <iframe src="https://talk.io/embed/6EABD2CE-687E-4302-B9A2-6AE2A0C81CDC"
                    width="100%" height="400px"
                    style="border-radius: 15px; border: none;"></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )
