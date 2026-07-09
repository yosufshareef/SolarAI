"""
=========================================================
SolarTwin AI
Image Validation Module

Author : SolarTwin AI
Version: 1.0

Enterprise Image Validation Engine

This module validates uploaded images before AI processing.

Checks
-------
✔ Resolution
✔ Blur
✔ Brightness
✔ Contrast
✔ Empty Image
✔ File Size
✔ Image Channels

Returns
-------
ImageValidationResult Dataclass
=========================================================
"""

from dataclasses import dataclass, field
from typing import List
import logging

import cv2
import numpy as np


# --------------------------------------------------------
# Logging
# --------------------------------------------------------

logger = logging.getLogger(__name__)


# --------------------------------------------------------
# Dataclass
# --------------------------------------------------------

@dataclass
class ImageValidationResult:

    is_valid: bool

    quality_score: int

    resolution: tuple

    blur_score: float

    brightness: float

    contrast: float

    file_size_mb: float

    messages: List[str] = field(default_factory=list)


# --------------------------------------------------------
# Validator
# --------------------------------------------------------

class ImageValidator:

    # Minimum requirements

    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    MIN_BLUR = 90

    MIN_BRIGHTNESS = 40
    MAX_BRIGHTNESS = 220

    MIN_CONTRAST = 20

    MAX_FILE_MB = 30

    # ----------------------------------------------------

    @staticmethod
    def validate(image: np.ndarray, file_size_mb: float = 0.0):

        messages = []

        score = 100

        valid = True

        if image is None:

            return ImageValidationResult(
                False,
                0,
                (0, 0),
                0,
                0,
                0,
                file_size_mb,
                ["Image could not be loaded."]
            )

        h, w = image.shape[:2]

        resolution = (w, h)

        # ----------------------------------------------
        # Resolution
        # ----------------------------------------------

        if w < ImageValidator.MIN_WIDTH or h < ImageValidator.MIN_HEIGHT:

            score -= 20

            valid = False

            messages.append(
                f"Low Resolution ({w}x{h}). "
                f"Minimum recommended is "
                f"{ImageValidator.MIN_WIDTH}x{ImageValidator.MIN_HEIGHT}."
            )

        # ----------------------------------------------
        # Blur
        # ----------------------------------------------

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        blur_score = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        if blur_score < ImageValidator.MIN_BLUR:

            score -= 25

            valid = False

            messages.append(
                "Image appears blurry. "
                "Please retake from a stable position."
            )

        # ----------------------------------------------
        # Brightness
        # ----------------------------------------------

        brightness = np.mean(gray)

        if brightness < ImageValidator.MIN_BRIGHTNESS:

            score -= 15

            valid = False

            messages.append(
                "Image is too dark."
            )

        elif brightness > ImageValidator.MAX_BRIGHTNESS:

            score -= 10

            messages.append(
                "Image is over exposed."
            )

        # ----------------------------------------------
        # Contrast
        # ----------------------------------------------

        contrast = gray.std()

        if contrast < ImageValidator.MIN_CONTRAST:

            score -= 10

            messages.append(
                "Low contrast detected."
            )

        # ----------------------------------------------
        # Empty image
        # ----------------------------------------------

        unique = np.unique(gray)

        if len(unique) < 15:

            score -= 50

            valid = False

            messages.append(
                "Image appears empty or almost blank."
            )

        # ----------------------------------------------
        # File size
        # ----------------------------------------------

        if file_size_mb > ImageValidator.MAX_FILE_MB:

            score -= 5

            messages.append(
                "Large image size may increase processing time."
            )

        # ----------------------------------------------
        # Channels
        # ----------------------------------------------

        if len(image.shape) != 3:

            score -= 10

            valid = False

            messages.append(
                "Unsupported image format."
            )

        score = max(score, 0)

        if valid:

            messages.append("Image validation passed.")

        logger.info(
            "Validation completed. Score=%d",
            score
        )

        return ImageValidationResult(

            is_valid=valid,

            quality_score=score,

            resolution=resolution,

            blur_score=round(blur_score, 2),

            brightness=round(brightness, 2),

            contrast=round(contrast, 2),

            file_size_mb=round(file_size_mb, 2),

            messages=messages

        )


# --------------------------------------------------------
# Helper
# --------------------------------------------------------

def quality_badge(score: int):

    if score >= 90:
        return "🟢 Excellent"

    if score >= 75:
        return "🟡 Good"

    if score >= 60:
        return "🟠 Fair"

    return "🔴 Poor"