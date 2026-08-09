from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class BaseTool(ABC):
    name: str
    description: str
    args_schema: Optional[type[BaseModel]] = None

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the tool logic safely"""
        pass
