import streamlit as st
from orders import main as orders_main

# ⬅️ تحميل CSS من الملف
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")  # ربط CSS
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>👨‍⚕️ أهلاً بك في منصة المحاضرات</h2>
            <p>اختر المحاضرة من القائمة الجانبية وابدأ الآن!</p>
            <a href="#" class="button">بدء الاختبار</a>
            <a href="#" class="button">عرض المحاضرات</a>
            <div class="footer">
                جميع الحقوق محفوظة © 2025
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 🟢 تشغيل بقية الموقع
    orders_main()

if __name__ == "__main__":
    main()
