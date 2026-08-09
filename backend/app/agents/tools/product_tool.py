import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.tools.base import BaseTool
from app.repositories.product_repository import ProductRepository


class ProductLookupInput(BaseModel):
    product_id: Optional[str] = Field(None, description="UUID string of product")
    product_name: Optional[str] = Field(None, description="Name of product to search")


class ProductLookupTool(BaseTool):
    name = "product_lookup_tool"
    description = "Looks up product specifications and details in the AIMOS database"
    args_schema = ProductLookupInput

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = ProductRepository(db_session)

    async def execute(
        self,
        product_id: Optional[str] = None,
        product_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        if product_id:
            try:
                pid = uuid.UUID(product_id)
                product = await self.repo.get_by_id(pid)
                if product:
                    return {
                        "found": True,
                        "id": str(product.id),
                        "name": product.name,
                        "category": product.category,
                        "target_market": product.target_market,
                        "status": product.status,
                    }
            except ValueError:
                pass

        if product_name:
            products = await self.repo.get_multi_ordered(skip=0, limit=10)
            for p in products:
                if product_name.lower() in p.name.lower():
                    return {
                        "found": True,
                        "id": str(p.id),
                        "name": p.name,
                        "category": p.category,
                        "target_market": p.target_market,
                        "status": p.status,
                    }

        return {"found": False, "message": "Product not found in database."}
