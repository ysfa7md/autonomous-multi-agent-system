from typing import TypedDict


QUALITY_THRESHOLD = 0.8
MAX_RETRIES = 2


class ResearchState(TypedDict):
    goal: str  # user's research objective
    tasks: list[str]  # produced by Planner
    findings: list[str]  # produced by Researcher
    critique: str  # Critic's written feedback / gaps
    quality_score: float  # 0.0 - 1.0, produced by Critic
    retry_count: int  # incremented on every loop back
    report: str  # final structured report (markdown)

    # --- extra fields (allowed on top of the minimum contract) ---
    context_docs: list[str]  # chunks retrieved from uploaded documents
    total_tokens: int  # running token usage, for the dashboard counter
    log: list[str]  # human-readable trace of every cycle
    model: str  # model selected in the sidebar
    temperature: float  # temperature selected in the sidebar


def initial_state(
    goal: str,
    context_docs: list[str] | None = None,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.2,
) -> ResearchState:
    """Build a fresh state for a new run."""
    return ResearchState(
        goal=goal,
        tasks=[],
        findings=[],
        critique="",
        quality_score=0.0,
        retry_count=0,
        report="",
        context_docs=context_docs or [],
        total_tokens=0,
        log=[],
        model=model,
        temperature=temperature,
    )
