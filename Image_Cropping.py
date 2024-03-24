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

            try:
                # Save the cropped image data to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img_file:
                    tmp_img_file.write(cropped_image)

                # Open the temporary image file using PIL
                pil_image = Image.open(tmp_img_file.name)

                # Display the cropped image
                st.write("Cropped Image:")
                st.image(pil_image, use_column_width=True)

                # Provide download button for the cropped image
                img_bytes = tmp_img_file.read()
                st.download_button("Download Cropped Image", img_bytes, file_name="cropped_image.png", mime="image/png")

            except Exception as e:
                st.error(f"Error: {e}")

            finally:
                # Clean up the temporary image file
                os.unlink(tmp_img_file.name)

    # Clean up the temporary PDF file
    os.unlink(tmp_file_path)
else:
    st.write("Upload a PDF file using the file uploader above.")
