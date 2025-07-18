import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
    /* خلفية متدرجة ناعمة */
    body {
        background: linear-gradient(to bottom right, #f8f9fa, #e2e6ea, #dee2e6);
    }

    /* كروت أنيقة */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 15px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }

    /* مربع الأسئلة */
    .stRadio > div {
        background-color: #ffffffdd;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* العنوان الرئيسي */
    h1 {
        color: #2c3e50;
        font-size: 2.2em;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
