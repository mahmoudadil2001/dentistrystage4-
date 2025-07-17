import streamlit as st
from orders import orders_o, send_to_telegram

# التحقق من تسجيل المستخدم
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك؟ ")
    group = st.text_input("👥 كروبك؟")

    if st.button("✅ موافق"):
        if name.strip() == "" or group.strip() == "":
            st.warning("يرجى ملء كل الحقول.")
        else:
            send_to_telegram(name, group)
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            st.experimental_rerun()
    st.stop()

st.markdown(f"### 👋 أهلاً {st.session_state.visitor_name}")

orders_o()

# زر فتح دردشة Chatango
st.markdown("""
    <div style="display:flex; justify-content:center; margin-top:40px;">
        <button onclick="window.open('https://dentistrychat.chatango.com/', 'chatango', 'width=400,height=500,resizable=yes')" 
                style="background:#00b8ff; color:#fff; border:none; padding:12px 25px; border-radius:25px; cursor:pointer; font-size:16px; font-family:sans-serif;">
            💬 افتح دردشة الموقع (Chatango)
        </button>
    </div>
""", unsafe_allow_html=True)

# زر قناة التلي تحت المحتوى
st.markdown('''
    <div style="display:flex; justify-content:center; margin-top:40px;">
        <a href="https://dentistrychat.chatango.com/" target="_blank"
           style="background:#00b8ff; color:#fff; border:none; padding:12px 25px; border-radius:25px;
                  cursor:pointer; font-size:16px; font-family:sans-serif; text-decoration:none; display:inline-block;">
            💬 افتح دردشة الموقع (Chatango)
        </a>
    </div>
''', unsafe_allow_html=True)
