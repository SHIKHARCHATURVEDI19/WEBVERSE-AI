from __future__ import annotations

import copy
import re
import time
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from .errors import ApiError
from .mock_provider import generate_site_spec
from .models import GenerationRun, Project, ProjectVersion, utc_now
from .schemas import SiteSpec


def validated_spec(value: dict[str, Any]) -> dict[str, Any]:
    try:
        spec = SiteSpec.model_validate(value)
    except ValidationError as exc:
        raise ApiError(422, "invalid_site_spec", "The SiteSpec failed validation.", exc.errors()) from exc
    return spec.model_dump(mode="json", by_alias=True, exclude_none=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:120] or "untitled-project"


def _unique_slug(session: Session, workspace_id: str, name: str) -> str:
    base = slugify(name)
    candidate = base
    suffix = 2
    while session.scalar(select(Project.id).where(Project.workspace_id == workspace_id, Project.slug == candidate)):
        candidate = f"{base[:110]}-{suffix}"
        suffix += 1
    return candidate


def get_project(session: Session, project_id: str, workspace_id: str, *, lock: bool = False) -> Project:
    query = select(Project).where(Project.id == project_id, Project.workspace_id == workspace_id)
    if lock:
        query = query.with_for_update()
    project = session.scalar(query)
    if project is None:
        raise ApiError(404, "project_not_found", "Project not found.")
    return project


def get_version(session: Session, project_id: str, version_id: str, workspace_id: str) -> ProjectVersion:
    version = session.scalar(
        select(ProjectVersion)
        .join(Project, Project.id == ProjectVersion.project_id)
        .where(
            ProjectVersion.id == version_id,
            ProjectVersion.project_id == project_id,
            Project.workspace_id == workspace_id,
        )
    )
    if version is None:
        raise ApiError(404, "version_not_found", "Project version not found.")
    return version


def version_payload(version: ProjectVersion) -> dict[str, Any]:
    return {
        "id": version.id,
        "project_id": version.project_id,
        "version_number": version.version_number,
        "site_spec": validated_spec(version.site_spec),
        "change_description": version.change_description,
        "created_at": version.created_at,
    }


def project_payload(session: Session, project: Project) -> dict[str, Any]:
    if project.current_version_id is None:
        raise ApiError(409, "project_has_no_version", "Project has no current version.")
    current = session.get(ProjectVersion, project.current_version_id)
    if current is None:
        raise ApiError(409, "current_version_missing", "The project's current version is missing.")
    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "site_type": project.site_type,
        "status": project.status,
        "current_version_id": current.id,
        "current_version_number": current.version_number,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "current_version": version_payload(current),
    }


def project_summary_payload(session: Session, project: Project) -> dict[str, Any]:
    payload = project_payload(session, project)
    payload.pop("current_version")
    return payload


def create_project(
    session: Session,
    workspace_id: str,
    prompt: str,
    category: str,
    enable_3d: bool,
) -> tuple[Project, ProjectVersion, GenerationRun]:
    site_spec = validated_spec(generate_site_spec(prompt, category, enable_3d))
    project = Project(
        workspace_id=workspace_id,
        name=site_spec["project"]["name"],
        slug=_unique_slug(session, workspace_id, site_spec["project"]["name"]),
        site_type=category,
        status="active",
    )
    try:
        session.add(project)
        session.flush()
        version = ProjectVersion(
            project_id=project.id,
            version_number=1,
            site_spec=site_spec,
            change_description="Initial generation",
        )
        session.add(version)
        session.flush()
        run = GenerationRun(
            project_id=project.id,
            resulting_version_id=version.id,
            status="completed",
            generation_mode="create",
            completed_at=utc_now(),
        )
        project.current_version_id = version.id
        session.add(run)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return project, version, run


def create_generation_run(session: Session, project_id: str, mode: str) -> GenerationRun:
    run = GenerationRun(project_id=project_id, status="running", generation_mode=mode)
    session.add(run)
    session.commit()
    return run


def mark_run_failed(session: Session, run_id: str, message: str) -> None:
    session.rollback()
    run = session.get(GenerationRun, run_id)
    if run is None:
        return
    run.status = "failed"
    run.error_message = message[:500]
    run.completed_at = utc_now()
    session.commit()


def append_version(
    session: Session,
    project_id: str,
    workspace_id: str,
    site_spec: dict[str, Any],
    change_description: str,
    run_id: str,
    *,
    max_attempts: int = 5,
) -> tuple[Project, ProjectVersion]:
    snapshot = validated_spec(site_spec)
    for attempt in range(max_attempts):
        try:
            project = get_project(session, project_id, workspace_id, lock=True)
            highest = session.scalar(
                select(func.max(ProjectVersion.version_number)).where(ProjectVersion.project_id == project_id)
            ) or 0
            version = ProjectVersion(
                project_id=project.id,
                version_number=highest + 1,
                site_spec=copy.deepcopy(snapshot),
                change_description=change_description,
            )
            session.add(version)
            session.flush()
            run = session.get(GenerationRun, run_id)
            if run is None or run.project_id != project.id:
                raise ApiError(409, "generation_run_missing", "Generation run could not be completed.")
            project.current_version_id = version.id
            project.updated_at = utc_now()
            run.resulting_version_id = version.id
            run.status = "completed"
            run.completed_at = utc_now()
            session.commit()
            return project, version
        except (IntegrityError, OperationalError) as exc:
            session.rollback()
            if attempt + 1 == max_attempts:
                raise ApiError(409, "version_conflict", "A concurrent version update could not be resolved.") from exc
            time.sleep(0.02 * (attempt + 1))
        except Exception:
            session.rollback()
            raise
    raise ApiError(409, "version_conflict", "A concurrent version update could not be resolved.")


def generate_new_version(
    session: Session,
    project_id: str,
    workspace_id: str,
    prompt: str,
    enable_3d: bool,
    change_description: str | None,
) -> tuple[Project, ProjectVersion, GenerationRun]:
    project = get_project(session, project_id, workspace_id)
    category = project.site_type
    run = create_generation_run(session, project.id, "generate")
    try:
        spec = generate_site_spec(prompt, category, enable_3d)
        description = change_description or f"Generated from prompt: {prompt[:450]}"
        project, version = append_version(
            session, project.id, workspace_id, spec, description, run.id
        )
        return project, version, run
    except Exception as exc:
        mark_run_failed(session, run.id, str(exc))
        raise


def restore_version(
    session: Session,
    project_id: str,
    version_id: str,
    workspace_id: str,
) -> tuple[Project, ProjectVersion, GenerationRun]:
    project = get_project(session, project_id, workspace_id)
    source = get_version(session, project.id, version_id, workspace_id)
    run = create_generation_run(session, project.id, "restore")
    try:
        project, restored = append_version(
            session,
            project.id,
            workspace_id,
            copy.deepcopy(source.site_spec),
            f"Restored from version {source.version_number}",
            run.id,
        )
        return project, restored, run
    except Exception as exc:
        mark_run_failed(session, run.id, str(exc))
        raise


def list_projects(session: Session, workspace_id: str) -> list[Project]:
    return list(
        session.scalars(
            select(Project).where(Project.workspace_id == workspace_id).order_by(Project.updated_at.desc())
        )
    )


def list_versions(session: Session, project_id: str, workspace_id: str) -> list[ProjectVersion]:
    get_project(session, project_id, workspace_id)
    return list(
        session.scalars(
            select(ProjectVersion)
            .where(ProjectVersion.project_id == project_id)
            .order_by(ProjectVersion.version_number.desc())
        )
    )


def delete_project(session: Session, project_id: str, workspace_id: str) -> None:
    project = get_project(session, project_id, workspace_id, lock=True)
    try:
        project.current_version_id = None
        session.flush()
        session.delete(project)
        session.commit()
    except Exception:
        session.rollback()
        raise
