#!/usr/bin/env python3
"""Offline isometric preview of the dragon models (no Minecraft needed).

Composes each bone's rotation/pivot chain, projects cubes orthographically with a
painter's-algorithm fill, shades faces by a light direction, and tiles all 21
dragons into one montage so silhouettes/proportions can be eyeballed pre-merge.
"""
import math
import os
from PIL import Image, ImageDraw
from dragons_data import DRAGONS
from mclib.dragonbuild import build, _col

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL = 300
YAW, PITCH = math.radians(28), math.radians(18)
LIGHT = (-0.4, 0.8, -0.45)


def rot_euler(v, deg):
    x, y, z = v
    rx, ry, rz = (math.radians(a) for a in deg)
    # Rx
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    # Ry
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    # Rz
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return [x, y, z]


def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def bone_chain(geo):
    by = {b.name: b for b in geo.bones}
    chain = {}
    for b in geo.bones:
        c, cur = [], b
        while cur is not None:
            chain.setdefault(b.name, []).append(cur)
            cur = by.get(cur.parent) if cur.parent else None
    return chain


def world_point(p, bone, chain):
    for bn in chain[bone.name]:
        if bone.rotation and bn is bone:
            p = add(rot_euler(sub(p, bn.pivot), bone.rotation), bn.pivot)
        if bn.rotation and bn is not bone:
            p = add(rot_euler(sub(p, bn.pivot), bn.rotation), bn.pivot)
    return p


def project(p):
    x, y, z = p
    x, z = x * math.cos(YAW) + z * math.sin(YAW), -x * math.sin(YAW) + z * math.cos(YAW)
    y, z = y * math.cos(PITCH) - z * math.sin(PITCH), y * math.sin(PITCH) + z * math.cos(PITCH)
    return (x, -y, z)


FACES = [((0, 1, 2, 3), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)),
         ((0, 1, 5, 4), (0, -1, 0)), ((3, 2, 6, 7), (0, 1, 0)),
         ((1, 2, 6, 5), (1, 0, 0)), ((0, 3, 7, 4), (-1, 0, 0))]


def render(d):
    geo = build(d)
    chain = bone_chain(geo)
    quads = []
    for b in geo.bones:
        for c in b.cubes:
            ox, oy, oz = c.origin
            sx, sy, sz = c.size
            corners = [[ox, oy, oz], [ox + sx, oy, oz], [ox + sx, oy + sy, oz], [ox, oy + sy, oz],
                       [ox, oy, oz + sz], [ox + sx, oy, oz + sz], [ox + sx, oy + sy, oz + sz],
                       [ox, oy + sy, oz + sz]]
            wc = [project(world_point(p, b, chain)) for p in corners]
            base = _col(d["palette"], c.region or "body")
            for idx, n in FACES:
                pts = [wc[i] for i in idx]
                depth = sum(p[2] for p in pts) / 4
                nz = rot_euler(list(n), b.rotation) if b.rotation else list(n)
                sh = 0.55 + 0.45 * max(0, (nz[0] * LIGHT[0] + nz[1] * LIGHT[1] + nz[2] * LIGHT[2]))
                col = tuple(max(0, min(255, int(ch * sh))) for ch in base[:3]) + (base[3],)
                quads.append((depth, [(p[0], p[1]) for p in pts], col))
    quads.sort(key=lambda q: q[0])
    # fit to cell
    xs = [pt[0] for _, q, _ in quads for pt in q]
    ys = [pt[1] for _, q, _ in quads for pt in q]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    scale = (CELL - 30) / max(maxx - minx, maxy - miny)
    img = Image.new("RGBA", (CELL, CELL), (32, 34, 44, 255))
    dr = ImageDraw.Draw(img)
    cx = (CELL - (minx + maxx) * scale) / 2
    cy = (CELL - (miny + maxy) * scale) / 2
    for _, q, col in quads:
        dr.polygon([(p[0] * scale + cx, p[1] * scale + cy) for p in q],
                   fill=col, outline=(0, 0, 0, 60))
    dr.text((8, 8), d["name"], fill=(255, 255, 255, 255))
    return img


def main():
    cols = 5
    rows = (len(DRAGONS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * CELL, rows * CELL), (20, 21, 28, 255))
    for n, d in enumerate(DRAGONS):
        sheet.paste(render(d), ((n % cols) * CELL, (n // cols) * CELL))
    out = os.path.join(ROOT, "dragons_preview.png")
    sheet.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
