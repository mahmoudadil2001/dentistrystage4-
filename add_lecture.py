import streamlit as st
import os
import base64
import json
import requests

def update_lecture_titles(subject, lec_num, lec_title):
    titles_path = os.path.join(subject, "edit", "lecture_titles.py")

    # إذا الملف ما موجود، نعمله ونضيف dict فارغ
    if not os.path.exists(os.path.dirname(titles_path)):
        os.makedirs(os.path.dirname(titles_path))

    if not os.path.exists(titles_path):
        with open(titles_path, "w", encoding="utf-8") as f:
            f.write("lecture_titles = {}\n")

    # قراءة المحتوى الحالي
    with open(titles_path, "r", encoding="utf-8") as f:
        content = f.read()

    # استخراج القاموس الحالي
    namespace = {}
    exec(content, namespace)
    lecture_titles = namespace.get("lecture_titles", {})

    # إضافة / تعديل العنوان
    lecture_titles[int(lec_num)] = lec_title

    # كتابة التغييرات
    with open(titles_path, "w", encoding="utf-8") as f:
        f.write("lecture_titles = " + json.dumps(lecture_titles, ensure_ascii=False, indent=4))

def push_to_github(file_path, commit_message):
    token = st.secrets["GITHUB_TOKEN"]
    user = st.secrets["GITHUB_USER"]
    repo = st.secrets["GITHUB_REPO"]

    url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}"

    # تحقق إذا الملف موجود مسبقاً للحصول على sha
    r = requests.get(url, headers={"Authorization": f"token {token}"})
    sha = r.json().get("sha") if r.status_code == 200 else None

    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    data = {
        "message": commit_message,
        "content": content,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    res = requests.put(url, headers={"Authorization": f"token {token}"}, json=data)
    if res.status_code in [200, 201]:
        st.success("✅ تم رفع الملف إلى GitHub")
    else:
        st.error(f"❌ فشل الرفع: {res.status_code}")
        st.json(res.json())

def add_lecture_page():
    st.title("➕ إضافة محاضرة جديدة")

    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
    ]
    subject = st.selectbox("اختر المادة", subjects)

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

        # إنشاء المجلد إذا غير موجود
        if not os.path.exists(subject):
            os.makedirs(subject)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_code)

        update_lecture_titles(subject, lec_num, lec_title)
        st.success(f"✅ تم إنشاء الملف: {file_path}")

        push_to_github(file_path, f"Add lecture {filename}")

if __name__ == "__main__":
    add_lecture_page()
