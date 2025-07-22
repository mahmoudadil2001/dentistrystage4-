import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

def main():
    # Read query params
    params = st.experimental_get_query_params()
    name = params.get("name", [None])[0]
    group = params.get("group", [None])[0]

    # If received name and group and not logged yet
    if name and group and "user_logged" not in st.session_state:
        # Save to session state
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.user_logged = True
        st.session_state.page = "orders"

        # Send to telegram
        bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
        chat_id = "6283768537"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}\n🕓 {timestamp}"

        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except:
            pass

        # Clear URL params and rerun to update UI immediately
        st.experimental_set_query_params()
        st.experimental_rerun()

    # If logged in, show welcome message
    if st.session_state.get("user_logged", False):
        st.success(f"👋 أهلاً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        return

    # Otherwise, show the embedded form
    with open("welcome.html", "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=600)
