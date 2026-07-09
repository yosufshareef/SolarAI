"""
=========================================================
SolarTwin AI

Photo Upload Module

Enterprise Image Upload & Validation

Author : SolarTwin AI
=========================================================
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from ai.roof_detector import RoofDetector
from ai.object_detector import ObjectDetector
from services.geometry_engine import GeometryEngine


from ai.image_validator import (
    ImageValidator,
    quality_badge
)

from utils.image_utils import (
    uploaded_file_to_cv2,
    cv2_to_pil,
    image_information
)


# -----------------------------------------------------
# Image Validation Card
# -----------------------------------------------------

def validation_card(result):

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Quality Score",
            f"{result.quality_score}%"
        )

        st.metric(
            "Blur Score",
            result.blur_score
        )

        st.metric(
            "Brightness",
            result.brightness
        )

    with c2:

        st.metric(
            "Resolution",
            f"{result.resolution[0]} x {result.resolution[1]}"
        )

        st.metric(
            "Contrast",
            result.contrast
        )

        st.metric(
            "File Size",
            f"{result.file_size_mb:.2f} MB"
        )

    st.success(
        quality_badge(
            result.quality_score
        )
    )

    if result.is_valid:

        st.success("Image passed validation.")

    else:

        st.error("Image failed validation.")

    if result.messages:

        st.subheader("Recommendations")

        for msg in result.messages:

            st.write("•", msg)


# -----------------------------------------------------
# Image Preview
# -----------------------------------------------------

def preview_image(cv_image):

    pil = cv2_to_pil(cv_image)

    st.image(

        pil,

        use_container_width=True

    )


# -----------------------------------------------------
# Upload Section
# -----------------------------------------------------

def upload_section():

    uploaded = st.file_uploader(

        "Upload Roof Images",

        type=["jpg", "jpeg", "png"],

        accept_multiple_files=True

    )

    return uploaded


# -----------------------------------------------------
# Main Page
# -----------------------------------------------------

def show_photo_upload():

    st.title("📸 Photo Upload")

    st.caption(
        "Upload one or two rooftop images for AI analysis."
    )

    st.divider()

    uploaded_files = upload_section()

    if not uploaded_files:

        st.info(
            "Upload at least one rooftop image."
        )

        return

    if len(uploaded_files) > 2:

        st.warning(
            "Maximum two images allowed."
        )

        return

    image_results = []

    image_objects = []

    st.divider()

    for index, uploaded in enumerate(uploaded_files):

        st.subheader(
            f"Image {index+1}"
        )

        cv_image = uploaded_file_to_cv2(uploaded)

        if cv_image is None:

            st.error(
                "Unable to load image."
            )

            continue

        preview_image(cv_image)

        file_size = uploaded.size / (1024 * 1024)

        result = ImageValidator.validate(

            cv_image,

            file_size

        )

        validation_card(result)

        info = image_information(cv_image)

        image_results.append(result)

        image_objects.append(
            {
                "image": cv_image,
                "info": info,
                "validation": result
            }
        )

        st.divider()

    # ------------------------------------
    # Summary
    # ------------------------------------

    st.header("Validation Summary")

    table = []

    for idx, obj in enumerate(image_objects):

        r = obj["validation"]

        table.append({

            "Image": idx + 1,

            "Quality": r.quality_score,

            "Status": "PASS" if r.is_valid else "FAIL",

            "Resolution":
                f"{r.resolution[0]} x {r.resolution[1]}",

            "Blur": r.blur_score

        })

    df = pd.DataFrame(table)

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )

    # ------------------------------------
    # Check overall validity
    # ------------------------------------

    valid_images = [

        x

        for x in image_objects

        if x["validation"].is_valid

    ]

    if len(valid_images) == 0:

        st.error(

            "No valid images available."

        )

        return

    st.success(

        f"{len(valid_images)} valid image(s) ready for AI processing."

    )

    # ------------------------------------
    # Save into session
    # ------------------------------------

    if "project" not in st.session_state:

        st.session_state.project = {}

    st.session_state.project["uploaded_images"] = valid_images

    st.success(

        "Images stored successfully."

    )

    st.divider()

    st.subheader("Next Step")

    st.info(

        """
The next milestone will automatically:

✔ Detect roof boundary

✔ Detect obstacles

✔ Estimate usable roof area

✔ Prepare editable polygon

"""
    )

    col1, col2, col3 = st.columns(3)

    with col2:

        if st.button(

            "🚀 Run AI Detection",

            use_container_width=True

        ):

            image = valid_images[0]["image"]

            # -------------------------------
            # Roof Detection
            # -------------------------------

            with st.spinner("Detecting roof..."):

                roof_result = RoofDetector().detect(image)

            st.image(

                cv2_to_pil(roof_result.overlay),

                caption="Detected Roof",

                use_container_width=True

            )

            st.info(roof_result.message)

            if roof_result.success:

                st.session_state.project["roof_polygon"] = (

                    roof_result.suggested_polygon

                )

                geometry = GeometryEngine()

                roof_info = geometry.roof_summary(

                    roof_result.suggested_polygon

                )

                st.session_state.project["roof_info"] = roof_info

                st.success(

                    "Roof detected successfully."

                )

            else:

                st.warning(

                    "Automatic roof detection failed. You can continue with the Polygon Editor."

                )

            # -------------------------------
            # Obstacle Detection
            # -------------------------------

            with st.spinner("Detecting obstacles..."):

                annotated, detections = ObjectDetector().detect(image)

            st.image(

                cv2_to_pil(annotated),

                caption="Detected Obstacles",

                use_container_width=True

            )

            st.session_state.project["obstacles"] = detections

            st.success(

                f"{len(detections)} obstacle(s) detected."

            )

            st.info(

                "Next → Open 🟩 Polygon Editor to verify or edit the detected roof boundary."

            )