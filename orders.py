import streamlit as st
import os
import importlib.util
import sys
import importlib

from versions_manager import get_lectures_and_versions, select_version_ui

def load_lecture_titles(subject_name):
    titles_file = os.path.join(subject_name, "edit", "lecture_titles.py")
    if not os.path.exists(titles_file):
        return {}

    spec = importlib.util.spec_from_file_location(f"{subject_name}_titles", titles_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if f"{subject_name}_titles" in sys.modules:
        importlib.reload(sys.modules[f"{subject_name}_titles"])

    return getattr(module, "lecture_titles", {})

def import_module_from_file(filepath):
    if not os.path.exists(filepath):
        return None
    spec = importlib.util.spec_from_file_location(os.path.basename(filepath).replace(".py", ""), filepath)
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

    subject = st.selectbox("Select Subject", subjects)

    lectures_versions = get_lectures_and_versions(subject)
    if not lectures_versions:
        st.error(f"⚠️ No lecture files found for subject {subject}!")
        return

    # تحميل عناوين المحاضرات
    lecture_titles = load_lecture_titles(subject)

    lectures_options = []
    for lec_num in sorted(lectures_versions.keys()):
        title = lecture_titles.get(lec_num, None)
        if title:
            display_name = f"Lec {lec_num} - {title}"
        else:
            display_name = f"Lec {lec_num} - (بدون عنوان)"
        lectures_options.append((lec_num, display_name))

    lec_num = st.selectbox(
        "Select Lecture",
        options=lectures_options,
        format_func=lambda x: x[1]
    )[0]

    # اختيار نسخة الأسئلة إذا كانت موجودة
    versions_dict = lectures_versions.get(lec_num, {})

    selected_version = select_version_ui(versions_dict)

    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    # تهيئة حالة الأسئلة في الجلسة
    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lec_num) or \
       (st.session_state.get("current_subject", None) != subject) or \
       (st.session_state.get("current_version", None) != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lec_num
        st.session_state.current_subject = subject
        st.session_state.current_version = selected_version

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
        st.markdown(f"### Question {current_q_num}/{total_qs}: {q['question']}")

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
            if st.button("Answer", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            user_ans = st.session_state.user_answers[index]
            if user_ans == correct_text:
                st.success("✅ Correct answer")
            else:
                st.error(f"❌ Correct answer: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 Explanation: {q['explanation']}")

            if st.button("Next Question", key=f"next_{index}"):
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
        st.header("🎉 Quiz Completed!")
        correct = 0
        for i, q in enumerate(questions):
            correct_text = normalize_answer(q)
            user = st.session_state.user_answers[i]
            if user == correct_text:
                correct += 1
                st.write(f"Question {i+1}: ✅ Correct")
            else:
                st.write(f"Question {i+1}: ❌ Wrong (Your answer: {user}, Correct: {correct_text})")
        st.success(f"Score: {correct} out of {len(questions)}")

        if st.button("🔁 Restart Quiz"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()

def main():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            border-radius: 15px;
            padding: 20px;
            color: #003049;
            font-family: 'Tajawal', sans-serif;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
        ">
        Hello students! This content is for fourth-year dental students at Al-Esraa University. Select a subject and lecture and start the quiz. Good luck!
        </div>
        """
    , unsafe_allow_html=True)
    orders_o()

    st.markdown('''
    <div style="display:flex; justify-content:center; margin-top:50px;">
        <a href="https://t.me/dentistryonly0" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">
            Telegram Channel
            <span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;">
                <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;">
                    <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.2 3.2-6.5 3.2l2.3-33.3 60.6-54.7c2.6-2.3-0.6-3.5-4-2.2L93.5 123.7 56.7 104.9c-6.1-1.9-6.2-6.1 1.3-9l90-34.7c4.1-1.5 7.7 1 6.7 8.4z"/>
                </svg>
            </span>
        </a>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
