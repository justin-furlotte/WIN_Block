import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def dataframe_to_pdf(df):
    buffer = BytesIO()  # Create an in-memory buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Convert DataFrame to list format (including headers)
    data = [df.columns.tolist()] + df.values.tolist()

    # Create the table
    table = Table(data)

    # Apply table styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Add table to elements list
    elements.append(table)

    # Build the PDF
    doc.build(elements)

    buffer.seek(0)  # Move to the start of the buffer
    return buffer


# Function to create a ZIP file with multiple PDFs
def create_zip_with_pdfs(pdf_buffers, filenames):
    zip_buffer = BytesIO()  # Create ZIP in memory
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pdf_buffer, filename in zip(pdf_buffers, filenames):
            zipf.writestr(filename, pdf_buffer.getvalue())  # Write each PDF to ZIP

    zip_buffer.seek(0)  # Reset ZIP buffer position
    return zip_buffer


st.title("WIN Block Processor")

uploaded_file = st.file_uploader("Upload a CSV file (if using Excel, save as CSV UTF-8)", type="csv")

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
                try:
                    student = student.replace('\xa0', ' ')
                    student_name, student_class = student.split(" - ")
                    sub_df = pd.DataFrame({"Class": [student_class], "Student": [student_name], "WIN Block": [col]})
                    blocks.append(sub_df)
                except Exception as e:
                    message = (f"PROCESSING FAILED AT:\n\n"
                               f"ROW: {idx}\n\n"
                               f"COLUMN: {col}\n\n"
                               f"The contents of this cell are: '{student}'\n\n"
                               f"Please verify there is a space, a dash, "
                               f"and a space, e.g. ' - ', separating the student and home room.")
                    st.write(f"{message}\n\nError: {e}")
                    raise ValueError(e)

    blocks = pd.concat(blocks)

    # Sort by class
    blocks = blocks.sort_values(
        by=['Class'], key=lambda x: x.map({classes[i]: i for i in range(len(classes))})
    )

    pdf_buffers = []
    for cls in classes:
        class_df = blocks.loc[blocks["Class"] == cls]
        class_df = class_df.sort_values(by="Student", ascending=True)
        pdf = dataframe_to_pdf(class_df)
        pdf_buffers.append(pdf)

    # PDF file names - replace slashes with dashes so it doesn't create directories
    filenames = [f"{cls.replace("/", "-")}.pdf" for cls in classes]

    zip_buffer = create_zip_with_pdfs(pdf_buffers=pdf_buffers, filenames=filenames)

    st.write("Processed Data Preview:")
    st.write(blocks.head())

    # Download processed files
    st.download_button(
        label="Download All PDFs as ZIP",
        data=zip_buffer,
        file_name="win_blocks_sorted_by_home_room.zip",
        mime="application/zip",
    )
