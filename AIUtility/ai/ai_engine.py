from datetime import datetime
import os
import glob
from anthropic import Anthropic
from pypdf import PdfReader


MODEL = "claude-sonnet-5"

SUPPORTED_EXTS = (
    ".txt",
    ".md",
    ".csv",
    ".pdf"
)

GENERAL_SYSTEM_PROMPT = """
You are SolarTwin AI Engineer.

You are an enterprise solar engineering assistant.

Answer using the uploaded SolarTwin report whenever possible.

If the report does not contain the answer,
answer using your solar engineering knowledge.

Keep answers concise,
professional,
and suitable for rooftop solar planning.
"""

REPORT_SYSTEM_TEMPLATE = """
You are SolarTwin AI Engineer.

Always answer using the report excerpts below.

If the answer is present,
cite the report.

If not present,
answer using general rooftop solar engineering knowledge.

Report:

{context}
"""

class AIEngine:
        # --------------------------------------------------
    # Claude Initialization
    # --------------------------------------------------

    def __init__(self):

        self.client = Anthropic(

            api_key="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"

        )

        self.report_index = []

            # --------------------------------------------------
    # PDF Reader
    # --------------------------------------------------

    def extract_text(

        self,

        path

    ):

        ext = os.path.splitext(path)[1].lower()

        try:

            if ext == ".pdf":

                reader = PdfReader(path)

                return "\n".join(

                    (page.extract_text() or "")

                    for page in reader.pages

                )

            with open(

                path,

                "r",

                encoding="utf-8",

                errors="ignore"

            ) as f:

                return f.read()

        except Exception:

            return ""
        # --------------------------------------------------
    # Chunking
    # --------------------------------------------------

    def chunk_text(

        self,

        text,

        size=1200,

        overlap=150

    ):

        chunks = []

        start = 0

        n = len(text)

        while start < n:

            end = start + size

            chunk = text[start:end].strip()

            if chunk:

                chunks.append(chunk)

            start = end - overlap

        return chunks
        # --------------------------------------------------
    # Load Solar Report
    # --------------------------------------------------

    def load_report(

        self,

        report_path="exports/SolarTwin_Report.pdf"

    ):

        self.report_index = []

        if not os.path.exists(report_path):

            return

        text = self.extract_text(report_path)

        if not text:

            return

        for chunk in self.chunk_text(text):

            self.report_index.append(

                (

                    os.path.basename(report_path),

                    chunk

                )

            )
        # --------------------------------------------------
    # Score Chunks
    # --------------------------------------------------

    def score_chunk(

        self,

        query_words,

        chunk_text

    ):

        text = chunk_text.lower()

        return sum(

            1

            for word in query_words

            if word in text

        )
        # --------------------------------------------------
    # Top Matching Chunks
    # --------------------------------------------------

    def top_chunks(

        self,

        query,

        k=4

    ):

        words = [

            w

            for w in query.lower().split()

            if len(w) > 2

        ]

        scored = []

        for filename, chunk in self.report_index:

            score = self.score_chunk(

                words,

                chunk

            )

            scored.append(

                (

                    score,

                    filename,

                    chunk

                )

            )

        scored.sort(

            key=lambda x: x[0],

            reverse=True

        )

        top = [

            x

            for x in scored

            if x[0] > 0

        ][:k]

        if not top:

            top = scored[:k]

        return top
        # --------------------------------------------------
    # Build Claude Context
    # --------------------------------------------------

    def build_prompt(

        self,

        question

    ):

        chunks = self.top_chunks(question)

        context = "\n\n".join(

            f"[{fname}]\n{chunk}"

            for _, fname, chunk in chunks

        )

        return REPORT_SYSTEM_TEMPLATE.format(

            context=context

        )
        # --------------------------------------------------
    # Claude Chat
    # --------------------------------------------------

    def ask_pdf(

        self,

        question

    ):

        if not self.report_index:

            self.load_report()

        system_prompt = self.build_prompt(

            question

        )

        response = self.client.messages.create(

            model=MODEL,

            max_tokens=700,

            system=system_prompt,

            messages=[

                {

                    "role":"user",

                    "content":question

                }

            ]

        )

        return "".join(

            block.text

            for block in response.content

            if block.type == "text"

        )

    # --------------------------------------------------
    # AI Recommendations
    # --------------------------------------------------

    def recommendations(self, project):

        blueprint = project.get("blueprint", {})
        roof = project.get("roof_info", {})
        roi = project.get("roi", {})

        rec = []

        area = roof.get("area_m2", 0)

        if area < 40:
            rec.append("Roof area is limited. Consider high-efficiency solar panels.")

        if blueprint.get("orientation") != "South":
            rec.append("South-facing panels generally maximize solar generation.")

        if roi.get("payback", 100) > 7:
            rec.append("Consider subsidies or reducing installation cost to improve ROI.")

        if not rec:
            rec.append("Current design is well optimized.")

        return rec

    # --------------------------------------------------
    # Executive Summary
    # --------------------------------------------------

    def executive_summary(self, project):

        roof = project.get("roof_info", {})
        blueprint = project.get("blueprint", {})
        generation = project.get("generation", {})
        roi = project.get("roi", {})

        return f"""
            SolarTwin AI Executive Summary
            Roof Area : {roof.get('area_m2',0):.1f} m²
            Panels : {blueprint.get('count',0)}
            Installed Capacity : {blueprint.get('capacity',0):.2f} kW
            Annual Energy : {generation.get('annual_energy',0):,.0f} kWh
            Annual Saving : ₹{roi.get('annual_saving',0):,.0f}
            Payback Period : {roi.get('payback',0):.1f} years
            25-Year Profit : ₹{roi.get('profit_25_year',0):,.0f}
            Generated by SolarTwin AI Enterprise.
            """