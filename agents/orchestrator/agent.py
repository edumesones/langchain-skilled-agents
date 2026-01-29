"""Main orchestrator agent implementation."""

import uuid
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.base import BaseAgent
from agents.orchestrator.memory import CentralMemory
from agents.orchestrator.prompts import get_orchestrator_system_prompt
from agents.orchestrator.router import IntentRouter, TargetAgent
from config.logging_config import get_trace_logger
from skills.loader import get_skill_tools


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator agent that coordinates the multi-agent system.

    Responsibilities:
    - Understand user requests
    - Route to appropriate sub-agents
    - Load skills as needed
    - Consolidate responses
    - Maintain central memory
    """

    def __init__(
        self,
        llm: BaseChatModel,
        session_id: str | None = None,
        user_id: str = "analyst",
    ):
        """
        Initialize the orchestrator.

        Args:
            llm: Language model to use
            session_id: Session identifier (generated if not provided)
            user_id: User identifier
        """
        # Get skill tools
        tools = get_skill_tools()

        super().__init__(
            name="ORCH",
            llm=llm,
            tools=tools,
        )

        # Initialize memory
        self.session_id = session_id or str(uuid.uuid4())
        self.memory = CentralMemory(
            session_id=self.session_id,
            user_id=user_id,
        )

        # Initialize router
        self.router = IntentRouter()

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.trace_logger = get_trace_logger()

    def get_system_prompt(self) -> str:
        """Get the system prompt with dynamic skills section."""
        return get_orchestrator_system_prompt()

    async def process(
        self,
        messages: list[BaseMessage],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user request.

        Args:
            messages: Conversation history
            context: Additional context

        Returns:
            Dict with response and metadata
        """
        context = context or {}

        # Get the last user message for routing
        last_message = messages[-1] if messages else None
        if not last_message or not isinstance(last_message, HumanMessage):
            return {
                "response": "No se recibió mensaje del usuario.",
                "routing": None,
                "skills_loaded": [],
            }

        user_message = last_message.content
        self.log(f"Received: \"{user_message[:100]}...\"" if len(user_message) > 100 else f"Received: \"{user_message}\"")

        # Route the request
        routing = self.router.route(user_message, context)
        self.log(
            f"Intent classified: {routing.request_type.value}",
            routing_to=routing.primary_agent.value,
            reason=routing.reasoning,
        )

        # Update context from routing
        entities = self.router.extract_entities(user_message)
        if entities["alert_ids"]:
            self.memory.set_current_alert(entities["alert_ids"][0])
        if entities["customer_ids"]:
            self.memory.set_current_customer(entities["customer_ids"][0])

        # Prepare the prompt
        system_prompt = self.get_system_prompt()

        # Add context about current focus
        context_addition = ""
        if self.memory.session.current_alert_id:
            context_addition += f"\n\n**Alerta en contexto:** {self.memory.session.current_alert_id}"
        if self.memory.session.current_customer_id:
            context_addition += f"\n**Cliente en contexto:** {self.memory.session.current_customer_id}"
        if self.memory.get_loaded_skills():
            context_addition += f"\n**Skills cargados:** {', '.join(self.memory.get_loaded_skills())}"

        full_system_prompt = system_prompt + context_addition

        # Invoke the LLM
        prompt_messages = self.prompt.format_messages(
            system_prompt=full_system_prompt,
            messages=messages,
        )

        response = await self.llm_with_tools.ainvoke(prompt_messages)

        # Process tool calls if any
        skills_loaded = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']

                self.log_tool_use(tool_name, tool_args)

                # Execute the tool
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool:
                    tool_result = tool.invoke(tool_args)

                    # Cache loaded skills
                    if tool_name == 'load_skill':
                        skill_id = tool_args.get('skill_id')
                        if skill_id and not tool_result.startswith("Error"):
                            self.memory.cache_skill(skill_id, tool_result)
                            skills_loaded.append(skill_id)

        # Get final response content
        response_content = response.content if hasattr(response, 'content') else str(response)

        self.log("Response generated")

        return {
            "response": response_content,
            "routing": {
                "request_type": routing.request_type.value,
                "primary_agent": routing.primary_agent.value,
                "secondary_agent": routing.secondary_agent.value if routing.secondary_agent else None,
                "required_skills": routing.required_skills,
            },
            "skills_loaded": skills_loaded,
            "context": {
                "current_alert": self.memory.session.current_alert_id,
                "current_customer": self.memory.session.current_customer_id,
                "loaded_skills": self.memory.get_loaded_skills(),
            },
        }

    async def delegate_to_risk(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Delegate a task to the Risk agent.

        Args:
            task: Task description
            context: Context to pass

        Returns:
            Result from the Risk agent
        """
        self.log(f"Delegating to RISK: {task[:50]}...")

        # Record delegation
        record = self.memory.record_delegation(
            to_agent="RISK",
            reason="Risk analysis required",
            task_summary=task,
        )

        # Here we would actually invoke the Risk agent
        # For now, return placeholder
        result = {
            "status": "delegated",
            "agent": "RISK",
            "task": task,
        }

        self.memory.complete_delegation(record, "Completed")

        return result

    async def delegate_to_compliance(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Delegate a task to the Compliance agent.

        Args:
            task: Task description
            context: Context to pass

        Returns:
            Result from the Compliance agent
        """
        self.log(f"Delegating to COMPLIANCE: {task[:50]}...")

        # Record delegation
        record = self.memory.record_delegation(
            to_agent="COMPLIANCE",
            reason="Compliance analysis required",
            task_summary=task,
        )

        # Here we would actually invoke the Compliance agent
        result = {
            "status": "delegated",
            "agent": "COMPLIANCE",
            "task": task,
        }

        self.memory.complete_delegation(record, "Completed")

        return result

    def get_session_summary(self) -> dict[str, Any]:
        """Get a summary of the current session."""
        return self.memory.get_session_summary()
