import streamlit as st
import fitz  # PyMuPDF

st.title("PDF Viewer")

pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
page_number = st.number_input("Enter the page number:", min_value=1, format="%d", value=1)

if pdf_file is not None:
    pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

    if page_number > len(pdf_document):
        st.error(f"Invalid page number. Maximum page number is {len(pdf_document)}.")
    else:
        page = pdf_document.load_page(page_number - 1)
        page_text = page.get_text()
        st.write(f"Page {page_number} of {len(pdf_document)}:")
        st.write(page_text)
else:
    st.write("Upload a PDF file using the file uploader above.")
