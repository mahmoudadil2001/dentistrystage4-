import streamlit as st
import os
import importlib.util

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

    # تعيين "Lecture 1 name" لجميع المواد
    lecture_titles = {subject: {1: "Lecture 1 name"} for subject in subjects}

    subject = st.selectbox("اختر المادة", subjects)

    total_lectures = count_lectures(subject)
    if total_lectures == 0:
        st.error(f"⚠️ لا يوجد ملفات محاضرات للمادة {subject}!")
        return

    lectures = []
    for i in range(1, total_lectures + 1):
        if subject in lecture_titles and i in lecture_titles[subject]:
            lectures.append(lecture_titles[subject][i])
        else:
            lectures.append(f"Lecture {i}")

    lecture = st.selectbox("اختر المحاضرة", lectures)

    lecture_num = int(lecture.split()[1])
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
                st.error(f"❌ الإجابة الصحيحة: {correct_text}")

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
