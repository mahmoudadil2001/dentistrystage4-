import streamlit as st
import os
import re
import requests
from versions_storage import get_user_checkboxes

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby0Y1Iq0incLLHdMAQUDWOp2qRXivZthdfLYEusIXZUEgCltNvxjuIRSaK4M2WUlfwK/exec"

def save_checkbox_state_to_sheet(username, sheet_name, version, checked):
    payload = {
        "action": "save_checkbox",
        "username": username,
        "sheet_name": sheet_name,
        "version": str(version),
        "checked": "true" if checked else "false"
    }
    try:
        requests.post(GOOGLE_SCRIPT_URL, data=payload)
    except:
        pass

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


def select_version_ui_with_checkboxes(
    versions_dict, 
    username,
    sheet_name,
    sidebar_title="Select Question version", 
    key="version_select",
    default_version=None,
):
    selected_version = default_version if default_version in versions_dict else 1

    # جلب حالات الـ checkbox من السيرفر
    saved_states = get_user_checkboxes(username, sheet_name)

    st.sidebar.markdown(f"### {sidebar_title}")

    version_keys = sorted(versions_dict.keys())

    # عرض نسخ المجموعة 1
    st.sidebar.markdown("#### نسخ المجموعة 1")
    for v in version_keys[:3]:
        checked = saved_states.get(v, False)
        cols = st.sidebar.columns([0.1, 3])
        new_checked = cols[0].checkbox("", value=checked, key=f"{key}_checkbox_{v}")

        if new_checked != checked:
            # حدث الحالة وأرسلها للسيرفر
            save_checkbox_state_to_sheet(username, sheet_name, v, new_checked)

        if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
            selected_version = v

    # نسخ المجموعة 2 إذا موجودة
    if len(version_keys) > 3:
        st.sidebar.markdown("#### نسخ المجموعة 2")
        for v in version_keys[3:6]:
            checked = saved_states.get(v, False)
            cols = st.sidebar.columns([0.1, 3])
            new_checked = cols[0].checkbox("", value=checked, key=f"{key}_checkbox_{v}")

            if new_checked != checked:
                save_checkbox_state_to_sheet(username, sheet_name, v, new_checked)

            if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v

    return selected_version


def select_version_ui(
    versions_dict, 
    sidebar_title="Select Question version", 
    sidebar_label="Available versions", 
    key="version_select"
):
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
