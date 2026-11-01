from fastapi.testclient import TestClient

from app.main import app
from app.mock_provider import generate_site_spec


client = TestClient(app)


def test_portfolio_spec_contains_3d_hero_and_required_pages() -> None:
    spec = generate_site_spec("Create a creative developer portfolio", "portfolio", True)
    assert spec["project"]["category"] == "portfolio"
    assert spec["pages"][0]["sections"][0]["type"] == "3d-hero"
    assert spec["pages"][0]["sections"][0]["scene"]["enabled"] is True


def test_restaurant_spec_uses_restaurant_content() -> None:
    spec = generate_site_spec("Create an Italian restaurant website", "restaurant", True)
    assert spec["project"]["name"] == "Bella Italia"
    assert any(page["path"] == "/menu" for page in spec["pages"])


def test_3d_can_be_disabled() -> None:
    spec = generate_site_spec("Create a website", "other", False)
    assert spec["pages"][0]["sections"][0]["scene"]["enabled"] is False


def test_generation_endpoint_returns_validated_site_spec() -> None:
    response = client.post(
        "/api/generations",
        json={"prompt": "Create a warm portfolio for a product designer", "category": "portfolio", "enable_3d": True},
        headers={"Origin": "http://127.0.0.1:3000"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    payload = response.json()
    assert payload["provider"] == "mock"
    assert payload["site_spec"]["schemaVersion"] == "0.1.0"
    assert payload["site_spec"]["project"]["description"].startswith("Create a warm")
    assert "scene" not in payload["site_spec"]["pages"][0]["sections"][1]


def test_generation_endpoint_rejects_short_prompts() -> None:
    response = client.post(
        "/api/generations",
        json={"prompt": "Too short", "category": "portfolio", "enable_3d": True},
    )
    assert response.status_code == 422
