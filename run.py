import streamlit as st
from login import login_page
from orders import orders_o, get_current_questions_count
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
        # تأكد من تهيئة القيم الأساسية في session_state
        if "selected_subject" not in st.session_state:
            st.session_state.selected_subject = "endodontics"
        if "selected_lecture" not in st.session_state:
            st.session_state.selected_lecture = 1
        if "selected_version" not in st.session_state:
            st.session_state.selected_version = 1
        if "current_question" not in st.session_state:
            st.session_state.current_question = 0

        # جلب عدد الأسئلة الحالية حسب المادة والمحاضرة والإصدار
        questions_count = get_current_questions_count(
            st.session_state.selected_subject,
            st.session_state.selected_lecture,
            st.session_state.selected_version
        )

        with st.sidebar:
            st.markdown("### 📝 أسئلة المحاضرة")
            for i in range(questions_count):
                label = f"Question {i+1}"
                if st.button(label, key=f"nav_{i}"):
                    st.session_state.current_question = i
            
            st.markdown("---")

            # زر اختيار الصفحة تحت أزرار الأسئلة
            page = st.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"],
                            index=0 if "page" not in st.session_state else ["📖 الأسئلة", "➕ إضافة محاضرة"].index(st.session_state.page))
            st.session_state.page = page

        # عرض الصفحة المختارة
        if st.session_state.page == "📖 الأسئلة":
            orders_o()
        elif st.session_state.page == "➕ إضافة محاضرة":
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
                        st.rerun()
                    else:
                        st.error("❌ كلمة السر غير صحيحة")
            else:
                add_lecture_page()

if __name__ == "__main__":
    main()
