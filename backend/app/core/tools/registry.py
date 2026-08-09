import logging
from typing import Dict, List, Optional, Type
from app.agents.tools.base import BaseTool
from app.agents.tools.product_tool import ProductLookupTool
from app.agents.tools.image_tool import ImageGenerationTool
from app.core.tools.skeleton_tools import (
    CompetitorAnalysisTool,
    AdPerformanceTool,
    EcommerceCatalogTool,
    AutomationWebhookTool,
)

logger = logging.getLogger("aimos.tools.registry")


class ToolRegistry:
    """
    Central Tool Registry for AIMOS.
    Registers, organizes, and retrieves tools for AI Agents across domain categories:
    RESEARCH, MARKETING, ADS, ECOMMERCE, CONTENT, AUTOMATION, ANALYTICS.
    """

    _registry: Dict[str, BaseTool] = {}
    _categories: Dict[str, List[str]] = {
        "RESEARCH": ["product_lookup_tool", "competitor_analysis_tool"],
        "MARKETING": ["product_lookup_tool"],
        "ADS": ["ad_performance_tool"],
        "ECOMMERCE": ["ecommerce_catalog_tool"],
        "CONTENT": ["image_generation_tool"],
        "AUTOMATION": ["automation_webhook_tool"],
        "ANALYTICS": ["ad_performance_tool"],
    }

    @classmethod
    def register(cls, tool_instance: BaseTool) -> None:
        cls._registry[tool_instance.name] = tool_instance
        logger.info(f"Registered Tool in ToolRegistry: '{tool_instance.name}'")

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        return cls._registry.get(name)

    @classmethod
    def get_tools_for_category(cls, category: str) -> List[BaseTool]:
        cat_keys = cls._categories.get(category.upper(), [])
        return [cls._registry[k] for k in cat_keys if k in cls._registry]

    @classmethod
    def list_all_tools(cls) -> Dict[str, Dict[str, str]]:
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
            }
            for name, tool in cls._registry.items()
        }


# Automatically register built-in tools upon module import
ToolRegistry.register(ImageGenerationTool())
ToolRegistry.register(CompetitorAnalysisTool())
ToolRegistry.register(AdPerformanceTool())
ToolRegistry.register(EcommerceCatalogTool())
ToolRegistry.register(AutomationWebhookTool())
