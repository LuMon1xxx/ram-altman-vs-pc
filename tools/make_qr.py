"""Генерирует настоящий QR-код для синего экрана смерти."""

import os
import sys

import qrcode
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "bsod_qr.png")

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=5,
    border=2,
)
qr.add_data("https://www.windows.com/stopcode")
qr.make(fit=True)
img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255)).convert("RGB")
print("modules:", qr.modules_count, "size:", img.size)
img.save(OUT)
print("saved", OUT)
