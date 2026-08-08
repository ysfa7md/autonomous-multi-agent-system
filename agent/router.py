from agent.state import AgentState
import re
import json


THRESHOLD = 0.8
MAX_ITERS = 3


class FinalReport(BaseModel):
    goal: str
    summary: str
    key_findings: List[str] = Field(min_length=3)
    risks: List[str]
    sources: List[str]
    iterations: int
    confidence: str = Field(description="high | medium | low")


def reporter(state: AgentState):
    findings = state["findings"]

    risks = [
        item.strip() for item in re.split(r"[;\n]", findings) if "risk" in item.lower()
    ] or ["See findings."]

    confidence = "high" if state["quality_score"] >= THRESHOLD else "medium"

    report = FinalReport(
        goal=state["goal"],
        summary=findings[:300],
        key_findings=[
            item.strip() for item in re.split(r"[.;\n]", findings) if item.strip()
        ][:5]
        or [findings],
        risks=risks,
        sources=state.get("sources", []),
        iterations=state["iteration"],
        confidence=confidence,
    )

    print("📝 Reporter -> validated FinalReport")

    return {"report": report.model_dump()}


def route(state: AgentState) -> str:
    score = state["quality_score"]
    iteration = state["iteration"]

    if score >= THRESHOLD:
        return "approve"

    if iteration >= MAX_ITERS:
        print(
            "   ⚠️ Max iterations hit -> "
            "approving best-effort "
            "(quality below threshold)."
        )
        return "approve"

    return "retry"
