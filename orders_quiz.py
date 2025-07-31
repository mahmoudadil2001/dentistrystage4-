import streamlit as st
from orders_loader import import_module_from_file
from orders_selection import select_subject, select_lecture

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

def orders_o():
    # زر الدخول والخروج من وضع الاختبار
    if "in_quiz_mode" not in st.session_state:
        st.session_state.in_quiz_mode = False

    if st.session_state.in_quiz_mode:
        if st.button("🔙 خروج من وضع الاختبار"):
            st.session_state.in_quiz_mode = False
            st.rerun()
    else:
        if st.button("▶️ دخول وضع الاختبار"):
            st.session_state.in_quiz_mode = True
            st.rerun()

    # إذا في وضع الاختبار نعرض فقط السؤال الحالي مع خياراته وإخفاء كل شيء آخر
    if st.session_state.in_quiz_mode:
        # نستخدم بيانات الحالة الجارية (المادة، الملف)
        filename = st.session_state.get("current_lecture")
        subject = st.session_state.get("current_subject")
        if not filename or not subject:
            st.error("⚠️ الرجاء اختيار المحاضرة والنسخة أولاً في الوضع العادي.")
            return

        file_path = f"{subject}/{filename}"
        questions_module = import_module_from_file(file_path)

        if questions_module is None:
            st.error(f"⚠️ ملف {filename} غير موجود أو لا يمكن تحميله.")
            return

        questions = getattr(questions_module, "questions", [])
        Links = getattr(questions_module, "Links", [])

        def show_question(index):
            q = questions[index]
            correct_text = normalize_answer(q)
            current_q_num = index + 1
            total_qs = len(questions)
            st.markdown(f"### سؤال {current_q_num} من {total_qs}: {q['question']}")

            default_idx = 0
            if st.session_state.user_answers[index] in q["options"]:
                default_idx = q["options"].index(st.session_state.user_answers[index])

            selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")

            if not st.session_state.answer_shown[index]:
                if st.button("إظهار الإجابة", key=f"submit_{index}"):
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
                        st.info(f"💡 توضيح: {q['explanation']}")

                if st.button("السؤال التالي", key=f"next_{index}"):
                    if index + 1 < len(questions):
                        st.session_state.current_question += 1
                    else:
                        st.session_state.quiz_completed = True
                    st.rerun()

            if Links:
                st.markdown("---")
                for link in Links:
                    st.markdown(f"- [{link['title']}]({link['url']})")

        # تحضير حالة الأسئلة عند الدخول لوضع الاختبار لأول مرة
        if ("questions_count" not in st.session_state) or \
           (st.session_state.questions_count != len(questions)) or \
           (st.session_state.get("current_lecture", None) != filename) or \
           (st.session_state.get("current_subject", None) != subject):

            st.session_state.questions_count = len(questions)
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.session_state.current_lecture = filename
            st.session_state.current_subject = subject

        if not st.session_state.quiz_completed:
            show_question(st.session_state.current_question)
        else:
            st.header("🎉 انتهى الاختبار!")
            correct = 0
            for i, q in enumerate(questions):
                correct_text = normalize_answer(q)
                user = st.session_state.user_answers[i]
                if user == correct_text:
                    correct += 1
                    st.write(f"السؤال {i+1}: ✅ صحيح")
                else:
                    st.write(f"السؤال {i+1}: ❌ خطأ (إجابتك: {user}, الصحيحة: {correct_text})")
            st.success(f"النتيجة: {correct} من {len(questions)}")

            if st.button("🔁 إعادة الاختبار"):
                st.session_state.current_question = 0
                st.session_state.user_answers = [None] * len(questions)
                st.session_state.answer_shown = [False] * len(questions)
                st.session_state.quiz_completed = False
                st.rerun()

    else:
        # الوضع العادي: اختيار المادة، المحاضرة، النسخة، ثم عرض السؤال بشكل كامل مع الشريط الجانبي
        filename, subject = select_lecture(select_subject())
        if filename is None or subject is None:
            return

        file_path = f"{subject}/{filename}"
        questions_module = import_module_from_file(file_path)

        if questions_module is None:
            st.error(f"⚠️ ملف {filename} غير موجود أو لا يمكن تحميله.")
            return

        questions = getattr(questions_module, "questions", [])
        Links = getattr(questions_module, "Links", [])

        if ("questions_count" not in st.session_state) or \
           (st.session_state.questions_count != len(questions)) or \
           (st.session_state.get("current_lecture", None) != filename) or \
           (st.session_state.get("current_subject", None) != subject):

            st.session_state.questions_count = len(questions)
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.session_state.current_lecture = filename
            st.session_state.current_subject = subject

        with st.sidebar:
            st.markdown(f"### 🧪 {subject.upper()}")

            for i in range(len(questions)):
                correct_text = normalize_answer(questions[i])
                user_ans = st.session_state.user_answers[i]
                status = "⬜" if user_ans is None else ("✅" if user_ans == correct_text else "❌")
                if st.button(f"{status} سؤال {i+1}", key=f"nav_{i}"):
                    st.session_state.current_question = i

        def show_question(index):
            q = questions[index]
            correct_text = normalize_answer(q)
            current_q_num = index + 1
            total_qs = len(questions)
            st.markdown(f"### سؤال {current_q_num} من {total_qs}: {q['question']}")

            default_idx = 0
            if st.session_state.user_answers[index] in q["options"]:
                default_idx = q["options"].index(st.session_state.user_answers[index])

            selected_answer = st.radio("", q["options"], index=default_idx, key=f"radio_{index}")

            if not st.session_state.answer_shown[index]:
                if st.button("إظهار الإجابة", key=f"submit_{index}"):
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
                        st.info(f"💡 توضيح: {q['explanation']}")

                if st.button("السؤال التالي", key=f"next_{index}"):
                    if index + 1 < len(questions):
                        st.session_state.current_question += 1
                    else:
                        st.session_state.quiz_completed = True
                    st.rerun()

            if Links:
                st.markdown("---")
                for link in Links:
                    st.markdown(f"- [{link['title']}]({link['url']})")

        if not st.session_state.quiz_completed:
            show_question(st.session_state.current_question)
        else:
            st.header("🎉 انتهى الاختبار!")
            correct = 0
            for i, q in enumerate(questions):
                correct_text = normalize_answer(q)
                user = st.session_state.user_answers[i]
                if user == correct_text:
                    correct += 1
                    st.write(f"السؤال {i+1}: ✅ صحيح")
                else:
                    st.write(f"السؤال {i+1}: ❌ خطأ (إجابتك: {user}, الصحيحة: {correct_text})")
            st.success(f"النتيجة: {correct} من {len(questions)}")

            if st.button("🔁 إعادة الاختبار"):
                st.session_state.current_question = 0
                st.session_state.user_answers = [None] * len(questions)
                st.session_state.answer_shown = [False] * len(questions)
                st.session_state.quiz_completed = False
                st.rerun()
