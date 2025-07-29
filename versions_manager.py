import streamlit as st
import os
import re

#هلا جات جي بي تي قبل لاتعدل اي شي احب انبهك ان الملف مربوط بدوال مهمة بملف اسموا order.py
#سطر 50 و 69 و 71 بالترتيب 
#lectures_versions = get_lectures_and_versions(subject)   
#versions_dict = lectures_versions.get(lec_num, {})   
#selected_version = select_version_ui_with_checkboxes(versions_dict)  


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

    # إذا فيه أكثر من نسخة
    if versions_count > 1:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        for v in version_keys:
            cols = st.sidebar.columns([0.2, 3])  # عمود صغير للcheckbox، وعمود أعرض للزر
            completed_versions[v] = cols[0].checkbox(
                label="",
                key=f"{key}_checkbox_{v}"
            )

            # محيط الزر div مخصص فقط لزر "نسخة"
            with cols[1]:
                st.markdown(
                    """
                    <style>
                    div.custom-version-button > div.stButton > button {
                        height: 45px;
                        width: 130px;
                        font-size: 18px;
                        background-color: #4CAF50;
                        color: white;
                    }
                    div.custom-version-button > div.stButton > button:hover {
                        background-color: #45a049;
                    }
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
                st.markdown('<div class="custom-version-button">', unsafe_allow_html=True)
                if st.button(f"نسخة {v}", key=f"{key}_button_{v}"):
                    selected_version = v
                st.markdown('</div>', unsafe_allow_html=True)
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

    # CSS خاص لأزرار النسخ فقط
    st.sidebar.markdown(
        """
        <style>
        div.custom-version-button > div.stButton > button {
            height: 20px;
            width: 90px;
            font-size: 18px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            border: none;
            transition: background-color 0.3s ease;
            cursor: pointer;
        }
        div.custom-version-button > div.stButton > button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # عرض 3 نسخ الأولى
    for v in version_keys[:3]:
        cols = st.sidebar.columns([0.2, 3])
        completed_versions[v] = cols[0].checkbox("", key=f"{key}_checkbox_{v}")
        with cols[1]:
            st.markdown('<div class="custom-version-button">', unsafe_allow_html=True)
            if st.button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v
            st.markdown('</div>', unsafe_allow_html=True)

    # إذا فيه أكثر من 3 نسخ، عرض 3 نسخ إضافية (المجموعة 2)
    if len(version_keys) > 3:
        st.sidebar.markdown("#### نسخ المجموعة 2")
        for v in version_keys[3:6]:
            cols = st.sidebar.columns([0.2, 3])
            completed_versions[v] = cols[0].checkbox("", key=f"{key}_checkbox_{v}")
            with cols[1]:
                st.markdown('<div class="custom-version-button">', unsafe_allow_html=True)
                if st.button(f"نسخة {v}", key=f"{key}_button_{v}"):
                    selected_version = v
                st.markdown('</div>', unsafe_allow_html=True)

    return selected_version
