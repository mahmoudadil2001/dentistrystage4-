import streamlit as st
import os
import importlib.util
import sys

from versions_manager import get_lectures_and_versions


def load_lecture_titles(subject_name):
    import os
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
    if "in_quiz_mode" not in st.session_state:
        st.session_state.in_quiz_mode = False

    if not st.session_state.in_quiz_mode:
        # الوضع العادي: عرض كل عناصر اختيار المادة، المحاضرة، النسخة، وزر بدء الاختبار

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

        lecture_titles = load_lecture_titles(subject)

        lectures_options = []
        for lec_num in sorted(lectures_versions.keys()):
            title = lecture_titles.get(lec_num, "").strip()
            display_name = f"Lec {lec_num}  {title}" if title else f"Lec {lec_num}"
            lectures_options.append((lec_num, display_name))

        lec_num = st.selectbox("Select Lecture", options=lectures_options, format_func=lambda x: x[1])[0]

        versions_dict = lectures_versions.get(lec_num, {})
        versions_keys = sorted(versions_dict.keys())
        if not versions_keys:
            st.error("⚠️ No versions available for this lecture.")
            return

        if "selected_version" not in st.session_state or st.session_state.get("selected_version") not in versions_dict:
            st.session_state.selected_version = versions_keys[0]

        selected_version = st.selectbox(
            "Select Version",
            options=versions_keys,
            index=versions_keys.index(st.session_state.selected_version)
        )
        st.session_state.selected_version = selected_version

        # زر الدخول في وضع الاختبار مركزي
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("▶️ الدخول في وضع الاختبار"):
                st.session_state.in_quiz_mode = True
                st.session_state.current_question = 0
                file_path = os.path.join(subject, versions_dict[selected_version])
                questions_module = import_module_from_file(file_path)
                questions = getattr(questions_module, "questions", [])
                st.session_state.user_answers = [None] * len(questions)
                st.session_state.answer_shown = [False] * len(questions)
                st.session_state.quiz_completed = False
                st.session_state.current_subject = subject
                st.session_state.current_lecture = lec_num
                st.session_state.current_version = selected_version
                st.rerun()

        # عرض الشرح أو محتوى المحاضرة هنا لو تحب (ضع الكود هنا)
        # مثلاً يمكنك إضافة وصف أو نص محاضرة من ملف أو ثابت

    else:
        # وضع الاختبار: صفحة نظيفة جداً، فقط سؤال واحد وأزرار، لا شريط جانبي ولا ترحيب

        subject = st.session_state.current_subject
        lec_num = st.session_state.current_lecture
        selected_version = st.session_state.current_version
        versions_dict = get_lectures_and_versions(subject).get(lec_num, {})
        file_path = os.path.join(subject, versions_dict[selected_version])
        questions_module = import_module_from_file(file_path)

        if questions_module is None:
            st.error(f"⚠️ File {versions_dict[selected_version]} not found or cannot be imported.")
            return

        questions = getattr(questions_module, "questions", [])

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
                key=f"radio_quiz_{index}"
            )

            if not st.session_state.answer_shown[index]:
                if st.button("Answer", key=f"submit_quiz_{index}"):
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

                if st.button("Next Question", key=f"next_quiz_{index}"):
                    if index + 1 < len(questions):
                        st.session_state.current_question += 1
                        st.session_state.answer_shown[st.session_state.current_question] = False
                    else:
                        st.session_state.quiz_completed = True
                    st.rerun()

        # زر خروج من وضع الاختبار مركزي فوق
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️ خروج من وضع الاختبار"):
                st.session_state.in_quiz_mode = False
                st.rerun()

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

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⬅️ خروج من وضع الاختبار"):
                    st.session_state.in_quiz_mode = False
                    st.rerun()


def main():
    orders_o()


if __name__ == "__main__":
    main()
