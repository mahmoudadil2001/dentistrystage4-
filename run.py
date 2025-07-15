import firebase_admin
from firebase_admin import credentials, auth
import streamlit as st

# تهيئة Firebase (مرة واحدة فقط)
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("aooo.json")  # ← غيّر الاسم لو الملف عندك اسمه غير هذا
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

# دالة تسجيل الدخول
def sign_in(email, password):
    import requests
    api_key = "YOUR_FIREBASE_API_KEY"  # ← غيّرها بـ API Key الخاص بك من Firebase
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None


from orders import orders_o
orders_o ()

import streamlit as st
st.markdown('<div style="display:flex; justify-content:center; margin-top:50px;"><a href="https://t.me/io_620" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">حسابي على التلي<span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;"><svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;"><path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/></svg></span></a></div>', unsafe_allow_html=True)
