import streamlit as st

def extras_feature():
    st.info("هذه ميزة إضافية يمكن تطويرها هنا بدون تعديل في orders.py أو run.py")

def main():
    # هنا تضع أي كود تريده يظهر في الموقع
    st.header("قسم الإضافات")
    extras_feature()
