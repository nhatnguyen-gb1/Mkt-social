import logging
from typing import Dict, Any, Type, List, Optional
from app.agents.base import BaseAgent
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.marketing_strategy_agent import MarketingStrategyAgent
from app.agents.creative_agent import CreativeAgent
from app.agents.ads_agent import AdsAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.marketing_lead_agent import MarketingLeadAgent
from app.agents.product_agent import ProductAgent
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.agents.skeleton_agents import AutomationAgent, EcommerceAgent

logger = logging.getLogger("aimos.agents.registry")


class AgentRegistry:
    """
    Central Agent Registry for AIMOS.
    Tracks, organizes, and retrieves all AI Agents across the marketing lifecycle.
    """

    _agents: Dict[str, Dict[str, Any]] = {
        "MarketingLeadAgent": {
            "class": MarketingLeadAgent,
            "domain": "LEADERSHIP",
            "status": "REAL",
            "description": "AI Head of Marketing orchestrating strategy, delegation, output review, and final recommendations.",
        },
        "MarketResearchAgent": {
            "class": MarketResearchAgent,
            "domain": "RESEARCH",
            "status": "REAL",
            "description": "Analyzes market demand, audience segments, and competitor risks.",
        },
        "ProductAgent": {
            "class": ProductAgent,
            "domain": "PRODUCT_STRATEGY",
            "status": "REAL",
            "description": "Senior Product Strategist analyzing PMF, USP, UVP, positioning, offer design, and validation plans.",
        },
        "LeadQualificationAgent": {
            "class": LeadQualificationAgent,
            "domain": "PRE_SALES",
            "status": "REAL",
            "description": "AI Pre-Sales / Lead Qualification Specialist extracting intent, scoring leads, selecting next questions, and generating sales handoffs.",
        },
        "MarketingStrategyAgent": {
            "class": MarketingStrategyAgent,
            "domain": "STRATEGY",
            "status": "REAL",
            "description": "Formulates brand positioning, marketing hooks, and campaign angles.",
        },
        "CreativeAgent": {
            "class": CreativeAgent,
            "domain": "CREATIVE",
            "status": "REAL",
            "description": "Generates visual prompts (DALL-E) and short video scripts.",
        },
        "AdsAgent": {
            "class": AdsAgent,
            "domain": "ADVERTISING",
            "status": "REAL",
            "description": "Structures campaign parameters, targeting criteria, and ad copy.",
        },
        "OptimizationAgent": {
            "class": OptimizationAgent,
            "domain": "ANALYTICS",
            "status": "REAL",
            "description": "Evaluates CPA/CTR/ROAS metrics and proposes budget scaling/pausing.",
        },
        "AutomationAgent": {
            "class": AutomationAgent,
            "domain": "AUTOMATION",
            "status": "SKELETON",
            "description": "Orchestrates native background tasks and integration pipelines.",
        },
        "EcommerceAgent": {
            "class": EcommerceAgent,
            "domain": "ECOMMERCE",
            "status": "SKELETON",
            "description": "Syncs product catalog and inventory with Shopify and TikTok Shop.",
        },
    }

    @classmethod
    def list_all_agents(cls) -> List[Dict[str, Any]]:
        return [
            {
                "agent_name": name,
                "domain": meta["domain"],
                "status": meta["status"],
                "description": meta["description"],
            }
            for name, meta in cls._agents.items()
        ]

    @classmethod
    def get_agent_class(cls, agent_name: str) -> Optional[Type[BaseAgent]]:
        meta = cls._agents.get(agent_name)
        return meta["class"] if meta else None
