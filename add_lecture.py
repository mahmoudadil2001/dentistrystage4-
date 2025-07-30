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

    return titles_path  # ✅ نرجع مسار الملف حتى نرفعه على GitHub

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

    # ✅ تبويب إضافة محاضرة
    with tab1:
        subject = st.selectbox("اختر المادة", subjects, key="add_subject")
        lecture_titles = load_lecture_titles(subject)
        lecture_dict = get_existing_lectures(subject)

        lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1)
        lec_title = st.text_input("عنوان المحاضرة (سيظهر في الواجهة)")
        version_num = st.number_input("رقم النسخة", min_value=1, step=1)
        content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300)

        if st.button("✅ إضافة وحفظ"):
            if not lec_title.strip():
                st.error("❌ يجب كتابة عنوان المحاضرة")
                return
            if not content_code.strip():
                st.error("❌ يجب كتابة الكود")
                return

            filename = f"{subject}{int(lec_num)}" + (f"_v{int(version_num)}" if version_num > 1 else "") + ".py"
            file_path = os.path.join(subject, filename)

            if not os.path.exists(subject):
                os.makedirs(subject)

            # ✅ إنشاء ملف الأسئلة
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content_code)

            # ✅ تحديث عنوان المحاضرة في lecture_titles
            lecture_titles[int(lec_num)] = lec_title.strip()
            titles_path = save_lecture_titles(subject, lecture_titles)

            # ✅ رفع الملفات إلى GitHub
            push_to_github(file_path, f"Add lecture {filename}")
            push_to_github(titles_path, f"Update lecture titles for {subject}")

            st.success(f"✅ تم إنشاء الملف: {file_path}")
            st.info("📌 تم تحديث العنوان في lecture_titles.py ورفعه إلى GitHub ✅")

    # ✅ تبويب الحذف
    with tab2:
        subject = st.selectbox("اختر المادة", subjects, key="delete_subject")
        lecture_titles = load_lecture_titles(subject)
        lecture_dict = get_existing_lectures(subject)

        st.subheader("📋 المحاضرات الحالية")
        if lecture_dict:
            options = []
            for lec_num in sorted(lecture_dict.keys()):
                title = lecture_titles.get(lec_num, "بدون عنوان")
                options.append(f"{lec_num} - {title}")

            selected_option = st.selectbox("اختر محاضرة", options, key="lecture_select")
            selected_lec_num = int(selected_option.split(" - ")[0])

            versions = sorted(lecture_dict[selected_lec_num], key=lambda x: x[0])
            version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]

            selected_version = st.selectbox("اختر النسخة لحذفها", version_options, key="version_select")
            selected_file = versions[version_options.index(selected_version)][1]

            if st.button("❌ حذف النسخة المحددة"):
                file_path = os.path.join(subject, selected_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    push_to_github(file_path, f"Delete lecture {selected_file}", delete=True)
                    st.rerun()
                else:
                    st.error("❌ الملف غير موجود للحذف")
        else:
            st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")

if __name__ == "__main__":
    add_lecture_page()
