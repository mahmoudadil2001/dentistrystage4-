import streamlit as st
from orders import main as orders_main
import extras

def main():
    extras.apply_custom_styles()  # طبق التنسيقات من ملف extras.py
    orders_main()  # شغل التطبيق من ملف orders.py

if __name__ == "__main__":
    main()
