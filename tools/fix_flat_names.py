import io

p = r"ram_altman_game\tools\make_for_gemini_flat.py"
s = io.open(p, encoding="utf-8").read()

s = s.replace(
    """    ("GEMINI_BUNDLE.md", "00_GEMINI_BUNDLE.md"),
    ("main.py", "01_main.py"),
    ("tools/build_assets.py", "02_build_assets.py"),
    ("tools/build_video.py", "03_build_video.py"),
    ("PROMPT_FOR_GEMINI.md", "04_PROMPT_FOR_GEMINI.md"),
    ("README.md", "05_README.md"),
    ("tools/make_voice.ps1", "06_make_voice.ps1"),""",
    """    ("GEMINI_BUNDLE.md", "01_GEMINI_BUNDLE.md"),
    ("main.py", "02_main.py"),
    ("tools/build_assets.py", "03_build_assets.py"),
    ("tools/build_video.py", "04_build_video.py"),
    ("PROMPT_FOR_GEMINI.md", "05_PROMPT_FOR_GEMINI.md"),
    ("README.md", "06_README.md"),
    ("tools/make_voice.ps1", "07_make_voice.ps1"),""",
)

s = s.replace("`00_…` … `06_…`", "`00_…` … `07_…`")
s = s.replace("1. `00_GEMINI_BUNDLE.md`", "1. `01_GEMINI_BUNDLE.md`")
s = s.replace("2. `01_main.py`", "2. `02_main.py`")
s = s.replace("`00_GEMINI_BUNDLE.md` и скажи", "`01_GEMINI_BUNDLE.md` и скажи")
s = s.replace("3. `04_PROMPT_FOR_GEMINI.md`", "3. `05_PROMPT_FOR_GEMINI.md`")
s = s.replace(
    "7. `02_build_assets.py` и `03_build_video.py`",
    "7. `03_build_assets.py` и `04_build_video.py`",
)
s = s.replace(
    """```
00_GEMINI_BUNDLE.md
01_main.py
04_PROMPT_FOR_GEMINI.md""",
    """```
01_GEMINI_BUNDLE.md
02_main.py
05_PROMPT_FOR_GEMINI.md""",
)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
