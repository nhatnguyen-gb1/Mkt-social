import logging
import uuid
from typing import List, Optional, Dict, Any
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.services.audit_service import AuditService
from app.schemas.creative import ImageGenerateRequest, AssetResponse, AssetCreate
from app.core.media.factory import MediaGeneratorFactory

logger = logging.getLogger("aimos.services.asset")


class AssetService:
    """
    Domain service for generating and managing creative media assets.
    Handles image generation via MediaGeneratorFactory and DB persistence.
    """

    def __init__(self, asset_repo: AssetRepository, audit_service: AuditService):
        self.asset_repo = asset_repo
        self.audit_service = audit_service

    async def generate_and_save_image(
        self, request: ImageGenerateRequest, actor_id: Optional[str] = None
    ) -> AssetResponse:
        logger.info(f"Generating image asset '{request.title}' using provider '{request.provider}'...")
        
        # 1. Resolve media generator provider (OpenAI / Mock)
        generator = MediaGeneratorFactory.get_image_generator(request.provider)
        
        # 2. Execute image generation
        gen_result = await generator.generate_image(
            prompt=request.prompt,
            size=request.size,
            style=request.style,
        )

        # 3. Create DB Asset record
        asset_data = {
            "product_id": request.product_id,
            "asset_type": "IMAGE",
            "title": request.title,
            "file_url": gen_result["file_url"],
            "prompt": gen_result["prompt"],
            "asset_metadata": gen_result.get("metadata", {}),
            "status": "APPROVED",
        }
        
        asset = await self.asset_repo.create(asset_data)

        # 4. Record Audit Log
        await self.audit_service.log_action(
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            action="ASSET_GENERATED",
            entity_type="Asset",
            entity_id=asset.id,
            input_data=request.model_dump(mode="json"),
            output_data={"asset_id": str(asset.id), "file_url": asset.file_url},
            status="SUCCESS",
        )

        return AssetResponse.model_validate(asset)

    async def get_asset(self, asset_id: uuid.UUID) -> Optional[AssetResponse]:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return None
        return AssetResponse.model_validate(asset)

    async def list_assets(
        self, product_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[AssetResponse]:
        if product_id:
            assets = await self.asset_repo.get_by_product_id(product_id, skip=skip, limit=limit)
        else:
            assets = await self.asset_repo.get_multi(skip=skip, limit=limit)
        return [AssetResponse.model_validate(a) for a in assets]
