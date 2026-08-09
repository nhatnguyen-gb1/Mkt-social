from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """
    Metadata representation parsed from SKILL.md
    """
    name: str
    version: str = "1.0.0"
    description: str = ""
    purpose: str = ""
    inputs: List[Any] = Field(default_factory=list)
    outputs: List[Any] = Field(default_factory=list)
    workflow: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """
    Full runtime representation of an AIMOS Skill
    """
    metadata: SkillMetadata
    rules_content: str = ""
    examples_content: str = ""
    evals_content: str = ""
    skill_dir: str = ""
    is_valid: bool = True
    validation_error: Optional[str] = None


class SkillResult(BaseModel):
    """
    Execution output of a Skill
    """
    skill_name: str
    skill_version: str = "1.0.0"
    status: str = "SUCCESS"  # SUCCESS / FAILED / MOCK_SUCCESS
    provider_used: str = "mock"
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: int = 0
    errors: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SkillEvalResult(BaseModel):
    """
    Evaluation output of a Skill result against EVALS.md criteria
    """
    skill_name: str
    skill_version: str = "1.0.0"
    score: float = 100.0  # 0 to 100
    accuracy: float = 100.0
    completeness: float = 100.0
    rule_compliance: float = 100.0
    format_compliance: float = 100.0
    issues: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
