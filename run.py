import streamlit as st
from orders import main as orders_main
import extras  # ✅ ربط ملف الإضافات

def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # ✅ تطبيق التنسيقات
    extras.apply_custom_styles()

    # ✅ تشغيل الوظائف الأساسية
    orders_main()

if __name__ == "__main__":
    main()
