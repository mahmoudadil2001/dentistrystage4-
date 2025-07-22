import streamlit as st
import pandas as pd

# 🟢 تحميل بيانات المستخدمين من Google Sheets
@st.cache_data
def load_users():
    CSV_URL = "https://docs.google.com/spreadsheets/d/1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ/export?format=csv"
    df = pd.read_csv(CSV_URL)
    return df

# 🟢 التحقق من معلومات الدخول
def check_login(username, password, users_df):
    for _, row in users_df.iterrows():
        if str(row['username']).lower() == username.lower() and str(row['password']) == password:
            return True
    return False

# 🟢 الصفحة الرئيسية بعد تسجيل الدخول
def show_main_page(username):
    st.success(f"مرحبًا {username}، تم تسجيل الدخول بنجاح! 🎉")
    st.write("✅ هذا هو محتوى الموقع بعد تسجيل الدخول.")

# 🟢 الصفحة الرئيسية
def main():
    st.set_page_config(page_title="تسجيل الدخول", page_icon="🔐", layout="centered")

    # 🔄 حالة تسجيل الدخول
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    users_df = load_users()

    if st.session_state.logged_in:
        show_main_page(st.session_state.username)
    else:
        st.title("🔐 تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            if check_login(username, password, users_df):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")

if __name__ == "__main__":
    main()
