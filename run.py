import streamlit as st
from login import login_page, forgot_password_page
from orders import main as orders_main  # ملف عرض الأسئلة والمحاضرات

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def main():
    load_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        if st.session_state.get('show_forgot', False):
            forgot_password_page()
        else:
            login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state['user_name']}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.rerun()

        orders_main()

if __name__ == "__main__":
    main()
