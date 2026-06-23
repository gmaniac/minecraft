"""Texture painting helpers (box-UV nets) built on Pillow.

Paints the standard Minecraft box-UV net for a cube so generated models get
plausible region colouring without a live Blockbench preview. Colours are tweakable
in Blockbench afterward.
"""
from __future__ import annotations
from PIL import Image


class Tex:
    def __init__(self, w: int = 128, h: int = 128):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.px = self.img.load()

    def rect(self, x, y, w, h, color):
        x, y, w, h = int(x), int(y), int(w), int(h)
        for j in range(y, min(y + h, self.h)):
            for i in range(x, min(x + w, self.w)):
                if 0 <= i < self.w and 0 <= j < self.h:
                    self.px[i, j] = color

    def box(self, u, v, sx, sy, sz, base, top=None, side=None, belly=None):
        """Paint a cube's box-UV net at (u,v) for integer dimensions sx,sy,sz.

        Net layout (Minecraft standard):
          top    : (u+sz,        v)        sx x sz
          bottom : (u+sz+sx,     v)        sx x sz
          east   : (u,           v+sz)     sz x sy
          north  : (u+sz,        v+sz)     sx x sy
          west   : (u+sz+sx,     v+sz)     sz x sy
          south  : (u+sz+sx+sz,  v+sz)     sx x sy
        """
        sx, sy, sz = int(round(sx)), int(round(sy)), int(round(sz))
        top = top or base
        side = side or base
        belly = belly or base
        self.rect(u + sz, v, sx, sz, top)              # top
        self.rect(u + sz + sx, v, sx, sz, belly)       # bottom
        self.rect(u, v + sz, sz, sy, side)             # east
        self.rect(u + sz, v + sz, sx, sy, base)        # north (front)
        self.rect(u + sz + sx, v + sz, sz, sy, side)   # west
        self.rect(u + sz + sx + sz, v + sz, sx, sy, base)  # south (back)

    def save(self, path: str):
        self.img.save(path)


def shade(color, factor):
    """Lighten (factor>1) or darken (factor<1) an RGBA color."""
    r, g, b, a = color
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor))),
        a,
    )


def hex_rgba(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)
