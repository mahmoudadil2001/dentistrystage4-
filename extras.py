import streamlit as st

def load_custom_styles():
    st.markdown("""
    <style>
    /* 🔵 خلفية متدرجة */
    body {
        background: linear-gradient(135deg, #f0f4f8, #d9e4f5);
    }

    /* 🔵 خط أنيق */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }

    /* 🔵 زر أزرق ناعم */
    button[kind="primary"] {
        background-color: #008CBA !important;
        color: white !important;
        border-radius: 12px;
        padding: 8px 20px;
        font-size: 16px;
    }

    /* 🔵 بطاقة ترحيب */
    .welcome-box {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 50px auto;
        text-align: center;
    }

    .welcome-box h2 {
        color: #008CBA;
    }

    /* 🔵 عداد النتيجة */
    .score-counter {
        font-size: 48px;
        color: #008CBA;
        text-align: center;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def show_welcome_card():
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 أهلاً بك في منصة أسئلة طب الأسنان</h2>
        <p>منصة تفاعلية للاختبار الذاتي وتثبيت المعلومات 🧠</p>
    </div>
    """, unsafe_allow_html=True)

def show_score_animation(final_score, total):
    import time

    st.markdown("<div class='score-counter'>النتيجة:</div>", unsafe_allow_html=True)
    score_placeholder = st.empty()

    for i in range(final_score + 1):
        score_placeholder.markdown(f"<div class='score-counter'>{i} / {total}</div>", unsafe_allow_html=True)
        time.sleep(0.05)
