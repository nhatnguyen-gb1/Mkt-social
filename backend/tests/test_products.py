import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient):
    payload = {
        "name": "Alpha Optimizer Pro",
        "description": "AI-powered campaign optimization software",
        "source_url": "https://example.com/alpha-optimizer",
        "category": "SaaS",
        "target_market": "B2B Marketers",
        "status": "ACTIVE",
    }
    response = await client.post("/api/v1/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert "created_at" in data

    # Verify retrieval
    product_id = data["id"]
    get_res = await client.get(f"/api/v1/products/{product_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == product_id


@pytest.mark.asyncio
async def test_create_product_invalid_input(client: AsyncClient):
    # Empty name should fail validation
    payload = {
        "name": "",
        "description": "Invalid product without title",
    }
    response = await client.post("/api/v1/products", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient):
    # Create two products
    await client.post("/api/v1/products", json={"name": "Product 1"})
    await client.post("/api/v1/products", json={"name": "Product 2"})

    response = await client.get("/api/v1/products?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient):
    create_res = await client.post("/api/v1/products", json={"name": "Old Title"})
    product_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Title", "status": "ACTIVE"},
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["name"] == "Updated Title"
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient):
    create_res = await client.post("/api/v1/products", json={"name": "To Delete"})
    product_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/products/{product_id}")
    assert del_res.status_code == 204

    # Verify 404 on subsequent get
    get_res = await client.get(f"/api/v1/products/{product_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_product(client: AsyncClient):
    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/products/{random_id}")
    assert response.status_code == 404
