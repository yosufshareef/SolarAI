import streamlit as st
import os
from ai.ai_engine import AIEngine
from streamlit_mic_recorder import speech_to_text

def show_ai_chat():

    st.title("🤖 AI Engineer")

    st.caption(
        "Powered by Claude AI"
    )

    ai = AIEngine()

    pdf_path = os.path.join(
        "exports",
        "SolarTwin_Report.pdf"
    )

    if os.path.exists(pdf_path):
        ai.load_report(pdf_path)
    else:
        st.warning(
            "⚠ Generate the Enterprise PDF Report first."
        )

    if "messages" not in st.session_state:

        st.session_state.messages = [

            {

                "role":"assistant",

                "content":
                "Hello 👋\n\n"
                "I have loaded your generated SolarTwin Report.\n\n"
                "Ask me anything about your project."

            }

        ]

    left,right = st.columns([3,1])

    with left:

        if os.path.exists(pdf_path):

            st.success("📄 SolarTwin_Report.pdf Loaded")

        else:

            st.error("❌ Report not found")

    with right:

        if st.button("🗑 Clear Chat"):

            st.session_state.messages=[

                {

                    "role":"assistant",

                    "content":
                    "Chat cleared. Ask me anything."

                }

            ]

            st.rerun()
        # --------------------------------------------------
    # Conversation
    # --------------------------------------------------

    st.divider()

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(

                message["content"]

            )

    st.divider()

    col1, col2 = st.columns([8,0.5])

    with col1:

        question = st.chat_input(
            "Ask anything about your SolarTwin project...",
            key="solar_chat_input"
        )

    with col2:

        voice_text = speech_to_text(

            start_prompt="🎙️",

            stop_prompt="⏹ Stop",

            language="en",

            just_once=True,

            use_container_width=True,

            key="voice_input"

        )
        '''
        st.write("Voice Text :", voice_text)
        if voice_text is not None and voice_text.strip():

            question = voice_text
        '''
        # --------------------------------------------------
    # Ask Claude
    # --------------------------------------------------

    if question:

        # Show user message immediately
        st.session_state.messages.append(

            {

                "role": "user",

                "content": question

            }

        )

        with st.chat_message("user"):

            st.markdown(question)

        # Claude response
        with st.chat_message("assistant"):

            with st.spinner("🧠 AI Engineer is analyzing your SolarTwin Report..."):

                try:

                    answer = ai.ask_pdf(question)

                except Exception as e:

                    answer = (

                        "❌ Unable to contact Claude API.\n\n"

                        f"{e}"

                    )

                st.markdown(answer)

        # Save assistant response

        st.session_state.messages.append(

            {

                "role": "assistant",

                "content": answer

            }

        )

        # Refresh chat

        st.rerun()

            # --------------------------------------------------
    # Enterprise Information Panel
    # --------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(
            "🤖 Claude Sonnet 5"
        )

    with c2:

        st.success(
            "📄 Report Loaded"
        )

    with c3:

        st.info(
            "💬 Chat Mode"
        )

    with st.expander("ℹ AI Engineer"):

        st.markdown("""

### SolarTwin AI Engineer

This assistant automatically analyzes the generated **SolarTwin Report** and answers questions using Claude AI.

**Knowledge Source**

- Generated Enterprise PDF Report
- Solar Engineering Knowledge
- Rooftop Design Recommendations

**You can ask:**

- Explain my report
- Annual generation
- ROI
- Panel count
- Orientation
- Roof utilization
- CO₂ savings
- Payback period
- Executive summary
- Improvement suggestions
- General solar questions

""")