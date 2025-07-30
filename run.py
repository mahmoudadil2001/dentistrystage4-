import streamlit as st
from login import login_page
from orders import main as orders_main
from add_lecture import add_lecture_page  # ✅ استدعاء الصفحة الجديدة

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

def main():
    local_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        page = st.sidebar.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"])
        
        if page == "📖 الأسئلة":
            orders_main()
        elif page == "➕ إضافة محاضرة":
            add_lecture_page()

if __name__ == "__main__":
    main()
