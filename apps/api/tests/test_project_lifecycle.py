from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.errors import ApiError
from app.main import create_app
from app.models import Base, GenerationRun, ProjectVersion
from app.services import append_version, create_generation_run, validated_spec


PORTFOLIO_REQUEST = {
    "prompt": "Create a warm portfolio for a product designer with selected work",
    "category": "portfolio",
    "enable_3d": True,
}


def create_project(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post("/api/projects", json=PORTFOLIO_REQUEST, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_project_creation_and_retrieval(client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project = created["project"]
    assert project["current_version_number"] == 1
    assert created["version"]["version_number"] == 1
    assert "scene" not in created["version"]["site_spec"]["pages"][0]["sections"][1]

    retrieved = client.get(f"/api/projects/{project['id']}", headers=workspace_headers)
    assert retrieved.status_code == 200
    assert retrieved.json()["current_version"]["site_spec"] == created["version"]["site_spec"]


def test_project_persists_across_application_restart(database_url, workspace_headers) -> None:
    first_app = create_app(database_url)
    Base.metadata.create_all(first_app.state.engine)
    with TestClient(first_app) as first_client:
        created = create_project(first_client, workspace_headers)
        project_id = created["project"]["id"]
    first_app.state.engine.dispose()

    second_app = create_app(database_url)
    with TestClient(second_app) as second_client:
        response = second_client.get(f"/api/projects/{project_id}", headers=workspace_headers)
        assert response.status_code == 200
        assert response.json()["current_version_number"] == 1
    second_app.state.engine.dispose()


def test_new_versions_are_sequential_and_historical_versions_are_immutable(client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    original_version = created["version"]

    generated = client.post(
        f"/api/projects/{project_id}/generate",
        json={"prompt": "Create a revised portfolio focused on motion systems", "change_description": "Motion-focused revision"},
        headers=workspace_headers,
    )
    assert generated.status_code == 200, generated.text
    assert generated.json()["version"]["version_number"] == 2

    old_response = client.get(
        f"/api/projects/{project_id}/versions/{original_version['id']}", headers=workspace_headers
    )
    assert old_response.status_code == 200
    assert old_response.json()["site_spec"] == original_version["site_spec"]
    assert old_response.json()["site_spec"]["project"]["description"] == PORTFOLIO_REQUEST["prompt"]


def test_failed_transaction_rolls_back_version(app, client, workspace_headers, monkeypatch) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    session_factory = app.state.session_factory

    with session_factory() as session:
        run = create_generation_run(session, project_id, "generate")
        original_commit = session.commit

        def fail_commit() -> None:
            raise RuntimeError("simulated commit failure")

        monkeypatch.setattr(session, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="simulated commit failure"):
            append_version(
                session,
                project_id,
                "workspace-a",
                created["version"]["site_spec"],
                "Should roll back",
                run.id,
            )
        monkeypatch.setattr(session, "commit", original_commit)

    with session_factory() as verification:
        count = verification.scalar(
            select(func.count()).select_from(ProjectVersion).where(ProjectVersion.project_id == project_id)
        )
        assert count == 1


def test_concurrent_version_creation_uses_unique_sequential_numbers(app, client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    session_factory = app.state.session_factory
    run_ids: list[str] = []
    with session_factory() as session:
        for _ in range(3):
            run_ids.append(create_generation_run(session, project_id, "generate").id)

    def add_version(run_id: str, index: int) -> int:
        with session_factory() as session:
            spec = copy.deepcopy(created["version"]["site_spec"])
            spec["project"]["description"] = f"Concurrent revision {index}"
            _, version = append_version(
                session, project_id, "workspace-a", spec, f"Concurrent {index}", run_id
            )
            return version.version_number

    with ThreadPoolExecutor(max_workers=3) as executor:
        numbers = list(executor.map(add_version, run_ids, range(3)))

    assert sorted(numbers) == [2, 3, 4]
    response = client.get(f"/api/projects/{project_id}/versions", headers=workspace_headers)
    assert [version["version_number"] for version in response.json()] == [4, 3, 2, 1]


def test_restore_creates_new_version_without_changing_history(client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    version_one = created["version"]
    generated = client.post(
        f"/api/projects/{project_id}/generate",
        json={"prompt": "Create a stark editorial revision for the same portfolio"},
        headers=workspace_headers,
    ).json()

    restored = client.post(
        f"/api/projects/{project_id}/versions/{version_one['id']}/restore", headers=workspace_headers
    )
    assert restored.status_code == 200, restored.text
    assert restored.json()["version"]["version_number"] == 3
    assert restored.json()["version"]["site_spec"] == version_one["site_spec"]

    version_two = client.get(
        f"/api/projects/{project_id}/versions/{generated['version']['id']}", headers=workspace_headers
    ).json()
    assert version_two["version_number"] == 2
    assert version_two["site_spec"] == generated["version"]["site_spec"]


def test_invalid_site_spec_is_rejected_before_persistence(app, client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    invalid = copy.deepcopy(created["version"]["site_spec"])
    invalid["theme"]["colors"]["primary"] = "not-a-color"
    with pytest.raises(ApiError) as error:
        validated_spec(invalid)
    assert error.value.code == "invalid_site_spec"

    response = client.get(f"/api/projects/{project_id}/versions", headers=workspace_headers)
    assert len(response.json()) == 1


def test_failed_generation_run_is_recorded(app, client, workspace_headers, monkeypatch) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    monkeypatch.setattr("app.services.generate_site_spec", lambda *_: {"invalid": True})

    response = client.post(
        f"/api/projects/{project_id}/generate",
        json={"prompt": "Create a revision that will fail validation"},
        headers=workspace_headers,
    )
    assert response.status_code == 422
    with app.state.session_factory() as session:
        runs = list(session.scalars(select(GenerationRun).where(GenerationRun.project_id == project_id)))
        assert runs[-1].status == "failed"
        assert runs[-1].resulting_version_id is None


def test_previewing_older_version_returns_exact_snapshot(client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    version_one = created["version"]
    client.post(
        f"/api/projects/{project_id}/generate",
        json={"prompt": "Create a second saved version for preview testing"},
        headers=workspace_headers,
    )

    preview = client.get(
        f"/api/projects/{project_id}/preview/{version_one['id']}", headers=workspace_headers
    )
    assert preview.status_code == 200
    assert preview.json()["version"]["version_number"] == 1
    assert preview.json()["version"]["site_spec"] == version_one["site_spec"]


def test_workspace_boundary_hides_projects_and_versions(client, workspace_headers) -> None:
    created = create_project(client, workspace_headers)
    project_id = created["project"]["id"]
    version_id = created["version"]["id"]
    other_workspace = {"X-Workspace-ID": "workspace-b"}

    assert client.get(f"/api/projects/{project_id}", headers=other_workspace).status_code == 404
    assert client.get(
        f"/api/projects/{project_id}/versions/{version_id}", headers=other_workspace
    ).status_code == 404
    assert client.get(f"/api/projects", headers=other_workspace).json() == []
