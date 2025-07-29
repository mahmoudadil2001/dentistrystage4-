import streamlit as st

def select_version_ui(
    versions_dict, 
    sidebar_title="Select Question version", 
    sidebar_label="Available versions", 
    key="version_select"
):
    """
    عرض واجهة اختيار النسخة في الشريط الجانبي مع checkboxes لكل نسخة وزر بجانب كل نسخة.
    ترجع رقم النسخة المختارة.
    """
    versions_count = len(versions_dict)
    selected_version = 1
    completed_versions = {}

    if versions_count > 0:
        st.sidebar.markdown(f"### {sidebar_title}")
        version_keys = sorted(versions_dict.keys())

        for v in version_keys:
            cols = st.sidebar.columns([0.1, 3])  # عمود صغير للcheckbox، وعمود كبير لزر النسخة

            # Checkbox بدون نص في العمود الأول (مربع صغير فقط)
            completed_versions[v] = cols[0].checkbox(
                label="",
                key=f"{key}_checkbox_{v}"
            )

            # زر النسخة يظهر في العمود الثاني كنص تفاعلي
            if cols[1].button(f"نسخة {v}", key=f"{key}_button_{v}"):
                selected_version = v

    else:
        selected_version = 1

    return selected_version, completed_versions
