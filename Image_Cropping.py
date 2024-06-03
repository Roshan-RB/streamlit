import streamlit as st
from streamlit_cropperjs import st_cropperjs
from streamlit_image_coordinates import streamlit_image_coordinates
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
import cv2
import time
import base64
import io




fa_css = '''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<i class="fa-solid fa-bars";></i>
''' 
st.write(fa_css, unsafe_allow_html=True)


reader = easyocr.Reader(['en'])

st.title("Dimension Detection!")
# Initialize session state variables
if 'pdf_file' not in st.session_state:
    st.session_state.pdf_file = None
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'image_with_boxes' not in st.session_state:
    st.session_state.image_with_boxes = None
if 'bounds' not in st.session_state:
    st.session_state.bounds = None
if 'cropped_image' not in st.session_state:
    st.session_state.cropped_image = None
if 'Processed_image' not in st.session_state:
    st.session_state.Processed_image = None
if 'crop_button_clicked' not in st.session_state:
    st.session_state.crop_button_clicked = False
if 'pil_image' not in st.session_state:
    st.session_state.pil_image = None
if 'tmp_file_path' not in st.session_state:
    st.session_state.tmp_file_path = None
if 'pdf_document' not in st.session_state:
    st.session_state.pdf_document  = None

pdf_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
page_number = st.sidebar.number_input("Enter the page number:", min_value=1, format="%d", value=1)

if pdf_file:
    st.session_state.pdf_file = pdf_file

if st.session_state.pdf_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(st.session_state.pdf_file.read())
        tmp_file_path = tmp_file.name
    st.session_state.tmp_file_path = tmp_file_path
    try:
        pdf_document = fitz.open(st.session_state.tmp_file_path)
        st.session_state.pdf_document  = pdf_document

        if page_number > len(st.session_state.pdf_document):
            st.error(f"Invalid page number. Maximum page number is {len(st.session_state.pdf_document)}.")
        else:
            st.session_state.page_number = page_number
            page = st.session_state.pdf_document.load_page(st.session_state.page_number - 1)

            image_bytes = page.get_pixmap().tobytes()
            st.session_state.image_bytes = image_bytes

            # Display the PDF page
            st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**PDF**</span>', unsafe_allow_html=True)
            st.image(st.session_state.image_bytes, use_column_width=True, caption=f"Page {page_number}")

            # Use cropper to select and crop a part of the image only if the page number changes
            if st.button("Select area to crop"):
                st.session_state.crop_button_clicked = True
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.pdf_file = None  # Clear the uploaded PDF file

    if st.session_state.crop_button_clicked:
        cropped_image = st_cropperjs(st.session_state.image_bytes, btn_text="Crop Image")

        if cropped_image:
            st.session_state.cropped_image = cropped_image
            with st.spinner("Loading the cropped image..."):
                time.sleep(5)
            st.success("You can extract the text now !")
            try:
                # Convert cropped image to PIL Image
                pil_image = Image.open(BytesIO(st.session_state.cropped_image))
                st.session_state.pil_image = pil_image

                # Display the cropped image
                st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**Cropped Image**</span>', unsafe_allow_html=True)
                st.image(st.session_state.pil_image, use_column_width='auto')
                width, height = st.session_state.pil_image.size
                st.write("Image Size (Width x Height):", width, "x", height)

                 

                # Save the cropped image as a PNG file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img_file:
                    st.session_state.pil_image.save(tmp_img_file.name)

                    # Read the cropped image back as bytes
                    with open(tmp_img_file.name, "rb") as img_file:
                        img_bytes = img_file.read()

                    # Provide download button for the cropped image
                    st.download_button("Download Cropped Image", img_bytes, file_name="cropped_image.png", mime="image/png")

            except Exception as e:
                st.error(f"Error: {e}")


    #if st.session_state.pdf_file:
        #try:
            #st.session_state.pdf_document.close()  # Close the PDF document
            #os.unlink(tmp_file_path)  # Clean up the temporary file
        #except Exception as e:
            #st.error(f"Error during cleanup: {e}")

else:
    st.write("Upload a PDF file using the file uploader above.")




if st.session_state.pil_image:

    

    def rotate_image(im, angle):
        return im.rotate(angle, expand=True)
    
    
    image_np = np.array(st.session_state.pil_image)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    #st.image( gray, caption='grayscale_image', use_column_width='never')

    # Get the dimensions of the grayscale image
    height, width = gray.shape[:2]

    # Calculate the new width and height by multiplying current dimensions by 2
    new_width = width * 2
    new_height = height * 2

    # Resize the grayscale image
    resized_gray = cv2.resize(gray, (new_width, new_height))

    # Convert NumPy array back to PIL Image
    Processed_Image = Image.fromarray(resized_gray)
    st.write('')
    #st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**Processed Image**</span>', unsafe_allow_html=True)
    #st.image(Processed_Image, use_column_width='auto')

    n_width, n_height = Processed_Image.size
    st.write("Image Size (Width x Height):", n_width, "x", n_height)


    rotated_image = rotate_image(Processed_Image, -90)
    st.write('')
    #st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**Rotated Image**</span>', unsafe_allow_html=True)
    #st.image(rotated_image, use_column_width='auto')



     # Convert PIL Image to JPEG format
    img_byte_arr = BytesIO()
    Processed_Image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Convert PIL Image to JPEG format
    img_byte_arr_ro = BytesIO()
    rotated_image.save(img_byte_arr_ro, format='PNG')
    img_byte_arr_ro = img_byte_arr_ro.getvalue()
    rotation_list = [180, 270]


    # Doing OCR. Get bounding boxes.
    bounds = reader.readtext(img_byte_arr, rotation_info = rotation_list, allowlist = '0123456789')
    if bounds not in st.session_state:
        st.session_state.bounds = bounds
    #st.write(st.session_state)
    #st.write(bounds[0][0])
    #for bound in bounds:
        #st.write(bound)
        #st.write(bound[0][:4])
    rotated_bounds = reader.readtext(img_byte_arr_ro)
    #bounds

    # Draw bounding boxes
    def draw_boxes(image, bounds, color='red', width=2):
        rgb_image = Image.new('RGB', image.size)
        rgb_image.paste(image)
        draw = ImageDraw.Draw(rgb_image)
        for bound in bounds:
            p0, p1, p2, p3 = bound[0]
            draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
        return rgb_image

    
    #st.write(st.session_state)
    
        
    #extract_text = st.button(label= 'Extract Text')
    

    if st.button('Extract_text'):
        st.markdown(f'<i class="fa-solid fa-cube" style="margin-right: 10px; font-size: 20px;"></i> <span style="font-size: 24px; color: #3573b3;">**OCR**</span>', unsafe_allow_html=True)
        with st.spinner('Extracting text...'):
            time.sleep(8)

        image_with_boxes = draw_boxes(Processed_Image.copy(), bounds)
        print(image_with_boxes.size)
        st.session_state.image_with_boxes = image_with_boxes
        rotated_image_with_boxes = draw_boxes(rotated_image.copy(), rotated_bounds)

        st.write('')
        st.write('Cropped Image with OCR Bounding_Boxes')
        if 'image_with_boxes' in st.session_state:
            st.image(st.session_state.image_with_boxes, use_column_width= 'auto')

        st.write('')
        st.write('Rotated Image with OCR Bounding_Boxes')
        #st.image(rotated_image_with_boxes, use_column_width= "auto")


        

        #To get the text from the bounding boxes
        result = reader.readtext(img_byte_arr)
        text = [entry[1] for entry in result]
        

        
        ocr_data = []
        for idx, tex in enumerate(text):
            ocr_data.append((idx + 1, tex))

        ocr_df = pd.DataFrame(ocr_data, columns=None)
        st.write('Extracted text:')
        
        


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
        im_with_horiz_boxes = draw_boxes(Processed_Image.copy(), horizontal_text, color='green')
        st.image(im_with_horiz_boxes, use_column_width=None)

    if vert_text:
        # Draw bounding boxes for vertical text
        im_with_vert_boxes = draw_boxes(Processed_Image.copy(), vertical_text, color='blue')
        st.image(im_with_vert_boxes, use_column_width=None)


    #-----------------------------------------------------------------------------------------------------------
    #st.write(st.session_state)
    

   


