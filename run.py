import streamlit as st

def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")
    st.title("مرحباً بك في التطبيق")

    if st.button("فتح غرفة الدردشة"):
        # استيراد ملف main.py وتنفيذ دالة main منه
        from main import main as chat_main
        chat_main()

if __name__ == "__main__":
    main()
