"""Bedrock geometry (.geo.json) builder.

A small, dependency-free helper for procedurally generating entity/block models in
the Bedrock 1.21 geometry format. Used by every domain's model generator so we never
hand-author thousands of cubes.

Conventions:
- Box UV (per-cube [u, v]) — simplest to pair with the texture generator.
- Right-handed Minecraft space: +x east, +y up, +z south. Pivots are world-space.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Cube:
    origin: list          # [x, y, z] of the min corner
    size: list            # [sx, sy, sz]
    uv: list              # [u, v] box-uv top-left
    inflate: float = 0.0
    pivot: Optional[list] = None
    rotation: Optional[list] = None
    mirror: bool = False
    region: Optional[str] = None  # paint hint, not serialized

    def to_dict(self) -> dict:
        d = {"origin": [r(v) for v in self.origin],
             "size": [r(v) for v in self.size],
             "uv": [int(self.uv[0]), int(self.uv[1])]}
        if self.inflate:
            d["inflate"] = r(self.inflate)
        if self.pivot is not None:
            d["pivot"] = [r(v) for v in self.pivot]
        if self.rotation is not None:
            d["rotation"] = [r(v) for v in self.rotation]
        if self.mirror:
            d["mirror"] = True
        return d


@dataclass
class Bone:
    name: str
    pivot: list = field(default_factory=lambda: [0, 0, 0])
    parent: Optional[str] = None
    rotation: Optional[list] = None
    cubes: list = field(default_factory=list)
    binding: Optional[str] = None

    def cube(self, origin, size, uv, **kw) -> "Bone":
        self.cubes.append(Cube(origin, size, uv, **kw))
        return self

    def to_dict(self) -> dict:
        d = {"name": self.name, "pivot": [r(v) for v in self.pivot]}
        if self.parent:
            d["parent"] = self.parent
        if self.rotation is not None:
            d["rotation"] = [r(v) for v in self.rotation]
        if self.binding is not None:
            d["binding"] = self.binding
        d["cubes"] = [c.to_dict() for c in self.cubes]
        return d


class Geometry:
    def __init__(self, identifier: str, tex_w: int = 128, tex_h: int = 128):
        self.identifier = identifier
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bones: list[Bone] = []
        self.bounds = [10, 10, 10]
        self.bounds_offset = [0, 4, 0]

    def bone(self, name, pivot=(0, 0, 0), parent=None, rotation=None, binding=None) -> Bone:
        b = Bone(name, list(pivot), parent, list(rotation) if rotation else None,
                 binding=binding)
        self.bones.append(b)
        return b

    def all_cubes(self):
        for b in self.bones:
            for c in b.cubes:
                yield c

    def set_bounds(self, w, h, offset):
        self.bounds = [w, w, h] if isinstance(w, (int, float)) else list(w)
        self.bounds = [w, h, w] if isinstance(w, (int, float)) else self.bounds
        self.bounds_offset = list(offset)

    def to_dict(self) -> dict:
        return {
            "format_version": "1.21.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": self.identifier,
                    "texture_width": self.tex_w,
                    "texture_height": self.tex_h,
                    "visible_bounds_width": self.bounds[0],
                    "visible_bounds_height": self.bounds[1],
                    "visible_bounds_offset": [r(v) for v in self.bounds_offset],
                },
                "bones": [b.to_dict() for b in self.bones],
            }],
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def r(v):
    """Round to 4 decimals, collapsing -0.0 and whole floats to ints."""
    f = round(float(v), 4)
    return int(f) if f == int(f) else f
