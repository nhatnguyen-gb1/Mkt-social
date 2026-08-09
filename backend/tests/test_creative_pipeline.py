import pytest
import uuid
from httpx import AsyncClient
from app.core.media.factory import MediaGeneratorFactory
from app.core.media.mock_media_provider import MockImageGenerator
from app.core.llm.mock_provider import MockLLMProvider
from app.agents.marketing_strategy_agent import MarketingStrategyAgent
from app.agents.creative_agent import CreativeAgent


@pytest.mark.asyncio
async def test_mock_image_generator():
    generator = MediaGeneratorFactory.get_image_generator("mock")
    assert isinstance(generator, MockImageGenerator)
    assert generator.get_provider_name() == "mock"

    res = await generator.generate_image(
        prompt="High resolution mooncake gift box photoshoot",
        size="1024x1024",
        style="vivid",
    )
    assert "file_url" in res
    assert res["provider"] == "mock"
    assert res["metadata"]["is_mock"] is True


@pytest.mark.asyncio
async def test_marketing_strategy_agent_execution():
    llm = MockLLMProvider()
    agent = MarketingStrategyAgent(llm_provider=llm)
    state = await agent.run({"product_name": "Bánh Trung Thu", "market_research_summary": "Tốt"})
    assert state.status == "COMPLETED"
    assert "ad_concepts" in state.final_result
    assert len(state.final_result["ad_concepts"]) >= 1


@pytest.mark.asyncio
async def test_creative_agent_execution():
    llm = MockLLMProvider()
    agent = CreativeAgent(llm_provider=llm)
    state = await agent.run({"product_name": "Bánh Trung Thu", "strategy_summary": "Cao cấp"})
    assert state.status == "COMPLETED"
    assert "image_prompts" in state.final_result
    assert "video_scripts" in state.final_result


@pytest.mark.asyncio
async def test_strategy_api_endpoint(client: AsyncClient):
    payload = {
        "product_name": "Bánh Trung Thu",
        "market_research_summary": "Thị trường quà tặng cao cấp tăng trưởng 20%",
        "provider": "mock",
    }
    response = await client.post("/api/v1/agents/strategy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["agent_name"] == "MarketingStrategyAgent"
    assert "ad_concepts" in data["result"]


@pytest.mark.asyncio
async def test_creative_api_endpoint(client: AsyncClient):
    payload = {
        "product_name": "Bánh Trung Thu",
        "strategy_summary": "Định vị sản phẩm quà tặng ngoại giao cao cấp",
        "provider": "mock",
    }
    response = await client.post("/api/v1/agents/creative", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["agent_name"] == "CreativeAgent"
    assert "image_prompts" in data["result"]


@pytest.mark.asyncio
async def test_asset_image_generation_and_retrieval(client: AsyncClient):
    # 1. Generate image asset
    gen_payload = {
        "title": "Ảnh Banner Bánh Trung Thu - Test",
        "prompt": "Luxury mooncake box, cinematic studio lighting",
        "size": "1024x1024",
        "style": "vivid",
        "provider": "mock",
    }
    create_res = await client.post("/api/v1/assets/generate-image", json=gen_payload)
    assert create_res.status_code == 201
    asset_data = create_res.json()
    assert asset_data["title"] == "Ảnh Banner Bánh Trung Thu - Test"
    assert asset_data["asset_type"] == "IMAGE"
    assert asset_data["status"] == "APPROVED"
    asset_id = asset_data["id"]

    # 2. Get asset by ID
    get_res = await client.get(f"/api/v1/assets/{asset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == asset_id

    # 3. List assets
    list_res = await client.get("/api/v1/assets")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
