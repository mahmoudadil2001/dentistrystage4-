import streamlit as st

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

def show_question(index, questions):
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
        key=f"radio_{index}"
    )

    if not st.session_state.answer_shown[index]:
        if st.button("Answer", key=f"submit_{index}"):
            st.session_state.user_answers[index] = selected_answer
            st.session_state.answer_shown[index] = True
            st.rerun()
    else:
        user_ans = st.session_state.user_answers[index]
        if user_ans == correct_text:
            st.success("✅ Correct answer")
        else:
            st.error(f"❌ Correct answer: {correct_text}")
            if "explanation" in q:
                st.info(f"💡 Explanation: {q['explanation']}")

        if st.button("Next Question", key=f"next_{index}"):
            if index + 1 < len(questions):
                st.session_state.current_question += 1
            else:
                st.session_state.quiz_completed = True
            st.rerun()

def show_quiz_summary(questions):
    st.header("🎉 Quiz Completed!")
    correct = 0
    for i, q in enumerate(questions):
        correct_text = normalize_answer(q)
        user = st.session_state.user_answers[i]
        if user == correct_text:
            correct += 1
            st.write(f"Question {i+1}: ✅ Correct")
        else:
            st.write(f"Question {i+1}: ❌ Wrong (Your answer: {user}, Correct: {correct_text})")
    st.success(f"Score: {correct} out of {len(questions)}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.rerun()
