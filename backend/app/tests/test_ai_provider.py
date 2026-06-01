import pytest
from app.services.ai_provider import GeminiArchitectureProvider

@pytest.mark.asyncio
async def test_deterministic_provider_shape(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    data = await GeminiArchitectureProvider().generate("Build a scalable food delivery platform with payments and analytics")
    assert "functional_requirements" in data
    assert "mermaid_diagrams" in data
    assert "system" in data["mermaid_diagrams"]
