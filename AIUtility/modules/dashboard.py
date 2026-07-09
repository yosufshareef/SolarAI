from duckdb import project
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from services.weather_service import WeatherService
from services.solar_service import SolarService
from ai.ai_engine import AIEngine
from services.pdf_service import PDFService

def show_dashboard():

    st.title("📊 SolarTwin AI Dashboard")

    if "project" not in st.session_state:
        st.warning("Create a project first.")
        return

    project = st.session_state.project

    if "blueprint" not in project:
        st.warning("Generate Blueprint first.")
        return

    if "location" not in project:
        st.warning("Search location first.")
        return

    location = project["location"]
    blueprint = project["blueprint"]
    roof = project.get("roof_info", {})

    weather_service = WeatherService()
    solar_service = SolarService()
    ai = AIEngine()

    weather = project.get("weather")

    generation = project.get("generation")

    roi = project.get("roi")

    monthly = project.get("monthly_generation")

    if weather is None or generation is None or roi is None or monthly is None:

        with st.spinner("Fetching weather & solar data..."):

            weather = weather_service.summary(
                location["lat"],
                location["lon"]
            )

            generation = solar_service.annual_generation(
                location["lat"],
                location["lon"],
                blueprint["capacity"]
            )

            monthly = solar_service.monthly_generation(
                location["lat"],
                location["lon"],
                blueprint["capacity"]
            )

            roi = solar_service.roi(
                generation["annual_energy"],
                electricity_rate=8,
                installation_cost=60000,
                capacity_kw=blueprint["capacity"]
            )

        project["weather"] = weather
        project["generation"] = generation
        project["monthly_generation"] = monthly
        project["roi"] = roi

    st.subheader("Executive KPIs")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Roof Area",
        f'{roof.get("area_m2",0):.1f} m²'
    )

    c2.metric(
        "Panels",
        blueprint["count"]
    )

    c3.metric(
        "Capacity",
        f'{blueprint["capacity"]:.2f} kW'
    )

    c4.metric(
        "Orientation",
        blueprint["orientation"]
    )

    st.divider()

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Annual Energy",
        f'{generation["annual_energy"]:.0f} kWh'
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
        "25 Yr Profit",
        f'₹{roi["profit_25_year"]:,.0f}'
    )

    st.divider()

    st.subheader("Current Weather")

    w1,w2,w3,w4 = st.columns(4)

    w1.metric(
        "Temperature",
        f'{weather["temperature"]}°C'
    )

    w2.metric(
        "Cloud",
        f'{weather["cloud"]}%'
    )

    w3.metric(
        "Wind",
        f'{weather["wind"]} km/h'
    )

    w4.metric(
        "Humidity",
        f'{weather["humidity"]}%'
    )

    st.divider()

    st.subheader("Monthly Energy Generation")

    if monthly:
        df = pd.DataFrame(monthly)
    else:
        st.warning("Monthly generation data is unavailable.")
        return
    
    fig = px.bar(

        df,

        x="month",

        y="energy",

        text="energy",

        labels={

            "month":"Month",

            "energy":"kWh"

        }

    )

    fig.update_layout(

        height=450,

        xaxis_title="",

        yaxis_title="Energy (kWh)"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("Monthly Solar Irradiance")

    fig2 = px.line(

        df,

        x="month",

        y="irradiance",

        markers=True

    )

    fig2.update_layout(

        height=420,

        yaxis_title="kWh/m²"

    )

    st.plotly_chart(

        fig2,

        use_container_width=True

    )

    st.divider()

    st.subheader("Sustainability")

    s1,s2 = st.columns(2)

    s1.metric(

        "CO₂ Offset",

        f'{solar_service.carbon_offset(generation["annual_energy"]):,.0f} kg/year'

    )

    s2.metric(

        "Trees Equivalent",

        solar_service.trees_equivalent(

            generation["annual_energy"]

        )

    )

    st.divider()

    st.subheader("🤖 AI Recommendations")
    recommendations = ai.recommendations(project)
    project["recommendations"] = recommendations
    for rec in ai.recommendations(project):
        

        st.success(rec)

    st.divider()

    summary = ai.executive_summary(project)
    project["executive_summary"] = summary
    st.download_button(

        "⬇ Download Executive Summary",

        summary,

        file_name="ExecutiveSummary.txt",

        mime="text/plain"

    )
    st.divider()

    if st.button("📄 Generate Enterprise PDF Report"):

        os.makedirs("exports", exist_ok=True)

        pdf_path = "exports/SolarTwin_Report.pdf"

        pdf = PDFService()

        pdf.generate(project, pdf_path)

        with open(pdf_path, "rb") as f:

            st.download_button(

                "⬇ Download PDF",

                f,

                file_name="SolarTwin_Report.pdf",

                mime="application/pdf"

            )