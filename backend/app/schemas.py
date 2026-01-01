from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class WallCalibration(BaseModel):
    left_corner: List[float]
    right_corner: List[float]
    floor_line_y: float


class WallImage(BaseModel):
    wall_id: str
    filename: str


class RoomScale(BaseModel):
    reference_wall: str
    reference_length_m: float


class FurniturePlacement(BaseModel):
    sku: str
    variant: str
    wall_id: str
    position: List[float]
    rotation_deg: float


class RenderRequest(BaseModel):
    project_id: UUID
    walls: Optional[List[str]] = None


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    walls: Dict[str, WallImage] = Field(default_factory=dict)
    calibrations: Dict[str, WallCalibration] = Field(default_factory=dict)
    scale: Optional[RoomScale] = None
    placements: List[FurniturePlacement] = Field(default_factory=list)


class CreateProjectRequest(BaseModel):
    name: str


class UploadWallResponse(BaseModel):
    wall_id: str
    stored_filename: str


class RenderedWall(BaseModel):
    wall_id: str
    image_path: str


class RenderResponse(BaseModel):
    project_id: UUID
    rendered: List[RenderedWall]
