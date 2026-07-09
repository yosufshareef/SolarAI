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

def extract_polygon_points(shape):

    points = []

    # -----------------------------------------
    # Fabric Path (your version)
    # -----------------------------------------

    if shape.get("type") == "path":

        for cmd in shape["path"]:

            if cmd[0] in ("M", "L"):

                x = int(cmd[1])
                y = int(cmd[2])

                if (x, y) not in points:
                    points.append((x, y))

        return points

    # -----------------------------------------
    # Polygon (newer versions)
    # -----------------------------------------

    if "points" in shape:

        left = shape.get("left", 0)
        top = shape.get("top", 0)

        for p in shape["points"]:

            points.append(

                (

                    int(left + p["x"]),
                    int(top + p["y"])

                )

            )

        return points

    return points


# ---------------------------------------------------------

def show_polygon_editor():

    st.title("🟩 Roof Polygon Editor")

    if "project" not in st.session_state:

        st.warning("No active project.")

        return

    project = st.session_state.project

    if "uploaded_images" not in project or len(project["uploaded_images"]) == 0:

        st.warning("Upload an image first.")

        return

    image = project["uploaded_images"][0]["image"]

    # -------------------------------------------------
    # AI Roof Detection Preview
    # -------------------------------------------------

    st.subheader("AI Roof Detection")

    detector = RoofDetector()

    result = detector.detect(image)

    c1, c2 = st.columns(2)

    with c1:

        st.image(

            cv2.cvtColor(

                image,

                cv2.COLOR_BGR2RGB

            ),

            use_column_width=True,

            caption="Original"

        )

    with c2:

        st.image(

            cv2.cvtColor(

                result.overlay,

                cv2.COLOR_BGR2RGB

            ),

            use_column_width=True,

            caption=f"AI Suggestion ({result.confidence}%)"

        )

    if result.success:

        st.success(result.message)

    else:

        st.warning(result.message)

    st.divider()

    # -------------------------------------------------
    # Polygon Canvas
    # -------------------------------------------------

    st.subheader("Edit Roof Polygon")

    rgb = cv2.cvtColor(

        image,

        cv2.COLOR_BGR2RGB

    )

    pil = Image.fromarray(rgb)
    if "canvas_id" not in st.session_state:
        st.session_state.canvas_id = 0
    canvas = st_canvas(

        background_image=pil,

        drawing_mode="polygon",

        stroke_color="#00ff00",

        stroke_width=3,

        fill_color="rgba(0,255,0,0.25)",

        update_streamlit=False,

        height=pil.height,

        width=pil.width,

        key=f"roof_polygon_canvas_{st.session_state.canvas_id}"

    )
    #st.write("Canvas JSON:", canvas.json_data)

    points = []

    roof_info = None

    if canvas.json_data:

        objects = canvas.json_data.get(

            "objects",

            []

        )

        if objects:

            # Find the PATH object instead of assuming polygon
            polygon = None

            for obj in reversed(objects):

                if obj.get("type") == "path":

                    polygon = obj
                    break

            if polygon is not None:

                points = extract_polygon_points(
                    polygon
                )

    if len(points) >= 3:

        geometry = GeometryEngine()

        roof_info = geometry.roof_summary(

            points

        )
        st.session_state["edited_polygon"] = points
        project["roof_polygon"] = points
        project["roof_info"] = roof_info

        st.success("Roof polygon updated.")

    else:

        st.info(

            "Draw and close a polygon around the roof. Once completed, the measurements and actions will appear below."

        )
        # ---------------------------------------------------------
    # Roof Statistics
    # ---------------------------------------------------------

    if roof_info is not None:

        st.divider()

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

    # ---------------------------------------------------------
    # Obstacle Detection
    # ---------------------------------------------------------

    st.divider()

    st.subheader("🚧 Rooftop Obstacles")

    from ai.object_detector import ObjectDetector

    if st.button("Detect Obstacles"):

        with st.spinner("Running AI object detection..."):

            detector = ObjectDetector()

            result = detector.detect(image)

            project["obstacles"] = result.detections

        st.image(

            cv2.cvtColor(

                result.overlay,

                cv2.COLOR_BGR2RGB

            ),

            caption="Detected Obstacles",

            use_column_width=True

        )

        if result.success:

            st.success(result.message)

            if result.detections:

                st.dataframe(

                    result.detections,

                    hide_index=True

                )

        else:

            st.info("No rooftop obstacles detected.")

    # ---------------------------------------------------------
    # Polygon Preview
    # ---------------------------------------------------------

    st.divider()

    with st.expander("Polygon Coordinates"):

        if points:

            st.write(points)

        else:

            st.info("No polygon drawn yet.")

    # ---------------------------------------------------------
    # Action Buttons
    # ---------------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button("💾 Save Polygon"):

            saved_points = st.session_state.get("edited_polygon", [])
            if len(saved_points) < 3:
                st.error("Please draw a polygon first.")
            else:
                project["roof_polygon"] = saved_points
                project["roof_info"] = roof_info
                st.success("Polygon saved successfully.")

    with c2:

        if st.button("🗑 Clear Polygon"):

            st.session_state.canvas_id += 1

            project["roof_polygon"] = []

            project["roof_info"] = {}

            st.rerun()

    with c3:

        if st.button("➡ Continue to Blueprint"):

            if len(points) < 3:

                st.error("Please draw a valid roof polygon.")

            else:

                project["roof_polygon"] = points

                project["roof_info"] = roof_info

                st.success("Polygon finalized.")

                st.info(

                    "Now open 📐 Blueprint from the sidebar."

                )
    '''
    # ---------------------------------------------------------
    # Debug (Temporary)
    # ---------------------------------------------------------

    st.divider()

    with st.expander("Developer Debug"):

        st.write("Stored Roof Polygon:")

        st.write(project.get("roof_polygon", []))

        st.write("Canvas JSON:")

        if canvas.json_data:

            st.json(canvas.json_data)

        else:

            st.write("Canvas not initialized.")

    # ---------------------------------------------------------
    '''
    st.divider()

    st.success("✔ Roof polygon editor ready.")