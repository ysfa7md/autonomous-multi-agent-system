from langgraph.graph import StateGraph, START, END

from agent.state import ResearchState
from agent.nodes import planner, researcher, critic, decision, reporting
from agent.router import should_retry


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner)
    graph.add_node("researcher", researcher)
    graph.add_node("critic", critic)
    graph.add_node("decision", decision)
    graph.add_node("reporting", reporting)
#===---===---===
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "critic")
    graph.add_edge("critic", "decision")

    graph.add_conditional_edges(
        "decision",
        should_retry,
        {"retry": "planner", "approve": "reporting"},
    )

    graph.add_edge("reporting", END)

    return graph.compile()


app = build_graph()

