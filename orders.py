import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json

# قراءة بيانات الخدمة من Secrets Streamlit
service_account_info = json.loads(st.secrets["firebase"]["service_account"])

# تهيئة Firebase (تأكد أنه يتم مرة واحدة فقط)
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://nothing-ddb83-default-rtdb.firebaseio.com/"
    })

def send_to_telegram(name, group):
    import requests
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def show_online_users():
    user_id = st.session_state.visitor_name + "_" + st.session_state.visitor_group
    now = datetime.now().isoformat()
    ref = db.reference(f"online_users/{user_id}")
    ref.set(now)

def orders_o():
    # هنا تضيف الكود الأساسي الخاص بالاختبارات أو المحاضرات
    st.write("هنا يظهر محتوى التطبيق الأساسي (الاختبارات أو المحاضرات).")
