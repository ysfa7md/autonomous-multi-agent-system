from agent.state import AgentState
import json
import re



# ---- Planner: adapts on retry using last critique ----
def planner(state: AgentState):
    iteration = state["iteration"] + 1
    prior = state.get("gaps", "")

    if HAS_KEY:
        prompt = (
            f"You are a planning agent. Goal: {state['goal']}.\n"
            f"Previous critique to address (empty on first pass): "
            f"{prior or 'none'}.\n"
            "Return 3 short task bullets that specifically address any gaps. "
            "One per line, no numbering."
        )

        text = llm.invoke(prompt).content

        tasks = [
            task.strip("-* ").strip() for task in text.splitlines() if task.strip()
        ][:3]

    else:
        base_tasks = [
            f"Define scope of '{state['goal']}'",
            "Gather key facts",
            "Identify risks",
        ]

        tasks = (
            base_tasks
            if iteration == 1
            else base_tasks + [f"Address gap: {prior[:60]}"]
        )

    print(
        f"🧭 Planner (iteration {iteration}) -> "
        f"{len(tasks)} tasks" + (f' [addressing: "{prior[:40]}..."]' if prior else "")
    )

    return {
        "iteration": iteration,
        "completed_tasks": tasks,
    }


# ---- Researcher: RAG-grounded ----
def research(state: AgentState):
    ctx, srcs = retrieve(state["goal"])

    if HAS_KEY:
        prompt = (
            "Answer ONLY from the context. Be concise (3-4 sentences). "
            "If a task from the plan isn't covered, say so.\n"
            f"Plan: {state['completed_tasks']}\n\n"
            f"Context:\n{ctx}\n\n"
            f"Goal: {state['goal']}"
        )

        findings = llm.invoke(prompt).content

    else:
        findings = (
            f"Findings on {state['goal']} (grounded): "
            "market is growing, led by Copilot/Cursor; "
            "key risks are security/license leakage, hallucinated APIs, "
            "and unclear regulation; "
            "pricing is per-seat 10-40 USD/user/month."
        )

        # First pass intentionally omits risks
        # so the Critic can detect the gap.
        if state["iteration"] == 1:
            findings = (
                f"Findings on {state['goal']} (grounded): "
                "market is growing, led by Copilot/Cursor."
            )

    print(
        "🔎 Research -> grounded findings gathered",
        "| sources:",
        srcs,
    )

    return {
        "findings": findings,
        "sources": srcs,
    }


# ---- Critic: scores findings and identifies gaps ----
def _extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.S)
    return json.loads(match.group(0)) if match else {}


def critic(state: AgentState):
    if HAS_KEY:
        prompt = (
            "You are a strict reviewer. "
            "Score the findings for completeness vs the goal.\n"
            "Return ONLY JSON: "
            '{"score": <0..1 float>, "gaps": "<one sentence>"}.\n'
            f"Goal: {state['goal']}\n"
            f"Findings: {state['findings']}"
        )

        try:
            data = _extract_json(llm.invoke(prompt).content)

            score = float(data.get("score", 0.5))
            gaps = str(data.get("gaps", ""))

        except Exception:
            score = 0.5
            gaps = "Could not parse critic output; " "treat as incomplete."

    else:
        has_risks = "risk" in state["findings"].lower()

        score = 0.9 if has_risks else 0.5

        gaps = (
            ""
            if has_risks
            else "Findings omit key risks; " "add security, regulation, over-reliance."
        )

    print(
        f"🧐 Critic -> quality_score = {round(score, 2)}"
        + (f" | gap: {gaps[:50]}" if gaps else "")
    )

    return {
        "quality_score": score,
        "gaps": gaps,
    }


def decision(state: AgentState):
    print(
        f"⚖️ Decision -> score "
        f"{round(state['quality_score'], 2)} "
        f"at iteration {state['iteration']}"
    )

    return {}
