# -*- coding: utf-8 -*-
"""Assembles the release folder: exe + mp4 + readme."""

import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(ROOT, "release")
os.makedirs(REL, exist_ok=True)

exe = os.path.join(ROOT, "dist", "RAM_Altman_vs_PC.exe")
mp4 = os.path.join(ROOT, "out", "Altman_RAM_interview.mp4")
readme = os.path.join(ROOT, "README.md")

for src, name in (
    (exe, "RAM_Altman_vs_PC.exe"),
    (mp4, "Altman_RAM_interview.mp4"),
    (readme, "README.md"),
):
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(REL, name))
        print("copied", name, "%.1f MB" % (os.path.getsize(src) / 1e6))
    else:
        print("MISSING", src)
