"""Fake Windows 11 desktop used as an overlay fallback and for screenshots."""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets as B  # noqa: E402


def make_fake_desktop():
    W, H = B.W, B.H
    img = B.vgrad((W, H), (18, 52, 110), (6, 16, 42)).convert("RGBA")
    for cx, cy, r, col in (
        (300, 260, 420, (30, 90, 220, 90)),
        (760, 180, 360, (70, 170, 255, 70)),
        (1050, 420, 420, (20, 60, 160, 80)),
        (520, 620, 380, (120, 60, 200, 55)),
    ):
        B.add_glow(img, col, r, (cx, cy), 1.0)
    # abstract "bloom" ribbons
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(7):
        d.arc(
            (250 + i * 18, 90 + i * 12, 1030 - i * 14, 700 - i * 10),
            200,
            340,
            fill=(120, 200, 255, 26),
            width=26,
        )
    img = img.filter(ImageFilter.GaussianBlur(0.6))

    # desktop icons
    f = B.font(B.SEGOE_B, 13)
    icons = [
        ("Этот компьютер", (255, 230, 140)),
        ("Корзина", (200, 220, 240)),
        ("Chrome", (120, 220, 170)),
        ("Word", (110, 170, 250)),
        ("Тест_ОЗУ.docx", (250, 250, 250)),
        ("Altman.mp4", (255, 150, 150)),
        ("Проект", (255, 210, 120)),
    ]
    for i, (label, col) in enumerate(icons):
        x, y = 24, 22 + i * 92
        d.rounded_rectangle(
            (x, y, x + 52, y + 52),
            10,
            fill=(22, 34, 58, 220),
            outline=(130, 160, 200, 120),
            width=1,
        )
        d.rounded_rectangle((x + 14, y + 12, x + 38, y + 40), 3, fill=col + (235,))
        d.text((x + 26, y + 76), label, font=f, fill=(240, 246, 255, 235), anchor="ma")

    # taskbar
    d.rectangle((0, H - 48, W, H), fill=(12, 18, 30, 235))
    cx = W // 2
    for i in range(5):
        bx = cx - 190 + i * 76
        d.rounded_rectangle((bx, H - 42, bx + 44, H - 8), 6, fill=(38, 52, 76, 240))
        d.ellipse((bx + 12, H - 34, bx + 32, H - 14), fill=(120, 190, 255, 220))
    d.text(
        (W - 90, H - 24),
        "12:04",
        font=B.font(B.SEGOE_B, 13),
        fill=(226, 236, 250),
        anchor="mm",
    )
    d.text(
        (W - 90, H - 10),
        "08.11.2026",
        font=B.font(B.SEGOE_B, 10),
        fill=(190, 205, 225),
        anchor="mm",
    )
    B.save(img.convert("RGB"), "fake_desktop.png")


if __name__ == "__main__":
    random.seed(1)
    make_fake_desktop()
