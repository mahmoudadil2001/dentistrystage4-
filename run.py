import streamlit as st
import pandas as pd

# ✅ رابط Google Sheets بصيغة CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/1g1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ/export?format=csv"

# ✅ تحميل بيانات المستخدمين من Google Sheets
@st.cache_data
def load_users():
    df = pd.read_csv(CSV_URL)
    df.columns = ['username', 'password']  # تأكد أن الأعمدة تطابق الأسماء
    return df

# ✅ التحقق من اسم المستخدم وكلمة المرور
def check_login(username, password):
    users_df = load_users()
    for _, row in users_df.iterrows():
        if row['username'].lower() == username.lower() and row['password'] == password:
            return True
    return False

# ✅ تنفيذ التطبيق
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 تسجيل الدخول")
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("✅ دخول"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()  # إعادة تحميل الصفحة بعد تسجيل الدخول
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    else:
        st.success(f"مرحبًا {st.session_state.username}، تم تسجيل الدخول بنجاح! 🎉")
        
        # هنا تكتب بقية موقعك بعد تسجيل الدخول
        st.write("✅ هذا هو محتوى الموقع بعد تسجيل الدخول.")
        # مثال:
        st.markdown("---")
        st.header("📚 المحاضرات والاختبارات")
        st.write("اختر المحاضرة لبدء الاختبار...")

if __name__ == "__main__":
    main()
