import os
import json
import math
import tempfile
import re

from pathlib import Path
from datetime import date

import pdfplumber
from anthropic import Anthropic

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import (
    TA_LEFT,
    TA_JUSTIFY
)

from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer,

    Image as RLImage,

    HRFlowable,

    KeepTogether

)

MODEL = "claude-sonnet-5"

GREEN = "#1a3c34"

GOLD = "#c9a24b"

LIGHT_GREEN = "#e8f0ee"

GREY = "#666666"

DARK = "#222222"

SYSTEM_PROMPT = """
You are SolarTwin AI Engineer.

Your job is to convert a raw engineering solar report
into a professional enterprise report.

Rules:

- Never invent numerical values.
- Explain every metric clearly.
- Improve readability.
- Use professional language.
- Produce client-ready content.
- Keep engineering accuracy.

Return exactly

===DATA===

JSON

===NARRATIVE===

Markdown report.
"""

TONE_HINTS = {

    "client":

    "Write for homeowners and business owners.",

    "technical":

    "Write for engineers using engineering terminology.",

    "sales":

    "Write as a professional solar proposal."

}

class AIReportService:

    def __init__(self):

        self.client = Anthropic(

            api_key="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"

        )

    # --------------------------------------------------
    # Extract PDF Content
    # --------------------------------------------------

    def extract_pdf_content(

        self,

        pdf_path

    ):

        parts = []

        with pdfplumber.open(pdf_path) as pdf:

            for i, page in enumerate(pdf.pages, start=1):

                text = page.extract_text() or ""

                if text.strip():

                    parts.append(

                        f"--- Page {i} ---\n{text}"

                    )

                tables = page.extract_tables()

                for table in tables:

                    if not table:

                        continue

                    rows = [

                        "\t".join(

                            cell or ""

                            for cell in row

                        )

                        for row in table

                    ]

                    parts.append(

                        "\n".join(rows)

                    )

        return "\n\n".join(parts)
        # --------------------------------------------------
        # Claude Processing
        # --------------------------------------------------

    def generate_content(

            self,

            raw_text,

            tone="client"

        ):

            prompt = f"""

    {TONE_HINTS[tone]}

    Below is a rooftop solar report.

    Rewrite it professionally.

    Return EXACTLY:

    ===DATA===

    JSON

    ===NARRATIVE===

    Markdown

    Report:

    {raw_text}

    """

            response = self.client.messages.create(

                model=MODEL,

                max_tokens=4000,

                system=SYSTEM_PROMPT,

                messages=[

                    {

                        "role":"user",

                        "content":prompt

                    }

                ]

            )

            text = "\n".join(

                block.text

                for block in response.content

                if block.type == "text"

            )

            return text
    # --------------------------------------------------
    # Parse Claude Output
    # --------------------------------------------------

    def parse_response(

        self,

        response_text

    ):

        chart_data = {

            "metrics":[],

            "orientation":{},

            "timeseries":[],

            "breakdown":[]

        }

        narrative = response_text

        if (

            "===DATA===" in response_text

            and

            "===NARRATIVE===" in response_text

        ):

            data = response_text.split(

                "===DATA===",

                1

            )[1].split(

                "===NARRATIVE===",

                1

            )[0].strip()

            narrative = response_text.split(

                "===NARRATIVE===",

                1

            )[1].strip()

            try:

                chart_data = json.loads(data)

            except Exception:

                pass

        return chart_data, narrative
    # --------------------------------------------------
    # Metrics Dashboard
    # --------------------------------------------------

    def make_metrics_dashboard(

        self,

        metrics,

        output_path

    ):

        if not metrics:

            return None

        cols = min(4, len(metrics))

        rows = math.ceil(len(metrics) / cols)

        fig, axes = plt.subplots(

            rows,

            cols,

            figsize=(2.8 * cols, 2 * rows)

        )

        if len(metrics) == 1:

            axes = [axes]

        else:

            axes = axes.flatten()

        for ax, metric in zip(axes, metrics):

            ax.axis("off")

            card = mpatches.FancyBboxPatch(

                (0.05,0.05),

                0.9,

                0.9,

                boxstyle="round,pad=0.02",

                facecolor=LIGHT_GREEN,

                edgecolor=GREEN,

                linewidth=1.5,

                transform=ax.transAxes

            )

            ax.add_patch(card)

            value = metric.get("value","")

            unit = metric.get("unit","")

            label = metric.get("label","")

            ax.text(

                0.5,

                0.62,

                f"{value} {unit}",

                ha="center",

                va="center",

                fontsize=15,

                fontweight="bold",

                color=GREEN,

                transform=ax.transAxes

            )

            ax.text(

                0.5,

                0.28,

                label,

                ha="center",

                va="center",

                fontsize=9,

                color=GREY,

                transform=ax.transAxes,

                wrap=True

            )

        for ax in axes[len(metrics):]:

            ax.axis("off")

        plt.tight_layout()

        fig.savefig(

            output_path,

            dpi=170,

            transparent=True

        )

        plt.close(fig)

        return output_path
    # --------------------------------------------------
    # Monthly Energy Chart
    # --------------------------------------------------

    def make_energy_chart(

        self,

        series,

        output_path

    ):

        if not series:

            return None

        labels = series.get(

            "labels",

            []

        )

        values = series.get(

            "values",

            []

        )

        if not labels or not values:

            return None

        fig, ax = plt.subplots(

            figsize=(7,3.5)

        )

        bars = ax.bar(

            labels,

            values,

            color=GREEN

        )

        ax.set_title(

            series.get(

                "title",

                "Monthly Energy"

            )

        )

        ax.set_ylabel(

            series.get(

                "unit",

                ""

            )

        )

        ax.grid(

            axis="y",

            alpha=.3

        )

        for b,v in zip(

            bars,

            values

        ):

            ax.text(

                b.get_x()+b.get_width()/2,

                v,

                f"{v}",

                ha="center",

                fontsize=8

            )

        plt.tight_layout()

        fig.savefig(

            output_path,

            dpi=170,

            transparent=True

        )

        plt.close(fig)

        return output_path
    # --------------------------------------------------
    # Roof Orientation Diagram
    # --------------------------------------------------

    def make_orientation_chart(

        self,

        orientation,

        output_path

    ):

        if not orientation:

            return None

        tilt = orientation.get("tilt_deg")

        azimuth = orientation.get("azimuth_deg")

        if tilt is None and azimuth is None:

            return None

        fig, ax = plt.subplots(

            figsize=(5,5)

        )

        ax.set_aspect("equal")

        ax.axis("off")

        circle = plt.Circle(

            (0,0),

            1,

            fill=False,

            linewidth=2,

            color=GREEN

        )

        ax.add_patch(circle)

        directions = {

            "N":90,

            "E":0,

            "S":270,

            "W":180

        }

        for d,a in directions.items():

            r = math.radians(a)

            ax.text(

                1.15*math.cos(r),

                1.15*math.sin(r),

                d,

                ha="center",

                va="center",

                fontsize=12,

                fontweight="bold"

            )

        if azimuth is not None:

            ang = math.radians(

                90-azimuth

            )

            ax.arrow(

                0,

                0,

                0.8*math.cos(ang),

                0.8*math.sin(ang),

                width=0.02,

                color=GOLD

            )

        ax.set_title(

            f"Tilt : {tilt}°   Azimuth : {azimuth}°",

            fontsize=10

        )

        plt.tight_layout()

        fig.savefig(

            output_path,

            dpi=170,

            transparent=True

        )

        plt.close(fig)

        return output_path
    # --------------------------------------------------
    # Cost Breakdown
    # --------------------------------------------------

    def make_breakdown_chart(

        self,

        breakdown,

        output_path

    ):

        if not breakdown:

            return None

        labels = breakdown.get(

            "labels",

            []

        )

        values = breakdown.get(

            "values",

            []

        )

        if not labels or not values:

            return None

        colors_list = [

            GREEN,

            GOLD,

            "#6BAA75",

            "#87C38F",

            "#BFD8B8"

        ]

        fig, ax = plt.subplots(

            figsize=(5,4)

        )

        ax.pie(

            values,

            labels=labels,

            autopct="%1.1f%%",

            colors=colors_list[:len(labels)]

        )

        ax.set_title(

            breakdown.get(

                "title",

                "Breakdown"

            )

        )

        plt.tight_layout()

        fig.savefig(

            output_path,

            dpi=170,

            transparent=True

        )

        plt.close(fig)

        return output_path
    # --------------------------------------------------
    # Generate Charts
    # --------------------------------------------------

    def generate_all_charts(

        self,

        chart_data,

        workdir

    ):

        charts = {}

        p = os.path.join(

            workdir,

            "dashboard.png"

        )

        if self.make_metrics_dashboard(

            chart_data.get(

                "metrics",

                []

            ),

            p

        ):

            charts["Executive Summary"] = p

        ts = chart_data.get(

            "timeseries",

            []

        )

        if ts:

            p = os.path.join(

                workdir,

                "energy.png"

            )

            if self.make_energy_chart(

                ts[0],

                p

            ):

                charts["Estimated Energy Production"] = p

        p = os.path.join(

            workdir,

            "orientation.png"

        )

        if self.make_orientation_chart(

            chart_data.get(

                "orientation",

                {}

            ),

            p

        ):

            charts["Site & Roof Assessment"] = p

        bd = chart_data.get(

            "breakdown",

            []

        )

        if bd:

            p = os.path.join(

                workdir,

                "financial.png"

            )

            if self.make_breakdown_chart(

                bd[0],

                p

            ):

                charts["Financial Outlook"] = p

        return charts
    # --------------------------------------------------
    # Page Footer
    # --------------------------------------------------

    def draw_page_footer(

        self,

        canvas,

        doc,

        source_name,

        report_date

    ):

        canvas.saveState()

        width, height = letter

        left = 0.8 * inch

        right = width - 0.8 * inch

        canvas.setStrokeColor(

            colors.HexColor(GOLD)

        )

        canvas.setLineWidth(0.8)

        canvas.line(

            left,

            0.55 * inch,

            right,

            0.55 * inch

        )

        canvas.setFont(

            "Helvetica",

            8

        )

        canvas.setFillColor(

            colors.HexColor(GREY)

        )

        canvas.drawString(

            left,

            0.35 * inch,

            f"SolarTwin AI Report | {source_name}"

        )

        canvas.drawCentredString(

            width/2,

            0.35 * inch,

            report_date

        )

        canvas.drawRightString(

            right,

            0.35 * inch,

            f"Page {doc.page}"

        )

        canvas.restoreState()
    # --------------------------------------------------
    # PDF Styles
    # --------------------------------------------------

    def build_styles(self):

        styles = getSampleStyleSheet()

        title = ParagraphStyle(

            "TITLE",

            parent=styles["Title"],

            fontSize=24,

            leading=28,

            textColor=colors.white,

            backColor=colors.HexColor(GREEN),

            borderPadding=16,

            spaceAfter=15

        )

        heading = ParagraphStyle(

            "H2",

            parent=styles["Heading2"],

            textColor=colors.HexColor(GREEN),

            fontSize=15,

            leading=18,

            spaceBefore=18,

            spaceAfter=8

        )

        subheading = ParagraphStyle(

            "H3",

            parent=styles["Heading3"],

            textColor=colors.HexColor(GOLD),

            fontSize=12,

            leading=16,

            spaceBefore=10,

            spaceAfter=5

        )

        body = ParagraphStyle(

            "BODY",

            parent=styles["BodyText"],

            fontSize=10,

            leading=16,

            alignment=TA_JUSTIFY,

            textColor=colors.HexColor(DARK)

        )

        bullet = ParagraphStyle(

            "BULLET",

            parent=body,

            leftIndent=18,

            bulletIndent=5,

            spaceAfter=5

        )

        caption = ParagraphStyle(

            "CAPTION",

            parent=styles["Normal"],

            alignment=1,

            textColor=colors.HexColor(GREY),

            fontSize=8

        )

        return {

            "title":title,

            "heading":heading,

            "subheading":subheading,

            "body":body,

            "bullet":bullet,

            "caption":caption

        }
        # --------------------------------------------------
    # Markdown Cleanup
    # --------------------------------------------------

    def clean_markdown(

        self,

        text

    ):

        text = re.sub(

            r"\*\*(.*?)\*\*",

            r"<b>\1</b>",

            text

        )

        text = re.sub(

            r"\*(.*?)\*",

            r"<i>\1</i>",

            text

        )

        return text
    #--------------------
    # --------------------------------------------------
    # Markdown -> Enterprise PDF
    # --------------------------------------------------

    def markdown_to_pdf(

        self,

        markdown_text,

        charts,

        output_path,

        source_filename

    ):

        styles = self.build_styles()

        report_date = date.today().strftime(

            "%B %d, %Y"

        )

        doc = SimpleDocTemplate(

            output_path,

            pagesize=letter,

            topMargin=0.8 * inch,

            bottomMargin=0.8 * inch,

            leftMargin=0.8 * inch,

            rightMargin=0.8 * inch

        )

        story = []

        used_charts = set()

        title_added = False

        lines = markdown_text.splitlines()
        def add_chart(

            image_path,

            caption=""

        ):

            image = RLImage(image_path)

            max_width = 6.2 * inch

            if image.drawWidth > max_width:

                scale = max_width / image.drawWidth

                image.drawWidth *= scale

                image.drawHeight *= scale

            image.hAlign = "CENTER"

            block = [

                Spacer(1, 5),

                image

            ]

            if caption:

                block.append(

                    Paragraph(

                        caption,

                        styles["caption"]

                    )

                )

            block.append(

                Spacer(1, 12)

            )

            story.append(

                KeepTogether(block)

            )


        def add_rule():

            story.append(

                HRFlowable(

                    width="100%",

                    thickness=1,

                    color=colors.HexColor(GOLD),

                    spaceBefore=3,

                    spaceAfter=10

                )

            )
            # --------------------------------------------------
            # Default Title
            # --------------------------------------------------

            if not title_added:

                story.insert(

                    0,

                    Paragraph(

                        "SolarTwin AI Enterprise Report",

                        styles["title"]

                    )

                )

                story.insert(

                    1,

                    Spacer(

                        1,

                        18

                    )

                )

            # --------------------------------------------------
            # Add Remaining Charts
            # --------------------------------------------------

            for chart_name, chart_path in charts.items():

                if chart_name not in used_charts:

                    add_chart(

                        chart_path,

                        chart_name

                    )

            # --------------------------------------------------
            # Build PDF
            # --------------------------------------------------

            doc.build(

                story,

                onFirstPage=lambda canvas, doc: self.draw_page_footer(

                    canvas,

                    doc,

                    source_filename,

                    report_date

                ),

                onLaterPages=lambda canvas, doc: self.draw_page_footer(

                    canvas,

                    doc,

                    source_filename,

                    report_date

                )

            )
            # --------------------------------------------------
            # Parse Markdown
            # --------------------------------------------------

            for raw_line in lines:

                line = raw_line.strip()

                if not line:

                    continue

                # -------------------------------
                # Title
                # -------------------------------

                if line.startswith("# "):

                    story.append(

                        Paragraph(

                            self.clean_markdown(

                                line[2:]

                            ),

                            styles["title"]

                        )

                    )

                    story.append(

                        Paragraph(

                            f"Source : {source_filename}<br/>Generated : {report_date}",

                            styles["body"]

                        )

                    )

                    story.append(

                        Spacer(

                            1,

                            15

                        )

                    )

                    title_added = True

                    continue

                # -------------------------------
                # Heading
                # -------------------------------

                if line.startswith("## "):

                    heading = line[3:].strip()

                    story.append(

                        Paragraph(

                            self.clean_markdown(

                                heading

                            ),

                            styles["heading"]

                        )

                    )

                    add_rule()

                    heading_lower = heading.lower()

                    for chart_name, chart_path in charts.items():

                        if (

                            chart_name.lower()

                            in

                            heading_lower

                        ):

                            if chart_name not in used_charts:

                                add_chart(

                                    chart_path,

                                    chart_name

                                )

                                used_charts.add(

                                    chart_name

                                )

                    continue

                # -------------------------------
                # Sub Heading
                # -------------------------------

                if line.startswith("### "):

                    story.append(

                        Paragraph(

                            self.clean_markdown(

                                line[4:]

                            ),

                            styles["subheading"]

                        )

                    )

                    continue

                # -------------------------------
                # Bullet
                # -------------------------------

                if (

                    line.startswith("- ")

                    or

                    line.startswith("* ")

                ):

                    story.append(

                        Paragraph(

                            f"• {self.clean_markdown(line[2:])}",

                            styles["bullet"]

                        )

                    )

                    continue

                # -------------------------------
                # Normal Paragraph
                # -------------------------------

                story.append(

                    Paragraph(

                        self.clean_markdown(

                            line

                        ),

                        styles["body"]

                    )

                )
        # --------------------------------------------------
        # Generate AI Report
        # --------------------------------------------------

    def generate(

        self,

        input_pdf="exports/SolarTwin_Report.pdf",

        output_pdf="exports/SolarTwin_AIReport.pdf",

        tone="client"

    ):

        if not os.path.exists(input_pdf):

            raise FileNotFoundError(

                f"{input_pdf} not found."

            )

        raw_content = self.extract_pdf_content(

            input_pdf

        )

        response = self.generate_content(

            raw_content,

            tone

        )

        print("========== CLAUDE RESPONSE ==========")
        print(response[:3000])
        print("=====================================")

        chart_data, narrative = self.parse_response(

            response

        )

        os.makedirs(

            os.path.dirname(output_pdf),

            exist_ok=True

        )

        with tempfile.TemporaryDirectory() as workdir:

            charts = self.generate_all_charts(

                chart_data,

                workdir

            )

            self.markdown_to_pdf(

                markdown_text=narrative,

                charts=charts,

                output_path=output_pdf,

                source_filename=os.path.basename(input_pdf)

            )

        preview = narrative

        if len(preview) > 2500:

            preview = preview[:2500] + "\n\n..."

        return {

            "success": True,

            "preview": preview,

            "pdf_path": output_pdf,

            "chart_data": chart_data

        }
    