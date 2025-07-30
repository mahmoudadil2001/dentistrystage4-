# orders.py

import streamlit as st
from orders1 import load_and_select_subject_lecture_version
from orders2 import show_question_block
from orders3 import show_quiz_results_block

def main():
    # تحميل الأسئلة والبيانات من orders1
    questions, Links, subject, lec_num, selected_version = load_and_select_subject_lecture_version()

    if questions is None:
        # في حال لم يتم تحميل أسئلة أو حدث خطأ، خروج مبكر
        return

    # تهيئة state للجلسة إن لم تكن موجودة
    if ("questions_count" not in st.session_state or
        st.session_state.questions_count != len(questions) or
        st.session_state.get("current_lecture") != lec_num or
        st.session_state.get("current_subject") != subject or
        st.session_state.get("current_version") != selected_version):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lec_num
        st.session_state.current_subject = subject
        st.session_state.current_version = selected_version

    # إذا لم ينتهي الاختبار، عرض السؤال الحالي
    if not st.session_state.quiz_completed:
        show_question_block(questions, Links, st.session_state.current_question)
    else:
        # عرض نتائج الاختبار بعد الانتهاء
        show_quiz_results_block(questions, st.session_state.user_answers)

