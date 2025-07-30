import streamlit as st
from orders2 import normalize_answer   # أضف هذا السطر

def add_sidebar_navigation(subject, questions):
    st.sidebar.markdown(f"### 🧪 {subject.upper()}")
    for i in range(len(questions)):
        correct_text = normalize_answer(questions[i])
        user_ans = st.session_state.user_answers[i]
        if user_ans is None:
            status = "⬜"
        elif user_ans == correct_text:
            status = "✅"
        else:
            status = "❌"

        if st.sidebar.button(f"{status} Question {i+1}", key=f"nav_{i}"):
            st.session_state.current_question = i
            st.rerun()
