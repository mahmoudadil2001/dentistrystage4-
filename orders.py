import streamlit as st
import os
import importlib.util
import sys
import importlib
from versions_manager import get_lectures_and_versions


def load_lecture_titles(subject_name):
    titles_file = os.path.join(subject_name, "edit", "lecture_titles.py")
    if not os.path.exists(titles_file):
        return {}

    module_name = f"{subject_name}_titles"

    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, titles_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, "lecture_titles", {})


def import_module_from_file(filepath):
    if not os.path.exists(filepath):
        return None
    spec = importlib.util.spec_from_file_location(os.path.basename(filepath).replace(".py", ""), filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def orders_o():
    # تهيئة المتغيرات في الجلسة
    if "quiz_mode" not in st.session_state:
        st.session_state.quiz_mode = False
    if "selected_subject" not in st.session_state:
        st.session_state.selected_subject = "endodontics"
    if "selected_lecture" not in st.session_state:
        st.session_state.selected_lecture = None
    if "selected_version" not in st.session_state:
        st.session_state.selected_version = 1

    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative", "oralpathology",
        "oralsurgery", "orthodontics", "pedodontics", "periodontology", "prosthodontics"
    ]

    # زر الدخول/الخروج من وضع الاختبار دائماً فوق الصناديق
    if st.button("Enter Quiz Mode" if not st.session_state.quiz_mode else "Exit Quiz Mode"):
        st.session_state.quiz_mode = not st.session_state.quiz_mode
        if st.session_state.quiz_mode:
            st.session_state.current_subject = st.session_state.selected_subject
            st.session_state.current_lecture = st.session_state.selected_lecture
            st.session_state.current_version = st.session_state.selected_version
        st.rerun()

    # نص أحمر يظهر فوق الزر في وضع الاختبار
    if st.session_state.quiz_mode:
        subject = st.session_state.current_subject
        lec_num = st.session_state.current_lecture
        selected_version = st.session_state.current_version

        lecture_titles = load_lecture_titles(subject)
        title = lecture_titles.get(lec_num, "").strip()
        display_title = f"{subject} lec{lec_num} {title} (v{selected_version})".strip()
        st.markdown(f"<p style='color:red;font-size:13px;font-weight:bold;margin-top:-15px;margin-bottom:10px'>{display_title}</p>", unsafe_allow_html=True)

    # إذا لم يكن في وضع الاختبار نعرض رسالة ترحيب زرقاء وصناديق الاختيار
    if not st.session_state.quiz_mode:
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
            """,
            unsafe_allow_html=True,
        )

        subject = st.selectbox("Select Subject", subjects, index=subjects.index(st.session_state.selected_subject))
        st.session_state.selected_subject = subject

        lectures_versions = get_lectures_and_versions(subject)
        if not lectures_versions:
            st.error(f"⚠️ No lecture files found for subject {subject}!")
            return

        lecture_titles = load_lecture_titles(subject)
        lectures_options = []
        for lec_num in sorted(lectures_versions.keys()):
            title = lecture_titles.get(lec_num, "").strip()
            display_name = f"Lec {lec_num}  {title}" if title else f"Lec {lec_num}"
            lectures_options.append((lec_num, display_name))

        if st.session_state.selected_lecture in [lec[0] for lec in lectures_options]:
            default_idx = [lec[0] for lec in lectures_options].index(st.session_state.selected_lecture)
        else:
            default_idx = 0

        lec_num = st.selectbox("Select Lecture", options=lectures_options, index=default_idx, format_func=lambda x: x[1])[0]
        st.session_state.selected_lecture = lec_num

        versions_dict = lectures_versions.get(lec_num, {})
        versions_keys = sorted(versions_dict.keys())
        if st.session_state.selected_version not in versions_keys:
            st.session_state.selected_version = versions_keys[0]

        selected_version = st.selectbox("Select Version", options=versions_keys, index=versions_keys.index(st.session_state.selected_version))
        st.session_state.selected_version = selected_version

    else:
        subject = st.session_state.current_subject
        lec_num = st.session_state.current_lecture
        selected_version = st.session_state.current_version

    lectures_versions = get_lectures_and_versions(subject)
    versions_dict = lectures_versions.get(lec_num, {})
    filename = versions_dict.get(selected_version, None)
    if not filename:
        st.error("⚠️ الملف الخاص بالمحاضرة غير موجود.")
        return

    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)
    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    # تهيئة الحالة عند تغير المادة أو المحاضرة
    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture") != lec_num) or \
       (st.session_state.get("current_subject") != subject) or \
       (st.session_state.get("current_version") != selected_version):

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
            ac = answer.strip().upper()
            if ac in ["A", "B", "C", "D"]:
                idx = ord(ac) - ord("A")
                return options[idx] if 0 <= idx < len(options) else None
            if answer in options:
                return answer
        return None

    # شريط التنقل في الشريط الجانبي
    with st.sidebar:
        st.markdown(f"### 🧪 {subject.upper()}")
        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            status = "⬜" if user_ans is None else ("✅" if user_ans == correct_text else "❌")
            if st.button(f"{status} Q{i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)

        st.markdown(
            f"<div style='margin-top:-5px;margin-bottom:3px;font-size:17px;font-weight:bold;'>Q{index+1}/{len(questions)}: {q['question']}</div>",
            unsafe_allow_html=True
        )

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio(
            "", q["options"], index=default_idx, key=f"radio_{index}", label_visibility="collapsed"
        )

        if not st.session_state.answer_shown[index]:
            if st.button("Answer", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            if st.session_state.user_answers[index] == correct_text:
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
        correct = sum(
            1 for i, q in enumerate(questions)
            if st.session_state.user_answers[i] == normalize_answer(q)
        )
        st.success(f"Score: {correct} / {len(questions)}")
        if st.button("🔁 Restart Quiz"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()


def main():
    orders_o()


if __name__ == "__main__":
    main()
