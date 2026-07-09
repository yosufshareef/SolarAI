import streamlit as st

from ai.ai_engine import AIEngine


def show_ai_chat():

    st.title("🤖 Solar AI Engineer")

    if "project" not in st.session_state:

        st.warning("No active project.")

        return

    project = st.session_state.project

    ai = AIEngine()

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    st.info(
        "Ask anything about your solar project."
    )

    suggestions = [

        "How many solar panels fit on my roof?",

        "What is the estimated solar capacity?",

        "Why was this panel orientation selected?",

        "What is the expected annual energy generation?",

        "What is the estimated ROI?",

        "How much money will I save each year?",

        "Can I increase the number of panels?",

        "How do rooftop obstacles affect the design?",

        "What are your recommendations?",

        "Give me the executive project summary."

    ]

    selected = st.selectbox(

        "Quick Questions",

        [""] + suggestions

    )

    question = st.text_input(

        "Ask Solar AI",

        value=selected

    )

    if st.button("Ask AI"):

        if question.strip() == "":

            st.warning("Enter a question.")

        else:

            answer = ai.answer(

                question,

                project

            )

            st.session_state.chat_history.append(

                {

                    "question": question,

                    "answer": answer

                }

            )

    st.divider()

    for chat in reversed(

        st.session_state.chat_history

    ):

        with st.chat_message("user"):

            st.write(chat["question"])

        with st.chat_message("assistant"):

            st.write(chat["answer"])

    st.divider()

    st.subheader("📋 AI Project Insights")

    try:

        summary = project.get("ai_summary")

        if summary is None:

            summary = ai.generate_summary(project)

            project["ai_summary"] = summary

        c1, c2 = st.columns(2)

        c1.metric(

            "Capacity",

            f'{summary["capacity"]:.2f} kW'

        )

        c2.metric(

            "Panels",

            summary["panels"]

        )

        st.success(

            f"Roof Area : {summary['roof_area']:.2f} m²"

        )

        st.success(

            f"Orientation : {summary['orientation']}"

        )

        st.success(

            f"Location : {summary['location']}"

        )

    except Exception as e:

        st.warning(

            f"Unable to display AI insights: {e}"

        )

    st.divider()

    st.subheader("⚡ AI Suggestions")

    recommendations = project.get("recommendations")

    if recommendations is None:

        recommendations = ai.recommendations(project)

        project["recommendations"] = recommendations

    for tip in recommendations:

        st.success(tip)

    st.divider()

    if st.button("Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()