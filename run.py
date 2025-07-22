import streamlit as st
import pandas as pd
from orders import main as orders_main  # لو عندك ملف orders.py

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ/export?format=csv&id=1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ&gid=0"

def check_login(username, password):
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL, header=None, names=["username", "password", "email", "phone"])
    df = df.fillna('')

    for _, row in df.iterrows():
        user_cell = row['username']
        pass_cell = row['password']

        if (isinstance(user_cell, str) and isinstance(pass_cell, str) and
            user_cell.lower() == username.lower() and pass_cell == password):
            return True
    return False

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        st.title("تسجيل الدخول")

        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        login_button = st.button("دخول")

        if login_button:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()  # لإعادة تشغيل التطبيق والانتقال للمحتوى
            else:
                st.error("اسم المستخدم أو كلمة المرور خاطئ.")
    else:
        st.success(f"مرحبًا {st.session_state.username}، تم تسجيل الدخول بنجاح!")
        
        # زر تسجيل الخروج
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()

        # عرض المحتوى بعد الدخول
        orders_main()

if __name__ == "__main__":
    main()
