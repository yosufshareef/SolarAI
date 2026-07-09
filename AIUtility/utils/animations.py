import time
import streamlit as st


class UIEffects:

    @staticmethod
    def inject_css():

        st.markdown("""
        <style>

        .main{
            padding-top:1rem;
        }

        .glass{

            background:rgba(255,255,255,0.08);

            border-radius:16px;

            padding:18px;

            border:1px solid rgba(255,255,255,0.15);

            box-shadow:0 6px 20px rgba(0,0,0,.15);

            margin-bottom:12px;

        }

        .successCard{

            background:#E8F5E9;

            border-left:6px solid #43A047;

            padding:12px;

            border-radius:8px;

            margin-bottom:10px;

        }

        .warningCard{

            background:#FFF8E1;

            border-left:6px solid #FFA000;

            padding:12px;

            border-radius:8px;

            margin-bottom:10px;

        }

        .dangerCard{

            background:#FBE9E7;

            border-left:6px solid #E53935;

            padding:12px;

            border-radius:8px;

            margin-bottom:10px;

        }

        div.stButton>button{

            width:100%;

            height:48px;

            border-radius:10px;

            font-weight:bold;

        }

        </style>

        """, unsafe_allow_html=True)

    # -------------------------------------------------

    @staticmethod
    def hero(title, subtitle):

        st.markdown(f"""

        <div class="glass">

        <h1>{title}</h1>

        <p>{subtitle}</p>

        </div>

        """, unsafe_allow_html=True)

    # -------------------------------------------------

    @staticmethod
    def success(message):

        st.markdown(

            f"""

            <div class="successCard">

            ✅ {message}

            </div>

            """,

            unsafe_allow_html=True

        )

    # -------------------------------------------------

    @staticmethod
    def warning(message):

        st.markdown(

            f"""

            <div class="warningCard">

            ⚠️ {message}

            </div>

            """,

            unsafe_allow_html=True

        )

    # -------------------------------------------------

    @staticmethod
    def danger(message):

        st.markdown(

            f"""

            <div class="dangerCard">

            ❌ {message}

            </div>

            """,

            unsafe_allow_html=True

        )

    # -------------------------------------------------

    @staticmethod
    def loading(text="Processing..."):

        progress = st.progress(0)

        status = st.empty()

        for i in range(101):

            progress.progress(i)

            status.write(f"{text} {i}%")

            time.sleep(0.01)

        status.empty()

        progress.empty()

    # -------------------------------------------------

    @staticmethod
    def step(title):

        st.markdown(f"## {title}")

    # -------------------------------------------------

    @staticmethod
    def badge(text):

        st.markdown(

            f"<span style='background:#1976D2;color:white;padding:6px 12px;border-radius:20px'>{text}</span>",

            unsafe_allow_html=True

        )

    # -------------------------------------------------

    @staticmethod
    def divider():

        st.markdown("---")

    # -------------------------------------------------

    @staticmethod
    def footer():

        st.markdown("""

        <hr>

        <center>

        <small>

        SolarTwin AI • IntelliAutomators Solution • LTTS

        </small>

        </center>

        """, unsafe_allow_html=True)