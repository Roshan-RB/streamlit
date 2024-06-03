
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

st.set_page_config(layout="wide")




from streamlit_image_coordinates import streamlit_image_coordinates


try:
    # Check if the image is in session state
    if 'image_with_boxes' in st.session_state:
        # Retrieve the image from session state
        image_with_boxes = st.session_state.image_with_boxes

    else:
        st.write("No image found in session state.")

    scale_str = st.select_slider(
        "Select scaling factor to downsize the image",
        options=["1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "5.5", "6"])

    scale = float(scale_str)

    #st.write("My favorite color is", scale)
    if image_with_boxes is not None:

        width, height = image_with_boxes.size
        value = streamlit_image_coordinates(image_with_boxes) #width = (width/scale))



    
        

    def point_in_box(x,y,box,scale):
        p0,p1,p2,p3 = box
        min_x = min(p0[0], p1[0], p2[0], p3[0])#/scale
        max_x = max(p0[0], p1[0], p2[0], p3[0])#/scale
        min_y = min(p0[1], p1[1], p2[1], p3[1])#/scale
        max_y = max(p0[1], p1[1], p2[1], p3[1])#/scale
        return min_x <= x <= max_x and min_y <= y <= max_y

    #value = None   
    if value:
        #st.write(value)
        x,y = value["x"], value["y"]


    dimension = []
    if "bounds" in st.session_state:
        bounds = st.session_state.bounds

        # Initialize temp and dimension lists
        if "temp" not in st.session_state:
            st.session_state.temp = []

        if "dimension" not in st.session_state:
            st.session_state.dimension = []

        

        for bound in bounds :
            box = [bound[0][0], bound[0][1], bound[0][2], bound[0][3]]
            if value is not None:
                if point_in_box(x,y,box,scale):

                    text = bound[1]
                    if len(st.session_state.temp) < 3:
                        st.session_state.temp.append(text)
                
                # When we have two dimensions, add the pair to the main list
                if len(st.session_state.temp) == 2:
                    st.session_state.dimension.append(st.session_state.temp[:])
                    st.session_state.temp = []


                    st.write('You have selected the text    : ', text)
        
                  
        else:
            st.warning('Click on the required dimension to select')

        # Output the final dimension list and convert to DataFrame
        if st.session_state.dimension:
            #st.write('Selected dimension pairs: ', st.session_state.dimension)
            df = pd.DataFrame(st.session_state.dimension, columns=['Width', 'Height'])
            #st.write('DataFrame of Selected Dimensions:')
            st.data_editor(df)

except Exception as e:
    print(e)

    st.warning('Please select extract in the main page to detect the text, then come back here to select the required dimension text!')
