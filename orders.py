import streamlit as st
import os
import importlib.util
import sys
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

    # إذا كان وضع الاختبار مفعّل → نخفي الشريط الجانبي والهيدر ونعرض فقط الامتحان
    if st.session_state.exam_mode:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"], 
            [data-testid="stHeader"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        exam_mode_ui(questions, Links)
        return

    # تهيئة حالة الأسئلة إذا لم تكن موجودة أو تغيرت المحاضرة أو النسخة
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

    # عرض الشريط الجانبي مع أزرار التنقل وحالة الإجابات
    with st.sidebar:
        st.markdown(f"### 🧪 {subject.upper()}")
        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i] if "user_answers" in st.session_state else None
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} سؤال {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)

        st.markdown(f"### سؤال {index+1} / {len(questions)}: {q['question']}")

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")

        if not st.session_state.answer_shown[index]:
            if st.button("إظهار الإجابة", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.experimental_rerun()
        else:
            if st.session_state.user_answers[index] == correct_text:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ الإجابة الصحيحة: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 شرح: {q['explanation']}")

            if st.button("السؤال التالي", key=f"next_{index}"):
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
        st.header("🎉 انتهى الاختبار!")
        correct = 0
        for i, q in enumerate(questions):
            correct_text = normalize_answer(q)
            user = st.session_state.user_answers[i]
            if user == correct_text:
                correct += 1
                st.write(f"السؤال {i+1}: ✅ صحيح")
            else:
                st.write(f"السؤال {i+1}: ❌ خطأ (إجابتك: {user}, الإجابة الصحيحة: {correct_text})")
        st.success(f"النتيجة: {correct} من أصل {len(questions)}")

        if st.button("🔁 إعادة الاختبار"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.experimental_rerun()
