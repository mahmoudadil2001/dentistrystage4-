import streamlit as st
import os
import re

def select_version_ui(
    versions_dict, 
    sidebar_title="Select Question version", 
    sidebar_label="Available versions", 
    key="version_select"
):
    """
    واجهة اختيار النسخة في الشريط الجانبي مع Checkbox قريب جداً يمين و Radio يسار.
    ترجع:
    selected_version → النسخة المختارة
    completed_versions → حالة كل Checkbox
    """
    versions_count = len(versions_dict)
    selected_version = 1
    completed_versions = {}

    if versions_count > 0:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        for v in version_keys:
            cols = st.sidebar.columns([1, 0.3])  # عمود للراديو أكبر، وعمود صغير جداً للcheckbox قريب منه

            # Radio لاختيار النسخة بدون نص label
            if cols[0].radio(
                label="",
                options=[v],
                index=0 if v == version_keys[0] else -1,
                key=f"{key}_radio_{v}"
            ):
                selected_version = v

            # Checkbox بدون نص label عشان يكون مربع صغير فقط قريب
            completed_versions[v] = cols[1].checkbox(
                label="",
                key=f"{key}_checkbox_{v}"
            )

    return selected_version, completed_versions


def get_lectures_and_versions(subject_name, base_path="."):
    """
    Returns dict:
    { lec_num: { version_num: filename, ... }, ... }
    """
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
