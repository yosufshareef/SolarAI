import streamlit as st

from services.blueprint_engine import BlueprintEngine
from services.blueprint_plotter import BlueprintPlotter
from services.weather_service import WeatherService
from services.solar_service import SolarService


def show_blueprint():

    st.title("📐 Solar Blueprint")

    if "project" not in st.session_state:

        st.warning("No active project.")

        return

    project = st.session_state.project

    if len(project.get("roof_polygon", [])) < 3:

        st.warning("Please create a roof polygon first.")

        return

    st.subheader("Panel Configuration")

    panel = st.selectbox(

        "Select Solar Panel",

        [

            "550W",

            "610W",

            "700W"

        ]

    )

    if not st.button(

        "Generate Blueprint",

        use_container_width=True

    ):

        return

    with st.spinner(

        "Generating optimal solar layout..."

    ):

        blueprint = BlueprintEngine.generate(

            roof_points=project["roof_polygon"],

            panel=panel,

            obstacles=project.get(

                "obstacles",

                []

            )

        )

    if not blueprint["success"]:

        st.error(

            blueprint["message"]

        )

        return

    project["blueprint"] = blueprint

    project["selected_panel"] = panel

    st.success(

        blueprint["message"]

    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(

        "Panels",

        blueprint["count"]

    )

    c2.metric(

        "Capacity",

        f'{blueprint["capacity"]:.2f} kW'

    )

    c3.metric(

        "Orientation",

        blueprint["orientation"]

    )

    c4.metric(

        "Roof Utilization",

        f'{blueprint["utilization"]:.1f}%'

    )

    st.divider()

    st.subheader("Blueprint Layout")

    fig = BlueprintPlotter.create(

        project["roof_polygon"],

        blueprint["panels"],

        project.get(

            "obstacles",

            []

        )

    )

    project["blueprint_plot"] = fig

    st.plotly_chart(

        fig,

        use_column_width=True

    )

    st.info(

        "🖱 Mouse Wheel → Zoom | Drag → Pan | Double Click → Reset"

    )

    st.divider()
    # --------------------------------------------------
    # Weather + Solar Analysis
    # --------------------------------------------------

    location = project.get("location")

    if location:

        st.subheader("🌤 Weather")

        weather_service = WeatherService()

        weather = weather_service.summary(

            location["lat"],

            location["lon"]

        )

        project["weather"] = weather

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(

            "Temperature",

            f'{weather["temperature"]} °C'

        )

        c2.metric(

            "Cloud",

            f'{weather["cloud"]}%'

        )

        c3.metric(

            "Wind",

            f'{weather["wind"]} km/h'

        )

        c4.metric(

            "Humidity",

            f'{weather["humidity"]}%'

        )

        for tip in weather_service.recommendation(weather):

            st.info(tip)

        st.divider()

        # ----------------------------------------------

        st.subheader("☀ Solar Generation")

        solar = SolarService()

        generation = solar.annual_generation(

            location["lat"],

            location["lon"],

            blueprint["capacity"]

        )

        project["generation"] = generation

        monthly = solar.monthly_generation(

            location["lat"],

            location["lon"],

            blueprint["capacity"]

        )

        roi = solar.roi(

            annual_energy=generation["annual_energy"],

            electricity_rate=8,

            installation_cost=60000,

            capacity_kw=blueprint["capacity"]

        )

        project["roi"] = roi

        c1, c2, c3 = st.columns(3)

        c1.metric(

            "Annual Energy",

            f'{generation["annual_energy"]:.0f} kWh'

        )

        c2.metric(

            "Daily Energy",

            f'{generation["daily_energy"]:.1f} kWh'

        )

        c3.metric(

            "Solar Irradiance",

            f'{generation["yearly_irradiance"]:.0f} kWh/m²'

        )

        st.divider()

        # ----------------------------------------------

        st.subheader("💰 Return on Investment")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(

            "Installation",

            f'₹{roi["installation_cost"]:,.0f}'

        )

        c2.metric(

            "Annual Saving",

            f'₹{roi["annual_saving"]:,.0f}'

        )

        c3.metric(

            "Payback",

            f'{roi["payback"]:.1f} Years'

        )

        c4.metric(

            "25 Year Profit",

            f'₹{roi["profit_25_year"]:,.0f}'

        )

        st.divider()

        # ----------------------------------------------

        st.subheader("🌱 Sustainability")

        c1, c2 = st.columns(2)

        c1.metric(

            "CO₂ Offset",

            f'{solar.carbon_offset(generation["annual_energy"]):,.0f} kg/year'

        )

        c2.metric(

            "Trees Equivalent",

            solar.trees_equivalent(

                generation["annual_energy"]

            )

        )

    else:

        st.info(

            "📍 No map location selected."

        )

        st.caption(

            "Weather, solar estimation and ROI will be available after using the Map Search module."

        )

    # --------------------------------------------------

    project["last_step"] = "Blueprint"

    st.success(

        "✅ Blueprint generation completed successfully."

    )

    st.info(

        "Next → Open 📊 Dashboard to view analytics and 📑 Report to generate the final presentation."

    )