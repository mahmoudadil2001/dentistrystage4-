import streamlit as st

def exam_mode_ui(questions, Links):
    st.title("🎯 وضع الاختبار")

    if "exam_question_index" not in st.session_state:
        st.session_state.exam_question_index = 0
        st.session_state.exam_answers = [None] * len(questions)
        st.session_state.exam_finished = False

    index = st.session_state.exam_question_index
    q = questions[index]

    st.markdown(f"### السؤال {index + 1} من {len(questions)}")
    st.write(q['question'])

    selected = st.radio("اختر الإجابة", q["options"], key=f"exam_radio_{index}")

    if st.button("تأكيد الإجابة"):
        st.session_state.exam_answers[index] = selected
        if index + 1 < len(questions):
            st.session_state.exam_question_index += 1
        else:
            st.session_state.exam_finished = True
        st.experimental_rerun()

    if st.session_state.exam_finished:
        st.success("🎉 انتهى الاختبار!")

        correct_count = 0
        for i, q in enumerate(questions):
            ans = q.get("answer") or q.get("correct_answer")
            correct = q["options"][ans] if isinstance(ans, int) else ans
            if st.session_state.exam_answers[i] == correct:
                correct_count += 1

        st.write(f"✅ الدرجة: {correct_count} من {len(questions)}")

        if st.button("خروج من وضع الاختبار"):
            st.session_state.exam_mode = False
            del st.session_state.exam_question_index
            del st.session_state.exam_answers
            del st.session_state.exam_finished
            st.experimental_rerun()

    if Links:
        st.markdown("---")
        for link in Links:
            st.markdown(f"- [{link['title']}]({link['url']})")
