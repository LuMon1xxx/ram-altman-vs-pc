#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Asset factory for "RAM Altman vs PC".

Real cutouts (Sam / PC case / RAM stick / logo) come from the user's
"фото и видео" folder; everything else is drawn procedurally with PIL and
every sound effect / music loop is synthesized with numpy.  No network needed.
"""

import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
def find_source_media():
    """Source cutouts live in ./source_media (fallback: the original folder)."""
    for cand in (os.path.join(ROOT, "source_media"),
                 os.path.join(os.path.dirname(ROOT), "фото и видео")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(ROOT, "source_media")


SRC = find_source_media()

# current name -> legacy name in the user's original folder
SOURCE_ALIASES = {
    "sam_cutout.png": "sam-removebg-preview.png",
    "pc_case.png": "pc.png",
    "ram_stick.png": "ram.png",
    "chatgpt_logo.png": "ChatGPT-Logo.png",
}
W, H = 1280, 720

FONT_DIR = "C:/Windows/Fonts"
IMPACT = os.path.join(FONT_DIR, "impact.ttf")
SEGOE_B = os.path.join(FONT_DIR, "segoeuib.ttf")
ARIAL_B = os.path.join(FONT_DIR, "arialbd.ttf")
CONSOLA_B = os.path.join(FONT_DIR, "consolab.ttf")

random.seed(7)
np.random.seed(7)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def lerp(a, b, t):
    return a + (b - a) * t


def vgrad(size, top, bottom):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    top = np.array(top, dtype=np.float32)
    bottom = np.array(bottom, dtype=np.float32)
    arr = (top * (1 - t) + bottom * t) * np.ones((1, w, 1), dtype=np.float32)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def radial_glow(size, color, radius, center=None, strength=1.0):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = center if center else (w / 2, h / 2)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(radius, 1)
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    layer = np.zeros((h, w, 4), dtype=np.uint8)
    layer[..., 0] = color[0]
    layer[..., 1] = color[1]
    layer[..., 2] = color[2]
    al = a * (color[3] if len(color) > 3 else 255)
    layer[..., 3] = np.clip(al, 0, 255).astype(np.uint8)
    return Image.fromarray(layer, "RGBA")


def add_glow(img, color, radius, center=None, strength=1.0):
    glow = radial_glow(img.size, color, radius, center, strength)
    out = Image.alpha_composite(img.convert("RGBA"), glow)
    img.paste(out.convert(img.mode), (0, 0))
    return img


def noise_overlay(img, amount=10, mono=True):
    arr = np.array(img.convert("RGB")).astype(np.int16)
    n = np.random.normal(0, amount, arr.shape[:2])
    n = n[..., None] if mono else np.random.normal(0, amount, arr.shape)
    arr = np.clip(arr + n, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def scanlines(img, step=3, alpha=26):
    w, h = img.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def vignette(img, power=2.0, alpha=90):
    w, h = img.size
    v = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(v)
    for y in range(0, h, 2):
        a = int(alpha * (abs(y - h / 2) / (h / 2)) ** power)
        d.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), v).convert("RGB")


def save(img, name, mode=None):
    path = os.path.join(ASSETS, name)
    if mode:
        img = img.convert(mode)
    img.save(path)
    print("  [img]", name, img.size)


def load_rgba(name):
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        alt = SOURCE_ALIASES.get(name)
        p = os.path.join(SRC, alt) if alt else p
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    im = Image.open(p).convert("RGBA")
    return im.crop(im.getbbox())


# --------------------------------------------------------------------------
# real cutouts -> game sprites (rim light + glow)
# --------------------------------------------------------------------------
def trim_band(im, keep_frac=0.72, fade=40):
    """Cut the leftover photo background band and melt the new bottom edge."""
    w, h = im.size
    cut = int(h * keep_frac)
    out = im.crop((0, 0, w, cut))
    if fade:
        out = fade_bottom(out, 1 - fade / float(out.height))
    return out


def prep_cutout(
    src_name, target_h, rim=(120, 225, 255), glow_alpha=150, glow_radius=14
):
    im = load_rgba(src_name)
    w = max(1, round(im.width * target_h / im.height))
    im = im.resize((w, target_h), Image.LANCZOS)
    # kill the soft leftover background / dark halo from the auto-cutout
    a = im.split()[3].point(lambda v: 0 if v < 110 else 255)
    a = a.filter(ImageFilter.GaussianBlur(0.9))
    a = a.point(lambda v: 255 if v > 205 else (0 if v < 55 else v))
    im.putalpha(a)
    pad = 44
    size = (w + pad * 2, target_h + pad * 2)

    def color_mask(mask, color):
        layer = Image.new("RGBA", size, color + (0,))
        full = Image.new("L", size, 0)
        full.paste(mask, (pad, pad))
        layer.putalpha(full)
        return layer

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    # soft aura
    aura = a.filter(ImageFilter.GaussianBlur(glow_radius))
    aura = aura.point(lambda v: int(v * glow_alpha / 255))
    out = Image.alpha_composite(out, color_mask(aura, rim))
    # hard rim
    rim_mask = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(7)), a)
    out = Image.alpha_composite(out, color_mask(rim_mask, rim))
    out.alpha_composite(im, (pad, pad))
    return out


def make_sprites():
    pc = prep_cutout("pc_case.png", 300, rim=(90, 210, 255), glow_alpha=120, glow_radius=12)
    save(pc, "pc.png")
    sam_full = prep_cutout(
        "sam_cutout.png",
        330,
        rim=(80, 255, 175),
        glow_alpha=110,
        glow_radius=12,
    )
    # fight sprite keeps the body, only the last strip of leftover photo bg is cut
    fight = trim_band(sam_full, 0.92, 46)
    save(fight, "sam_fight.png")
    # poster / avatar use the head-and-shoulders crop
    sam = trim_band(sam_full.copy(), 0.725, 40)
    save(sam, "sam.png")
    ram = load_rgba("ram_stick.png")
    ram = ram.resize((260, round(ram.height * 260 / ram.width)), Image.LANCZOS)
    save(ram, "ram.png")
    # white + green versions of the OpenAI mark
    logo = load_rgba("chatgpt_logo.png")
    logo = logo.resize((512, 512), Image.LANCZOS)
    alpha = logo.split()[3]
    for name, col in (
        ("logo_white.png", (245, 250, 255)),
        ("logo_green.png", (80, 255, 175)),
    ):
        lay = Image.new("RGBA", logo.size, col + (0,))
        lay.putalpha(alpha)
        save(lay, name)
    return sam


def head_from_cutout(sam):
    """Square head crop used for the HUD portrait."""
    w, h = sam.size
    side = int(h * 0.52)
    head = sam.crop((w // 2 - side // 2, 0, w // 2 + side // 2, side))
    head = head.resize((300, 300), Image.LANCZOS)
    return head


def make_avatar(sam):
    head = head_from_cutout(sam)
    bg = Image.new("RGBA", (340, 340), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    d.ellipse((0, 0, 339, 339), fill=(14, 40, 32, 255))
    add_glow(bg, (60, 255, 160, 230), 200, (170, 170), 0.5)
    bg.alpha_composite(head, (20, 26))
    mask = Image.new("L", (1360, 1360), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 1359, 1359), fill=255)
    mask = mask.resize((340, 340), Image.LANCZOS)
    out = Image.new("RGBA", (340, 340), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.ellipse((3, 3, 336, 336), outline=(70, 240, 160, 255), width=8)
    save(out, "sam_avatar.png")


# --------------------------------------------------------------------------
# backgrounds
# --------------------------------------------------------------------------
def make_arena():
    img = vgrad((W, H), (9, 10, 18), (26, 30, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    add_glow(img, (120, 190, 210, 255), 340, (980, 130), 0.55)
    d.ellipse((925, 75, 1035, 185), fill=(196, 220, 226, 220))
    d.ellipse((945, 88, 1030, 175), fill=(215, 234, 238, 255))

    rng = random.Random(3)
    for i in range(26):
        bw = rng.randint(26, 60)
        bx = rng.randint(-20, W)
        bh = rng.randint(60, 250)
        d.rectangle((bx, 430 - bh, bx + bw, 470), fill=(14, 18, 24, 255))
        for y in range(430 - bh + 8, 460, 12):
            if rng.random() < 0.55:
                d.rectangle(
                    (bx + 6, y, bx + bw - 6, y + 2),
                    fill=(40, 220, 150, rng.randint(40, 120)),
                )

    for px in (52, 1130):
        d.rectangle((px, 60, px + 98, 620), fill=(23, 24, 30, 255))
        d.rectangle((px - 12, 44, px + 110, 78), fill=(30, 31, 38, 255))
        d.rectangle((px - 12, 578, px + 110, 620), fill=(30, 31, 38, 255))
        for y in range(90, 570, 46):
            d.line((px + 4, y, px + 94, y), fill=(16, 17, 22, 255), width=3)
        for gx in range(px + 10, px + 96, 22):
            d.line((gx, 80, gx, 578), fill=(18, 19, 25, 255), width=2)

    rng = random.Random(11)
    for x in range(-20, W + 40, 34):
        hh = rng.randint(46, 74)
        y = 428 + rng.randint(-4, 8)
        col = (12, 13, 18, 255)
        d.ellipse((x, y - hh, x + 30, y - hh + 34), fill=col)
        d.rounded_rectangle((x - 4, y - hh + 26, x + 34, y + 30), 12, fill=col)
        if rng.random() < 0.12:
            d.ellipse(
                (x + 8, y - hh + 10, x + 14, y - hh + 16), fill=(220, 60, 60, 120)
            )

    for rx in (300, 372, 470):
        d.rectangle(
            (rx, 250, rx + 58, 440), fill=(17, 22, 26, 255), outline=(36, 46, 50, 255)
        )
        for y in range(262, 430, 16):
            d.rectangle((rx + 8, y, rx + 50, y + 5), fill=(30, 200, 130, 70))

    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor)
    fd.polygon([(0, 470), (W, 470), (W, H), (0, H)], fill=(21, 22, 27, 255))
    fd.polygon([(0, 470), (W, 470), (W, 500), (0, 500)], fill=(31, 33, 40, 255))
    for i in range(-8, 26):
        x0 = i * 90
        fd.line(
            [(640 + (x0 - 640) * 0.55, 500), (640 + (x0 - 640) * 2.6, H)],
            fill=(34, 36, 43, 255),
            width=2,
        )
    for y in (520, 556, 600, 654):
        fd.line([(0, y), (W, y)], fill=(34, 36, 43, 255), width=2)
    img.alpha_composite(floor)

    add_glow(img, (90, 200, 190, 255), 460, (640, 620), 0.20)
    add_glow(img, (255, 170, 60, 255), 230, (52, 300), 0.55)
    add_glow(img, (255, 170, 60, 255), 230, (1200, 300), 0.55)

    for tx in (98, 1178):
        d.rectangle((tx - 7, 300, tx + 7, 400), fill=(40, 32, 26, 255))
        d.polygon([(tx, 258), (tx - 16, 312), (tx + 16, 312)], fill=(255, 190, 70, 235))
        d.polygon([(tx, 274), (tx - 8, 308), (tx + 8, 308)], fill=(255, 245, 190, 245))

    img = noise_overlay(img.convert("RGB"), 5)
    img = scanlines(img, 4, 18)
    save(vignette(img, 2.0, 110), "arena_bg.png", "RGB")


def make_keynote_bg():
    img = vgrad((W, H), (5, 9, 15), (10, 20, 27)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((150, 70, 1130, 640), 20, fill=(15, 26, 35, 255))
    add_glow(img, (90, 200, 230, 255), 560, (640, 340), 0.30)
    d.rounded_rectangle((172, 92, 1108, 618), 14, fill=(23, 44, 56, 255))
    add_glow(img, (150, 235, 250, 255), 330, (640, 300), 0.30)
    rng = random.Random(5)
    for _ in range(40):
        x, y = rng.randint(0, W), rng.randint(0, H)
        r = rng.randint(6, 46)
        add_glow(img, (110, 210, 240, rng.randint(20, 70)), r * 2, (x, y), 0.6)
    d.polygon([(0, 640), (W, 640), (W, H), (0, H)], fill=(7, 11, 15, 255))
    add_glow(img, (80, 190, 220, 255), 300, (640, 690), 0.16)
    save(scanlines(img.convert("RGB"), 4, 14), "keynote_bg.png")


def make_victory_bg():
    img = vgrad((W, H), (6, 15, 21), (2, 6, 10)).convert("RGBA")
    add_glow(img, (255, 195, 85, 255), 640, (640, 520), 0.34)
    add_glow(img, (60, 220, 190, 255), 380, (250, 120), 0.14)
    shafts = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shafts)
    for i in range(14):
        a0 = -math.pi / 2 + (i - 6.5) * 0.13
        x2 = 640 + math.cos(a0) * 1800
        y2 = 560 + math.sin(a0) * 1800
        sd.polygon([(640, 560), (x2 - 46, y2), (x2 + 46, y2)], fill=(255, 214, 130, 17))
    shafts = shafts.filter(ImageFilter.GaussianBlur(9))
    img.alpha_composite(shafts)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 596, W, 600), fill=(255, 210, 120, 55))
    add_glow(img, (255, 210, 120, 255), 300, (640, 620), 0.18)
    save(noise_overlay(vignette(img.convert("RGB"), 2.4, 120), 4), "victory_bg.png")


def fade_bottom(im, start_frac=0.68):
    """Soft alpha gradient on the lower part, so a cropped photo melts away."""
    w, h = im.size
    mask = Image.new("L", (1, h))
    for y in range(h):
        if y < h * start_frac:
            v = 255
        else:
            v = int(255 * max(0.0, 1 - (y - h * start_frac) / (h * (1 - start_frac)) ** 1.35))
        mask.putpixel((0, y), v)
    mask = mask.resize((w, h))
    out = im.copy()
    out.putalpha(ImageChops.multiply(im.split()[3], mask))
    return out


def make_thanks_wall(sam):
    """Full-bleed "thank you" poster: copy on the left, Sam on the right."""
    img = vgrad((W, H), (3, 9, 7), (1, 4, 3)).convert("RGBA")

    # soft light behind Sam (no hard edges anywhere)
    add_glow(img, (26, 190, 132, 255), 620, (980, 360), 0.55)
    add_glow(img, (60, 255, 175, 255), 320, (960, 300), 0.35)

    s = sam.crop(sam.getbbox())
    target_h = 470
    s = s.resize((round(s.width * target_h / s.height), target_h), Image.LANCZOS)
    sx = 1262 - s.width
    sy = 706 - s.height
    img.alpha_composite(s, (sx, sy))

    d = ImageDraw.Draw(img, "RGBA")

    # left column
    logo = load_rgba("chatgpt_logo.png").resize((88, 88), Image.LANCZOS)
    dark = Image.new("RGBA", logo.size, (22, 60, 46, 0))
    dark.putalpha(logo.split()[3].point(lambda v: int(v * 0.55)))
    img.alpha_composite(dark, (74, 62))

    d.text((80, 176), "СПАСИБО", font=font(IMPACT, 112), fill=(110, 245, 178, 255))
    d.text((80, 268), "ЗА ВКЛАД!", font=font(IMPACT, 112), fill=(110, 245, 178, 255))
    d.text((82, 412), "Ваш ПК стал на 1 ГБ", font=font(SEGOE_B, 34),
           fill=(214, 236, 227, 255))
    d.text((82, 458), "медленнее. AGI уже близко.", font=font(SEGOE_B, 34),
           fill=(214, 236, 227, 255))
    d.text((84, 536), "— Сэм Альтман, CEO OpenAI", font=font(SEGOE_B, 24),
           fill=(96, 210, 160, 255))

    # bottom hairline (left half only) + vignette, then grain
    d.rectangle((0, 646, 620, 648), fill=(40, 120, 92, 80))
    img = noise_overlay(img.convert("RGB"), 5)
    img = scanlines(img, 4, 20)
    save(vignette(img, 2.2, 130), "thanks_wall.png", "RGB")


# --------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------
def make_rack():
    S = (300, 620)
    im = Image.new("RGBA", S, (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(
        (18, 6, 282, 600),
        12,
        fill=(28, 30, 34, 255),
        outline=(64, 70, 78, 255),
        width=4,
    )
    d.rounded_rectangle((30, 18, 270, 588), 8, fill=(18, 20, 24, 255))
    for i in range(9):
        y = 30 + i * 60
        d.rounded_rectangle(
            (40, y, 260, y + 50),
            5,
            fill=(34, 37, 43, 255),
            outline=(58, 63, 72, 255),
            width=2,
        )
        for fx in range(52, 150, 10):
            d.ellipse((fx, y + 12, fx + 9, y + 40), fill=(12, 14, 17, 255))
        for lx in range(170, 256, 14):
            col = (60, 255, 150, 255) if (i + lx) % 3 else (255, 190, 60, 255)
            d.ellipse((lx, y + 16, lx + 8, y + 24), fill=col)
            d.ellipse((lx, y + 30, lx + 8, y + 38), fill=(40, 130, 90, 255))
    d.rounded_rectangle(
        (64, 250, 236, 320),
        6,
        fill=(16, 90, 46, 255),
        outline=(90, 255, 160, 255),
        width=3,
    )
    d.text(
        (150, 285),
        "H100",
        font=font(IMPACT, 52),
        fill=(180, 255, 210, 255),
        anchor="mm",
    )
    add_glow(im, (60, 255, 150, 255), 260, (150, 300), 0.35)
    save(im, "server_rack.png")


def make_ram_icons():
    ram = load_rgba("ram_stick.png")
    sm = ram.resize((120, round(ram.height * 120 / ram.width)), Image.LANCZOS)
    save(sm, "ram_icon.png")


def make_coin():
    im = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse(
        (6, 6, 104, 104), fill=(40, 120, 80, 255), outline=(120, 255, 180, 255), width=4
    )
    d.ellipse((16, 16, 94, 94), fill=(24, 200, 120, 255))
    d.text((55, 58), "$20", font=font(IMPACT, 40), fill=(6, 30, 20, 255), anchor="mm")
    add_glow(im, (60, 255, 160, 255), 90, (55, 55), 0.6)
    save(im, "coin20.png")


def make_chrome():
    im = Image.new("RGBA", (260, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(
        (4, 10, 256, 176),
        8,
        fill=(238, 240, 244, 255),
        outline=(120, 126, 136, 255),
        width=2,
    )
    d.rounded_rectangle((4, 10, 256, 44), 8, fill=(214, 220, 228, 255))
    d.rectangle((10, 24, 250, 44), fill=(214, 220, 228, 255))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((16 + i * 18, 18, 30 + i * 18, 32), fill=c + (255,))
    d.rounded_rectangle((84, 18, 246, 36), 9, fill=(248, 249, 251, 255))
    d.text(
        (96, 27),
        "chrome://tabs",
        font=font(SEGOE_B, 11),
        fill=(120, 128, 140, 255),
        anchor="lm",
    )
    for i in range(3):
        y = 54 + i * 34
        d.rounded_rectangle((16, y, 60, y + 26), 4, fill=(206, 212, 220, 255))
        d.rounded_rectangle((66, y, 244, y + 26), 4, fill=(226, 230, 236, 255))
    d.text(
        (130, 148),
        "500 вкладок",
        font=font(SEGOE_B, 16),
        fill=(180, 40, 40, 255),
        anchor="mm",
    )
    save(im, "chrome_win.png")


def make_icon(sam):
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 255, 255), fill=(12, 30, 24, 255))
    s = sam.copy()
    s = s.resize((round(s.width * 240 / s.height), 240), Image.LANCZOS)
    im.alpha_composite(s, ((256 - s.width) // 2, 24))
    mask = Image.new("L", (1024, 1024), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 1023, 1023), fill=255)
    mask = mask.resize((256, 256), Image.LANCZOS)
    out = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    out.save(
        os.path.join(ROOT, "icon.ico"), sizes=[(256, 256), (64, 64), (32, 32), (16, 16)]
    )
    save(out, "sam_icon.png")


# --------------------------------------------------------------------------
# audio synthesis
# --------------------------------------------------------------------------
SR = 44100


def write_wav(name, data, sr=SR):
    data = np.asarray(data, dtype=np.float32)
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype("<i2")
    path = os.path.join(ASSETS, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    print("  [wav]", name, "%.2fs" % (len(data) / sr))


def t(sec, sr=SR):
    return np.arange(int(sec * sr)) / sr


def env(n, a=0.005, d=0.1, r=0.1, sustain_level=0.7):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s = max(0, n - a - d - r)
    e = np.concatenate(
        [
            np.linspace(0, 1, max(a, 1)),
            np.linspace(1, sustain_level, max(d, 1)),
            np.full(s, sustain_level),
            np.linspace(sustain_level, 0, max(r, 1)),
        ]
    )
    return e[:n]


def sine(f, dur, sr=SR):
    return np.sin(2 * np.pi * f * np.arange(int(dur * sr)) / sr)


def saw(f, dur, sr=SR):
    x = (np.arange(int(dur * sr)) * f / sr) % 1.0
    return 2 * x - 1


def square(f, dur, duty=0.5, sr=SR):
    x = (np.arange(int(dur * sr)) * f / sr) % 1.0
    return np.where(x < duty, 1.0, -1.0)


def noise(dur, sr=SR):
    return np.random.uniform(-1, 1, int(dur * sr))


def lowpass(x, cutoff, sr=SR):
    n = max(1, int(sr / (2 * np.pi * max(cutoff, 20))))
    return np.convolve(x, np.ones(n) / n, mode="same")


def highpass(x, cutoff, sr=SR):
    return x - lowpass(x, cutoff, sr)


def reverb(x, decay=0.35, delays=(0.031, 0.047, 0.071, 0.113), mix=0.4):
    out = x.copy()
    for dl in delays:
        d = int(dl * SR)
        pad = np.zeros(d)
        delayed = np.concatenate([pad, x])[: len(x)]
        out += delayed * decay * mix
    return out


def place(buf, x, at):
    i = int(at * SR)
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i : i + n] += x[:n]


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def sfx_all():
    dur = 0.22
    x = lowpass(noise(dur) * env(int(dur * SR), 0.001, 0.06, 0.08), 900)
    x += sine(70, dur) * env(int(dur * SR), 0.001, 0.1, 0.06) * 0.9
    write_wav("hit.wav", x * 0.85)

    dur = 0.9
    x = np.zeros(int(dur * SR))
    for f in (420, 631, 887, 1207, 1720):
        x += sine(f, dur) * np.exp(-t(dur) * 6) * 0.18
    x += highpass(noise(dur), 3000) * np.exp(-t(dur) * 30) * 0.4
    write_wav("clang.wav", x * 0.8)

    dur = 0.5
    tt = t(dur)
    f = 1800 * np.exp(-tt * 3) + 180
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-tt * 2.5)
    write_wav("laser.wav", x * 0.55)

    dur = 0.42
    x = np.zeros(int(dur * SR))
    place(x, sine(1320, 0.12) * np.exp(-t(0.12) * 8) * 0.5, 0)
    place(x, sine(1760, 0.3) * np.exp(-t(0.3) * 7) * 0.5, 0.09)
    write_wav("coin.wav", x)

    dur = 0.35
    n = noise(dur)
    n = lowpass(n, 1400) * np.linspace(0, 1, len(n)) ** 1.5 * np.exp(-t(dur) * 4)
    write_wav("whoosh.wav", n * 0.6)

    dur = 2.2
    tt = t(dur)
    x = sine(48, dur) * np.exp(-tt * 1.6)
    x += sine(31, dur) * np.exp(-tt * 1.1) * 0.8
    x += lowpass(noise(dur), 700) * np.exp(-tt * 3.2) * 0.9
    x += lowpass(noise(dur), 4000) * np.exp(-tt * 14) * 0.5
    write_wav("boom.wav", np.tanh(x * 1.2) * 0.95)

    dur = 2.6
    tt = t(dur)
    x = lowpass(noise(dur), 900) * np.exp(-tt * 1.7)
    x += sine(40, dur) * np.exp(-tt * 1.2) * 0.8
    x = reverb(np.tanh(x * 2.0), 0.5, mix=0.6)
    write_wav("explosion.wav", x * 0.9)

    dur = 3.2
    tt = t(dur)
    base = lowpass(noise(dur), 2200)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * tt)
    x = base * mod * np.minimum(tt * 4, 1) * np.exp(-np.maximum(tt - 1.2, 0) * 1.4)
    x += lowpass(noise(dur), 500) * 0.3
    write_wav("crowd.wav", x * 0.5)

    dur = 1.6
    tt = t(dur)
    x = (sine(58.27, dur) + sine(87.3, dur) * 0.5) * 0.5
    x += lowpass(noise(dur), 300) * 0.12
    x *= np.minimum(tt * 6, 1)
    write_wav("bsod.wav", x * 0.5)

    dur = 0.08
    write_wav("click.wav", square(900, dur, 0.3) * np.exp(-t(dur) * 50) * 0.25)

    dur = 0.65
    x = np.zeros(int(dur * SR))
    place(x, (sine(740, 0.22) * 0.4 + square(740, 0.22) * 0.1), 0)
    place(x, (sine(620, 0.34) * 0.4 + square(620, 0.34) * 0.1), 0.28)
    write_wav("error.wav", x * 0.6)

    dur = 3.4
    x = np.zeros(int(dur * SR))
    for n, at, ln in [
        (60, 0.0, 0.28),
        (64, 0.18, 0.28),
        (67, 0.36, 0.3),
        (72, 0.54, 0.9),
        (67, 0.9, 0.22),
        (72, 1.1, 1.3),
    ]:
        f = midi(n)
        v = sine(f, ln) + saw(f, ln) * 0.35 + sine(f * 2, ln) * 0.2
        v *= env(len(v), 0.01, 0.1, 0.5, 0.55) * 0.33
        place(x, v, at)
        place(x, v * 0.5, at + 0.02)
    write_wav("victory.wav", reverb(x, 0.4, mix=0.35) * 0.8)

    dur = 2.0
    tt = t(dur)
    x = np.zeros(int(dur * SR))
    for f, a in ((110, 0.6), (164, 0.3), (221, 0.2), (330, 0.12), (442, 0.08)):
        x += sine(f, dur) * np.exp(-tt * 2.2) * a
    x += highpass(noise(dur), 4000) * np.exp(-tt * 20) * 0.3
    write_wav("gong.wav", x * 0.6)

    dur = 0.5
    x = np.zeros(int(dur * SR))
    for i in range(9):
        place(
            x, square(600 + i * 90, 0.06, 0.5) * np.exp(-t(0.06) * 40) * 0.12, i * 0.045
        )
    write_wav("tabs.wav", x)


def music_theme():
    bpm = 132.0
    beat = 60 / bpm
    bars = 8
    dur = beat * 4 * bars
    buf = np.zeros(int(dur * SR))

    def at(bar, bt):
        return (bar * 4 + bt) * beat

    roots = [45, 45, 48, 43, 45, 45, 41, 43]
    for bar in range(bars):
        root = roots[bar]
        for i in range(16):
            f = midi(root - 12) * (2 if i % 4 == 3 else 1)
            b = saw(f, beat / 4 * 0.9) * env(
                int(beat / 4 * 0.9 * SR), 0.002, 0.05, 0.04, 0.8
            )
            place(buf, b * 0.30, at(bar, i / 4))
        for bt in (0, 1, 2, 3):
            kd = 0.22
            tt = t(kd)
            k = sine(52 * np.exp(-tt * 8) + 30, kd) * np.exp(-tt * 16) * 1.4
            k += lowpass(noise(kd), 900) * np.exp(-tt * 90) * 0.5
            place(buf, k * 0.55, at(bar, bt))
        for bt in (1, 3):
            sd = 0.2
            s = highpass(noise(sd), 1400) * np.exp(-t(sd) * 18) * 0.3
            s += sine(190, sd) * np.exp(-t(sd) * 25) * 0.15
            place(buf, s, at(bar, bt))
        for i in range(8):
            hd = 0.05
            h = (
                highpass(noise(hd), 7000)
                * np.exp(-t(hd) * 55)
                * (0.10 if i % 2 else 0.06)
            )
            place(buf, h, at(bar, i / 2))
        if bar >= 2:
            for bt, off in [(0, 0), (0.75, 7), (1.5, 5), (2.25, 3), (3, 7)]:
                f = midi(root + 12 + off)
                ld = beat * 0.28
                y = (
                    saw(f, ld) * 0.5
                    + square(f * 1.005, ld) * 0.3
                    + sine(f * 0.5, ld) * 0.3
                )
                y *= env(len(y), 0.01, 0.08, 0.14, 0.5)
                place(buf, y * 0.15, at(bar, bt))
        if bar in (0, 4):
            pd = beat * 16
            for off in (0, 3, 7):
                f = midi(root + 24 + off)
                y = saw(f, pd) * 0.35 + saw(f * 1.01, pd) * 0.35
                y *= np.minimum(t(pd) * 1.2, 1) * np.minimum((pd - t(pd)) * 0.9, 1)
                place(buf, lowpass(y, 2600) * 0.10, at(bar, 0))
    rd = beat * 4
    r = highpass(noise(rd), 400) * np.linspace(0, 1, int(rd * SR)) ** 2 * 0.25
    place(buf, r, dur - rd)
    for bar in (0, 4):
        bd = 1.2
        tt = t(bd)
        im_ = (
            sine(46, bd) * np.exp(-tt * 3)
            + lowpass(noise(bd), 800) * np.exp(-tt * 8) * 0.6
        )
        place(buf, im_ * 0.5, at(bar, 0))
    buf = np.tanh(buf * 1.1)
    fade = int(0.05 * SR)
    buf[:fade] *= np.linspace(0, 1, fade)
    write_wav("mk_theme.wav", buf * 0.9)


def ambient_loop():
    dur = 12.0
    tt = t(dur)
    x = sine(55, dur) * 0.12 + sine(82.4, dur) * 0.07
    x += lowpass(noise(dur), 400) * 0.05
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * tt)
    fade = int(1.5 * SR)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    write_wav("ambient.wav", x * 0.6)


def read_wav(path):
    with wave.open(path, "rb") as w:
        ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    if ch == 2:
        x = x.reshape(-1, 2).mean(axis=1)
    return x, sr


def voice_fx():
    """Arcade announcer treatment: pitch down + long reverb."""
    for name, pitch, wet, gain in (
        ("vo_rack", 0.88, 0.55, 1.15),
        ("vo_mkannounce", 0.90, 0.85, 1.20),
        ("vo_fatality", 0.86, 0.95, 1.20),
        ("vo_round2announce", 0.92, 0.6, 1.1),
    ):
        p = os.path.join(ASSETS, name + ".wav")
        if not os.path.exists(p):
            print("  [fx] missing", name)
            continue
        x, sr = read_wav(p)
        idx = np.arange(0, len(x) - 1, pitch)
        i0 = idx.astype(int)
        frac = idx - i0
        y = x[i0] * (1 - frac) + x[i0 + 1] * frac
        y = reverb(y, 0.45, mix=wet)
        y = np.tanh(y * gain) * 0.92
        write_wav(name + "_fx.wav", y, sr)
        print("  [fx]", name)


# --------------------------------------------------------------------------
def main():
    os.makedirs(ASSETS, exist_ok=True)
    print("cutout sprites")
    sam = make_sprites()
    make_avatar(sam)
    make_icon(sam)
    make_ram_icons()
    make_rack()
    make_coin()
    make_chrome()
    print("backgrounds")
    make_arena()
    make_keynote_bg()
    make_victory_bg()
    make_thanks_wall(sam)
    print("audio")
    sfx_all()
    music_theme()
    ambient_loop()
    voice_fx()
    print("done ->", ASSETS)


if __name__ == "__main__":
    main()
