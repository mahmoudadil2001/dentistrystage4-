import streamlit as st
import requests
from orders import orders_o, send_to_telegram

# إعدادات Sendbird
APP_ID = "6EABD2CE-687E-4302-B9A2-6AE2A0C81CDC"
API_TOKEN = "77e4dab0d9568f41dadd61befe71d71405ba0c4d"
CHANNEL_URL = "sendbird_group_channel_646633550_eaa97ea9b7e0857d89d2e159d30469c6679d3b70"

def get_online_user_count():
    url = f"https://api-{APP_ID}.sendbird.com/v3/group_channels/{CHANNEL_URL}"
    headers = {"Api-Token": API_TOKEN, "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("member_count", 0)
        else:
            return "❌ خطأ في الجلب"
    except Exception as e:
        return f"⚠️ {str(e)}"

# تسجيل المستخدم
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() and group.strip():
            send_to_telegram(name.strip(), group.strip())
            st.session_state.user_logged = True
            st.session_state.name = name.strip()
            st.session_state.group = group.strip()
            st.rerun()
    st.stop()

# الحالة لإظهار الدردشة
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# زر إظهار/إخفاء الدردشة
if st.button("💬 فتح/إغلاق دردشة Sendbird"):
    st.session_state.show_chat = not st.session_state.show_chat

# عرض عدد المستخدمين أونلاين فوق الزر
st.markdown(
    f"""
    <div style="background-color:#f0f8ff; padding:10px; border-radius:12px; 
                box-shadow:0 4px 6px rgba(0,0,0,0.1); width:fit-content; margin-bottom:10px;">
        👥 <b>Online Users:</b> {get_online_user_count()}
    </div>
    """,
    unsafe_allow_html=True
)

# عرض الدردشة إذا كانت مفعلة
if st.session_state.show_chat:
    # هنا رابط تضمين دردشة Sendbird (يجب التأكد من رابط الإطار الصحيح)
    iframe_code = f"""
    <iframe
        src="https://widget.sendbird.com/chat?app_id={APP_ID}&channel_url={CHANNEL_URL}"
        style="width: 100%; height: 500px; border: none; border-radius: 10px;"
        allow="microphone; camera"
        allowfullscreen>
    </iframe>
    """
    st.markdown(iframe_code, unsafe_allow_html=True)

# المحتوى الأساسي
orders_o()
