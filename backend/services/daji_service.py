from __future__ import annotations

"""Da-Ji API wrapper (product details & image search).

Implements real HTTP calls when DAJI_API_KEY / DAJI_API_SECRET are configured; otherwise
falls back to deterministic fake data so that the rest of the backend can operate
without external dependency.
"""

from typing import Any, Dict, Optional
import os
import asyncio
import hashlib
import base64
import random
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

DAJI_API_KEY = os.getenv("DAJI_API_KEY")
DAJI_API_SECRET = os.getenv("DAJI_API_SECRET")
DAJI_API_BASE_URL = os.getenv("DAJI_API_BASE_URL", "https://openapi.dajisaas.com/")

############################################################
# Helpers
############################################################

def _sign_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Return params with appKey and sign fields appended."""
    if not DAJI_API_KEY or not DAJI_API_SECRET:
        raise ValueError("DAJI_API_KEY / DAJI_API_SECRET missing")

    params_with_key = {"appKey": DAJI_API_KEY, **params}
    sorted_items = sorted(params_with_key.items())
    sign_str = "&".join(f"{k}={v}" for k, v in sorted_items if v is not None)
    sign_str = f"{sign_str}&secret={DAJI_API_SECRET}"
    md5_hash = hashlib.md5(sign_str.encode()).hexdigest().upper()
    return {**params_with_key, "sign": md5_hash}


def _parse_taobao_id(url: str) -> Optional[str]:
    m = re.search(r"[?&]id=(\d+)", url)
    return m.group(1) if m else None


def _parse_1688_id(url: str) -> Optional[str]:
    # Example: https://detail.1688.com/offer/123456.html
    m = re.search(r"offer/(\d+)", url)
    return m.group(1) if m else None

############################################################
# Real API calls
############################################################

async def _fetch_taobao(product_id: str) -> Dict[str, Any]:
    params = {
        "item_id": product_id,
        "language": "en",
    }
    signed = _sign_params(params)
    url = f"{DAJI_API_BASE_URL}taobao/traffic/item/get"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=signed)
        r.raise_for_status()
        return r.json()


async def _fetch_1688(product_id: str) -> Dict[str, Any]:
    params = {
        "offerId": product_id,
        "country": "en",
    }
    signed = _sign_params(params)
    url = f"{DAJI_API_BASE_URL}alibaba/product/queryProductDetail"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=signed)
        r.raise_for_status()
        return r.json()

############################################################
# Public helper used by backend.main
############################################################

_FAKE_PRODUCTS = [
    {
        "platform": "taobao",
        "productId": "123456",
        "title": "耐克 Air Zoom Pegasus 40 跑鞋",
        "price": 699.0,
        "url": "https://item.taobao.com/item.htm?id=123456",
    },
    {
        "platform": "1688",
        "productId": "890123",
        "title": "阿迪达斯 运动衫",
        "price": 299.0,
        "url": "https://detail.1688.com/offer/890123.html",
    },
]


async def fetch_product_detail(url: str) -> Dict[str, Any]:
    """Return product detail for Taobao / 1688 URL.

    Fallback: when keys missing / API error, return static fake product so that
    the rest of the flow doesn't break.
    """
    platform: str | None = None
    product_id: Optional[str] = None
    if "taobao.com" in url or "tb.cn" in url:
        platform = "taobao"
        product_id = _parse_taobao_id(url)
    elif "1688.com" in url:
        platform = "1688"
        product_id = _parse_1688_id(url)

    if not platform or not product_id:
        return random.choice(_FAKE_PRODUCTS)

    # If credentials missing, return fake matching platform
    if not DAJI_API_KEY or not DAJI_API_SECRET:
        await asyncio.sleep(0.05)
        for prod in _FAKE_PRODUCTS:
            if prod["platform"] == platform:
                return prod
        return random.choice(_FAKE_PRODUCTS)

    try:
        if platform == "taobao":
            return await _fetch_taobao(product_id)
        if platform == "1688":
            return await _fetch_1688(product_id)
    except Exception as exc:  # pragma: no cover
        # network error or invalid response → return fake data matching platform if possible
        for prod in _FAKE_PRODUCTS:
            if prod["platform"] == platform:
                return prod
        return random.choice(_FAKE_PRODUCTS)

    return random.choice(_FAKE_PRODUCTS) 