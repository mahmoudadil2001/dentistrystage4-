from orders import orders_o
orders_o ()
import streamlit as st
st.markdown('<div style="display:flex; justify-content:center; margin-top:50px;"><a href="https://t.me/io_620" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">حسابي على التلي<span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;"><svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;"><path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/></svg></span></a></div>', unsafe_allow_html=True)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# تحميل بيانات تسجيل الدخول من ملف JSON الخاص بك
if not firebase_admin._apps:
    cred = credentials.Certificate("your_firebase_key.json")  # ضع اسم ملف المفتاح هنا
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id.firebaseio.com/'  # ضع رابط مشروعك هنا
    })

# الدالة التي تتحقق من الكود
def check_code(code):
    ref = db.reference(f"codes/{code}")
    data = ref.get()
    if data is None:
        return False, "الكود غير صحيح."
    if data.get("used", False):
        return False, "تم استخدام الكود من قبل."
    ref.update({"used": True})
    return True, "تم تفعيل الكود بنجاح!"

# واجهة المستخدم
st.title("تسجيل الدخول")
st.session_state.setdefault("auth", False)

if not st.session_state.auth:
    code = st.text_input("أدخل كود التفعيل")
    if st.button("تفعيل"):
        ok, msg = check_code(code.strip())
        if ok:
            st.session_state.auth = True
            st.success(msg)
        else:
            st.error(msg)
else:
    st.success("تم تسجيل الدخول! مرحبًا بك.")
    st.write("هنا محتوى الموقع بعد التفعيل.")
