#!/usr/bin/env python3
"""
Rooftop Estimator Report Enhancer
==================================

Takes an existing auto-generated rooftop solar estimator PDF report
(the terse, templated kind: numbers, labels, maybe a table) and
rewrites it as a descriptive, chart-illustrated PDF report using Claude.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python rooftop_report_agent.py --input report.pdf --output report_descriptive.pdf

    # Preview the generated narrative + extracted chart data without building a PDF:
    python rooftop_report_agent.py --input report.pdf --dry-run

    # Use a different model or tone:
    python rooftop_report_agent.py --input report.pdf --output out.pdf \
        --model claude-sonnet-5 --tone technical

Pipeline:
    1. Extract raw text + tables from the input PDF (pdfplumber).
    2. Send the extracted data to Claude, which returns:
         a) a structured JSON block of the numeric data found in the
            source (single-value metrics, orientation, any monthly/
            time-series figures, any cost/category breakdown), and
         b) a descriptive narrative (Markdown) built only from what's
            in the source -- no invented figures, no "Assumptions &
            Limitations" boilerplate section.
    3. Render charts/diagrams from the structured numeric data
       (matplotlib): a key-metrics dashboard, an orientation/tilt
       diagram, a monthly production chart, and a cost/category
       breakdown chart -- whichever apply given what's in the source.
    4. Render the narrative + charts into a formatted output PDF
       (reportlab), with each chart placed under the section it's
       most relevant to.
"""

import argparse
import json
import os
import re
import sys
import math
import tempfile
from datetime import date
from functools import partial
from pathlib import Path

import pdfplumber
from anthropic import Anthropic

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, HRFlowable, KeepTogether
)
from reportlab.lib import colors


DEFAULT_MODEL = "claude-sonnet-5"

GREEN = "#1a3c34"
GOLD = "#c9a24b"
LIGHT_GREEN = "#e8f0ee"
GREY = "#666666"
DARK = "#222222"

SYSTEM_PROMPT = """You are a solar energy analyst who rewrites terse, \
auto-generated rooftop solar estimator reports into clear, descriptive, \
client-ready reports with supporting charts.

Rules:
- Do NOT invent numbers. Only use figures that appear in the source data \
provided to you.
- Where the source gives a bare number or label (e.g. "Usable Area: 42 m2", \
"Tilt: 18deg", "Annual Output: 6200 kWh"), explain what it means, why it \
matters, and any reasonable engineering context (typical ranges, what \
drives that number, trade-offs).
- If you are giving general domain context rather than citing an exact \
source figure, make that distinction naturally in the prose (e.g. "for \
reference, similar residential systems typically..."), so the reader can \
tell source-derived facts from general guidance.
- Do NOT include an "Assumptions & Limitations" section or any similar \
disclaimer section. Keep the report focused and descriptive only.
- Organize the narrative into clear sections with headings. Use this \
structure unless the source data clearly calls for a different one:
  1. Executive Summary
  2. Site & Roof Assessment
  3. Solar Resource & Shading
  4. Recommended System Configuration
  5. Estimated Energy Production
  6. Financial Outlook (only if source has cost/savings data)
- Use plain, confident, professional language. Avoid marketing fluff.
- Do not use Markdown tables in the narrative -- use bullet points or \
prose instead. Keep it thorough but not padded.

You must respond with EXACTLY two parts, in this exact order, with these \
exact markers on their own lines:

===DATA===
<a single JSON object -- see schema below -- with no markdown fences>
===NARRATIVE===
<the Markdown narrative report, starting with a "# Title" line>

JSON schema for the DATA block (use null / empty list when not present in \
the source -- never fabricate a value to fill a field):
{
  "metrics": [ {"label": string, "value": number, "unit": string} ... ],
  "orientation": {"tilt_deg": number|null, "azimuth_deg": number|null},
  "timeseries": [
    {"title": string, "unit": string, "labels": [string...], "values": [number...]}
  ],
  "breakdown": [
    {"title": string, "unit": string, "labels": [string...], "values": [number...]}
  ]
}
- "metrics" = standalone single-value figures worth highlighting (roof \
area, panel count, annual output, system size, irradiance, etc.) -- pick \
the 4-8 most report-worthy ones.
- "orientation" = only fill if the source gives a roof tilt and/or azimuth.
- "timeseries" = only fill if the source gives a series across a dimension \
like months or years (e.g. monthly production estimates). Omit entirely \
(empty list) if the source only gives a single annual total.
- "breakdown" = only fill if the source gives a categorical split (e.g. \
equipment vs. installation cost, or energy sources). Omit if not present.
"""

TONE_HINTS = {
    "client": "Write for a homeowner or business owner client with no "
              "technical background. Explain jargon in plain terms.",
    "technical": "Write for an engineering / technical audience. You can "
                 "use domain terminology (irradiance, derate factor, "
                 "azimuth, tilt, kWp, PR) without re-explaining basics.",
    "sales": "Write with a persuasive but factual tone suitable for a "
             "sales proposal, emphasizing benefits while staying accurate "
             "to the source data.",
}


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def extract_pdf_content(pdf_path: str) -> str:
    """Extract text and tables from the source PDF into one text blob."""
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"--- Page {i} text ---\n{text.strip()}")

            tables = page.extract_tables()
            for t_idx, table in enumerate(tables, start=1):
                if not table:
                    continue
                rows = ["\t".join(cell or "" for cell in row) for row in table]
                parts.append(
                    f"--- Page {i} table {t_idx} ---\n" + "\n".join(rows)
                )

    if not parts:
        raise ValueError(
            "No extractable text or tables found in the PDF. "
            "It may be a scanned/image-only report; OCR would be needed first."
        )
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# Claude call
# --------------------------------------------------------------------------

def generate_report_content(raw_content: str, model: str, tone: str):
    """Send extracted content to Claude; return (chart_data_dict, markdown_narrative)."""
    client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

    tone_hint = TONE_HINTS.get(tone, TONE_HINTS["client"])
    user_prompt = (
        f"{tone_hint}\n\n"
        "Below is the raw extracted content (text and tables) from an "
        "auto-generated rooftop solar estimator report. Produce the DATA "
        "and NARRATIVE blocks exactly as instructed.\n\n"
        "=== RAW SOURCE REPORT CONTENT ===\n"
        f"{raw_content}\n"
        "=== END SOURCE REPORT CONTENT ==="
    )

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    full_text = "\n".join(b.text for b in response.content if b.type == "text").strip()

    if "===DATA===" not in full_text or "===NARRATIVE===" not in full_text:
        # Fallback: no chart data, treat everything as narrative
        return {"metrics": [], "orientation": {}, "timeseries": [], "breakdown": []}, full_text

    data_part = full_text.split("===DATA===", 1)[1].split("===NARRATIVE===", 1)[0].strip()
    narrative_part = full_text.split("===NARRATIVE===", 1)[1].strip()

    try:
        chart_data = json.loads(data_part)
    except json.JSONDecodeError:
        chart_data = {"metrics": [], "orientation": {}, "timeseries": [], "breakdown": []}

    chart_data.setdefault("metrics", [])
    chart_data.setdefault("orientation", {})
    chart_data.setdefault("timeseries", [])
    chart_data.setdefault("breakdown", [])

    return chart_data, narrative_part


# --------------------------------------------------------------------------
# Chart generation
# --------------------------------------------------------------------------

def make_metrics_dashboard(metrics: list, out_path: str):
    """Grid of stat cards, one per scalar metric."""
    if not metrics:
        return None
    n = len(metrics)
    cols = min(4, n)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(2.6 * cols, 1.7 * rows))
    if n > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for ax, m in zip(axes, metrics):
        ax.axis("off")
        card = mpatches.FancyBboxPatch(
            (0.03, 0.03), 0.94, 0.94, boxstyle="round,pad=0.02,rounding_size=0.08",
            transform=ax.transAxes, facecolor=LIGHT_GREEN, edgecolor=GREEN, linewidth=1.2,
        )
        ax.add_patch(card)
        value = m.get("value")
        unit = m.get("unit") or ""
        label = m.get("label") or ""
        if isinstance(value, (int, float)):
            # Thousands separators, but keep small/decimal values readable.
            value_str = f"{value:,.0f}" if abs(value) >= 1000 else f"{value:g}"
        else:
            value_str = str(value)
        ax.text(0.5, 0.62, f"{value_str} {unit}".strip(), transform=ax.transAxes,
                ha="center", va="center", fontsize=15, fontweight="bold", color=GREEN)
        ax.text(0.5, 0.24, label, transform=ax.transAxes, ha="center", va="center",
                fontsize=9, color=GREY, wrap=True)

    for ax in axes[n:]:
        ax.axis("off")

    fig.tight_layout()
    fig.savefig(out_path, dpi=160, transparent=True)
    plt.close(fig)
    return out_path


def make_orientation_diagram(orientation: dict, out_path: str):
    """Compass showing azimuth + a simple side-view tilt wedge."""
    tilt = orientation.get("tilt_deg")
    azimuth = orientation.get("azimuth_deg")
    if tilt is None and azimuth is None:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.2))

    # --- Compass (azimuth) ---
    ax = axes[0]
    ax.set_aspect("equal")
    ax.axis("off")
    circle = plt.Circle((0, 0), 1, fill=False, edgecolor=GREEN, linewidth=1.5)
    ax.add_patch(circle)
    for label, ang in [("N", 90), ("E", 0), ("S", 270), ("W", 180)]:
        rad = math.radians(ang)
        ax.text(1.15 * math.cos(rad), 1.15 * math.sin(rad), label,
                ha="center", va="center", fontsize=11, color=GREY, fontweight="bold")
    if azimuth is not None:
        math_ang = math.radians(90 - azimuth)  # compass bearing -> math angle
        ax.annotate("", xy=(0.9 * math.cos(math_ang), 0.9 * math.sin(math_ang)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=GOLD, linewidth=2.5))
        ax.set_title(f"Azimuth: {azimuth:g}\u00b0", fontsize=10, color=GREEN)
    else:
        ax.set_title("Azimuth: n/a", fontsize=10, color=GREY)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)

    # --- Tilt side view ---
    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(-0.2, 1.4)
    ax2.set_ylim(-0.2, 1.0)
    ax2.plot([-0.1, 1.3], [0, 0], color=GREY, linewidth=1)  # ground
    if tilt is not None:
        t = math.radians(tilt)
        rx, ry = 1.1 * math.cos(t), 1.1 * math.sin(t)
        ax2.plot([0, rx], [0, ry], color=GREEN, linewidth=3)  # roof plane
        arc = mpatches.Arc((0, 0), 0.6, 0.6, angle=0, theta1=0, theta2=tilt, color=GOLD, linewidth=2)
        ax2.add_patch(arc)
        ax2.text(0.4, 0.12, f"{tilt:g}\u00b0", fontsize=10, color=GOLD, fontweight="bold")
        ax2.set_title("Roof tilt", fontsize=10, color=GREEN)
    else:
        ax2.set_title("Roof tilt: n/a", fontsize=10, color=GREY)

    fig.tight_layout()
    fig.savefig(out_path, dpi=160, transparent=True)
    plt.close(fig)
    return out_path


def make_timeseries_chart(series: dict, out_path: str):
    labels = series.get("labels") or []
    values = series.get("values") or []
    if not labels or not values or len(labels) != len(values):
        return None

    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#dddddd", linewidth=0.8)
    bars = ax.bar(labels, values, color=GREEN, width=0.72)
    ax.set_ylabel(series.get("unit", ""), fontsize=9, color=GREY)
    ax.set_title(series.get("title", "Production over time"), fontsize=11,
                 color=GREEN, fontweight="bold", pad=10)
    ax.tick_params(axis="x", labelsize=8, rotation=45)
    ax.tick_params(axis="y", labelsize=8)
    ax.margins(y=0.15)
    # Value labels above each bar.
    for bar, val in zip(bars, values):
        if isinstance(val, (int, float)):
            label = f"{val:,.0f}" if abs(val) >= 1000 else f"{val:g}"
            ax.annotate(label, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7, color=GREEN)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, transparent=True)
    plt.close(fig)
    return out_path


def make_breakdown_chart(breakdown: dict, out_path: str):
    labels = breakdown.get("labels") or []
    values = breakdown.get("values") or []
    if not labels or not values or len(labels) != len(values):
        return None

    palette = [GREEN, GOLD, "#6b9080", "#a4c3b2", "#cce3de", "#84a98c"]
    colors_cycle = [palette[i % len(palette)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, _, autotexts = ax.pie(
        values, labels=None, autopct="%1.0f%%", colors=colors_cycle,
        textprops={"fontsize": 9, "color": "white", "fontweight": "bold"},
    )
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, frameon=False)
    ax.set_title(breakdown.get("title", "Breakdown"), fontsize=11, color=GREEN)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, transparent=True)
    plt.close(fig)
    return out_path


def generate_charts(chart_data: dict, workdir: str) -> dict:
    """Build all applicable charts; return {section_keyword: image_path}."""
    charts = {}

    p = os.path.join(workdir, "dashboard.png")
    if make_metrics_dashboard(chart_data.get("metrics", []), p):
        charts["executive summary"] = p

    p = os.path.join(workdir, "orientation.png")
    if make_orientation_diagram(chart_data.get("orientation", {}) or {}, p):
        charts["site & roof assessment"] = p

    timeseries_list = chart_data.get("timeseries", [])
    if timeseries_list:
        p = os.path.join(workdir, "timeseries.png")
        if make_timeseries_chart(timeseries_list[0], p):
            charts["estimated energy production"] = p

    breakdown_list = chart_data.get("breakdown", [])
    if breakdown_list:
        p = os.path.join(workdir, "breakdown.png")
        if make_breakdown_chart(breakdown_list[0], p):
            charts["financial outlook"] = p

    return charts


# --------------------------------------------------------------------------
# PDF rendering
# --------------------------------------------------------------------------

def _draw_page_furniture(canvas, doc, source_filename: str, gen_date: str):
    """Footer (drawn on every page): gold rule, source + date, page number."""
    canvas.saveState()
    width, _ = letter
    left = 0.85 * inch
    right = width - 0.85 * inch

    canvas.setStrokeColor(colors.HexColor(GOLD))
    canvas.setLineWidth(0.75)
    canvas.line(left, 0.58 * inch, right, 0.58 * inch)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor(GREY))
    canvas.drawString(left, 0.42 * inch, f"Rooftop Solar Assessment  |  {source_filename}")
    canvas.drawCentredString(width / 2, 0.42 * inch, gen_date)
    canvas.drawRightString(right, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def markdown_to_pdf(markdown_text: str, charts: dict, output_path: str, source_filename: str):
    """Render the Markdown narrative (with charts inserted under matching headings) into a PDF."""
    styles = getSampleStyleSheet()
    gen_date = date.today().strftime("%B %d, %Y")

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=24, leading=28,
        alignment=TA_LEFT, textColor=colors.white,
        backColor=colors.HexColor(GREEN), borderPadding=(16, 16, 18, 16),
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=9,
        textColor=colors.white, backColor=colors.HexColor(GOLD),
        borderPadding=(6, 16, 6, 16), spaceAfter=22,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=14.5, spaceBefore=20,
        spaceAfter=2, textColor=colors.HexColor(GREEN), leading=18,
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=12,
        spaceAfter=4, textColor=colors.HexColor(GOLD), leading=15,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10.5, leading=15.5,
        spaceAfter=8, alignment=TA_JUSTIFY, textColor=colors.HexColor(DARK),
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=body_style, leftIndent=18, bulletIndent=6,
        spaceAfter=5, alignment=TA_LEFT,
    )
    caption_style = ParagraphStyle(
        "Caption", parent=styles["Normal"], fontSize=8.5, alignment=1,
        textColor=colors.HexColor(GREY), spaceBefore=3, spaceAfter=14,
    )

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        title="Rooftop Solar Assessment Report",
    )
    story = []
    used_charts = set()

    def clean_inline(t: str) -> str:
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<i>\1</i>", t)
        return t

    def section_rule():
        return HRFlowable(width="100%", thickness=1, color=colors.HexColor(GOLD),
                          spaceBefore=3, spaceAfter=9, lineCap="round")

    def add_image(path: str, caption: str = ""):
        img = RLImage(path)
        max_w = 6.3 * inch
        if img.drawWidth > max_w:
            scale = max_w / img.drawWidth
            img.drawWidth *= scale
            img.drawHeight *= scale
        img.hAlign = "CENTER"
        block = [Spacer(1, 4), img]
        if caption:
            block.append(Paragraph(caption, caption_style))
        else:
            block.append(Spacer(1, 12))
        # Keep an image with its caption together on one page.
        story.append(KeepTogether(block))

    title_written = False
    lines = markdown_text.splitlines()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), title_style))
            story.append(Paragraph(
                f"Source report: {source_filename}  &nbsp;&bull;&nbsp;  Prepared {gen_date}",
                subtitle_style))
            title_written = True
        elif line.startswith("## "):
            heading_text = line[3:]
            story.append(Paragraph(clean_inline(heading_text), h2_style))
            story.append(section_rule())
            key = heading_text.strip().lower()
            for chart_key, chart_path in charts.items():
                if chart_key in key and chart_key not in used_charts:
                    add_image(chart_path, caption=chart_key.title())
                    used_charts.add(chart_key)
        elif line.startswith("### "):
            story.append(Paragraph(clean_inline(line[4:]), h3_style))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph(
                '<font color="%s">&bull;</font>&nbsp;&nbsp;' % GOLD + clean_inline(line[2:]),
                bullet_style))
        else:
            story.append(Paragraph(clean_inline(line), body_style))

    if not title_written:
        story.insert(0, Paragraph("Rooftop Solar Assessment Report", title_style))

    # Any charts that never matched a heading (e.g. narrative used different wording) go at the end
    for chart_key, chart_path in charts.items():
        if chart_key not in used_charts:
            add_image(chart_path, caption=chart_key.title())

    furniture = partial(_draw_page_furniture, source_filename=source_filename, gen_date=gen_date)
    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Enhance a rooftop estimator PDF report into a descriptive, chart-illustrated report using Claude.")
    parser.add_argument("--input", "-i", required=True, help="Path to the source estimator PDF report")
    parser.add_argument("--output", "-o", help="Path to write the descriptive PDF report (required unless --dry-run)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--tone", default="client", choices=list(TONE_HINTS.keys()), help="Target audience tone (default: client)")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated Markdown + chart data instead of building a PDF")
    args = parser.parse_args()

    if not args.dry_run and not args.output:
        parser.error("--output is required unless --dry-run is set")

    # if not os.environ.get("ANTHROPIC_API_KEY"):
    #     sys.exit("ERROR: set the ANTHROPIC_API_KEY environment variable before running this script.")

    ANTHROPIC_API_KEY = "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"
    
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"ERROR: input file not found: {input_path}")

    print(f"[1/4] Extracting content from {input_path.name} ...")
    raw_content = extract_pdf_content(str(input_path))
    print(f"      Extracted {len(raw_content)} characters.")

    print(f"[2/4] Generating descriptive narrative + chart data with {args.model} (tone: {args.tone}) ...")
    chart_data, narrative = generate_report_content(raw_content, args.model, args.tone)

    if args.dry_run:
        print("\n=== CHART DATA ===\n")
        print(json.dumps(chart_data, indent=2))
        print("\n=== NARRATIVE ===\n")
        print(narrative)
        return

    with tempfile.TemporaryDirectory() as workdir:
        print("[3/4] Generating charts from extracted numeric data ...")
        charts = generate_charts(chart_data, workdir)
        print(f"      Generated {len(charts)} chart(s): {', '.join(charts) if charts else 'none'}")

        print(f"[4/4] Rendering PDF -> {args.output}")
        markdown_to_pdf(narrative, charts, args.output, input_path.name)

    print("Done.")


if __name__ == "__main__":
    main()
