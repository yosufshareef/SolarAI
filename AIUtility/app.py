import streamlit as st

from config import *

from modules.home import show_home
from modules.manual_input import show_manual_input
from modules.photo_upload import show_photo_upload
from modules.map_search import show_map_search
from modules.live_camera import show_live_camera
from modules.polygon_editor import show_polygon_editor
from modules.blueprint import show_blueprint
from modules.dashboard import show_dashboard
from modules.report import show_report
from modules.ai_chat import show_ai_chat
from utils.animations import UIEffects


# --------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

UIEffects.inject_css()

# --------------------------------------------------------
# Initialize Project
# --------------------------------------------------------

if "project" not in st.session_state:

    st.session_state.project = {

        "uploaded_images": [],

        "roof_polygon": [],

        "roof_info": {},

        "location": {},

        "obstacles": [],

        "blueprint": {},

        "weather": {},

        "generation": {},

        "roi": {},

        "recommendations": []

    }

# --------------------------------------------------------

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/169/169367.png",
    width=80
)

UIEffects.hero(
    "☀ SolarTwin AI",
    "Intelligent Rooftop Solar Planning Platform"
)

# --------------------------------------------------------

PAGES = {

    "🏠 Home": show_home,

    "✍ Manual Input": show_manual_input,

    "📸 Photo Upload": show_photo_upload,

    "🌍 Map Search": show_map_search,

    "📷 Live Camera": show_live_camera,

    "🟩 Polygon Editor": show_polygon_editor,

    "📐 Blueprint": show_blueprint,

    "📊 Dashboard": show_dashboard,

    "🤖 AI Engineer": show_ai_chat,

    "📑 Report": show_report

}

# --------------------------------------------------------

page = st.sidebar.radio(

    "Navigation",

    list(PAGES.keys())

)

PAGES[page]()

# --------------------------------------------------------

UIEffects.footer()