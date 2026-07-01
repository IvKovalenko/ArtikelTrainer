#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Генерация PNG-иконок PWA из того же дизайна, что icon.svg.
Запуск:  python tools/gen_icons.py   (нужен Pillow)"""
import os
from PIL import Image, ImageDraw, ImageFont

BG = (43, 43, 43, 255)      # #2b2b2b
WHITE = (255, 255, 255, 255)
GREEN = (47, 158, 68, 255)  # #2f9e44
SS = 4                      # суперсэмплинг для сглаживания

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "public", "icons")

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(px):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


def render(size, maskable=False):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if maskable:
        d.rectangle([0, 0, s, s], fill=BG)          # полный квадрат — маску наложит ОС
        scale = 0.80                                 # контент в безопасной зоне
    else:
        r = int(0.219 * s)
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=BG)
        scale = 1.0

    font = load_font(int(0.60 * s * scale))
    cx, cy = s / 2, s * (0.46 if not maskable else 0.44)
    d.text((cx, cy), "d", font=font, fill=WHITE, anchor="mm")

    bw, bh = 0.312 * s * scale, 0.039 * s * scale
    by = s * (0.72 if not maskable else 0.68)
    d.rounded_rectangle([cx - bw / 2, by, cx + bw / 2, by + bh],
                        radius=bh / 2, fill=GREEN)

    return img.resize((size, size), Image.LANCZOS)


def save(img, name):
    path = os.path.join(ICONS, name)
    img.save(path)
    print("written", path)


def main():
    os.makedirs(ICONS, exist_ok=True)
    save(render(192), "icon-192.png")
    save(render(512), "icon-512.png")
    save(render(512, maskable=True), "icon-maskable-512.png")
    save(render(180), "apple-touch-icon.png")


if __name__ == "__main__":
    main()
