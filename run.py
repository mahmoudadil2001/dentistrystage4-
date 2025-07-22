import streamlit as st
from orders import main as orders_main

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def main():
    load_css("styles.css")  # تأكد أن ملف styles.css موجود بجانب run.py

    # تحقق من حالة الدخول في الجلسة
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("## 👋 مرحبًا بك في موقع Dentistrystage4")
        st.markdown("### 📝 لتسجيل الدخول:")
        st.markdown("[اضغط هنا لفتح صفحة تسجيل الدخول](https://script.google.com/macros/s/AKfycYOURURL/exec)")

        st.warning("🔒 بعد تسجيل الدخول، ارجع إلى هذه الصفحة واضغط الزر بالأسفل لتأكيد الدخول.")
        if st.button("✅ تم تسجيل الدخول"):
            st.session_state.logged_in = True
            st.experimental_rerun()

    else:
        orders_main()

if __name__ == "__main__":
    main()
