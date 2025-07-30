import streamlit as st
from login import login_page
from orders import main as orders_main
from add_lecture import add_lecture_page

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

def main():
    local_css("styles.css")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        page = st.sidebar.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"])

        if page == "📖 الأسئلة":
            orders_main()

        elif page == "➕ إضافة محاضرة":
            # ✅ طلب كلمة السر قبل فتح الصفحة
            if "admin_verified" not in st.session_state:
                st.session_state["admin_verified"] = False

            if not st.session_state["admin_verified"]:
                password = st.text_input("🔑 أدخل كلمة السر", type="password")
                if st.button("تسجيل دخول"):
                    if password == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["admin_verified"] = True
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ كلمة السر غير صحيحة")
            else:
                add_lecture_page()

if __name__ == "__main__":
    main()
