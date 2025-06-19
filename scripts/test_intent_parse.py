import sys
import json
from typing import Any, Dict

import httpx

API_URL = "http://127.0.0.1:8000/api/v1/intent/parse"


def call_intent_parse(user_input: str) -> Dict[str, Any]:
    """Call the local intent/parse endpoint and return JSON response."""
    payload = {"userInput": user_input}
    headers = {"Content-Type": "application/json"}
    with httpx.Client() as client:
        resp = client.post(API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_intent_parse.py <text>")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    try:
        data = call_intent_parse(text)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except httpx.HTTPError as exc:
        print(f"Request failed: {exc}")
        if exc.response is not None:
            try:
                print("Server response:", exc.response.text)
            except Exception:  # noqa: BLE001
                pass
        sys.exit(2)


if __name__ == "__main__":
    main() 