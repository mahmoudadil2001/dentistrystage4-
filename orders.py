import streamlit as st
import os
import importlib.util
import re

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
            lectures.setdefault(lec_num, {})[version_num] = f

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
    if "completed_versions" not in st.session_state:
        st.session_state.completed_versions = {}

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

    lectures_list = []
    for lec_num in sorted(lectures_versions.keys()):
        title = custom_titles.get(subject, {}).get(lec_num, f"Lecture {lec_num}")
        lectures_list.append(f"{lec_num} - {title}")

    lecture_choice = st.selectbox("Select Lecture", lectures_list)
    lec_num = int(lecture_choice.split(" ")[0])
    versions_dict = lectures_versions.get(lec_num, {})
    version_keys = sorted(versions_dict.keys())

    # تحديث نسخة + علامة صح
    def build_labels():
        labels = []
        for v in version_keys:
            key = f"{subject}_{lec_num}_{v}"
            mark = "✅" if st.session_state.completed_versions.get(key, False) else ""
            labels.append(f"Version {v} {mark}")
        return labels

    version_labels = build_labels()

    with st.sidebar:
        st.markdown("### اختر النسخة")
        selected_label = st.radio("", options=version_labels, index=0, key="version_radio")
        selected_version = version_keys[version_labels.index(selected_label)]

        key = f"{subject}_{lec_num}_{selected_version}"
        if key not in st.session_state:
            st.session_state[key] = False

        clicked = st.checkbox("", value=st.session_state[key], key=f"chk_{key}_ui")

        if clicked != st.session_state[key]:
            st.session_state[key] = clicked
            st.session_state.completed_versions[key] = clicked
            st.session_state.version_labels = build_labels()
            st.rerun()

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
        """, unsafe_allow_html=True)
    orders_o()

if __name__ == "__main__":
    main()
