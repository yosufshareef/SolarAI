"""
=========================================================
SolarTwin AI

AI Object Detection Engine

Version : 2.0

Uses YOLOv8 for rooftop obstacle detection.
=========================================================
"""

from dataclasses import dataclass
from typing import List, Dict

import cv2
from ultralytics import YOLO
import numpy as np

# ---------------------------------------------------------

@dataclass
class ObjectDetectionResult:

    success: bool

    detections: List[Dict]

    overlay: np.ndarray

    message: str


# ---------------------------------------------------------

class ObjectDetector:

    _model = None

    # Only keep useful rooftop obstacles
    VALID_CLASSES = {
        "person",
        "car",
        "truck",
        "bus",
        "motorcycle",
        "bicycle",
        "chair",
        "bench",
        "potted plant",
        "tv",
        "bird",
        "airplane",
        "boat"

    }

    def __init__(self):

        if ObjectDetector._model is None:

            ObjectDetector._model = YOLO("yolov8n.pt")

        self.model = ObjectDetector._model

    # ---------------------------------------------------------

    def detect(self, image, confidence=0.30):

        output = image.copy()

        detections = []

        results = self.model.predict(

            source=image,

            conf=confidence,

            verbose=False

        )

        for result in results:

            for box in result.boxes:

                x1, y1, x2, y2 = map(

                    int,

                    box.xyxy[0]

                )

                cls = int(box.cls[0])

                score = float(box.conf[0])

                label = self.model.names[cls]

                if label not in self.VALID_CLASSES:

                    continue

                detections.append({

                    "label": label,

                    "confidence": round(score, 2),

                    "bbox": (x1, y1, x2, y2)

                })

                cv2.rectangle(

                    output,

                    (x1, y1),

                    (x2, y2),

                    (0, 0, 255),

                    2

                )

                cv2.putText(

                    output,

                    f"{label} {score:.2f}",

                    (x1, max(20, y1 - 8)),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.55,

                    (0, 255, 0),

                    2

                )

        return ObjectDetectionResult(

            success=len(detections) > 0,

            detections=detections,

            overlay=output,

            message=f"{len(detections)} obstacle(s) detected."

        )