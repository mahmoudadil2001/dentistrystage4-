import streamlit as st
from orders import main as orders_main
from chat import main as chat_main
from welcome import main as welcome_main

def main():
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    if st.session_state.page == "welcome":
        welcome_main()
    elif st.session_state.page == "orders":
        orders_main()
    elif st.session_state.page == "chat":
        chat_main()

if __name__ == "__main__":
    main()
