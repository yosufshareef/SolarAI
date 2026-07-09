import streamlit as st
from streamlit_option_menu import option_menu

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

# ----------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# CSS
# ----------------------------------------------------

st.markdown("""
<style>

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

.stApp{
background:#F3F6FB;
color:#1F2937;
}

.block-container{

padding-top:0rem;
padding-bottom:1rem;
padding-left:2rem;
padding-right:2rem;

}

section[data-testid="stSidebar"]{
    background:white;
    border-right:1px solid #E5E7EB;
    min-width:240px !important;
    max-width:240px !important;
}
.enterprise-header{

background:white;
padding:18px;
border-radius:14px;
margin-bottom:20px;
box-shadow:0 2px 10px rgba(0,0,0,.08);

}

.sidebar-category{

font-size:12px;
font-weight:700;
color:#6B7280;
letter-spacing:1px;
margin-top:18px;
margin-bottom:8px;

}

div[data-testid="metric-container"]{

background:white;
border-radius:12px;
padding:15px;
border:1px solid #ECECEC;
box-shadow:0 2px 8px rgba(0,0,0,.05);

}

.stButton>button{

width:100%;
height:44px;
border-radius:10px;
background:#1565C0;
color:white;
font-weight:600;
border:none;

}

.stButton>button:hover{

background:#0D47A1;
color:white;

}

/* ---------- Global Text ---------- */

html,
body,
p,
span,
label,
small,
strong,
div{
    color:#1F2937 !important;
}

h1,h2,h3,h4,h5,h6{
    color:#111827 !important;
}

.stMarkdown{
    color:#1F2937 !important;
}

.stTitle,
.stHeader,
.stSubheader{
    color:#111827 !important;
}

div[data-testid="metric-container"] label{
    color:#6B7280 !important;
}

div[data-testid="metric-container"] div{
    color:#111827 !important;
}

[data-testid="stDataFrame"]{
    color:#111827 !important;
}

label{
    color:#111827 !important;
}

button[data-baseweb="tab"]{
    color:#111827 !important;
}

.streamlit-expanderHeader{
    color:#111827 !important;
}

section[data-testid="stSidebar"] *{
    color:#1F2937;
}
/* Option Menu */

.nav-link{

color:#1F2937 !important;

font-weight:500 !important;

}

.nav-link:hover{

color:#1565C0 !important;

}

.nav-link.active{

color:white !important;

}

/* ===== Fixed Sidebar ===== */

section[data-testid="stSidebar"]{
    background:#FFFFFF;
    border-right:1px solid #E5E7EB;
}

/* Sidebar content */

section[data-testid="stSidebar"]{
    background:white;
    border-right:1px solid #E5E7EB;
}

section[data-testid="stSidebar"] > div:first-child{
}

section[data-testid="stSidebar"]{
    min-width:240px !important;
    max-width:240px !important;
}
            
</style>
""",unsafe_allow_html=True)


# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.markdown("""

<div class="enterprise-header">

<div style="display:flex;
justify-content:space-between;
align-items:center;">

<div>

<h1 style="margin:0;color:#1565C0;">
☀️ SolarTwin AI
</h1>

<div style="color:#666;">
Intelligent Rooftop Solar Planning Platform 🔹Powering smarter solar decisions
</div>

</div>

<div>

<b>Version</b><br>

v1.0

</div>

</div>

</div>

""",unsafe_allow_html=True)

UIEffects.inject_css()

# ----------------------------------------------------
# Initialize Project
# ----------------------------------------------------

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

# ----------------------------------------------------
# Sidebar Styles
# ----------------------------------------------------

MENU_STYLES = {

    "container": {
        "padding": "0!important",
        "background-color": "#FFFFFF",
    },

    "icon": {
        "color": "#1565C0",
        "font-size": "18px",
    },

    "nav-link": {
        "font-size": "14px",
        "text-align": "left",
        "margin": "1px",
        "padding": "6px 10px",
        "border-radius": "10px",
        "--hover-color": "#EAF2FF",
        "color": "#1F2937",          # <-- ADD
    },

    "nav-link-selected": {
        "background-color": "#1565C0",
        "color": "#FFFFFF",
    },

}

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

with st.sidebar:

    from PIL import Image
    import os
    logo_path = os.path.join("assests", "Logo.png")   # or "assests" if that's your actual folder name

    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.image(logo, width=180)
    else:
        st.warning("Logo not found.")
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

    page = option_menu(
        menu_title="Navigation",
        options=[
            "Home",
            "Manual Input",
            "Photo Upload",
            "Map Search",
            "Live Camera",
            "Polygon Editor",
            "Blueprint",
            "Dashboard",
            "AI Engineer",
            "Report",
        ],
        icons=[
            "house",
            "pencil-square",
            "image",
            "geo-alt",
            "camera",
            "bounding-box",
            "grid-3x3-gap",
            "bar-chart",
            "robot",
            "file-earmark-text",
        ],
        default_index=0,
        styles=MENU_STYLES,
    )


# ----------------------------------------------------
# Page Routing
# ----------------------------------------------------

PAGES = {

    "Home": show_home,

    "Manual Input": show_manual_input,

    "Photo Upload": show_photo_upload,

    "Map Search": show_map_search,

    "Live Camera": show_live_camera,

    "Polygon Editor": show_polygon_editor,

    "Blueprint": show_blueprint,

    "Dashboard": show_dashboard,

    "AI Engineer": show_ai_chat,

    "Report": show_report,

}

if page in PAGES:
    PAGES[page]()
else:
    show_home()

# ----------------------------------------------------
# Footer
# ----------------------------------------------------

UIEffects.footer()

