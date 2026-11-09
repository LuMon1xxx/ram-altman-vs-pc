def make_fight_extras():
    """Генерация новых спрайтов для расширенного боя."""
    # 1. Шар-логотип ChatGPT (orb_gpt.png)
    orb = Image.new("RGBA", (92, 92), (0, 0, 0, 0))
    d = ImageDraw.Draw(orb, "RGBA")
    d.ellipse(
        (6, 6, 86, 86),
        fill=(14, 52, 38, 245),
        outline=(80, 255, 175, 255),
        width=4,
    )
    add_glow(orb, (80, 255, 175, 220), 44, (46, 46), 0.55)
    logo = load_rgba("chatgpt_logo.png").resize((58, 58), Image.LANCZOS)
    white_logo = Image.new("RGBA", logo.size, (240, 255, 248, 0))
    white_logo.putalpha(logo.split()[3])
    orb.alpha_composite(white_logo, (17, 17))
    save(orb, "orb_gpt.png")

    # 2. Снаряд-винт системного блока (screw_proj.png)
    screw = Image.new("RGBA", (56, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(screw, "RGBA")
    pts = []
    for i in range(6):
        a = math.pi / 3 * i
        pts.append((28 + math.cos(a) * 20, 28 + math.sin(a) * 20))
    d.polygon(pts, fill=(185, 200, 218, 255), outline=(95, 215, 255, 255))
    d.ellipse((16, 16, 40, 40), fill=(110, 122, 138, 255), outline=(230, 240, 255, 255), width=2)
    d.line((20, 28, 36, 28), fill=(35, 42, 52, 255), width=4)
    d.line((28, 20, 28, 36), fill=(35, 42, 52, 255), width=4)
    add_glow(screw, (95, 215, 255, 200), 26, (28, 28), 0.5)
    save(screw, "screw_proj.png")

    # 3. Падающий знак $ инвестора (dollar_drop.png)
    dlr = Image.new("RGBA", (110, 130), (0, 0, 0, 0))
    add_glow(dlr, (255, 205, 90, 240), 54, (55, 65), 0.7)
    d = ImageDraw.Draw(dlr, "RGBA")
    d.text((57, 68), "$", font=font(IMPACT, 102), fill=(25, 45, 20, 220), anchor="mm")
    d.text((55, 65), "$", font=font(IMPACT, 102), fill=(255, 215, 85, 255), anchor="mm")
    save(dlr, "dollar_drop.png")

    # 4. Целевой маркер на полу (floor_marker.png)
    mk = Image.new("RGBA", (150, 38), (0, 0, 0, 0))
    d = ImageDraw.Draw(mk, "RGBA")
    d.ellipse((4, 4, 146, 34), fill=(255, 60, 60, 75), outline=(255, 95, 95, 235), width=3)
    d.ellipse((28, 10, 122, 28), outline=(255, 215, 110, 210), width=2)
    save(mk, "floor_marker.png")

    # 5. Мини-стойка для «серверного шквала» (mini_rack.png)
    mr = Image.new("RGBA", (110, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(mr, "RGBA")
    d.rounded_rectangle(
        (8, 6, 102, 214),
        8,
        fill=(26, 30, 36, 255),
        outline=(80, 255, 175, 255),
        width=3,
    )
    for i in range(5):
        y = 18 + i * 36
        d.rounded_rectangle((16, y, 94, y + 26), 4, fill=(38, 44, 52, 255))
        d.ellipse((76, y + 8, 86, y + 18), fill=(80, 255, 175, 255))
    d.text((55, 115), "H100", font=font(IMPACT, 26), fill=(200, 255, 225, 255), anchor="mm")
    save(mr, "mini_rack.png")

    # 6. Ауры фаз Сэма (aura_p1.png, aura_p2.png, aura_p3.png)
    for idx, col, strength in (
        (1, (80, 255, 175, 180), 0.32),
        (2, (95, 215, 255, 210), 0.48),
        (3, (255, 75, 75, 235), 0.62),
    ):
        au = radial_glow((380, 420), col, 185, (190, 210), strength)
        save(au, f"aura_p{idx}.png")