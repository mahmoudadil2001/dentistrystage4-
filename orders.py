import streamlit as st
import os
import importlib.util
import re
from login import save_selected_versions  # لاستعمال الدالة التي تحفظ النسخ في Google Sheet

custom_titles_data = {
    ("endodontics", 1): "Lecture 1 introduction",
    ("endodontics", 2): "Lecture 2 periapical disease classification",
    ("generalmedicine", 1): "Lecture 1 name",
    ("oralpathology", 1): "Lec 1 Biopsy"
}

custom_titles = {}
for (subject, num), title in custom_titles_data.items():
    custom_titles.setdefault(subject, {})[num] = title

def get_lectures_and_versions(subject_name, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    if not os.path.exists(subject_path):
        return {}

    files = os.listdir(subject_path)
    pattern = re.compile(rf"^{re.escape(subject_name)}(\d+)(?:_v(\d+))?\.py$", re.IGNORECASE)

    lectures = {}
    for f in files:
        m = pattern.match(f)
        if m:
            lec_num = int(m.group(1))
            version_num = int(m.group(2)) if m.group(2) else 1
            if lec_num not in lectures:
                lectures[lec_num] = {}
            lectures[lec_num][version_num] = f

    for lec in lectures:
        lectures[lec] = dict(sorted(lectures[lec].items()))
    return lectures

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

    lectures_list = []
    for lec_num in sorted(lectures_versions.keys()):
        if subject in custom_titles and lec_num in custom_titles[subject]:
            lectures_list.append(f"{lec_num} - {custom_titles[subject][lec_num]}")
        else:
            lectures_list.append(f"{lec_num} - Lecture {lec_num}")

    lecture_choice = st.selectbox("Select Lecture", lectures_list)
    lec_num = int(lecture_choice.split(" ")[0])
    versions_dict = lectures_versions.get(lec_num, {})

    selected_version = 1
    if len(versions_dict) > 1:
        version_keys = sorted(versions_dict.keys())
        selected_version = st.radio(
            "اختر النسخة:",
            options=version_keys,
            index=0,
            key="version_select"
        )

        # ✅ حفظ النسخة المختارة في حساب المستخدم
        if st.session_state.get("logged_in"):
            username = st.session_state.get("user_name")
            if st.checkbox("حفظ هذه النسخة لهذا الحساب", key=f"save_{subject}_{lec_num}_{selected_version}"):
                version_text = f"{subject}:{lec_num}:{selected_version}"
                save_selected_versions(username, version_text)
                st.success("✅ تم حفظ النسخة في حسابك")

    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture") != lecture_choice) or \
       (st.session_state.get("current_subject") != subject) or \
       (st.session_state.get("current_version") != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lecture_choice
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
            status = "⬜" if user_ans is None else "✅" if user_ans == correct_text else "❌"
            if st.button(f"{status} Question {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

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
            st.session_state.user_answers[i] == normalize_answer(q) for i, q in enumerate(questions)
        )
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
        <div style="background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        border-radius: 15px; padding: 20px; color: #003049; font-size: 18px; text-align: center;">
        Hello students! This content is for fourth-year dental students at Al-Esraa University. 
        Select a subject and lecture and start the quiz. Good luck!
        </div>
        """,
        unsafe_allow_html=True
    )
    orders_o()
