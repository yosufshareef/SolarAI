import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


class PDFService:

    def __init__(self):

        self.styles = getSampleStyleSheet()

        self.title_style = self.styles["Heading1"]
        self.title_style.alignment = TA_CENTER

        self.heading = self.styles["Heading2"]

        self.normal = self.styles["BodyText"]

    # --------------------------------------------------

    def _table(self, data):

        table = Table(data, colWidths=[2.8*inch,3.2*inch])

        table.setStyle(

            TableStyle([

                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f4e79")),

                ("TEXTCOLOR",(0,0),(-1,0),colors.white),

                ("GRID",(0,0),(-1,-1),0.5,colors.grey),

                ("BACKGROUND",(0,1),(-1,-1),colors.beige),

                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

                ("BOTTOMPADDING",(0,0),(-1,0),8),

                ("TOPPADDING",(0,1),(-1,-1),5)

            ])

        )

        return table

    # --------------------------------------------------

    def generate(self, project, output_path):

        doc = SimpleDocTemplate(

            output_path,

            leftMargin=25,

            rightMargin=25,

            topMargin=25,

            bottomMargin=25

        )

        story = []

        # -------------------------------------

        story.append(

            Paragraph(

                "SolarTwin AI",

                self.title_style

            )

        )

        story.append(

            Paragraph(

                "Enterprise Solar Assessment Report",

                self.heading

            )

        )

        story.append(Spacer(1,0.25*inch))

        story.append(

            Paragraph(

                datetime.now().strftime("%d-%m-%Y %H:%M"),

                self.normal

            )

        )

        story.append(Spacer(1,0.25*inch))

        # -------------------------------------

        location = project.get("location",{})

        roof = project.get("roof_info",{})

        blueprint = project.get("blueprint",{})

        weather = project.get("weather",{})

        roi = project.get("roi",{})

        generation = project.get("generation",{})

        # -------------------------------------

        story.append(

            Paragraph(

                "Project Information",

                self.heading

            )

        )

        table = self._table([

            ["Parameter","Value"],

            ["Location",location.get("address","-")],

            ["Roof Area",f'{roof.get("area_m2",0):.2f} m²'],

            ["Panels",str(blueprint.get("count",0))],

            ["Capacity",f'{blueprint.get("capacity",0):.2f} kW'],

            ["Orientation",blueprint.get("orientation","-")]

        ])

        story.append(table)

        story.append(Spacer(1,0.3*inch))

        # -------------------------------------

        story.append(

            Paragraph(

                "Weather",

                self.heading

            )

        )

        table = self._table([

            ["Parameter","Value"],

            ["Temperature",f'{weather.get("temperature","-")} °C'],

            ["Cloud Cover",f'{weather.get("cloud","-")} %'],

            ["Wind",f'{weather.get("wind","-")} km/h'],

            ["Humidity",f'{weather.get("humidity","-")} %']

        ])

        story.append(table)

        story.append(Spacer(1,0.3*inch))

        # -------------------------------------

        story.append(

            Paragraph(

                "Solar Production",

                self.heading

            )

        )

        table = self._table([

            ["Parameter","Value"],

            ["Annual Energy",

             f'{generation.get("annual_energy",0):.0f} kWh'],

            ["Daily Energy",

             f'{generation.get("daily_energy",0):.1f} kWh'],

            ["Annual Saving",

             f'₹ {roi.get("annual_saving",0):,.0f}'],

            ["Payback",

             f'{roi.get("payback",0)} Years'],

            ["25 Year Profit",

             f'₹ {roi.get("profit_25_year",0):,.0f}']

        ])

        story.append(table)

        story.append(Spacer(1,0.3*inch))

        # -------------------------------------

        if "blueprint_png" in project:

            img_path = project["blueprint_png"]

            if os.path.exists(img_path):

                story.append(

                    Paragraph(

                        "Solar Blueprint",

                        self.heading

                    )

                )

                img = Image(

                    img_path,

                    width=6.5*inch,

                    height=4.5*inch

                )

                story.append(img)

                story.append(Spacer(1,0.3*inch))

        # -------------------------------------

        story.append(

            Paragraph(

                "AI Recommendations",

                self.heading

            )

        )

        recs = project.get("recommendations",[])

        if len(recs)==0:

            recs=[

                "South facing installation recommended.",

                "Remove rooftop obstacles if possible.",

                "Periodic cleaning improves generation."

            ]

        for r in recs:

            story.append(

                Paragraph(

                    "• "+r,

                    self.normal

                )

            )

        story.append(Spacer(1,0.3*inch))

        # -------------------------------------

        story.append(

            Paragraph(

                "Executive Conclusion",

                self.heading

            )

        )

        conclusion = f"""
SolarTwin AI concludes that the analysed rooftop is suitable
for a photovoltaic installation of approximately
{blueprint.get('capacity',0):.2f} kW.

The estimated annual production is
{generation.get('annual_energy',0):.0f} kWh,
with estimated annual savings of
₹ {roi.get('annual_saving',0):,.0f}.

The generated layout maximizes the usable roof area
while considering rooftop geometry and detected obstacles.

The proposed design is recommended for further
engineering validation before installation.
"""

        story.append(

            Paragraph(

                conclusion,

                self.normal

            )

        )

        def add_page_number(canvas, doc):

            canvas.saveState()

            canvas.setFont(

                "Helvetica",

                9

            )

            canvas.drawRightString(

                560,

                20,

                f"Page {canvas.getPageNumber()}"

            )

            canvas.restoreState()


        doc.build(

            story,

            onFirstPage=add_page_number,

            onLaterPages=add_page_number

        )

        return output_path