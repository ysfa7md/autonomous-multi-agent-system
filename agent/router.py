from agent.state import QUALITY_THRESHOLD, MAX_RETRIES


def should_retry(state) -> str:
    if state["quality_score"] >= QUALITY_THRESHOLD:
        return "approve"
    if state["retry_count"] >= MAX_RETRIES:
        return "approve"
    return "retry"
