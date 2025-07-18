import streamlit as st
import os
import importlib.util
import requests
import extras  # ✅ ربط ملف التنسيقات

# ✅ تطبيق التنسيق الجميل من extras
extras.apply_custom_style()

# ✅ إرسال الاسم والقروب إلى تليجرام
def send_to_telegram(name, group):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👨‍🎓 الكروب: {group}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg}
    requests.post(url, data=data)

# ✅ أسماء المحاضرات
custom_titles_data = {
    ("endodontics", 1): "Lecture 1 introduction",
    ("endodontics", 2): "Lecture 2 test",
    ("generalmedicine", 1): "General Med Lecture 1"
}

custom_titles = {}
for (subject, num), title in custom_titles_data.items():
    custom_titles[f"{subject}_{num}"] = title

# ✅ تحميل الأسئلة
def load_questions(subject, lecture_number):
    filename = f"questions/{subject}_{lecture_number}.py"
    if not os.path.isfile(filename):
        st.error("الملف غير موجود.")
        return []
    spec = importlib.util.spec_from_file_location("questions_module", filename)
    questions_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(questions_module)
    return questions_module.questions

# ✅ الصفحة الرئيسية
def main():
    st.title("🦷 منصة أسئلة طب الأسنان")

    with st.form("user_info_form"):
        name = st.text_input("👤 أدخل اسمك")
        group = st.text_input("👨‍🎓 أدخل كروبك")
        submitted = st.form_submit_button("🚀 ابدأ")
        if submitted and name and group:
            st.session_state.name = name
            st.session_state.group = group
            send_to_telegram(name, group)
            st.success("تم تسجيل الدخول بنجاح 🎉")

    if "name" in st.session_state and "group" in st.session_state:
        subject = st.selectbox("📚 اختر المادة", ["endodontics", "generalmedicine"])
        lecture_number = st.number_input("📖 رقم المحاضرة", min_value=1, max_value=20, step=1)

        key = f"{subject}_{lecture_number}"
        title = custom_titles.get(key, f"Lecture {lecture_number}")
        st.subheader(f"📄 {title}")

        questions = load_questions(subject, lecture_number)

        if not questions:
            st.warning("لا توجد أسئلة لهذه المحاضرة.")
            return

        for idx, q in enumerate(questions):
            st.markdown(f"### سؤال {idx + 1}")
            user_answer = st.radio(q["question"], q["options"], key=f"q{idx}")
            if user_answer == q["answer"]:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ خاطئة. الإجابة الصحيحة: {q['answer']}")
                explanation = q.get("explanation")
                if explanation:
                    st.info(f"🧠 شرح: {explanation}")
