"""
=========================================================
SolarTwin AI

Enterprise Blueprint Engine

Version : 2.0
=========================================================
"""

from shapely.geometry import Polygon, box
from shapely.validation import make_valid


class BlueprintEngine:

    PIXEL_TO_METER = 0.05

    PANEL_DATABASE = {

        "550W": {

            "length": 2.279,

            "width": 1.134,

            "power": 550

        },

        "610W": {

            "length": 2.382,

            "width": 1.134,

            "power": 610

        },

        "700W": {

            "length": 2.500,

            "width": 1.300,

            "power": 700

        }

    }

    # --------------------------------------------------

    @classmethod
    def _roof_polygon(cls, roof_points):

        if roof_points is None:

            return None

        if len(roof_points) < 3:

            return None

        try:

            roof = Polygon(roof_points)

            if not roof.is_valid:

                roof = make_valid(roof)

            return roof

        except Exception:

            return None

    # --------------------------------------------------

    @classmethod
    def _obstacle_polygons(cls, obstacles):

        polys = []

        for obj in obstacles:

            if "bbox" not in obj:

                continue

            x1, y1, x2, y2 = obj["bbox"]

            polys.append(

                box(

                    x1,

                    y1,

                    x2,

                    y2

                )

            )

        return polys

    # --------------------------------------------------

    @classmethod
    def _panel_rect(

        cls,

        x,

        y,

        w,

        h,

        orientation

    ):

        return {

            "x": round(x, 2),

            "y": round(y, 2),

            "width": round(w, 2),

            "height": round(h, 2),

            "orientation": orientation

        }

    # --------------------------------------------------

    @classmethod
    def _generate_layout(

        cls,

        roof,

        obstacle_polygons,

        panel_width,

        panel_height,

        orientation

    ):

        minx, miny, maxx, maxy = roof.bounds

        panels = []

        y = miny

        while y + panel_height <= maxy:

            x = minx

            while x + panel_width <= maxx:

                rect = box(

                    x,

                    y,

                    x + panel_width,

                    y + panel_height

                )

                if not roof.contains(rect):

                    x += panel_width

                    continue

                blocked = False

                for obstacle in obstacle_polygons:

                    if rect.intersects(obstacle):

                        blocked = True

                        break

                if not blocked:

                    panels.append(

                        cls._panel_rect(

                            x,

                            y,

                            panel_width,

                            panel_height,

                            orientation

                        )

                    )

                x += panel_width

            y += panel_height

        return panels
        # --------------------------------------------------

    @classmethod
    def generate(

        cls,

        roof_points,

        panel="550W",

        obstacles=None

    ):

        if obstacles is None:

            obstacles = []

        roof = cls._roof_polygon(

            roof_points

        )

        if roof is None:

            return {

                "success": False,

                "message": "Invalid roof polygon.",

                "panels": [],

                "count": 0,

                "capacity": 0,

                "orientation": "Unknown",

                "utilization": 0,

                "roof_area": 0,

                "panel": panel

            }

        if panel not in cls.PANEL_DATABASE:

            panel = "550W"

        data = cls.PANEL_DATABASE[panel]

        obstacle_polygons = cls._obstacle_polygons(

            obstacles

        )

        # ------------------------------------------
        # Convert panel size from meters to pixels
        # ------------------------------------------

        portrait_w = (

            data["width"] /

            cls.PIXEL_TO_METER

        )

        portrait_h = (

            data["length"] /

            cls.PIXEL_TO_METER

        )

        landscape_w = (

            data["length"] /

            cls.PIXEL_TO_METER

        )

        landscape_h = (

            data["width"] /

            cls.PIXEL_TO_METER

        )

        portrait = cls._generate_layout(

            roof,

            obstacle_polygons,

            portrait_w,

            portrait_h,

            "Portrait"

        )

        landscape = cls._generate_layout(

            roof,

            obstacle_polygons,

            landscape_w,

            landscape_h,

            "Landscape"

        )

        if len(landscape) > len(portrait):

            panels = landscape

            orientation = "Landscape"

            panel_width = landscape_w

            panel_height = landscape_h

        else:

            panels = portrait

            orientation = "Portrait"

            panel_width = portrait_w

            panel_height = portrait_h

        count = len(panels)

        capacity = round(

            count *

            data["power"] /

            1000,

            2

        )

        roof_area_m2 = (

            roof.area *

            (cls.PIXEL_TO_METER ** 2)

        )

        panel_area = (

            count *

            data["length"] *

            data["width"]

        )

        utilization = 0

        if roof_area_m2 > 0:

            utilization = round(

                panel_area /

                roof_area_m2 *

                100,

                2

            )

        return {

            "success": True,

            "message": "Blueprint generated successfully.",

            "panel": panel,

            "panel_power": data["power"],

            "panel_size": (

                data["length"],

                data["width"]

            ),

            "panel_width_px": round(panel_width, 2),

            "panel_height_px": round(panel_height, 2),

            "orientation": orientation,

            "count": count,

            "capacity": capacity,

            "roof_area": round(

                roof_area_m2,

                2

            ),

            "utilization": utilization,

            "panels": panels

        }