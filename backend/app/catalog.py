from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class FurnitureVariant:
    color: str
    material: str


@dataclass
class FurnitureItem:
    sku: str
    name: str
    width_m: float
    depth_m: float
    height_m: float
    variants: List[FurnitureVariant]


CATALOG: List[FurnitureItem] = [
    FurnitureItem(
        sku="IK101",
        name="Soffa 3-sits",
        width_m=2.1,
        depth_m=0.9,
        height_m=0.85,
        variants=[
            FurnitureVariant(color="Ljusgrå", material="Textil"),
            FurnitureVariant(color="Mörkblå", material="Textil"),
        ],
    ),
    FurnitureItem(
        sku="IK205",
        name="Loungefåtölj",
        width_m=0.9,
        depth_m=0.85,
        height_m=1.05,
        variants=[
            FurnitureVariant(color="Beige", material="Textil"),
            FurnitureVariant(color="Svart", material="Läder"),
        ],
    ),
    FurnitureItem(
        sku="IK320",
        name="Matbord rund",
        width_m=1.2,
        depth_m=1.2,
        height_m=0.74,
        variants=[
            FurnitureVariant(color="Ek", material="Trä"),
            FurnitureVariant(color="Valnöt", material="Trä"),
        ],
    ),
    FurnitureItem(
        sku="IK450",
        name="Sideboard",
        width_m=1.8,
        depth_m=0.45,
        height_m=0.8,
        variants=[
            FurnitureVariant(color="Vit", material="Laminerad"),
            FurnitureVariant(color="Grå", material="Laminerad"),
        ],
    ),
    FurnitureItem(
        sku="IK560",
        name="Golvlampa",
        width_m=0.45,
        depth_m=0.45,
        height_m=1.6,
        variants=[
            FurnitureVariant(color="Mässing", material="Metall"),
            FurnitureVariant(color="Svart", material="Metall"),
        ],
    ),
]
