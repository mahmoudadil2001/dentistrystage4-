import streamlit as st
import requests
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# تحميل بيانات اعتماد Google Sheets من secrets
GOOGLE_SHEETS_CREDENTIALS = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]

def get_gsheet_client():
    creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client

def save_to_gsheet(name, group):
    client = get_gsheet_client()
    sheet = client.open_by_key("1b_Fh4M9RbjyYBqguYz-g4oVj8E2U2-0smc9MtWsMpdM").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, group, now])

def send_to_telegram(name, group):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك الكامل")
    group = st.text_input("👥 اسم القروب")

    if st.button("✅ موافق"):
        if name.strip() == "" or group.strip() == "":
            st.warning("يرجى ملء كل الحقول.")
        else:
            send_to_telegram(name, group)
            save_to_gsheet(name, group)  # هنا تحفظ للشييت
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            st.rerun()
    st.stop()

# بقية الكود حسب السابق...
