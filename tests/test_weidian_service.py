from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response

from backend.services import weidian_service


@pytest.mark.asyncio
@patch("backend.services.weidian_service.httpx.AsyncClient")
async def test_fetch_product_detail_success(MockAsyncClient, monkeypatch):
    """Test successful fetch from the Weidian API."""
    mock_api_response = {"result": {"itemName": "Real Weidian Item"}}
    mock_response = Response(200, json=mock_api_response)
    mock_response.request = Request("GET", "https://anyurl.com")
    instance = MockAsyncClient.return_value.__aenter__.return_value
    instance.get.return_value = mock_response

    monkeypatch.setattr(weidian_service, "RAPIDAPI_KEY", "fake_key")

    url = "https://weidian.com/item.html?itemID=w123"
    result = await weidian_service.fetch_product_detail(url)

    assert result["result"]["itemName"] == "Real Weidian Item"
    instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_product_detail_no_credentials(monkeypatch):
    """Test fallback to fake data when RAPIDAPI_KEY is not set."""
    monkeypatch.setattr(weidian_service, "RAPIDAPI_KEY", None)
    url = "https://weidian.com/item.html?itemID=w123"
    result = await weidian_service.fetch_product_detail(url)
    assert result == weidian_service._FAKE_PRODUCT


@pytest.mark.asyncio
@patch("backend.services.weidian_service.httpx.AsyncClient")
async def test_fetch_product_detail_api_failure(MockAsyncClient, monkeypatch):
    """Test fallback to fake data on API error."""
    request = Request("GET", "https://anyurl.com")
    instance = MockAsyncClient.return_value.__aenter__.return_value
    instance.get.side_effect = HTTPStatusError(
        "Server Error", request=request, response=Response(500)
    )

    monkeypatch.setattr(weidian_service, "RAPIDAPI_KEY", "fake_key")
    url = "https://weidian.com/item.html?itemID=w123"
    result = await weidian_service.fetch_product_detail(url)
    assert result == weidian_service._FAKE_PRODUCT

@pytest.mark.asyncio
async def test_fetch_product_detail_invalid_url():
    """Test fallback for a URL where the product ID cannot be parsed."""
    url = "https://weidian.com/not-a-product-page/"
    result = await weidian_service.fetch_product_detail(url)
    assert result == weidian_service._FAKE_PRODUCT 