import pytest
from backend.services.preprocessor import preprocess_input


@pytest.mark.parametrize(
    "text, expected_type, expected_urls_count, has_platform, skip_llm",
    [
        (
            "我想买这个 https://item.taobao.com/item.htm?id=123456 还有这个 https://weidian.com/item.html?itemID=w123",
            "url",
            2,
            True,
            True,
        ),
        (
            "就这个链接 https://item.taobao.com/item.htm?id=123456",
            "url",
            1,
            True,
            True,
        ),
        (
            "帮我看看这个怎么样 https://unsupported-shop.com/product/abc",
            "text",
            1,
            False,
            False,
        ),
        ("我想买一双新鞋子，你有什么推荐吗？", "text", 0, False, False),
        ("", "text", 0, False, False),
        (None, "text", 0, False, False),
    ],
)
def test_preprocess_input_scenarios(
    text, expected_type, expected_urls_count, has_platform, skip_llm
):
    """Test preprocess_input across different scenarios."""
    result = preprocess_input(text)

    assert result["type"] == expected_type
    assert len(result["urls"]) == expected_urls_count
    assert bool(result["platform_map"]) == has_platform
    assert result["skip_llm"] is skip_llm
    if text:
        assert result["content"] == text.strip()


def test_preprocess_input_extracts_multiple_platforms():
    """Test mixed supported URLs are correctly mapped."""
    text = (
        "看看这个 https://item.taobao.com/item.htm?id=123 "
        "和这个 https://detail.1688.com/offer/456.html "
        "还有微店的 https://weidian.com/item.html?itemID=789"
    )
    result = preprocess_input(text)
    assert result["skip_llm"] is True
    assert "taobao" in result["platform_map"]
    assert "1688" in result["platform_map"]
    assert "weidian" in result["platform_map"]
    assert len(result["platform_map"]["taobao"]) == 1
    assert len(result["platform_map"]["1688"]) == 1
    assert len(result["platform_map"]["weidian"]) == 1 