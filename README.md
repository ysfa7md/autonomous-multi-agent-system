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

## Setup — Colab tunnel

```python
!pip install -r requirements.txt
!wget -q -O - ipv4.icanhazip.com   # note the IP, used as the tunnel password
!streamlit run app.py & npx localtunnel --port 8501
```

Open the printed `localtunnel` URL and paste the IP as the tunnel password.

## How the retry loop works

1. `decision` checks `quality_score` vs `QUALITY_THRESHOLD` (0.8). If below
   and `retry_count < MAX_RETRIES` (2), it increments `retry_count`.
2. `should_retry` (the conditional edge) reads that already-incremented
   `retry_count` and returns `"retry"` (→ back to `planner`, which re-plans
   using `critique`) or `"approve"` (→ `reporting`).
3. If the cap is reached before the score clears the threshold, the graph
   still approves — `reporting` flags the report as **accepted below
   threshold** instead of looping forever.

Without an API key, the mock Critic always scores the first pass at 0.55
(below threshold) and the second pass at 0.9, so a real retry → approve
cycle is guaranteed on every run for the demo.

## Screenshots

_(add 2–3 screenshots here: objective entered → reasoning stream → retry →
approval → exported Markdown)_

## Checklist before submitting

- [ ] Fresh clone, fresh venv, `pip install -r requirements.txt`, `streamlit run app.py` — works
- [ ] No `.env` or real keys committed
- [ ] A full run completes without a traceback
- [ ] Demo shows a real failed check, a real retry, a real approval
- [ ] Token counter is non-zero and increases as the run proceeds
- [ ] Downloaded `.md` opens and contains the structured report
- [ ] Retry cap tested: an objective that never reaches 0.8 still terminates
