"""Fake Windows 11 desktop used as an overlay fallback and for screenshots."""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets as B  # noqa: E402


def make_fake_desktop():
    W, H = B.W, B.H
    img = B.vgrad((W, H), (12, 34, 74), (3, 8, 22)).convert("RGBA")

    # светящееся «дыхание» виндовс-11: крупные размытые пятна без резких дуг
    for cx, cy, r, col in (
        (380, 220, 520, (40, 120, 255, 120)),
        (860, 130, 460, (90, 195, 255, 95)),
        (1080, 470, 470, (26, 70, 190, 100)),
        (430, 640, 520, (120, 70, 210, 70)),
    ):
        B.add_glow(img, col, r, (cx, cy), 1.0)

    # тонкая лента-«цветок», сильно размытая — читается как обои, а не как фигура
    ribbon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ribbon)
    for i in range(5):
        rd.ellipse(
            (300 + i * 26, 150 + i * 22, 900 - i * 18, 640 - i * 16),
            outline=(160, 220, 255, 26),
            width=14,
        )
    ribbon = ribbon.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(ribbon)

    img = img.filter(ImageFilter.GaussianBlur(1.2))

    # иконки рабочего стола
    d = ImageDraw.Draw(img, "RGBA")
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
            outline=(130, 160, 200, 110),
            width=1,
        )
        d.rounded_rectangle((x + 14, y + 12, x + 38, y + 40), 3, fill=col + (235,))
        d.text((x + 26, y + 76), label, font=f, fill=(240, 246, 255, 235), anchor="ma")

    # панель задач
    d.rectangle((0, H - 48, W, H), fill=(10, 16, 28, 235))
    cx = W // 2
    for i in range(5):
        bx = cx - 190 + i * 76
        d.rounded_rectangle((bx, H - 42, bx + 44, H - 8), 6, fill=(34, 48, 72, 240))
        d.ellipse((bx + 12, H - 34, bx + 32, H - 14), fill=(120, 190, 255, 215))
    d.text(
        (W - 90, H - 26),
        "12:04",
        font=B.font(B.SEGOE_B, 13),
        fill=(226, 236, 250),
        anchor="mm",
    )
    d.text(
        (W - 90, H - 11),
        "08.11.2026",
        font=B.font(B.SEGOE_B, 10),
        fill=(190, 205, 225),
        anchor="mm",
    )

    B.save(img.convert("RGB"), "fake_desktop.png")


if __name__ == "__main__":
    random.seed(1)
    make_fake_desktop()
