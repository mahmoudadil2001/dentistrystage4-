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
    titles_dir = os.path.join(subject, "edit")
    if not os.path.exists(titles_dir):
        os.makedirs(titles_dir)

    titles_path = os.path.join(titles_dir, "lecture_titles.py")

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
    if not os.path.exists(subject):
        return {}

    lecture_files = os.listdir(subject)
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

    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ إضافة محاضرة", 
        "🗑️ إدارة / حذف المحاضرات", 
        "✏️ تعديل المحاضرة", 
        "🤖 شدز للـ AI"
    ])

    # ➕ إضافة محاضرة
    with tab1:
        st.header("➕ إضافة محاضرة")
        subject = st.selectbox("📌 اختر المادة", [""] + subjects, key="add_subject")
        if subject:
            operation = st.selectbox("اختر العملية", ["", "محاضرة جديدة", "نسخة جديدة"], key="add_operation")
            if operation == "محاضرة جديدة":
                lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1, key="add_lec_num")
                lec_title = st.text_input("عنوان المحاضرة (سيظهر في الواجهة)", key="add_lec_title")
                content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300, key="add_code")

                if st.button("✅ إضافة وحفظ", key="add_save_lecture"):
                    if not lec_title.strip():
                        st.error("❌ يجب كتابة عنوان المحاضرة")
                    elif not content_code.strip():
                        st.error("❌ يجب كتابة الكود")
                    else:
                        lecture_dict = get_existing_lectures(subject)
                        if lec_num in lecture_dict:
                            st.error(f"❌ عذراً، المحاضرة رقم {lec_num} موجودة بالفعل!")
                        else:
                            filename = f"{subject}{lec_num}.py"
                            file_path = os.path.join(subject, filename)

                            if not os.path.exists(subject):
                                os.makedirs(subject)

                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content_code)

                            lecture_titles = load_lecture_titles(subject)
                            lecture_titles[int(lec_num)] = lec_title.strip()
                            titles_path = save_lecture_titles(subject, lecture_titles)

                            push_to_github(file_path, f"Add lecture {filename}")
                            push_to_github(titles_path, f"Update lecture titles for {subject}")

                            st.success(f"✅ تم إنشاء الملف: {file_path}")
                            st.info("📌 تم تحديث العنوان في lecture_titles.py ورفعه إلى GitHub ✅")
                            st.experimental_rerun()

            elif operation == "نسخة جديدة":
                lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1, key="add_ver_lec_num")
                version_num = st.number_input("رقم النسخة", min_value=2, step=1, key="add_version_num")
                content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300, key="add_ver_code")

                if st.button("✅ إضافة وحفظ النسخة", key="add_save_version"):
                    lecture_dict = get_existing_lectures(subject)
                    versions = [v for v, _ in lecture_dict.get(lec_num, [])]

                    if version_num in versions:
                        st.error(f"❌ عذراً، النسخة رقم {version_num} من المحاضرة {lec_num} موجودة بالفعل!")
                    elif not content_code.strip():
                        st.error("❌ يجب كتابة الكود")
                    else:
                        filename = f"{subject}{lec_num}_v{version_num}.py"
                        file_path = os.path.join(subject, filename)

                        if not os.path.exists(subject):
                            os.makedirs(subject)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content_code)

                        push_to_github(file_path, f"Add version {version_num} for lecture {lec_num}")
                        st.success(f"✅ تم إنشاء النسخة: {file_path}")
                        st.experimental_rerun()

    # 🗑️ إدارة / حذف المحاضرات
    with tab2:
        st.header("🗑️ إدارة / حذف المحاضرات")
        subject = st.selectbox("📌 اختر المادة", [""] + subjects, key="delete_subject")
        if subject:
            lecture_dict = get_existing_lectures(subject)
            lecture_titles = load_lecture_titles(subject)
            if not lecture_dict:
                st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")
            else:
                options = []
                for lec_num in sorted(lecture_dict.keys()):
                    title = lecture_titles.get(lec_num, "بدون عنوان")
                    options.append(f"{lec_num} - {title}")

                selected_option = st.selectbox("اختر محاضرة", [""] + options, key="delete_lecture_select")
                if selected_option:
                    selected_lec_num = int(selected_option.split(" - ")[0])

                    versions = sorted(lecture_dict[selected_lec_num], key=lambda x: x[0])
                    version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]

                    selected_version = st.selectbox("اختر النسخة لحذفها", [""] + version_options, key="delete_version_select")
                    if selected_version:
                        selected_file = versions[version_options.index(selected_version)][1]

                        if st.button("❌ حذف النسخة المحددة", key="delete_button"):
                            file_path = os.path.join(subject, selected_file)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                push_to_github(file_path, f"Delete lecture {selected_file}", delete=True)
                                st.success("✅ تم حذف الملف")
                                st.experimental_rerun()
                            else:
                                st.error("❌ الملف غير موجود للحذف")

    # ✏️ تعديل المحاضرة
    with tab3:
        st.header("✏️ تعديل المحاضرة")
        subject = st.selectbox("📌 اختر المادة", [""] + subjects, key="edit_subject")
        if subject:
            lecture_dict = get_existing_lectures(subject)
            lecture_titles = load_lecture_titles(subject)

            if not lecture_dict:
                st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")
            else:
                options = []
                for lec_num in sorted(lecture_dict.keys()):
                    title = lecture_titles.get(lec_num, "بدون عنوان")
                    options.append(f"{lec_num} - {title}")

                selected_option = st.selectbox("اختر محاضرة", [""] + options, key="edit_lecture_select")
                if selected_option:
                    selected_lec_num = int(selected_option.split(" - ")[0])
                    versions = sorted(lecture_dict[selected_lec_num], key=lambda x: x[0])
                    version_options = [f"نسخة {v[0]} - {v[1]}" for v in versions]

                    selected_version = st.selectbox("اختر النسخة لتعديلها", [""] + version_options, key="edit_version_select")
                    if selected_version:
                        selected_file = versions[version_options.index(selected_version)][1]
                        file_path = os.path.join(subject, selected_file)

                        lec_title = st.text_input("تعديل عنوان المحاضرة", value=lecture_titles.get(selected_lec_num, ""), key="edit_lec_title")
                        with open(file_path, "r", encoding="utf-8") as f:
                            existing_code = f.read()

                        content_code = st.text_area("تعديل كود المحاضرة", value=existing_code, height=300, key="edit_code")

                        if st.button("💾 حفظ التعديلات", key="edit_save_button"):
                            if not lec_title.strip():
                                st.error("❌ يجب كتابة عنوان المحاضرة")
                            elif not content_code.strip():
                                st.error("❌ يجب كتابة الكود")
                            else:
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content_code)

                                lecture_titles[selected_lec_num] = lec_title.strip()
                                titles_path = save_lecture_titles(subject, lecture_titles)

                                push_to_github(file_path, f"Edit lecture {selected_file}")
                                push_to_github(titles_path, f"Update lecture titles for {subject}")

                                st.success("✅ تم حفظ التعديلات ورفعها إلى GitHub")
                                st.experimental_rerun()

    # 🤖 شدز للـ AI
    with tab4:
        section = st.selectbox(
            "اختر القسم:", 
            ["📌 تعليمات إضافة محاضرة", "📚 تعليمات إضافة نسخة", "💬 كود اضافة رابط"], 
            key="select_tab4_section"
        )

        if section == "📌 تعليمات إضافة محاضرة":
            st.markdown("1- روح لموقع **chat.deepseek.com**")
            st.markdown("2- حمل المحاضرة المطلوبة")
            st.markdown("3- تكتبله هذا النص بس تبدل عدد الـ MCQs")

            code1 = '''make number of Mcqs in python language in this patern
questions = [
    {
        "question": "What is monkey?",
        "options": ["animal", "plant", "car", "donkey"],
        "answer": "animal",
        "explanation": "'make a good explantation."
    }
]'''

            st.code(code1, language="python")
            st.download_button(
                "📋 نسخ", 
                data=code1, 
                file_name="mcqs_template.py", 
                mime="text/plain", 
                key="download_mcqs_template"
            )

        elif section == "📚 تعليمات إضافة نسخة":
            st.markdown("1- روح لـ **تعديل المحاضرة** وانسخ النسخ الموجودة")
            st.markdown("2- روح لموقع **chat.deepseek.com**")
            st.mkardown("3- ارسل النسخ اللي نسختها، بعدها حمل المحاضرة:")
            st.mkardown("4- اكتبله هالنص وغير عدد الاسئلة:")

            code2 = '''make number of Mcqs in python language in this patern Provided that you do not repeat or send any questions similar to the ones I sent.
questions = [
    {
        "question": "What is monkey?",
        "options": ["animal", "plant", "car", "donkey"],
        "answer": "animal",
        "explanation": "'make a good explantation."
    }
]'''

            st.code(code2, language="python")
            st.download_button(
                "📋 نسخ", 
                data=code2, 
                file_name="mcqs_version_template.py", 
                mime="text/plain", 
                key="download_mcqs_version_template"
            )

        elif section == "💬 كود اضافة رابط":
            st.write("تحطه في نهاية ملف الاسئلة")
            st.write("تكتب اسم ونص الرابط")

            code3 = '''Links = [
{"title": "الاسم", "url": "النص"},
]'''

            st.code(code3, language="python")
            st.download_button(
                "📋 نسخ", 
                data=code3, 
                file_name="links_code.py", 
                mime="text/plain", 
                key="download_links"
            )


def main():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            border-radius: 15px;
            padding: 20px;
            color: #003049;
            font-family: 'Tajawal', sans-serif;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
        ">
        مرحبًا بكم! هذا القسم مخصص لإدارة المحاضرات: الإضافة، الحذف، والتعديل.
        </div>
        """,
        unsafe_allow_html=True,
    )
    add_lecture_page()

if __name__ == "__main__":
    main()
