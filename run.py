import streamlit as st
import pandas as pd

def check_login(username, password):
    df = pd.read_csv("users.csv")
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
            # هنا يبدأ عرض محتوى التطبيق
            st.write("هنا محتوى التطبيق بعد الدخول")
        else:
            st.error("اسم المستخدم أو كلمة المرور خاطئ.")

if __name__ == "__main__":
    main()
