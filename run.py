import streamlit as st
from orders import main as orders_main

def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")

    st.markdown("""
    <h2 style='text-align: center;'>👨‍⚕️ أهلاً بك في منصة المحاضرات</h2>
    <p style='text-align: center;'>اختر المحاضرة من القائمة الجانبية وابدأ الآن!</p>

    <div style="text-align: center;">
      <a href="#" class="button">بدء الاختبار</a>
      <a href="#" class="button">عرض المحاضرات</a>
    </div>

    <div class="footer">
      جميع الحقوق محفوظة © 2025
    </div>
    """, unsafe_allow_html=True)

    orders_main()

if __name__ == "__main__":
    main()
