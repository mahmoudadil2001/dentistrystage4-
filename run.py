import streamlit as st
from orders import main as orders_main
import extras  # ربط ملف التنسيقات

def main():
    # تطبيق التنسيقات أولاً
    extras.apply_custom_styles()

    # تشغيل التطبيق الرئيسي
    orders_main()

if __name__ == "__main__":
    main()
