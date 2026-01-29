"""Edge functions for conditional routing in the LangGraph workflow."""

import logging
from typing import Literal

from graph.state import AgentState

logger = logging.getLogger(__name__)


def route_after_orchestrator(
    state: AgentState,
) -> Literal["risk", "compliance", "risk_then_compliance", "synthesizer", "error_handler"]:
    """
    Determine next node after orchestrator based on routing decision.

    Routes:
    - "risk": Go to risk analysis only
    - "compliance": Go to compliance analysis only
    - "risk_then_compliance": Sequential analysis (risk -> compliance)
    - "direct": Orchestrator handled directly, go to synthesizer
    - "end": Error or end state
    """
    route = state.get("route", "direct")
    error = state.get("error")

    if error:
        logger.info("[ROUTER] Error detected, routing to error handler")
        return "error_handler"

    if route == "risk":
        logger.info("[ROUTER] Routing to risk agent")
        return "risk"

    if route == "compliance":
        logger.info("[ROUTER] Routing to compliance agent")
        return "compliance"

    if route == "risk_compliance" or route == "both":
        logger.info("[ROUTER] Routing to risk then compliance")
        return "risk_then_compliance"

    # Default: direct response from orchestrator
    logger.info("[ROUTER] Direct response, routing to synthesizer")
    return "synthesizer"


def route_after_risk(
    state: AgentState,
) -> Literal["compliance", "synthesizer", "error_handler"]:
    """
    Determine next node after risk analysis.

    If the original route was "risk_then_compliance" or "both",
    continue to compliance. Otherwise, go to synthesizer.
    """
    route = state.get("route", "")
    error = state.get("error")

    if error:
        logger.info("[ROUTER] Error in risk, routing to error handler")
        return "error_handler"

    if route in ("risk_compliance", "both", "risk_then_compliance"):
        logger.info("[ROUTER] Continuing to compliance after risk")
        return "compliance"

    logger.info("[ROUTER] Risk complete, routing to synthesizer")
    return "synthesizer"


def route_after_compliance(
    state: AgentState,
) -> Literal["synthesizer", "error_handler"]:
    """
    Determine next node after compliance analysis.

    Always goes to synthesizer unless there's an error.
    """
    error = state.get("error")

    if error:
        logger.info("[ROUTER] Error in compliance, routing to error handler")
        return "error_handler"

    logger.info("[ROUTER] Compliance complete, routing to synthesizer")
    return "synthesizer"


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    Check if the workflow should continue or end.

    Used for iteration limits and error checking.
    """
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 10  # Safety limit

    if iteration_count >= max_iterations:
        logger.warning(f"[ROUTER] Max iterations ({max_iterations}) reached")
        return "end"

    if state.get("final_response"):
        return "end"

    return "continue"
