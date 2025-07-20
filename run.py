import streamlit as st
from orders import main as orders_main
from chat import main as chat_main  # استيراد من chat.py بدل main.py

if "page" not in st.session_state:
    st.session_state.page = "orders"  # البداية بالصفحة الرئيسية (orders)

def run_app():
    if st.session_state.page == "orders":
        orders_main()
    elif st.session_state.page == "chat":
        chat_main()

if __name__ == "__main__":
    run_app()
import streamlit as st
from chat import main as chat_main

def run_app():
    chat_main()

if __name__ == "__main__":
    run_app()
