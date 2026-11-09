"""Headless check: orb spacing and fight balance sanity."""

import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "\\..")

import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
import main as M

M.grab_desktop_surface = lambda: None
app = M.App()
app.display.windowed((M.CW, M.CH), "test")

f = M.FightScreen(app, 1, overlay=True)
f.mode = "fight"
f.mode_t = 5.0

# запускаем волну и смотрим минимальный зазор между соседними шарами
f.spawn_orb_wave()
gaps = []
prev = {}
for step in range(60 * 20):
    f.update(1 / 60, [])
    snap = sorted(ob["x"] for ob in f.orbs)
    for a, b in zip(snap, snap[1:]):
        gaps.append(b - a)
    if step % (60 * 6) == 0:
        f.spawn_orb_wave()

print("orbs max on screen:", max(len(f.orbs), 0))
print("min gap: %.1f px (orb is 92 px wide)" % (min(gaps) if gaps else -1))
print("avg gap: %.1f px" % (sum(gaps) / len(gaps) if gaps else -1))

pc = f.pc_img.get_size()
sam = f.sam_img.get_size()
print("pc sprite:", pc, "sam sprite:", sam)

# проверим, что модель урона жива: 20 ударов по Сэму
f.player["x"] = 700.0
f.sam["x"] = 800.0
hp0 = f.sam["hp"]
for i in range(20):
    f.player["atk_cd"] = 0.0
    f.player_attack()
    f.update(1 / 60, [])
print("sam hp after 20 hits: %.0f (was %.0f)" % (f.sam["hp"], hp0))
pygame.quit()
