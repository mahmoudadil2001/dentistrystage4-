import streamlit as st
import requests

API_URL = "https://script.google.com/macros/s/AKfycbwNxvRTvClnSlcZ1iRu6jMydObLrUo_ylaVwSFAFNMMvM71RKi1edi53jT_Teb9siDJ/exec"
# إعداد الصفحة
st.set_page_config(page_title="تسجيل الدخول", page_icon="🔑", layout="centered")

# 🎨 تصميم CSS للباقات
st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        width: 400px;
        margin: auto;
    }
    .title {
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🔐 نظام تسجيل الدخول</div>", unsafe_allow_html=True)

option = st.radio("اختر الإجراء:", ["تسجيل الدخول", "إنشاء حساب", "نسيت كلمة السر"])

# 🟢 تسجيل الدخول
if option == "تسجيل الدخول":
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            res = requests.post(API_URL, data={"action": "check", "username": username, "password": password})
            if res.text == "TRUE":
                st.success("✅ تم تسجيل الدخول بنجاح")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
        st.markdown("</div>", unsafe_allow_html=True)

# 🟡 إنشاء حساب
elif option == "إنشاء حساب":
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        new_username = st.text_input("👤 اسم المستخدم الجديد")
        new_password = st.text_input("🔑 كلمة المرور", type="password")
        full_name = st.text_input("📛 الاسم الثلاثي الكامل")
        group = st.text_input("🏫 المجموعة")
        phone = st.text_input("📱 رقم الهاتف")
        
        if st.button("إنشاء الحساب"):
            res = requests.post(API_URL, data={
                "action": "add",
                "username": new_username,
                "password": new_password,
                "full_name": full_name,
                "group": group,
                "phone": phone
            })
            if res.text == "USERNAME_EXISTS":
                st.error("⚠️ هذا الاسم مستخدم مسبقًا، اختر اسمًا آخر")
            elif res.text == "ADDED":
                st.success("✅ تم إنشاء الحساب بنجاح")
            else:
                st.error("❌ حدث خطأ")
        st.markdown("</div>", unsafe_allow_html=True)

# 🔵 نسيت كلمة السر (بخطوتين)
elif option == "نسيت كلمة السر":
    step = st.session_state.get("step", 1)

    # 🟢 الخطوة 1: إدخال الاسم الثلاثي
    if step == 1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            full_name = st.text_input("📛 أدخل اسمك الثلاثي الكامل")
            if st.button("بحث"):
                res = requests.post(API_URL, data={"action": "find_username", "full_name": full_name})
                if res.text.startswith("FOUND"):
                    _, masked_phone, found_username = res.text.split(",")
                    st.session_state["step"] = 2
                    st.session_state["full_name"] = full_name
                    st.session_state["masked_phone"] = masked_phone
                    st.session_state["found_username"] = found_username
                    st.rerun()
                else:
                    st.error("❌ لم يتم العثور على مستخدم بهذا الاسم")
            st.markdown("</div>", unsafe_allow_html=True)

    # 🟢 الخطوة 2: إدخال آخر 4 أرقام
    elif step == 2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.info(f"📞 رقم هاتفك: {st.session_state['masked_phone']}")
            last4 = st.text_input("✍️ أدخل آخر 4 أرقام من رقم هاتفك")
            if st.button("تحقق"):
                res = requests.post(API_URL, data={
                    "action": "verify_last4",
                    "full_name": st.session_state["full_name"],
                    "last4": last4
                })
                if res.text.startswith("VERIFIED"):
                    _, username = res.text.split(",")
                    st.session_state["step"] = 3
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("❌ الأرقام غير صحيحة")
            st.markdown("</div>", unsafe_allow_html=True)

    # 🟢 الخطوة 3: إظهار اسم المستخدم وتغيير كلمة المرور
    elif step == 3:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.success(f"✅ تم التحقق! اسم المستخدم الخاص بك هو: {st.session_state['username']}")
            new_pass = st.text_input("🔑 أدخل كلمة مرور جديدة", type="password")
            if st.button("تغيير كلمة المرور"):
                res = requests.post(API_URL, data={
                    "action": "update_password",
                    "username": st.session_state["username"],
                    "new_password": new_pass
                })
                if res.text == "UPDATED":
                    st.success("✅ تم تحديث كلمة المرور بنجاح!")
                    st.session_state["step"] = 1
                else:
                    st.error("⚠️ حدث خطأ")
            st.markdown("</div>", unsafe_allow_html=True)
