import streamlit as st
from orders1 import normalize_answer, import_module_from_file

def initialize_quiz_state(questions, lec_num, subject, selected_version):
    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lec_num) or \
       (st.session_state.get("current_subject", None) != subject) or \
       (st.session_state.get("current_version", None) != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lec_num
        st.session_state.current_subject = subject
        st.session_state.current_version = selected_version

def show_question(index, questions, Links):
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
            st.experimental_rerun()
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
            st.experimental_rerun()

    if Links:
        st.markdown("---")
        for link in Links:
            st.markdown(f"- [{link['title']}]({link['url']})")

def show_sidebar(questions):
    with st.sidebar:
        st.markdown(f"### 🧪 {st.session_state.current_subject.upper()}")

        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} Question {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

def quiz_interface(questions, Links):
    show_sidebar(questions)

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question, questions, Links)
    else:
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
            st.experimental_rerun()
