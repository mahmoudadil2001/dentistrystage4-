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
    واجهة اختيار النسخة في الشريط الجانبي.
    🔹 ترجع:
       - إذا استدعيتها كالسابق → نفس رقم النسخة فقط.
       - وإذا خزّنت النتيجة في متغيرين → يعطيك (selected_version, completed_versions).
    """
    versions_count = len(versions_dict)
    selected_version = 1
    completed_versions = {}

    if versions_count > 1:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        # الوظيفة الأساسية (اختيار النسخة)
        selected_version = st.sidebar.radio(
            sidebar_label,
            options=version_keys,
            index=0,
            key=key
        )

        # إضافة Checkboxes بدون التأثير على الكود القديم
        st.sidebar.markdown("### ضع علامة صح إذا أنهيت النسخة:")
        for v in version_keys:
            completed_versions[v] = st.sidebar.checkbox(
                f"✔️ النسخة {v}",
                key=f"{key}_checkbox_{v}"
            )
    else:
        selected_version = 1
        completed_versions[1] = st.sidebar.checkbox(
            "✔️ النسخة 1",
            key=f"{key}_checkbox_1"
        )

    # إذا استُخدمت كما في الكود القديم → ترجع رقم النسخة فقط
    # وإذا استُخدمت مع متغيرين → ترجع النسخة وحالة الصح
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
