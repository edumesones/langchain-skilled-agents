"""State definitions for the LangGraph workflow."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for the multi-agent workflow.

    This state is passed between all nodes in the graph and maintains
    the conversation context and intermediate results.
    """

    # Conversation messages (with automatic message merging)
    messages: Annotated[list[BaseMessage], add_messages]

    # Current user input
    user_input: str

    # Session and user identification
    session_id: str
    user_id: str

    # Routing decision from orchestrator
    route: str | None  # "risk", "compliance", "direct", "end"

    # Task context extracted by orchestrator
    task_context: dict | None

    # Results from specialized agents
    risk_result: dict | None
    compliance_result: dict | None

    # Final response to user
    final_response: str | None

    # Error state
    error: str | None

    # Workflow metadata
    current_node: str | None
    iteration_count: int
