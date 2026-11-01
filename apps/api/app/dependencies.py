from __future__ import annotations

import re

from fastapi import Header

from .errors import ApiError


WORKSPACE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,120}$")


def get_workspace_id(x_workspace_id: str = Header(default="default")) -> str:
    if not WORKSPACE_PATTERN.fullmatch(x_workspace_id):
        raise ApiError(400, "invalid_workspace", "X-Workspace-ID must contain only letters, numbers, _ or -.")
    return x_workspace_id
