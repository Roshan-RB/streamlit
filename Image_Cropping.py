import streamlit as st
from streamlit_cropperjs import st_cropperjs
import fitz  # PyMuPDF
import tempfile
import os
import PIL
from PIL import Image
from io import BytesIO
from PIL import ImageDraw
import numpy as np
import easyocr
import pandas as pd

fa_css = '''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<i class="fa-solid fa-bars";></i>
''' 
st.write(fa_css, unsafe_allow_html=True)


reader = easyocr.Reader(['en'])

st.title("Dimension Detection!")

# Initialize session state
if 'crop_button_clicked' not in st.session_state:
    st.session_state.crop_button_clicked = False

pdf_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
page_number = st.sidebar.number_input("Enter the page number:", min_value=1, format="%d", value=1)

img_bytes = None
pil_image = None 

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
        st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**PDF**</span>', unsafe_allow_html=True)
        st.image(image_bytes, use_column_width=True, caption=f"Page {page_number}")

        # Use cropper to select and crop a part of the image only if the page number changes
        if st.button("Select area to crop"):
            st.session_state.crop_button_clicked = True

    if st.session_state.crop_button_clicked:
        cropped_image = st_cropperjs(image_bytes, btn_text="Crop Image")

        if cropped_image is not None:
            try:
                # Convert cropped image to PIL Image
                pil_image = Image.open(BytesIO(cropped_image))

                # Display the cropped image
                #st.write("Cropped Image:")
                st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**Cropped Image**</span>', unsafe_allow_html=True)
                st.image(pil_image, use_column_width=True)

                # Save the cropped image as a PNG file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img_file:
                    pil_image.save(tmp_img_file.name)

                    # Read the cropped image back as bytes
                    with open(tmp_img_file.name, "rb") as img_file:
                        img_bytes = img_file.read()

                    # Provide download button for the cropped image
                    st.download_button("Download Cropped Image", img_bytes, file_name="cropped_image.png", mime="image/png")

            except Exception as e:
                st.error(f"Error: {e}")


    # Close the PDF document
    pdf_document.close()

    # Clean up the temporary files
    os.unlink(tmp_file_path)

else:
    st.write("Upload a PDF file using the file uploader above.")

if pil_image is not None:

    def rotate_image(im, angle):
        return im.rotate(angle, expand=True)
    
    rotated_image = rotate_image(pil_image, -90)


     # Convert PIL Image to JPEG format
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Convert PIL Image to JPEG format
    img_byte_arr_ro = BytesIO()
    rotated_image.save(img_byte_arr_ro, format='PNG')
    img_byte_arr_ro = img_byte_arr_ro.getvalue()


    #st.image(img_bytes, use_column_width=True)
    # Doing OCR. Get bounding boxes.
    bounds = reader.readtext(img_byte_arr)
    rotated_bounds = reader.readtext(img_byte_arr_ro)
    #bounds

    # Draw bounding boxes
    def draw_boxes(image, bounds, color='red', width=2):
        draw = ImageDraw.Draw(image)
        for bound in bounds:
            p0, p1, p2, p3 = bound[0]
            draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
        return image

    #draw_boxes(im, bounds)

    
    st.write('')
    st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**Rotated Image**</span>', unsafe_allow_html=True)
    st.image(rotated_image, use_column_width=True)


    #im = PIL.Image.open(pil_image)


    st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**OCR**</span>', unsafe_allow_html=True)

    image_with_boxes = draw_boxes(pil_image.copy(), bounds)
    rotated_image_with_boxes = draw_boxes(rotated_image.copy(), rotated_bounds)
    st.write('')
    st.write('Cropped Image with OCR Bounding_Boxes')
    st.image(image_with_boxes, use_column_width= "never")

    st.write('')
    st.write('Rotated Image with OCR Bounding_Boxes')
    st.image(rotated_image_with_boxes, use_column_width= "never")



    #To get the text from the bounding boxes
    result = reader.readtext(img_byte_arr)
    text = [entry[1] for entry in result]
    

    
    ocr_data = []
    for idx, tex in enumerate(text):
        ocr_data.append((idx + 1, tex))

    ocr_df = pd.DataFrame(ocr_data, columns=None)
    st.write('Extracted text:')
    st.dataframe(ocr_data, width = 200)

#---------------------------------------------------------------------------------------------------------

# Define a function to classify text based on aspect ratio
def classify_text(bounds, threshold=1.5):
    vertical_text = []
    horizontal_text = []
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        # Calculate width and height of bounding box
        width = ((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)**0.5
        height = ((p3[0] - p0[0])**2 + (p3[1] - p0[1])**2)**0.5
        # Calculate aspect ratio
        aspect_ratio = height / width
        # Classify based on aspect ratio
        if aspect_ratio > threshold:
            vertical_text.append(bound)
        else:
            horizontal_text.append(bound)
    return vertical_text, horizontal_text

# Classify text into vertical and horizontal categories
vertical_text, horizontal_text = classify_text(bounds)

col1, col2 = st.columns(2, gap="small")
with col1:
    horiz_text = st.button('Get only Horizontal text')

with col2:
    vert_text = st.button('Get only Vertical text')

if horiz_text:
    # Draw bounding boxes for vertical text
    im_with_horiz_boxes = draw_boxes(pil_image.copy(), horizontal_text, color='green')
    st.image(im_with_horiz_boxes, use_column_width='never')

if vert_text:
    # Draw bounding boxes for vertical text
    im_with_vert_boxes = draw_boxes(pil_image.copy(), vertical_text, color='blue')
    st.image(im_with_vert_boxes, use_column_width=None)




