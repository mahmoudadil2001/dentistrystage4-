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

    with tab1:
        # اختيار المادة
        subject = st.selectbox("📌 اختر المادة", subjects, key="add_subject")

        # إذا اختار المستخدم المادة استمر في إظهار باقي الخيارات
        if subject:

            # اختيار العملية: محاضرة جديدة أم نسخة جديدة
            action = st.radio("⚙️ اختر العملية", ["➕ محاضرة جديدة", "📄 نسخة جديدة"], key="add_action")

            # تحميل العناوين الموجودة والمحاضرات
            lecture_titles = load_lecture_titles(subject)
            lecture_dict = get_existing_lectures(subject)

            lec_num = st.number_input("📖 رقم المحاضرة", min_value=1, step=1, key="lec_num")

            if action == "➕ محاضرة جديدة":
                lec_title = st.text_input("📝 عنوان المحاضرة (سيظهر في الواجهة)", key="lec_title")
                content_code = st.text_area("✍️ اكتب كود الأسئلة (questions و Links)", height=300, key="content_code")

                if st.button("✅ إضافة وحفظ"):
                    # تحقق من وجود المحاضرة والنسخة مسبقًا
                    if lec_num in lecture_dict and any(v[0] == 1 for v in lecture_dict[lec_num]):
                        st.error(f"❌ عذراً، المحاضرة رقم {lec_num} موجودة بالفعل!")

                    elif not lec_title.strip():
                        st.error("❌ يجب كتابة عنوان المحاضرة")

                    elif not content_code.strip():
                        st.error("❌ يجب كتابة كود الأسئلة")

                    else:
                        filename = f"{subject}{int(lec_num)}.py"
                        file_path = os.path.join(subject, filename)

                        if not os.path.exists(subject):
                            os.makedirs(subject)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content_code)

                        lecture_titles[int(lec_num)] = lec_title.strip()
                        titles_path = save_lecture_titles(subject, lecture_titles)

                        push_to_github(file_path, f"Add lecture {filename}")
                        push_to_github(titles_path, f"Update lecture titles for {subject}")

                        st.success(f"✅ تم إنشاء المحاضرة رقم {lec_num} بنجاح!")
                        st.experimental_rerun()

            elif action == "📄 نسخة جديدة":
                version_num = st.number_input("🔢 رقم النسخة", min_value=2, step=1, key="version_num")
                content_code = st.text_area("✍️ اكتب كود النسخة الجديدة فقط", height=300, key="version_code")

                if st.button("✅ إضافة وحفظ نسخة جديدة"):
                    if lec_num not in lecture_dict:
                        st.error(f"❌ لا توجد محاضرة برقم {lec_num} لإضافة نسخة لها!")

                    elif any(v[0] == version_num for v in lecture_dict[lec_num]):
                        st.error(f"❌ النسخة رقم {version_num} موجودة بالفعل للمحاضرة {lec_num}!")

                    elif not content_code.strip():
                        st.error("❌ يجب كتابة كود النسخة الجديدة")

                    else:
                        filename = f"{subject}{int(lec_num)}_v{int(version_num)}.py"
                        file_path = os.path.join(subject, filename)

                        if not os.path.exists(subject):
                            os.makedirs(subject)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content_code)

                        # لا نحتاج لتحديث lecture_titles هنا لأنه نفس المحاضرة
                        push_to_github(file_path, f"Add version {version_num} for lecture {lec_num}")

                        st.success(f"✅ تم إضافة النسخة رقم {version_num} للمحاضرة رقم {lec_num} بنجاح!")
                        st.experimental_rerun()

    with tab2:
        subject = st.selectbox("📌 اختر المادة", subjects, key="delete_subject")

        if subject:
            lecture_titles = load_lecture_titles(subject)
            lecture_dict = get_existing_lectures(subject)

            st.subheader("📋 المحاضرات الحالية")
            if lecture_dict:
                options = []
                for lec_num in sorted(lecture_dict.keys()):
                    title = lecture_titles.get(lec_num, "بدون عنوان")
                    options.append(f"{lec_num} - {title}")

                selected_option = st.selectbox("📚 اختر محاضرة", options, key="lecture_select")
                selected_lec_num = int(selected_option.split(" - ")[0])

                versions = sorted(lecture_dict[selected_lec_num], key=lambda x: x[0])
                version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]

                selected_version = st.selectbox("📄 اختر النسخة لحذفها", version_options, key="version_select")
                selected_file = versions[version_options.index(selected_version)][1]

                if st.button("❌ حذف النسخة المحددة"):
                    file_path = os.path.join(subject, selected_file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        push_to_github(file_path, f"Delete lecture {selected_file}", delete=True)
                        st.experimental_rerun()
                    else:
                        st.error("❌ الملف غير موجود للحذف")
            else:
                st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")

if __name__ == "__main__":
    add_lecture_page()
