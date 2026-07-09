import streamlit as st

from services.geometry_engine import GeometryEngine


def show_manual_input():

    st.title("✍ Manual Roof Input")

    st.write("Enter rooftop dimensions manually.")

    length = st.number_input(
        "Roof Length (m)",
        min_value=1.0,
        value=10.0,
        step=0.5
    )

    width = st.number_input(
        "Roof Width (m)",
        min_value=1.0,
        value=8.0,
        step=0.5
    )

    obstacle_area = st.number_input(
        "Obstacle Area (m²)",
        min_value=0.0,
        value=0.0,
        step=0.5
    )

    if st.button("Generate Roof"):

        total_area = length * width
        usable_area = max(total_area - obstacle_area, 0)

        # ------------------------------------
        # Simple rectangle polygon
        # ------------------------------------

        scale = 20

        roof_polygon = [

            (0, 0),

            (length * scale, 0),

            (length * scale, width * scale),

            (0, width * scale)

        ]

        geometry = GeometryEngine(pixel_to_meter=1 / scale)

        roof_info = geometry.roof_summary(roof_polygon)

        roof_info["area_m2"] = usable_area

        project = st.session_state.project

        project["roof_polygon"] = roof_polygon

        project["roof_info"] = roof_info

        project["manual_input"] = {

            "length": length,

            "width": width,

            "total_area": total_area,

            "usable_area": usable_area,

            "obstacle_area": obstacle_area

        }

        project["obstacles"] = []

        st.success("Manual roof created successfully.")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Area",
            f"{total_area:.2f} m²"
        )

        c2.metric(
            "Obstacle Area",
            f"{obstacle_area:.2f} m²"
        )

        c3.metric(
            "Usable Area",
            f"{usable_area:.2f} m²"
        )

        st.info("You can now continue to 📐 Blueprint.")