from typing import Dict, Any
from app.agents.tools.base import BaseTool
from app.core.media.factory import MediaGeneratorFactory


class ImageGenerationTool(BaseTool):
    """
    Tool used by Creative and Asset agents to generate image assets using the configured Media Generator Provider.
    """
    name: str = "image_generation_tool"
    description: str = "Generates ad images from visual text prompts using AI Media Generator Abstraction."

    def __init__(self, provider_name: str = "mock"):
        self.provider_name = provider_name

    async def execute(
        self,
        prompt: str = None,
        size: str = "1024x1024",
        style: str = "vivid",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        generator = MediaGeneratorFactory.get_image_generator(self.provider_name)
        visual_prompt = prompt or "High quality product marketing creative visual"
        result = await generator.generate_image(prompt=visual_prompt, size=size, style=style, **kwargs)
        return result
