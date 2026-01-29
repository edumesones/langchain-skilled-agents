"""Node functions for the LangGraph workflow."""

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from agents.orchestrator import OrchestratorAgent
from agents.risk import RiskAgent
from agents.compliance import ComplianceAgent
from config.llm_providers import get_llm
from graph.state import AgentState

logger = logging.getLogger(__name__)

# Cache for agent instances (per session)
_agent_cache: dict[str, Any] = {}


def _get_orchestrator(state: AgentState) -> OrchestratorAgent:
    """Get or create orchestrator agent for session."""
    session_id = state.get("session_id", "default")
    cache_key = f"orchestrator_{session_id}"

    if cache_key not in _agent_cache:
        llm = get_llm()
        _agent_cache[cache_key] = OrchestratorAgent(
            llm=llm,
            session_id=session_id,
            user_id=state.get("user_id", "anonymous"),
        )

    return _agent_cache[cache_key]


def _get_risk_agent() -> RiskAgent:
    """Get or create risk agent (stateless, shared)."""
    if "risk_agent" not in _agent_cache:
        llm = get_llm()
        _agent_cache["risk_agent"] = RiskAgent(llm=llm)

    return _agent_cache["risk_agent"]


def _get_compliance_agent() -> ComplianceAgent:
    """Get or create compliance agent (stateless, shared)."""
    if "compliance_agent" not in _agent_cache:
        llm = get_llm()
        _agent_cache["compliance_agent"] = ComplianceAgent(llm=llm)

    return _agent_cache["compliance_agent"]


async def orchestrator_node(state: AgentState) -> dict:
    """
    Orchestrator node: analyzes input and decides routing.

    The orchestrator:
    1. Maintains conversation context (memory)
    2. Classifies the user's intent
    3. Decides which specialized agent to invoke (if any)
    4. Can respond directly for simple queries
    """
    logger.info("[ORCHESTRATOR] Processing user input")

    try:
        orchestrator = _get_orchestrator(state)
        user_input = state.get("user_input", "")
        messages = state.get("messages", [])

        # Process through orchestrator
        result = await orchestrator.process(
            messages=messages,
            context={"task": user_input},
        )

        # Extract routing decision
        route = result.get("route", "direct")
        task_context = result.get("task_context", {})

        logger.info(f"[ORCHESTRATOR] Route decision: {route}")

        # If direct response, set final response
        if route == "direct":
            return {
                "route": route,
                "task_context": task_context,
                "final_response": result.get("response", ""),
                "current_node": "orchestrator",
                "messages": [AIMessage(content=result.get("response", ""))],
            }

        return {
            "route": route,
            "task_context": task_context,
            "current_node": "orchestrator",
        }

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error: {e}")
        return {
            "error": str(e),
            "route": "end",
            "current_node": "orchestrator",
        }


async def risk_node(state: AgentState) -> dict:
    """
    Risk analysis node: performs detailed risk assessment.

    Specializes in:
    - Customer profile analysis (Customer 360)
    - Pattern detection (structuring, velocity, etc.)
    - Relationship mapping
    - Historical analysis
    """
    logger.info("[RISK] Starting risk analysis")

    try:
        risk_agent = _get_risk_agent()
        messages = state.get("messages", [])
        task_context = state.get("task_context", {})

        # Process through risk agent
        result = await risk_agent.process(
            messages=messages,
            context=task_context,
        )

        logger.info("[RISK] Analysis completed")

        return {
            "risk_result": result,
            "current_node": "risk",
        }

    except Exception as e:
        logger.error(f"[RISK] Error: {e}")
        return {
            "error": str(e),
            "risk_result": {"error": str(e)},
            "current_node": "risk",
        }


async def compliance_node(state: AgentState) -> dict:
    """
    Compliance node: regulatory assessment and documentation.

    Specializes in:
    - Alert prioritization
    - False positive identification
    - Decision documentation
    - SAR report generation
    """
    logger.info("[COMPLIANCE] Starting compliance assessment")

    try:
        compliance_agent = _get_compliance_agent()
        messages = state.get("messages", [])
        task_context = state.get("task_context", {}) or {}

        # Include risk analysis if available
        risk_result = state.get("risk_result")
        if risk_result and risk_result.get("response"):
            task_context["risk_analysis"] = risk_result["response"]

        # Process through compliance agent
        result = await compliance_agent.process(
            messages=messages,
            context=task_context,
        )

        logger.info("[COMPLIANCE] Assessment completed")

        return {
            "compliance_result": result,
            "current_node": "compliance",
        }

    except Exception as e:
        logger.error(f"[COMPLIANCE] Error: {e}")
        return {
            "error": str(e),
            "compliance_result": {"error": str(e)},
            "current_node": "compliance",
        }


async def synthesizer_node(state: AgentState) -> dict:
    """
    Synthesizer node: combines results from specialized agents.

    This node:
    1. Collects results from risk and/or compliance agents
    2. Synthesizes a unified response
    3. Formats the final output for the user
    """
    logger.info("[SYNTHESIZER] Combining agent results")

    try:
        risk_result = state.get("risk_result")
        compliance_result = state.get("compliance_result")
        route = state.get("route", "direct")

        # Build combined response
        response_parts = []

        if risk_result and risk_result.get("response"):
            response_parts.append("## Análisis de Riesgo\n")
            response_parts.append(risk_result["response"])
            response_parts.append("\n")

        if compliance_result and compliance_result.get("response"):
            response_parts.append("## Evaluación de Compliance\n")
            response_parts.append(compliance_result["response"])

        if not response_parts:
            final_response = "No se pudo completar el análisis. Por favor, reformule su consulta."
        else:
            final_response = "\n".join(response_parts)

        logger.info("[SYNTHESIZER] Response synthesized")

        return {
            "final_response": final_response,
            "current_node": "synthesizer",
            "messages": [AIMessage(content=final_response)],
        }

    except Exception as e:
        logger.error(f"[SYNTHESIZER] Error: {e}")
        return {
            "error": str(e),
            "final_response": f"Error al sintetizar la respuesta: {e}",
            "current_node": "synthesizer",
        }


async def error_handler_node(state: AgentState) -> dict:
    """
    Error handler node: gracefully handles errors.

    Provides user-friendly error messages and logs details for debugging.
    """
    error = state.get("error", "Unknown error")
    logger.error(f"[ERROR_HANDLER] Handling error: {error}")

    error_response = (
        "Lo siento, ha ocurrido un error al procesar su solicitud. "
        "Por favor, intente reformular su consulta o contacte al soporte técnico.\n\n"
        f"Detalle técnico: {error}"
    )

    return {
        "final_response": error_response,
        "current_node": "error_handler",
        "messages": [AIMessage(content=error_response)],
    }


def clear_agent_cache(session_id: str | None = None) -> None:
    """
    Clear cached agent instances.

    Args:
        session_id: If provided, only clear agents for this session.
                   If None, clear all cached agents.
    """
    global _agent_cache

    if session_id:
        keys_to_remove = [k for k in _agent_cache if session_id in k]
        for key in keys_to_remove:
            del _agent_cache[key]
    else:
        _agent_cache.clear()

    logger.info(f"[CACHE] Cleared agent cache (session: {session_id or 'all'})")
