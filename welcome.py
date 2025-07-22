import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import json

def main():
    st.markdown("<style>body {background-color: #f9f9fb;}</style>", unsafe_allow_html=True)
    st.title("")

    # Load welcome.html content (you can also read it from file)
    with open("welcome.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Embed the HTML with height 600px and allow scripts
    components.html(
        html_content,
        height=600,
        scrolling=False,
        # key="welcome_html"
    )

    # Listen for message events from iframe using Streamlit experimental feature
    # BUT Streamlit currently does NOT directly capture postMessage from components.html
    # So, workaround: ask user to fill Streamlit input fields for now

    # Alternative simple fallback: show inputs and wait for submit in Streamlit
    # (you can remove this if you want strict iframe-only UI)
    st.markdown("---")
    st.write("أو أدخل اسمك وقروبك هنا:")

    with st.form("fallback_form"):
        name = st.text_input("اسمك")
        group = st.text_input("قروبك")
        submitted = st.form_submit_button("موافق")
        if submitted and name and group:
            st.success(f"مرحباً {name}!")
            st.session_state["page"] = "orders"
            st.session_state["user_name"] = name
            st.session_state["user_group"] = group

            # Send to telegram
            bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
            chat_id = "6283768537"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"👤 {name}\n👥 {group}\n🕓 {timestamp}"
            try:
                requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
            except Exception as e:
                st.error(f"Failed to send telegram message: {e}")
