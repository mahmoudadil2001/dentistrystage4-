import streamlit as st
import os
import re

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


def select_version_ui(
    versions_dict, 
    sidebar_title="Select Question version", 
    sidebar_label="Available versions", 
    key="version_select"
):
    """
    واجهة اختيار النسخة في الشريط الجانبي.
    ترجع رقم النسخة المختارة.
    """
    versions_count = len(versions_dict)
    selected_version = 1
    completed_versions = {}

    if versions_count > 1:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        for v in version_keys:
            cols = st.sidebar.columns([0.1, 3])  # عمود صغير للcheckbox، وعمود كبير لزر النسخة

            completed_versions[v] = cols[0].checkbox(
                label="",
                key=f"{key}_checkbox_{v}"
            )

            if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v
    else:
        selected_version = 1

    return selected_version


def select_version_ui_with_checkboxes(versions_dict, sidebar_title="Select Question version", key="version_select"):
    """
    دالة تعرض نسخ (versions) في الشريط الجانبي مع checkboxes لكل نسخة وزر اختيار نسخة.
    تعرض 3 نسخ أولى، ثم 3 نسخ أخرى (مثلاً للعرض بشكل مجموعتين).
    ترجع النسخة المختارة (selected_version).
    """
    selected_version = 1
    completed_versions = {}

    st.sidebar.markdown(f"### {sidebar_title}")

    version_keys = sorted(versions_dict.keys())

    # عرض 3 نسخ الأولى
    st.sidebar.markdown("#### نسخ المجموعة 1")
    for v in version_keys[:3]:
        cols = st.sidebar.columns([0.1, 3])
        completed_versions[v] = cols[0].checkbox("", key=f"{key}_checkbox_{v}")
        if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
            selected_version = v

    # إذا فيه أكثر من 3 نسخ، عرض 3 نسخ إضافية (المجموعة 2)
    if len(version_keys) > 3:
        st.sidebar.markdown("#### نسخ المجموعة 2")
        for v in version_keys[3:6]:
            cols = st.sidebar.columns([0.1, 3])
            completed_versions[v] = cols[0].checkbox("", key=f"{key}_checkbox_{v}")
            if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v

    return selected_version
