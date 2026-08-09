import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.models.campaign import Campaign
from app.models.safety import PolicyRule

logger = logging.getLogger("aimos.safety.engine")


class PolicyCheckResult(BaseModel):
    is_allowed: bool = True
    requires_human_approval: bool = True
    policy_violations: List[str] = Field(default_factory=list)
    evaluated_rules_count: int = 0


class PolicyEngine:
    """
    Core Safety & Policy Engine for AIMOS.
    Evaluates campaign parameters and ad copies against safety policy rules.
    Prevents financial overrun and unauthorized ad publishing.
    """

    @staticmethod
    def evaluate_campaign(
        campaign: Campaign, active_rules: List[PolicyRule]
    ) -> PolicyCheckResult:
        result = PolicyCheckResult(evaluated_rules_count=len(active_rules))
        
        # Default safety constraint: Require human approval for any financial mutation
        result.requires_human_approval = True

        for rule in active_rules:
            if not rule.is_active:
                continue

            rule_type = rule.rule_type.upper()
            params = rule.parameters or {}

            # Rule 1: Hạn mức ngân sách hàng ngày (MAX_DAILY_BUDGET)
            if rule_type == "MAX_DAILY_BUDGET":
                max_budget = params.get("max_daily_budget_usd", 500.0)
                if campaign.daily_budget > max_budget:
                    msg = f"[VIOLATION] Campaign daily budget (${campaign.daily_budget}) exceeds maximum allowed threshold (${max_budget})."
                    logger.warning(msg)
                    result.policy_violations.append(msg)
                    result.is_allowed = False

            # Rule 2: Từ khóa cấm / Hạn chế nội dung (RESTRICTED_KEYWORDS)
            elif rule_type == "RESTRICTED_KEYWORDS":
                restricted_list = params.get(
                    "keywords", ["free money", "guaranteed return", "cam kết 100%"]
                )
                
                # Check campaign name
                for kw in restricted_list:
                    if kw.lower() in campaign.name.lower():
                        msg = f"[VIOLATION] Campaign name contains restricted keyword '{kw}'."
                        result.policy_violations.append(msg)
                        result.is_allowed = False

                # Check Ad Sets & Ads primary text / headlines if loaded
                if campaign.ad_sets:
                    for ad_set in campaign.ad_sets:
                        if ad_set.ads:
                            for ad in ad_set.ads:
                                text_content = f"{ad.headline or ''} {ad.primary_text or ''}".lower()
                                for kw in restricted_list:
                                    if kw.lower() in text_content:
                                        msg = f"[VIOLATION] Ad '{ad.name}' contains restricted keyword '{kw}'."
                                        result.policy_violations.append(msg)
                                        result.is_allowed = False

            # Rule 3: Bắt buộc Phê duyệt bởi Con người (REQUIRE_APPROVAL_FOR_PUBLISH)
            elif rule_type == "REQUIRE_APPROVAL_FOR_PUBLISH":
                result.requires_human_approval = params.get("require_approval", True)

        return result
