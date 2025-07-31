import streamlit as st

def exam_mode_ui(questions, Links):
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

    if "in_exam_mode" not in st.session_state:
        st.session_state.in_exam_mode = True  # هنا نضمن تفعيل الوضع عند الدخول لأول مرة

    # زر خروج أو دخول وضع الاختبار - سيتم التحكم فيه من orders.py، هنا نترك فقط العرض
    # لكن إذا أردنا عرض زر هنا (اختياري) يمكن إزالة هذا التعليق.

    index = st.session_state.current_question

    q = questions[index]
    correct_text = normalize_answer(q)

    current_q_num = index + 1
    total_qs = len(questions)
    st.markdown(f"### Question {current_q_num}/{total_qs}: {q['question']}")

    default_idx = 0
    if st.session_state.user_answers[index] in q["options"]:
        default_idx = q["options"].index(st.session_state.user_answers[index])

    selected_answer = st.radio(
        "",
        q["options"],
        index=default_idx,
        key=f"exam_radio_{index}"
    )

    if not st.session_state.answer_shown[index]:
        if st.button("Answer", key=f"exam_submit_{index}"):
            st.session_state.user_answers[index] = selected_answer
            st.session_state.answer_shown[index] = True
            st.experimental_rerun()
    else:
        user_ans = st.session_state.user_answers[index]
        if user_ans == correct_text:
            st.success("✅ Correct answer")
        else:
            st.error(f"❌ Correct answer: {correct_text}")
            if "explanation" in q:
                st.info(f"💡 Explanation: {q['explanation']}")

        if st.button("Next Question", key=f"exam_next_{index}"):
            if index + 1 < len(questions):
                st.session_state.current_question += 1
            else:
                st.session_state.quiz_completed = True
            st.experimental_rerun()

    if Links:
        st.markdown("---")
        for link in Links:
            st.markdown(f"- [{link['title']}]({link['url']})")
