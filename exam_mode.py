import streamlit as st

def exam_mode_ui(questions, Links):
    if "in_exam_mode" not in st.session_state:
        st.session_state.in_exam_mode = False

    def toggle_exam_mode():
        st.session_state.in_exam_mode = not st.session_state.in_exam_mode
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.experimental_rerun()

    st.button(
        "🧪 " + ("خروج من وضع الاختبار" if st.session_state.in_exam_mode else "دخول وضع الاختبار"),
        on_click=toggle_exam_mode
    )

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

    if st.session_state.in_exam_mode:
        if not questions:
            st.warning("لا توجد أسئلة للعرض في وضع الاختبار.")
            return

        index = st.session_state.get("current_question", 0)

        q = questions[index]
        correct_text = normalize_answer(q)

        st.markdown(f"### سؤال {index + 1} من {len(questions)}:")
        st.write(q["question"])

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio(
            "اختر الإجابة الصحيحة:",
            q["options"],
            index=default_idx,
            key=f"radio_{index}"
        )

        if not st.session_state.answer_shown[index]:
            if st.button("عرض الإجابة", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.experimental_rerun()
        else:
            user_ans = st.session_state.user_answers[index]
            if user_ans == correct_text:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ الإجابة الصحيحة: {correct_text}")
                if "explanation" in q:
                    st.info(f"💡 شرح: {q['explanation']}")

            if st.button("السؤال التالي", key=f"next_{index}"):
                if index + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                    st.experimental_rerun()

        if Links:
            st.markdown("---")
            for link in Links:
                st.markdown(f"- [{link['title']}]({link['url']})")

    else:
        st.info("اضغط على زر 'دخول وضع الاختبار' للدخول إلى وضع الاختبار وإخفاء كل شيء آخر.")
