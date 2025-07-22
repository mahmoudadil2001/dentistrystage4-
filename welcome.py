import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

def main():
    query_params = st.query_params
    name = query_params.get("name", [None])[0]
    group = query_params.get("group", [None])[0]

    if name and group and "user_name" not in st.session_state:
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.page = "orders"

        bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
        chat_id = "6283768537"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}\n🕓 {timestamp}"

        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except Exception as e:
            st.error(f"حدث خطأ أثناء إرسال البيانات إلى تليجرام: {e}")

        st.experimental_set_query_params()  # Remove params from URL after reading
        st.experimental_rerun()

    if "user_name" in st.session_state and st.session_state.page == "orders":
        st.success(f"👋 أهلاً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        return

    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=600)
