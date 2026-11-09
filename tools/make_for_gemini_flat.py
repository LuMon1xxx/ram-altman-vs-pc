# -*- coding: utf-8 -*-
"""Flattens everything into ../for_gemini_flat — one level, uploadable file by file."""

import glob
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(os.path.dirname(ROOT), "for_gemini_flat")

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)

# (source path, destination name)
PLAN = [
    ("GEMINI_BUNDLE.md", "01_GEMINI_BUNDLE.md"),
    ("main.py", "02_main.py"),
    ("tools/build_assets.py", "03_build_assets.py"),
    ("tools/build_video.py", "04_build_video.py"),
    ("PROMPT_FOR_GEMINI.md", "05_PROMPT_FOR_GEMINI.md"),
    ("README.md", "06_README.md"),
    ("tools/make_voice.ps1", "07_make_voice.ps1"),
]

SHOTS = [
    ("toast_2.2.png", "shot_1_notification.png"),
    ("toast_jump.png", "shot_2_no_button_jumped.png"),
    ("thanks.png", "shot_3_thanks_A_G_I.png"),
    ("fight1_4.2.png", "shot_4_round1_fight.png"),
    ("fight1_cut1.png", "shot_5_round1_rack_drop.png"),
    ("bsod_1.5.png", "shot_6_bsod.png"),
    ("fight2_cue1.png", "shot_7_round2_dodge_cue.png"),
    ("fight2_fat1.png", "shot_8_round2_fatality.png"),
    ("victory_2.png", "shot_9_victory.png"),
]

IMAGES = [
    ("sam_fight.png", "img_sam_fight.png"),
    ("sam.png", "img_sam.png"),
    ("sam_avatar.png", "img_sam_avatar.png"),
    ("pc.png", "img_pc.png"),
    ("ram.png", "img_ram.png"),
    ("ram_icon.png", "img_ram_icon.png"),
    ("server_rack.png", "img_server_rack.png"),
    ("coin20.png", "img_coin20.png"),
    ("chrome_win.png", "img_chrome_win.png"),
    ("logo_green.png", "img_logo_green.png"),
    ("logo_white.png", "img_logo_white.png"),
    ("arena_bg.png", "img_arena_bg.png"),
    ("thanks_wall.png", "img_thanks_wall.png"),
    ("fake_desktop.png", "img_fake_desktop.png"),
]

SOURCE = [
    ("sam_cutout.png", "src_sam_cutout.png"),
    ("pc_case.png", "src_pc_case.png"),
    ("ram_stick.png", "src_ram_stick.png"),
    ("chatgpt_logo.png", "src_chatgpt_logo.png"),
]


def put(src, name):
    if not os.path.exists(src):
        print("  MISSING", src)
        return 0
    shutil.copy2(src, os.path.join(DST, name))
    return os.path.getsize(src)


total = 0
for rel, name in PLAN:
    total += put(os.path.join(ROOT, rel), name)
for src, name in SHOTS:
    total += put(os.path.join(ROOT, "tools", "shots", src), name)
for src, name in IMAGES:
    total += put(os.path.join(ROOT, "assets", src), name)
for src, name in SOURCE:
    total += put(os.path.join(ROOT, "source_media", src), name)

START = """# ЗАГРУЖАТЬ В GEMINI ЭТИМИ ФАЙЛАМИ

Всё лежит одним уровнем, ничего распаковывать не надо. Имена с префиксами, чтобы не путаться:

- `00_…` … `07_…` — код и инструкции.
- `shot_1…shot_9` — скриншоты: как игра выглядит сейчас (это твой дизайн-референс).
- `img_…` — готовые спрайты из `assets/`.
- `src_…` — исходные вырезки из `source_media/`.

## Порядок загрузки (важен)

1. `01_GEMINI_BUNDLE.md` — весь код одним файлом. **Обязательно первым.**
2. `02_main.py` — если AI Studio примет `.py`. Если откажется — загрузи
   `01_GEMINI_BUNDLE.md` и скажи: «main.py внутри бандла, раздел `## main.py`».
3. `05_PROMPT_FOR_GEMINI.md` — там задача.
4. `shot_1…shot_9` — все 9 подряд: он увидит уведомление, бой, BSOD, победу.
5. `img_sam_fight.png`, `img_pc.png`, `img_logo_green.png`, `img_chrome_win.png`,
   `img_coin20.png`, `img_server_rack.png` — минимальный набор спрайтов для боя.
6. Остальные `img_…` и `src_…` — по желанию, если хочешь, чтобы он видел сырьё.
7. `03_build_assets.py` и `04_build_video.py` — если он будет менять генерацию ассетов.

## Минимальный набор, если не хочется грузить всё (12 файлов)

```
01_GEMINI_BUNDLE.md
02_main.py
05_PROMPT_FOR_GEMINI.md
shot_1_notification.png
shot_4_round1_fight.png
shot_5_round1_rack_drop.png
shot_6_bsod.png
shot_7_round2_dodge_cue.png
shot_9_victory.png
img_sam_fight.png
img_pc.png
img_logo_green.png
```

## Что сказать в сообщении

> Прикрепляю реальный код и картинки. Это не пример, а рабочая игра. Не пересоздавай проект,
> правь существующий код. Сделай бой длиннее (60–90 с), добавь прыжок на W, удар сверху,
> отскок, заряженный выстрел винтами, и атаку Сэма — шары с логотипом ChatGPT, которые катятся
> по полу и которые игрок перепрыгивает; Сэм сам подпрыгивает, когда его шар подлетает к нему.
> Трогай только `FightScreen` и его константы. Новые спрайты — кодом в `build_assets.py`,
> в `main.py` только `pygame.image.load(asset(...))`. Верни `main.py` целиком, не фрагментом.
> Сначала план на 10–15 строк, дождись «ок», потом код.

## Чего не делать

- Не грузи `mk_theme.wav` — 2.5 МБ и бесполезен для правок.
- Не проси «улучшить весь проект целиком» — он снесёт рабочую системную часть
  (уведомление, оверлей, службу автозапуска).
"""
with open(
    os.path.join(DST, "00_START_HERE.md"), "w", encoding="utf-8", newline="\n"
) as f:
    f.write(START)

files = sorted(f for f in os.listdir(DST) if os.path.isfile(os.path.join(DST, f)))
print("\n%d files, %.1f MB -> %s\n" % (len(files) + 1, total / 1e6, DST))
for f in files:
    print("  %-38s %7.0f KB" % (f, os.path.getsize(os.path.join(DST, f)) / 1024))
