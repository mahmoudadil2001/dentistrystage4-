import streamlit as st
import requests
import time

# 🟢 دالة عرض عدد الأشخاص الأونلاين
def get_online_users_count():
    headers = {
        "Api-Token": "77e4dab0d9568f41dadd61befe71d71405ba0c4d"
    }

    response = requests.get(
        "https://api-{app_id}.sendbird.com/v3/group_channels/dentistrystage4".format(app_id="6EABD2CE-687E-4302-B9A2-6AE2A0C81CDC"),
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("member_count", "غير معروف")
    else:
        return "❌ خطأ في جلب البيانات"

# 🟢 هنا كل الكود داخل هذه الدالة
def orders_o():
    st.set_page_config(page_title="دردشة طب الأسنان", layout="centered")

    # ⏱️ تحديث تلقائي كل 10 ثواني
    st.experimental_rerun_interval = 10

    # 🟢 عرض عدد الأشخاص الأونلاين
    with st.container():
        st.markdown("### 👥 عدد المستخدمين الأونلاين الآن")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.info("🔄 يتم التحديث كل 10 ثواني")
        with col2:
            count = get_online_users_count()
            st.success(f"🟢 {count} مستخدم داخل الغرفة")

    st.markdown("---")

    # 🟣 تضمين شات Talk.io
    st.markdown("""
        <iframe src="https://talk.io/embed?channel=dentistrystage4" 
                width="100%" height="500px" frameborder="0" 
                style="border-radius: 10px;">
        </iframe>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("تم بناء هذه الصفحة باستخدام Streamlit و Sendbird API.")

