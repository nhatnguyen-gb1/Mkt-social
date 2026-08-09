import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_audit_logs_generated_on_product_actions(client: AsyncClient):
    # Perform a product creation action
    create_res = await client.post(
        "/api/v1/products",
        json={"name": "Audit Test Product", "category": "Test"},
    )
    assert create_res.status_code == 201
    product_id = create_res.json()["id"]

    # Check audit logs GET endpoint
    audit_res = await client.get("/api/v1/audit-logs")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["total"] >= 1

    actions = [item["action"] for item in audit_data["items"]]
    assert "PRODUCT_CREATED" in actions

    # Update product and verify new audit entry created
    await client.patch(f"/api/v1/products/{product_id}", json={"name": "Updated Audit Product"})

    audit_res2 = await client.get("/api/v1/audit-logs")
    assert audit_res2.status_code == 200
    actions2 = [item["action"] for item in audit_res2.json()["items"]]
    assert "PRODUCT_UPDATED" in actions2
