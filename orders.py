import streamlit as st
import os
import importlib.util
import re

# أسماء المحاضرات (يمكن تعديله)
custom_titles_data = {
    ("endodontics", 1): "Lecture 1 introduction",
    ("endodontics", 2): "Lecture 2 periapical disease classification",
    ("endodontics", 3): "Lecture 3 name",
    ("generalmedicine", 1): "Lecture 1 name",
    ("oralpathology", 1): "Lec 1 Biopsy"
}

custom_titles = {}
for (subject, num), title in custom_titles_data.items():
    custom_titles.setdefault(subject, {})[num] = title

def get_lectures_and_versions(subject_name, base_path="."):
    """
    ترجع قاموس بصيغة:
    { lec_num: { version_num: filename, ... }, ... }
    """
    subject_path = os.path.join(base_path, subject_name)
    if not os.path.exists(subject_path):
        return {}

    files = os.listdir(subject_path)
    # نمط اسم الملف: subjectname + رقم المحاضرة + _vرقم النسخة (اختياري) + .py
    pattern = re.compile(rf"^{re.escape(subject_name)}(\d+)(?:_v(\d+))?\.py$", re.IGNORECASE)

    lectures = {}
    for f in files:
        m = pattern.match(f)
        if m:
            lec_num = int(m.group(1))
            version_num = int(m.group(2)) if m.group(2) else 1  # النسخة 1 إذا غير محددة
            if lec_num not in lectures:
                lectures[lec_num] = {}
            lectures[lec_num][version_num] = f

    # ترتيب النسخ تصاعدياً لكل محاضرة
    for lec in lectures:
        lectures[lec] = dict(sorted(lectures[lec].items()))
    return lectures

def import_module_from_file(filepath):
    if not os.path.exists(filepath):
        return None
    spec = importlib.util.spec_from_file_location(os.path.basename(filepath).replace(".py", ""), filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def orders_o():
    subjects = [
        "endodontics",
        "generalmedicine",
        "generalsurgery",
        "operative",
        "oralpathology",
        "oralsurgery",
        "orthodontics",
        "pedodontics",
        "periodontology",
        "prosthodontics"
    ]

    subject = st.selectbox("اختر المادة", subjects)

    lectures_versions = get_lectures_and_versions(subject)
    if not lectures_versions:
        st.error(f"⚠️ لا يوجد ملفات محاضرات للمادة {subject}!")
        return

    # تحضير قائمة المحاضرات مع عناوين مخصصة أو عامة
    lectures_list = []
    for lec_num in sorted(lectures_versions.keys()):
        if subject in custom_titles and lec_num in custom_titles[subject]:
            lectures_list.append(f"{lec_num} - {custom_titles[subject][lec_num]}")
        else:
            lectures_list.append(f"{lec_num} - Lecture {lec_num}")

    # اختيار المحاضرة
    lecture_choice = st.selectbox("اختر المحاضرة", lectures_list)
    # نأخذ رقم المحاضرة فقط من النص
    lec_num = int(lecture_choice.split(" ")[0])

    # جلب النسخ المتاحة للمحاضرة المختارة
    versions_dict = lectures_versions.get(lec_num, {})
    versions_count = len(versions_dict)

    # إذا النسخة أكثر من 1 نعرض شريط اختيار نسخة بشكل صغير جانباً
    selected_version = 1
    if versions_count > 1:
        st.sidebar.markdown("### اختر نسخة الأسئلة")
        version_keys = sorted(versions_dict.keys())
        selected_version = st.sidebar.radio(
            "النسخ المتاحة:",
            options=version_keys,
            index=0,
            key="version_select"
        )
    else:
        # نسخة واحدة فقط - اختارها مباشرة
        selected_version = 1

    # استيراد ملف الأسئلة المناسب
    filename = versions_dict[selected_version]
    file_path = os.path.join(subject, filename)
    questions_module = import_module_from_file(file_path)

    if questions_module is None:
        st.error(f"⚠️ الملف {filename} غير موجود أو لا يمكن استيراده.")
        return

    questions = getattr(questions_module, "questions", [])
    Links = getattr(questions_module, "Links", [])

    # بدء حالة الأسئلة في الجلسة أو إعادة التهيئة لو المحاضرة أو النسخة تغيرت
    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lecture_choice) or \
       (st.session_state.get("current_subject", None) != subject) or \
       (st.session_state.get("current_version", None) != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lecture_choice
        st.session_state.current_subject = subject
        st.session_state.current_version = selected_version

    def normalize_answer(q):
        answer = q.get("answer") or q.get("correct_answer")
        options = q["options"]

        if isinstance(answer, int) and 0 <= answer < len(options):
            return options[answer]

        if isinstance(answer, str):
            answer_clean = answer.strip().upper()
            if answer_clean in ["A", "B", "C", "D"]:
                idx = ord(answer_clean) - ord("A")
                if 0 <= idx < len(options):
                    return options[idx]
            if answer in options:
                return answer

        return None

    with st.sidebar:
        st.markdown(f"### 🧪 {subject.upper()}")

        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} سؤال {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)

        current_q_num = index + 1
        total_qs = len(questions)
        st.markdown(f"### سؤال {current_q_num}/{total_qs}: {q['question']}")

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio(
            "",
            q["options"],
            index=default_idx,
            key=f"radio_{index}"
        )

        if not st.session_state.answer_shown[index]:
            if st.button("أجب", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            user_ans = st.session_state.user_answers[index]
            if user_ans == correct_text:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ الإجابة الصحيحة: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 الشرح: {q['explanation']}")

            if st.button("السؤال التالي", key=f"next_{index}"):
                if index + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()

        # عرض روابط الشرح أسفل السؤال بدون عنوان النص
        if Links:
            st.markdown("---")
            for link in Links:
                st.markdown(f"- [{link['title']}]({link['url']})")

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question)
    else:
        st.header("🎉 تم الانتهاء من الاختبار!")
        correct = 0
        for i, q in enumerate(questions):
            correct_text = normalize_answer(q)
            user = st.session_state.user_answers[i]
            if user == correct_text:
                correct += 1
                st.write(f"سؤال {i+1}: ✅ صحيحة")
            else:
                st.write(f"سؤال {i+1}: ❌ خاطئة (إجابتك: {user}, الصحيحة: {correct_text})")
        st.success(f"النتيجة: {correct} من {len(questions)}")

        if st.button("🔁 أعد الاختبار"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()

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
        هلا طلاب شونكم؟ المواد تخص طلاب مرحلة رابعة طب الأسنان جامعة الأسراء اختار المادة والمحاضرة وابدأ الاختبار بالتوفيق
        </div>
        """,
        unsafe_allow_html=True,
    )
    orders_o()

    st.markdown('''
    <div style="display:flex; justify-content:center; margin-top:50px;">
        <a href="https://t.me/dentistryonly0" target="_blank" style="display:inline-flex; align-items:center; background:#0088cc; color:#fff; padding:8px 16px; border-radius:30px; text-decoration:none; font-family:sans-serif;">
            قناة التلي
            <span style="width:24px; height:24px; background:#fff; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-left:8px;">
                <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:16px; height:16px; fill:#0088cc;">
                    <path d="M120 0C53.7 0 0 53.7 0 120s53.7 120 120 120 120-53.7 120-120S186.3 0 120 0zm58 84.6l-19.7 92.8c-1.5 6.7-5.5 8.4-11.1 5.2l-30.8-22.7-14.9 14.3c-1.7 1.7-3.1 3.1-6.4 3.1l2.3-32.5 59.1-53.3c2.6-2.3-.6-3.6-4-1.3l-72.8 45.7-31.4-9.8c-6.8-2.1-6.9-6.8 1.4-10.1l123.1-47.5c5.7-2.2 10.7 1.3 8.8 10z"/>
                </svg>
            </span>
        </a>
    </div>

    <div style="text-align:center; margin-top:15px; font-size:16px; color:#444;">
        اشتركوا بقناة التلي حتى توصلكم كل التحديثات أو المحاضرات اللي راح انزلها على الموقع إن شاء الله
    </div>
    ''', unsafe_allow_html=True)
