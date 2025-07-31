import streamlit as st
from versions_manager import get_lectures_and_versions, select_version_ui

def select_subject():
    subjects = ["endodontics", "implant", "periodontics"]  # مثال
    return st.sidebar.selectbox("اختر المادة", subjects)

def select_lecture(subject):
    if "in_quiz_mode" in st.session_state and st.session_state.in_quiz_mode:
        # في وضع الاختبار لا نعرض الاختيارات، نعطي القيم من الحالة مباشرة
        return st.session_state.get("current_lecture"), st.session_state.get("current_subject")

    lectures = get_lectures_and_versions(subject)
    if not lectures:
        st.sidebar.warning("لا توجد محاضرات متاحة لهذه المادة.")
        return None, None

    lecture_nums = sorted(lectures.keys())
    lec_num = st.sidebar.selectbox("اختر رقم المحاضرة", lecture_nums)

    versions = lectures[lec_num]
    version_num = select_version_ui(versions, sidebar_title="اختر نسخة السؤال", sidebar_label="النسخ المتاحة", key="version_select")

    filename = versions.get(version_num)
    return filename, subject
