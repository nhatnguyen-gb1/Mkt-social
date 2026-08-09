import logging
from typing import Dict, Any, Optional
from app.core.skills.model import SkillResult, SkillEvalResult
from app.core.skills.registry import skill_registry, SkillRegistry

logger = logging.getLogger("aimos.skills.evaluator")


class SkillEvaluator:
    """
    SkillEvaluator framework service for assessing Skill execution quality
    against EVALS.md guidelines and rules.
    """

    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or skill_registry

    def evaluate_result(self, skill_name: str, skill_result: SkillResult) -> SkillEvalResult:
        """
        Evaluates a SkillResult instance and returns structured evaluation metrics.
        """
        skill = self.registry.get_skill(skill_name)
        skill_version = skill.metadata.version if skill else "1.0.0"

        issues = []
        rule_compliance = 100.0
        format_compliance = 100.0
        completeness = 100.0
        accuracy = 100.0

        if skill_result.status not in ("SUCCESS", "MOCK_SUCCESS"):
            issues.append(f"Skill execution status is '{skill_result.status}' (Not SUCCESS)")
            rule_compliance -= 50.0

        if not skill_result.result:
            issues.append("Skill result object is empty")
            completeness -= 50.0

        # Check required fields if defined in SKILL.md outputs
        if skill and skill.metadata.outputs:
            output_data = skill_result.result or {}
            missing_keys = []
            for item in skill.metadata.outputs:
                key = item.get("name") if isinstance(item, dict) else str(item)
                if key and key not in output_data:
                    missing_keys.append(key)
            if missing_keys:
                issues.append(f"Missing required output fields: {missing_keys}")
                completeness -= (len(missing_keys) * 15.0)

        # Normalize score bounds
        rule_compliance = max(0.0, rule_compliance)
        format_compliance = max(0.0, format_compliance)
        completeness = max(0.0, completeness)
        accuracy = max(0.0, accuracy)

        overall_score = round(
            (rule_compliance * 0.3) + (format_compliance * 0.2) + (completeness * 0.3) + (accuracy * 0.2),
            2,
        )

        logger.info(
            f"[SKILL EVALUATION] skill={skill_name} v={skill_version} score={overall_score} issues_count={len(issues)}"
        )

        return SkillEvalResult(
            skill_name=skill_name,
            skill_version=skill_version,
            score=overall_score,
            accuracy=accuracy,
            completeness=completeness,
            rule_compliance=rule_compliance,
            format_compliance=format_compliance,
            issues=issues,
            details={
                "evals_file_loaded": bool(skill and skill.evals_content),
                "has_result_data": bool(skill_result.result),
            },
        )
