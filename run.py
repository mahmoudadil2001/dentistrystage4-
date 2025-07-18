import streamlit as st
from orders import main as orders_main
import extras  # ✅ ربط ملف التصميمات

# ✅ تطبيق التنسيقات
extras.load_custom_styles()

# ✅ إظهار البطاقة الترحيبية (فقط إذا ما سجل اسمه)
if "user_logged" not in st.session_state:
    extras.show_welcome_card()

# ✅ تشغيل المنصة
orders_main()
