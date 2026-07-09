"""
=========================================================
SolarTwin AI

Roof Detection Engine (AI Assisted)

Version : 3.0
=========================================================
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

import cv2
import numpy as np


# ---------------------------------------------------------

@dataclass
class RoofDetectionResult:

    success: bool

    confidence: float

    message: str

    suggested_polygon: Optional[List[Tuple[int, int]]]

    overlay: np.ndarray

    edge_image: np.ndarray


# ---------------------------------------------------------

class RoofDetector:

    MIN_CONTOUR_AREA = 5000

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def enhance(self, image):

        if len(image.shape) == 3:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

        else:

            gray = image.copy()

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        return clahe.apply(gray)

    # ---------------------------------------------------------

    def detect_edges(self, image):

        blur = cv2.GaussianBlur(
            image,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blur,
            60,
            180
        )

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        edges = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel
        )

        edges = cv2.dilate(
            edges,
            kernel,
            iterations=1
        )

        return edges

    # ---------------------------------------------------------

    def largest_polygon(self, edge_image):

        contours, _ = cv2.findContours(

            edge_image,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )

        if not contours:

            return None

        largest = max(

            contours,

            key=cv2.contourArea

        )

        area = cv2.contourArea(largest)

        if area < self.MIN_CONTOUR_AREA:

            return None

        epsilon = 0.02 * cv2.arcLength(

            largest,

            True

        )

        polygon = cv2.approxPolyDP(

            largest,

            epsilon,

            True

        )

        return [

            (int(p[0][0]), int(p[0][1]))

            for p in polygon

        ]

    # ---------------------------------------------------------

    def draw_polygon(self, image, polygon):

        output = image.copy()

        if polygon is None:

            return output

        pts = np.array(

            polygon,

            dtype=np.int32

        ).reshape((-1, 1, 2))

        cv2.polylines(

            output,

            [pts],

            True,

            (0, 255, 0),

            3

        )

        for x, y in polygon:

            cv2.circle(

                output,

                (x, y),

                5,

                (0, 0, 255),

                -1

            )

        return output

    # ---------------------------------------------------------

    def confidence(self, polygon):

        if polygon is None:

            return 0

        area = cv2.contourArea(

            np.array(

                polygon,

                dtype=np.int32

            )

        )

        vertices = len(polygon)

        score = 60

        if area > 15000:

            score += 20

        elif area > 8000:

            score += 10

        if vertices == 4:

            score += 15

        elif vertices <= 6:

            score += 10

        elif vertices <= 8:

            score += 5

        return min(score, 98)

    # ---------------------------------------------------------

    def detect(self, image):

        enhanced = self.enhance(image)

        edges = self.detect_edges(enhanced)

        polygon = self.largest_polygon(edges)

        overlay = self.draw_polygon(

            image,

            polygon

        )

        score = self.confidence(polygon)

        success = polygon is not None

        if success:

            message = (
                "Roof detected successfully. "
                "Verify polygon before continuing."
            )

        else:

            message = (
                "Roof detection failed. "
                "Please adjust polygon manually."
            )

        return RoofDetectionResult(

            success=success,

            confidence=score,

            message=message,

            suggested_polygon=polygon,

            overlay=overlay,

            edge_image=edges

        )