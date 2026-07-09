import streamlit as st
import pandas as pd
import os

from ai.ai_engine import AIEngine
from services.pdf_service import PDFService


def show_report():

    st.title("📑 Enterprise Report")

    if "project" not in st.session_state:
        st.warning("No active project.")
        return

    project = st.session_state.project

    if "blueprint" not in project:
        st.warning("Generate blueprint first.")
        return

    ai = AIEngine()

    st.subheader("Executive Summary")

    summary = project.get("executive_summary")

    if summary is None:

        summary = ai.executive_summary(project)

        project["executive_summary"] = summary

    st.info(summary)

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    blueprint = project.get("blueprint", {})
    roof = project.get("roof_info", {})
    roi = project.get("roi", {})
    generation = project.get("generation", {})

    c1.metric(
        "Roof Area",
        f'{roof.get("area_m2",0):.2f} m²'
    )

    c2.metric(
        "Panels",
        blueprint.get("count", 0)
    )

    c3.metric(
        "Capacity",
        f'{blueprint.get("capacity",0):.2f} kW'
    )

    c4.metric(
        "Payback",
        f'{roi.get("payback",0)} Years'
    )

    st.divider()

    if project.get("blueprint_plot") is not None:

        st.subheader("Solar Blueprint")

        st.plotly_chart(

            project["blueprint_plot"],

            use_container_width=True

        )

    st.divider()

    st.subheader("Project Statistics")

    report = {

        "Location":

            project.get("location", {}).get("address", "-"),

        "Roof Area (m²)":

            roof.get("area_m2", 0),

        "Panels":

            blueprint.get("count", 0),

        "Capacity (kW)":

            blueprint.get("capacity", 0),

        "Orientation":

            blueprint.get("orientation", "-"),

        "Annual Energy (kWh)":

            generation.get("annual_energy", 0),

        "Annual Saving (₹)":

            roi.get("annual_saving", 0),

        "Payback (Years)":

            roi.get("payback", 0),

        "25 Year Profit (₹)":

            roi.get("profit_25_year", 0)

    }

    df = pd.DataFrame(

        report.items(),

        columns=[

            "Parameter",

            "Value"

        ]

    )

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    st.subheader("🤖 AI Recommendations")

    recommendations = project.get("recommendations")

    if recommendations is None:

        recommendations = ai.recommendations(project)

        project["recommendations"] = recommendations

    for r in recommendations:

        st.success(r)

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        if st.button("📄 Generate PDF Report"):

            os.makedirs("exports", exist_ok=True)

            pdf_path = "exports/SolarTwin_Report.pdf"

            try:

                PDFService().generate(

                    project,

                    pdf_path

                )

                st.success("PDF Generated")

            except Exception as e:

                st.error(f"Unable to generate PDF: {e}")

                return

            with open(pdf_path, "rb") as f:

                st.download_button(

                    "⬇ Download PDF",

                    f,

                    file_name="SolarTwin_Report.pdf",

                    mime="application/pdf"

                )

    with c2:

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(

            "📊 Export CSV",

            csv,

            file_name="SolarTwin_Report.csv",

            mime="text/csv"

        )

    st.divider()

    st.success("✔ Enterprise report ready for presentation.")