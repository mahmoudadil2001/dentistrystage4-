import streamlit as st
import pandas as pd

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ/export?format=csv&id=1ZUrFMmDcHMsDdVvyJ4Yxi2oE0drG2434OBsGD5jY9fQ&gid=0"

def main():
    st.title("معاينة ملف Google Sheets")

    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    st.write("أسماء الأعمدة الموجودة في ملف CSV:")
    st.write(df.columns.tolist())

    st.write("أول 5 صفوف من البيانات:")
    st.write(df.head())

if __name__ == "__main__":
    main()
