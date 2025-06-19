import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from backend.services.llm_service import get_shopping_intent


@pytest.mark.asyncio
async def test_get_shopping_intent_success(monkeypatch):
    """Test successful intent detection from LLM."""
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({"shopping_intent": True})

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_create = AsyncMock(return_value=mock_completion)
    monkeypatch.setattr("backend.services.llm_service.client.chat.completions.create", mock_create)

    result = await get_shopping_intent("I want to buy new shoes")
    assert result == {"shopping_intent": True}
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_get_shopping_intent_json_decode_error(monkeypatch):
    """Test handling of invalid JSON from LLM."""
    mock_choice = MagicMock()
    mock_choice.message.content = "This is not valid JSON"

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_create = AsyncMock(return_value=mock_completion)
    monkeypatch.setattr("backend.services.llm_service.client.chat.completions.create", mock_create)

    result = await get_shopping_intent("some input")
    assert result["shopping_intent"] is False
    assert "Failed to decode JSON" in result["reason"]


@pytest.mark.asyncio
async def test_get_shopping_intent_api_error(monkeypatch):
    """Test handling of a generic exception from the API call."""
    mock_create = AsyncMock(side_effect=Exception("API is down"))
    monkeypatch.setattr("backend.services.llm_service.client.chat.completions.create", mock_create)

    result = await get_shopping_intent("some input")
    assert result["shopping_intent"] is False
    assert "API is down" in result["reason"]


@pytest.mark.asyncio
async def test_get_shopping_intent_empty_input():
    """Test that empty input is handled correctly without calling the API."""
    result = await get_shopping_intent(" ")
    assert result["shopping_intent"] is False
    assert "Input text is empty" in result["reason"] 