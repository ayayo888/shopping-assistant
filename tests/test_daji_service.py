from unittest.mock import AsyncMock, patch

import pytest
from httpx import HTTPStatusError, Request, Response

from backend.services import daji_service


@pytest.mark.asyncio
@patch("backend.services.daji_service.httpx.AsyncClient")
async def test_fetch_product_detail_success(MockAsyncClient, monkeypatch):
    """Test successful fetch from real API with credentials."""
    # Mock the successful API response
    mock_api_response = {"data": {"item": {"title": "Real Taobao Item"}}}
    mock_response = Response(200, json=mock_api_response)
    mock_response.request = Request("GET", "https://anyurl.com")  # Attach dummy request
    instance = MockAsyncClient.return_value.__aenter__.return_value
    instance.get.return_value = mock_response

    # Patch credentials
    monkeypatch.setattr(daji_service, "DAJI_API_KEY", "fake_key")
    monkeypatch.setattr(daji_service, "DAJI_API_SECRET", "fake_secret")

    url = "https://item.taobao.com/item.htm?id=12345"
    result = await daji_service.fetch_product_detail(url)

    assert result["data"]["item"]["title"] == "Real Taobao Item"
    instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_product_detail_no_credentials(monkeypatch):
    """Test fallback to fake data when credentials are not set."""
    # Ensure credentials are not set
    monkeypatch.setattr(daji_service, "DAJI_API_KEY", None)

    url = "https://item.taobao.com/item.htm?id=12345"
    result = await daji_service.fetch_product_detail(url)

    assert result["platform"] == "taobao"
    assert "耐克" in result["title"]  # Check for default fake product


@pytest.mark.asyncio
@patch("backend.services.daji_service.httpx.AsyncClient")
async def test_fetch_product_detail_api_failure(MockAsyncClient, monkeypatch):
    """Test fallback to fake data on API error (e.g., 500)."""
    # Mock a server error
    instance = MockAsyncClient.return_value.__aenter__.return_value
    request = Request("GET", "https://someurl")
    instance.get.side_effect = HTTPStatusError(
        "Server Error", request=request, response=Response(500)
    )

    # Patch credentials
    monkeypatch.setattr(daji_service, "DAJI_API_KEY", "fake_key")
    monkeypatch.setattr(daji_service, "DAJI_API_SECRET", "fake_secret")

    url = "https://detail.1688.com/offer/890123.html"
    result = await daji_service.fetch_product_detail(url)

    assert result["platform"] == "1688"
    assert "阿迪达斯" in result["title"]


@pytest.mark.asyncio
async def test_fetch_product_detail_invalid_url():
    """Test response for a URL where the product ID cannot be parsed."""
    url = "https://taobao.com/not-a-product-page/"
    result = await daji_service.fetch_product_detail(url)

    # Should return one of the random fake products
    assert "platform" in result
    assert "productId" in result 