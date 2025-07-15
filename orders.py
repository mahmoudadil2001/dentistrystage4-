import streamlit as st
import os
import importlib.util
import requests
import uuid
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# ✅ إعداد Firebase (تشغيل مرة واحدة فقط)
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_config.json")  # تأكد أن الملف هذا موجود
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://nothing-ddb83-default-rtdb.firebaseio.com/"
    })
    st.session_state.firebase_initialized = True

# ✅ تسجيل المستخدمين في Firebase
def show_online_users():
    user_id = st.session_state.get("visitor_name", "") + "_" + str(uuid.uuid4())[:8]
    now = int(time.time())
    db.reference(f"online_users/{user_id}").set(now)

    # حذف غير النشطين (أكثر من 5 دقائق)
    cutoff = now - 300
    users_data = db.reference("online_users").get()
    active_count = 0

    if users_data:
        for uid, ts in users_data.items():
            if ts >= cutoff:
                active_count += 1
            else:
                db.reference(f"online_users/{uid}").delete()

    st.info(f"👥 المستخدمين المتصلين حاليًا: {active_count}")

# 🟢 إرسال الاسم والقروب إلى تليجرام
def send_to_telegram(name, group):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# 🗂️ باقي كود الأسئلة (نفس كودك الأصلي بدون تغيير)
# 📝 لاختصار الرد، إذا حبيت أرسل لك فقط الكود من بعد `orders_o()` قولي

# ضع هنا كل الكود الذي بعد def orders_o() كما هو من كودك الأصلي السابق
# لأني لم أغير شيء عليه (حرفيًا)، فقط أضفت Firebase وعدد المستخدمين
