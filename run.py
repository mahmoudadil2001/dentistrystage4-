import streamlit as st
from orders import main as orders_main
import extras  # ✅ ربط ملف التنسيقات

# ✅ تحميل التنسيقات أولاً
extras.load_custom_styles()

# ✅ إظهار البطاقة الترحيبية (فقط إذا ما سجل اسمه)
if "user_logged" not in st.session_state:
    extras.show_welcome_card()

# ✅ تشغيل الموقع
orders_main()
