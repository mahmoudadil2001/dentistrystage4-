import streamlit as st
from versions_manager import get_lectures_and_versions
from orders1 import load_lecture_titles, import_module_from_file

def load_subjects():
    return [
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

def get_selected_subject():
    subjects = load_subjects()
    subject = st.selectbox("Select Subject", subjects)
    return subject

def get_selected_lecture(subject):
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

    lec_num = st.selectbox(
        "Select Lecture",
        options=lectures_options,
        format_func=lambda x: x[1]
    )[0]

    return lec_num, lectures_versions

def get_selected_version(lec_num, lectures_versions):
    versions_dict = lectures_versions.get(lec_num, {})

    versions_keys = sorted(versions_dict.keys())
    if not versions_keys:
        st.error("⚠️ لا توجد نسخ متاحة لهذه المحاضرة.")
        return None, None

    if "selected_version" not in st.session_state or st.session_state.get("selected_version") not in versions_dict:
        st.session_state.selected_version = versions_keys[0]

    selected_version = st.selectbox(
        "Select Version",
        options=versions_keys,
        index=versions_keys.index(st.session_state.selected_version)
    )
    st.session_state.selected_version = selected_version

    filename = versions_dict[selected_version]
    return selected_version, filename
