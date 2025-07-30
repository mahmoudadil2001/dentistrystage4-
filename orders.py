import streamlit as st
from orders1 import load_and_select_subject_lecture_version
from orders2 import normalize_answer, show_question, show_quiz_summary
from orders3 import add_sidebar_navigation

def main():
    # تحميل الأسئلة والمحاضرات والإصدارات
    subject, lec_num, selected_version, data = load_and_select_subject_lecture_version()

    if subject is None:
        return  # خطأ أو لا توجد بيانات

    questions, Links = data

    # إعادة تهيئة الحالة عند تغير المحاضرة أو الموضوع أو النسخة
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

    add_sidebar_navigation(subject, questions)

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question, questions)
    else:
        show_quiz_summary(questions)

    # عرض الروابط الإضافية
    if Links:
        st.markdown("---")
        for link in Links:
            st.markdown(f"- [{link['title']}]({link['url']})")
