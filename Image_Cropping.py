import streamlit as st
from streamlit_cropperjs import st_cropperjs
import fitz  # PyMuPDF
import tempfile
import os
from PIL import Image
from io import BytesIO

st.title("PDF Cropper")

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
        image_bytes = page.get_pixmap().tobytes()

        # Display the PDF page
        st.image(image_bytes, use_column_width=True, caption=f"Page {page_number}")

        # Use cropper to select and crop a part of the image only if the page number changes
        if st.button("Crop Image"):
            cropped_image = st_cropperjs(image_bytes, btn_text="Crop Image")

            # Display the cropped image
            if cropped_image is not None:
                st.write("Cropped Image:")
                st.image(cropped_image, use_column_width=True)

                # Convert PIL Image to bytes
                img_byte_array = BytesIO()
                cropped_image.save(img_byte_array, format="PNG")
                img_bytes = img_byte_array.getvalue()

                # Download the cropped image
                st.download_button("Download Cropped Image", img_bytes, file_name="cropped_image.png", mime="image/png")

    # Clean up the temporary file
    os.unlink(tmp_file_path)
else:
    st.write("Upload a PDF file using the file uploader above.")
