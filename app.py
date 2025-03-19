import streamlit as st
import pandas as pd

st.title("WIN Block Processor")

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df = df.drop(0)

    classes = [
        "6A", "6B", "6C", "6D", "6E", "6F", "6G", "6I", "6J",
        "7A", "7B", "7C", "7D", "7E", "7F", "7G", "7I",
        "7/8H", "7/8J",
        "8A", "8B", "8C", "8D", "8E", "8F", "8G", "8I"
    ]

    blocks = []
    for col in df.columns:
        for idx in df.index:
            student = df.loc[idx, col]
            if isinstance(student, str):
                print(student)
                student_name, student_class = student.split(" - ")
                sub_df = pd.DataFrame({"Class": [student_class], "Student": [student_name], "WIN Block": [col]})
                # sub_df.loc[student_class, "Student"] = student_name
                # sub_df.loc[student_class, "WIN Block"] = col
                blocks.append(sub_df)

    blocks = pd.concat(blocks)

    # Sort by class
    blocks = blocks.sort_values(
        by=['Class'], key=lambda x: x.map({classes[i]: i for i in range(len(classes))})
    )

    st.write("Processed Data Preview:")
    st.write(blocks.head())

    # Download processed file
    st.download_button(
        label="Download Processed CSV",
        data=blocks.to_csv(index=False).encode("utf-8"),
        file_name="processed_file.csv",
        mime="text/csv",
    )
