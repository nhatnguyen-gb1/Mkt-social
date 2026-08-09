import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_asset_service
from app.services.asset_service import AssetService
from app.schemas.creative import ImageGenerateRequest, AssetResponse, AssetListResponse

router = APIRouter(prefix="/assets", tags=["Assets & Media Generation"])


@router.post(
    "/generate-image",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Ad Image Asset",
)
async def generate_image_asset(
    request: ImageGenerateRequest,
    service: AssetService = Depends(get_asset_service),
):
    """
    Triggers image generation via MediaGeneratorFactory (DALL-E 3 or Mock)
    and saves the generated image as a managed Asset entity in DB.
    """
    return await service.generate_and_save_image(request)


@router.get(
    "",
    response_model=AssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Media Assets",
)
async def list_assets(
    product_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    service: AssetService = Depends(get_asset_service),
):
    """
    Retrieves all generated creative assets, optionally filtered by product_id.
    """
    items = await service.list_assets(product_id=product_id, skip=skip, limit=limit)
    return AssetListResponse(total=len(items), items=items)


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Asset by ID",
)
async def get_asset_by_id(
    asset_id: uuid.UUID,
    service: AssetService = Depends(get_asset_service),
):
    """
    Retrieves details of a specific media asset by its UUID.
    """
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id '{asset_id}' not found",
        )
    return asset
