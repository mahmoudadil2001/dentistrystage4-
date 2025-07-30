import streamlit as st
import os
import base64
import json
import requests

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
        f.write("lecture_titles = " + json.dumps(lecture_titles, ensure_ascii=False, indent=4))

def push_to_github(file_path, commit_message, delete=False):
    token = st.secrets["GITHUB_TOKEN"]
    user = st.secrets["GITHUB_USER"]
    repo = st.secrets["GITHUB_REPO"]

    url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}"

    # تحقق من وجود الملف للحصول على sha
    r = requests.get(url, headers={"Authorization": f"token {token}"})
    sha = r.json().get("sha") if r.status_code == 200 else None

    if delete:
        if not sha:
            return
        res = requests.delete(url, headers={"Authorization": f"token {token}"}, json={"message": commit_message, "sha": sha, "branch": "main"})
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

def add_lecture_page():
    st.title("📚 إدارة المحاضرات (إضافة / حذف)")

    subjects = [
        "endodontics", "generalmedicine", "generalsurgery", "operative",
        "oralpathology", "oralsurgery", "orthodontics", "pedodontics",
        "periodontology", "prosthodontics"
    ]
    subject = st.selectbox("اختر المادة", subjects)

    lecture_titles = load_lecture_titles(subject)

    st.subheader("📋 المحاضرات الحالية")
    if lecture_titles:
        for lec_num, lec_title in sorted(lecture_titles.items()):
            col1, col2 = st.columns([4, 1])
            col1.write(f"📖 {lec_num} - {lec_title}")
            if col2.button("❌", key=f"del_{lec_num}"):
                # حذف ملفات المحاضرة
                for f in os.listdir(subject):
                    if f.startswith(f"{subject}{lec_num}"):
                        os.remove(os.path.join(subject, f))
                        push_to_github(os.path.join(subject, f), f"Delete lecture {f}", delete=True)

                # حذف من القاموس
                lecture_titles.pop(lec_num)
                save_lecture_titles(subject, lecture_titles)
                st.success(f"✅ تم حذف المحاضرة {lec_num}")
                st.rerun()
    else:
        st.info("ℹ️ لا توجد محاضرات لهذه المادة بعد")

    st.subheader("➕ إضافة محاضرة جديدة")
    lec_num = st.number_input("رقم المحاضرة", min_value=1, step=1)
    lec_title = st.text_input("عنوان المحاضرة (سيظهر في الواجهة)")
    version_num = st.number_input("رقم النسخة", min_value=1, step=1)
    content_code = st.text_area("اكتب كود الأسئلة (questions و Links)", height=300)

    if st.button("✅ إضافة وحفظ"):
        if lec_num in lecture_titles:
            st.error("❌ رقم المحاضرة موجود بالفعل")
            return
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

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_code)

        lecture_titles[int(lec_num)] = lec_title
        save_lecture_titles(subject, lecture_titles)

        st.success(f"✅ تم إنشاء الملف: {file_path}")
        push_to_github(file_path, f"Add lecture {filename}")

if __name__ == "__main__":
    add_lecture_page()
