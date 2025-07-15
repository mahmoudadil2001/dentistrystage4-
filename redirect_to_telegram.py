import streamlit as st

def redirect_to_telegram():
    if st.button("انتقل إلى قناة تيليجرام @io_620"):
        st.markdown(
            """
            <script>
            window.open('https://t.me/io_620', '_blank')
            </script>
            """,
            unsafe_allow_html=True
        )
