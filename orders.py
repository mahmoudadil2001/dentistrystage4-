import streamlit as st
import os
import importlib.util
import requests
import json

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwzHw6kXDxTx_hdJLGUDHON5DpKdoAd0azzvah-w5MggiDhV7XnFkyxPDvyPl6p60T3/exec"

# ✅ عناوين المحاضرات المخصصة
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


def get_versions(subject_name, lecture_num, base_path="."):
    """🔹 يجلب كل النسخ المتاحة للمحاضرة"""
    subject_path = os.path.join(base_path, subject_name)
    versions = []
    if not os.path.exists(subject_path):
        return versions

    for f in os.listdir(subject_path):
        if f.startswith(f"{subject_name}{lecture_num}") and f.endswith(".py"):
            parts = f.replace(".py", "").split("_v")
            if len(parts) == 2:
                versions.append(int(parts[1]))
            elif len(parts) == 1:
                versions.append(1)

    versions.sort()
    return versions


def import_module(subject_name, lecture_num, version=None, base_path="."):
    """🔹 استيراد ملف المحاضرة بناءً على النسخة"""
    subject_path = os.path.join(base_path, subject_name)
    if version and version > 1:
        module_file = os.path.join(subject_path, f"{subject_name}{lecture_num}_v{version}.py")
    else:
        module_file = os.path.join(subject_path, f"{subject_name}{lecture_num}.py")

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
        return json.loads(res.text)
    except:
        return []


def set_progress(username, subject, lecture_num, version, completed):
    try:
        requests.post(GOOGLE_SCRIPT_URL, data={
            "action": "set_progress",
            "username": username,
            "subject": subject,
            "lecture_num": lecture_num,
            "version": version,
            "completed": str(completed)
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

    subject = st.selectbox("Select Subject", subjects)

    total_lectures = count_lectures(subject)
    if total_lectures == 0:
        st.error(f"No lectures found for {subject}")
        return

    lectures = []
    for i in range(1, total_lectures + 1):
        if subject in custom_titles and i in custom_titles[subject]:
            lectures.append(custom_titles[subject][i])
        else:
            lectures.append(f"Lecture {i}")

    lecture = st.selectbox("Select Lecture", lectures)

    try:
        lecture_num = int(lecture.split()[1])
    except:
        st.error("Error reading lecture number")
        return

    versions = get_versions(subject, lecture_num)

    # ✅ تحميل تقدم المستخدم
    username = st.session_state.get("user_name", "")
    progress_data = get_progress(username, subject, lecture_num)
    completed_versions = {int(d["version"]): d["completed"] == "True" for d in progress_data}

    if len(versions) > 1:
        st.sidebar.markdown("### Available Versions")
        for v in versions:
            checked = completed_versions.get(v, False)
            new_state = st.sidebar.checkbox(f"Version {v}", value=checked, key=f"chk_{v}")
            if new_state != checked:
                set_progress(username, subject, lecture_num, v, new_state)
                completed_versions[v] = new_state
    else:
        # نسخة واحدة فقط
        v = 1
        checked = completed_versions.get(v, False)
        new_state = st.sidebar.checkbox("Completed", value=checked, key=f"chk_{v}")
        if new_state != checked:
            set_progress(username, subject, lecture_num, v, new_state)
            completed_versions[v] = new_state

    current_version = versions[0]
    questions_module = import_module(subject, lecture_num, current_version)
    if questions_module is None:
        st.error("Lecture file not found")
        return

    questions = questions_module.questions
    Links = getattr(questions_module, "Links", [])

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

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)
        st.markdown(f"### Q{index+1}/{len(questions)}: {q['question']}")

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
                st.success("✅ Correct")
            else:
                st.error(f"❌ Correct Answer: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 {q['explanation']}")

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
        st.success(f"Quiz Completed! Score: {sum(st.session_state.user_answers[i] == normalize_answer(q) for i,q in enumerate(questions))}/{len(questions)}")
        if st.button("🔁 Retry Quiz"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()


def main():
    st.title("Dental Quiz Platform")
    orders_o()
