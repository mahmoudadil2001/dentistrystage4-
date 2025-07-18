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
    ("generalmedicine", 1): "Lecture 1 name"
}

# تحويلها إلى شكل القاموس المستخدم في الكود
custom_titles = {}
for (subject, num), title in custom_titles_data.items():
    custom_titles.setdefault(subject, {})[num] = title

def count_lectures(subject_name, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    if not os.path.exists(subject_path):
        return 0
    files = [f for f in os.listdir(subject_path) if f.startswith(subject_name) and f.endswith(".py")]
    return len(files)

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
        "endodontics",
        "generalmedicine",
        "generalsurgery",
        "operative",
        "oralpathology",
        "oralsurgery",
        "orthodontics",
        "pedodontics",
        "periodontology",
        "prosthodontics"
    ]

    subject = st.selectbox("اختر المادة", subjects)

    total_lectures = count_lectures(subject)
    if total_lectures == 0:
        st.error(f"⚠️ لا يوجد ملفات محاضرات للمادة {subject}!")
        return

    lectures = []
    for i in range(1, total_lectures + 1):
        if subject in custom_titles and i in custom_titles[subject]:
            lectures.append(custom_titles[subject][i])
        else:
            lectures.append(f"Lecture {i}")

    lecture = st.selectbox("اختر المحاضرة", lectures)

    try:
        lecture_num = int(lecture.split()[1])
    except:
        st.error("⚠️ حدث خطأ في قراءة رقم المحاضرة.")
        return

    questions_module = import_module_from_folder(subject, lecture_num)
    if questions_module is None:
        st.error(f"⚠️ الملف {subject}{lecture_num}.py غير موجود في المجلد {subject}.")
        return

    questions = questions_module.questions

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
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} Question {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)

        current_q_num = index + 1
        total_qs = len(questions)
        st.markdown(f"### Q{current_q_num}/{total_qs}: {q['question']}")

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio(
            "",
            q["options"],
            index=default_idx,
            key=f"radio_{index}"
        )

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
                st.error(f"❌ الإجابة : {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 الشرح: {q['explanation']}")

            if st.button("السؤال التالي", key=f"next_{index}"):
                if index + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question)
    else:
        st.header("🎉 تم الانتهاء من الاختبار!")
        correct = 0
        for i, q in enumerate(questions):
            correct_text = normalize_answer(q)
            user = st.session_state.user_answers[i]
            if user == correct_text:
                correct += 1
                st.write(f"Q{i+1}: ✅ صحيحة")
            else:
                st.write(f"Q{i+1}: ❌ خاطئة (إجابتك: {user}, الصحيحة: {correct_text})")
        st.success(f"النتيجة: {correct} من {len(questions)}")

        if st.button("🔁 أعد الاختبار"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()

# --- الكود الخاص بتسجيل الاسم وتشغيل الموقع ---
def main():
    # 🛡️ التأكد من أن المستخدم سجل اسمه قبل تشغيل باقي الموقع
  if "user_logged" not in st.session_state:
    st.markdown("""
        <style>
        body {
            background-color: #f8f9fa;
        }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
            font-family: 'Arial', sans-serif;
        }
        .login-box h2 {
            margin-bottom: 20px;
            color: #2c3e50;
        }
        .login-box input {
            width: 90%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 16px;
        }
        .login-box button {
            width: 95%;
            padding: 10px;
            background-color: #4CAF50;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 18px;
            margin-top: 15px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .login-box button:hover {
            background-color: #45a049;
        }
        </style>

        <div class="login-container">
            <div class="login-box">
                <h2>📚 أهلاً بك في منصة طب الأسنان</h2>
                <p>يرجى إدخال اسمك وكروبك للمتابعة</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # نضع الحقول هنا تحت التصميم
    name = st.text_input("✍️ اسمك؟", key="html_name")
    group = st.text_input("👥 كروبك؟", key="html_group")

    if st.button("✅ دخول"):
        if name.strip() == "" or group.strip() == "":
            st.warning("يرجى ملء جميع الحقول.")
        else:
            send_to_telegram(name, group)
            st.session_state.user_logged = True
            st.session_state.visitor_name = name
            st.session_state.visitor_group = group
            st.rerun()

    st.stop()

    # ✅ بعد تسجيل الاسم، نعرض ترحيب
    st.markdown(f"### 👋 أهلاً {st.session_state.visitor_name}")

    # ✅ الآن فقط بعد تسجيل الاسم، شغل التطبيق الأساسي
    orders_o()

    # 🔵 زر قناة التلي + جملة تحت الزر
    st.markdown('''
    <div style="display:flex; justify-content:center; margin-top:50px;">
        <a href="https://t.me/dentistryonly0" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">
            قناة التلي
            <span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;">
                <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;">
                    <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/>
                </svg>
            </span>
        </a>
    </div>

    <div style="text-align:center; margin-top:15px; font-size:16px; color:#444;">
        اشتركوا بقناة التلي حتى توصلكم كل التحديثات أو المحاضرات اللي راح انزلها على الموقع إن شاء الله
    </div>
    ''', unsafe_allow_html=True)
