# -*- coding: utf-8 -*-
"""Packs the real sources into one file to upload into Gemini / AI Studio."""

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "GEMINI_BUNDLE.md")

FILES = [
    ("main.py", "python"),
    ("tools/build_assets.py", "python"),
    ("tools/build_video.py", "python"),
    ("tools/make_voice.ps1", "powershell"),
    ("README.md", "markdown"),
    ("PROMPT_FOR_GEMINI.md", "markdown"),
]

header = """# RAM Altman vs PC — полный исходник для доработки

**Это НЕ описание и НЕ пример. Это реальные файлы проекта, как они есть сейчас и работают.**
Не переписывай проект с нуля: меняй только то, что просят. Сохраняй имена классов,
методов, путей и поведение сценария, описанные в PROMPT_FOR_GEMINI.md.

Дерево файлов:

```
main.py                        весь код: ToastScreen, ThanksScreen, FightScreen,
                               BSODScreen, VictoryScreen, служба --watch, --install
assets/                        готовые PNG и WAV (уже сгенерированы)
source_media/                  исходные вырезки и сырое видео
out/Altman_RAM_interview.mp4   готовый «вброс»
tools/build_assets.py          генерация всех PNG/WAV кодом (PIL + numpy)
tools/build_video.py           сборка mp4 через ffmpeg
tools/make_voice.ps1           озвучка через Windows TTS
README.md                      инструкция
```

Сборка exe:

```powershell
pyinstaller --noconfirm --onefile --noconsole --name RAM_Altman_vs_PC ^
  --icon icon.ico --add-data "assets;assets" --add-data "icon.ico;." main.py
```

Проверка без открытия окна: `python main.py --selftest` (должен печатать SELFTEST OK).

---

"""

parts = [header]
for rel, lang in FILES:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print("skip", rel)
        continue
    with io.open(p, encoding="utf-8") as f:
        body = f.read()
    parts.append("\n## `%s`\n\n```%s\n%s\n```\n" % (rel, lang, body.rstrip("\n")))
    print("%-28s %6d lines" % (rel, body.count("\n") + 1))

text = "".join(parts)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("\nbundle:", OUT, "%.1f KB" % (len(text.encode("utf-8")) / 1024))
