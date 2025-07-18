import streamlit as st
from orders import main as orders_main  # استيراد الدالة الرئيسية من orders.py

def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")  # ربط ملف CSS
    orders_main()            # تشغيل الكود الرئيسي من ملف orders.py

if __name__ == "__main__":
    main()
