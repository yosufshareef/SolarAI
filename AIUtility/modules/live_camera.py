import av
import cv2
import streamlit as st

from streamlit_webrtc import (
    VideoProcessorBase,
    webrtc_streamer
)

from ai.roof_detector import RoofDetector
from ai.object_detector import ObjectDetector
from services.geometry_engine import GeometryEngine


# ---------------------------------------------------------

class CameraProcessor(VideoProcessorBase):

    def __init__(self):

        self.frame = None

    def recv(self, frame):

        image = frame.to_ndarray(

            format="bgr24"

        )

        self.frame = image.copy()

        return av.VideoFrame.from_ndarray(

            image,

            format="bgr24"

        )


# ---------------------------------------------------------

def show_live_camera():

    st.title("📷 Live Roof Scanner")

    st.info(

        "Capture a rooftop image directly from your webcam."

    )

    if "project" not in st.session_state:

        st.session_state.project = {}

    project = st.session_state.project

    ctx = webrtc_streamer(

        key="live_camera",

        video_processor_factory=CameraProcessor,

        media_stream_constraints={

            "video": True,

            "audio": False

        },

        async_processing=True

    )

    if ctx.video_processor is None:

        return

    if not st.button(

        "📸 Capture Image",

    ):

        return

    frame = ctx.video_processor.frame

    if frame is None:

        st.error(

            "No frame captured."

        )

        return

    rgb = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2RGB

    )

    st.image(

        rgb,

        caption="Captured Frame",

        use_column_width=True

    )

    project["uploaded_images"] = [

        {

            "image": frame,

            "info": {},

            "validation": None

        }

    ]

    st.divider()

    st.subheader("🏠 Roof Detection")

    with st.spinner(

        "Running AI roof detection..."

    ):

        detector = RoofDetector()

        result = detector.detect(frame)

    overlay = cv2.cvtColor(

        result.overlay,

        cv2.COLOR_BGR2RGB

    )

    st.image(

        overlay,

        caption="Detected Roof Boundary",

        use_column_width=True

    )

    st.metric(

        "Detection Confidence",

        f"{result.confidence}%"

    )

    st.info(

        result.message

    )

    if result.success:

        project["roof_polygon"] = result.suggested_polygon

        geometry = GeometryEngine()

        roof_info = geometry.roof_summary(

            result.suggested_polygon

        )

        project["roof_info"] = roof_info
    else:

        st.warning(
            "Automatic roof detection was unsuccessful."
        )

        st.info(

            "You can continue with the Polygon Editor and draw the roof manually."

        )

    # ---------------------------------------------------------

    st.divider()

    st.subheader("🚧 Obstacle Detection")

    with st.spinner(

        "Detecting rooftop obstacles..."

    ):

        detector = ObjectDetector()

        annotated_image, detections = detector.detect(

            frame

        )

    project["obstacles"] = detections

    annotated_rgb = cv2.cvtColor(

        annotated_image,

        cv2.COLOR_BGR2RGB

    )

    st.image(

        annotated_rgb,

        caption="Detected Obstacles",

        use_container_width=True

    )

    c1, c2 = st.columns(2)

    c1.metric(

        "Objects Detected",

        len(detections)

    )

    c2.metric(

        "Roof Detected",

        "Yes" if result.success else "No"

    )

    if detections:

        with st.expander("Detected Objects"):

            st.json(detections)

    else:

        st.success(

            "No rooftop obstacles detected."

        )

    # ---------------------------------------------------------

    if result.success:

        info = project.get(

            "roof_info",

            {}

        )

        st.divider()

        st.subheader("📐 Roof Information")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(

            "Area",

            f'{info.get("area_m2",0):.2f} m²'

        )

        c2.metric(

            "Perimeter",

            f'{info.get("perimeter_m",0):.2f} m'

        )

        c3.metric(

            "Width",

            f'{info.get("width_m",0):.2f} m'

        )

        c4.metric(

            "Height",

            f'{info.get("height_m",0):.2f} m'

        )

    # ---------------------------------------------------------

    project["last_step"] = "Live Camera"

    st.divider()

    st.success(

        "✅ Live scan completed."

    )

    st.info(

        "Next → Open 🟩 Polygon Editor to verify or adjust the detected roof boundary before generating the blueprint."

    )