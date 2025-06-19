from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Ensure environment variables are loaded when module imported
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")

if OPENROUTER_API_KEY is None:
    raise RuntimeError(
        "OPENROUTER_API_KEY not found. Please set it in your .env or system env vars."
    )

client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=OPENROUTER_API_KEY)


async def get_shopping_intent(text: str) -> Dict[str, Any]:
    """Determine whether *text* expresses shopping intent.

    Returns a dict like {"shopping_intent": bool, ...optional reason }.
    """
    if not text or not text.strip():
        return {"shopping_intent": False, "reason": "Input text is empty."}

    try:
        completion = await client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "get_shopping_intent",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "shopping_intent": {
                                "type": "boolean",
                                "description": "True if the user text expresses shopping intent, false otherwise.",
                            }
                        },
                        "required": ["shopping_intent"],
                    },
                },
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Analyze the user's text to determine if it expresses a direct or"
                        " indirect intent to purchase an item. Respond with only a JSON"
                        " object containing a single key 'shopping_intent' which is a"
                        " boolean value (true or false)."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=50,
        )
        response_text = completion.choices[0].message.content
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"shopping_intent": False, "reason": "Failed to decode JSON from model response."}
    except Exception as exc:  # noqa: BLE001
        return {
            "shopping_intent": False,
            "reason": f"An error occurred while calling LLM: {exc}",
        } 