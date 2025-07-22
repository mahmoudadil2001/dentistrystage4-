import streamlit as st
import os
import importlib.util
import requests

# 🟢 إرسال الاسم والقروب إلى تليجرام
def send_to_telegram(name, group):
    bot_token = "8165532786:AAHYiNEgO8k1TDz5WNtXmPHNruQM15LIgD4"
    chat_id = "6283768537"
    msg = f"📥 شخص جديد دخل الموقع:\n👤 الاسم: {name}\n👥 القروب: {group}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# ✅ أسماء المحاضرات (سهل التعديل لاحقًا)
custom_titles_data = {
    ("endodontics", 1): "Lecture 1 introduction",
    ("endodontics", 2): "Lecture 2 periapical disease classification",
    ("endodontics", 3): "Lecture 3 name",
    ("generalmedicine", 1): "Lecture 1 name",
    ("oralpathology", 1): "Lec 1 Biopsy"
}

custom_titles = {}
for (subject, num), title in custom_titles_data.items():
    custom_titles.setdefault(subject, {})[num] = title

def count_lectures(subject_name, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    if not os.path.exists(subject_path):
        return 0
    return len([f for f in os.listdir(subject_path) if f.startswith(subject_name) and f.endswith(".py")])

def import_module_from_folder(subject_name, lecture_num, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    module_file = os.path.join(subject_path, f"{subject_name}{lecture_num}.py")

    if not os.path.exists(module_file):
        return None

    spec = importlib.util.spec_from_file_location(f"{subject_name}{lecture_num}", module_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def orders_o():
    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
    ]

    subject = st.selectbox("اختر المادة", subjects)

    total_lectures = count_lectures(subject)
    if total_lectures == 0:
        st.error(f"⚠️ لا يوجد ملفات محاضرات للمادة {subject}!")
        return

    # ✅ طريقة عرض المحاضرات بشكل أفقي
    st.markdown("### 🎓 اختر المحاضرة:")
    cols = st.columns(min(total_lectures, 4))  # لا يزيد عن 4 أعمدة في السطر

    lecture = None
    for i in range(total_lectures):
        lec_title = custom_titles.get(subject, {}).get(i+1, f"Lecture {i+1}")
        col = cols[i % 4]
        if col.button(lec_title, key=f"lec_btn_{i}"):
            lecture = lec_title
            st.session_state.selected_lecture_num = i + 1
            st.session_state.selected_lecture_title = lec_title

    if "selected_lecture_num" not in st.session_state:
        return

    lecture_num = st.session_state.selected_lecture_num
    lecture = st.session_state.selected_lecture_title

    questions_module = import_module_from_folder(subject, lecture_num)
    if questions_module is None:
        st.error(f"⚠️ الملف {subject}{lecture_num}.py غير موجود في المجلد {subject}.")
        return

    questions = questions_module.questions
    Links = getattr(questions_module, "Links", [])

    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lecture) or \
       (st.session_state.get("current_subject", None) != subject):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lecture
        st.session_state.current_subject = subject

    def normalize_answer(q):
        answer = q.get("answer") or q.get("correct_answer")
        options = q["options"]
        if isinstance(answer, int) and 0 <= answer < len(options):
            return options[answer]
        if isinstance(answer, str):
            answer_clean = answer.strip().upper()
            if answer_clean in ["A", "B", "C", "D"]:
                idx = ord(answer_clean) - ord("A")
                if 0 <= idx < len(options):
                    return options[idx]
            if answer in options:
                return answer
        return None

    with st.sidebar:
        st.markdown(f"### 🧪 {subject.upper()}")
        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            status = "⬜" if user_ans is None else ("✅" if user_ans == correct_text else "❌")
            if st.button(f"{status} سؤال {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)
        st.markdown(f"### Q{index+1}/{len(questions)}: {q['question']}")
        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])
        selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")
        if not st.session_state.answer_shown[index]:
            if st.button("أجب", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            user_ans = st.session_state.user_answers[index]
            if user_ans == correct_text:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ الإجابة: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 الشرح: {q['explanation']}")
            if st.button("السؤال التالي", key=f"next_{index}"):
                if index + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()
        if Links:
            st.markdown("---")
            for link in Links:
                st.markdown(f"- [{link['title']}]({link['url']})")

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question)
    else:
        st.header("🎉 تم الانتهاء من الاختبار!")
        correct = sum(
            1 for i, q in enumerate(questions)
            if st.session_state.user_answers[i] == normalize_answer(q)
        )
        st.success(f"النتيجة: {correct} من {len(questions)}")
        if st.button("🔁 أعد الاختبار"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()

def main():
    if "user_logged" not in st.session_state:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
                border-radius: 15px;
                padding: 20px;
                color: #003049;
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 25px;
            ">
            ✨ مرحباً بكم في منصة مراجعة مواد طب الأسنان - المرحلة الرابعة / جامعة الأسراء ✨
            </div>
        """, unsafe_allow_html=True)

        name = st.text_input("✍️ اسمك؟ ")
        group = st.text_input("👥 كروبك؟")
        if st.button("✅ موافق"):
            if not name.strip() or not group.strip():
                st.warning("يرجى ملء كل الحقول.")
            else:
                send_to_telegram(name, group)
                st.session_state.user_logged = True
                st.session_state.visitor_name = name
                st.session_state.visitor_group = group
                st.rerun()
        st.stop()

    # ✅ بطاقة عرض معلومات المستخدم
    st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:15px 20px;border-radius:12px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <h4 style="margin-bottom:5px;">👤 الاسم: <span style="color:#3b5998;">{st.session_state.visitor_name}</span></h4>
            <h5>📘 المجموعة: <span style="color:#00a86b;">{st.session_state.visitor_group}</span></h5>
        </div>
    """, unsafe_allow_html=True)

    orders_o()

    st.markdown("""
    <div style="text-align:center; margin-top:50px;">
        <a href="https://t.me/dentistryonly0" target="_blank" style="background:#0088cc; color:#fff; padding:10px 20px; border-radius:30px; text-decoration:none;">
            🔗 تابع قناة التلي لمتابعة التحديثات
        </a>
    </div>
    """, unsafe_allow_html=True)
