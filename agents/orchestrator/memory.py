"""Central memory for the orchestrator agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SessionContext:
    """Context for the current session."""

    session_id: str
    user_id: str
    started_at: datetime = field(default_factory=datetime.now)

    # Active work items
    active_alerts: list[str] = field(default_factory=list)
    active_customers: list[str] = field(default_factory=list)
    active_case_id: str | None = None

    # Current focus
    current_alert_id: str | None = None
    current_customer_id: str | None = None


@dataclass
class DelegationRecord:
    """Record of a delegation to a sub-agent."""

    timestamp: datetime
    from_agent: str
    to_agent: str
    reason: str
    task_summary: str
    result_summary: str | None = None
    completed_at: datetime | None = None


@dataclass
class Insight:
    """An insight gathered from a sub-agent."""

    timestamp: datetime
    source_agent: str
    insight_type: str  # RISK_ASSESSMENT, PATTERN_DETECTED, FP_LIKELIHOOD, etc.
    content: dict[str, Any]
    relevance_score: float = 1.0


class CentralMemory:
    """
    Central memory maintained by the orchestrator.

    Stores:
    - Session context (active alerts, customers, etc.)
    - Loaded skills cache
    - Delegation history
    - Accumulated insights from sub-agents
    """

    def __init__(self, session_id: str, user_id: str):
        """Initialize central memory for a session."""
        self.session = SessionContext(
            session_id=session_id,
            user_id=user_id,
        )

        # Cache of loaded skill contents
        self.skill_cache: dict[str, str] = {}

        # History of delegations
        self.delegation_history: list[DelegationRecord] = []

        # Insights from sub-agents
        self.insights: list[Insight] = []

    # =========================================================================
    # Session Context
    # =========================================================================

    def set_current_alert(self, alert_id: str) -> None:
        """Set the current alert being worked on."""
        self.session.current_alert_id = alert_id
        if alert_id not in self.session.active_alerts:
            self.session.active_alerts.append(alert_id)

    def set_current_customer(self, customer_id: str) -> None:
        """Set the current customer in context."""
        self.session.current_customer_id = customer_id
        if customer_id not in self.session.active_customers:
            self.session.active_customers.append(customer_id)

    def clear_current_focus(self) -> None:
        """Clear current focus (alert/customer)."""
        self.session.current_alert_id = None
        self.session.current_customer_id = None

    # =========================================================================
    # Skill Cache
    # =========================================================================

    def cache_skill(self, skill_id: str, content: str) -> None:
        """Cache a loaded skill's content."""
        self.skill_cache[skill_id] = content

    def get_cached_skill(self, skill_id: str) -> str | None:
        """Get a cached skill's content."""
        return self.skill_cache.get(skill_id)

    def is_skill_loaded(self, skill_id: str) -> bool:
        """Check if a skill is already loaded."""
        return skill_id in self.skill_cache

    def get_loaded_skills(self) -> list[str]:
        """Get list of currently loaded skill IDs."""
        return list(self.skill_cache.keys())

    # =========================================================================
    # Delegation
    # =========================================================================

    def record_delegation(
        self,
        to_agent: str,
        reason: str,
        task_summary: str,
    ) -> DelegationRecord:
        """Record a delegation to a sub-agent."""
        record = DelegationRecord(
            timestamp=datetime.now(),
            from_agent="ORCH",
            to_agent=to_agent,
            reason=reason,
            task_summary=task_summary,
        )
        self.delegation_history.append(record)
        return record

    def complete_delegation(self, record: DelegationRecord, result_summary: str) -> None:
        """Mark a delegation as complete with result."""
        record.result_summary = result_summary
        record.completed_at = datetime.now()

    def get_recent_delegations(self, limit: int = 10) -> list[DelegationRecord]:
        """Get recent delegation records."""
        return self.delegation_history[-limit:]

    # =========================================================================
    # Insights
    # =========================================================================

    def add_insight(
        self,
        source_agent: str,
        insight_type: str,
        content: dict[str, Any],
        relevance_score: float = 1.0,
    ) -> Insight:
        """Add an insight from a sub-agent."""
        insight = Insight(
            timestamp=datetime.now(),
            source_agent=source_agent,
            insight_type=insight_type,
            content=content,
            relevance_score=relevance_score,
        )
        self.insights.append(insight)
        return insight

    def get_insights_for_customer(self, customer_id: str) -> list[Insight]:
        """Get all insights related to a customer."""
        return [
            i for i in self.insights
            if i.content.get("customer_id") == customer_id
        ]

    def get_insights_for_alert(self, alert_id: str) -> list[Insight]:
        """Get all insights related to an alert."""
        return [
            i for i in self.insights
            if i.content.get("alert_id") == alert_id
        ]

    def get_recent_insights(self, limit: int = 10) -> list[Insight]:
        """Get recent insights sorted by relevance."""
        sorted_insights = sorted(
            self.insights,
            key=lambda i: (i.relevance_score, i.timestamp),
            reverse=True,
        )
        return sorted_insights[:limit]

    # =========================================================================
    # Summary
    # =========================================================================

    def get_session_summary(self) -> dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_id": self.session.session_id,
            "user_id": self.session.user_id,
            "started_at": self.session.started_at.isoformat(),
            "active_alerts": self.session.active_alerts,
            "active_customers": self.session.active_customers,
            "current_alert": self.session.current_alert_id,
            "current_customer": self.session.current_customer_id,
            "loaded_skills": self.get_loaded_skills(),
            "total_delegations": len(self.delegation_history),
            "total_insights": len(self.insights),
        }

    def get_context_for_agent(self, agent: str) -> dict[str, Any]:
        """Get relevant context to pass to a sub-agent."""
        context = {
            "session_id": self.session.session_id,
            "current_alert_id": self.session.current_alert_id,
            "current_customer_id": self.session.current_customer_id,
            "loaded_skills": self.get_loaded_skills(),
        }

        # Add relevant insights
        if self.session.current_customer_id:
            context["customer_insights"] = [
                i.content for i in self.get_insights_for_customer(
                    self.session.current_customer_id
                )[-5:]
            ]

        if self.session.current_alert_id:
            context["alert_insights"] = [
                i.content for i in self.get_insights_for_alert(
                    self.session.current_alert_id
                )[-5:]
            ]

        return context
