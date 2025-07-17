import streamlit as st

# بداية الكود بعد تسجيل الدخول وغيره

st.markdown("""
<style>
#online_count {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 8px;
    color: #2c7be5;
    text-align: center;
}
#chatango_button {
    display: block;
    margin: 0 auto;
    background-color: #0088cc;
    color: white;
    padding: 10px 20px;
    border-radius: 30px;
    cursor: pointer;
    font-family: sans-serif;
    font-size: 16px;
    text-align: center;
    width: 200px;
}
</style>

<div id="online_count">جاري تحميل عدد الأشخاص...</div>

<button id="chatango_button">💬 افتح دردشة الموقع</button>

<script>
const openChatango = () => {
    if(document.getElementById('chatango_embed')) return; // لو مفتوح بالفعل

    const iframe = document.createElement('iframe');
    iframe.src = 'https://dentistrychat.chatango.com/';
    iframe.id = 'chatango_embed';
    iframe.style.position = 'fixed';
    iframe.style.bottom = '20px';
    iframe.style.right = '20px';
    iframe.style.width = '350px';
    iframe.style.height = '400px';
    iframe.style.border = '1px solid #ccc';
    iframe.style.borderRadius = '8px';
    iframe.style.zIndex = 9999;
    iframe.style.backgroundColor = 'white';
    document.body.appendChild(iframe);

    // إضافة زر إغلاق
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✖';
    closeBtn.style.position = 'fixed';
    closeBtn.style.bottom = '425px';
    closeBtn.style.right = '20px';
    closeBtn.style.zIndex = 10000;
    closeBtn.style.background = '#ff5c5c';
    closeBtn.style.color = 'white';
    closeBtn.style.border = 'none';
    closeBtn.style.borderRadius = '50%';
    closeBtn.style.width = '30px';
    closeBtn.style.height = '30px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.onclick = () => {
        iframe.remove();
        closeBtn.remove();
    }
    document.body.appendChild(closeBtn);

    // بعد فتح iframe نبدأ تحديث العدد كل 5 ثواني
    setTimeout(updateOnlineCount, 3000); // تأخير بسيط للتحميل
};

document.getElementById('chatango_button').onclick = openChatango;

// دالة تحديث عدد المستخدمين الأونلاين من iframe (لو كان بإمكاننا الوصول للـiframe داخلياً)
function updateOnlineCount() {
    const onlineCountDiv = document.getElementById('online_count');

    // ** ملاحظة مهمة: لا يمكن جلب بيانات من iframe في دومين مختلف (cross-origin)
    // لذا نحتاج طريقة أخرى أو أن يكون مزود الدردشة يوفر API أو iframe مدمج مع عداد.
    // للأسف Chatango يمنع الوصول لمحتوى iframe خارجي لسياسة الأمان.

    // بالتالي لا يمكننا قراءة العدد بشكل مباشر من iframe عبر جافاسكريبت.

    // كبديل: إظهار رسالة فقط أو محاولة من خلال طرق أخرى (Websocket API، API خارجي، إذا توفرت)

    onlineCountDiv.textContent = 'عدد الأشخاص الأونلاين يعرض داخل نافذة الدردشة فقط';
}

// عرض رسالة بداية
updateOnlineCount();
</script>
""", unsafe_allow_html=True)
