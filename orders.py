import streamlit as st
import os
import importlib.util
import sys
import importlib
from versions_manager import get_lectures_and_versions
from exam_mode import exam_mode_ui


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
    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
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
        display_name = f"Lec {lec_num} {title}" if title else f"Lec {lec_num}"
        lectures_options.append((lec_num, display_name))

    lec_num = st.selectbox("Select Lecture", options=lectures_options, format_func=lambda x: x[1])[0]
    versions_dict = lectures_versions.get(lec_num, {})
    versions_keys = sorted(versions_dict.keys())

    if not versions_keys:
        st.error("⚠️ لا توجد نسخ متاحة لهذه المحاضرة.")
        return

    selected_version = st.selectbox("Select Version", options=versions_keys)
    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    if "exam_mode" not in st.session_state:
        st.session_state.exam_mode = False

    if st.button("🎯 دخول وضع الاختبار"):
        st.session_state.exam_mode = True
        st.experimental_rerun()

    # ✅ إذا كان وضع الاختبار مفعّل → نخفي كل شيء ونستدعي exam_mode_ui فقط
    if st.session_state.exam_mode:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"], 
            [data-testid="stHeader"] {display: none;}
            </style>
            """, unsafe_allow_html=True
        )
        exam_mode_ui(questions, Links)
        return

   def show_question(index):
    q = questions[index]
    correct_text = normalize_answer(q)

    st.markdown(f"### Question {index+1}/{len(questions)}: {q['question']}")

    default_idx = 0
    if st.session_state.user_answers[index] in q["options"]:
        default_idx = q["options"].index(st.session_state.user_answers[index])

    selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")

    if not st.session_state.answer_shown[index]:
        if st.button("Answer", key=f"submit_{index}"):
            st.session_state.user_answers[index] = selected_answer
            st.session_state.answer_shown[index] = True
            st.experimental_rerun()
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
            st.experimental_rerun()

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
        st.experimental_rerun()


def main():
    # ✅ إخفاء صندوق التعليمات إذا كنا في وضع الاختبار
    if "exam_mode" not in st.session_state or not st.session_state.exam_mode:
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
            Hello students! This content is for fourth-year dental students at Al-Esraa University. 
            Select a subject and lecture and start the quiz. Good luck!
            </div>
            """,
            unsafe_allow_html=True
        )

    orders_o()


if __name__ == "__main__":
    main()
