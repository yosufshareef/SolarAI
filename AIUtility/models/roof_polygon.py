"""
=========================================================

SolarTwin AI

Roof Polygon Domain Model

Enterprise Domain Object

Author : SolarTwin AI

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Any
from datetime import datetime


# ---------------------------------------------------------
# Point
# ---------------------------------------------------------

@dataclass
class Point:

    x: float
    y: float

    def to_tuple(self):

        return (self.x, self.y)


# ---------------------------------------------------------
# Bounding Box
# ---------------------------------------------------------

@dataclass
class BoundingBox:

    x_min: float = 0

    y_min: float = 0

    x_max: float = 0

    y_max: float = 0

    @property
    def width(self):

        return self.x_max - self.x_min

    @property
    def height(self):

        return self.y_max - self.y_min


# ---------------------------------------------------------
# Roof Polygon
# ---------------------------------------------------------

@dataclass
class RoofPolygon:

    # ---------------------------
    # Geometry
    # ---------------------------

    points: List[Point] = field(default_factory=list)

    bounding_box: BoundingBox = field(default_factory=BoundingBox)

    pixel_area: float = 0

    perimeter_pixels: float = 0

    # ---------------------------
    # Real World
    # ---------------------------

    pixel_to_meter_scale: float = 1.0

    area_sq_m: float = 0

    perimeter_m: float = 0

    # ---------------------------
    # AI
    # ---------------------------

    confidence: float = 0

    detected_by: str = "User"

    # ---------------------------
    # Orientation
    # ---------------------------

    rotation_deg: float = 0

    roof_pitch: float = 0

    azimuth: float = 0

    # ---------------------------
    # Metadata
    # ---------------------------

    image_width: int = 0

    image_height: int = 0

    created_time: str = field(
        default_factory=lambda:
        datetime.now().isoformat()
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # -----------------------------------------------------

    def point_list(self):

        return [

            p.to_tuple()

            for p in self.points

        ]

    # -----------------------------------------------------

    def add_point(self, x, y):

        self.points.append(

            Point(x, y)

        )

    # -----------------------------------------------------

    def clear(self):

        self.points.clear()

    # -----------------------------------------------------

    def total_points(self):

        return len(self.points)

    # -----------------------------------------------------

    def update_scale(

            self,

            pixels,

            meters

    ):

        if pixels <= 0:

            return

        self.pixel_to_meter_scale = (

            meters / pixels

        )

    # -----------------------------------------------------

    def update_area(

            self,

            pixel_area

    ):

        self.pixel_area = pixel_area

        self.area_sq_m = (

            pixel_area *

            self.pixel_to_meter_scale *

            self.pixel_to_meter_scale

        )

    # -----------------------------------------------------

    def update_perimeter(

            self,

            perimeter_pixels

    ):

        self.perimeter_pixels = perimeter_pixels

        self.perimeter_m = (

            perimeter_pixels *

            self.pixel_to_meter_scale

        )

    # -----------------------------------------------------

    def update_bbox(

            self

    ):

        if not self.points:

            return

        xs = [

            p.x

            for p in self.points

        ]

        ys = [

            p.y

            for p in self.points

        ]

        self.bounding_box = BoundingBox(

            min(xs),

            min(ys),

            max(xs),

            max(ys)

        )

    # -----------------------------------------------------

    def center(self):

        if not self.points:

            return (0, 0)

        x = sum(

            p.x

            for p in self.points

        ) / len(self.points)

        y = sum(

            p.y

            for p in self.points

        ) / len(self.points)

        return (

            round(x, 2),

            round(y, 2)

        )

    # -----------------------------------------------------

    def to_dict(self):

        data = asdict(self)

        data["points"] = [

            p.to_tuple()

            for p in self.points

        ]

        return data

    # -----------------------------------------------------

    @classmethod
    def from_points(

            cls,

            pts

    ):

        obj = cls()

        obj.points = [

            Point(x, y)

            for x, y in pts

        ]

        obj.update_bbox()

        return obj

    # -----------------------------------------------------

    def summary(self):

        return {

            "points":

                self.total_points(),

            "pixel_area":

                round(self.pixel_area, 2),

            "area_sq_m":

                round(self.area_sq_m, 2),

            "confidence":

                self.confidence,

            "detected_by":

                self.detected_by

        }   