import streamlit as st

# ✅ كود CSS لتطبيق الخلفية المتدرجة والنص المتحرك
def apply_custom_styles():
    st.markdown("""
        <style>
        /* ✅ خلفية متدرجة */
        .main {
            background: linear-gradient(to bottom right, #f0f8ff, #e6f2ff, #ffffff);
        }

        /* ✅ نص مرحب متحرك */
        #welcome-text {
            font-size: 28px;
            color: #0066cc;
            font-weight: bold;
            text-align: center;
            animation: fadeIn 3s ease-in-out;
            margin-bottom: 30px;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        </style>

        <div id="welcome-text">👋 أهلاً بك في موقع المحاضرات!</div>
    """, unsafe_allow_html=True)
