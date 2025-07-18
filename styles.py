import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* خلفية متدرجة هادئة */
    .main {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
        min-height: 100vh;
        padding: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* أزرار أنيقة */
    div.stButton > button {
        background-color: #4CAF50;
        border-radius: 12px;
        color: white;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }
    div.stButton > button:hover 
        background-color: #45a049;
    }

    /* عناوين */
    h1, h2, h3, h4, h5, h6 {
        color: #333333;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)
button {
    background-color: #0078d7;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease;
    box-shadow: 0 4px 8px rgba(0, 120, 215, 0.3);
}

button:hover {
    background-color: #005a9e;
    transform: scale(1.1);
    box-shadow: 0 6px 12px rgba(0, 90, 158, 0.5);
}
