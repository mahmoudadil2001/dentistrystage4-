import streamlit as st
from login import login_page
from orders import main as orders_main

def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

def main():
    local_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        orders_main()

if __name__ == "__main__":
    main()
