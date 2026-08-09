import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from app.core.skills.registry import skill_registry
from app.core.skills.loader import SkillLoader
from app.core.skills.executor import SkillExecutor
from app.core.skills.evaluator import SkillEvaluator
from app.core.skills.model import SkillResult, SkillEvalResult

router = APIRouter(prefix="/skills", tags=["Skill System V1"])


class SkillExecuteRequest(BaseModel):
    input_payload: Dict[str, Any] = Field(
        default_factory=dict,
        example={"product_name": "Portable Blender", "target_market": "Vietnam"},
    )
    provider: str = Field(default="mock", example="mock")
    agent_name: str = Field(default="DirectApiUser", example="DirectApiUser")


class SkillValidateResponse(BaseModel):
    skill_name: str
    is_valid: bool
    version: str
    validation_error: Optional[str] = None
    files_checked: Dict[str, bool] = Field(default_factory=dict)


@router.get("", response_model=List[Dict[str, Any]])
async def list_skills():
    """
    Returns list of all discovered and registered AIMOS Skills.
    """
    skills = skill_registry.list_skills()
    return [
        {
            "name": s.metadata.name,
            "version": s.metadata.version,
            "description": s.metadata.description,
            "purpose": s.metadata.purpose,
            "inputs": s.metadata.inputs,
            "outputs": s.metadata.outputs,
            "dependencies": s.metadata.dependencies,
            "is_valid": s.is_valid,
        }
        for s in skills
    ]


@router.get("/{skill_name}", response_model=Dict[str, Any])
async def get_skill_details(skill_name: str):
    """
    Returns detailed metadata, rules, examples, and evals content for a specific Skill.
    """
    skill = skill_registry.get_skill(skill_name)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found in registry.",
        )
    return {
        "metadata": skill.metadata.model_dump(),
        "rules_content": skill.rules_content,
        "examples_content": skill.examples_content,
        "evals_content": skill.evals_content,
        "skill_dir": skill.skill_dir,
        "is_valid": skill.is_valid,
    }


@router.post("/{skill_name}/validate", response_model=SkillValidateResponse)
async def validate_skill(skill_name: str):
    """
    Validates presence and correctness of SKILL.md, RULES.md, EXAMPLES.md, and EVALS.md.
    """
    skill = skill_registry.get_skill(skill_name)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found in registry.",
        )

    sdir = skill.skill_dir
    files_checked = {
        "SKILL.md": os.path.exists(os.path.join(sdir, "SKILL.md")),
        "RULES.md": os.path.exists(os.path.join(sdir, "RULES.md")),
        "EXAMPLES.md": os.path.exists(os.path.join(sdir, "EXAMPLES.md")),
        "EVALS.md": os.path.exists(os.path.join(sdir, "EVALS.md")),
    }

    return SkillValidateResponse(
        skill_name=skill_name,
        is_valid=skill.is_valid,
        version=skill.metadata.version,
        validation_error=skill.validation_error,
        files_checked=files_checked,
    )


@router.post("/{skill_name}/execute", response_model=SkillResult)
async def execute_skill(skill_name: str, req: SkillExecuteRequest):
    """
    Directly executes a Skill with input payload via SkillExecutor.
    """
    if not skill_registry.has_skill(skill_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found in registry.",
        )

    executor = SkillExecutor()
    return await executor.execute_skill(
        skill_name=skill_name,
        input_data=req.input_payload,
        agent_name=req.agent_name,
        provider_name=req.provider,
    )


@router.get("/{skill_name}/evals", response_model=SkillEvalResult)
async def evaluate_skill(
    skill_name: str,
    product_name: str = Query(default="Portable Blender"),
    target_market: str = Query(default="Vietnam"),
    provider: str = Query(default="mock"),
):
    """
    Executes a skill test run and evaluates result quality against EVALS.md criteria using SkillEvaluator.
    """
    if not skill_registry.has_skill(skill_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found in registry.",
        )

    executor = SkillExecutor()
    exec_result = await executor.execute_skill(
        skill_name=skill_name,
        input_data={"product_name": product_name, "target_market": target_market},
        agent_name="SkillBenchmarkEvaluator",
        provider_name=provider,
    )

    evaluator = SkillEvaluator()
    return evaluator.evaluate_result(skill_name=skill_name, skill_result=exec_result)
