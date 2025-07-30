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
        requests.delete(url, headers={"Authorization": f"token {token}"},
                        json={"message": commit_message, "sha": sha, "branch": "main"})
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

    with tab1:
        subject = st.selectbox("اختر المادة", subjects, key="add_subject")
        lecture_titles = load_lecture_titles(subject)
        lecture_dict = get_existing_lectures(subject)

        action = st.radio("ماذا تريد؟", ["➕ محاضرة جديدة", "📄 نسخة جديدة"])

        if action == "➕ محاضرة جديدة":
            lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1)
            lec_title = st.text_input("عنوان المحاضرة (سيظهر في الواجهة)")
            content_code = st.text_area("اكتب كود الأسئلة", height=300)

            if st.button("✅ إضافة وحفظ"):
                if lec_num in lecture_dict:
                    st.error("❌ هذه المحاضرة موجودة بالفعل!")
                    return
                if not lec_title.strip() or not content_code.strip():
                    st.error("❌ يجب كتابة العنوان والكود")
                    return

                filename = f"{subject}{int(lec_num)}.py"
                file_path = os.path.join(subject, filename)
                os.makedirs(subject, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content_code)

                lecture_titles[int(lec_num)] = lec_title.strip()
                titles_path = save_lecture_titles(subject, lecture_titles)

                push_to_github(file_path, f"Add lecture {filename}")
                push_to_github(titles_path, f"Update lecture titles for {subject}")
                st.success("✅ تمت إضافة المحاضرة")

        elif action == "📄 نسخة جديدة":
            if not lecture_dict:
                st.warning("⚠️ لا توجد محاضرات لإضافة نسخة!")
                return

            lec_num = st.selectbox("اختر المحاضرة", sorted(lecture_dict.keys()))
            version_num = st.number_input("رقم النسخة", min_value=2, step=1)
            content_code = st.text_area("اكتب كود النسخة", height=300)

            if st.button("✅ إضافة النسخة"):
                versions = [v for v, _ in lecture_dict[lec_num]]
                if version_num in versions:
                    st.error("❌ هذه النسخة موجودة بالفعل!")
                    return

                filename = f"{subject}{int(lec_num)}_v{int(version_num)}.py"
                file_path = os.path.join(subject, filename)
                os.makedirs(subject, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content_code)

                push_to_github(file_path, f"Add new version {filename}")
                st.success("✅ تمت إضافة النسخة")

    # تبويب الحذف يبقى كما هو
    with tab2:
        st.write("هنا تضع كود الحذف القديم")

if __name__ == "__main__":
    add_lecture_page()
