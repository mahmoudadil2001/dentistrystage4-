import streamlit as st
import streamlit.components.v1 as components

# عنوان الموقع أو رسالة ترحيب
st.title("موقع المحاضرات والدردشة")

# تسجيل الدخول - لو حابب تضيفه
if "user_logged" not in st.session_state:
    st.header("👤 أدخل معلوماتك للبدء")
    name = st.text_input("✍️ اسمك؟")
    group = st.text_input("👥 كروبك؟")

    if st.button("✅ موافق"):
        if not name.strip() or not group.strip():
            st.warning("يرجى ملء كل الحقول.")
        else:
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            st.experimental_rerun()
    st.stop()

st.markdown(f"### 👋 أهلاً {st.session_state.visitor_name}")

# -----------------------
# زر دردشة منبثق - Floating Button & Popup Chat

# حالة عرض الدردشة
if "chat_visible" not in st.session_state:
    st.session_state.chat_visible = False

# HTML + CSS + JS لزر الدردشة المنبثق وصندوق الدردشة
chat_html = """
<style>
/* زر الدردشة الدائري */
#chat-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background-color: #0088cc;
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 30px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  z-index: 1000;
  transition: background-color 0.3s ease;
}
#chat-button:hover {
  background-color: #005f7a;
}

/* صندوق الدردشة المنبثق */
#chat-popup {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  z-index: 1000;
  display: none;
  flex-direction: column;
  overflow: hidden;
}

/* عنوان الصندوق */
#chat-header {
  background: #0088cc;
  color: white;
  padding: 12px;
  font-weight: bold;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* زر إغلاق الصندوق */
#close-chat {
  background: transparent;
  border: none;
  color: white;
  font-size: 22px;
  cursor: pointer;
}

/* iframe الدردشة */
#chat-iframe {
  flex-grow: 1;
  border: none;
}
</style>

<button id="chat-button" title="افتح الدردشة">💬</button>

<div id="chat-popup">
  <div id="chat-header">
    دردشة الدعم المباشر
    <button id="close-chat" title="إغلاق">×</button>
  </div>
  <iframe id="chat-iframe" src="https://dentistrychat.chatango.com/" ></iframe>
</div>

<script>
const chatBtn = document.getElementById('chat-button');
const chatPopup = document.getElementById('chat-popup');
const closeBtn = document.getElementById('close-chat');

chatBtn.onclick = () => {
  if (chatPopup.style.display === 'flex') {
    chatPopup.style.display = 'none';
  } else {
    chatPopup.style.display = 'flex';
  }
};

closeBtn.onclick = () => {
  chatPopup.style.display = 'none';
};
</script>
"""

components.html(chat_html, height=600, scrolling=False)
