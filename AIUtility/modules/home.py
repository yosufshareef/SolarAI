import streamlit as st


def show_home():

    st.title("☀ SolarTwin AI")

    st.subheader("Enterprise AI Powered Rooftop Solar Planning Platform")

    st.write("---")

    project = st.session_state.get("project", {})

    blueprint = project.get("blueprint", {})
    generation = project.get("generation", {})
    roi = project.get("roi", {})

    panels = blueprint.get("count", 0)
    capacity = blueprint.get("capacity", 0)
    energy = generation.get("annual_energy", 0)
    payback = roi.get("payback", "-")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Panels",
        panels
    )

    c2.metric(
        "Capacity",
        f"{capacity:.2f} kW"
    )

    c3.metric(
        "Annual Energy",
        f"{energy:.0f} kWh"
    )

    c4.metric(
        "Payback",
        f"{payback} Years"
    )

    st.divider()

    st.info(
        """
### 🚀 Welcome to SolarTwin AI

Select any input method from the left sidebar.

✅ Manual Dimensions

✅ Photo Upload

✅ Worldwide Map Search

✅ Live Camera

The application will automatically generate:

- 🏠 Roof Detection
- 📐 Solar Blueprint
- ☀ Solar Potential
- 💰 ROI Analysis
- 🌤 Weather Analysis
- 🤖 AI Recommendations
- 📄 Enterprise Report
        """
    )

    st.success("Ready to start a new solar assessment.")