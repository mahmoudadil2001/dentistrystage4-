import streamlit as st

def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")
    st.button("زر تجريبي")  # جرب الزر مع التأثيرات
    # باقي كودك...

if __name__ == "__main__":
    main()
from orders import main

if __name__ == "__main__":
    main()
