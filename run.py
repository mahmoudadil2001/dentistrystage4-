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
        if "exam_mode" not in st.session_state:
            st.session_state["exam_mode"] = False

        if st.session_state["exam_mode"]:
            # زر الخروج من وضع الاختبار في الأعلى
            if st.button("⬅️ خروج من وضع الاختبار"):
                st.session_state["exam_mode"] = False
                st.experimental_rerun()

            # عرض وضع الاختبار فقط (الأسئلة)
            orders_main()
            return

        # الوضع الطبيعي
        page = st.sidebar.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"])

        if page == "📖 الأسئلة":
            orders_main()

            # إضافة مسافة ثم زر الدخول في وضع الاختبار في الوسط
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="text-align: center;">
                    <button style="
                        background-color: #0078d7; 
                        color: white; 
                        border: none; 
                        border-radius: 12px; 
                        padding: 12px 30px; 
                        font-size: 18px; 
                        font-weight: 600; 
                        cursor: pointer;
                        box-shadow: 0 4px 8px rgba(0, 120, 215, 0.3);
                    " id="start_exam_btn">🎯 الدخول في وضع الاختبار</button>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # بدي نستخدم st.button لكن ما بنقدر نضيف زر داخل html بسهولة، لذلك نستخدم st.button عادي وسط الصفحة:
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

if __name__ == "__main__":
    main()
