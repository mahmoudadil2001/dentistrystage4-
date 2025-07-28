import streamlit as st
from login import login_page, forgot_password_page
from orders import main as orders_main  # ملف عرض الأسئلة والمحاضرات

def load_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

def main():
    load_css("styles.css")

    if not st.session_state.get('logged_in', False):
        if st.session_state.get('show_forgot', False):
            forgot_password_page()
        else:
            login_page()
    else:
        st.sidebar.write(f"مرحباً، {st.session_state.get('user_name', 'المستخدم')}")
        if st.sidebar.button("تسجيل خروج"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user_name', None)
            st.experimental_rerun()

        orders_main()

if __name__ == "__main__":
    main()
