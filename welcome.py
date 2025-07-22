import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

def main():
    # Use new st.query_params to read URL query parameters
    query_params = st.query_params
    name = query_params.get("name", [None])[0]
    group = query_params.get("group", [None])[0]

    # If user submitted data via URL params and not yet in session state
    if name and group and "user_name" not in st.session_state:
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.page = "orders"

        # Send to Telegram (handle exceptions silently)
        bot_token = "import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

def main():
    # Use new st.query_params to read URL query parameters
    query_params = st.query_params
    name = query_params.get("name", [None])[0]
    group = query_params.get("group", [None])[0]

    # If user submitted data via URL params and not yet in session state
    if name and group and "user_name" not in st.session_state:
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.page = "orders"

        # Send to Telegram (handle exceptions silently)
        bot_token = "import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

def main():
    # Use new st.query_params to read URL query parameters
    query_params = st.query_params
    name = query_params.get("name", [None])[0]
    group = query_params.get("group", [None])[0]

    # If user submitted data via URL params and not yet in session state
    if name and group and "user_name" not in st.session_state:
        st.session_state.user_name = name
        st.session_state.user_group = group
        st.session_state.page = "orders"

        # Send to Telegram (handle exceptions silently)
        bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
        chat_id = "6283768537"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"👤 {name}\n👥 {group}\n🕓 {timestamp}"
        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except:
            pass

        # Clear URL params so page refresh won't resubmit
        st.experimental_set_query_params()

        # Optional: trigger rerun to update UI immediately
        st.experimental_rerun()

    # If user already submitted and page is orders, show welcome message or continue
    if "user_name" in st.session_state and st.session_state.page == "orders":
        st.success(f"مرحباً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        return

    # Otherwise show the embedded welcome.html
    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=600)
"
        chat_id = "YOUR_CHAT_ID"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"👤 {name}\n👥 {group}\n🕓 {timestamp}"
        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except:
            pass

        # Clear URL params so page refresh won't resubmit
        st.experimental_set_query_params()

        # Optional: trigger rerun to update UI immediately
        st.experimental_rerun()

    # If user already submitted and page is orders, show welcome message or continue
    if "user_name" in st.session_state and st.session_state.page == "orders":
        st.success(f"مرحباً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        return

    # Otherwise show the embedded welcome.html
    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=600)
"
        chat_id = "YOUR_CHAT_ID"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"👤 {name}\n👥 {group}\n🕓 {timestamp}"
        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        except:
            pass

        # Clear URL params so page refresh won't resubmit
        st.experimental_set_query_params()

        # Optional: trigger rerun to update UI immediately
        st.experimental_rerun()

    # If user already submitted and page is orders, show welcome message or continue
    if "user_name" in st.session_state and st.session_state.page == "orders":
        st.success(f"مرحباً {st.session_state.user_name} من قروب {st.session_state.user_group}!")
        return

    # Otherwise show the embedded welcome.html
    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=600)
