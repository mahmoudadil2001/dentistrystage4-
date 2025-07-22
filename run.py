import streamlit as st
from orders import main as orders_main
from chat import main as chat_main
from welcome import show_welcome  # Import the welcome screen function

def main():
    if "welcome_shown" not in st.session_state:
        show_welcome()
        if st.button("👉 Click Here to Continue"):
            st.session_state.welcome_shown = True
            st.experimental_rerun()
    else:
        orders_main()

        if st.session_state.get("page") == "chat":
            chat_main()

if __name__ == "__main__":
    main()
