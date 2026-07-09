"""
=========================================================
SolarTwin AI

Image Utility Module

Common reusable image helper functions.

Author : SolarTwin AI
Version : 1.0
=========================================================
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
from io import BytesIO


# ----------------------------------------------------------
# Convert Streamlit UploadedFile to OpenCV image
# ----------------------------------------------------------

def uploaded_file_to_cv2(uploaded_file):

    file_bytes = np.asarray(
        bytearray(uploaded_file.getvalue()),
        dtype=np.uint8
    )

    image = cv2.imdecode(
        file_bytes,
        cv2.IMREAD_COLOR
    )

    return image


# ----------------------------------------------------------
# Convert CV2 to PIL
# ----------------------------------------------------------

def cv2_to_pil(image):

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    return Image.fromarray(rgb)


# ----------------------------------------------------------
# Convert PIL to CV2
# ----------------------------------------------------------

def pil_to_cv2(image):

    image = np.array(image)

    return cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )


# ----------------------------------------------------------
# Thumbnail
# ----------------------------------------------------------

def create_thumbnail(image, width=500):

    h, w = image.shape[:2]

    ratio = width / w

    new_height = int(h * ratio)

    return cv2.resize(
        image,
        (width, new_height)
    )


# ----------------------------------------------------------
# Get image size
# ----------------------------------------------------------

def get_image_size(image):

    h, w = image.shape[:2]

    return w, h


# ----------------------------------------------------------
# Calculate Area
# ----------------------------------------------------------

def calculate_rectangle_area(length, width):

    return round(length * width, 2)


# ----------------------------------------------------------
# Draw Polygon
# ----------------------------------------------------------

def draw_polygon(
        image,
        points,
        color=(0,255,0),
        thickness=2
):

    pts = np.array(
        points,
        np.int32
    )

    pts = pts.reshape(
        (-1,1,2)
    )

    output = image.copy()

    cv2.polylines(
        output,
        [pts],
        True,
        color,
        thickness
    )

    return output


# ----------------------------------------------------------
# Draw Bounding Box
# ----------------------------------------------------------

def draw_bbox(
        image,
        x1,
        y1,
        x2,
        y2,
        color=(255,0,0),
        thickness=2,
        label=""
):

    output = image.copy()

    cv2.rectangle(
        output,
        (x1,y1),
        (x2,y2),
        color,
        thickness
    )

    if label:

        cv2.putText(

            output,

            label,

            (x1,y1-8),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            color,

            2

        )

    return output


# ----------------------------------------------------------
# Draw Center Point
# ----------------------------------------------------------

def draw_center(image):

    output = image.copy()

    h,w = output.shape[:2]

    cx = w//2

    cy = h//2

    cv2.circle(

        output,

        (cx,cy),

        6,

        (0,0,255),

        -1

    )

    return output


# ----------------------------------------------------------
# Draw Grid
# ----------------------------------------------------------

def draw_grid(

        image,

        step=50,

        color=(220,220,220)

):

    output = image.copy()

    h,w = output.shape[:2]

    for x in range(0,w,step):

        cv2.line(

            output,

            (x,0),

            (x,h),

            color,

            1

        )

    for y in range(0,h,step):

        cv2.line(

            output,

            (0,y),

            (w,y),

            color,

            1

        )

    return output


# ----------------------------------------------------------
# Convert PIL image to bytes
# ----------------------------------------------------------

def pil_to_bytes(image):

    buffer = BytesIO()

    image.save(

        buffer,

        format="PNG"

    )

    return buffer.getvalue()


# ----------------------------------------------------------
# Image Information
# ----------------------------------------------------------

def image_information(image):

    h,w = image.shape[:2]

    channels = 1

    if len(image.shape)==3:

        channels=image.shape[2]

    return {

        "width":w,

        "height":h,

        "channels":channels,

        "pixels":w*h

    }


# ----------------------------------------------------------
# Resize while keeping aspect ratio
# ----------------------------------------------------------

def resize_keep_ratio(

        image,

        max_width=1200

):

    h,w = image.shape[:2]

    if w<=max_width:

        return image

    ratio=max_width/w

    new_h=int(h*ratio)

    return cv2.resize(

        image,

        (max_width,new_h)

    )


# ----------------------------------------------------------
# Blank Canvas
# ----------------------------------------------------------

def blank_canvas(

        width=1000,

        height=600,

        color=(255,255,255)

):

    canvas=np.zeros(

        (height,width,3),

        dtype=np.uint8

    )

    canvas[:]=color

    return canvas


# ----------------------------------------------------------
# Future Use
# ----------------------------------------------------------

def distance(p1,p2):

    return np.sqrt(

        (p1[0]-p2[0])**2 +

        (p1[1]-p2[1])**2

    )