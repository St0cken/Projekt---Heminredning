from __future__ import annotations

import os
from pathlib import Path
from typing import Dict
from uuid import UUID

from .schemas import Project


class ProjectStore:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[UUID, Project] = {}

    def add_project(self, project: Project) -> None:
        self.projects[project.id] = project

    def get(self, project_id: UUID) -> Project:
        if project_id not in self.projects:
            raise KeyError("Project not found")
        return self.projects[project_id]

    def save_wall_image(self, project_id: UUID, wall_id: str, file_data: bytes, filename: str) -> str:
        project_dir = self.base_dir / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{wall_id}_{filename}"
        target = project_dir / safe_name
        with target.open("wb") as f:
            f.write(file_data)
        return str(target)

    def save_rendered_wall(self, project_id: UUID, wall_id: str, image_bytes: bytes) -> str:
        render_dir = self.base_dir / str(project_id) / "renders"
        render_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{wall_id}_render.png"
        target = render_dir / filename
        with target.open("wb") as f:
            f.write(image_bytes)
        return str(target)


def ensure_dirs() -> None:
    os.makedirs("runtime/uploads", exist_ok=True)
    os.makedirs("runtime/renders", exist_ok=True)


store = ProjectStore(base_dir="runtime/uploads")
