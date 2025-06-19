import re
from typing import Dict, List

URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)

# Supported e-commerce platforms and simple hostname matchers
PLATFORM_RULES = {
    "taobao": re.compile(r"(taobao\.com|tb\.cn)", re.IGNORECASE),
    "1688": re.compile(r"(1688\.com)", re.IGNORECASE),
    "weidian": re.compile(r"(weidian\.com)", re.IGNORECASE),
}


def extract_urls(text: str) -> List[str]:
    """Return all URLs found in *text*."""
    if not text:
        return []
    return URL_REGEX.findall(text)


def detect_platform(url: str) -> str | None:
    """Return platform key if URL matches our supported platforms, else None."""
    for name, pattern in PLATFORM_RULES.items():
        if pattern.search(url):
            return name
    return None


def preprocess_input(text: str) -> Dict[str, object]:
    """Classify *text* as containing product URLs or pure text.

    Returns a dict with:
    - type: "url" | "text"
    - urls: list[str] of extracted URLs (may be empty)
    - platform_map: mapping of platform name -> list[urls]
    - content: Original text (trimmed)
    - skip_llm: bool – True when we can bypass LLM because at least one supported URL exists.
    """
    if text is None:
        text = ""
    text = text.strip()

    urls = extract_urls(text)
    platform_map: dict[str, list[str]] = {}
    for u in urls:
        platform = detect_platform(u)
        if platform:
            platform_map.setdefault(platform, []).append(u)

    has_supported_urls = bool(platform_map)

    return {
        "type": "url" if has_supported_urls else "text",
        "urls": urls,
        "platform_map": platform_map,
        "content": text,
        "skip_llm": has_supported_urls,
    } 