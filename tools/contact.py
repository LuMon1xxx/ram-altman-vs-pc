import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
A = os.path.join("ram_altman_game", "assets")

sheet = Image.new("RGB", (1280, 900), (24, 26, 30))
items = [
    ("arena_bg.png", (0, 0, 640, 360)),
    ("thanks_wall.png", (640, 0, 640, 360)),
    ("keynote_bg.png", (0, 360, 640, 360)),
    ("victory_bg.png", (640, 360, 640, 360)),
]
for name, box in items:
    im = (
        Image.open(os.path.join(A, name))
        .convert("RGB")
        .resize((box[2], box[3]), Image.LANCZOS)
    )
    sheet.paste(im, (box[0], box[1]))

# sprites row
x = 20
for name, h in [
    ("pc.png", 240),
    ("sam.png", 240),
    ("ram.png", 140),
    ("server_rack.png", 260),
    ("chrome_win.png", 130),
    ("coin20.png", 90),
    ("sam_avatar.png", 150),
]:
    im = Image.open(os.path.join(A, name)).convert("RGBA")
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    sheet.paste(im, (x, 740 - h // 2), im)
    x += im.width + 20

sheet.save(os.path.join("ram_altman_game", "tools", "contact.jpg"), quality=88)
print("ok", x)
