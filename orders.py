import streamlit as st
import os
import importlib.util
import requests
import json

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwzHw6kXDxTx_hdJLGUDHON5DpKdoAd0azzvah-w5MggiDhV7XnFkyxPDvyPl6p60T3/exec"

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


def count_lectures(subject_name, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    if not os.path.exists(subject_path):
        return 0
    files = [f for f in os.listdir(subject_path) if f.startswith(subject_name) and f.endswith(".py")]
    return len(files)


def find_versions(subject_name, lecture_num, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    versions = []
    for f in os.listdir(subject_path):
        if f.startswith(f"{subject_name}{lecture_num}") and f.endswith(".py"):
            if "_v" in f:
                versions.append(f.split("_v")[-1].replace(".py", ""))
            else:
                versions.append("1")
    versions = sorted(versions, key=lambda x: int(x) if x.isdigit() else 999)
    return versions


def import_module(subject_name, lecture_num, version=None, base_path="."):
    subject_path = os.path.join(base_path, subject_name)
    filename = f"{subject_name}{lecture_num}.py" if version in [None, "1"] else f"{subject_name}{lecture_num}_v{version}.py"
    module_file = os.path.join(subject_path, filename)

    if not os.path.exists(module_file):
        return None

    spec = importlib.util.spec_from_file_location(f"{subject_name}{lecture_num}_v{version}", module_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_progress(username, subject, lecture_num):
    try:
        res = requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "get_progress",
            "username": username,
            "subject": subject,
            "lecture_num": lecture_num
        }, timeout=30)
        if res.status_code == 200:
            return json.loads(res.text)
    except:
        return []
    return []


def set_progress(username, subject, lecture_num, version, completed):
    try:
        requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "set_progress",
            "username": username,
            "subject": subject,
            "lecture_num": lecture_num,
            "version": version,
            "completed": str(completed).lower()
        }, timeout=30)
    except:
        pass


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

    subject = st.selectbox("Choose Subject", subjects)

    total_lectures = count_lectures(subject)
    if total_lectures == 0:
        st.error(f"No lecture files found for {subject}")
        return

    lectures = []
    for i in range(1, total_lectures + 1):
        if subject in custom_titles and i in custom_titles[subject]:
            lectures.append(custom_titles[subject][i])
        else:
            lectures.append(f"Lecture {i}")

    lecture = st.selectbox("Choose Lecture", lectures)

    try:
        lecture_num = int(lecture.split()[1])
    except:
        st.error("Error reading lecture number.")
        return

    versions = find_versions(subject, lecture_num)

    selected_version = "1"
    if len(versions) > 1:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### Available Versions")
            progress_data = get_progress(st.session_state['user_name'], subject, lecture_num)

            for v in versions:
                checked = any(d["version"] == v and str(d["completed"]).lower() == "true" for d in progress_data)
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    if st.button(f"Version {v}", key=f"ver_btn_{v}"):
                        selected_version = v
                        st.session_state["selected_version"] = v
                        st.rerun()
                with col2:
                    new_state = st.checkbox("✔", value=checked, key=f"chk_{v}")
                    if new_state != checked:
                        set_progress(st.session_state['user_name'], subject, lecture_num, v, new_state)
            if "selected_version" in st.session_state:
                selected_version = st.session_state["selected_version"]
    else:
        selected_version = "1"

    questions_module = import_module(subject, lecture_num, selected_version)
    if questions_module is None:
        st.error(f"File for {subject} lecture {lecture_num} version {selected_version} not found.")
        return

    questions = questions_module.questions
    Links = getattr(questions_module, "Links", [])

    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lecture) or \
       (st.session_state.get("current_subject", None) != subject) or \
       (st.session_state.get("current_version", None) != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lecture
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
        st.markdown(f"### {subject.upper()}")
        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} Q{i+1}", key=f"nav_{i}"):
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

        selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")

        if not st.session_state.answer_shown[index]:
            if st.button("Submit", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            if st.session_state.user_answers[index] == correct_text:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Correct Answer: {correct_text}")
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
        st.success(f"Result: {correct} / {len(questions)}")

        if st.button("🔁 Retry Quiz"):
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
        Welcome! Choose a subject and lecture to start the quiz.
        </div>
        """,
        unsafe_allow_html=True,
    )
    orders_o()
