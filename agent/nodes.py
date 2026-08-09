import json
import re

from agent.llm import get_llm, extract_tokens
from agent.models import FinalReport
from agent.rag import retrieve
from agent.state import QUALITY_THRESHOLD, MAX_RETRIES


def _llm(state):
    return get_llm(
        state.get("model", "llama-3.3-70b-versatile"), state.get("temperature", 0.2)
    )


# -- Planner --
def planner(state):
    llm = _llm(state)
    critique = state.get("critique", "")

    if llm:
        prompt = (
            f"You are a planning agent. Goal: {state['goal']}\n"
            f"Previous critique to address (empty on first pass): {critique or 'none'}\n"
            "Return exactly 3 short research task bullets, one per line, "
            "no numbering. If a critique is given, the new tasks must "
            "specifically close those gaps — do not repeat the old plan."
        )
        response = llm.invoke(prompt)
        tasks = [
            t.strip("-* ").strip() for t in response.content.splitlines() if t.strip()
        ][:3]
        tokens = extract_tokens(response)
    else:
        base = [
            f"Define scope of '{state['goal']}'",
            "Gather key facts and data points",
            "Identify risks and open questions",
        ]
        tasks = base if not critique else base + [f"Address gap: {critique[:60]}"]
        tokens = 0

    log_line = f"[planner] retry_count={state['retry_count']} -> {len(tasks)} tasks"
    return {
        "tasks": tasks,
        "total_tokens": state["total_tokens"] + tokens,
        "log": state["log"] + [log_line],
    }


# -- Researcher --
def researcher(state):
    context_chunks = retrieve(state["goal"], state.get("context_docs", []))
    context = (
        "\n---\n".join(context_chunks) if context_chunks else "(no uploaded documents)"
    )

    llm = _llm(state)
    if llm:
        prompt = (
            "Address each task below in 1-2 sentences. Use the context if "
            "relevant, otherwise use general knowledge and say so.\n"
            f"Tasks: {state['tasks']}\n\n"
            f"Context:\n{context}\n\n"
            f"Goal: {state['goal']}"
        )
        response = llm.invoke(prompt)
        findings = [
            line.strip("-* ").strip()
            for line in response.content.splitlines()
            if line.strip()
        ]
        tokens = extract_tokens(response)
    else:
        findings = [
            f"Finding for '{task}': (mock) preliminary data gathered."
            for task in state["tasks"]
        ]
        tokens = 0

    log_line = (
        f"[researcher] {len(findings)} findings (docs used: {len(context_chunks)})"
    )
    return {
        "findings": findings,
        "total_tokens": state["total_tokens"] + tokens,
        "log": state["log"] + [log_line],
    }


# -- Critic --
def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def critic(state):
    llm = _llm(state)
    findings_text = "\n".join(state["findings"])

    if llm:
        prompt = (
            "You are a strict reviewer. Score coverage and quality of these "
            "findings against the goal, 0.0-1.0. Return ONLY JSON: "
            '{"score": <float>, "critique": "<one sentence on the gaps>"}\n'
            f"Goal: {state['goal']}\n"
            f"Findings:\n{findings_text}"
        )
        response = llm.invoke(prompt)
        data = _extract_json(response.content)
        score = float(data.get("score", 0.5))
        critique = str(
            data.get("critique", "Could not parse critic output; treat as incomplete.")
        )
        tokens = extract_tokens(response)
    else:
        # Deterministic mock: first pass always scores under threshold so
        # the retry loop is demonstrable with zero API key / cost.
        first_pass = state["retry_count"] == 0
        score = 0.55 if first_pass else 0.9
        critique = (
            "Findings lack depth on risks and sourcing; expand coverage."
            if first_pass
            else ""
        )
        tokens = 0

    log_line = f"[critic] score={round(score, 2)} critique='{critique[:50]}'"
    return {
        "quality_score": score,
        "critique": critique,
        "total_tokens": state["total_tokens"] + tokens,
        "log": state["log"] + [log_line],
    }


# -- Decision --
def decision(state):
    will_retry = (
        state["quality_score"] < QUALITY_THRESHOLD
        and state["retry_count"] < MAX_RETRIES
    )
    new_count = state["retry_count"] + 1 if will_retry else state["retry_count"]

    log_line = (
        f"[decision] score={round(state['quality_score'], 2)} "
        f"retry_count={state['retry_count']} -> {'RETRY' if will_retry else 'APPROVE'}"
    )
    return {
        "retry_count": new_count,
        "log": state["log"] + [log_line],
    }


# -- Reporting --
def reporting(state):
    report_obj = FinalReport(
        goal=state["goal"],
        quality_score=state["quality_score"],
        retries_used=state["retry_count"],
        below_threshold=state["quality_score"] < QUALITY_THRESHOLD,
        findings=state["findings"],
        critique=state["critique"],
    )

    log_line = "[reporting] final report validated + assembled"
    return {
        "report": report_obj.to_markdown(),
        "log": state["log"] + [log_line],
    }
