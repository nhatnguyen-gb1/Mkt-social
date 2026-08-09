import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services.product_service import ProductService
from app.api.dependencies import get_product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Product",
)
async def create_product(
    product_in: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(product_in)


@router.get(
    "",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Products",
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products(page=page, size=size)


@router.get(
    "/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Product by ID",
)
async def get_product(
    id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_product(id)


@router.patch(
    "/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a Product",
)
async def update_product(
    id: uuid.UUID,
    product_in: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(id, product_in)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Product",
)
async def delete_product(
    id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product(id)
    return None
