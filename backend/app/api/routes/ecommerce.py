from typing import List, Dict, Any
from fastapi import APIRouter, status

router = APIRouter(prefix="/ecommerce", tags=["E-Commerce Integration [SKELETON]"])


@router.get(
    "/products",
    status_code=status.HTTP_200_OK,
    summary="List External E-Commerce Catalog Items [SKELETON]",
)
async def list_ecommerce_catalog():
    """
    [SKELETON] Placeholder endpoint for Shopify, TikTok Shop, and Dropshipping product inventory sync.
    """
    return {
        "status": "SKELETON",
        "supported_platforms": ["Shopify", "TikTok Shop", "WooCommerce", "Dropship Catalog"],
        "items": [
            {
                "external_sku": "SKU-BTT-001",
                "name": "Bánh Trung Thu Thượng Hạng - Hộp Quà 4 Bánh",
                "price_usd": 49.9,
                "inventory_level": 150,
                "platform": "Shopify",
                "is_mock": True,
            }
        ],
    }
