from agent.state import ResearchState, QUALITY_THRESHOLD, MAX_REPEAT


def should_retry(state:ResearchState):
    if state['quality_score'] >= QUALITY_THRESHOLD or state['retry_count'] >= MAX_REPEAT:
        return 'reporting'

    else:
        state['retry_count']+=1
        return 'planner'
