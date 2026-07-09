from datetime import datetime


class AIEngine:

    # --------------------------------------------------

    def generate_summary(self, project):

        roof = project.get("roof_info", {})

        blueprint = project.get("blueprint", {})

        location = project.get("location", {})

        roi = project.get("roi", {})

        generation = project.get("generation", {})

        return {

            "location":

                location.get(

                    "address",

                    "Unknown"

                ),

            "roof_area":

                roof.get(

                    "area_m2",

                    0

                ),

            "capacity":

                blueprint.get(

                    "capacity",

                    0

                ),

            "panels":

                blueprint.get(

                    "count",

                    0

                ),

            "orientation":

                blueprint.get(

                    "orientation",

                    "Unknown"

                ),

            "annual_energy":

                generation.get(

                    "annual_energy",

                    0

                ),

            "annual_saving":

                roi.get(

                    "annual_saving",

                    0

                ),

            "payback":

                roi.get(

                    "payback",

                    0

                )

        }

    # --------------------------------------------------

    def recommendations(self, project):

        cached = project.get(

            "recommendations"

        )

        if cached:

            return cached

        roof = project.get(

            "roof_info",

            {}

        )

        blueprint = project.get(

            "blueprint",

            {}

        )

        weather = project.get(

            "weather",

            {}

        )

        obstacles = project.get(

            "obstacles",

            []

        )

        tips = []

        area = roof.get(

            "area_m2",

            0

        )

        capacity = blueprint.get(

            "capacity",

            0

        )

        utilization = blueprint.get(

            "utilization",

            0

        )

        orientation = blueprint.get(

            "orientation",

            "Unknown"

        )

        cloud = weather.get(

            "cloud",

            0

        )

        # ----------------------------------------

        if area < 20:

            tips.append(

                "Small rooftop detected. Residential installation is recommended."

            )

        elif area < 150:

            tips.append(

                "Roof size is suitable for residential or commercial deployment."

            )

        else:

            tips.append(

                "Large rooftop detected. Industrial-scale installation is feasible."

            )

        # ----------------------------------------

        if orientation == "Landscape":

            tips.append(

                "Landscape layout maximizes available installation area."

            )

        else:

            tips.append(

                "Portrait layout provides the best packing efficiency."

            )

        # ----------------------------------------

        if utilization < 70:

            tips.append(

                "Additional roof optimization may increase installed capacity."

            )

        elif utilization > 90:

            tips.append(

                "Excellent roof utilization achieved."

            )

        # ----------------------------------------

        if len(obstacles):

            tips.append(

                f"{len(obstacles)} rooftop obstacle(s) detected."

            )

            tips.append(

                "Relocating obstacles could increase solar capacity."

            )

        # ----------------------------------------

        if cloud > 60:

            tips.append(

                "Frequent cloud cover may reduce annual generation."

            )

        elif cloud < 30:

            tips.append(

                "Weather conditions are highly favorable for solar production."

            )

        # ----------------------------------------

        if capacity < 5:

            tips.append(

                "Suitable for residential self-consumption."

            )

        elif capacity < 25:

            tips.append(

                "Suitable for commercial buildings."

            )

        else:

            tips.append(

                "Large-capacity solar installation identified."

            )

        tips.append(

            "Clean solar panels every 2–3 months for optimal efficiency."

        )

        tips.append(

            "Perform annual electrical and structural inspections."

        )

        project["recommendations"] = tips

        return tips

    # --------------------------------------------------

    def estimate_generation(

        self,

        capacity

    ):

        return round(

            capacity * 1500,

            2

        )

    # --------------------------------------------------

    def estimate_co2(

        self,

        annual_energy

    ):

        return round(

            annual_energy * 0.82,

            2

        )

    # --------------------------------------------------

    def estimate_trees(

        self,

        annual_energy

    ):

        return int(

            annual_energy / 21

        )
        # --------------------------------------------------

    def answer(

        self,

        question,

        project

    ):

        q = question.lower().strip()

        roof = project.get("roof_info", {})

        blueprint = project.get("blueprint", {})

        roi = project.get("roi", {})

        generation = project.get("generation", {})

        weather = project.get("weather", {})

        location = project.get("location", {})

        area = roof.get("area_m2", 0)

        capacity = blueprint.get("capacity", 0)

        panels = blueprint.get("count", 0)

        orientation = blueprint.get("orientation", "Unknown")

        utilization = blueprint.get("utilization", 0)

        if any(word in q for word in ["capacity", "kw", "plant size"]):

            return (

                f"The estimated solar plant capacity is "

                f"{capacity:.2f} kW."

            )

        if any(word in q for word in ["panel", "panels"]):

            return (

                f"The optimized layout contains "

                f"{panels} solar panels."

            )

        if any(word in q for word in ["roof", "area"]):

            return (

                f"The usable rooftop area is "

                f"{area:.2f} m²."

            )

        if "orientation" in q:

            return (

                f"The selected panel orientation is "

                f"{orientation}."

            )

        if "utilization" in q:

            return (

                f"The roof utilization is "

                f"{utilization:.1f}%."

            )

        if any(word in q for word in ["roi", "payback"]):

            return (

                f"The estimated payback period is "

                f"{roi.get('payback',0):.1f} years."

            )

        if any(word in q for word in ["saving", "savings"]):

            return (

                f"Estimated annual savings are "

                f"₹{roi.get('annual_saving',0):,.0f}."

            )

        if any(word in q for word in ["generation", "energy", "electricity"]):

            return (

                f"Expected annual energy generation is "

                f"{generation.get('annual_energy',0):,.0f} kWh."

            )

        if "weather" in q:

            return (

                f"Current weather: "

                f"{weather.get('temperature',0)}°C, "

                f"{weather.get('cloud',0)}% cloud cover, "

                f"{weather.get('wind',0)} km/h wind."

            )

        if "location" in q:

            return (

                f"Project location: "

                f"{location.get('address','Unknown')}."

            )

        if "obstacle" in q:

            obstacles = project.get("obstacles", [])

            return (

                f"{len(obstacles)} obstacle(s) detected. "

                "Removing or relocating them may increase "

                "solar capacity."

            )

        if any(word in q for word in ["recommend", "recommendation", "advice"]):

            return "\n".join(

                self.recommendations(project)

            )

        if any(word in q for word in ["summary", "project"]):

            return self.executive_summary(project)

        return (

            "I can answer questions about:\n\n"

            "• Roof area\n"

            "• Solar capacity\n"

            "• Panel count\n"

            "• Orientation\n"

            "• Roof utilization\n"

            "• Annual generation\n"

            "• Annual savings\n"

            "• ROI & payback\n"

            "• Weather\n"

            "• Project location\n"

            "• Recommendations"

        )

    # --------------------------------------------------

    def executive_summary(

        self,

        project

    ):

        cached = project.get(

            "executive_summary"

        )

        if cached:

            return cached

        summary = self.generate_summary(

            project

        )

        text = f"""
SolarTwin AI Executive Summary

Location:
{summary['location']}

Roof Area:
{summary['roof_area']:.2f} m²

Installed Capacity:
{summary['capacity']:.2f} kW

Solar Panels:
{summary['panels']}

Panel Orientation:
{summary['orientation']}

Estimated Annual Generation:
{summary['annual_energy']:.0f} kWh

Estimated Annual Saving:
₹{summary['annual_saving']:,.0f}

Estimated Payback:
{summary['payback']:.1f} Years

Generated:
{datetime.now().strftime('%d-%m-%Y %H:%M')}
"""

        project["executive_summary"] = text

        return text

    # --------------------------------------------------

    def estimate_roi(

        self,

        capacity,

        tariff=8,

        installation_cost=60000

    ):

        annual = self.estimate_generation(

            capacity

        )

        saving = annual * tariff

        total_cost = capacity * installation_cost

        payback = (

            total_cost / saving

            if saving

            else 0

        )

        return {

            "annual_generation":

                annual,

            "annual_saving":

                saving,

            "installation_cost":

                total_cost,

            "payback":

                round(

                    payback,

                    1

                )

        }