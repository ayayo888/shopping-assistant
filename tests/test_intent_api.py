import asyncio
from typing import Any, Dict

import pytest
import pytest_asyncio
from httpx import AsyncClient

from backend.main import app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parse_text_intent(monkeypatch, async_client):
    """Pure text input should trigger LLM path and return intent JSON."""

    async def fake_get_intent(text: str) -> Dict[str, Any]:  # noqa: D401
        return {"shopping_intent": True}

    monkeypatch.setattr(
        "backend.services.llm_service.get_shopping_intent", fake_get_intent, raising=True
    )

    payload = {"userInput": "我想买一双耐克跑鞋"}
    resp = await async_client.post("/api/v1/intent/parse", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["hasUrls"] is False
    assert data.get("shopping_intent") is True
    assert data["llmAnalysis"]  # non-empty message


@pytest.mark.asyncio
async def test_parse_url_product(monkeypatch, async_client):
    """URL input should call product service and return product list."""

    fake_product = {
        "platform": "taobao",
        "productId": "123456",
        "title": "测试商品",
        "price": 10.0,
        "url": "https://item.taobao.com/item.htm?id=123456",
    }

    async def fake_fetch(url: str):  # noqa: D401
        return fake_product

    monkeypatch.setattr(
        "backend.services.daji_service.fetch_product_detail", fake_fetch, raising=True
    )

    payload = {"userInput": "https://item.taobao.com/item.htm?id=123456"}
    resp = await async_client.post("/api/v1/intent/parse", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["hasUrls"] is True
    assert data["products"] and data["products"][0]["productId"] == "123456" 