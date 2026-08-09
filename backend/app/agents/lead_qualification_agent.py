import logging
import uuid
from typing import List, Optional, Dict, Any
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool
from app.core.llm.base import BaseLLMProvider
from app.core.skills.executor import SkillExecutor
from app.core.skills.evaluator import SkillEvaluator
from app.core.qualification.engine import QualificationEngine

logger = logging.getLogger("aimos.agents.lead_qualification")


class LeadQualificationAgent(BaseAgent):
    """
    LeadQualificationAgent - AI Pre-Sales / Lead Qualification Specialist V2.
    
    Integrated with QualificationEngine:
    - 12-step structured qualification pipeline execution.
    - Information Extraction, Intent Detection, Need, Pain Point & Objection Detection.
    - Contradiction Detection (e.g. Budget 3B vs 1.5B).
    - Confidence Calibration per inference (0.0 - 1.0).
    - Configurable Lead Scoring Engine & Classification (HOT, WARM, COLD, INVALID, UNKNOWN).
    - Next Best Question & Sales Handoff Builder.
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
        skill_executor: Optional[SkillExecutor] = None,
        qualification_engine: Optional[QualificationEngine] = None,
    ):
        super().__init__(
            llm_provider=llm_provider,
            tools=tools,
            agent_name="LeadQualificationAgent",
        )
        self.skill_executor = skill_executor or SkillExecutor()
        self.evaluator = SkillEvaluator()
        self.qualification_engine = qualification_engine or QualificationEngine()

    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        input_payload = state.input_data or {}
        
        lead_input = input_payload.get("lead") or {}
        if isinstance(lead_input, str):
            lead_data = {"phone": "+84901234567", "source": lead_input}
        elif isinstance(lead_input, dict):
            lead_data = lead_input
        else:
            lead_data = {}

        conversation = input_payload.get("conversation") or []
        context = input_payload.get("context") or {}

        # If a plain message was provided, wrap into conversation
        if not conversation and isinstance(input_payload.get("message"), str):
            conversation = [{"speaker": "CUSTOMER", "text": input_payload.get("message")}]

        # Execute 12-step Qualification Pipeline
        engine_result = self.qualification_engine.process(
            lead_data=lead_data,
            conversation=conversation,
            context=context,
        )

        state.final_result = engine_result
        state.intermediate_steps.append({"node": "qualification_pipeline_execution", "status": "completed"})
        return state
