import streamlit as st
import os
import base64
import requests
import re

def load_lecture_titles(subject):
    titles_path = os.path.join(subject, "edit", "lecture_titles.py")
    if not os.path.exists(titles_path):
        return {}

    with open(titles_path, "r", encoding="utf-8") as f:
        content = f.read()

    namespace = {}
    exec(content, namespace)
    return namespace.get("lecture_titles", {})

def save_lecture_titles(subject, lecture_titles):
    titles_path = os.path.join(subject, "edit", "lecture_titles.py")
    if not os.path.exists(os.path.dirname(titles_path)):
        os.makedirs(os.path.dirname(titles_path))

    with open(titles_path, "w", encoding="utf-8") as f:
        f.write("lecture_titles = {\n")
        for k in sorted(lecture_titles.keys()):
            title = lecture_titles[k].replace('"', '\\"')
            f.write(f'    {k}: "{title}",\n')
        f.write("}\n")

    return titles_path

def push_to_github(file_path, commit_message, delete=False):
    token = st.secrets["GITHUB_TOKEN"]
    user = st.secrets["GITHUB_USER"]
    repo = st.secrets["GITHUB_REPO"]

    url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}"
    r = requests.get(url, headers={"Authorization": f"token {token}"})
    sha = r.json().get("sha") if r.status_code == 200 else None

    if delete:
        if not sha:
            return
        requests.delete(
            url,
            headers={"Authorization": f"token {token}"},
            json={"message": commit_message, "sha": sha, "branch": "main"}
        )
    else:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        data = {"message": commit_message, "content": content, "branch": "main"}
        if sha:
            data["sha"] = sha

        res = requests.put(url, headers={"Authorization": f"token {token}"}, json=data)

        if res.status_code not in [200, 201]:
            st.error(f"❌ خطأ في GitHub: {res.status_code}")
            st.json(res.json())

def get_existing_lectures(subject):
    lecture_files = os.listdir(subject) if os.path.exists(subject) else []
    lecture_dict = {}

    for f in lecture_files:
        match = re.match(rf"{subject}(\d+)(?:_v(\d+))?\.py$", f)
        if match:
            lec_num = int(match.group(1))
            version = int(match.group(2)) if match.group(2) else 1
            if lec_num not in lecture_dict:
                lecture_dict[lec_num] = []
            lecture_dict[lec_num].append((version, f))

    return lecture_dict

def add_lecture_page():
    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
    ]

    tab1, tab2 = st.tabs(["➕ إضافة محاضرة", "🗑️ إدارة / حذف المحاضرات"])

    # تبويب الإضافة
    with tab1:
        if "add_subject" not in st.session_state:
            st.session_state.add_subject = None
        if "action_choice" not in st.session_state:
            st.session_state.action_choice = None

        subject = st.selectbox("📌 اختر المادة", subjects, key="add_subject")
        st.session_state.add_subject = subject

        if st.session_state.add_subject:
            action = st.radio("⚙️ اختر العملية", ["➕ محاضرة جديدة", "📄 نسخة جديدة"], key="action_choice")
            st.session_state.action_choice = action

            lecture_dict = get_existing_lectures(st.session_state.add_subject)
            lecture_titles = load_lecture_titles(st.session_state.add_subject)

            if st.session_state.action_choice == "➕ محاضرة جديدة":
                lec_num = st.number_input("🔢 رقم المحاضرة", min_value=1, step=1, key="new_lec_num")
                lec_title = st.text_input("🏷️ عنوان المحاضرة (سيظهر في الواجهة)", key="new_lec_title")
                content_code = st.text_area("📜 اكتب كود الأسئلة", height=300, key="new_lec_code")

                if st.button("✅ إضافة وحفظ", key="save_new_lecture"):
                    if lec_num in lecture_dict:
                        st.error("❌ هذه المحاضرة موجودة بالفعل!")
                    else:
                        filename = f"{st.session_state.add_subject}{int(lec_num)}.py"
                        file_path = os.path.join(st.session_state.add_subject, filename)

                        if not os.path.exists(st.session_state.add_subject):
                            os.makedirs(st.session_state.add_subject)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content_code)

                        lecture_titles[int(lec_num)] = lec_title.strip()
                        titles_path = save_lecture_titles(st.session_state.add_subject, lecture_titles)

                        push_to_github(file_path, f"Add lecture {filename}")
                        push_to_github(titles_path, f"Update lecture titles for {st.session_state.add_subject}")
                        st.success(f"✅ تم إنشاء الملف: {file_path}")

            elif st.session_state.action_choice == "📄 نسخة جديدة":
                lec_num = st.number_input("🔢 اختر رقم المحاضرة لإضافة نسخة جديدة", min_value=1, step=1, key="copy_lec_num")
                version_num = st.number_input("📄 رقم النسخة", min_value=2, step=1, key="copy_version_num")
                content_code = st.text_area("📜 اكتب كود الأسئلة", height=300, key="copy_code")

                if st.button("✅ إضافة النسخة", key="save_new_version"):
                    if lec_num not in lecture_dict:
                        st.error("❌ هذه المحاضرة غير موجودة لإضافة نسخة جديدة!")
                    else:
                        filename = f"{st.session_state.add_subject}{int(lec_num)}_v{int(version_num)}.py"
                        file_path = os.path.join(st.session_state.add_subject, filename)

                        if os.path.exists(file_path):
                            st.error("❌ هذه النسخة موجودة بالفعل!")
                        else:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content_code)

                            push_to_github(file_path, f"Add new version {filename}")
                            st.success(f"✅ تم إنشاء النسخة: {file_path}")

    # تبويب الحذف
    with tab2:
        subject = st.selectbox("📌 اختر المادة", subjects, key="delete_subject")

        if subject:
            lecture_dict = get_existing_lectures(subject)
            lecture_titles = load_lecture_titles(subject)

            if lecture_dict:
                lec_num = st.selectbox("🔢 اختر المحاضرة", sorted(lecture_dict.keys()), key="del_lec_num")

                if lec_num:
                    versions = sorted(lecture_dict[lec_num], key=lambda x: x[0])
                    version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]
                    selected_version = st.selectbox("📄 اختر النسخة", version_options, key="del_version")

                    if selected_version:
                        selected_file = versions[version_options.index(selected_version)][1]

                        if st.button("❌ حذف النسخة المحددة", key="delete_btn"):
                            file_path = os.path.join(subject, selected_file)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                push_to_github(file_path, f"Delete lecture {selected_file}", delete=True)
                                st.success("🗑️ تم الحذف بنجاح!")
                                st.experimental_rerun()
                            else:
                                st.error("❌ الملف غير موجود للحذف")
            else:
                st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")

if __name__ == "__main__":
    add_lecture_page()
