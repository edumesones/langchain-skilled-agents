"""Structured logging configuration using structlog."""

import logging
import sys
from datetime import datetime, timezone
from typing import Any

import structlog
from rich.console import Console
from rich.logging import RichHandler

from config.settings import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure standard logging with Rich handler for pretty output
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                rich_tracebacks=True,
                tracebacks_show_locals=settings.debug,
                show_time=True,
                show_path=settings.debug,
            )
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)

    # Configure structlog
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.is_development:
        # Development: pretty console output
        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    exception_formatter=structlog.dev.rich_traceback,
                )
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Production: JSON output
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class AgentTraceLogger:
    """
    Logger specifically for agent traces to display in the UI.

    Captures agent decisions, routing, and tool usage in a format
    suitable for real-time display in the Gradio logs panel.
    """

    def __init__(self) -> None:
        self._traces: list[dict[str, Any]] = []
        self._max_traces: int = 1000

    def log(
        self,
        agent: str,
        message: str,
        level: str = "INFO",
        **metadata: Any,
    ) -> dict[str, Any]:
        """
        Log an agent trace entry.

        Args:
            agent: Agent identifier (ORCH, RISK, COMPL)
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            **metadata: Additional metadata

        Returns:
            The logged trace entry
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "level": level,
            "message": message,
            "metadata": metadata,
        }

        self._traces.append(entry)

        # Keep only recent traces
        if len(self._traces) > self._max_traces:
            self._traces = self._traces[-self._max_traces :]

        return entry

    def log_routing(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
    ) -> dict[str, Any]:
        """Log a routing decision."""
        return self.log(
            agent=from_agent,
            message=f"Routing to: {to_agent}",
            level="INFO",
            routing_to=to_agent,
            reason=reason,
        )

    def log_skill_load(
        self,
        agent: str,
        skill_id: str,
    ) -> dict[str, Any]:
        """Log a skill being loaded."""
        return self.log(
            agent=agent,
            message=f"Loading skill: {skill_id}",
            level="INFO",
            skill_id=skill_id,
        )

    def log_tool_execution(
        self,
        agent: str,
        tool_name: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log a tool execution."""
        return self.log(
            agent=agent,
            message=f"Executing tool: {tool_name}",
            level="INFO",
            tool_name=tool_name,
            params=params or {},
        )

    def log_error(
        self,
        agent: str,
        error: str,
        exception: Exception | None = None,
    ) -> dict[str, Any]:
        """Log an error."""
        return self.log(
            agent=agent,
            message=f"Error: {error}",
            level="ERROR",
            exception=str(exception) if exception else None,
        )

    def get_traces(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Get recent traces."""
        if limit:
            return self._traces[-limit:]
        return self._traces.copy()

    def get_formatted_traces(self, limit: int = 50) -> str:
        """Get traces formatted for display in UI."""
        traces = self.get_traces(limit)
        lines = []

        for trace in traces:
            timestamp = trace["timestamp"].split("T")[1].split(".")[0]  # HH:MM:SS
            agent = trace["agent"].ljust(5)
            message = trace["message"]
            lines.append(f"{timestamp} | {agent} | {message}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all traces."""
        self._traces.clear()


# Global trace logger instance
_trace_logger: AgentTraceLogger | None = None


def get_trace_logger() -> AgentTraceLogger:
    """Get the global agent trace logger."""
    global _trace_logger
    if _trace_logger is None:
        _trace_logger = AgentTraceLogger()
    return _trace_logger
