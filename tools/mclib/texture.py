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

    # ---- detailed face painting (shading + edges + surface patterns) ----
    def _put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = color

    def box_detailed(self, u, v, sx, sy, sz, base, region="body", style="plain"):
        sx, sy, sz = int(round(sx)), int(round(sy)), int(round(sz))
        # x, y, w, h, shade factor
        faces = [
            (u + sz, v, sx, sz, 1.14),                 # top
            (u + sz + sx, v, sx, sz, 0.74),            # bottom
            (u, v + sz, sz, sy, 0.88),                 # east
            (u + sz, v + sz, sx, sy, 1.0),             # north (front)
            (u + sz + sx, v + sz, sz, sy, 0.94),       # west
            (u + sz + sx + sz, v + sz, sx, sy, 0.9),   # south (back)
        ]
        for (x, y, w, h, f) in faces:
            self._face(x, y, w, h, shade(base, f), region, style)

    def _face(self, x, y, w, h, color, region, style):
        if w <= 0 or h <= 0:
            return
        for j in range(h):
            for i in range(w):
                n = (((x + i) * 73 + (y + j) * 151) % 7) - 3
                self._put(x + i, y + j, _shift(color, n))
        _PATTERN(self, x, y, w, h, color, region, style)
        dk = shade(color, 0.68)                          # edge shadow for definition
        for i in range(w):
            self._put(x + i, y, dk); self._put(x + i, y + h - 1, dk)
        for j in range(h):
            self._put(x, y + j, dk); self._put(x + w - 1, y + j, dk)

    def save(self, path: str):
        self.img.save(path)


def _shift(c, n):
    return (max(0, min(255, c[0] + n)), max(0, min(255, c[1] + n)),
            max(0, min(255, c[2] + n)), c[3])


def _scales(t, x, y, w, h, c):
    dk, lt = shade(c, 0.7), shade(c, 1.14)
    for j in range(0, h, 3):
        off = 2 if (j // 3) % 2 else 0
        for i in range(off, w, 4):
            t._put(x + i, y + j, dk)            # scale lower edge (shadow)
            t._put(x + i + 1, y + j, dk)
            t._put(x + i + 2, y + j, dk)
            if j > 0:
                t._put(x + i + 1, y + j - 1, lt)  # scale highlight


def _fur(t, x, y, w, h, c):
    dk, lt = shade(c, 0.85), shade(c, 1.12)
    for i in range(0, w, 2):
        col = dk if (i // 2) % 2 else lt
        for j in range(h):
            if (i + j) % 3:
                t._put(x + i, y + j, col)


def _panel(t, x, y, w, h, c):
    dk, lt = shade(c, 0.78), shade(c, 1.15)
    for i in range(w):
        t._put(x + i, y + 1, lt)            # highlight line
        if h > 4:
            t._put(x + i, y + h // 2, dk)   # panel seam
    for (rx, ry) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        t._put(x + rx, y + ry, dk)          # rivets


def _brushed(t, x, y, w, h, c):
    for j in range(0, h, 2):
        f = 1.1 if (j // 2) % 2 else 0.9
        for i in range(w):
            t._put(x + i, y + j, shade(c, f))


def _veins(t, x, y, w, h, c):
    lt = shade(c, 1.2)
    for k in range(1, max(2, w), 4):
        for j in range(h):
            t._put(x + min(w - 1, k + j // 2), y + j, lt)


def _grain(t, x, y, w, h, c):
    dk = shade(c, 0.82)
    for j in range(1, h, 3):
        for i in range(w):
            if (i + j) % 5:
                t._put(x + i, y + j, dk)


def _cloth(t, x, y, w, h, c):
    dk = shade(c, 0.88)
    for j in range(0, h, 2):
        for i in range(w):
            t._put(x + i, y + j, dk)
    for i in range(0, w, 2):
        for j in range(h):
            if (i + j) % 2:
                t._put(x + i, y + j, dk)


def _glass(t, x, y, w, h, c):
    lt = shade(c, 1.6)
    for k in range(min(w, h)):
        t._put(x + 1 + k, y + 1 + k, lt)


def _PATTERN(t, x, y, w, h, c, region, style):
    if region in ("glass", "fglass"):
        return _glass(t, x, y, w, h, c)
    if region == "eye":
        return t._put(x + w // 2, y + h // 2, shade(c, 1.5))
    if region in ("metal", "trim", "fmetal", "ftrim", "wingbone"):
        return _brushed(t, x, y, w, h, c)
    if region == "membrane":
        return _veins(t, x, y, w, h, c)
    if region in ("wood", "fwood", "fleg", "ftop"):
        return _grain(t, x, y, w, h, c)
    if region in ("ffabric", "fabric"):
        return _cloth(t, x, y, w, h, c)
    if region in ("body", "head", "tail", "leg", "belly", "neck", "ear"):
        if style == "scales":
            return _scales(t, x, y, w, h, c)
        if style == "fur":
            return _fur(t, x, y, w, h, c)
        if style == "panel":
            return _panel(t, x, y, w, h, c)


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
