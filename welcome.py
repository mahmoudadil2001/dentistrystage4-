# welcome.py

import streamlit as st
import requests
from datetime import datetime

def main():
    st.markdown(
        """
        <div style="background-color:#f0f0f5;padding:20px;border-radius:10px">
            <h2 style="color:#4a4a4a;text-align:center">🎓 Welcome to Dents3CH4!</h2>
            <p style="text-align:center">Here you'll learn useful content related to dentistry. Let's get started!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("user_info_form"):
        name = st.text_input("اسمك")
        group = st.text_input("قروبك")
        submitted = st.form_submit_button("موافق")
        
        if submitted and name and group:
            st.success(f"مرحبًا {name}! 👋")
            st.session_state.page = "orders"
            st.session_state.user_name = name
            st.session_state.user_group = group

            # Telegram Bot info
            bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
            chat_id = "YOUR_CHAT_ID"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"👤 اسم: {name}\n👥 قروب: {group}\n🕓 وقت: {timestamp}"
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}")
