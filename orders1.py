import streamlit as st
import os
import importlib.util

def load_and_select_subject_lecture_version():
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
        return None, None, None, None

    lecture_titles = load_lecture_titles(subject)

    lectures_options = []
    for lec_num in sorted(lectures_versions.keys()):
        title = lecture_titles.get(lec_num, "").strip()
        display_name = f"Lec {lec_num} {title}" if title else f"Lec {lec_num}"
        lectures_options.append((lec_num, display_name))

    lec_num = st.selectbox(
        "Select Lecture",
        options=lectures_options,
        format_func=lambda x: x[1]
    )[0]

    versions_dict = lectures_versions.get(lec_num, {})
    versions_keys = sorted(versions_dict.keys())

    if not versions_keys:
        st.error("⚠️ لا توجد نسخ متاحة لهذه المحاضرة.")
        return None, None, None, None

    selected_version = st.selectbox(
        "Select Version",
        options=versions_keys,
        index=0
    )

    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)

    questions_module = import_module_from_file(file_path)
    if questions_module is None:
        st.error(f"⚠️ File {filename} not found or cannot be imported.")
        return None, None, None, None

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    return subject, lec_num, selected_version, (questions, Links)


def import_module_from_file(filepath):
    if not os.path.exists(filepath):
        return None
    spec = importlib.util.spec_from_file_location(os.path.basename(filepath).replace(".py", ""), filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_lecture_titles(subject_name):
    titles_file = os.path.join(subject_name, "edit", "lecture_titles.py")
    if not os.path.exists(titles_file):
        return {}

    module_name = f"{subject_name}_titles"
    import sys
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, titles_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, "lecture_titles", {})


def get_lectures_and_versions(subject):
    import os
    path = os.path.join(subject, "versions")
    if not os.path.exists(path):
        return {}

    lectures_versions = {}
    for filename in os.listdir(path):
        if filename.endswith(".py"):
            parts = filename.replace(".py", "").split("_")
            if len(parts) >= 3 and parts[0] == "lec":
                lec_num = int(parts[1])
                version = parts[2]
                if lec_num not in lectures_versions:
                    lectures_versions[lec_num] = {}
                lectures_versions[lec_num][version] = os.path.join("versions", filename)
    return lectures_versions
