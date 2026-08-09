import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.llm.base import BaseLLMProvider
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool

logger = logging.getLogger("aimos.agents.base")


class BaseAgent(ABC):
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
        agent_name: str = "BaseAgent",
    ):
        self.llm_provider = llm_provider
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.agent_name = agent_name

    async def run(self, input_data: Dict[str, Any]) -> AgentState:
        request_id = str(uuid.uuid4())
        state = AgentState(
            request_id=request_id,
            agent_type=self.agent_name,
            input_data=input_data,
            status="RUNNING",
        )

        logger.info(f"Starting {self.agent_name} execution (request_id={request_id})")

        try:
            # Graph Step 1: Input node processing
            state = await self._node_input_processor(state)

            # Graph Step 2: Tool execution node (if tools registered)
            if self.tools:
                state = await self._node_tool_executor(state)

            # Graph Step 3: LLM Reasoning node
            state = await self._node_llm_reasoner(state)

            state.status = "COMPLETED"
            logger.info(f"{self.agent_name} completed successfully (request_id={request_id})")
        except Exception as e:
            state.status = "FAILED"
            state.error = str(e)
            logger.error(f"{self.agent_name} failed (request_id={request_id}): {str(e)}")

        return state

    async def _node_input_processor(self, state: AgentState) -> AgentState:
        """Pre-processes input parameters and adds initial message"""
        state.intermediate_steps.append({"node": "input_processor", "status": "ok"})
        return state

    async def _node_tool_executor(self, state: AgentState) -> AgentState:
        """Executes registered tools if needed by agent context"""
        for tool_name, tool in self.tools.items():
            result = await tool.execute(**state.input_data)
            state.tool_results[tool_name] = result
            state.intermediate_steps.append(
                {"node": "tool_executor", "tool": tool_name, "result": result}
            )
        return state

    @abstractmethod
    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        """Core reasoning node calling LLMProvider to generate output"""
        pass
