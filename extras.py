import streamlit as st

def chatango_popup_button():
    # هذا الزر يظهر في الزاوية اليسرى السفلية، ويعرض شات Chatango داخل نافذة منبثقة
    st.markdown("""
    <style>
    /* زر الدردشة */
    #chatango-button {
        position: fixed;
        bottom: 20px;
        left: 20px;
        background-color: #0078d7;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        cursor: pointer;
        font-size: 16px;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: background-color 0.3s ease;
    }
    #chatango-button:hover {
        background-color: #005a9e;
    }

    /* نافذة الشات المنبثقة */
    #chatango-popup {
        display: none;
        position: fixed;
        bottom: 70px;
        left: 20px;
        width: 350px;
        height: 400px;
        border: 2px solid #0078d7;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        z-index: 9999;
        background-color: white;
        overflow: hidden;
    }
    </style>

    <button id="chatango-button">💬 دردشة</button>

    <div id="chatango-popup">
        <iframe src="https://dentistrychat.chatango.com/" width="100%" height="100%" frameborder="0"></iframe>
    </div>

    <script>
    const btn = document.getElementById('chatango-button');
    const popup = document.getElementById('chatango-popup');

    btn.onclick = () => {
        if (popup.style.display === "none" || popup.style.display === "") {
            popup.style.display = "block";
        } else {
            popup.style.display = "none";
        }
    }
    </script>
    """, unsafe_allow_html=True)
