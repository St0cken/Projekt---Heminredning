from __future__ import annotations

import io
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont

from .catalog import CATALOG
from .schemas import (
    CreateProjectRequest,
    FurniturePlacement,
    Project,
    RenderRequest,
    RenderResponse,
    RenderedWall,
    RoomScale,
    UploadWallResponse,
    WallCalibration,
)
from .storage import ensure_dirs, store

app = FastAPI(title="Heminredningsvisualisering")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_dirs()


@app.get("/catalog")
def catalog():
    return [item.__dict__ for item in CATALOG]


@app.post("/projects", response_model=Project)
def create_project(req: CreateProjectRequest):
    project = Project(name=req.name)
    store.add_project(project)
    return project


@app.post("/projects/{project_id}/walls", response_model=UploadWallResponse)
def upload_wall(project_id: UUID, wall_id: str, file: UploadFile = File(...)):
    project = _get_project(project_id)
    contents = file.file.read()
    filename = store.save_wall_image(project_id, wall_id, contents, file.filename)
    project.walls[wall_id] = {
        "wall_id": wall_id,
        "filename": filename,
    }
    return UploadWallResponse(wall_id=wall_id, stored_filename=filename)


@app.post("/projects/{project_id}/calibrations/{wall_id}")
def set_calibration(project_id: UUID, wall_id: str, calibration: WallCalibration):
    project = _get_project(project_id)
    project.calibrations[wall_id] = calibration
    return {"status": "ok"}


@app.post("/projects/{project_id}/scale")
def set_scale(project_id: UUID, scale: RoomScale):
    project = _get_project(project_id)
    project.scale = scale
    return {"status": "ok"}


@app.post("/projects/{project_id}/placements")
def add_placement(project_id: UUID, placement: FurniturePlacement):
    project = _get_project(project_id)
    project.placements.append(placement)
    return {"status": "ok", "count": len(project.placements)}


@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: UUID):
    return _get_project(project_id)


@app.post("/render", response_model=RenderResponse)
def render(req: RenderRequest):
    project = _get_project(req.project_id)
    walls_to_render: List[str]
    if req.walls:
        walls_to_render = req.walls
    else:
        walls_to_render = list(project.walls.keys())

    rendered: List[RenderedWall] = []
    for wall_id in walls_to_render:
        image_path = project.walls.get(wall_id, {}).get("filename")
        if not image_path:
            raise HTTPException(status_code=400, detail=f"Saknar väggbild {wall_id}")
        base_image = Image.open(image_path).convert("RGBA")
        overlay = _placement_overlay(base_image.size, project, wall_id)
        combined = Image.alpha_composite(base_image, overlay)
        output = io.BytesIO()
        combined.save(output, format="PNG")
        saved_path = store.save_rendered_wall(project.id, wall_id, output.getvalue())
        rendered.append(RenderedWall(wall_id=wall_id, image_path=saved_path))
    return RenderResponse(project_id=project.id, rendered=rendered)


@app.get("/renders/{project_id}/{wall_id}")
def fetch_render(project_id: UUID, wall_id: str):
    path = Path("runtime/uploads") / str(project_id) / "renders" / f"{wall_id}_render.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Render saknas")
    return FileResponse(path)


def _get_project(project_id: UUID) -> Project:
    try:
        return store.get(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Projekt saknas")


def _placement_overlay(size: tuple[int, int], project: Project, wall_id: str) -> Image.Image:
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    width, height = size
    relevant = [p for p in project.placements if p.wall_id == wall_id]
    for placement in relevant:
        catalog_item = next((c for c in CATALOG if c.sku == placement.sku), None)
        text = catalog_item.name if catalog_item else placement.sku
        x_px = int(placement.position[0] * width)
        y_px = int(placement.position[1] * height)
        box_w = max(80, int((catalog_item.width_m if catalog_item else 1) * 20))
        box_h = max(50, int((catalog_item.height_m if catalog_item else 1) * 20))
        draw.rectangle(
            [(x_px, y_px), (x_px + box_w, y_px + box_h)], fill=(255, 255, 255, 120), outline=(0, 0, 0, 200)
        )
        draw.text((x_px + 6, y_px + 6), f"{text}\n{placement.variant}\n{placement.rotation_deg}°", fill=(0, 0, 0), font=font)
    return overlay
