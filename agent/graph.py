from langgraph.graph import StateGraph,START,END
from regex import E

from agent.state import ResearchState
from agent.router import should_retry
from agent.nodes import planner, research, critic, reporter, decision

nodes = {
    "planner": planner,
    "research": research,
    "critic": critic,
    "decision": decision,
    "reporter": reporter,
}

graph = StateGraph(ResearchState)

for name, function in nodes.items():
    graph.add_node(name, function)

graph.add_edge(START, 'planner')
graph.add_edge('planner', 'research')
graph.add_edge('research', 'critic')
graph.add_edge("critic", "decision")

graph.add_conditional_edges(
    "decision",
    should_retry,   #route,
    {
        "retry": "planner",
        "approve": "reporter",
    },
)

graph.add_edge("reporter", END)

app = graph.compile()

print("Graph compiled ✓")
