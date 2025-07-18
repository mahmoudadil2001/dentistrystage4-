import streamlit as st

def inject_css(file_name="styles.css"):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def inject_telegram_button():
    st.markdown("""
    <a href="https://t.me/dentistryonly0" target="_blank" class="telegram-btn" aria-label="Telegram Channel">
        قناة التلي
        <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/>
        </svg>
    </a>
    """, unsafe_allow_html=True)

def inject_js_alert():
    st.markdown("""
    <script>
    window.onload = function() {
        alert("مرحباً بك في موقع المحاضرات! نتمنى لك تجربة مفيدة وممتعة.");
    };
    </script>
    """, unsafe_allow_html=True)

def inject_welcome_box():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0078d7, #00bfff);
        color: white;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        font-family: 'Tajawal', sans-serif;
        box-shadow: 0 8px 16px rgba(0,120,215,0.3);
        margin-bottom: 30px;">
        <h2>👋 مرحباً بك في موقع المحاضرات</h2>
        <p style="font-size:18px;">تابع المحاضرات، حل الاختبارات، وارتقِ بمستواك العلمي بسهولة</p>
        <img src="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif" width="120" alt="Welcome GIF" />
    </div>
    """, unsafe_allow_html=True)
