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
        # التحكم في وضع الاختبار
        if "exam_mode" not in st.session_state:
            st.session_state["exam_mode"] = False

        # صفحة الاختبار فقط مع زر خروج
        if st.session_state["exam_mode"]:
            st.button("⬅️ خروج من وضع الاختبار", key="exit_exam_mode", on_click=exit_exam_mode)
            # عرض الأسئلة فقط بدون قائمة جانبية أو أي شيء آخر
            orders_main()
            return

        # الصفحة الرئيسية مع أزرار اختيار، مع زر للدخول لوضع الاختبار
        page = st.sidebar.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"])

        if page == "📖 الأسئلة":
            orders_main()
            # زر دخول وضع الاختبار تحت المحتوى (نفترض بعد orders_main)
            st.markdown("<br>", unsafe_allow_html=True)  # مسافة بسيطة تحت المحتوى
            if st.button("🎯 الدخول في وضع الاختبار"):
                st.session_state["exam_mode"] = True
                st.experimental_rerun()

        elif page == "➕ إضافة محاضرة":
            if "admin_verified" not in st.session_state:
                st.session_state["admin_verified"] = False

            if not st.session_state["admin_verified"]:
                st.markdown("""
                ### 👋 أهلا شباب  
                فقط الأدمن يقدر يضيف ويحذف محاضرات.  
                إذا حاب تساعدني راسلني على التليجرام 👉 **@io_620**
                """)
                password = st.text_input("🔑 أدخل كلمة السر", type="password")
                if st.button("تسجيل دخول"):
                    if password == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["admin_verified"] = True
                        st.success("✅ تم تسجيل الدخول بنجاح!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ كلمة السر غير صحيحة")
            else:
                add_lecture_page()

def exit_exam_mode():
    st.session_state["exam_mode"] = False
    st.experimental_rerun()

if __name__ == "__main__":
    main()
