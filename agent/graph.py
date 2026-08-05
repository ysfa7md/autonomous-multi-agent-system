from langgraph.graph import StateGraph,START,END
from regex import E

from agent.state import ResearchState
from agent.router import should_retry
from agent.nodes import planner, research, critic, reporting


graph = StateGraph(ResearchState)


nodes_list=[planner, research, critic, reporting]
for node in nodes_list:
    graph.add_node(node,str(node.__name__))

graph.add_edge(START, 'planner')
graph.add_edge('planner', 'research')
graph.add_edge('research', 'critic')
graph.add_edge('reporting', END)

graph.add_conditional_edges(
    source='critic',
    condition=should_retry,
    true_target='planner',
    false_target='reporting'
)

app = graph.compile()
