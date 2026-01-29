"""Compliance agent implementation."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.base import BaseAgent
from agents.compliance.prompts import get_compliance_agent_system_prompt
from skills.loader import get_skill_tools


class ComplianceAgent(BaseAgent):
    """
    Compliance agent (stateless).

    Specializes in:
    - Alert prioritization
    - False positive identification
    - Decision documentation
    - SAR report generation
    """

    def __init__(self, llm: BaseChatModel):
        """
        Initialize the compliance agent.

        Args:
            llm: Language model to use
        """
        tools = get_skill_tools()

        super().__init__(
            name="COMPL",
            llm=llm,
            tools=tools,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{task}"),
        ])

        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the compliance agent."""
        return get_compliance_agent_system_prompt()

    async def process(
        self,
        messages: list[BaseMessage],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a compliance task.

        Args:
            messages: Conversation history
            context: Context from orchestrator

        Returns:
            Compliance analysis results
        """
        context = context or {}
        self.log("Processing compliance task")

        # Extract task
        task = context.get("task", "")
        if not task and messages:
            last_msg = messages[-1]
            task = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

        # Include risk analysis if provided
        risk_analysis = context.get("risk_analysis", "")
        if risk_analysis:
            task = f"{task}\n\n**Análisis de Riesgo previo:**\n{risk_analysis}"

        # Build context
        context_str = ""
        if context.get("customer_id"):
            context_str += f"\nCliente: {context['customer_id']}"
        if context.get("alert_id"):
            context_str += f"\nAlerta: {context['alert_id']}"

        system_prompt = self.get_system_prompt() + context_str

        prompt_messages = self.prompt.format_messages(
            system_prompt=system_prompt,
            messages=messages[:-1] if messages else [],
            task=task,
        )

        # Invoke LLM
        response = await self.llm_with_tools.ainvoke(prompt_messages)

        # Handle tool calls
        tool_results = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']

                self.log_tool_use(tool_name, tool_args)

                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool:
                    result = tool.invoke(tool_args)
                    tool_results.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result[:500] + "..." if len(result) > 500 else result,
                    })

        response_content = response.content if hasattr(response, 'content') else str(response)

        self.log("Compliance analysis completed")

        return {
            "agent": "COMPLIANCE",
            "response": response_content,
            "tool_results": tool_results,
            "context_used": {
                "customer_id": context.get("customer_id"),
                "alert_id": context.get("alert_id"),
                "had_risk_analysis": bool(risk_analysis),
            },
        }
