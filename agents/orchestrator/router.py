"""Intent routing for the orchestrator."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RequestType(Enum):
    """Types of user requests."""

    ALERT_ANALYSIS = "alert_analysis"
    CUSTOMER_ANALYSIS = "customer_analysis"
    PATTERN_DETECTION = "pattern_detection"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    REPORT_GENERATION = "report_generation"
    DECISION_DOCUMENTATION = "decision_documentation"
    QUEUE_PRIORITIZATION = "queue_prioritization"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class TargetAgent(Enum):
    """Target agents for routing."""

    ORCHESTRATOR = "orchestrator"
    RISK = "risk"
    COMPLIANCE = "compliance"
    RISK_THEN_COMPLIANCE = "risk_then_compliance"


@dataclass
class RoutingDecision:
    """Result of routing analysis."""

    request_type: RequestType
    primary_agent: TargetAgent
    secondary_agent: TargetAgent | None
    required_skills: list[str]
    required_data: list[str]
    reasoning: str


class IntentRouter:
    """
    Routes user requests to the appropriate agent(s).

    Uses pattern matching and keywords to determine:
    - What type of request this is
    - Which agent(s) should handle it
    - What skills are needed
    """

    # Keyword patterns for each request type
    PATTERNS = {
        RequestType.ALERT_ANALYSIS: [
            r"alerta\s+ALT-\d+",
            r"analiza(r)?\s+(la\s+)?alerta",
            r"revisa(r)?\s+(la\s+)?alerta",
            r"investiga(r)?\s+(la\s+)?alerta",
        ],
        RequestType.CUSTOMER_ANALYSIS: [
            r"cliente\s+C-\d+",
            r"perfil\s+del?\s+cliente",
            r"información\s+del?\s+cliente",
            r"customer\s*360",
            r"conoce(r)?\s+al\s+cliente",
        ],
        RequestType.PATTERN_DETECTION: [
            r"patr[oó]n(es)?",
            r"anomal[ií]a(s)?",
            r"structuring",
            r"velocity",
            r"detect(ar|a)?\s+",
        ],
        RequestType.RELATIONSHIP_ANALYSIS: [
            r"relacion(es)?",
            r"red\s+de",
            r"grafo",
            r"conexion(es)?",
            r"v[ií]nculos?",
        ],
        RequestType.REPORT_GENERATION: [
            r"genera(r)?\s+(un\s+)?informe",
            r"genera(r)?\s+(un\s+)?reporte",
            r"sar",
            r"comunicaci[oó]n",
            r"sepblac",
        ],
        RequestType.DECISION_DOCUMENTATION: [
            r"documenta(r)?",
            r"justifica(r)?",
            r"cierra(r)?\s+como",
            r"decisi[oó]n",
            r"cerrar\s+alerta",
        ],
        RequestType.QUEUE_PRIORITIZATION: [
            r"prioriz(ar|a)",
            r"cola\s+de",
            r"pendientes",
            r"ordenar?\s+alertas",
            r"triaje",
        ],
    }

    # Skills typically needed for each request type
    SKILL_MAPPING = {
        RequestType.ALERT_ANALYSIS: ["customer_360", "alert_prioritizer", "history_analyzer"],
        RequestType.CUSTOMER_ANALYSIS: ["customer_360", "history_analyzer"],
        RequestType.PATTERN_DETECTION: ["pattern_detector", "customer_360"],
        RequestType.RELATIONSHIP_ANALYSIS: ["relationship_mapper", "customer_360"],
        RequestType.REPORT_GENERATION: ["case_report_generator", "decision_explainer"],
        RequestType.DECISION_DOCUMENTATION: ["decision_explainer"],
        RequestType.QUEUE_PRIORITIZATION: ["alert_prioritizer", "false_positive_filter"],
    }

    # Agent routing for each request type
    AGENT_ROUTING = {
        RequestType.ALERT_ANALYSIS: TargetAgent.RISK_THEN_COMPLIANCE,
        RequestType.CUSTOMER_ANALYSIS: TargetAgent.RISK,
        RequestType.PATTERN_DETECTION: TargetAgent.RISK,
        RequestType.RELATIONSHIP_ANALYSIS: TargetAgent.RISK,
        RequestType.REPORT_GENERATION: TargetAgent.COMPLIANCE,
        RequestType.DECISION_DOCUMENTATION: TargetAgent.COMPLIANCE,
        RequestType.QUEUE_PRIORITIZATION: TargetAgent.COMPLIANCE,
        RequestType.GENERAL_QUESTION: TargetAgent.ORCHESTRATOR,
        RequestType.UNKNOWN: TargetAgent.ORCHESTRATOR,
    }

    def __init__(self):
        """Initialize the router."""
        # Compile patterns for efficiency
        self._compiled_patterns = {
            request_type: [re.compile(p, re.IGNORECASE) for p in patterns]
            for request_type, patterns in self.PATTERNS.items()
        }

    def classify_request(self, message: str) -> RequestType:
        """
        Classify the type of user request.

        Args:
            message: User's message

        Returns:
            The classified RequestType
        """
        message_lower = message.lower()

        # Check each pattern set
        matches = []
        for request_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message_lower):
                    matches.append(request_type)
                    break

        if not matches:
            return RequestType.GENERAL_QUESTION

        # If multiple matches, prioritize more specific types
        priority_order = [
            RequestType.REPORT_GENERATION,
            RequestType.DECISION_DOCUMENTATION,
            RequestType.ALERT_ANALYSIS,
            RequestType.PATTERN_DETECTION,
            RequestType.RELATIONSHIP_ANALYSIS,
            RequestType.CUSTOMER_ANALYSIS,
            RequestType.QUEUE_PRIORITIZATION,
        ]

        for request_type in priority_order:
            if request_type in matches:
                return request_type

        return matches[0]

    def extract_entities(self, message: str) -> dict[str, list[str]]:
        """
        Extract entity references from the message.

        Args:
            message: User's message

        Returns:
            Dict with lists of found entities
        """
        entities = {
            "alert_ids": [],
            "customer_ids": [],
            "case_ids": [],
        }

        # Extract alert IDs (ALT-XXXX)
        alert_pattern = re.compile(r"ALT-\d+", re.IGNORECASE)
        entities["alert_ids"] = alert_pattern.findall(message.upper())

        # Extract customer IDs (C-XXXX)
        customer_pattern = re.compile(r"C-\d+", re.IGNORECASE)
        entities["customer_ids"] = [c.upper() for c in customer_pattern.findall(message)]

        # Extract case IDs (CASE-XXXX)
        case_pattern = re.compile(r"CASE-\d+-\d+", re.IGNORECASE)
        entities["case_ids"] = [c.upper() for c in case_pattern.findall(message)]

        return entities

    def route(self, message: str, context: dict[str, Any] | None = None) -> RoutingDecision:
        """
        Analyze a message and determine routing.

        Args:
            message: User's message
            context: Current session context

        Returns:
            RoutingDecision with complete routing information
        """
        context = context or {}

        # Classify the request
        request_type = self.classify_request(message)

        # Extract entities
        entities = self.extract_entities(message)

        # Determine target agent
        primary_agent = self.AGENT_ROUTING.get(request_type, TargetAgent.ORCHESTRATOR)

        secondary_agent = None
        if primary_agent == TargetAgent.RISK_THEN_COMPLIANCE:
            primary_agent = TargetAgent.RISK
            secondary_agent = TargetAgent.COMPLIANCE

        # Determine required skills
        required_skills = self.SKILL_MAPPING.get(request_type, [])

        # Determine required data
        required_data = []
        if entities["alert_ids"]:
            required_data.append("alert_details")
        if entities["customer_ids"]:
            required_data.append("customer_profile")
        if request_type in [RequestType.PATTERN_DETECTION, RequestType.ALERT_ANALYSIS]:
            required_data.append("transaction_history")

        # Generate reasoning
        reasoning = self._generate_reasoning(
            request_type=request_type,
            primary_agent=primary_agent,
            entities=entities,
        )

        return RoutingDecision(
            request_type=request_type,
            primary_agent=primary_agent,
            secondary_agent=secondary_agent,
            required_skills=required_skills,
            required_data=required_data,
            reasoning=reasoning,
        )

    def _generate_reasoning(
        self,
        request_type: RequestType,
        primary_agent: TargetAgent,
        entities: dict[str, list[str]],
    ) -> str:
        """Generate human-readable reasoning for the routing decision."""
        parts = [f"Solicitud clasificada como: {request_type.value}"]

        if entities["alert_ids"]:
            parts.append(f"Alertas referenciadas: {', '.join(entities['alert_ids'])}")
        if entities["customer_ids"]:
            parts.append(f"Clientes referenciados: {', '.join(entities['customer_ids'])}")

        parts.append(f"Agente primario: {primary_agent.value}")

        return ". ".join(parts)
