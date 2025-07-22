import streamlit as st
import requests
from datetime import datetime

def main():
    # Check if user submitted data via URL query params
    query_params = st.experimental_get_query_params()
    name = query_params.get("name", [None])[0]
    group = query_params.get("group", [None])[0]

    if name and group and "user_name" not in st.session_state:
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.page = "orders"

        # Send to Telegram (handle errors silently)
        bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
        chat_id = "6283768537"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"👤 {name}\n👥 {group}\n🕓 {timestamp}"
        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except:
            pass

        # Clean URL params so user doesn’t resubmit on refresh
        st.experimental_set_query_params()

    if "user_name" in st.session_state and st.session_state.page == "orders":
        st.success(f"مرحباً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        # Proceed to the quiz or whatever you want here (or just return to let run.py handle page routing)
        return

    # Otherwise, embed the welcome.html
    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    import streamlit.components.v1 as components
    components.html(html_content, height=600)
