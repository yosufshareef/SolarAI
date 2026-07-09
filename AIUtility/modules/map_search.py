import json

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from services.map_service import MapService
from services.geometry_engine import GeometryEngine

# ----------------------------------------------------------

def create_satellite_map(lat, lon):

    m = folium.Map(

        location=[lat, lon],

        zoom_start=21,

        control_scale=True,

        tiles=None

    )

    folium.TileLayer(

        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",

        attr="Esri",

        name="Satellite",

        overlay=False,

        control=True

    ).add_to(m)

    Draw(

        export=True,

        draw_options={

            "polygon": True,

            "rectangle": True,

            "polyline": False,

            "circle": False,

            "marker": False,

            "circlemarker": False

        },

        edit_options={

            "edit": True,

            "remove": True

        }

    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


# ----------------------------------------------------------

def show_map_search():

    st.title("🌍 Worldwide Rooftop Search")

    if "project" not in st.session_state:

        st.session_state.project = {}

    project = st.session_state.project

    query = st.text_input(

        "Search Location",

        placeholder="Eiffel Tower, Paris"

    )

    if query.strip() == "":

        st.info(

            "Search for any building worldwide."

        )

        return

    service = MapService()

    location = service.search(query)

    if location is None:

        st.error(

            "Location not found."

        )

        return

    project["location"] = location

    st.success(

        location["address"]

    )

    st.subheader("🛰 Satellite View")

    fmap = create_satellite_map(

        location["lat"],

        location["lon"]

    )

    map_data = st_folium(

        fmap,

        width=1200,

        height=700,

        returned_objects=[

            "all_drawings",

            "last_clicked"

        ],

        key="satellite_map"

    )

    if not map_data:

        return

    drawings = map_data.get(

        "all_drawings",

        []

    )

    if len(drawings) == 0:

        st.info(

            "Draw a polygon around the rooftop."

        )

        return

    drawing = drawings[-1]

    geometry = drawing.get(

        "geometry",

        {}

    )

    coords = geometry.get(

        "coordinates",

        None

    )

    if coords is None:

        st.warning(

            "Invalid drawing."

        )

        return

    project["roof_polygon_geo"] = coords

    geometry_type = geometry.get("type", "")

    if geometry_type not in ["Polygon", "Rectangle"]:

        st.error("Unsupported drawing type.")

        return

    ring = coords[0]

    origin_lon = ring[0][0]
    origin_lat = ring[0][1]

    SCALE = 100000

    roof_points = []

    for lon, lat in ring:

        x = (lon - origin_lon) * SCALE
        y = (origin_lat - lat) * SCALE

        roof_points.append((x, y))

    # Remove duplicated closing point
    if len(roof_points) > 1 and roof_points[0] == roof_points[-1]:

        roof_points.pop()

    if len(roof_points) < 3:

        st.error("Invalid roof polygon.")

        return

    project["roof_polygon"] = roof_points

    geometry_engine = GeometryEngine()

    roof_info = geometry_engine.roof_summary(roof_points)

    project["roof_info"] = roof_info
        # ----------------------------------------------------------
    # Roof Summary
    # ----------------------------------------------------------

    st.divider()

    st.subheader("🏠 Roof Analysis")

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

    st.success("Roof polygon captured successfully.")

    # ----------------------------------------------------------
    # Polygon Preview
    # ----------------------------------------------------------

    with st.expander("Polygon Coordinates"):

        st.write(roof_points)

    # ----------------------------------------------------------
    # Download GeoJSON Coordinates
    # ----------------------------------------------------------

    st.download_button(

        "⬇ Download Roof Polygon",

        json.dumps(

            project["roof_polygon_geo"],

            indent=4

        ),

        file_name="roof_polygon.json",

        mime="application/json"

    )

    # ----------------------------------------------------------
    # Clicked Coordinate
    # ----------------------------------------------------------

    st.divider()

    st.subheader("📍 Selected Coordinate")

    click = map_data.get("last_clicked")

    if click:

        project["selected_coordinate"] = {

            "lat": click["lat"],

            "lon": click["lng"]

        }

        c1, c2 = st.columns(2)

        c1.metric(

            "Latitude",

            round(click["lat"], 6)

        )

        c2.metric(

            "Longitude",

            round(click["lng"], 6)

        )

    else:

        st.info(

            "Click anywhere on the map to inspect coordinates."

        )

    # ----------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        if st.button(

            "💾 Save Roof",

            use_container_width=True

        ):

            project["roof_polygon"] = roof_points

            project["roof_info"] = roof_info

            st.success(

                "Roof saved successfully."

            )

    with c2:

        if st.button(

            "➡ Continue to Blueprint",

            use_container_width=True

        ):

            project["roof_polygon"] = roof_points

            project["roof_info"] = roof_info

            project["last_step"] = "Map Search"

            st.success(

                "Roof ready for blueprint generation."

            )

            st.info(

                "Open the 📐 Blueprint page from the sidebar."

            )

    st.divider()

    st.success("✔ Map search completed.")