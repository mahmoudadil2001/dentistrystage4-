import streamlit as st
import pandas as pd

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ/export?format=csv&id=1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ&gid=0"

def check_login(username, password):
    # نقرأ CSV بدون رأس ونعطي أسماء الأعمدة يدويًا
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL, header=None, names=["username", "password", "email", "phone"])
    
    for _, row in df.iterrows():
        if row['username'].lower() == username.lower() and row['password'] == password:
            return True
    return False

def main():
    st.title("تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    login_button = st.button("دخول")

    if login_button:
        if check_login(username, password):
            st.success(f"مرحبًا {username}، تم تسجيل الدخول بنجاح!")
            st.write("هنا محتوى الموقع بعد الدخول")
        else:
            st.error("اسم المستخدم أو كلمة المرور خاطئ.")

if __name__ == "__main__":
    main()
