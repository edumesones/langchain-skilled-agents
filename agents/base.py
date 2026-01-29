"""Base agent class with common functionality."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from config.logging_config import get_trace_logger


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        name: str,
        llm: BaseChatModel,
        tools: list | None = None,
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent identifier (e.g., "ORCH", "RISK", "COMPL")
            llm: Language model to use
            tools: List of tools available to this agent
        """
        self.name = name
        self.llm = llm
        self.tools = tools or []
        self.trace_logger = get_trace_logger()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    @abstractmethod
    async def process(
        self,
        messages: list[BaseMessage],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a request and return a response.

        Args:
            messages: Conversation history
            context: Additional context (customer_id, alert_id, etc.)

        Returns:
            Dict with response and metadata
        """
        pass

    def log(self, message: str, level: str = "INFO", **metadata: Any) -> None:
        """Log an agent action."""
        self.trace_logger.log(
            agent=self.name,
            message=message,
            level=level,
            **metadata,
        )

    def log_tool_use(self, tool_name: str, params: dict | None = None) -> None:
        """Log a tool invocation."""
        self.trace_logger.log_tool_execution(
            agent=self.name,
            tool_name=tool_name,
            params=params,
        )
