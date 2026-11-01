from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import Base


@pytest.fixture
def database_url(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'webverse-test.db').as_posix()}"


@pytest.fixture
def app(database_url):
    application = create_app(database_url)
    Base.metadata.create_all(application.state.engine)
    yield application
    application.state.engine.dispose()


@pytest.fixture
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def workspace_headers() -> dict[str, str]:
    return {"X-Workspace-ID": "workspace-a"}
