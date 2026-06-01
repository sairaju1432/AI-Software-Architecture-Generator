from typing import Any, TypedDict
from langgraph.graph import END, StateGraph
from app.agents.prompts import AGENT_STEPS
from app.services.ai_provider import GeminiArchitectureProvider

class ArchitectureState(TypedDict, total=False):
    prompt: str
    notes: list[str]
    output: dict[str, Any]

def _append_note(label: str):
    async def node(state: ArchitectureState) -> ArchitectureState:
        return {**state, "notes": [*state.get("notes", []), label]}
    return node

async def _generate(state: ArchitectureState) -> ArchitectureState:
    enriched_prompt = state["prompt"] + "\n\nWorkflow notes:\n" + "\n".join(state.get("notes", []))
    output = await GeminiArchitectureProvider().generate(enriched_prompt)
    return {**state, "output": output}

def build_architecture_workflow():
    graph = StateGraph(ArchitectureState)
    previous = None
    for index, step in enumerate(AGENT_STEPS):
        name = f"agent_{index}"
        graph.add_node(name, _append_note(step))
        if previous is None:
            graph.set_entry_point(name)
        else:
            graph.add_edge(previous, name)
        previous = name
    graph.add_node("generate_architecture", _generate)
    graph.add_edge(previous, "generate_architecture")
    graph.add_edge("generate_architecture", END)
    return graph.compile()
