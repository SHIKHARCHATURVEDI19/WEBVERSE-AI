from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_workspace_id
from ..schemas import (
    PersistedGenerationResponse,
    PreviewResponse,
    ProjectCreateRequest,
    ProjectGenerateRequest,
    ProjectResponse,
    ProjectSummary,
    RestoreResponse,
    VersionResponse,
    VersionSummary,
)
from ..services import (
    create_project,
    delete_project,
    generate_new_version,
    get_project,
    get_version,
    list_projects,
    list_versions,
    project_payload,
    project_summary_payload,
    restore_version,
    version_payload,
)


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post(
    "",
    response_model=PersistedGenerationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_project_route(
    request: ProjectCreateRequest,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    project, version, run = create_project(
        session, workspace_id, request.prompt, request.category, request.enable_3d
    )
    return {
        "project": project_payload(session, project),
        "version": version_payload(version),
        "run_id": run.id,
        "status": "completed",
        "provider": "mock",
    }


@router.get("", response_model=list[ProjectSummary])
def list_projects_route(
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> list[dict]:
    return [project_summary_payload(session, project) for project in list_projects(session, workspace_id)]


@router.get("/{project_id}", response_model=ProjectResponse, response_model_exclude_none=True)
def get_project_route(
    project_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    return project_payload(session, get_project(session, project_id, workspace_id))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_route(
    project_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> Response:
    delete_project(session, project_id, workspace_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{project_id}/versions", response_model=list[VersionSummary])
def list_versions_route(
    project_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> list[dict]:
    versions = list_versions(session, project_id, workspace_id)
    return [
        {key: value for key, value in version_payload(version).items() if key != "site_spec"}
        for version in versions
    ]


@router.get(
    "/{project_id}/versions/{version_id}",
    response_model=VersionResponse,
    response_model_exclude_none=True,
)
def get_version_route(
    project_id: str,
    version_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    return version_payload(get_version(session, project_id, version_id, workspace_id))


@router.post(
    "/{project_id}/versions/{version_id}/restore",
    response_model=RestoreResponse,
    response_model_exclude_none=True,
)
def restore_version_route(
    project_id: str,
    version_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    project, version, run = restore_version(session, project_id, version_id, workspace_id)
    return {
        "project": project_payload(session, project),
        "version": version_payload(version),
        "run_id": run.id,
    }


@router.post(
    "/{project_id}/generate",
    response_model=PersistedGenerationResponse,
    response_model_exclude_none=True,
)
def generate_project_route(
    project_id: str,
    request: ProjectGenerateRequest,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    project, version, run = generate_new_version(
        session,
        project_id,
        workspace_id,
        request.prompt,
        request.enable_3d,
        request.change_description,
    )
    return {
        "project": project_payload(session, project),
        "version": version_payload(version),
        "run_id": run.id,
        "status": "completed",
        "provider": "mock",
    }


@router.get(
    "/{project_id}/preview/{version_id}",
    response_model=PreviewResponse,
    response_model_exclude_none=True,
)
def preview_version_route(
    project_id: str,
    version_id: str,
    session: Session = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> dict:
    project = get_project(session, project_id, workspace_id)
    version = get_version(session, project.id, version_id, workspace_id)
    return {
        "project_id": project.id,
        "project_name": project.name,
        "version": version_payload(version),
    }
