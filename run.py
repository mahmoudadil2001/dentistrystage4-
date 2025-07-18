import streamlit as st
from orders import main as orders_main

# ✅ قراءة HTML مخصص وعرضه
def load_custom_html(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        html_content = f.read()
        st.markdown(html_content, unsafe_allow_html=True)

# ✅ ربط خطوط Google Fonts
def google_fonts():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Cairo&family=Tajawal&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

def main():
    google_fonts()
    load_custom_html("custom_layout.html")  # ✅ HTML واجهة مخصصة
    orders_main()

if __name__ == "__main__":
    main()
