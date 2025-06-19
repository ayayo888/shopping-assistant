from __future__ import annotations

"""Weidian product detail fetch via RapidAPI.
Falls back to static data if RAPIDAPI_KEY missing or request fails.
"""

from typing import Any, Dict
import os
import asyncio
import random
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
WEIDIAN_API_BASE_URL = "https://weidian-api2.p.rapidapi.com/"

_FAKE_PRODUCT = {
    "platform": "weidian",
    "productId": "w123",
    "title": "卫衣纯棉连帽上衣",
    "price": 199.0,
    "url": "https://weidian.com/item.html?itemID=w123",
}


def _parse_weidian_id(url: str) -> str | None:
    m = re.search(r"itemID=([\w\d]+)", url)
    return m.group(1) if m else None


async def _api_get_product(product_id: str) -> Dict[str, Any]:
    endpoint_path = "weidian/detail/v5"
    url = f"{WEIDIAN_API_BASE_URL}{endpoint_path}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "weidian-api2.p.rapidapi.com",
    }
    params = {"itemId": product_id}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_product_detail(url: str) -> Dict[str, Any]:
    """Return product detail for Weidian URL with graceful fallback."""
    product_id = _parse_weidian_id(url)
    if not product_id:
        return _FAKE_PRODUCT

    if not RAPIDAPI_KEY:
        await asyncio.sleep(0.05)
        return _FAKE_PRODUCT

    try:
        return await _api_get_product(product_id)
    except Exception:  # pragma: no cover
        return _FAKE_PRODUCT 