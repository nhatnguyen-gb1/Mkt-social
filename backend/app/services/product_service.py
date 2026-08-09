import uuid
from typing import Optional
from fastapi import HTTPException, status
from app.repositories.product_repository import ProductRepository
from app.services.audit_service import AuditService
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)


class ProductService:
    def __init__(
        self, product_repo: ProductRepository, audit_service: AuditService
    ):
        self.product_repo = product_repo
        self.audit_service = audit_service

    async def create_product(
        self, product_in: ProductCreate, actor_id: Optional[str] = None
    ) -> ProductResponse:
        data = product_in.model_dump()
        product = await self.product_repo.create(data)

        # Audit Log hook
        await self.audit_service.log_action(
            action="PRODUCT_CREATED",
            entity_type="Product",
            entity_id=product.id,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            input_data=data,
            output_data={"id": str(product.id), "name": product.name},
        )

        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: uuid.UUID) -> ProductResponse:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id '{product_id}' not found",
            )
        return ProductResponse.model_validate(product)

    async def list_products(
        self, page: int = 1, size: int = 50
    ) -> ProductListResponse:
        skip = (page - 1) * size
        products = await self.product_repo.get_multi_ordered(skip=skip, limit=size)
        total = await self.product_repo.count()
        return ProductListResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            size=size,
        )

    async def update_product(
        self,
        product_id: uuid.UUID,
        product_in: ProductUpdate,
        actor_id: Optional[str] = None,
    ) -> ProductResponse:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id '{product_id}' not found",
            )

        update_data = product_in.model_dump(exclude_unset=True)
        if not update_data:
            return ProductResponse.model_validate(product)

        updated_product = await self.product_repo.update(product, update_data)

        # Audit Log hook
        await self.audit_service.log_action(
            action="PRODUCT_UPDATED",
            entity_type="Product",
            entity_id=product_id,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            input_data=update_data,
            output_data={"id": str(product_id), "status": updated_product.status},
        )

        return ProductResponse.model_validate(updated_product)

    async def delete_product(
        self, product_id: uuid.UUID, actor_id: Optional[str] = None
    ) -> bool:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id '{product_id}' not found",
            )

        success = await self.product_repo.delete(product_id)

        # Audit Log hook
        await self.audit_service.log_action(
            action="PRODUCT_DELETED",
            entity_type="Product",
            entity_id=product_id,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            output_data={"deleted": success},
        )

        return success
