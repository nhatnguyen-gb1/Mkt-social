import logging
from typing import List, Optional
from app.models.campaign import Campaign
from app.models.safety import PolicyRule
from app.repositories.safety_repository import SafetyRepository
from app.core.safety.engine import PolicyEngine, PolicyCheckResult
from app.schemas.safety import PolicyRuleCreate, PolicyRuleResponse

logger = logging.getLogger("aimos.services.safety")


class SafetyService:
    """
    Domain service for Safety Engine rule evaluation and policy administration.
    """

    def __init__(self, safety_repo: SafetyRepository):
        self.safety_repo = safety_repo

    async def evaluate_campaign_safety(self, campaign: Campaign) -> PolicyCheckResult:
        active_rules = await self.safety_repo.get_active_rules()
        return PolicyEngine.evaluate_campaign(campaign, active_rules)

    async def create_policy_rule(self, request: PolicyRuleCreate) -> PolicyRuleResponse:
        rule_data = request.model_dump()
        rule = await self.safety_repo.create(rule_data)
        logger.info(f"Created new Safety PolicyRule '{rule.name}' (type={rule.rule_type})")
        return PolicyRuleResponse.model_validate(rule)

    async def list_policy_rules(self, skip: int = 0, limit: int = 100) -> List[PolicyRuleResponse]:
        rules = await self.safety_repo.get_multi(skip=skip, limit=limit)
        return [PolicyRuleResponse.model_validate(r) for r in rules]
