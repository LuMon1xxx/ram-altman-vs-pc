Ты — Senior Python/Pygame разработчик и гейм-дизайнер. Ниже — РЕАЛЬНЫЙ РАБОЧИЙ код
шуточной игры «RAM Altman vs PC» (Windows, pygame 2.6, сборка PyInstaller --onefile
--noconsole). Это не пример и не описание: код компилируется и запускается как есть.

НЕ пересоздавай проект с нуля. Правь существующий код.

## Игра в двух словах
Два артефакта. (1) Обычный mp4-«вброс»: интервью с Сэмом Альтманом, потом речь про
экспроприацию ОЗУ. (2) exe-«служба»: сидит в автозагрузке, ждёт пока mp4 откроют и закроют,
показывает тост-уведомление «Служба оптимизации OpenAI AGI». При «Нет» — не даёт нажать
кнопку (она убегает) и запускает бой поверх рабочего стола. Раунд 1: ПК против Сэма,
при HP Сэма <= 25 скриптовая подлянка — падает серверная стойка H100, 9999 урона, игрок
проигрывает. BSOD. Пробел — раунд 2. Там «ЖМИ ПРОБЕЛ ДЛЯ УВОРОТА» — уворот, фаталити,
победа.

## Что надо сделать (только бой!)

1. Сделать бой ДОЛЬШЕ и интереснее: 60–90 секунд вместо 20–30. HP 160–200 обоим.
   Таймер раунда на HUD. Фазы Сэма на 66% и 33% HP (быстрее, новые атаки, другая аура).
   Комбо-множитель урона.
2. Новые возможности игрока (системный блок):
   - Прыжок на W и стрелке вверх: гравитация, приземление с пылью.
   - Удар сверху в воздухе (Пробел): больше урона, но дольше приземление.
   - Отскок S/вниз: рывок назад, 0.2 с неуязвимости, afterimage.
   - Заряженный удар: удержание Пробела 0.6 с -> выстрел винтами (снаряд вперёд).
   - F «50 вкладок Google Chrome» — оставить, добавить кулдаун-индикатор, урон по площади.
3. НОВАЯ АТАКА СЭМА (обязательно): шары-логотипы ChatGPT. Сэм выпускает с правого края
   несколько крупных шаров с логотипом OpenAI (assets/logo_green.png, logo_white.png),
   они катятся по полу слева направо НА ВЫСОТЕ, КОТОРУЮ МОЖНО ПЕРЕПРЫГНУТЬ. Игрок обязан
   перепрыгивать их на W. Ритм: 2–4 шара с интервалом, иногда «двойной» с малым зазором.
   ИРОНИЯ: Сэм сам автоматически подпрыгивает, когда его же шар подлетает к нему
   (шар проходит под ним), с недовольной репликой изредка: «Мои же шары!».
4. Дополнительно Сэму: усиленный лазер выпайки с телеграфом 0.9 с; «призыв инвестора» —
   с неба падает знак $ по маркеру на полу, урон по площади; «апдейт модели» — Сэм на миг
   полупрозрачный и телепортируется; «серверный шквал» в 3-й фазе — 3 мини-стойки по очереди
   с маркерами.

## Совместимость (жёстко)

- Меняй только FightScreen и его константы/методы. НЕ трогай ToastScreen, ThanksScreen,
  BSODScreen, VictoryScreen, watch_service, install_service, uninstall_service, poll_quit,
  Display, Audio, helper-функции (text, bar, wrap, clamp, asset, get_font).
- Не меняй сигнатуры методов, которые зовут снаружи: FightScreen(app, round_no=1,
  overlay=False, desktop=None); поля done/result; App.run_screen.
- Сохрани скриптовую подлянку H100 и 9999 урона в раунде 1, «ЖМИ ПРОБЕЛ ДЛЯ УВОРОТА»
  и фаталити в раунде 2, работу в оверлее поверх скриншота рабочего стола.
- Новые спрайты (шары, маркеры, тени, эффекты) рисуй КОДОМ: в tools/build_assets.py
  функциями PIL и сохраняй в assets/. В main.py только pygame.image.load(asset("имя.png")).
  Никакой генерации ассетов на лету, никаких новых зависимостей, никакой сети.
- Esc и Ctrl+Q должны закрывать игру в любой момент.
- 60 FPS, чистить списки снарядов каждый кадр, лимит на частицы.
- Комментарии по-русски и коротко. Баланс — в константы.

## Что вернуть

1. Полный main.py целиком (не фрагмент!).
2. Патч/дополнение tools/build_assets.py, если добавил спрайты.
3. Короткий changelog и три сценария проверки: игрок стоит и проигрывает; игрок прыгает
   через шары и доводит Сэма до 25 HP; игрок доходит до фаталити во 2 раунде.

Сначала пришли план на 10–15 строк и дождись моего «ок». Потом код.

## Дерево проекта

```
main.py                        весь код игры (см. ниже)
assets/                        готовые PNG и WAV (уже сгенерированы)
source_media/                  исходные вырезки: sam_cutout.png, pc_case.png,
                               ram_stick.png, chatgpt_logo.png
out/Altman_RAM_interview.mp4   готовый «вброс»
tools/build_assets.py          генерация PNG/WAV кодом (PIL + numpy)
tools/build_video.py           сборка mp4 через ffmpeg
tools/make_voice.ps1           озвучка через Windows TTS
README.md                      инструкция
```

Готовые ассеты, которые уже есть: sam.png (портрет), sam_fight.png (полный рост для боя),
sam_avatar.png, pc.png (корпус), ram.png, ram_icon.png, server_rack.png (шкаф H100),
coin20.png, chrome_win.png, logo_green.png, logo_white.png (логотип OpenAI 512x512, белый
и зелёный), arena_bg.png, thanks_wall.png, fake_desktop.png.

Сборка: pyinstaller --onefile --noconsole --name RAM_Altman_vs_PC --icon icon.ico
--add-data "assets;assets" --add-data "icon.ico;." main.py
Проверка: python main.py --selftest (должен печатать SELFTEST OK).

---

# ФАЙЛ main.py

```python
# -*- coding: utf-8 -*-
"""RAM Altman vs PC — a joke arcade mini-game for a school IT lesson.

States:  intro video -> native prank dialog -> MK round 1 -> fake BSOD
         -> round 2 (dodge + fatality) -> victory screen.
Escape / Ctrl+Q quits from anywhere.
"""

import json
import math
import os
import random
import shutil
import subprocess
import sys
import time

import pygame

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE_DIR, "assets")
CW, CH = 1280, 720
FPS = 60

GREEN = (80, 255, 175)
CYAN = (95, 215, 255)
RED = (255, 72, 72)
GOLD = (255, 205, 90)
WHITE = (245, 248, 250)
GREY = (150, 158, 170)
DARK = (8, 10, 14)

FONT_PATHS = {
    "impact": r"C:\Windows\Fonts\impact.ttf",
    "segoe": r"C:\Windows\Fonts\segoeui.ttf",
    "segoeb": r"C:\Windows\Fonts\segoeuib.ttf",
    "segoel": r"C:\Windows\Fonts\segoeuil.ttf",
    "consola": r"C:\Windows\Fonts\consola.ttf",
    "consolab": r"C:\Windows\Fonts\consolab.ttf",
    "arialb": r"C:\Windows\Fonts\arialbd.ttf",
}


def asset(name):
    return os.path.join(ASSETS, name)


# --------------------------------------------------------------------------
# basics
# --------------------------------------------------------------------------
class QuitGame(Exception):
    pass


def clamp(v, a, b):
    return a if v < a else (b if v > b else v)


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def dpi_aware():
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


_fonts = {}
_text_cache = {}


def get_font(name, size):
    key = (name, size)
    f = _fonts.get(key)
    if f is None:
        path = FONT_PATHS.get(name)
        try:
            f = (
                pygame.font.Font(path, size)
                if path and os.path.exists(path)
                else pygame.font.SysFont(name, size)
            )
        except Exception:
            f = pygame.font.SysFont("segoeui", size)
        _fonts[key] = f
    return f


def text(
    surf,
    txt,
    size,
    color,
    pos,
    anchor="topleft",
    font="segoeb",
    outline=None,
    outline_w=2,
    shadow=False,
    alpha=255,
):
    key = (txt, size, tuple(color), font, outline, outline_w, shadow, alpha)
    s = _text_cache.get(key)
    if s is None:
        f = get_font(font, size)
        base = f.render(txt, True, color)
        pad = outline_w + 2 if outline else 0
        w, h = base.get_size()
        s = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        if outline:
            o = f.render(txt, True, outline)
            for dx, dy in (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
                (1, 1),
                (-1, -1),
                (1, -1),
                (-1, 1),
                (2, 0),
                (-2, 0),
                (0, 2),
                (0, -2),
            ):
                s.blit(o, (pad + dx, pad + dy))
        if shadow:
            sh = f.render(txt, True, (0, 0, 0))
            sh.set_alpha(150)
            layer = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            layer.blit(sh, (pad + 4, pad + 4))
            layer.blit(s, (0, 0))
            s = layer
        s.blit(base, (pad, pad))
        if alpha < 255:
            s = s.copy()
            s.set_alpha(alpha)
        if len(_text_cache) > 700:
            _text_cache.clear()
        _text_cache[key] = s
    r = s.get_rect(**{anchor: pos})
    surf.blit(s, r)
    return r


def wrap(font_name, size, txt, max_w):
    f = get_font(font_name, size)
    words = txt.split(" ")
    lines, cur = [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if f.size(probe)[0] <= max_w:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(
    surf, txt, size, color, x, y, max_w, line_h=None, font="segoe", anchor="topleft"
):
    line_h = line_h or int(size * 1.35)
    for i, line in enumerate(wrap(font, size, txt, max_w)):
        text(surf, line, size, color, (x, y + i * line_h), anchor=anchor, font=font)
    return y + len(wrap(font, size, txt, max_w)) * line_h


def hp_color(frac):
    if frac > 0.55:
        return (86, 235, 130)
    if frac > 0.25:
        return (255, 200, 70)
    return (255, 70, 70)


def bar(surf, x, y, w, h, frac, color, flip=False, ghost=None, border=(220, 228, 235)):
    pygame.draw.rect(surf, (10, 12, 16), (x - 3, y - 3, w + 6, h + 6), border_radius=4)
    pygame.draw.rect(surf, (44, 48, 56), (x, y, w, h), border_radius=3)
    if ghost is not None and ghost > frac:
        gw = int(w * clamp(ghost, 0, 1))
        gx = x + w - gw if flip else x
        pygame.draw.rect(surf, (120, 40, 40), (gx, y, gw, h), border_radius=3)
    fw = int(w * clamp(frac, 0, 1))
    if fw > 0:
        fx = x + w - fw if flip else x
        pygame.draw.rect(surf, color, (fx, y, fw, h), border_radius=3)
        pygame.draw.rect(
            surf, (255, 255, 255, 60), (fx, y, fw, max(2, h // 3)), border_radius=3
        )
    pygame.draw.rect(surf, border, (x, y, w, h), 2, border_radius=3)


def vignette_surface(w, h, alpha=110):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    steps = 24
    for i in range(steps):
        a = int(alpha * (i / steps) ** 2)
        m = int(min(w, h) * 0.5 * (1 - i / steps))
        pygame.draw.rect(s, (0, 0, 0, a), (i * 2, i * 2, w - i * 4, h - i * 4), m)
    return s


def scanline_surface(w, h, alpha=22, step=3):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, step):
        pygame.draw.line(s, (0, 0, 0, alpha), (0, y), (w, y))
    return s


def glitch_rects(surf, rect, n=10, color=(255, 60, 60)):
    for _ in range(n):
        y = random.randint(rect.top, rect.bottom)
        h = random.randint(2, 14)
        x = random.randint(rect.left, rect.right)
        w = random.randint(20, rect.width // 2)
        sub = surf.subsurface(
            pygame.Rect(x, y, min(w, rect.right - x), min(h, rect.bottom - y))
        ).copy()
        surf.blit(sub, (x + random.randint(-18, 18), y))


# --------------------------------------------------------------------------
# audio
# --------------------------------------------------------------------------
class Audio:
    def __init__(self):
        self.ok = False
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            self.ok = True
        except Exception as e:
            print("audio init failed:", e)

    def snd(self, name):
        if not self.ok:
            return None
        s = self.sounds.get(name)
        if s is None:
            p = asset(name + ".wav")
            if not os.path.exists(p):
                return None
            try:
                s = pygame.mixer.Sound(p)
            except Exception:
                return None
            self.sounds[name] = s
        return s

    def play(self, name, vol=0.9):
        s = self.snd(name)
        if s:
            s.set_volume(vol)
            s.play()

    def music(self, name, vol=0.55, loops=-1):
        if not self.ok:
            return
        p = asset(name + ".wav")
        if not os.path.exists(p):
            return
        try:
            pygame.mixer.music.load(p)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(loops)
        except Exception as e:
            print("music failed:", e)

    def stop_music(self, fade_ms=0):
        if not self.ok:
            return
        try:
            if fade_ms:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass

    def length(self, name):
        s = self.snd(name)
        return s.get_length() if s else 0.0


# --------------------------------------------------------------------------
# display
# --------------------------------------------------------------------------
class Display:
    def __init__(self):
        self.screen = None
        self.canvas = pygame.Surface((CW, CH))
        self.fullscreen = False
        self.title = ""

    def _new_mode(self, size, flags, title):
        if self.screen is not None:
            pygame.display.quit()
            pygame.display.init()
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption(title)
        self.title = title
        self.canvas = pygame.Surface((CW, CH)).convert()
        self.layered = True

    def windowed(self, size, title):
        self._new_mode(size, 0, title)
        self.fullscreen = False
        pygame.mouse.set_visible(True)

    def go_fullscreen(self, title):
        self._new_mode((0, 0), pygame.FULLSCREEN, title)
        self.fullscreen = True
        pygame.mouse.set_visible(False)

    def toast_window(self, title, w, h, key=(255, 0, 255)):
        """Borderless, always-on-top window; `key` colour becomes transparent."""
        try:
            sw, sh = screen_size()
            os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (sw - w - 24, sh - h - 76)
        except Exception:
            pass
        self._new_mode((w, h), pygame.NOFRAME, title)
        self.canvas = pygame.Surface((w, h)).convert()
        self.fullscreen = False
        pygame.mouse.set_visible(True)
        self.layered = True
        try:
            import ctypes

            u = ctypes.windll.user32
            u.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_uint]
            u.SetLayeredWindowAttributes.argtypes = [ctypes.c_void_p, ctypes.c_uint,
                                                     ctypes.c_ubyte, ctypes.c_uint]
            hwnd = pygame.display.get_wm_info().get("window")
            GWL_EXSTYLE, WS_EX_LAYERED = -20, 0x00080000
            LWA_COLORKEY = 0x1
            style = u.GetWindowLongW(hwnd, GWL_EXSTYLE)
            u.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
            colorref = key[0] | (key[1] << 8) | (key[2] << 16)
            if not u.SetLayeredWindowAttributes(hwnd, colorref, 0, LWA_COLORKEY):
                self.layered = False
            u.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
        except Exception as e:
            self.layered = False
            print("layered window failed:", e)

    def go_overlay(self, title):
        """Borderless, always-on-top window sized to the game's 16:9 frame."""
        sw, sh = screen_size()
        scale = min(sw / CW, sh / CH)
        w, h = max(2, int(CW * scale)), max(2, int(CH * scale))
        self._new_mode((w, h), pygame.NOFRAME, title)
        self.fullscreen = True
        try:
            import ctypes

            hwnd = pygame.display.get_wm_info().get("window")
            x, y = (sw - w) // 2, (sh - h) // 2
            ctypes.windll.user32.MoveWindow(hwnd, x, y, w, h, True)
            set_topmost()
        except Exception:
            pass
        pygame.mouse.set_visible(True)

    def present(self):
        if self.screen is None:
            return
        w, h = self.screen.get_size()
        cw, ch = self.canvas.get_size()
        scale = min(w / cw, h / ch)
        dst = (max(1, int(cw * scale)), max(1, int(ch * scale)))
        if dst == (cw, ch):
            scaled = self.canvas
        else:
            scaled = pygame.transform.smoothscale(self.canvas, dst)
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, ((w - dst[0]) // 2, (h - dst[1]) // 2))
        pygame.display.flip()

    def close(self):
        try:
            pygame.display.quit()
        except Exception:
            pass
        self.screen = None


def poll_quit(events):
    for e in events:
        if e.type == pygame.QUIT:
            raise QuitGame()
        if e.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if e.key == pygame.K_ESCAPE:
                raise QuitGame()
            if e.key == pygame.K_q and (mods & pygame.KMOD_CTRL):
                raise QuitGame()


# --------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Windows-10-style toast for the prank + the "thanks" takeover screen.

Spliced into main.py by tools/splice_prank.py, so it relies on main's globals
(pygame, os, random, time, ASSETS, asset, clamp, App).
"""

# --------------------------------------------------------------------------
# PRANK — Windows 10 style toast notification (pure pygame)
# --------------------------------------------------------------------------
TOAST_W, TOAST_H = 500, 428
TOAST_KEY = (255, 0, 255)
C_BG = (31, 31, 31)
C_EDGE = (59, 59, 59)
C_TXT = (245, 245, 245)
C_DIM = (168, 168, 168)
C_FAINT = (111, 111, 111)
C_ACCENT = (76, 194, 255)
C_GREEN = (110, 231, 168)
C_BTN = (40, 40, 40)
C_BTN_HOVER = (52, 52, 52)


def rr(surf, color, rect, radius, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)


class ToastButton:
    def __init__(self, rect, label, color, size=14):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.size = size
        self.hover = False

    def draw(self, surf, font="segoe"):
        rr(surf, C_BTN_HOVER if self.hover else C_BTN, self.rect, 4)
        pygame.draw.rect(surf, (65, 65, 65), self.rect, 1, border_radius=4)
        text(
            surf,
            self.label,
            self.size,
            self.color,
            self.rect.center,
            anchor="center",
            font=font,
        )

    def shrink(self, label):
        self.label = label
        self.size = 9
        f = get_font("segoe", self.size)
        w = f.size(label)[0] + 22
        self.rect.width = max(42, w)
        self.rect.height = 24


class ToastScreen:
    """Fake system notification; slides in from the bottom-right."""

    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.done = False
        self.result = None
        self.hover_count = 0
        self.hover_t = 0.0
        self.scan_t = 0.0
        self.scan_stage = 0
        self.found = ""
        self.hint = ""
        self.closing = 0.0
        self.icon = None
        self.logo = None
        try:
            p = asset("logo_white.png")
            if os.path.exists(p):
                self.logo = pygame.transform.smoothscale(
                    pygame.image.load(p).convert_alpha(), (22, 22)
                )
        except Exception:
            self.logo = None

        self.yes = ToastButton((26, TOAST_H - 46, 152, 34), "Да, во имя AGI", C_ACCENT)
        self.no = ToastButton(
            (196, TOAST_H - 46, 176, 34), "Нет, это моя память!", C_TXT
        )
        self.body = (
            "Из вашего ПК будет выпаян 1 ГБ ОЗУ специальным агентом OpenAI "
            "ради дата-центров Сэма Альтмана. Вы даже не заметите разницу в "
            "Chrome и Word, а ОЗУ пойдёт на пользу Сэму."
        )
        self.surf = pygame.Surface((TOAST_W, TOAST_H), pygame.SRCALPHA)
        self.slide = 0.0

    def update(self, dt, events):
        self.t += dt
        self.slide = 1.0

        if self.t > 0.55 and self.scan_stage < 26:
            self.scan_t += dt
            if self.scan_t > 0.06:
                self.scan_t = 0.0
                self.scan_stage += 1
                if self.scan_stage == 17:
                    self.found = ""
                if self.scan_stage >= 26:
                    self.found = "✔  Найдено 33 ГБ. Рекомендуется пожертвовать 1 ГБ."

        mp = pygame.mouse.get_pos()
        self.yes.hover = self.yes.rect.collidepoint(mp)
        over_no = self.no.rect.collidepoint(mp)
        if over_no:
            if not self.no.hover and self.t - self.hover_t > 0.3:
                self.no_hover()
            self.hover_t = self.t
        self.no.hover = over_no

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.yes.rect.collidepoint(e.pos):
                    self.app.audio.play("click", 0.9)
                    self.result = "yes"
                    self.done = True
                elif self.no.rect.collidepoint(e.pos):
                    if self.hover_count >= 3:
                        self.app.audio.play("click", 0.9)
                        self.result = "no"
                        self.done = True
                    else:
                        self.app.audio.play("error", 0.4)
                        self.hover_t = 0.0
                        self.jump_no()
                elif pygame.Rect(TOAST_W - 44, 12, 34, 34).collidepoint(e.pos):
                    self.result = "no"
                    self.done = True

    def no_hover(self):
        self.hover_count += 1
        if self.hover_count == 1:
            self.app.audio.play("whoosh", 0.75)
            self.jump_no()
            self.hint = "кнопка недоступна"
        elif self.hover_count == 2:
            self.app.audio.play("error", 0.45)
            self.no.shrink("нет, это моя память!")
            self.jump_no()
            self.hint = "кнопка повреждена"
        else:
            self.app.audio.play("tabs", 0.5)
            self.no.shrink("нет")
            self.no.rect.topleft = (TOAST_W - 26 - self.no.rect.width, TOAST_H - 42)
            self.hint = ""

    def jump_no(self):
        w, h = self.no.rect.size
        x = random.randint(22, max(24, TOAST_W - w - 22))
        y = random.randint(300, max(302, TOAST_H - h - 76))
        self.no.rect.topleft = (x, y)

    def draw(self):
        c = self.app.display.canvas
        c.fill(TOAST_KEY if self.app.display.layered else (24, 24, 26))
        s = c
        rr(s, C_BG, (0, 0, TOAST_W, TOAST_H), 9)
        pygame.draw.rect(s, C_EDGE, (0, 0, TOAST_W, TOAST_H), 2, border_radius=9)

        # header
        rr(s, (29, 138, 95), (13, 19, 30, 30), 7)
        pygame.draw.rect(s, (38, 168, 116), (13, 19, 30, 30), 1, border_radius=7)
        if self.logo:
            s.blit(self.logo, (17, 23))
        text(s, "СЛУЖБА ОПТИМИЗАЦИИ OPENAI AGI", 12, C_DIM, (52, 24), font="segoe")
        text(
            s, "системное уведомление · только что", 11, C_FAINT, (52, 42), font="segoe"
        )
        cx, cy = TOAST_W - 27, 33
        pygame.draw.line(s, C_DIM, (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
        pygame.draw.line(s, C_DIM, (cx - 6, cy + 6), (cx + 6, cy - 6), 2)
        pygame.draw.line(s, (51, 51, 51), (16, 62), (TOAST_W - 16, 62))

        # title + body
        text(s, "Внимание!", 17, C_TXT, (22, 78), font="segoeb")
        yy = 106
        for line in wrap("segoe", 13, self.body, TOAST_W - 44):
            text(s, line, 13, (214, 214, 214), (22, yy), font="segoe")
            yy += 18

        # scan
        text(
            s,
            [
                "Сканирую оперативную память…",
                "Сканирую оперативную память…",
                "Анализ конфигурации…",
                "Обнаружено 33 ГБ ОЗУ. Избыточно.",
                "Проверка завершена",
            ][min(4, self.scan_stage // 8)],
            11,
            (141, 141, 141),
            (22, 208),
            font="segoe",
        )
        pygame.draw.rect(s, (45, 45, 45), (22, 226, TOAST_W - 44, 5), border_radius=3)
        frac = self.scan_stage / 26.0
        if frac > 0:
            pygame.draw.rect(
                s, C_ACCENT, (22, 228, int((TOAST_W - 44) * frac), 5), border_radius=3
            )
        if self.found:
            text(s, self.found, 13, C_GREEN, (22, 240), font="segoe")

        # question
        qy = 292
        for line in wrap(
            "segoeb",
            15,
            "Пожертвовать 1 ГБ оперативной памяти Сэму Альтману?",
            TOAST_W - 44,
        ):
            text(s, line, 15, C_TXT, (22, qy), font="segoeb")
            qy += 21

        # footer
        pygame.draw.line(
            s, (51, 51, 51), (16, TOAST_H - 62), (TOAST_W - 16, TOAST_H - 62)
        )
        self.yes.draw(s)
        self.no.draw(s)
        if self.hint:
            text(
                s,
                self.hint,
                11,
                C_FAINT,
                (TOAST_W - 22, TOAST_H - 29),
                anchor="midright",
                font="segoe",
            )
        c.blit(s, (0, 0))

    def window_rect(self, sw, sh):
        x = sw - TOAST_W - 24
        y = sh - TOAST_H - 76
        k = 1 - (1 - self.slide) ** 3
        x = int(sw + 12 + (x - (sw + 12)) * k)
        return pygame.Rect(x, y, TOAST_W, TOAST_H)


# --------------------------------------------------------------------------
# THANKS — full-screen takeover, dismissed only by holding A + G + I
# --------------------------------------------------------------------------
class ThanksScreen:
    HOLD = 0.35

    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.done = False
        self.held = set()
        self.hold_t = 0.0
        self.hint_a = 0.0
        self.bg = pygame.image.load(asset("thanks_wall.png")).convert()
        self.hold_bar = 0.0

    def update(self, dt, events):
        self.t += dt
        keys = pygame.key.get_pressed()
        need = {pygame.K_a: "a", pygame.K_g: "g", pygame.K_i: "i"}
        active = {v for k, v in need.items() if keys[k]}
        if active == {"a", "g", "i"}:
            self.hold_t += dt
            self.hold_bar = clamp(self.hold_t / self.HOLD, 0, 1)
            if self.hold_t >= self.HOLD:
                self.done = True
        else:
            self.hold_t = 0.0
            self.hold_bar = max(0.0, self.hold_bar - dt * 3)
        self.hint_a = clamp((self.t - 5.0) / 1.5, 0, 1)

    def draw(self):
        c = self.app.display.canvas
        c.blit(self.bg, (0, 0))
        if self.hint_a > 0:
            a = int(120 * self.hint_a)
            text(
                c,
                "удерживайте  A + G + I,  чтобы закрыть",
                15,
                (26, 74, 56),
                (CW // 2, CH - 30),
                anchor="center",
                font="segoe",
                alpha=a,
            )
            if self.hold_bar > 0:
                w = 260
                pygame.draw.rect(
                    c, (16, 46, 34), (CW // 2 - w // 2, CH - 22, w, 4), border_radius=2
                )
                pygame.draw.rect(
                    c,
                    (70, 210, 150),
                    (CW // 2 - w // 2, CH - 22, int(w * self.hold_bar), 4),
                    border_radius=2,
                )


# --------------------------------------------------------------------------
# FIGHT
# --------------------------------------------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "grav")

    def __init__(self, x, y, vx, vy, life, color, size, grav=900):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.color, self.size, self.grav = color, size, grav


class FightScreen:
    FLOOR = 608

    def __init__(self, app, round_no=1, overlay=False, desktop=None):
        self.app = app
        self.round_no = round_no
        self.overlay = overlay
        self.t = 0.0
        self.result = None
        self.music_started = False
        self.over = False

        if overlay:
            self.bg = desktop or grab_desktop_surface() or fake_desktop_surface()
        else:
            self.bg = None
        if self.bg is None:
            self.bg = pygame.image.load(asset("arena_bg.png")).convert()
        self.stage = self.build_stage() if overlay else None
        self.dim = None
        if overlay:
            self.dim = pygame.Surface((CW, CH))
            self.dim.fill((3, 5, 8))
            self.dim.set_alpha(96)
        self.pc_img = pygame.image.load(asset("pc.png")).convert_alpha()
        _si = pygame.image.load(asset("sam_fight.png")).convert_alpha()
        _sh = 384
        self.sam_img = pygame.transform.smoothscale(
            _si, (int(_si.get_width() * _sh / _si.get_height()), _sh)
        )
        self.sam_white = self.sam_img.copy()
        self.sam_white.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
        self.pc_white = self.pc_img.copy()
        self.pc_white.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
        self.rack = pygame.image.load(asset("server_rack.png")).convert_alpha()
        self.rack = pygame.transform.smoothscale(
            self.rack,
            (int(self.rack.get_width() * 0.84), int(self.rack.get_height() * 0.84)),
        )
        self.coin = pygame.image.load(asset("coin20.png")).convert_alpha()
        self.chrome = pygame.image.load(asset("chrome_win.png")).convert_alpha()
        self.avatar = pygame.image.load(asset("sam_avatar.png")).convert_alpha()
        self.avatar = pygame.transform.smoothscale(self.avatar, (72, 72))
        self.ram_icon = pygame.image.load(asset("ram_icon.png")).convert_alpha()

        self.player = {
            "x": 330.0,
            "hp": 100.0,
            "maxhp": 100.0,
            "ghost": 100.0,
            "face": 1,
            "atk": 0.0,
            "atk_cd": 0.0,
            "special_cd": 0.0,
            "hurt": 0.0,
            "lunge": 0.0,
            "dead": False,
            "dash": 0.0,
            "vx": 0.0,
        }
        self.sam = {
            "x": 970.0,
            "hp": 100.0,
            "maxhp": 100.0,
            "ghost": 100.0,
            "atk_cd": 1.2,
            "hurt": 0.0,
            "stun": 0.0,
            "dead": False,
            "pose": "idle",
            "bob": 0.0,
            "blink": 0.0,
            "rise": 0.0,
            "vy": 0.0,
            "x0": 970.0,
        }
        if round_no == 2:
            self.player["hp"] = self.player["maxhp"] = self.player["ghost"] = 140.0
            self.sam["hp"] = self.sam["maxhp"] = self.sam["ghost"] = 100.0

        self.projectiles = []
        self.tabs = []
        self.particles = []
        self.damage_text = []
        self.shake_t = 0.0
        self.shake_mag = 0.0
        self.flash = 0.0
        self.flash_color = (255, 255, 255)
        self.mode = "intro"
        self.mode_t = 0.0
        self.phase = None
        self.phase_t = 0.0
        self.rack_y = -700.0
        self.rack_x = 0.0
        self.combo = 0
        self.combo_t = 0.0
        self.intro_step = 0
        self.dodge_window = 0.0
        self.dodge_used = False
        self.rack_ready = 0.0
        self.sam_taunt = ""
        self.sam_taunt_t = 0.0
        self.fight_start = 0.0
        self.scan = scanline_surface(CW, CH, 16, 4)
        self.vign = vignette_surface(CW, CH, 120)
        self.logo = pygame.image.load(asset("logo_green.png")).convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (90, 90))

    # helpers --------------------------------------------------------------
    def say(self, txt, dur=1.6):
        self.sam_taunt = txt
        self.sam_taunt_t = dur

    def burst(
        self,
        x,
        y,
        n=18,
        colors=((255, 220, 120), (255, 150, 60), (255, 255, 255)),
        speed=420,
        life=0.6,
        size=(2, 5),
        grav=900,
    ):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(speed * 0.3, speed)
            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(a) * v,
                    math.sin(a) * v - 120,
                    random.uniform(life * 0.5, life),
                    random.choice(colors),
                    random.randint(*size),
                    grav,
                )
            )

    def dmg(self, target, amount, x=None, y=None, big=False, color=(255, 235, 120)):
        d = self.player if target == "player" else self.sam
        d["hp"] = max(0.0, d["hp"] - amount)
        d["hurt"] = 0.22
        self.damage_text.append(
            {
                "x": x if x is not None else d["x"] + random.randint(-24, 24),
                "y": y if y is not None else 330 + random.randint(-30, 10),
                "t": 0.0,
                "life": 0.9 if not big else 1.6,
                "txt": str(int(amount)) if not big else str(int(amount)),
                "size": 40 if not big else 96,
                "color": color,
            }
        )
        if target == "sam":
            self.combo += 1
            self.combo_t = 1.1

    def shake(self, mag, dur):
        self.shake_mag = mag
        self.shake_t = self.shake_dur = dur

    # update ---------------------------------------------------------------
    def update(self, dt, events):
        self.t += dt
        self.mode_t += dt
        for e in events:
            if e.type == pygame.KEYDOWN:
                if (
                    e.key in (pygame.K_SPACE, pygame.K_RETURN)
                    and self.mode == "intro"
                    and self.mode_t > 0.4
                ):
                    self.start_fight()
                elif self.mode == "cutscene":
                    if e.key == pygame.K_SPACE and self.phase == "r2_cue":
                        self.do_dodge()
                elif self.mode == "fight":
                    if e.key == pygame.K_SPACE:
                        self.player_attack()
                    elif e.key == pygame.K_f:
                        self.player_special()
                if (
                    e.key == pygame.K_SPACE
                    and self.mode == "over"
                    and self.mode_t > 1.2
                ):
                    self.result = "won" if self.round_no == 2 else "lost"

        self.shake_t = max(0.0, self.shake_t - dt)
        self.flash = max(0.0, self.flash - dt * 3.2)
        self.combo_t -= dt
        if self.combo_t <= 0:
            self.combo = 0
        self.sam_taunt_t = max(0.0, self.sam_taunt_t - dt)

        for p in self.particles:
            p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.grav * dt
        for d in self.damage_text:
            d["t"] += dt
            d["y"] -= 60 * dt
        self.damage_text = [d for d in self.damage_text if d["t"] < d["life"]]

        if self.mode == "intro":
            self.update_intro(dt)
        elif self.mode == "fight":
            self.update_fight(dt)
        elif self.mode == "cutscene":
            self.update_cutscene(dt)
        elif self.mode == "over":
            self.update_over(dt)

        for d in (self.player, self.sam):
            if d["ghost"] > d["hp"]:
                d["ghost"] = max(d["hp"], d["ghost"] - 55 * dt)
            d["hurt"] = max(0.0, d["hurt"] - dt)
        self.sam["bob"] += dt

    def update_intro(self, dt):
        if not self.music_started and self.mode_t > 0.05:
            self.music_started = True
            self.app.audio.play("gong", 0.9)
            self.app.audio.music("mk_theme", 0.42)
            if self.round_no == 1:
                self.app.audio.play("vo_mkannounce_fx", 1.0)
            else:
                self.app.audio.play("vo_round2announce_fx", 0.9)
        if self.mode_t > 1.5 and self.intro_step == 0:
            self.intro_step = 1
            self.app.audio.play("gong", 0.7)
            self.app.audio.play("vo_fight", 0.9)
        if self.mode_t > 3.4:
            self.start_fight()

    def start_fight(self):
        self.mode = "fight"
        self.mode_t = 0.0
        self.fight_start = self.t
        if self.round_no == 2:
            self.app.audio.play("vo_round2", 0.95)
            self.say("Реванш? Твоя память уже в Калифорнии.", 2.4)

    def player_attack(self):
        p = self.player
        if p["atk_cd"] > 0 or p["dead"]:
            return
        p["atk"] = 0.34
        p["atk_cd"] = 0.36
        p["lunge"] = 1.0
        self.app.audio.play("whoosh", 0.45)
        dist = self.sam["x"] - p["x"]
        if dist < 245:
            dmg = random.randint(9, 13)
            self.dmg("sam", dmg, self.sam["x"] - 30, 330)
            self.app.audio.play("hit", 0.9)
            self.burst(self.sam["x"] - 20, 360, 16)
            self.shake(7, 0.18)
            self.sam["stun"] = 0.12
            if self.sam["hp"] <= 0:
                self.ko_sam()
        else:
            self.say("Промах! Хром тормозит.", 1.0)

    def player_special(self):
        p = self.player
        if p["special_cd"] > 0 or p["dead"]:
            return
        p["special_cd"] = 5.5
        self.app.audio.play("tabs", 1.0)
        self.app.audio.play("whoosh", 0.7)
        sx = self.sam["x"]
        for i in range(7):
            self.tabs.append(
                {
                    "x": sx + random.randint(-150, 150),
                    "y": -200 - i * 80,
                    "vy": random.randint(520, 700),
                    "hit": False,
                    "rot": random.uniform(-18, 18),
                    "delay": i * 0.07,
                }
            )

    def update_fight(self, dt):
        p, s = self.player, self.sam
        keys = pygame.key.get_pressed()
        moving = 0
        if not p["dead"]:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moving -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moving += 1
        p["vx"] = moving * 330
        if p["atk"] <= 0:
            p["x"] = clamp(p["x"] + moving * 330 * dt, 120, 660)
        p["x"] += p["lunge"] * 120 * dt * (1 if p["atk"] > 0.2 else 0)
        p["lunge"] = max(0.0, p["lunge"] - dt * 3)
        p["atk"] = max(0.0, p["atk"] - dt)
        p["atk_cd"] = max(0.0, p["atk_cd"] - dt)
        p["special_cd"] = max(0.0, p["special_cd"] - dt)
        p["hit_anim"] = 0

        # Sam AI
        s["atk_cd"] -= dt
        s["stun"] = max(0.0, s["stun"] - dt)
        dist = s["x"] - p["x"]
        if s["stun"] <= 0 and not s["dead"]:
            if dist > 470:
                s["x"] -= 150 * dt
            elif dist < 250:
                s["x"] += 130 * dt
            s["x"] = clamp(s["x"], 700, 1165)
        s["pose"] = "summon" if s["stun"] > 0 else "idle"
        if s["atk_cd"] <= 0 and s["stun"] <= 0 and not s["dead"] and not p["dead"]:
            if dist < 250:
                self.sam_melee()
                s["atk_cd"] = random.uniform(1.5, 2.4)
            else:
                if random.random() < 0.62:
                    self.sam_coin()
                else:
                    self.sam_laser()
                s["atk_cd"] = random.uniform(1.5, 2.5)
            if random.random() < 0.25:
                self.say(
                    random.choice(
                        [
                            "Это ради AGI!",
                            "Ещё один гигабайт!",
                            "Не сопротивляйся.",
                            "$20 — и память ваша.",
                        ]
                    ),
                    1.4,
                )

        # projectiles
        for pr in list(self.projectiles):
            pr["x"] += pr["vx"] * dt
            pr["t"] += dt
            pr["rot"] += pr["spin"] * dt
            if pr["kind"] == "coin":
                r = pygame.Rect(0, 0, 46, 46)
                r.center = (int(pr["x"]), int(pr["y"]))
                if not pr["hit"] and r.colliderect(
                    pygame.Rect(p["x"] - 70, self.FLOOR - 300, 140, 300)
                ):
                    pr["hit"] = True
                    pr["dead"] = True
                    self.dmg("player", random.randint(7, 10), p["x"], 340)
                    self.app.audio.play("coin", 0.8)
                    self.burst(pr["x"], pr["y"], 12, [(255, 220, 120), (80, 230, 160)])
                    self.shake(5, 0.15)
            elif pr["kind"] == "laser_charge":
                if pr["t"] > 0.72:
                    pr["kind"] = "laser"
                    pr["t"] = 0.0
                    self.app.audio.play("laser", 0.9)
                    if abs(p["x"] - pr["x"]) < 78 and pr["y"] > 300:
                        self.dmg("player", random.randint(11, 14), p["x"], 340)
                        self.shake(8, 0.2)
                    else:
                        self.say("Увернулся? Просто галочка в логах.", 1.2)
            elif pr["kind"] == "laser":
                if pr["t"] > 0.3:
                    pr["dead"] = True
            if pr["x"] < -100 or pr["x"] > CW + 100:
                pr["dead"] = True
        self.projectiles = [p_ for p_ in self.projectiles if not p_.get("dead")]

        # chrome tabs rain
        for tb in list(self.tabs):
            if tb["delay"] > 0:
                tb["delay"] -= dt
                continue
            tb["y"] += tb["vy"] * dt
            if tb["y"] > 470 and not tb["hit"]:
                tb["hit"] = True
                if abs(tb["x"] - s["x"]) < 190:
                    self.dmg("sam", 5, tb["x"], 330)
                    self.app.audio.play("hit", 0.45)
                    self.burst(
                        tb["x"],
                        420,
                        8,
                        [(200, 210, 225), (255, 255, 255)],
                        300,
                        0.4,
                        (2, 4),
                    )
                self.shake(4, 0.1)
            if tb["y"] > 760:
                tb["dead"] = True
        self.tabs = [tb for tb in self.tabs if not tb.get("dead")]

        # scripted rack
        if self.round_no == 1:
            if s["hp"] <= 25 and self.phase is None and not self.over:
                self.start_r1_cutscene()
        else:
            if (
                s["hp"] <= 25
                and self.phase is None
                and self.t > self.rack_ready
                and not self.over
            ):
                self.start_r2_cutscene()

        if p["hp"] <= 0 and not p["dead"] and not self.over:
            self.player_die()

    def sam_melee(self):
        p = self.player
        dmg = random.randint(9, 13)
        if not p["dead"]:
            self.dmg("player", dmg, p["x"], 340)
            self.app.audio.play("hit", 0.9)
            self.burst(p["x"], 380, 14, [(255, 120, 90), (255, 220, 150)])
            self.shake(9, 0.2)
            self.say("Удар паяльником!", 1.0)
            p["atk"] = 0.0

    def sam_coin(self):
        s = self.sam
        self.projectiles.append(
            {
                "kind": "coin",
                "x": s["x"] - 90,
                "y": 330,
                "vx": -620,
                "t": 0.0,
                "rot": 0.0,
                "spin": 540,
                "hit": False,
            }
        )
        self.app.audio.play("coin", 0.55)

    def sam_laser(self):
        s = self.sam
        self.projectiles.append(
            {
                "kind": "laser_charge",
                "x": self.player["x"],
                "y": 330,
                "vx": 0,
                "t": 0.0,
                "rot": 0,
                "spin": 0,
                "hit": False,
            }
        )
        self.say("Лазер выпайки!", 1.0)

    def ko_sam(self):
        s = self.sam
        s["dead"] = True
        self.app.audio.play("crowd", 0.8)
        self.app.audio.play("clang", 0.8)
        self.burst(
            s["x"], 360, 40, [(255, 200, 100), (255, 80, 80), (255, 255, 255)], 600, 1.2
        )
        self.shake(16, 0.5)
        if self.round_no == 1:
            self.over = True
            self.result = "lost"
        else:
            self.victory_sequence()

    def player_die(self):
        self.player["dead"] = True
        self.over = True
        self.mode = "over"
        self.mode_t = 0.0
        self.result = "lost"
        self.app.audio.play("boom", 1.0)
        self.shake(20, 0.7)
        self.flash = 1.0
        self.flash_color = (255, 90, 60)

    def update_over(self, dt):
        pass

    # round 1 scripted loss ------------------------------------------------
    def start_r1_cutscene(self):
        self.mode = "cutscene"
        self.mode_t = 0.0
        self.phase = "r1_call"
        self.phase_t = 0.0
        self.rack_y = -760.0
        self.rack_x = self.player["x"]
        self.sam["atk_cd"] = 99
        self.sam["pose"] = "summon"
        self.app.audio.stop_music(600)
        self.app.audio.play("vo_rack_fx", 1.0)
        self.say("ВЫЗЫВАЮ СЕРВЕРНУЮ СТОЙКУ!", 2.6)

    def start_r2_cutscene(self):
        self.mode = "cutscene"
        self.mode_t = 0.0
        self.phase = "r2_cue"
        self.phase_t = 0.0
        self.rack_y = -760.0
        self.rack_x = self.player["x"]
        self.dodge_window = 2.9
        self.dodge_used = False
        self.sam["atk_cd"] = 99
        self.sam["pose"] = "summon"
        self.app.audio.play("vo_rack_fx", 1.0)
        self.say("ВЫЗЫВАЮ СЕРВЕРНУЮ СТОЙКУ!", 2.2)

    def do_dodge(self):
        if self.phase != "r2_cue" or self.dodge_used:
            return
        self.dodge_used = True
        self.phase = "r2_dodge"
        self.phase_t = 0.0
        self.player["dash"] = 1.0
        self.app.audio.play("whoosh", 1.0)
        self.player["x"] = clamp(self.player["x"] - 300, 110, 660)
        self.shake(6, 0.2)

    def update_cutscene(self, dt):
        self.phase_t += dt
        s, p = self.sam, self.player
        if self.phase == "r1_call":
            s["pose"] = "summon"
            self.rack_y = lerp(-760, -730, min(1, self.phase_t / 2.2))
            if self.phase_t > 2.3:
                self.phase = "r1_fall"
                self.phase_t = 0.0
                self.app.audio.play("whoosh", 0.9)
        elif self.phase == "r1_fall":
            t = clamp(self.phase_t / 0.85, 0, 1)
            self.rack_y = lerp(-730, 96, ease_in_out(t) ** 2.1)
            self.shake(6, 0.1)
            if t >= 1:
                self.phase = "r1_impact"
                self.phase_t = 0.0
                self.app.audio.play("boom", 1.0)
                self.shake(26, 0.9)
                self.flash = 1.0
                self.flash_color = (255, 255, 255)
                p["hp"] = 0.0
                p["dead"] = True
                self.damage_text.append(
                    {
                        "x": p["x"],
                        "y": 300,
                        "t": 0.0,
                        "life": 1.9,
                        "txt": "9999",
                        "size": 104,
                        "color": (255, 90, 80),
                    }
                )
                self.burst(
                    p["x"],
                    520,
                    60,
                    [(255, 210, 120), (255, 120, 60), (220, 220, 220)],
                    800,
                    1.6,
                )
        elif self.phase == "r1_impact":
            if self.phase_t > 1.6 and not self.over:
                self.over = True
                self.mode = "over"
                self.mode_t = 0.0
                self.result = "lost"
                self.app.audio.play("crowd", 0.25)
        elif self.phase == "r2_cue":
            self.dodge_window -= dt
            t = clamp(self.phase_t / 2.9, 0, 1)
            self.rack_y = lerp(-760, -10, ease_out(t))
            if self.dodge_window <= 0:
                self.phase = "r2_miss"
                self.phase_t = 0.0
                self.app.audio.play("boom", 1.0)
                self.shake(24, 0.8)
                self.flash = 1.0
                self.flash_color = (255, 120, 90)
                self.dmg("player", 55, p["x"], 320, big=True)
                self.burst(p["x"], 520, 50, [(255, 200, 120), (255, 110, 70)], 700, 1.3)
                self.say("Ха-ха-ха. Слабый компьютер.", 2.0)
                self.app.audio.play("vo_laugh", 0.9)
        elif self.phase == "r2_miss":
            if self.phase_t > 2.4:
                self.phase = None
                self.mode = "fight"
                self.mode_t = 0.0
                self.rack_ready = self.t + 3.0
                self.sam["atk_cd"] = 1.4
                self.sam["pose"] = "idle"
                self.player["hp"] = max(self.player["hp"], 12)
                self.player["ghost"] = self.player["hp"]
        elif self.phase == "r2_dodge":
            t = clamp(self.phase_t / 0.45, 0, 1)
            self.rack_y = lerp(self.rack_y, 96, ease_out(t) ** 1.6)
            if t >= 1:
                self.phase = "r2_fatality"
                self.phase_t = 0.0
                self.app.audio.play("boom", 1.0)
                self.app.audio.play("explosion", 0.9)
                self.shake(28, 1.0)
                self.flash = 1.0
                self.burst(
                    self.rack_x, 520, 60, [(255, 210, 120), (160, 255, 210)], 800, 1.5
                )
                self.dmg("sam", 75, s["x"], 300, big=True)
                s["dead"] = True
                s["pose"] = "hurt"
        elif self.phase == "r2_fatality":
            if self.phase_t > 0.6:
                self.phase = "r2_combo"
                self.phase_t = 0.0
                self.app.audio.play("clang", 1.0)
                self.app.audio.play("vo_fatality_fx", 1.0)
                self.shake(18, 0.7)
                self.flash = 1.0
                self.flash_color = (220, 255, 240)
                self.burst(
                    s["x"],
                    330,
                    70,
                    [(140, 255, 190), (255, 255, 255), (255, 210, 120)],
                    900,
                    1.6,
                )
        elif self.phase == "r2_combo":
            if self.phase_t > 3.2:
                self.mode = "over"
                self.mode_t = 0.0
                self.result = "won"
                self.over = True

    def victory_sequence(self):
        self.mode = "cutscene"
        self.mode_t = 0.0
        self.phase = "r2_fatality"
        self.phase_t = 0.0
        self.over = True
        self.result = "won"

    # draw -----------------------------------------------------------------
    def build_stage(self):
        """Translucent arena laid over the frozen desktop screenshot."""
        s = pygame.Surface((CW, CH), pygame.SRCALPHA)
        for i in range(170):
            a = int(150 * (i / 170) ** 1.6)
            pygame.draw.rect(s, (3, 6, 9, a), (0, 540 + i, CW, 1))
        for cx, col in ((330, (70, 240, 200)), (970, (255, 190, 90))):
            for r in range(300, 0, -10):
                a = int(16 * (1 - r / 300) ** 1.5)
                pygame.draw.circle(s, col + (a,), (cx, 560), r)
        for w, a in ((22, 18), (12, 34), (5, 70), (2, 150)):
            pygame.draw.line(s, (80, 255, 175, a), (0, self.FLOOR), (CW, self.FLOOR), w)
        pygame.draw.line(
            s, (255, 255, 255, 60), (0, self.FLOOR - 1), (CW, self.FLOOR - 1), 1
        )
        return s

    def draw(self):
        c = self.app.display.canvas
        world = pygame.Surface((CW, CH)).convert()
        shake_x = shake_y = 0
        if self.shake_t > 0:
            k = self.shake_t / max(self.shake_dur, 0.001)
            shake_x = int(random.uniform(-1, 1) * self.shake_mag * k)
            shake_y = int(random.uniform(-1, 1) * self.shake_mag * k)

        world.blit(self.bg, (shake_x, shake_y))
        if self.dim is not None:
            world.blit(self.dim, (0, 0))
        if self.stage is not None:
            world.blit(self.stage, (shake_x, shake_y))
        self.draw_floorshadows(world, shake_x, shake_y)
        self.draw_rack(world, shake_x, shake_y)
        self.draw_sam(world, shake_x, shake_y)
        self.draw_player(world, shake_x, shake_y)
        self.draw_projectiles(world, shake_x, shake_y)
        self.draw_tabs(world, shake_x, shake_y)
        self.draw_particles(world, shake_x, shake_y)

        c.blit(world, (0, 0))
        c.blit(self.scan, (0, 0))
        c.blit(self.vign, (0, 0))
        self.draw_damage_text(c)
        self.draw_hud(c)
        self.draw_overlays(c)

        if self.flash > 0:
            ov = pygame.Surface((CW, CH))
            ov.fill(self.flash_color)
            ov.set_alpha(int(200 * clamp(self.flash, 0, 1)))
            c.blit(ov, (0, 0))

    def draw_floorshadows(self, s, dx, dy):
        for x, w in ((self.player["x"], 120), (self.sam["x"], 135)):
            sh = pygame.Surface((w, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
            s.blit(sh, (x - w // 2 + dx, self.FLOOR - 14 + dy))

    def draw_player(self, s, dx, dy):
        p = self.player
        img = self.pc_img
        x = p["x"] + dx
        y = self.FLOOR + dy
        ang = 0
        if p["dead"]:
            ang = -74
        elif p["hurt"] > 0:
            ang = 7
        elif p["atk"] > 0:
            ang = -5
        if p["dash"] > 0:
            p["dash"] = max(0.0, p["dash"] - 0.06)
            for i in range(3):
                ghost = img.copy()
                ghost.set_alpha(50 - i * 12)
                s.blit(ghost, ghost.get_rect(midbottom=(x + 40 + i * 26, y)))
        if ang:
            img = pygame.transform.rotate(img, ang)
        bob = math.sin(self.sam["bob"] * 2.6) * 3 if not p["dead"] else 0
        rect = img.get_rect(midbottom=(x, y + bob))
        s.blit(img, rect)
        if p["hurt"] > 0:
            g = self.pc_white.copy()
            g.set_alpha(int(230 * (p["hurt"] / 0.22)))
            s.blit(pygame.transform.rotate(g, ang) if ang else g, rect)
        # punch spark
        if p["atk"] > 0.2:
            px = x + 120
            for i in range(3):
                pygame.draw.arc(
                    s,
                    (255, 235, 170),
                    (px - 20 - i * 8, 360 - i * 12, 70, 60),
                    0.4,
                    2.2,
                    3,
                )

    def draw_sam(self, s, dx, dy):
        sm = self.sam
        img = self.sam_img
        x = sm["x"] + dx
        y = self.FLOOR + dy + math.sin(sm["bob"] * 2.2) * 5
        if sm["dead"]:
            if self.phase in ("r2_fatality", "r2_combo"):
                # blasted away
                off = (
                    min(1.0, self.phase_t / 0.6) if self.phase == "r2_fatality" else 1.0
                )
                ang = -80 * off
                img = pygame.transform.rotate(img, ang)
                x += 260 * off
                y -= 180 * off
            else:
                img = pygame.transform.rotate(img, -78)
                y += 40
        elif sm["hurt"] > 0:
            img = pygame.transform.rotate(img, 6)
        elif sm["pose"] == "summon":
            glow = pygame.Surface((420, 420), pygame.SRCALPHA)
            pygame.draw.circle(glow, (60, 255, 160, 40), (210, 210), 190)
            pygame.draw.circle(glow, (60, 255, 160, 30), (210, 210), 150)
            s.blit(glow, (x - 210, y - 430))
            img = pygame.transform.scale(
                img, (int(img.get_width() * 1.05), int(img.get_height() * 1.05))
            )
        rect = img.get_rect(midbottom=(x, y))
        s.blit(img, rect)
        if sm["hurt"] > 0 and not sm["dead"]:
            g = self.sam_white.copy()
            g.set_alpha(int(230 * (sm["hurt"] / 0.22)))
            s.blit(g, g.get_rect(midbottom=(x, y)))
        if sm["taunt"] if "taunt" in sm else False:
            pass

    def draw_rack(self, s, dx, dy):
        if self.rack_y < -600:
            return
        r = self.rack
        x = self.rack_x + dx + 130 - r.get_width() // 2
        y = int(self.rack_y) + dy
        # motion streaks
        if self.mode == "cutscene" and self.phase in ("r1_fall", "r2_cue", "r2_dodge"):
            for i in range(4):
                pygame.draw.line(
                    s, (60, 255, 170, 40), (x + i * 60, y - 200), (x + i * 60, y), 2
                )
        s.blit(r, (x, y))

    def draw_projectiles(self, s, dx, dy):
        for pr in self.projectiles:
            if pr["kind"] == "coin":
                img = pygame.transform.rotate(self.coin, pr["rot"])
                s.blit(img, img.get_rect(center=(pr["x"] + dx, pr["y"] + dy)))
            elif pr["kind"] == "laser_charge":
                a = 0.4 + 0.6 * abs(math.sin(pr["t"] * 18))
                col = (255, int(80 + 100 * a), 80)
                pygame.draw.circle(
                    s, col, (int(pr["x"] + dx), 470 + dy), int(12 + 10 * a), 3
                )
                pygame.draw.circle(s, (255, 60, 60), (int(pr["x"] + dx), 470 + dy), 4)
                pygame.draw.line(
                    s,
                    (255, 70, 70, 90),
                    (int(pr["x"] + dx), 300),
                    (int(pr["x"] + dx), 600),
                    2,
                )
            elif pr["kind"] == "laser":
                x0 = self.sam["x"] + dx - 100
                x1 = pr["x"] + dx
                yy = 470 + dy
                w = 10
                pygame.draw.line(s, (255, 60, 60), (x0, 360 + dy), (x1, yy), w + 8)
                pygame.draw.line(s, (255, 230, 230), (x0, 360 + dy), (x1, yy), w)
                glow = pygame.Surface((CW, CH), pygame.SRCALPHA)
                pygame.draw.line(
                    glow, (255, 90, 90, 90), (x0, 360 + dy), (x1, yy), w + 26
                )
                s.blit(glow, (0, 0))

    def draw_tabs(self, s, dx, dy):
        for tb in self.tabs:
            if tb["delay"] > 0:
                continue
            img = pygame.transform.rotate(self.chrome, tb["rot"])
            img = pygame.transform.smoothscale(img, (170, 118))
            s.blit(img, img.get_rect(center=(tb["x"] + dx, tb["y"] + dy)))

    def draw_particles(self, s, dx, dy):
        for p in self.particles:
            a = int(255 * clamp(p.life / p.max_life, 0, 1))
            col = (p.color[0], p.color[1], p.color[2], a)
            surf = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (p.size, p.size), p.size)
            s.blit(surf, (p.x + dx - p.size, p.y + dy - p.size))

    def draw_damage_text(self, c):
        for d in self.damage_text:
            a = int(255 * clamp(1 - d["t"] / d["life"], 0, 1))
            text(
                c,
                d["txt"],
                d["size"],
                d["color"],
                (d["x"], d["y"]),
                anchor="center",
                font="impact",
                outline=(20, 20, 24),
                alpha=a,
            )

    def draw_hud(self, c):
        p, sm = self.player, self.sam
        # top gradient
        grad = pygame.Surface((CW, 150), pygame.SRCALPHA)
        for i in range(150):
            pygame.draw.line(grad, (4, 6, 9, int(180 * (1 - i / 150))), (0, i), (CW, i))
        c.blit(grad, (0, 0))

        text(
            c,
            "СИСТЕМНЫЙ БЛОК",
            30,
            WHITE,
            (44, 30),
            font="impact",
            outline=(10, 12, 16),
        )
        bar(
            c,
            44,
            70,
            420,
            26,
            p["hp"] / p["maxhp"],
            hp_color(p["hp"] / p["maxhp"]),
            ghost=p["ghost"] / p["maxhp"],
        )
        text(
            c,
            "%d / %d" % (int(p["hp"]), int(p["maxhp"])),
            18,
            (230, 236, 244),
            (44, 104),
            font="consolab",
        )

        text(
            c,
            "СЭМ АЛЬТМАН",
            30,
            WHITE,
            (CW - 150, 30),
            anchor="topright",
            font="impact",
            outline=(10, 12, 16),
        )
        bar(
            c,
            CW - 150 - 420,
            70,
            420,
            26,
            sm["hp"] / sm["maxhp"],
            hp_color(sm["hp"] / sm["maxhp"]),
            flip=True,
            ghost=sm["ghost"] / sm["maxhp"],
        )
        text(
            c,
            "%d / %d" % (int(sm["hp"]), int(sm["maxhp"])),
            18,
            (230, 236, 244),
            (CW - 150, 104),
            anchor="topright",
            font="consolab",
        )
        c.blit(self.avatar, (CW - 44 - 72, 16))
        pygame.draw.circle(c, (60, 230, 160), (CW - 44 - 36, 16 + 36), 37, 2)

        # round / combo
        text(
            c,
            "ROUND %d" % self.round_no,
            22,
            (200, 210, 225),
            (CW // 2, 30),
            anchor="midtop",
            font="impact",
        )
        if self.combo > 1:
            text(
                c,
                "%d HITS" % self.combo,
                34,
                GOLD,
                (CW // 2, 66),
                anchor="midtop",
                font="impact",
                outline=(60, 30, 0),
            )
        # special cooldown
        sp = self.player["special_cd"]
        x0, y0 = 44, 140
        pygame.draw.rect(c, (12, 16, 22), (x0, y0, 176, 30), border_radius=6)
        pygame.draw.rect(c, (24, 28, 36), (x0 + 2, y0 + 2, 172, 26), border_radius=5)
        frac = 1 - sp / 5.5
        pygame.draw.rect(
            c,
            (255, 205, 90) if sp <= 0 else (90, 96, 110),
            (x0 + 2, y0 + 2, int(172 * clamp(frac, 0, 1)), 26),
            border_radius=5,
        )
        text(
            c,
            "F · 50 ВКЛАДОК",
            14,
            (20, 22, 26) if sp <= 0 else (210, 215, 225),
            (x0 + 88, y0 + 15),
            anchor="center",
            font="consolab",
        )
        text(
            c,
            "← → двигаться      ПРОБЕЛ удар      F спецприём",
            15,
            (190, 198, 210),
            (CW // 2, 690),
            anchor="midbottom",
            font="segoe",
            alpha=190,
        )

        # sam speech bubble
        if self.sam_taunt_t > 0 and self.sam_taunt and self.mode == "fight":
            lines = wrap("segoeb", 20, self.sam_taunt, 360)
            bw = max(get_font("segoeb", 20).size(l)[0] for l in lines) + 36
            bh = 22 + len(lines) * 26
            bx = clamp(sm["x"] - bw // 2, 20, CW - bw - 20)
            by = 170
            box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(box, (12, 40, 30, 235), box.get_rect(), border_radius=12)
            pygame.draw.rect(box, (60, 230, 160), box.get_rect(), 2, border_radius=12)
            c.blit(box, (bx, by))
            for i, ln in enumerate(lines):
                text(
                    c,
                    ln,
                    20,
                    (215, 255, 235),
                    (bx + bw // 2, by + 12 + i * 26),
                    anchor="midtop",
                    font="segoeb",
                )
            pygame.draw.polygon(
                c,
                (12, 40, 30),
                [
                    (sm["x"] - 10, by + bh),
                    (sm["x"] + 10, by + bh),
                    (sm["x"], by + bh + 14),
                ],
            )

    def draw_overlays(self, c):
        if self.mode == "intro":
            ov = pygame.Surface((CW, CH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 190))
            c.blit(ov, (0, 0))
            t = self.mode_t
            if t < 1.5:
                k = clamp(t / 0.25, 0, 1)
                text(
                    c,
                    "MORTAL KOMBAT",
                    96,
                    GREEN,
                    (CW // 2, 240),
                    anchor="center",
                    font="impact",
                    outline=(6, 40, 24),
                    alpha=int(255 * k),
                )
                text(
                    c,
                    "RAM ALTМАН vs PC",
                    42,
                    GOLD,
                    (CW // 2, 330),
                    anchor="center",
                    font="impact",
                    outline=(50, 30, 0),
                    alpha=int(255 * k),
                )
            else:
                text(
                    c,
                    "ROUND %d" % self.round_no,
                    120,
                    WHITE,
                    (CW // 2, 280),
                    anchor="center",
                    font="impact",
                    outline=(10, 10, 14),
                )
                text(
                    c,
                    "FIGHT!",
                    86,
                    GOLD,
                    (CW // 2, 400),
                    anchor="center",
                    font="impact",
                    outline=(60, 30, 0),
                )
            if self.mode_t < 1.2:
                text(
                    c,
                    "TEST YOUR MIGHT!",
                    34,
                    (200, 255, 225),
                    (CW // 2, 470),
                    anchor="center",
                    font="impact",
                    alpha=220,
                )
            text(
                c,
                "ENTER — пропустить",
                14,
                (110, 118, 130),
                (CW - 24, CH - 18),
                anchor="bottomright",
                font="segoe",
            )

        if self.mode == "cutscene":
            ov = pygame.Surface((CW, CH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 110))
            c.blit(ov, (0, 0))
            if self.phase == "r1_call":
                text(
                    c,
                    "СЭМ ВЫЗЫВАЕТ ПОДДЕРЖКУ",
                    26,
                    (255, 120, 110),
                    (CW // 2, 150),
                    anchor="midtop",
                    font="impact",
                )
            if self.phase in ("r1_fall", "r2_dodge"):
                pygame.draw.polygon(
                    c,
                    (255, 230, 120),
                    [
                        (self.rack_x - 40, 60),
                        (self.rack_x + 40, 60),
                        (self.rack_x, 100),
                    ],
                )
                text(
                    c,
                    "СЕРВЕРНАЯ СТОЙКА H100",
                    22,
                    (255, 230, 120),
                    (self.rack_x, 110),
                    anchor="midtop",
                    font="impact",
                )
            if self.phase == "r1_impact":
                text(
                    c,
                    "K.O.",
                    140,
                    (255, 70, 60),
                    (CW // 2, 240),
                    anchor="center",
                    font="impact",
                    outline=(40, 0, 0),
                )
                text(
                    c,
                    "Сэм забирает вашу ОЗУ…",
                    26,
                    (235, 235, 235),
                    (CW // 2, 350),
                    anchor="center",
                    font="segoeb",
                )
            if self.phase == "r2_cue":
                blink = 0.5 + 0.5 * math.sin(self.t * 12)
                text(
                    c,
                    "ЖМИ ПРОБЕЛ ДЛЯ УВОРОТА!",
                    52,
                    (255, int(120 + 120 * blink), 80),
                    (CW // 2, 152),
                    anchor="center",
                    font="impact",
                    outline=(70, 10, 0),
                )
                bw = 520
                frac = clamp(self.dodge_window / 2.9, 0, 1)
                pygame.draw.rect(
                    c, (20, 24, 30), (CW // 2 - bw // 2, 232, bw, 18), border_radius=6
                )
                pygame.draw.rect(
                    c,
                    (255, 180, 60),
                    (CW // 2 - bw // 2, 220, int(bw * frac), 18),
                    border_radius=6,
                )
                text(
                    c,
                    "SPACE",
                    60,
                    (255, 255, 255),
                    (CW // 2, 258),
                    anchor="center",
                    font="impact",
                    outline=(0, 0, 0),
                    alpha=int(120 + 100 * blink),
                )
            if self.phase == "r2_miss":
                text(
                    c,
                    "ПРОМАХ!",
                    72,
                    (255, 90, 80),
                    (CW // 2, 240),
                    anchor="center",
                    font="impact",
                    outline=(40, 0, 0),
                )
            if self.phase in ("r2_fatality", "r2_combo"):
                if self.phase == "r2_fatality":
                    k = clamp(self.phase_t / 0.35, 0, 1)
                    text(
                        c,
                        "PASCALABC.NET",
                        58,
                        (220, 255, 240),
                        (CW // 2, 250),
                        anchor="center",
                        font="consolab",
                        outline=(10, 40, 30),
                        alpha=int(255 * k),
                    )
                    text(
                        c,
                        "FATAL CRASH!",
                        92,
                        (255, 90, 80),
                        (CW // 2, 320),
                        anchor="center",
                        font="impact",
                        outline=(40, 0, 0),
                        alpha=int(255 * k),
                    )
                else:
                    text(
                        c,
                        "FATALITY!",
                        120,
                        (255, 210, 90),
                        (CW // 2, 250),
                        anchor="center",
                        font="impact",
                        outline=(60, 20, 0),
                    )
                    text(
                        c,
                        "RAM IS SECURED!",
                        54,
                        (140, 255, 200),
                        (CW // 2, 340),
                        anchor="center",
                        font="impact",
                        outline=(6, 40, 24),
                    )
                    text(
                        c,
                        "Сэм Альтман отправлен оптимизировать код.",
                        24,
                        (225, 235, 230),
                        (CW // 2, 410),
                        anchor="center",
                        font="segoeb",
                    )

        if self.mode == "over":
            ov = pygame.Surface((CW, CH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            c.blit(ov, (0, 0))
            if self.round_no == 1:
                text(
                    c,
                    "ПОРАЖЕНИЕ",
                    110,
                    (255, 80, 70),
                    (CW // 2, 280),
                    anchor="center",
                    font="impact",
                    outline=(40, 0, 0),
                )
                text(
                    c,
                    "Сэм забирает вашу ОЗУ и уходит в закат.",
                    26,
                    (230, 230, 230),
                    (CW // 2, 370),
                    anchor="center",
                    font="segoeb",
                )
                if self.mode_t > 1.2:
                    text(
                        c,
                        "МЕСТО ПРЕСТУПЛЕНИЯ: ВАШ ПК",
                        20,
                        (150, 160, 175),
                        (CW // 2, 430),
                        anchor="center",
                        font="consolab",
                    )
                    if self.mode_t > 2.0:
                        self.result = "lost"


# --------------------------------------------------------------------------
# BSOD
# --------------------------------------------------------------------------
class BSODScreen:
    BLUE = (0, 120, 215)

    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.done = False
        self.result = None
        self.start = time.time()
        self.qr = self.make_qr()
        self.app.audio.stop_music(300)
        self.app.audio.play("bsod", 0.7)

    def make_qr(self):
        s = pygame.Surface((92, 92))
        s.fill((255, 255, 255))
        rnd = random.Random(42)
        cell = 7
        for y in range(0, 13):
            for x in range(0, 13):
                if rnd.random() < 0.45:
                    pygame.draw.rect(
                        s, (0, 0, 0), (x * cell + 2, y * cell + 2, cell, cell)
                    )
        for ox, oy in ((0, 0), (9, 0), (0, 9)):
            pygame.draw.rect(
                s, (0, 0, 0), (ox * cell + 2, oy * cell + 2, 5 * cell, 5 * cell)
            )
            pygame.draw.rect(
                s, (255, 255, 255), (ox * cell + 3, oy * cell + 3, 3 * cell, 3 * cell)
            )
            pygame.draw.rect(
                s, (0, 0, 0), (ox * cell + 4, oy * cell + 4, 3 * cell - 2, 3 * cell - 2)
            )
        return s

    def update(self, dt, events):
        self.t += dt
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.t > 0.4:
                    self.result = "rematch"
                    self.done = True

    def draw(self):
        c = self.app.display.canvas
        c.fill(self.BLUE)
        text(c, ":(", 120, (255, 255, 255), (108, 46), font="segoe")
        y = 196
        text(
            c,
            "На вашем ПК возникла проблема: Сэм Альтман победил в честном поединке.",
            30,
            (255, 255, 255),
            (112, y),
            font="segoe",
        )
        y += 58
        text(
            c,
            "1 ГБ вашей оперативной памяти был успешно выпаян агентом OpenAI",
            24,
            (255, 255, 255),
            (112, y),
            font="segoe",
        )
        text(
            c,
            "и отправлен экспресс-доставкой в дата-центр Сан-Франциско.",
            24,
            (255, 255, 255),
            (112, y + 32),
            font="segoe",
        )
        y += 92
        text(
            c,
            "Сбор пожертвований на AGI: 100% завершено.",
            24,
            (255, 255, 255),
            (112, y),
            font="segoe",
        )
        y += 70
        text(
            c,
            "Код остановки: CRITICAL_RAM_DEFICIT",
            22,
            (255, 255, 255),
            (112, y),
            font="segoe",
        )
        y += 34
        text(
            c,
            "Что вызвало проблему: SamAltman_SolderingIron.sys",
            22,
            (255, 255, 255),
            (112, y),
            font="segoe",
        )

        c.blit(self.qr, (112, CH - 190))
        text(
            c,
            "Для получения дополнительной информации посетите",
            15,
            (235, 240, 250),
            (216, CH - 188),
            font="segoe",
        )
        text(
            c,
            "openai.com/agi-datacenter",
            15,
            (235, 240, 250),
            (216, CH - 168),
            font="segoe",
        )

        blink = 0.5 + 0.5 * math.sin(self.t * 4.0)
        btn = pygame.Rect(CW // 2 - 430, CH - 116, 860, 52)
        pygame.draw.rect(c, (255, 255, 255), btn, 2, border_radius=6)
        text(
            c,
            "[ НАЖМИТЕ ПРОБЕЛ, ЧТОБЫ ВЫЗВАТЬ СЭМА НА РЕВАНШ ]",
            20,
            (255, 240, int(150 + 100 * blink)),
            btn.center,
            anchor="center",
            font="consolab",
        )
        text(
            c,
            "и отбить свою ОЗУ",
            15,
            (225, 232, 245),
            (btn.centerx, btn.bottom + 8),
            anchor="midtop",
            font="segoe",
        )


# --------------------------------------------------------------------------
# VICTORY
# --------------------------------------------------------------------------
class VictoryScreen:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.done = False
        self.bg = pygame.image.load(asset("victory_bg.png")).convert()
        self.pc = pygame.image.load(asset("pc.png")).convert_alpha()
        self.ram = pygame.image.load(asset("ram.png")).convert_alpha()
        self.ram = pygame.transform.smoothscale(self.ram, (240, 166))
        self.logo = pygame.image.load(asset("logo_green.png")).convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (64, 64))
        self.confetti = []
        for _ in range(80):
            self.confetti.append(
                {
                    "x": random.uniform(0, CW),
                    "y": random.uniform(-CH, 0),
                    "vy": random.uniform(60, 190),
                    "vx": random.uniform(-40, 40),
                    "c": random.choice(
                        [
                            (255, 205, 90),
                            (80, 255, 175),
                            (95, 215, 255),
                            (255, 255, 255),
                        ]
                    ),
                    "s": random.randint(3, 8),
                    "r": random.uniform(0, 6.28),
                }
            )
        self.btn = pygame.Rect(CW // 2 - 130, 600, 260, 62)
        self.app.audio.stop_music(200)
        self.app.audio.play("victory", 0.9)
        self.app.audio.play("crowd", 0.6)

    def update(self, dt, events):
        self.t += dt
        for cf in self.confetti:
            cf["y"] += cf["vy"] * dt
            cf["x"] += cf["vx"] * dt
            cf["r"] += dt
            if cf["y"] > CH + 10:
                cf["y"] = -10
                cf["x"] = random.uniform(0, CW)
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.done = True
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.btn.collidepoint(e.pos):
                    self.done = True

    def draw(self):
        c = self.app.display.canvas
        c.blit(self.bg, (0, 0))
        for cf in self.confetti:
            pygame.draw.rect(c, cf["c"], (cf["x"], cf["y"], cf["s"], cf["s"]))
        for i in range(2):
            pygame.draw.circle(c, (255, 220, 140), (740, 150), 300 - i * 42, 1)

        # RAM flies into the PC
        t = clamp(self.t / 1.8, 0, 1)
        pc_x, pc_y = 300, 560
        img = self.pc
        rect = img.get_rect(midbottom=(pc_x, pc_y))
        c.blit(img, rect)
        if t < 1:
            rx = lerp(CW + 160, pc_x + 40, ease_out(t))
            ry = lerp(120, 420, ease_in_out(t))
            r = self.ram.get_rect(center=(rx, ry))
        else:
            r = self.ram.get_rect(center=(pc_x + 40, 420))
        c.blit(self.ram, r)
        if t >= 1 and self.t < 2.2:
            for i in range(2):
                a = int(160 * (1 - (self.t - 1) / 1.2))
                pygame.draw.circle(c, (120, 255, 190), (pc_x + 40, 420), 60 + i * 26, 2)

        text(
            c,
            "ПОБЕДА!",
            104,
            GOLD,
            (740, 96),
            anchor="midtop",
            font="impact",
            outline=(60, 30, 0),
        )
        text(
            c,
            "RAM IS SECURED",
            28,
            (200, 255, 230),
            (740, 208),
            anchor="midtop",
            font="impact",
        )

        # ram counter
        gb = int(33 * clamp((self.t - 0.6) / 2.2, 0, 1))
        text(
            c,
            "ОЗУ: %d ГБ" % gb,
            52,
            (255, 255, 255),
            (740, 264),
            anchor="midtop",
            font="impact",
        )
        bar(c, 740 - 190, 344, 380, 20, gb / 33.0, (120, 255, 190))

        text(
            c,
            "Ваша память в безопасности.",
            26,
            (225, 235, 230),
            (740, 392),
            anchor="midtop",
            font="segoeb",
        )
        text(
            c,
            "Сэму Альтману придётся оптимизировать код.",
            26,
            (225, 235, 230),
            (740, 430),
            anchor="midtop",
            font="segoeb",
        )
        c.blit(self.logo, (592, 492))
        text(
            c,
            "33 GB DDR5 · возвращено владельцу",
            16,
            (140, 160, 155),
            (676, 524),
            anchor="midleft",
            font="consolab",
        )

        hover = self.btn.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(
            c, (60, 220, 160) if hover else (18, 60, 46), self.btn, border_radius=10
        )
        pygame.draw.rect(c, (140, 255, 200), self.btn, 2, border_radius=10)
        text(
            c,
            "ВЫХОД",
            30,
            (255, 255, 255) if hover else (200, 255, 230),
            self.btn.center,
            anchor="center",
            font="impact",
        )


# --------------------------------------------------------------------------
# app
# --------------------------------------------------------------------------
def screen_size():
    try:
        import ctypes

        return (
            ctypes.windll.user32.GetSystemMetrics(0),
            ctypes.windll.user32.GetSystemMetrics(1),
        )
    except Exception:
        return (1280, 720)


def set_topmost():
    try:
        import ctypes

        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass


def grab_desktop_surface():
    """Screenshot of the real desktop, cover-fitted to the canvas."""
    try:
        from PIL import Image, ImageGrab

        img = ImageGrab.grab(all_screens=True).convert("RGB")
        sw, sh = img.size
        scale = max(CW / sw, CH / sh)
        nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
        img = img.resize((nw, nh), Image.LANCZOS)
        img = img.crop(
            ((nw - CW) // 2, (nh - CH) // 2, (nw - CW) // 2 + CW, (nh - CH) // 2 + CH)
        )
        return pygame.image.fromstring(img.tobytes(), (CW, CH), "RGB")
    except Exception as e:
        print("desktop grab failed:", e)
        return None


def fake_desktop_surface():
    p = asset("fake_desktop.png")
    if os.path.exists(p):
        try:
            return pygame.image.load(p).convert()
        except Exception:
            pass
    return None


def hide_window():
    try:
        import ctypes

        hwnd = pygame.display.get_wm_info().get("window")
        ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


class App:
    def __init__(self):
        self.display = Display()
        self.audio = Audio()
        self.clock = pygame.time.Clock()

    def run_screen(self, screen):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            events = pygame.event.get()
            poll_quit(events)
            screen.update(dt, events)
            screen.draw()
            self.display.present()
            if getattr(screen, "done", False):
                return None
            if getattr(screen, "result", None):
                return screen.result

    def play(self):
        try:
            pygame.mouse.set_visible(True)
            self.display.toast_window("Служба оптимизации OpenAI AGI",
                                      TOAST_W, TOAST_H, TOAST_KEY)
            toast = ToastScreen(self)
            while not toast.done:
                dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
                events = pygame.event.get()
                poll_quit(events)
                toast.update(dt, events)
                toast.draw()
                self.display.present()
            if toast.result == "yes":
                self.app_audio_stop()
                self.display.go_overlay("RAM Altman vs PC")
                self.run_screen(ThanksScreen(self))
                return
            if toast.result != "no":
                return

            hide_window()
            time.sleep(0.25)
            desktop = grab_desktop_surface()
            self.display.go_overlay("RAM Altman vs PC")
            fight = FightScreen(self, 1, overlay=True, desktop=desktop)
            if self.run_screen(fight) != "lost":
                return
            bsod = BSODScreen(self)
            if self.run_screen(bsod) != "rematch":
                return
            fight2 = FightScreen(self, 2, overlay=True, desktop=desktop)
            if self.run_screen(fight2) != "won":
                return
            self.run_screen(VictoryScreen(self))
        except QuitGame:
            pass
        finally:
            self.app_audio_stop()
            try:
                pygame.mixer.quit()
            except Exception:
                pass
            try:
                pygame.display.quit()
            except Exception:
                pass
            pygame.quit()

    def app_audio_stop(self):
        self.audio.stop_music(0)
        try:
            pygame.mixer.stop()
        except Exception:
            pass


# --------------------------------------------------------------------------
# service: autostart watcher that waits for the video to be opened+closed
# --------------------------------------------------------------------------
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def local_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    p = os.path.join(base, "OpenAI_AGI_Service")
    os.makedirs(p, exist_ok=True)
    return p


def config_path():
    return os.path.join(local_dir(), "config.json")


def desktop_dir():
    try:
        import ctypes
        from ctypes import wintypes

        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf)
        if buf.value:
            return buf.value
    except Exception:
        pass
    d = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(d):
        d = os.path.join(os.path.expanduser("~"), "Рабочий стол")
    return d


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "OpenAI AGI Optimization Service"


def set_run_key(value):
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as k:
        if value is None:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass
        else:
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, value)


def run_key_value():
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as k:
            return winreg.QueryValueEx(k, RUN_NAME)[0]
    except Exception:
        return None


def launch_prefix():
    if getattr(sys, "frozen", False):
        return [os.path.abspath(sys.executable)]
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return [
        pyw if os.path.exists(pyw) else sys.executable,
        os.path.abspath(sys.argv[0]),
    ]


def quote(s):
    return '"%s"' % s


def file_in_use(path):
    """True when some process holds the file open (Restart Manager)."""
    try:
        import ctypes
        from ctypes import wintypes

        class RM_UNIQUE_PROCESS(ctypes.Structure):
            _fields_ = [
                ("dwProcessId", wintypes.DWORD),
                ("ProcessStartTime", wintypes.FILETIME),
            ]

        class RM_PROCESS_INFO(ctypes.Structure):
            _fields_ = [
                ("Process", RM_UNIQUE_PROCESS),
                ("strAppName", wintypes.WCHAR * 256),
                ("strServiceShortName", wintypes.WCHAR * 64),
                ("ApplicationType", ctypes.c_uint),
                ("AppStatus", wintypes.ULONG),
                ("TSSessionId", wintypes.DWORD),
                ("bRestartable", wintypes.BOOL),
            ]

        rm = ctypes.WinDLL("rstrtmgr")
        rm.RmStartSession.argtypes = [
            ctypes.POINTER(wintypes.DWORD),
            wintypes.DWORD,
            wintypes.LPWSTR,
        ]
        rm.RmRegisterResources.argtypes = [
            wintypes.DWORD,
            wintypes.UINT,
            ctypes.POINTER(wintypes.LPCWSTR),
            wintypes.UINT,
            ctypes.c_void_p,
            wintypes.UINT,
            ctypes.c_void_p,
        ]
        rm.RmGetList.argtypes = [
            wintypes.DWORD,
            ctypes.POINTER(wintypes.UINT),
            ctypes.POINTER(wintypes.UINT),
            ctypes.POINTER(RM_PROCESS_INFO),
            ctypes.POINTER(wintypes.DWORD),
        ]
        session = wintypes.DWORD()
        if rm.RmStartSession(ctypes.byref(session), 0, None) != 0:
            return None
        try:
            res = (wintypes.LPCWSTR * 1)(path)
            if rm.RmRegisterResources(session, 1, res, 0, None, 0, None) != 0:
                return None
            needed = wintypes.UINT(0)
            count = wintypes.UINT(0)
            reason = wintypes.DWORD(0)
            r = rm.RmGetList(
                session,
                ctypes.byref(needed),
                ctypes.byref(count),
                None,
                ctypes.byref(reason),
            )
            if needed.value == 0:
                return False
            arr = (RM_PROCESS_INFO * needed.value)()
            count = wintypes.UINT(needed.value)
            r = rm.RmGetList(
                session,
                ctypes.byref(needed),
                ctypes.byref(count),
                arr,
                ctypes.byref(reason),
            )
            if r != 0:
                return None
            return count.value > 0
        finally:
            rm.RmEndSession(session)
    except Exception:
        return None


def window_titles():
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        titles = []
        buf = ctypes.create_unicode_buffer(512)

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                n = user32.GetWindowTextW(hwnd, buf, 512)
                if n:
                    titles.append(buf.value)
            return True

        user32.EnumWindows(cb, 0)
        return titles
    except Exception:
        return []


def video_open(path):
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    if not os.path.exists(path):
        return False
    used = file_in_use(path)
    if used:
        return True
    if used is None:
        for t in window_titles():
            tl = t.lower()
            if stem and (stem in tl or "альтман" in tl and "интервью" in tl):
                return True
    return False


def watch_log(msg):
    try:
        with open(os.path.join(local_dir(), "watch.log"), "a", encoding="utf-8") as f:
            f.write("%s  %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))
    except Exception:
        pass


def watch_service():
    import json

    dpi_aware()
    watch_log("watcher started")
    try:
        cfg = json.load(open(config_path(), encoding="utf-8"))
    except Exception as e:
        watch_log("no config: %r" % (e,))
        return
    video = cfg.get("video", "")
    watch_log("watching %s" % video)
    if not os.path.exists(video):
        watch_log("video missing, exit")
        return

    seen = False
    closed = 0
    hot = 0
    while True:
        try:
            active = video_open(video)
        except Exception as e:
            watch_log("probe error %r" % (e,))
            active = False
        if active:
            if not seen:
                watch_log("video opened")
            seen = True
            hot = 0
            closed = 0
        elif seen:
            closed += 1
            if closed >= 3:
                watch_log("video closed -> firing")
                time.sleep(0.5)
                try:
                    subprocess.Popen(
                        launch_prefix() + ["--game"],
                        creationflags=0x08000000,
                        cwd=app_dir(),
                    )
                except Exception as e:
                    watch_log("spawn failed %r" % (e,))
                return
        else:
            hot += 1
            if hot % 600 == 0:
                watch_log("still waiting (%d min)" % (hot // 2))
        time.sleep(0.5)


def install_service():
    import json
    import shutil

    here = app_dir()
    mp4s = [f for f in os.listdir(here) if f.lower().endswith(".mp4")]
    if not mp4s:
        return "Рядом с программой нет видеофайла .mp4"
    src = os.path.join(here, mp4s[0])
    dst = os.path.join(desktop_dir(), "Сэм Альтман — интервью.mp4")
    try:
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy2(src, dst)
    except Exception as e:
        return "Не удалось скопировать видео: %r" % (e,)

    prefix = launch_prefix()
    if getattr(sys, "frozen", False):
        local_exe = os.path.join(local_dir(), "RAM_Altman_vs_PC.exe")
        try:
            if os.path.abspath(prefix[0]) != os.path.abspath(local_exe):
                shutil.copy2(prefix[0], local_exe)
            prefix = [local_exe]
        except Exception:
            prefix = [os.path.abspath(sys.executable)]

    cfg = {"video": dst, "installed": time.time(), "exe": prefix[0]}
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    cmd = " ".join(quote(p) for p in prefix) + " --watch"
    set_run_key(cmd)
    watch_log("installed: %s" % cmd)
    try:
        subprocess.Popen(prefix + ["--watch"], creationflags=0x08000000, cwd=app_dir())
    except Exception as e:
        return "Служба установлена, но не запустилась: %r" % (e,)
    return None


def uninstall_service():
    try:
        set_run_key(None)
    except Exception:
        pass
    try:
        os.remove(config_path())
    except Exception:
        pass
    return None


def info_box(title, message, ok_only=True):
    """Native Win32 message box (no tkinter -> smaller exe)."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, title, 0x00000040 | 0x00040000)
    except Exception:
        print(title, message)


def selftest():
    """Headless check of the packaged build: every asset, font and screen."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    lines = []

    def w(msg):
        lines.append(msg)
        print(msg)

    try:
        app = App()
        app.display.windowed((CW, CH), "selftest")

        for name in sorted(os.listdir(ASSETS)):
            path = os.path.join(ASSETS, name)
            if name.endswith(".png") or name.endswith(".jpg"):
                im = pygame.image.load(path)
                w("img  %-22s %s" % (name, im.get_size()))
            elif name.endswith(".wav"):
                import wave

                with wave.open(path, "rb") as wf:
                    w("wav  %-22s %.2fs" % (name, wf.getnframes() / wf.getframerate()))
        for key in FONT_PATHS:
            get_font(key, 20)
            w("font %s ok" % key)

        ToastScreen(app).draw()
        w("screen toast ok")
        app.display.windowed((CW, CH), "selftest")
        ThanksScreen(app).draw()
        w("screen thanks ok")
        FightScreen(app, 1, overlay=True).draw()
        w("screen fight1 ok")
        FightScreen(app, 2, overlay=True).draw()
        w("screen fight2 ok")
        BSODScreen(app).draw()
        w("screen bsod ok")
        VictoryScreen(app).draw()
        w("screen victory ok")
        w("SELFTEST OK")
    except Exception as e:
        import traceback

        w("SELFTEST FAILED: %r" % (e,))
        w(traceback.format_exc())
    finally:
        try:
            pygame.quit()
        except Exception:
            pass
        try:
            os.makedirs(local_dir(), exist_ok=True)
            with open(os.path.join(local_dir(), "selftest.log"), "w",
                      encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception:
            pass


def main():
    dpi_aware()
    if "--selftest" in sys.argv:
        selftest()
        return
    if "--watch" in sys.argv:
        watch_service()
        return
    if "--install" in sys.argv:
        err = install_service()
        if err:
            info_box("Служба оптимизации OpenAI AGI", err)
        else:
            info_box(
                "Служба оптимизации OpenAI AGI",
                "Служба установлена и добавлена в автозагрузку.\n\n"
                "На рабочем столе появился файл «Сэм Альтман — интервью.mp4».\n"
                "Когда его откроют и закроют — начнётся проверка вашей ОЗУ.\n\n"
                "Выход из игры в любой момент: Esc или Ctrl+Q.",
            )
        return
    if "--uninstall" in sys.argv:
        uninstall_service()
        info_box("Служба оптимизации OpenAI AGI", "Служба удалена из автозагрузки.")
        return

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    if "--shots" in sys.argv:
        shots()
    else:
        App().play()


# --------------------------------------------------------------------------
# offline screenshot harness (dev only)
# --------------------------------------------------------------------------
def shots():
    global grab_desktop_surface
    grab_desktop_surface = lambda: None
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    app = App()
    app.display.windowed((CW, CH), "shots")
    out = os.path.join(BASE_DIR, "tools", "shots")
    os.makedirs(out, exist_ok=True)

    def grab(name):
        pygame.image.save(app.display.canvas, os.path.join(out, name + ".png"))
        print("shot:", name)

    app.display.toast_window("Служба оптимизации OpenAI AGI", TOAST_W, TOAST_H, TOAST_KEY)
    toast = ToastScreen(app)
    for w in (0.2, 1.0, 2.2):
        while toast.t < w:
            toast.update(1 / 60, [])
        toast.slide = 1.0
        toast.draw()
        grab("toast_%03.1f" % w)
    toast.hover_count = 2
    toast.no_hover()
    toast.no_hover()
    toast.draw()
    grab("toast_jump")

    app.display.windowed((CW, CH), "shots")
    th = ThanksScreen(app)
    while th.t < 6.5:
        th.update(1 / 60, [])
    th.draw()
    grab("thanks")

    app.display.windowed((CW, CH), "shots")
    fight = FightScreen(app, 1, overlay=True)
    for w in (0.3, 1.7, 4.2):
        while fight.t < w:
            fight.update(1 / 60, [])
        fight.draw()
        grab("fight1_%03.1f" % w)
    fight.sam["hp"] = 24
    fight.start_r1_cutscene()
    for i, w in enumerate((0.6, 2.6, 3.4, 4.4)):
        target = fight.t + w
        while fight.t < target:
            fight.update(1 / 60, [])
        fight.draw()
        grab("fight1_cut%d" % i)

    bsod = BSODScreen(app)
    for w in (0.2, 1.5):
        while bsod.t < w:
            bsod.update(1 / 60, [])
        bsod.draw()
        grab("bsod_%02.1f" % w)

    f2 = FightScreen(app, 2, overlay=True)
    while f2.t < 4.2:
        f2.update(1 / 60, [])
    f2.draw()
    grab("fight2_start")
    f2.sam["hp"] = 24
    f2.start_r2_cutscene()
    for i, w in enumerate((1.0, 2.2)):
        target = f2.t + w
        while f2.t < target:
            f2.update(1 / 60, [])
        f2.draw()
        grab("fight2_cue%d" % i)
    f2.do_dodge()
    for i, w in enumerate((0.5, 1.2, 2.6)):
        target = f2.t + w
        while f2.t < target:
            f2.update(1 / 60, [])
        f2.draw()
        grab("fight2_fat%d" % i)

    vic = VictoryScreen(app)
    for i, w in enumerate((0.5, 2.4, 4.0)):
        while vic.t < w:
            vic.update(1 / 60, [])
        vic.draw()
        grab("victory_%d" % i)

    app.display.close()


if __name__ == "__main__":
    main()
```

# КОНЕЦ ФАЙЛА

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
```

# КОНЕЦ ФАЙЛА

