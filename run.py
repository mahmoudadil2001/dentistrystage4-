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
        # نبدأ محتويات الشريط الجانبي
        with st.sidebar:
            # أي محتوى تريده فوق، مثلاً هنا لا يوجد شيء إضافي
            # لو عندك عنوان أو معلومات تكتبها هنا
            
            # **محتويات الشريط الجانبي الأخرى ممكن توضع هنا إذا احتجت**
            # ...

            # نضيف مسافة فارغة لدفع الاختيار للأسفل (اختياري)
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)

            # هنا في النهاية زرار اختيار الصفحة
            page = st.radio("📂 اختر الصفحة", ["📖 الأسئلة", "➕ إضافة محاضرة"])

        # بعد تحديد الصفحة
        if page == "📖 الأسئلة":
            orders_main()

        elif page == "➕ إضافة محاضرة":
            if "admin_verified" not in st.session_state:
                st.session_state["admin_verified"] = False

            if not st.session_state["admin_verified"]:
                # ✅ إضافة الشرح فوق مربع كلمة السر
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
