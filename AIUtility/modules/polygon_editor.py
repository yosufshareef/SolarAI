"""
=========================================================
SolarTwin AI

Polygon Editor

Enterprise Version
=========================================================
"""

import cv2
import streamlit as st

from PIL import Image
from streamlit_drawable_canvas import st_canvas

from services.geometry_engine import GeometryEngine
from ai.roof_detector import RoofDetector


def show_polygon_editor():

    st.title("🟩 Roof Polygon Editor")

    if "project" not in st.session_state:

        st.warning("No active project.")

        return

    project = st.session_state.project

    if "uploaded_images" not in project:

        st.warning("Upload an image first.")

        return

    if len(project["uploaded_images"]) == 0:

        st.warning("Upload an image first.")

        return

    image = project["uploaded_images"][0]["image"]

    st.subheader("AI Roof Detection")

    detector = RoofDetector()

    result = detector.detect(image)

    col1, col2 = st.columns(2)

    with col1:

        st.image(

            cv2.cvtColor(

                image,

                cv2.COLOR_BGR2RGB

            ),

            use_container_width=True,

            caption="Original"

        )

    with col2:

        st.image(

            cv2.cvtColor(

                result.overlay,

                cv2.COLOR_BGR2RGB

            ),

            use_container_width=True,

            caption=f"AI Suggestion ({result.confidence}%)"

        )

    if result.success:

        st.success(result.message)

    else:

        st.warning(result.message)

    st.divider()

    st.subheader("Edit Roof Polygon")

    rgb = cv2.cvtColor(

        image,

        cv2.COLOR_BGR2RGB

    )

    pil = Image.fromarray(rgb)

    canvas = st_canvas(

        background_image=pil,

        drawing_mode="polygon",

        stroke_color="#00ff00",

        stroke_width=3,

        fill_color="rgba(0,255,0,0.25)",

        update_streamlit=True,

        height=pil.height,

        width=pil.width,

        key="roof_polygon_canvas"

    )

    if canvas.json_data is None:

        return

    objects = canvas.json_data.get(

        "objects",

        []

    )

    if len(objects) == 0:

        return

    polygon = objects[-1]

    if polygon["type"] != "polygon":

        return

    points = []

    for item in polygon["path"]:

        if item[0] in ["M", "L"]:

            points.append(

                (

                    int(item[1]),

                    int(item[2])

                )

            )

    if len(points) < 3:

        st.warning(

            "Polygon requires at least 3 points."

        )

        return

    geometry = GeometryEngine()

    roof_info = geometry.roof_summary(points)

    project["roof_polygon"] = points

    project["roof_info"] = roof_info

    st.success("Roof polygon updated.")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(

        "Area",

        f'{roof_info["area_m2"]:.2f} m²'

    )

    c2.metric(

        "Perimeter",

        f'{roof_info["perimeter_m"]:.2f} m'

    )

    c3.metric(

        "Width",

        f'{roof_info["width_m"]:.2f} m'

    )

    c4.metric(

        "Height",

        f'{roof_info["height_m"]:.2f} m'

    )

    st.json(roof_info)

    st.divider()

    # ---------------------------------------------------------
    # Obstacle Detection
    # ---------------------------------------------------------

    st.subheader("🚧 Rooftop Obstacles")

    from ai.object_detector import ObjectDetector

    if st.button(
        "Detect Obstacles",
        use_container_width=True
    ):

        with st.spinner(
            "Running AI object detection..."
        ):

            detector = ObjectDetector()

            result = detector.detect(image)

            project["obstacles"] = result.detections

            st.image(

                cv2.cvtColor(

                    result.overlay,

                    cv2.COLOR_BGR2RGB

                ),

                use_container_width=True,

                caption="Detected Obstacles"

            )

            if result.success:

                st.success(result.message)

                if len(result.detections):

                    st.dataframe(

                        result.detections,

                        use_container_width=True,

                        hide_index=True

                    )

            else:

                st.info(

                    "No significant rooftop obstacles detected."

                )

    st.divider()

    # ---------------------------------------------------------
    # Polygon Preview
    # ---------------------------------------------------------

    with st.expander("Polygon Coordinates"):

        st.write(points)

    st.divider()

    # ---------------------------------------------------------
    # Action Buttons
    # ---------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(

            "💾 Save Polygon",

            use_container_width=True

        ):

            project["roof_polygon"] = points

            project["roof_info"] = roof_info

            st.success(

                "Polygon saved successfully."

            )

    with c2:

        if st.button(

            "🗑 Clear Polygon",

            use_container_width=True

        ):

            if "roof_polygon_canvas" in st.session_state:

                del st.session_state["roof_polygon_canvas"]

            st.rerun()

    with c3:

        if st.button(

            "➡ Continue to Blueprint",

            use_container_width=True

        ):

            if len(points) < 3:

                st.error(

                    "Please draw a valid roof polygon."

                )

            else:

                project["roof_polygon"] = points

                project["roof_info"] = roof_info

                st.success(

                    "Polygon finalized."

                )

                st.info(

                    "Open the '📐 Blueprint' page from the sidebar."

                )

    st.divider()

    st.success("✔ Roof polygon editing completed.")