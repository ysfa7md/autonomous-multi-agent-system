import streamlit as st
import pandas as pd
import os
import re
import time


# '''
# - chat interface
# - file upload
# - sidebar
#     - temp
#     - api-key
#     - model
# - token counter
# - state view
# - download markdown


# '''

# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="AI Operations Dashboard",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# Session State
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tokens" not in st.session_state:
    st.session_state.tokens = 0

if "last_report" not in st.session_state:
    st.session_state.last_report = ""


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.header("⚙️ Controls")

    model = st.selectbox(
        "Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-20b",
        ],
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
    )

    st.metric(
        "Tokens used (session)",
        st.session_state.tokens,
    )

    if st.button("Reset chat"):
        st.session_state.messages = []
        st.session_state.tokens = 0
        st.session_state.last_report = ""

        st.rerun()


# ============================================================
# Main UI
# ============================================================

st.title("🤖 AI Operations Dashboard")

st.caption(
    "Multi-agent research system · streaming · token tracking"
)


# ============================================================
# Display previous messages
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# Chat Input
# ============================================================

prompt = st.chat_input(
    "Enter a research objective..."
)


# ============================================================
# Run Agent
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    # --------------------------------------------------------
    # Assistant response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        # Status container
        with st.status(
            "Agent working...",
            expanded=True,
        ) as status:

            final_report = ""

            try:

                # ------------------------------------------------
                # Replace this with your actual agent
                # ------------------------------------------------

                for node, message, tokens in run_agent(
                    prompt,
                    model=model,
                    temperature=temperature,
                ):

                    # Update token counter
                    st.session_state.tokens += tokens


                    # --------------------------------------------
                    # Final report
                    # --------------------------------------------

                    if node == "report":

                        final_report = message

                        st.write(
                            "📝 **Report** → final report ready"
                        )


                    # --------------------------------------------
                    # Agent steps
                    # --------------------------------------------

                    else:

                        icons = {
                            "planner": "🧭",
                            "research": "🔎",
                            "critic": "🧐",
                            "decision": "⚖️",
                        }

                        icon = icons.get(
                            node,
                            "•",
                        )

                        st.write(
                            f"{icon} **{node}** → {message}"
                        )


                # Agent finished
                status.update(
                    label="Done ✅",
                    state="complete",
                )


            except Exception as e:

                status.update(
                    label="Error",
                    state="error",
                )

                st.error(
                    f"Agent failed: {e}"
                )


        # --------------------------------------------------------
        # Display final report
        # --------------------------------------------------------

        if final_report:

            st.markdown("### Final Report")

            st.markdown(final_report)

            # Save report in session
            st.session_state.last_report = final_report

            # Save assistant message
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": final_report,
                }
            )


# ============================================================
# Export Report
# ============================================================

if st.session_state.last_report:

    st.download_button(
        label="⬇️ Export report (Markdown)",
        data=st.session_state.last_report,
        file_name="agent_report.md",
        mime="text/markdown",
    )
