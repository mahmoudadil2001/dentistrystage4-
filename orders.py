import streamlit as st
import os
from login import get_lectures_and_versions, import_module_from_file

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
    versions_count = len(versions_dict)

    selected_version = 1
    if versions_count > 1:
        st.sidebar.markdown("### Select Question version")
        version_keys = sorted(versions_dict.keys())
        selected_version = st.sidebar.radio(
            "النسخ المتاحة:",
            options=version_keys,
            index=0,
            key="version_select"
        )
    else:
        selected_version = 1

    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    st.markdown(f"### {custom_titles.get(subject, {}).get(lec_num, f'Lecture {lec_num}')} (Version {selected_version})")

    # عرض الأسئلة بالتنقل بينهم
    if "question_index" not in st.session_state:
        st.session_state["question_index"] = 0

    if len(questions) == 0:
        st.warning("لا توجد أسئلة في هذا الملف.")
        return

    current_index = st.session_state["question_index"]

    question = questions[current_index]

    st.markdown(f"**السؤال {current_index+1}:** {question['question']}")

    # خيارات السؤال
    options = question.get("options", [])
    selected_option = st.radio("اختر إجابة:", options, key=f"question_{current_index}")

    if st.button("السؤال التالي"):
        if st.session_state["question_index"] < len(questions) - 1:
            st.session_state["question_index"] += 1
        else:
            st.success("لقد وصلت إلى آخر سؤال في هذا المحاضرة")

    if st.button("السؤال السابق"):
        if st.session_state["question_index"] > 0:
            st.session_state["question_index"] -= 1

    # إظهار الشرح إذا كان متاح
    if selected_option is not None:
        answer_index = question.get("answer")
        explanation = question.get("explanation", "")
        if options.index(selected_option) == answer_index:
            st.success("✅ إجابة صحيحة")
        else:
            st.error("❌ إجابة خاطئة")
        if explanation:
            st.info(f"شرح: {explanation}")

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
                    <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/>
                </svg>
            </span>
        </a>
    </div>

    <div style="text-align:center; margin-top:15px; font-size:16px; color:#444;">
        Subscribe to the Telegram channel to get all updates and new lectures I will upload here, God willing.
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
