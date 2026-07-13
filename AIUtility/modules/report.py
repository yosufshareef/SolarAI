import streamlit as st
import pandas as pd
import os

from ai.ai_engine import AIEngine
from services.pdf_service import PDFService
from services.solar_service import SolarService


def show_report():

    st.title(" 📊 SolarTwin AI Dashboard")

    if "project" not in st.session_state:
        st.warning("No active project.")
        return

    project = st.session_state.project

    if not project.get("blueprint"):
        st.warning("Generate Blueprint first.")
        return

    ai = AIEngine()
    solar = SolarService()

    roof = project.get("roof_info", {})
    blueprint = project.get("blueprint", {})
    roi = project.get("roi", {})
    generation = project.get("generation", {})
    weather = project.get("weather", {})
    location = project.get("location", {})

    st.subheader("Executive Summary")

    summary = project.get("executive_summary")

    if not summary:

        summary = ai.executive_summary(project)

        project["executive_summary"] = summary

    st.info(summary)

    st.divider()
    # ======================================================
    # Executive KPI Dashboard
    # ======================================================

    st.subheader("Executive KPIs")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Roof Area",
        f"{roof.get('area_m2',0):.1f} m²"
    )

    k2.metric(
        "Solar Panels",
        blueprint.get("count",0)
    )

    k3.metric(
        "Capacity",
        f"{blueprint.get('capacity',0):.2f} kW"
    )

    k4.metric(
        "Payback",
        f"{roi.get('payback',0):.1f} Years"
    )

    st.divider()

    # ======================================================
    # Financial KPIs
    # ======================================================

    st.subheader("Financial Analysis")

    f1, f2, f3 = st.columns(3)

    f1.metric(
        "Annual Savings",
        f"₹{roi.get('annual_saving',0):,.0f}"
    )

    f2.metric(
        "25 Year Profit",
        f"₹{roi.get('profit_25_year',0):,.0f}"
    )

    f3.metric(
        "Annual Energy",
        f"{generation.get('annual_energy',0):,.0f} kWh"
    )

    st.divider()

    # ======================================================
    # Project Information
    # ======================================================

    st.subheader("Project Information")

    left, right = st.columns([2,1])

    with left:

        project_info = pd.DataFrame({

            "Parameter":[

                "Location",

                "Latitude",

                "Longitude",

                "Roof Area",

                "Orientation",

                "Capacity",

                "Panels"

            ],

            "Value":[

                location.get("address","-"),

                location.get("lat","-"),

                location.get("lon","-"),

                f"{roof.get('area_m2',0):.2f} m²",

                blueprint.get("orientation","-"),

                f"{blueprint.get('capacity',0):.2f} kW",

                blueprint.get("count",0)

            ]

        })

        st.dataframe(

            project_info,

            hide_index=True,

            use_container_width=True

        )

    with right:

        st.subheader("Current Weather")

        st.metric(
            "Temperature",
            f"{weather.get('temperature',0)} °C"
        )

        st.metric(
            "Humidity",
            f"{weather.get('humidity',0)} %"
        )

        st.metric(
            "Wind",
            f"{weather.get('wind',0)} km/h"
        )

        st.metric(
            "Cloud",
            f"{weather.get('cloud',0)} %"
        )

    st.divider()

    # ======================================================
    # Sustainability
    # ======================================================

    st.subheader("Sustainability")

    s1, s2 = st.columns(2)

    s1.metric(

        "CO₂ Offset",

        f"{solar.carbon_offset(generation.get('annual_energy',0)):,.0f} kg/year"

    )

    s2.metric(

        "Trees Equivalent",

        solar.trees_equivalent(

            generation.get("annual_energy",0)

        )

    )

    st.divider()
        # ======================================================
    # Solar Blueprint
    # ======================================================

    st.subheader("Solar Blueprint Layout")

    if project.get("blueprint_plot") is not None:

        st.plotly_chart(

            project["blueprint_plot"],

            use_container_width=True

        )

    else:

        st.info("Blueprint preview unavailable.")

    st.divider()

    # ======================================================
    # Monthly Energy Generation
    # ======================================================

    monthly = project.get("monthly_generation", [])

    if monthly:

        df = pd.DataFrame(monthly)

        st.subheader("Monthly Energy Generation")

        st.bar_chart(

            data=df,

            x="month",

            y="energy",

            use_container_width=True

        )

        st.divider()

        st.subheader("Monthly Solar Irradiance")

        st.line_chart(

            data=df,

            x="month",

            y="irradiance",

            use_container_width=True

        )

    else:

        st.warning("Monthly generation data unavailable.")

    st.divider()

    # ======================================================
    # Engineering Statistics
    # ======================================================

    st.subheader("Engineering Statistics")

    engineering = {

        "Location":
            location.get("address","-"),

        "Latitude":
            location.get("lat","-"),

        "Longitude":
            location.get("lon","-"),

        "Roof Area (m²)":
            roof.get("area_m2",0),

        "Roof Orientation":
            blueprint.get("orientation","-"),

        "Solar Panels":
            blueprint.get("count",0),

        "Installed Capacity (kW)":
            blueprint.get("capacity",0),

        "Annual Energy (kWh)":
            generation.get("annual_energy",0),

        "Annual Saving (₹)":
            roi.get("annual_saving",0),

        "Payback (Years)":
            roi.get("payback",0),

        "25-Year Profit (₹)":
            roi.get("profit_25_year",0),

        "Temperature (°C)":
            weather.get("temperature",0),

        "Humidity (%)":
            weather.get("humidity",0),

        "Wind (km/h)":
            weather.get("wind",0),

        "Cloud Cover (%)":
            weather.get("cloud",0),

        "CO₂ Offset (kg/year)":
            solar.carbon_offset(
                generation.get("annual_energy",0)
            ),

        "Trees Equivalent":
            solar.trees_equivalent(
                generation.get("annual_energy",0)
            )

    }

    engineering_df = pd.DataFrame(

        engineering.items(),

        columns=[

            "Parameter",

            "Value"

        ]

    )

    st.dataframe(

        engineering_df,

        hide_index=True,

        use_container_width=True

    )

    st.divider()
        # ======================================================
    # AI Recommendations
    # ======================================================

    st.subheader("🤖 AI Engineering Recommendations")

    recommendations = project.get("recommendations")

    if not recommendations:

        recommendations = ai.recommendations(project)

        project["recommendations"] = recommendations

    for rec in recommendations:

        st.success(rec)

    st.divider()

    # ======================================================
    # Executive Report Preview
    # ======================================================

    st.subheader("Executive Report Preview")

    st.markdown(summary)

    st.divider()

    # ======================================================
    # Downloads
    # ======================================================

    st.subheader("Export Report")

    c1, c2 = st.columns(2)

    with c1:

        if st.button("📄 Generate Enterprise PDF Report"):

            os.makedirs("exports", exist_ok=True)

            pdf_path = "exports/SolarTwin_Report.pdf"

            try:

                PDFService().generate(

                    project,

                    pdf_path

                )

                st.success("Enterprise PDF Generated Successfully.")

                with open(pdf_path, "rb") as f:

                    st.download_button(

                        "⬇ Download Enterprise PDF",

                        f,

                        file_name="SolarTwin_Report.pdf",

                        mime="application/pdf",

                        use_container_width=True

                    )

            except Exception as e:

                st.error(f"PDF Generation Failed : {e}")

    with c2:

        os.makedirs("exports", exist_ok=True)

        csv_path = os.path.join(
            "exports",
            "SolarTwin_Engineering_Report.csv"
        )

        engineering_df.to_csv(
            csv_path,
            index=False
        )

        with open(csv_path, "rb") as f:

            st.download_button(

                "📊 Export Engineering Data",

                f,

                file_name="SolarTwin_Engineering_Report.csv",

                mime="text/csv",

                use_container_width=True

            )

    st.divider()

    # ======================================================
    # Footer
    # ======================================================

    st.markdown(
    """
    ---
    ### ✅ Enterprise Assessment Complete

    **SolarTwin AI** has successfully analyzed the rooftop,
    generated the engineering blueprint,
    estimated annual generation,
    calculated ROI,
    evaluated sustainability,
    and produced an enterprise-ready report.

    This report is suitable for homeowners,
    solar installers,
    consultants,
    and enterprise stakeholders.
    """
    )

    st.success("✔ Report Ready for Presentation")