import streamlit as st
import fitz  # PyMuPDF
import tempfile
import os

st.title("PDF Viewer")

pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
page_number = st.number_input("Enter the page number:", min_value=1, format="%d", value=1)

if pdf_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_file_path = tmp_file.name

    pdf_document = fitz.open(tmp_file_path)

    if page_number > len(pdf_document):
        st.error(f"Invalid page number. Maximum page number is {len(pdf_document)}.")
    else:
        page = pdf_document.load_page(page_number - 1)
        page_text = page.get_text()
        st.write(f"Page {page_number} of {len(pdf_document)}:")
        st.write(page_text)

    # Clean up the temporary file
    os.unlink(tmp_file_path)
else:
    st.write("Upload a PDF file using the file uploader above.")
