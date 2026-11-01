from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


SiteCategory = Literal["portfolio", "restaurant", "other"]
SectionType = Literal[
    "3d-hero", "hero", "about", "project-grid", "menu-grid", "gallery",
    "booking-form", "contact", "faq", "testimonials", "footer",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerateRequest(StrictModel):
    prompt: str = Field(min_length=10, max_length=4000)
    category: SiteCategory = "other"
    enable_3d: bool = True


class ProjectSpec(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    category: SiteCategory
    description: str = Field(default="", max_length=4000)


class ColorSpec(StrictModel):
    primary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    surface: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    muted: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class FontSpec(StrictModel):
    display: str
    body: str


class ThemeSpec(StrictModel):
    colors: ColorSpec
    fonts: FontSpec
    radius: Literal["small", "medium", "large"] = "medium"


class SceneSpec(StrictModel):
    preset: str
    enabled: bool = True
    rotation_speed: float = Field(default=0.2, alias="rotationSpeed", ge=0, le=2)


class SectionSpec(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    type: SectionType
    title: str = Field(max_length=180)
    scene: SceneSpec | None = None


class PageSpec(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    path: str = Field(pattern=r"^/")
    title: str = Field(max_length=120)
    sections: list[SectionSpec] = Field(default_factory=list, max_length=40)


class SiteSpec(StrictModel):
    schemaVersion: str
    project: ProjectSpec
    theme: ThemeSpec
    pages: list[PageSpec] = Field(min_length=1, max_length=20)
    assets: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationResponse(StrictModel):
    project_id: str
    run_id: str
    status: Literal["completed"]
    provider: Literal["mock"]
    site_spec: SiteSpec


class ProjectCreateRequest(StrictModel):
    prompt: str = Field(min_length=10, max_length=4000)
    category: SiteCategory
    enable_3d: bool = True


class ProjectGenerateRequest(StrictModel):
    prompt: str = Field(min_length=10, max_length=4000)
    enable_3d: bool = True
    change_description: str | None = Field(default=None, min_length=1, max_length=500)


class VersionSummary(StrictModel):
    id: str
    project_id: str
    version_number: int
    change_description: str
    created_at: datetime


class VersionResponse(VersionSummary):
    site_spec: SiteSpec


class ProjectSummary(StrictModel):
    id: str
    name: str
    slug: str
    site_type: SiteCategory
    status: Literal["active", "archived"]
    current_version_id: str
    current_version_number: int
    created_at: datetime
    updated_at: datetime


class ProjectResponse(ProjectSummary):
    current_version: VersionResponse


class PersistedGenerationResponse(StrictModel):
    project: ProjectResponse
    version: VersionResponse
    run_id: str
    status: Literal["completed"]
    provider: Literal["mock"]


class RestoreResponse(StrictModel):
    project: ProjectResponse
    version: VersionResponse
    run_id: str


class PreviewResponse(StrictModel):
    project_id: str
    project_name: str
    version: VersionResponse
