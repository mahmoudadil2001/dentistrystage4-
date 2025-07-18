import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("styles.css")  # هنا تربط ملف الستايل
    # باقي كود main...

# مثال بسيط لتجربة
if __name__ == "__main__":
    main()
from orders import main

if __name__ == "__main__":
    main()
