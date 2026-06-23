#!/usr/bin/env python3
"""Generate MotorCraft pack icons (BP + RP), 128x128."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_icon(path, accent):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # gradient background
    for y in range(128):
        t = y / 127
        c = (int(24 + 18 * t), int(26 + 22 * t), int(38 + 30 * t), 255)
        d.line([(0, y), (128, y)], fill=c)
    # accent diamond (a stylised dragon scale / hex)
    cx, cy = 64, 60
    d.polygon([(cx, cy - 34), (cx + 34, cy), (cx, cy + 34), (cx - 34, cy)],
              fill=accent, outline=(255, 255, 255, 200))
    d.polygon([(cx, cy - 18), (cx + 18, cy), (cx, cy + 18), (cx - 18, cy)],
              fill=(255, 255, 255, 40))
    # "MC" monogram bar
    d.rectangle([20, 100, 108, 116], fill=(0, 0, 0, 150))
    d.text((44, 102), "MOTOR", fill=(255, 255, 255, 255))
    img.save(path)
    print("wrote", path)


if __name__ == "__main__":
    make_icon(os.path.join(ROOT, "MotorCraft_BP", "pack_icon.png"), (210, 90, 50, 255))
    make_icon(os.path.join(ROOT, "MotorCraft_RP", "pack_icon.png"), (70, 130, 210, 255))
