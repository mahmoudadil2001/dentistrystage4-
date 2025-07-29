import streamlit as st
import os
import re

def select_version_ui(
    versions_dict, 
    sidebar_title="Select Question version", 
    sidebar_label="Available versions", 
    key="version_select"
):
    versions_count = len(versions_dict)
    selected_version = 1
    completed_versions = {}

    if versions_count > 0:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        for v in version_keys:
            cols = st.sidebar.columns([0.1, 3])  # عمود صغير للcheckbox، وعمود كبير للنسخة

            # Checkbox بدون نص في العمود الأول
            completed_versions[v] = cols[0].checkbox(
                label="",
                key=f"{key}_checkbox_{v}"
            )

            # رقم النسخة يظهر كنص عادي (بدل الراديو) في العمود الثاني
            if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v

    return selected_version, completed_versions


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
