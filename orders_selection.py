import streamlit as st
from versions_manager import get_lectures_and_versions
from orders_loader import load_lecture_titles

def select_subject():
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
    return st.selectbox("Select Subject", subjects)

def select_lecture(subject):
    lectures_versions = get_lectures_and_versions(subject)
    if not lectures_versions:
        st.error(f"⚠️ No lecture files found for subject {subject}!")
        return None, None

    lecture_titles = load_lecture_titles(subject)
    lectures_options = []
    for lec_num in sorted(lectures_versions.keys()):
        title = lecture_titles.get(lec_num, "").strip()
        display_name = f"Lec {lec_num}  {title}" if title else f"Lec {lec_num}"
        lectures_options.append((lec_num, display_name))

    lec_num = st.selectbox("Select Lecture", options=lectures_options, format_func=lambda x: x[1])[0]

    versions_dict = lectures_versions.get(lec_num, {})
    if not versions_dict:
        st.error("⚠️ لا توجد نسخ متاحة لهذه المحاضرة.")
        return None, None

    versions_keys = sorted(versions_dict.keys())

    # حفظ أو تحديث النسخة المحددة في session_state
    if "selected_version" not in st.session_state or st.session_state.get("selected_version") not in versions_dict:
        st.session_state.selected_version = versions_keys[0]

    selected_version = st.selectbox(
        "Select Version",
        options=versions_keys,
        index=versions_keys.index(st.session_state.selected_version)
    )
    st.session_state.selected_version = selected_version

    filename = versions_dict[selected_version]
    return filename, subject
