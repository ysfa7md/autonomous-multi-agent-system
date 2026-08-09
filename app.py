
# # '''
# # - chat interface
# # - file upload
# # - sidebar
# #     - temp
# #     - api-key
# #     - model
# # - token counter
# # - state view
# # - download markdown


import streamlit as st

from agent import app as agent_app, QUALITY_THRESHOLD, MAX_RETRIES, initial_state
from agent.rag import load_pdf, chunk_text

st.set_page_config(
    page_title="Multi-Agent Research Dashboard", page_icon="🤖", layout="wide"
)

# ============================================================
# Session state
# ============================================================
_DEFAULTS = {
    "messages": [],
    "tokens": 0,
    "context_docs": [],
    "last_report": "",
    "last_log": [],
}
for _key, _value in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.header("⚙️ Controls")

    model = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b"],
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)

    st.divider()
    st.subheader("📄 Knowledge source")
    uploaded_files = st.file_uploader(
        "Upload documents for the Researcher",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        chunks = []
        for f in uploaded_files:
            raw = f.read()
            if f.type == "application/pdf":
                chunks += load_pdf(raw)
            else:
                chunks += chunk_text(raw.decode("utf-8", errors="ignore"))
        st.session_state.context_docs = chunks
        st.success(f"{len(chunks)} chunks indexed from {len(uploaded_files)} file(s)")

    st.divider()
    st.metric("Tokens used (session)", st.session_state.tokens)
    st.caption(
        f"Quality threshold: **{QUALITY_THRESHOLD}** · Max retries: **{MAX_RETRIES}**"
    )

    if st.button("Reset chat"):
        for _key, _value in _DEFAULTS.items():
            st.session_state[_key] = _value
        st.rerun()

# ============================================================
# Header
# ============================================================
st.title("🤖 Multi-Agent Research Dashboard")
st.caption(
    "Planner → Researcher → Critic → Decision → Reporting — with a live, visible retry loop"
)

# ============================================================
# Chat history
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter a research objective...")

ICONS = {
    "planner": "🧭",
    "researcher": "🔎",
    "critic": "🧐",
    "decision": "⚖️",
    "reporting": "📝",
}

# ============================================================
# Run agent
# ============================================================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        state_view = st.empty()
        final_report = ""
        current_state = dict(
            initial_state(
                goal=prompt,
                context_docs=st.session_state.context_docs,
                model=model,
                temperature=temperature,
            )
        )

        with st.status("Agent working...", expanded=True) as status:
            try:
                for update in agent_app.stream(current_state):
                    for node_name, partial in update.items():
                        current_state.update(partial)
                        icon = ICONS.get(node_name, "•")

                        if node_name == "planner":
                            st.write(
                                f"{icon} **Planner** → {len(current_state['tasks'])} tasks planned"
                            )
                        elif node_name == "researcher":
                            st.write(
                                f"{icon} **Researcher** → {len(current_state['findings'])} findings gathered"
                            )
                        elif node_name == "critic":
                            gap = current_state["critique"][:60] or "no gaps"
                            st.write(
                                f"{icon} **Critic** → score {round(current_state['quality_score'], 2)} ({gap})"
                            )
                        elif node_name == "decision":
                            verdict = (
                                "RETRY"
                                if current_state["log"][-1].endswith("RETRY")
                                else "APPROVE"
                            )
                            st.write(
                                f"{icon} **Decision** → retry_count={current_state['retry_count']} → {verdict}"
                            )
                        elif node_name == "reporting":
                            final_report = current_state["report"]
                            st.write(f"{icon} **Reporting** → final report assembled")

                        st.session_state.tokens = current_state["total_tokens"]

                        with state_view.container():
                            st.markdown("##### 📊 Live state")
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Tasks", len(current_state.get("tasks", [])))
                            c2.metric(
                                "Quality score",
                                round(current_state.get("quality_score", 0.0), 2),
                            )
                            c3.metric(
                                "Retry count",
                                f"{current_state.get('retry_count', 0)}/{MAX_RETRIES}",
                            )

                status.update(label="Done ✅", state="complete")

            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"Agent failed: {e}")

        if final_report:
            st.markdown("### Final Report")
            st.markdown(final_report)

            with st.expander("🕓 Full cycle log (per-node trace)"):
                for line in current_state.get("log", []):
                    st.text(line)

            st.session_state.last_report = final_report
            st.session_state.last_log = current_state.get("log", [])
            st.session_state.messages.append(
                {"role": "assistant", "content": final_report}
            )


if st.session_state.last_report:
    st.download_button(
        "⬇️ Export report (Markdown)",
        data=st.session_state.last_report,
        file_name="agent_report.md",
        mime="text/markdown",
    )
