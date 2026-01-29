"""Main LangGraph workflow definition."""

import logging
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph.nodes import (
    orchestrator_node,
    risk_node,
    compliance_node,
    synthesizer_node,
    error_handler_node,
)
from graph.edges import (
    route_after_orchestrator,
    route_after_risk,
    route_after_compliance,
)

logger = logging.getLogger(__name__)

# Compiled graph cache
_compiled_graph = None


def create_workflow() -> StateGraph:
    """
    Create the multi-agent workflow graph.

    Graph structure:
    ```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              │              ▼
        ┌─────────┐          │        ┌───────────┐
        │  Risk   │          │        │ Compliance│
        └────┬────┘          │        └─────┬─────┘
             │               │              │
             └───────┬───────┘              │
                     │                      │
                     ▼                      │
              ┌───────────┐                 │
              │Synthesizer│◄────────────────┘
              └─────┬─────┘
                    │
                    ▼
                  [END]
    ```

    Returns:
        Configured StateGraph
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("error_handler", error_handler_node)

    # Set entry point
    workflow.set_entry_point("orchestrator")

    # Add conditional edges from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "risk": "risk",
            "compliance": "compliance",
            "risk_then_compliance": "risk",
            "synthesizer": "synthesizer",
            "error_handler": "error_handler",
        },
    )

    # Add conditional edges from risk
    workflow.add_conditional_edges(
        "risk",
        route_after_risk,
        {
            "compliance": "compliance",
            "synthesizer": "synthesizer",
            "error_handler": "error_handler",
        },
    )

    # Add conditional edges from compliance
    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "synthesizer": "synthesizer",
            "error_handler": "error_handler",
        },
    )

    # Synthesizer and error handler always go to END
    workflow.add_edge("synthesizer", END)
    workflow.add_edge("error_handler", END)

    logger.info("[WORKFLOW] Graph created successfully")

    return workflow


def get_compiled_graph():
    """
    Get the compiled workflow graph (cached).

    Returns:
        Compiled LangGraph
    """
    global _compiled_graph

    if _compiled_graph is None:
        workflow = create_workflow()
        _compiled_graph = workflow.compile()
        logger.info("[WORKFLOW] Graph compiled successfully")

    return _compiled_graph


async def run_workflow(
    user_input: str,
    session_id: str = "default",
    user_id: str = "anonymous",
    messages: list | None = None,
) -> dict[str, Any]:
    """
    Run the workflow with user input.

    Args:
        user_input: The user's message/query
        session_id: Session identifier for memory
        user_id: User identifier
        messages: Previous conversation messages

    Returns:
        Final state with response
    """
    graph = get_compiled_graph()

    # Build initial state
    initial_state: AgentState = {
        "messages": messages or [],
        "user_input": user_input,
        "session_id": session_id,
        "user_id": user_id,
        "route": None,
        "task_context": None,
        "risk_result": None,
        "compliance_result": None,
        "final_response": None,
        "error": None,
        "current_node": None,
        "iteration_count": 0,
    }

    # Add user message
    initial_state["messages"].append(HumanMessage(content=user_input))

    logger.info(f"[WORKFLOW] Starting workflow for session {session_id}")

    # Run the graph
    try:
        final_state = await graph.ainvoke(initial_state)
        logger.info("[WORKFLOW] Workflow completed successfully")
        return final_state

    except Exception as e:
        logger.error(f"[WORKFLOW] Error running workflow: {e}")
        return {
            **initial_state,
            "error": str(e),
            "final_response": f"Error en el procesamiento: {e}",
        }


def get_workflow_visualization() -> str:
    """
    Get a text visualization of the workflow.

    Returns:
        ASCII representation of the graph
    """
    return """
    ┌─────────────────────────────────────────────────────────────┐
    │                    FINTECH AML WORKFLOW                      │
    └─────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │    START     │
                         └──────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     ORCHESTRATOR      │
                    │  • Intent analysis    │
                    │  • Memory management  │
                    │  • Route decision     │
                    └───────────┬───────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   │                   ▼
    ┌───────────────┐           │           ┌───────────────┐
    │     RISK      │           │           │  COMPLIANCE   │
    │ • Customer360 │           │           │ • Prioritize  │
    │ • Patterns    │           │           │ • FP filter   │
    │ • Relations   │           │           │ • SAR reports │
    └───────┬───────┘           │           └───────┬───────┘
            │                   │                   │
            └───────────────────┴───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     SYNTHESIZER       │
                    │  • Combine results    │
                    │  • Format response    │
                    └───────────┬───────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │     END      │
                         └──────────────┘
    """
