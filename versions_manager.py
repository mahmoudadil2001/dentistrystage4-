import streamlit as st

def select_version_ui(versions_dict, sidebar_title="Select Question version", sidebar_label="Available versions", key="version_select"):
    """
    عرض واجهة اختيار النسخة في الشريط الجانبي.
    ترجع رقم النسخة المختارة.
    """
    versions_count = len(versions_dict)
    selected_version = 1

    if versions_count > 1:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())
        selected_version = st.sidebar.radio(
            sidebar_label,
            options=version_keys,
            index=0,
            key=key
        )
    else:
        selected_version = 1

    return selected_version


def get_lectures_and_versions(subject_name, base_path="."):
    """
    Returns dict:
    { lec_num: { version_num: filename, ... }, ... }
    """
    import os
    import re

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
