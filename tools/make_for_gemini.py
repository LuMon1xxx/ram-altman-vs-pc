# -*- coding: utf-8 -*-
"""Builds ../for_gemini — a flat folder with everything to upload into Gemini."""

import glob
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(os.path.dirname(ROOT), "for_gemini")

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)

CODE = [
    ("main.py", "main.py"),
    ("tools/build_assets.py", "build_assets.py"),
    ("tools/build_video.py", "build_video.py"),
    ("tools/make_voice.ps1", "make_voice.ps1"),
    ("PROMPT_FOR_GEMINI.md", "PROMPT_FOR_GEMINI.md"),
    ("GEMINI_BUNDLE.md", "GEMINI_BUNDLE.md"),
    ("README.md", "README.md"),
]
IMAGES = [
    "sam.png",
    "sam_fight.png",
    "sam_avatar.png",
    "pc.png",
    "ram.png",
    "ram_icon.png",
    "server_rack.png",
    "coin20.png",
    "chrome_win.png",
    "logo_green.png",
    "logo_white.png",
    "arena_bg.png",
    "thanks_wall.png",
    "fake_desktop.png",
    "keynote_bg.png",
    "victory_bg.png",
    "sam_icon.png",
]
SOURCE = ["sam_cutout.png", "pc_case.png", "ram_stick.png", "chatgpt_logo.png"]
SHOTS = [
    "toast_2.2.png",
    "toast_jump.png",
    "thanks.png",
    "fight1_4.2.png",
    "fight1_cut1.png",
    "bsod_1.5.png",
    "fight2_cue1.png",
    "fight2_fat1.png",
    "victory_2.png",
]


def put(src, folder, name=None):
    if not os.path.exists(src):
        print("  MISSING", src)
        return 0
    dst = os.path.join(DST, folder, name or os.path.basename(src))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return os.path.getsize(dst)


total = 0
for rel, name in CODE:
    total += put(os.path.join(ROOT, rel), "", name)

for name in IMAGES:
    total += put(os.path.join(ROOT, "assets", name), "images")

for name in SOURCE:
    total += put(os.path.join(ROOT, "source_media", name), "source_media")

for name in SHOTS:
    total += put(os.path.join(ROOT, "tools", "shots", name), "screenshots")

for name in ("mk_theme.wav", "hit.wav", "boom.wav", "laser.wav"):
    total += put(os.path.join(ROOT, "assets", name), "sounds")

START = """# ЧТО ЭТО ЗА ПАПКА

Здесь **реальный рабочий код** игры «RAM Altman vs PC» и её картинки. Это не пример и не
описание — файлы ровно такие, какие собираются в exe и запускаются сейчас.

## Как читать

1. `main.py` — весь код (стучись сюда за логикой боя: класс `FightScreen`).
2. `build_assets.py` — как рисуются все PNG и синтезируются WAV (PIL + numpy).
3. `PROMPT_FOR_GEMINI.md` — что именно надо доработать.
4. `GEMINI_BUNDLE.md` — те же исходники одним файлом (удобно, если .py не прикрепляется).
5. `images/` — итоговые спрайты: `sam.png` (поясной портрет), `sam_fight.png`
   (полный рост для боя), `pc.png` (корпус ПК), `logo_green.png` / `logo_white.png`
   (логотип OpenAI — из него делать шары-снаряды), `chrome_win.png` (вкладка), `coin20.png`.
6. `source_media/` — исходные вырезки до обработки (`sam_cutout.png`, `pc_case.png`,
   `ram_stick.png`, `chatgpt_logo.png`).
7. `screenshots/` — как игра выглядит сейчас: уведомление, экран благодарности,
   раунд 1, падение стойки, BSOD, раунд 2, победа.
8. `sounds/` — примеры синтезированных звуков.

## Жёсткие правила

- Не переписывать проект с нуля. Править существующий код.
- Трогать только бой (`FightScreen`) и, если нужны новые спрайты, `build_assets.py`.
  `ToastScreen`, `ThanksScreen`, `BSODScreen`, `VictoryScreen`, `watch_service`,
  `install_service`, `poll_quit` — не менять.
- Новые картинки/звуки генерировать кодом в `build_assets.py`. В `main.py` — только
  `pygame.image.load(asset("имя.png"))`, никакой генерации на лету.
- Возвращать `main.py` целиком, не фрагментом.
- Сначала план на 10–15 строк, потом код.
"""
with open(
    os.path.join(DST, "00_START_HERE.md"), "w", encoding="utf-8", newline="\n"
) as f:
    f.write(START)

files = glob.glob(os.path.join(DST, "**", "*"), recursive=True)
files = [f for f in files if os.path.isfile(f)]
print("\n%d files, %.1f MB -> %s" % (len(files), total / 1e6, DST))
for f in sorted(files):
    print("  %-58s %7.0f KB" % (os.path.relpath(f, DST), os.path.getsize(f) / 1024))
