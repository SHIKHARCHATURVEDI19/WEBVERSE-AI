from __future__ import annotations

from uuid import uuid4
from typing import Any


def generate_site_spec(prompt: str, category: str, enable_3d: bool) -> dict[str, Any]:
    """Return a deterministic demo SiteSpec without any external model calls."""
    restaurant = category == "restaurant"
    title = "Bella Italia" if restaurant else "Alex Morgan — Creative Developer"
    pages = (
        [
            {
                "id": "home", "path": "/", "title": "Home",
                "sections": [
                    {"id": "hero", "type": "3d-hero", "title": "A little taste of Italy.", "scene": {"preset": "floating-pizza", "enabled": enable_3d, "rotationSpeed": 0.25}},
                    {"id": "menu", "type": "menu-grid", "title": "Made with amore"},
                    {"id": "story", "type": "about", "title": "Our story"},
                    {"id": "booking", "type": "booking-form", "title": "Save your table"}
                ]
            },
            {"id": "menu-page", "path": "/menu", "title": "Menu", "sections": [{"id": "menu-all", "type": "menu-grid", "title": "The menu"}]},
            {"id": "contact", "path": "/contact", "title": "Contact", "sections": [{"id": "contact-info", "type": "contact", "title": "Come say hello"}]}
        ]
        if restaurant
        else [
            {
                "id": "home", "path": "/", "title": "Home",
                "sections": [
                    {"id": "hero", "type": "3d-hero", "title": "Ideas made tangible.", "scene": {"preset": "abstract-sculpture", "enabled": enable_3d, "rotationSpeed": 0.2}},
                    {"id": "work", "type": "project-grid", "title": "Selected work"},
                    {"id": "about", "type": "about", "title": "A little about me"},
                    {"id": "contact", "type": "contact", "title": "Let's make something"}
                ]
            },
            {"id": "projects", "path": "/projects", "title": "Projects", "sections": [{"id": "all-work", "type": "project-grid", "title": "All projects"}]}
        ]
    )
    return {
        "schemaVersion": "0.1.0",
        "project": {"name": title, "category": category, "description": prompt},
        "theme": {
            "colors": {"primary": "#C96532", "background": "#FBF6ED", "surface": "#FFFDF8", "text": "#2D2925", "muted": "#8A7C70"},
            "fonts": {"display": "Playfair Display", "body": "DM Sans"},
            "radius": "medium"
        },
        "pages": pages,
        "assets": [],
        "metadata": {"provider": "mock", "generated": False, "notes": "Deterministic starter output. No AI API was called."}
    }


def create_generation(prompt: str, category: str, enable_3d: bool) -> dict[str, Any]:
    return {
        "project_id": f"prj_{uuid4().hex[:10]}",
        "run_id": f"run_{uuid4().hex[:10]}",
        "status": "completed",
        "provider": "mock",
        "site_spec": generate_site_spec(prompt, category, enable_3d),
    }
