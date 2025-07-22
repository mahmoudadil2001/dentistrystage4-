import streamlit as st
from orders import main as orders_main

def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def main():
    load_css("styles.css")  # make sure styles.css is in the same folder as run.py
    orders_main()

if __name__ == "__main__":
    main()
