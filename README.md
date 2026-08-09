# Multi-Agent Research Dashboard

Planner → Researcher → Critic → Decision → Reporting, with a live retry loop,
wrapped in a Streamlit dashboard.

## Project structure

```
task2/
├── agent/
│   ├── __init__.py     # public surface: app, ResearchState, constants
│   ├── state.py         # ResearchState schema + QUALITY_THRESHOLD / MAX_RETRIES
│   ├── llm.py            # ChatGroq factory + token extraction (falls back to mock)
│   ├── rag.py             # lightweight retrieval over uploaded docs
│   ├── models.py           # Pydantic FinalReport (validated output)
│   ├── nodes.py             # planner, researcher, critic, decision, reporting
│   ├── router.py             # should_retry conditional edge
│   └── graph.py               # build_graph() -> compiled LangGraph app
├── app.py                # Streamlit dashboard (imports agent, no agent logic)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup — local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste your GROQ_API_KEY
streamlit run app.py
```

Without a `GROQ_API_KEY`, every node falls back to a deterministic mock —
the graph, the retry loop, and the UI all still run end to end. This is
intentional: it's how you demo the retry cycle without burning API calls.

## Screenshots

...

## Checklist before submitting

- [X] Fresh clone, fresh venv, `pip install -r requirements.txt`, `streamlit run app.py` — works
- [X] No `.env` or real keys committed
- [ ] A full run completes without a traceback
- [ ] Demo shows a real failed check, a real retry, a real approval
- [ ] Token counter is non-zero and increases as the run proceeds
- [X] Downloaded `.md` opens and contains the structured report
- [ ] Retry cap tested: an objective that never reaches 0.8 still terminates
