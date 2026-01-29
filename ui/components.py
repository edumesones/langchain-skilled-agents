"""Reusable UI components for the Gradio interface."""

from datetime import datetime
from typing import Any

import gradio as gr


def format_agent_badge(agent_name: str) -> str:
    """Format an agent name as an HTML badge."""
    agent_classes = {
        "ORCHESTRATOR": "agent-orchestrator",
        "ORCH": "agent-orchestrator",
        "RISK": "agent-risk",
        "COMPLIANCE": "agent-compliance",
        "COMPL": "agent-compliance",
    }

    css_class = agent_classes.get(agent_name.upper(), "agent-orchestrator")
    return f'<span class="agent-badge {css_class}">{agent_name}</span>'


def format_status_badge(status: str) -> str:
    """Format a status as an HTML badge."""
    status_classes = {
        "success": "status-success",
        "completed": "status-success",
        "active": "status-success",
        "warning": "status-warning",
        "pending": "status-warning",
        "in_progress": "status-warning",
        "error": "status-error",
        "failed": "status-error",
        "critical": "status-error",
        "info": "status-info",
        "processing": "status-info",
    }

    css_class = status_classes.get(status.lower(), "status-info")
    return f'<span class="status-badge {css_class}">{status}</span>'


def format_log_entry(
    timestamp: datetime,
    level: str,
    agent: str,
    message: str,
) -> str:
    """Format a log entry as HTML."""
    level_class = f"log-level-{level.lower()}"
    time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]

    return f"""
    <div class="log-entry">
        <span class="log-timestamp">{time_str}</span>
        <span class="{level_class}">[{level.upper()}]</span>
        {format_agent_badge(agent)}
        <span>{message}</span>
    </div>
    """


def format_workflow_status(
    current_node: str | None,
    route: str | None,
    error: str | None,
) -> str:
    """Format the current workflow status."""
    if error:
        status = "error"
        status_text = "Error"
    elif current_node:
        status = "in_progress"
        status_text = f"En {current_node.title()}"
    else:
        status = "pending"
        status_text = "Esperando"

    route_info = f"Ruta: {route}" if route else ""

    return f"""
    <div class="sidebar-panel">
        <div class="sidebar-title">Estado del Workflow</div>
        <div style="margin-bottom: 0.5rem;">
            {format_status_badge(status)} {status_text}
        </div>
        <div style="font-size: 0.875rem; color: #71717a;">
            {route_info}
        </div>
    </div>
    """


def format_context_panel(context: dict[str, Any] | None) -> str:
    """Format the current context/session info."""
    if not context:
        return """
        <div class="sidebar-panel">
            <div class="sidebar-title">Contexto Actual</div>
            <div style="color: #71717a; font-size: 0.875rem;">
                Sin contexto activo
            </div>
        </div>
        """

    items = []
    if context.get("customer_id"):
        items.append(f"<div><strong>Cliente:</strong> {context['customer_id']}</div>")
    if context.get("alert_id"):
        items.append(f"<div><strong>Alerta:</strong> {context['alert_id']}</div>")
    if context.get("session_id"):
        items.append(f"<div><strong>Sesión:</strong> {context['session_id'][:8]}...</div>")

    return f"""
    <div class="sidebar-panel">
        <div class="sidebar-title">Contexto Actual</div>
        <div style="font-size: 0.875rem;">
            {''.join(items) or '<span style="color: #71717a;">Sin datos</span>'}
        </div>
    </div>
    """


def format_skills_panel(loaded_skills: list[str] | None) -> str:
    """Format the loaded skills panel."""
    if not loaded_skills:
        return """
        <div class="sidebar-panel">
            <div class="sidebar-title">Skills Cargados</div>
            <div style="color: #71717a; font-size: 0.875rem;">
                Ningún skill cargado
            </div>
        </div>
        """

    skill_items = "".join([
        f'<div style="padding: 0.25rem 0; font-family: monospace; font-size: 0.8125rem;">'
        f'<span style="color: #22c55e;">●</span> {skill}</div>'
        for skill in loaded_skills
    ])

    return f"""
    <div class="sidebar-panel">
        <div class="sidebar-title">Skills Cargados</div>
        <div>
            {skill_items}
        </div>
    </div>
    """


def create_example_queries() -> list[str]:
    """Get example queries for the chat interface."""
    return [
        "Analiza el perfil de riesgo del cliente CUST-000042",
        "¿Cuáles son las alertas pendientes más críticas?",
        "Busca patrones de structuring en el cliente CUST-000123",
        "Genera un reporte SAR para la alerta ALT-000015",
        "Muestra las relaciones del cliente CUST-000007",
        "¿Qué transacciones sospechosas hay de países de alto riesgo?",
        "Evalúa la alerta ALT-000089 y determina si es falso positivo",
        "Dame un resumen del estado de las alertas por severidad",
    ]


def format_alert_card(alert: dict) -> str:
    """Format an alert as an HTML card."""
    severity_colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#eab308",
        "LOW": "#22c55e",
    }

    severity = alert.get("severity", "UNKNOWN")
    color = severity_colors.get(severity, "#71717a")

    return f"""
    <div style="
        background: #18181b;
        border: 1px solid #27272a;
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: #e4e4e7;">{alert.get('alert_id', 'N/A')}</span>
            <span style="
                background: {color}20;
                color: {color};
                padding: 0.125rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            ">{severity}</span>
        </div>
        <div style="font-size: 0.875rem; color: #a1a1aa; margin-bottom: 0.25rem;">
            {alert.get('alert_type', 'Unknown Type')}
        </div>
        <div style="font-size: 0.8125rem; color: #71717a;">
            Cliente: {alert.get('customer_id', 'N/A')} |
            Score: {alert.get('risk_score', 'N/A')}
        </div>
    </div>
    """


def format_customer_card(customer: dict) -> str:
    """Format a customer as an HTML card."""
    risk_colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#eab308",
        "LOW": "#22c55e",
    }

    risk_level = customer.get("risk_level", "UNKNOWN")
    color = risk_colors.get(risk_level, "#71717a")

    return f"""
    <div style="
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: #e4e4e7;">{customer.get('full_name', 'N/A')}</span>
            <span style="
                background: {color}20;
                color: {color};
                padding: 0.125rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            ">{risk_level}</span>
        </div>
        <div style="font-size: 0.875rem; color: #a1a1aa;">
            {customer.get('customer_id', 'N/A')}
        </div>
        <div style="font-size: 0.8125rem; color: #71717a; margin-top: 0.25rem;">
            {customer.get('customer_type', 'individual').title()} |
            {customer.get('country', 'ES')} |
            {'PEP' if customer.get('pep') else 'No PEP'}
        </div>
    </div>
    """
