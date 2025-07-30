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
        st.error("⚠️ لا توجد نسخ متاحة لهذه المحاضرة.")
        return

    if "selected_version" not in st.session_state or st.session_state.get("selected_version") not in versions_dict:
        st.session_state.selected_version = versions_keys[0]

    selected_version = st.selectbox(
        "Select Version",
        options=versions_keys,
        index=versions_keys.index(st.session_state.selected_version)
    )
    st.session_state.selected_version = selected_version

    file_path = os.path.join(subject, versions_dict[selected_version])
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ File {versions_dict[selected_version]} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    # تهيئة متغيرات الجلسة المهمة
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "user_answers" not in st.session_state or len(st.session_state.user_answers) != len(questions):
        st.session_state.user_answers = [None] * len(questions)
    if "answer_shown" not in st.session_state or len(st.session_state.answer_shown) != len(questions):
        st.session_state.answer_shown = [False] * len(questions)
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False
    if "in_quiz_mode" not in st.session_state:
        st.session_state.in_quiz_mode = False

    # زر الدخول والخروج من وضع الاختبار (منتصف الصفحة تقريباً)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.in_quiz_mode:
            if st.button("▶️ الدخول في وضع الاختبار"):
                # تعيين المتغيرات قبل الدخول لو لم تكن موجودة
                st.session_state.current_subject = subject
                st.session_state.current_lecture = lec_num
                st.session_state.current_version = selected_version
                st.session_state.in_quiz_mode = True
                st.rerun()
        else:
            if st.button("⬅️ خروج من وضع الاختبار"):
                st.session_state.in_quiz_mode = False
                st.rerun()

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

    # هنا نقرر ماذا نعرض بناءً على وضع الاختبار
    if st.session_state.in_quiz_mode:
        # نتحقق من المتغيرات المهمة أولاً
        if (
            "current_subject" not in st.session_state
            or "current_lecture" not in st.session_state
            or "current_version" not in st.session_state
        ):
            st.error("⚠️ البيانات غير مكتملة لدخول وضع الاختبار. الرجاء الخروج واختيار المادة والمحاضرة أولًا.")
            if st.button("⬅️ خروج من وضع الاختبار"):
                st.session_state.in_quiz_mode = False
                st.rerun()
            return

        # إظهار السؤال مع خياراته فقط بدون أي إضافات
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

    else:
        # الوضع الطبيعي: عرض كل شيء - الشريط الجانبي، العنوان، الشرح، أسئلة قابلة للتصفح
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

        # عرض السؤال والشرح المعتاد
        q = questions[st.session_state.current_question]

        st.markdown(f"### Question {st.session_state.current_question + 1}/{len(questions)}: {q['question']}")

        default_idx = 0
        if st.session_state.user_answers[st.session_state.current_question] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[st.session_state.current_question])

        selected_answer = st.radio(
            "",
            q["options"],
            index=default_idx,
            key=f"radio_{st.session_state.current_question}"
        )

        if not st.session_state.answer_shown[st.session_state.current_question]:
            if st.button("Answer", key=f"submit_{st.session_state.current_question}"):
                st.session_state.user_answers[st.session_state.current_question] = selected_answer
                st.session_state.answer_shown[st.session_state.current_question] = True
                st.rerun()
        else:
            user_ans = st.session_state.user_answers[st.session_state.current_question]
            correct_text = normalize_answer(q)
            if user_ans == correct_text:
                st.success("✅ Correct answer")
            else:
                st.error(f"❌ Correct answer: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 Explanation: {q['explanation']}")

            if st.button("Next Question", key=f"next_{st.session_state.current_question}"):
                if st.session_state.current_question + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()

        if Links:
            st.markdown("---")
            for link in Links:
                st.markdown(f"- [{link['title']}]({link['url']})")


def main():
    orders_o()


if __name__ == "__main__":
    main()
