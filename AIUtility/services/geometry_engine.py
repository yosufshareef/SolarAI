import math
import cv2
import numpy as np

from shapely.geometry import Polygon, Point


class GeometryEngine:

    DEFAULT_PIXEL_TO_METER = 0.05

    def __init__(self, pixel_to_meter=None):

        self.scale = pixel_to_meter or self.DEFAULT_PIXEL_TO_METER

    # --------------------------------------------------

    def _valid(self, points):

        return points is not None and len(points) >= 3

    # --------------------------------------------------

    def polygon(self, points):

        if not self._valid(points):
            return None

        try:
            return Polygon(points)
        except Exception:
            return None

    # --------------------------------------------------

    def area_pixels(self, points):

        poly = self.polygon(points)

        if poly is None:
            return 0.0

        return float(abs(poly.area))

    # --------------------------------------------------

    def area_m2(self, points):

        return self.area_pixels(points) * (self.scale ** 2)

    # --------------------------------------------------

    def perimeter_pixels(self, points):

        poly = self.polygon(points)

        if poly is None:
            return 0.0

        return float(poly.length)

    # --------------------------------------------------

    def perimeter_m(self, points):

        return self.perimeter_pixels(points) * self.scale

    # --------------------------------------------------

    def centroid(self, points):

        poly = self.polygon(points)

        if poly is None:
            return (0.0, 0.0)

        c = poly.centroid

        return (

            round(float(c.x), 2),

            round(float(c.y), 2)

        )

    # --------------------------------------------------

    def bounding_box(self, points):

        poly = self.polygon(points)

        if poly is None:

            return {

                "xmin": 0,

                "ymin": 0,

                "xmax": 0,

                "ymax": 0,

                "width": 0,

                "height": 0

            }

        minx, miny, maxx, maxy = poly.bounds

        return {

            "xmin": round(float(minx), 2),

            "ymin": round(float(miny), 2),

            "xmax": round(float(maxx), 2),

            "ymax": round(float(maxy), 2),

            "width": round(float(maxx - minx), 2),

            "height": round(float(maxy - miny), 2)

        }

    # --------------------------------------------------

    def dimensions_m(self, points):

        bbox = self.bounding_box(points)

        return {

            "width": bbox["width"] * self.scale,

            "height": bbox["height"] * self.scale

        }

    # --------------------------------------------------

    def orientation(self, points):

        if not self._valid(points):

            return 0.0

        pts = np.array(

            points,

            dtype=np.float32

        )

        rect = cv2.minAreaRect(pts)

        angle = rect[-1]

        if angle < -45:
            angle += 90

        return round(float(angle), 2)

    # --------------------------------------------------

    def convex_hull(self, points):

        poly = self.polygon(points)

        if poly is None:
            return []

        hull = poly.convex_hull

        return [

            (float(x), float(y))

            for x, y in hull.exterior.coords

        ]

    # --------------------------------------------------

    def compactness(self, points):

        poly = self.polygon(points)

        if poly is None:
            return 0.0

        area = poly.area

        perimeter = poly.length

        if perimeter == 0:

            return 0.0

        return float(

            4 * math.pi * area /

            (perimeter * perimeter)

        )

    # --------------------------------------------------

    def roof_summary(self, points):

        if not self._valid(points):

            return {

                "area_px": 0,

                "area_m2": 0,

                "perimeter_m": 0,

                "orientation": 0,

                "compactness": 0,

                "width_m": 0,

                "height_m": 0,

                "bbox": {},

                "centroid": (0, 0)

            }

        bbox = self.bounding_box(points)

        dims = self.dimensions_m(points)

        return {

            "area_px":

                round(

                    self.area_pixels(points),

                    2

                ),

            "area_m2":

                round(

                    self.area_m2(points),

                    2

                ),

            "perimeter_m":

                round(

                    self.perimeter_m(points),

                    2

                ),

            "orientation":

                self.orientation(points),

            "compactness":

                round(

                    self.compactness(points),

                    3

                ),

            "width_m":

                round(

                    dims["width"],

                    2

                ),

            "height_m":

                round(

                    dims["height"],

                    2

                ),

            "bbox":

                bbox,

            "centroid":

                self.centroid(points)

        }

    # --------------------------------------------------

    def point_inside(self, point, polygon):

        poly = self.polygon(polygon)

        if poly is None:

            return False

        return poly.contains(

            Point(point)

        )

    # --------------------------------------------------

    def polygon_inside(self, polygon1, polygon2):

        p1 = self.polygon(polygon1)

        p2 = self.polygon(polygon2)

        if p1 is None or p2 is None:

            return False

        return p2.contains(p1)

    # --------------------------------------------------

    def distance(self, p1, p2):

        return float(

            math.sqrt(

                (p1[0] - p2[0]) ** 2 +

                (p1[1] - p2[1]) ** 2

            )

        )

    # --------------------------------------------------

    def translate(self, points, dx, dy):

        return [

            (

                x + dx,

                y + dy

            )

            for x, y in points

        ]

    # --------------------------------------------------

    def rotate(self, points, angle):

        if not self._valid(points):

            return []

        angle = math.radians(angle)

        cx, cy = self.centroid(points)

        rotated = []

        cos_a = math.cos(angle)

        sin_a = math.sin(angle)

        for x, y in points:

            tx = x - cx

            ty = y - cy

            rx = tx * cos_a - ty * sin_a

            ry = tx * sin_a + ty * cos_a

            rotated.append(

                (

                    round(rx + cx, 2),

                    round(ry + cy, 2)

                )

            )

        return rotated