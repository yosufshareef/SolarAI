import os
import base64
import pandas as pd
import streamlit as st
import subprocess
import sys

from ai.ai_engine import AIEngine
from services.pdf_service import PDFService
from services.solar_service import SolarService
from services.ai_report_service import AIReportService


# ---------------------------------------------------------
# PDF Preview
# ---------------------------------------------------------

def pdf_preview(pdf_path):

    with open(pdf_path, "rb") as f:

        base64_pdf = base64.b64encode(
            f.read()
        ).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="900"
        type="application/pdf">
    </iframe>
    """

    st.markdown(
        pdf_display,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# Report Page
# ---------------------------------------------------------

def show_dashboard():
    # -----------------------------------------
    # Session State
    # -----------------------------------------

    if "show_pdf" not in st.session_state:
        st.session_state.show_pdf = False

    if "ai_report_result" not in st.session_state:
        st.session_state.ai_report_result = None

    ai_report = AIReportService()

    #st.title("📑 REPORT PREVIEW")
    st.title("🤖 AI Enhanced Report")

    st.caption(
        "Generate a professional client-ready report using Claude AI."
    )

    preview_col, generate_col = st.columns(2)

    source_pdf = os.path.join(
        "exports",
        "SolarTwin_Report.pdf"
    )

    ai_pdf = os.path.join(
        "exports",
        "SolarTwin_AIReport.pdf"
    )

    with preview_col:

        if st.button(
            "👁 Show Preview",
            use_container_width=True
        ):

            if not os.path.exists(source_pdf):

                st.error("Generate Enterprise PDF first.")

            else:

                with st.spinner("Generating latest AI Report..."):

                    try:

                        # result = ai_report.generate(
                        #     input_pdf=source_pdf,
                        #     output_pdf=ai_pdf,
                        #     tone="client"
                        # )
                        script_path = os.path.join(
                            os.getcwd(),
                            "rooftop_report_agent.py"
                        )

                        subprocess.run(
                            [
                                sys.executable,
                                script_path,
                                "--input",
                                source_pdf,
                                "--output",
                                ai_pdf,
                                "--tone",
                                "client"
                            ],
                            check=True
                        )

                        st.success("AI Report Generated Successfully")
                        st.session_state.ai_report_result = result
                        st.session_state.show_pdf = True

                    except Exception as e:

                        st.error(str(e))

    with generate_col:

        if st.button(
            "🚀 Generate AI Report",
            use_container_width=True
        ):

            if not os.path.exists(source_pdf):

                st.error("Generate Enterprise PDF first.")

            else:

                with st.spinner("Generating latest AI Report..."):

                    try:
                        result = ai_report.generate(
                            input_pdf=source_pdf,
                            output_pdf=ai_pdf,
                            tone="client"
                        )
                        print(result)
                        st.session_state.ai_report_result = result
                        st.session_state.show_pdf = True

                        with open(ai_pdf, "rb") as f:

                            st.download_button(
                                "⬇ Download AI Report",
                                f,
                                file_name="SolarTwin_AIReport.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                    except Exception as e:

                        st.error(str(e))
    # =====================================================
    # AI Report Preview
    # =====================================================

    st.divider()

    if st.session_state.get("show_pdf", False):

        if os.path.exists(ai_pdf):

            st.subheader("📄 AI Report Preview")

            pdf_preview(ai_pdf)

        else:

            st.warning(
                "AI Report not found."
            )

    # =====================================================
    # Download Section
    # =====================================================

    st.divider()

    if os.path.exists(ai_pdf):

        st.subheader("Download")

        with open(ai_pdf, "rb") as pdf_file:

            st.download_button(

                "⬇ Download Latest AI Report",

                pdf_file,

                file_name="SolarTwin_AIReport.pdf",

                mime="application/pdf",

                use_container_width=True

            )

    # =====================================================
    # Status
    # =====================================================

    st.divider()

    if os.path.exists(ai_pdf):

        st.success(
            "✅ Latest AI Report is available."
        )

    else:

        st.info(
            "Generate an AI Report to preview and download."
        )
    