from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class AgentState:
    request_id: str
    agent_type: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, str]] = field(default_factory=list)
    intermediate_steps: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    final_result: Optional[Dict[str, Any]] = None
    status: str = "PENDING"
    error: Optional[str] = None
