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
            u.SetWindowPos.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_uint,
            ]
            u.SetLayeredWindowAttributes.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_ubyte,
                ctypes.c_uint,
            ]
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
                    self.found = "Найдено 33 ГБ. Рекомендуется пожертвовать 1 ГБ."

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
        self._cheer_done = False
        try:
            self.app.audio.music("ambient", 0.16)
            self.app.audio.play("vo_yes", 1.0)
        except Exception:
            pass

    def update(self, dt, events):
        self.t += dt
        if not self._cheer_done and self.t > 4.2:
            self._cheer_done = True
            try:
                self.app.audio.play("crowd", 0.55)
            except Exception:
                pass
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
            a = int(230 * self.hint_a)
            pill = pygame.Rect(24, CH - 66, 336, 40)
            ov = pygame.Surface(pill.size, pygame.SRCALPHA)
            pygame.draw.rect(
                ov, (6, 22, 17, int(200 * self.hint_a)), ov.get_rect(), border_radius=8
            )
            pygame.draw.rect(
                ov,
                (44, 128, 96, int(190 * self.hint_a)),
                ov.get_rect(),
                1,
                border_radius=8,
            )
            c.blit(ov, pill.topleft)
            text(
                c,
                "удерживайте  A + G + I,  чтобы закрыть",
                15,
                (150, 236, 196),
                (pill.centerx, pill.centery),
                anchor="center",
                font="segoe",
                alpha=a,
            )
            if self.hold_bar > 0:
                w = 336
                pygame.draw.rect(c, (16, 46, 34), (24, CH - 20, w, 5), border_radius=3)
                pygame.draw.rect(
                    c,
                    (70, 210, 150),
                    (24, CH - 20, int(w * self.hold_bar), 5),
                    border_radius=3,
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
    # Константы баланса и физики боя
    FLOOR = 608
    MAX_PARTICLES = 180
    ROUND_TIME = 90.0

    P_HP_R1 = 180.0
    P_HP_R2 = 200.0
    SAM_HP_R1 = 180.0
    SAM_HP_R2 = 180.0
    SCRIPT_HP = 25.0

    GRAV = 1950.0
    JUMP_VY = -780.0
    SAM_JUMP_VY = -660.0
    MOVE_SPEED = 350.0

    BACKSTEP_VX = -680.0
    BACKSTEP_DUR = 0.22
    BACKSTEP_INVULN = 0.20
    BACKSTEP_CD = 0.85

    CHARGE_NEED = 0.60
    SPECIAL_CD = 6.5
    COMBO_STEP = 0.08
    COMBO_MAX = 10

    LASER_TELEGRAPH = 0.90
    ORB_Y = 562
    ORB_SPEED = 450.0
    # Между шарами должно влезать три системных блока: 3 * 271 px (ширина
    # спрайта ПК) + 92 px диаметра шара = 905 px между центрами.
    ORB_MIN_GAP = 905.0

    def __init__(self, app, round_no=1, overlay=False, desktop=None):
        self.app = app
        self.round_no = round_no
        self.overlay = overlay
        self.t = 0.0
        self.done = False
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

        # Основные спрайты
        _pi = pygame.image.load(asset("pc.png")).convert_alpha()
        _ph = 300
        self.pc_img = pygame.transform.smoothscale(
            _pi, (int(_pi.get_width() * _ph / _pi.get_height()), _ph)
        )
        _si = pygame.image.load(asset("sam_fight.png")).convert_alpha()
        _sh = 318
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
            (int(self.rack.get_width() * 0.72), int(self.rack.get_height() * 0.72)),
        )
        self.coin = pygame.image.load(asset("coin20.png")).convert_alpha()
        self.chrome = pygame.image.load(asset("chrome_win.png")).convert_alpha()
        self.avatar = pygame.image.load(asset("sam_avatar.png")).convert_alpha()
        self.avatar = pygame.transform.smoothscale(self.avatar, (72, 72))
        self.ram_icon = pygame.image.load(asset("ram_icon.png")).convert_alpha()
        self.logo = pygame.image.load(asset("logo_green.png")).convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (90, 90))

        # Новые спрайты боя из assets/ (создаются в tools/build_assets.py)
        self.orb_img = pygame.image.load(asset("orb_gpt.png")).convert_alpha()
        self.screw_img = pygame.image.load(asset("screw_proj.png")).convert_alpha()
        self.dollar_img = pygame.image.load(asset("dollar_drop.png")).convert_alpha()
        self.marker_img = pygame.image.load(asset("floor_marker.png")).convert_alpha()
        self.mini_rack_img = pygame.image.load(asset("mini_rack.png")).convert_alpha()
        self.auras = {
            1: pygame.image.load(asset("aura_p1.png")).convert_alpha(),
            2: pygame.image.load(asset("aura_p2.png")).convert_alpha(),
            3: pygame.image.load(asset("aura_p3.png")).convert_alpha(),
        }

        p_hp = self.P_HP_R2 if round_no == 2 else self.P_HP_R1
        s_hp = self.SAM_HP_R2 if round_no == 2 else self.SAM_HP_R1

        self.player = {
            "x": 330.0,
            "y": float(self.FLOOR),
            "vy": 0.0,
            "on_ground": True,
            "hp": p_hp,
            "maxhp": p_hp,
            "ghost": p_hp,
            "face": 1,
            "atk": 0.0,
            "atk_cd": 0.0,
            "air_atk": False,
            "special_cd": 0.0,
            "hurt": 0.0,
            "lunge": 0.0,
            "dead": False,
            "dash": 0.0,
            "vx": 0.0,
            "invuln": 0.0,
            "backstep_t": 0.0,
            "backstep_cd": 0.0,
            "charge_t": 0.0,
            "charging": False,
            "afterimages": [],
        }
        self.sam = {
            "x": 970.0,
            "y": float(self.FLOOR),
            "vy": 0.0,
            "on_ground": True,
            "hp": s_hp,
            "maxhp": s_hp,
            "ghost": s_hp,
            "atk_cd": 1.3,
            "hurt": 0.0,
            "stun": 0.0,
            "dead": False,
            "pose": "idle",
            "bob": 0.0,
            "blink": 0.0,
            "rise": 0.0,
            "x0": 970.0,
            "boss_phase": 1,
            "alpha": 255,
            "tp_timer": 0.0,
            "tp_target": 970.0,
            "orb_cd": 3.2,
            "barrage_cd": 6.0,
        }

        self.projectiles = []
        self.orbs = []
        self.orb_queue = []
        self.hazards = []
        self.tabs = []
        self.particles = []
        self.damage_text = []

        self.shake_t = 0.0
        self.shake_dur = 0.001
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
        self.round_timer = self.ROUND_TIME
        self.phase_banner = ""
        self.phase_banner_t = 0.0

        self.scan = scanline_surface(CW, CH, 16, 4)
        self.vign = vignette_surface(CW, CH, 120)

    # Вспомогательные методы -----------------------------------------------
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
            if len(self.particles) >= self.MAX_PARTICLES:
                break
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

    def combo_mult(self):
        return 1.0 + min(self.combo, self.COMBO_MAX) * self.COMBO_STEP

    def dmg(self, target, amount, x=None, y=None, big=False, color=(255, 235, 120)):
        if target == "player":
            p = self.player
            if p["invuln"] > 0 and not big:
                return
            p["hp"] = max(0.0, p["hp"] - amount)
            p["hurt"] = 0.22
            self.combo = 0
            self.combo_t = 0.0
            d = p
        else:
            s = self.sam
            if not big:
                amount = int(round(amount * self.combo_mult()))
            s["hp"] = max(0.0, s["hp"] - amount)
            s["hurt"] = 0.20
            self.combo += 1
            self.combo_t = 2.1
            d = s

        self.damage_text.append(
            {
                "x": x if x is not None else d["x"] + random.randint(-24, 24),
                "y": y if y is not None else d["y"] - 260 + random.randint(-30, 10),
                "t": 0.0,
                "life": 0.9 if not big else 1.6,
                "txt": str(int(amount)),
                "size": 40 if not big else 96,
                "color": color,
            }
        )

    def shake(self, mag, dur):
        self.shake_mag = mag
        self.shake_t = self.shake_dur = max(0.001, dur)

    # Основной цикл обновления ---------------------------------------------
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
                    if e.key in (pygame.K_w, pygame.K_UP):
                        self.player_jump()
                    elif e.key in (pygame.K_s, pygame.K_DOWN):
                        self.player_backstep()
                    elif e.key == pygame.K_SPACE:
                        if not self.player["on_ground"]:
                            self.player_air_attack()
                        else:
                            self.player["charging"] = True
                            self.player["charge_t"] = 0.0
                    elif e.key == pygame.K_f:
                        self.player_special()
                if (
                    e.key == pygame.K_SPACE
                    and self.mode == "over"
                    and self.mode_t > 1.2
                ):
                    self.result = "won" if self.round_no == 2 else "lost"

            elif e.type == pygame.KEYUP and self.mode == "fight":
                if e.key == pygame.K_SPACE and self.player["charging"]:
                    held = self.player["charge_t"]
                    self.player["charging"] = False
                    self.player["charge_t"] = 0.0
                    if held >= self.CHARGE_NEED:
                        self.player_fire_screw()
                    else:
                        self.player_attack()

        self.shake_t = max(0.0, self.shake_t - dt)
        self.flash = max(0.0, self.flash - dt * 3.2)
        self.phase_banner_t = max(0.0, self.phase_banner_t - dt)
        self.combo_t -= dt
        if self.combo_t <= 0:
            self.combo = 0
        self.sam_taunt_t = max(0.0, self.sam_taunt_t - dt)

        for p in self.particles:
            p.life -= dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.grav * dt
        self.particles = [p for p in self.particles if p.life > 0]
        if len(self.particles) > self.MAX_PARTICLES:
            self.particles = self.particles[-self.MAX_PARTICLES :]

        for d in self.damage_text:
            d["t"] += dt
            d["y"] -= 60 * dt
        self.damage_text = [d for d in self.damage_text if d["t"] < d["life"]]

        for ai in self.player["afterimages"]:
            ai["life"] -= dt
        self.player["afterimages"] = [
            ai for ai in self.player["afterimages"] if ai["life"] > 0
        ]

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
        else:
            self.say("Сдавай планки DDR5 добровольно!", 2.2)

    # Приёмы игрока --------------------------------------------------------
    def player_jump(self):
        p = self.player
        if p["dead"] or not p["on_ground"]:
            return
        p["vy"] = self.JUMP_VY
        p["on_ground"] = False
        self.app.audio.play("whoosh", 0.45)
        self.burst(
            p["x"],
            self.FLOOR - 4,
            8,
            [(180, 190, 205), (120, 130, 145)],
            190,
            0.35,
            (2, 4),
            350,
        )

    def player_backstep(self):
        p = self.player
        if p["dead"] or p["backstep_cd"] > 0:
            return
        p["backstep_t"] = self.BACKSTEP_DUR
        p["backstep_cd"] = self.BACKSTEP_CD
        p["invuln"] = self.BACKSTEP_INVULN
        p["charging"] = False
        p["charge_t"] = 0.0
        self.app.audio.play("whoosh", 0.75)
        for i in range(4):
            p["afterimages"].append(
                {
                    "x": p["x"] + i * 18,
                    "y": p["y"],
                    "life": 0.22 - i * 0.04,
                    "max_life": 0.22,
                }
            )

    def player_attack(self):
        p = self.player
        if p["atk_cd"] > 0 or p["dead"]:
            return
        p["atk"] = 0.30
        p["atk_cd"] = 0.34
        p["air_atk"] = False
        p["lunge"] = 1.0
        self.app.audio.play("whoosh", 0.45)
        dist = abs(self.sam["x"] - p["x"])
        if dist < 245 and abs(self.sam["y"] - p["y"]) < 140:
            dmg = random.randint(8, 11)
            self.dmg("sam", dmg, self.sam["x"] - 30, self.sam["y"] - 260)
            self.app.audio.play("hit", 0.9)
            self.burst(self.sam["x"] - 20, self.sam["y"] - 230, 14)
            self.shake(6, 0.16)
            self.sam["stun"] = 0.11
            if self.sam["hp"] <= 0:
                self.ko_sam()
        else:
            if random.random() < 0.35:
                self.say("Промах! Хром тормозит.", 1.0)

    def player_air_attack(self):
        p = self.player
        if p["atk_cd"] > 0 or p["dead"]:
            return
        p["atk"] = 0.42
        p["atk_cd"] = 0.56
        p["air_atk"] = True
        p["vy"] = max(p["vy"], 260.0)
        p["charging"] = False
        p["charge_t"] = 0.0
        self.app.audio.play("whoosh", 0.7)
        dist = abs(self.sam["x"] - p["x"])
        if dist < 265:
            dmg = random.randint(14, 18)
            self.dmg(
                "sam",
                dmg,
                self.sam["x"] - 20,
                self.sam["y"] - 280,
                color=(255, 200, 90),
            )
            self.app.audio.play("hit", 1.0)
            self.app.audio.play("clang", 0.55)
            self.burst(
                self.sam["x"] - 20,
                self.sam["y"] - 240,
                22,
                [(95, 215, 255), (255, 230, 120), (255, 255, 255)],
                500,
            )
            self.shake(10, 0.24)
            self.sam["stun"] = 0.20
            if self.sam["hp"] <= 0:
                self.ko_sam()

    def player_fire_screw(self):
        p = self.player
        if p["dead"]:
            return
        p["atk"] = 0.28
        p["atk_cd"] = 0.40
        self.app.audio.play("clang", 0.65)
        self.app.audio.play("whoosh", 0.8)
        self.burst(
            p["x"] + 80,
            p["y"] - 170,
            10,
            [(95, 215, 255), (255, 255, 255)],
            320,
            0.35,
        )
        self.projectiles.append(
            {
                "kind": "screw",
                "x": p["x"] + 90,
                "y": p["y"] - 170,
                "vx": 780.0,
                "t": 0.0,
                "rot": 0.0,
                "spin": -720.0,
                "hit": False,
            }
        )

    def player_special(self):
        p = self.player
        if p["special_cd"] > 0 or p["dead"]:
            return
        p["special_cd"] = self.SPECIAL_CD
        self.app.audio.play("tabs", 1.0)
        self.app.audio.play("whoosh", 0.7)
        sx = self.sam["x"]
        for i in range(8):
            self.tabs.append(
                {
                    "x": clamp(sx + random.randint(-220, 220), 220, CW - 120),
                    "y": -180 - i * 75,
                    "vy": random.randint(560, 740),
                    "hit": False,
                    "rot": random.uniform(-18, 18),
                    "delay": i * 0.06,
                }
            )

    # Основная логика боя --------------------------------------------------
    def update_fight(self, dt):
        p, s = self.player, self.sam
        keys = pygame.key.get_pressed()

        # Таймер раунда
        self.round_timer = max(0.0, self.round_timer - dt)
        if self.round_timer <= 0 and not self.over:
            if self.round_no == 1:
                self.start_r1_cutscene()
            else:
                self.start_r2_cutscene()
            return

        # Удержание заряда Пробела
        if p["charging"] and not p["dead"]:
            if keys[pygame.K_SPACE]:
                p["charge_t"] += dt
            else:
                held = p["charge_t"]
                p["charging"] = False
                p["charge_t"] = 0.0
                if held >= self.CHARGE_NEED:
                    self.player_fire_screw()
                else:
                    self.player_attack()

        # Движение игрока по горизонтали
        moving = 0
        if not p["dead"]:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moving -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moving += 1

        if p["backstep_t"] > 0:
            p["backstep_t"] = max(0.0, p["backstep_t"] - dt)
            p["x"] = clamp(p["x"] + self.BACKSTEP_VX * dt, 95, 760)
        else:
            spd = self.MOVE_SPEED * (0.65 if p["charging"] else 1.0)
            p["vx"] = moving * spd
            if p["atk"] <= 0 or not p["on_ground"]:
                p["x"] = clamp(p["x"] + moving * spd * dt, 95, 760)

        p["x"] = clamp(
            p["x"] + p["lunge"] * 120 * dt * (1 if p["atk"] > 0.18 else 0), 95, 760
        )
        p["lunge"] = max(0.0, p["lunge"] - dt * 3.2)

        # Прыжок и гравитация игрока
        if not p["on_ground"]:
            p["y"] += p["vy"] * dt
            p["vy"] += self.GRAV * dt
            if p["y"] >= self.FLOOR:
                p["y"] = float(self.FLOOR)
                p["vy"] = 0.0
                p["on_ground"] = True
                # Приземление с пылью (и доп. задержка после удара в воздухе)
                dust_n = 14 if p["air_atk"] else 8
                self.burst(
                    p["x"],
                    self.FLOOR - 3,
                    dust_n,
                    [(195, 205, 220), (130, 140, 155)],
                    240 if p["air_atk"] else 160,
                    0.42,
                    (2, 5),
                    400,
                )
                if p["air_atk"]:
                    p["atk_cd"] = max(p["atk_cd"], 0.42)
                    self.shake(5, 0.12)
                p["air_atk"] = False

        p["atk"] = max(0.0, p["atk"] - dt)
        p["atk_cd"] = max(0.0, p["atk_cd"] - dt)
        p["special_cd"] = max(0.0, p["special_cd"] - dt)
        p["invuln"] = max(0.0, p["invuln"] - dt)
        p["backstep_cd"] = max(0.0, p["backstep_cd"] - dt)

        # Проверка смены фаз Сэма (66% и 33% HP)
        hp_frac = s["hp"] / s["maxhp"]
        if hp_frac <= 0.66 and s["boss_phase"] == 1:
            s["boss_phase"] = 2
            self.phase_banner = "ФАЗА 2 · GPT-5 TURBO MODE"
            self.phase_banner_t = 2.2
            self.flash = 0.55
            self.flash_color = (95, 215, 255)
            self.shake(12, 0.35)
            self.app.audio.play("gong", 0.8)
            self.say("Подключаю кластеры! Больше инвестиций!", 2.2)
            self.spawn_orb_wave()
        elif hp_frac <= 0.33 and s["boss_phase"] < 3:
            s["boss_phase"] = 3
            self.phase_banner = "ФАЗА 3 · AGI OVERCLOCK"
            self.phase_banner_t = 2.4
            self.flash = 0.7
            self.flash_color = (255, 90, 90)
            self.shake(15, 0.45)
            self.app.audio.play("gong", 0.95)
            self.say("AGI ПОЧТИ ГОТОВ! ОТДАЙ ВСЮ ПАМЯТЬ!", 2.4)
            self.sam_server_barrage()

        # Гравитация и прыжки Сэма
        if not s["on_ground"]:
            s["y"] += s["vy"] * dt
            s["vy"] += self.GRAV * dt
            if s["y"] >= self.FLOOR:
                s["y"] = float(self.FLOOR)
                s["vy"] = 0.0
                s["on_ground"] = True

        # Телепорт («апдейт модели»)
        if s["tp_timer"] > 0:
            s["tp_timer"] -= dt
            s["alpha"] = 95
            if s["tp_timer"] <= 0:
                s["x"] = s["tp_target"]
                s["alpha"] = 255
                self.burst(
                    s["x"],
                    s["y"] - 190,
                    18,
                    [(80, 255, 175), (95, 215, 255), (255, 255, 255)],
                    420,
                    0.45,
                )
        else:
            s["alpha"] = 255

        # ИИ Сэма
        speed_mult = (
            1.0 if s["boss_phase"] == 1 else (1.28 if s["boss_phase"] == 2 else 1.55)
        )
        s["atk_cd"] -= dt * speed_mult
        s["orb_cd"] -= dt
        s["barrage_cd"] -= dt
        s["stun"] = max(0.0, s["stun"] - dt)

        dist = s["x"] - p["x"]
        if s["stun"] <= 0 and not s["dead"] and s["tp_timer"] <= 0:
            if dist > 480:
                s["x"] -= 155 * speed_mult * dt
            elif dist < 255:
                s["x"] += 140 * speed_mult * dt
            s["x"] = clamp(s["x"], 680, 1170)

        s["pose"] = "summon" if s["stun"] > 0 else "idle"

        # Регулярный запуск шаров-логотипов ChatGPT
        if s["orb_cd"] <= 0 and not s["dead"] and not p["dead"]:
            self.spawn_orb_wave()
            s["orb_cd"] = random.uniform(6.2, 8.8) / (
                1.0 + 0.15 * (s["boss_phase"] - 1)
            )

        # Серверный шквал в 3-й фазе
        if (
            s["boss_phase"] >= 3
            and s["barrage_cd"] <= 0
            and not s["dead"]
            and not p["dead"]
        ):
            self.sam_server_barrage()
            s["barrage_cd"] = random.uniform(7.5, 10.0)

        if s["atk_cd"] <= 0 and s["stun"] <= 0 and not s["dead"] and not p["dead"]:
            self.choose_sam_attack(dist)
            s["atk_cd"] = random.uniform(1.45, 2.25)

        # Очередь спавна шаров-логотипов
        for item in list(self.orb_queue):
            item["delay"] -= dt
            if item["delay"] <= 0:
                # держим безопасный зазор: не выпускаем шар, пока предыдущий
                # не отъехал достаточно далеко от левого края
                if any(ob["x"] < self.ORB_MIN_GAP for ob in self.orbs):
                    continue
                self.orbs.append(
                    {
                        "x": -50.0,
                        "y": float(self.ORB_Y),
                        "vx": item["speed"],
                        "rot": 0.0,
                        "hit": False,
                        "sam_jumped": False,
                    }
                )
                self.app.audio.play("whoosh", 0.5)
                self.orb_queue.remove(item)

        # Движение и коллизии шаров-логотипов ChatGPT
        for ob in list(self.orbs):
            ob["x"] += ob["vx"] * dt
            ob["rot"] -= 340 * dt

            # Игрок обязан перепрыгивать шары на W
            if not ob["hit"] and not p["dead"]:
                if abs(ob["x"] - p["x"]) < 54 and p["y"] > self.FLOOR - 78:
                    ob["hit"] = True
                    self.dmg(
                        "player",
                        random.randint(9, 13),
                        p["x"],
                        p["y"] - 180,
                        color=(255, 110, 90),
                    )
                    self.app.audio.play("hit", 0.85)
                    self.burst(
                        ob["x"],
                        ob["y"],
                        14,
                        [(80, 255, 175), (255, 255, 255)],
                        360,
                        0.45,
                    )
                    self.shake(7, 0.16)

            # ИРОНИЯ: Сэм сам подпрыгивает через свои же шары
            if (
                not ob["sam_jumped"]
                and not s["dead"]
                and s["x"] - 185 <= ob["x"] <= s["x"] - 35
            ):
                ob["sam_jumped"] = True
                if s["on_ground"]:
                    s["vy"] = self.SAM_JUMP_VY
                    s["on_ground"] = False
                    self.app.audio.play("whoosh", 0.4)
                    if random.random() < 0.48:
                        self.say(
                            random.choice(
                                [
                                    "Мои же шары!",
                                    "Опять свои же шары прыгать!",
                                    "Кто пустил логотипы по полу?!",
                                ]
                            ),
                            1.5,
                        )

            if ob["x"] > CW + 90:
                ob["dead"] = True
        self.orbs = [ob for ob in self.orbs if not ob.get("dead")]

        # Снаряды (монеты, лазер, винты игрока)
        for pr in list(self.projectiles):
            pr["x"] += pr["vx"] * dt
            pr["t"] += dt
            pr["rot"] += pr["spin"] * dt

            if pr["kind"] == "coin":
                r = pygame.Rect(0, 0, 46, 46)
                r.center = (int(pr["x"]), int(pr["y"]))
                p_rect = pygame.Rect(int(p["x"] - 64), int(p["y"] - 290), 128, 290)
                if not pr["hit"] and r.colliderect(p_rect):
                    pr["hit"] = True
                    pr["dead"] = True
                    self.dmg("player", random.randint(8, 11), p["x"], p["y"] - 220)
                    self.app.audio.play("coin", 0.8)
                    self.burst(pr["x"], pr["y"], 12, [(255, 220, 120), (80, 230, 160)])
                    self.shake(5, 0.15)

            elif pr["kind"] == "screw":
                if not pr["hit"] and not s["dead"]:
                    if (
                        abs(pr["x"] - s["x"]) < 72
                        and abs(pr["y"] - (s["y"] - 190)) < 175
                    ):
                        pr["hit"] = True
                        pr["dead"] = True
                        self.dmg(
                            "sam",
                            random.randint(15, 20),
                            s["x"] - 20,
                            pr["y"],
                            color=(95, 215, 255),
                        )
                        self.app.audio.play("hit", 0.95)
                        self.app.audio.play("clang", 0.65)
                        self.burst(
                            pr["x"],
                            pr["y"],
                            18,
                            [(95, 215, 255), (255, 230, 130), (255, 255, 255)],
                            460,
                        )
                        self.shake(8, 0.2)
                        s["stun"] = 0.16
                        if s["hp"] <= 0:
                            self.ko_sam()

            elif pr["kind"] == "laser_charge":
                if pr["t"] >= self.LASER_TELEGRAPH:
                    pr["kind"] = "laser"
                    pr["t"] = 0.0
                    self.app.audio.play("laser", 0.95)
                    if abs(p["x"] - pr["x"]) < 82 and p["y"] > self.FLOOR - 170:
                        self.dmg("player", random.randint(12, 16), p["x"], p["y"] - 230)
                        self.shake(9, 0.22)
                    else:
                        if random.random() < 0.5:
                            self.say("Увернулся? Просто галочка в логах.", 1.2)

            elif pr["kind"] == "laser":
                if pr["t"] > 0.32:
                    pr["dead"] = True

            if pr["x"] < -120 or pr["x"] > CW + 120:
                pr["dead"] = True
        self.projectiles = [p_ for p_ in self.projectiles if not p_.get("dead")]

        # Падающие опасности по маркерам ($ инвестора и мини-стойки)
        for hz in list(self.hazards):
            if hz["delay"] > 0:
                hz["delay"] -= dt
                continue
            hz["t"] += dt
            if hz["state"] == "warn":
                if hz["t"] >= hz["warn_dur"]:
                    hz["state"] = "fall"
                    hz["t"] = 0.0
                    self.app.audio.play("whoosh", 0.65)
            elif hz["state"] == "fall":
                hz["y"] += hz["vy"] * dt
                hz["vy"] += 1400 * dt
                if hz["y"] >= self.FLOOR - 24:
                    hz["y"] = float(self.FLOOR - 24)
                    hz["state"] = "done"
                    hz["dead"] = True
                    rad = 115 if hz["kind"] == "dollar" else 95
                    dmg_val = (
                        random.randint(13, 17)
                        if hz["kind"] == "dollar"
                        else random.randint(11, 15)
                    )
                    self.app.audio.play(
                        "coin" if hz["kind"] == "dollar" else "boom", 0.85
                    )
                    self.shake(9, 0.22)
                    self.burst(
                        hz["x"],
                        self.FLOOR - 16,
                        22,
                        [(255, 215, 90), (80, 255, 175), (255, 255, 255)]
                        if hz["kind"] == "dollar"
                        else [(255, 140, 80), (80, 255, 175), (220, 220, 220)],
                        480,
                        0.65,
                    )
                    if abs(p["x"] - hz["x"]) < rad and p["y"] > self.FLOOR - 140:
                        self.dmg(
                            "player",
                            dmg_val,
                            p["x"],
                            p["y"] - 220,
                            color=(255, 200, 80),
                        )
        self.hazards = [h for h in self.hazards if not h.get("dead")]

        # Вкладки Google Chrome (урон по площади)
        for tb in list(self.tabs):
            if tb["delay"] > 0:
                tb["delay"] -= dt
                continue
            tb["y"] += tb["vy"] * dt
            if tb["y"] >= self.FLOOR - 48 and not tb["hit"]:
                tb["hit"] = True
                # Урон по площади (AoE радиус 240 пкс)
                if abs(tb["x"] - s["x"]) < 240 and not s["dead"]:
                    self.dmg("sam", 4, tb["x"], s["y"] - 250)
                    self.app.audio.play("hit", 0.45)
                    if s["hp"] <= 0:
                        self.ko_sam()
                self.burst(
                    tb["x"],
                    self.FLOOR - 20,
                    9,
                    [(200, 210, 225), (95, 215, 255), (255, 255, 255)],
                    320,
                    0.4,
                    (2, 4),
                )
                self.shake(4, 0.1)
            if tb["y"] > 760:
                tb["dead"] = True
        self.tabs = [tb for tb in self.tabs if not tb.get("dead")]

        # Скриптовая серверная стойка H100 при HP <= 25
        if self.round_no == 1:
            if s["hp"] <= self.SCRIPT_HP and self.phase is None and not self.over:
                self.start_r1_cutscene()
        else:
            if (
                s["hp"] <= self.SCRIPT_HP
                and self.phase is None
                and self.t > self.rack_ready
                and not self.over
            ):
                self.start_r2_cutscene()

        if p["hp"] <= 0 and not p["dead"] and not self.over:
            self.player_die()

    # Атаки Сэма -----------------------------------------------------------
    def choose_sam_attack(self, dist):
        s = self.sam
        if dist < 245:
            if s["boss_phase"] >= 2 and random.random() < 0.35:
                self.sam_model_update()
            else:
                self.sam_melee()
            return

        roll = random.random()
        if s["boss_phase"] == 1:
            if roll < 0.45:
                self.sam_coin()
            elif roll < 0.80:
                self.sam_laser()
            else:
                self.sam_investor_drop()
        elif s["boss_phase"] == 2:
            if roll < 0.30:
                self.sam_coin()
            elif roll < 0.58:
                self.sam_laser()
            elif roll < 0.82:
                self.sam_investor_drop()
            else:
                self.sam_model_update()
        else:
            if roll < 0.25:
                self.sam_coin()
            elif roll < 0.52:
                self.sam_laser()
            elif roll < 0.78:
                self.sam_investor_drop()
            else:
                self.sam_model_update()

        if random.random() < 0.24:
            self.say(
                random.choice(
                    [
                        "Это ради AGI!",
                        "Ещё один гигабайт!",
                        "Не сопротивляйся.",
                        "$20 — и память ваша.",
                        "Контекстное окно растёт!",
                    ]
                ),
                1.4,
            )

    def spawn_orb_wave(self):
        s = self.sam
        count = random.randint(2, 3 if s["boss_phase"] == 1 else 4)
        spd = self.ORB_SPEED + (s["boss_phase"] - 1) * 45.0
        delay_acc = 0.15
        for i in range(count):
            self.orb_queue.append({"delay": delay_acc, "speed": spd})
            # Зазор задаёт ORB_MIN_GAP, поэтому очередь только «просит» шары —
            # фактический ритм держит проверка дистанции при спавне.
            delay_acc += random.uniform(0.90, 1.20)
        self.say("Лови шары ChatGPT! Прыгай на W!", 1.7)

    def sam_melee(self):
        p = self.player
        dmg = random.randint(10, 14)
        if not p["dead"]:
            self.dmg("player", dmg, p["x"], p["y"] - 220)
            self.app.audio.play("hit", 0.9)
            self.burst(p["x"], p["y"] - 190, 14, [(255, 120, 90), (255, 220, 150)])
            self.shake(9, 0.2)
            self.say("Удар паяльником!", 1.0)
            p["atk"] = 0.0

    def sam_coin(self):
        s = self.sam
        self.projectiles.append(
            {
                "kind": "coin",
                "x": s["x"] - 90,
                "y": 350,
                "vx": -620 - (s["boss_phase"] - 1) * 50,
                "t": 0.0,
                "rot": 0.0,
                "spin": 540,
                "hit": False,
            }
        )
        self.app.audio.play("coin", 0.55)

    def sam_laser(self):
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
        self.say("Усиленный лазер выпайки!", 1.1)

    def sam_investor_drop(self):
        px = clamp(self.player["x"] + random.randint(-60, 60), 150, 740)
        self.hazards.append(
            {
                "kind": "dollar",
                "x": px,
                "y": -140.0,
                "vy": 420.0,
                "state": "warn",
                "t": 0.0,
                "warn_dur": 0.75,
                "delay": 0.0,
            }
        )
        if self.sam["boss_phase"] >= 2:
            px2 = clamp(px + random.choice([-160, 160]), 150, 740)
            self.hazards.append(
                {
                    "kind": "dollar",
                    "x": px2,
                    "y": -140.0,
                    "vy": 420.0,
                    "state": "warn",
                    "t": 0.0,
                    "warn_dur": 0.75,
                    "delay": 0.25,
                }
            )
        self.say("Призыв инвестора! $7 триллионов!", 1.5)

    def sam_model_update(self):
        s = self.sam
        s["tp_timer"] = 0.26
        s["tp_target"] = random.uniform(730, 1130)
        self.app.audio.play("whoosh", 0.8)
        self.burst(
            s["x"], s["y"] - 190, 14, [(80, 255, 175), (95, 215, 255)], 360, 0.35
        )
        self.say("Апдейт весов модели!", 1.2)

    def sam_server_barrage(self):
        base_x = clamp(self.player["x"], 180, 660)
        offsets = [-150, 0, 150]
        random.shuffle(offsets)
        for i, off in enumerate(offsets):
            tx = clamp(base_x + off, 140, 740)
            self.hazards.append(
                {
                    "kind": "mini_rack",
                    "x": tx,
                    "y": -180.0,
                    "vy": 480.0,
                    "state": "warn",
                    "t": 0.0,
                    "warn_dur": 0.70,
                    "delay": i * 0.34,
                }
            )
        self.say("СЕРВЕРНЫЙ ШКВАЛ!", 1.8)

    # Нокаут и катсцены ----------------------------------------------------
    def ko_sam(self):
        s = self.sam
        s["dead"] = True
        self.app.audio.play("crowd", 0.8)
        self.app.audio.play("clang", 0.8)
        self.burst(
            s["x"],
            360,
            40,
            [(255, 200, 100), (255, 80, 80), (255, 255, 255)],
            600,
            1.2,
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

    def start_r1_cutscene(self):
        self.mode = "cutscene"
        self.mode_t = 0.0
        self.phase = "r1_call"
        self.phase_t = 0.0
        self.rack_y = -760.0
        self.rack_x = self.player["x"]
        self.player["y"] = float(self.FLOOR)
        self.player["on_ground"] = True
        self.orbs.clear()
        self.orb_queue.clear()
        self.hazards.clear()
        self.projectiles.clear()
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
        self.player["y"] = float(self.FLOOR)
        self.player["on_ground"] = True
        self.orbs.clear()
        self.orb_queue.clear()
        self.hazards.clear()
        self.projectiles.clear()
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
                    self.rack_x,
                    520,
                    60,
                    [(255, 210, 120), (160, 255, 210)],
                    800,
                    1.5,
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

    # Отрисовка ------------------------------------------------------------
    def build_stage(self):
        """Translucent arena laid over the frozen desktop screenshot."""
        s = pygame.Surface((CW, CH), pygame.SRCALPHA)
        for i in range(170):
            a = int(150 * (i / 170) ** 1.6)
            pygame.draw.rect(s, (3, 6, 9, a), (0, 540 + i, CW, 1))
        # мягкие световые пятна на полу под бойцами (эллипсы, а не купол)
        for cx, col in ((330, (70, 240, 200)), (970, (255, 190, 90))):
            for k in range(6):
                a = 6 + k * 2
                rx = 215 - k * 28
                ry = 24 - k * 3
                pygame.draw.ellipse(
                    s,
                    col + (a,),
                    (cx - rx, self.FLOOR - ry - 2, rx * 2, ry * 2 + 6),
                )
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
        self.draw_hazards(world, shake_x, shake_y)
        self.draw_rack(world, shake_x, shake_y)
        self.draw_sam(world, shake_x, shake_y)
        self.draw_player(world, shake_x, shake_y)
        self.draw_orbs(world, shake_x, shake_y)
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
        for ent, w0 in ((self.player, 120), (self.sam, 135)):
            h_gap = max(0.0, self.FLOOR - ent["y"])
            scale = clamp(1.0 - h_gap / 380.0, 0.45, 1.0)
            w = max(24, int(w0 * scale))
            sh = pygame.Surface((w, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, int(130 * scale)), sh.get_rect())
            s.blit(sh, (ent["x"] - w // 2 + dx, self.FLOOR - 14 + dy))

    def draw_player(self, s, dx, dy):
        p = self.player
        img = self.pc_img
        x = p["x"] + dx
        y = p["y"] + dy

        # Шлейф afterimage при отскоке S/вниз
        for ai in p["afterimages"]:
            ghost = img.copy()
            ghost.set_alpha(int(115 * clamp(ai["life"] / ai["max_life"], 0, 1)))
            s.blit(ghost, ghost.get_rect(midbottom=(ai["x"] + dx, ai["y"] + dy)))

        if p["dash"] > 0:
            p["dash"] = max(0.0, p["dash"] - 0.06)
            for i in range(3):
                ghost = img.copy()
                ghost.set_alpha(50 - i * 12)
                s.blit(ghost, ghost.get_rect(midbottom=(x + 40 + i * 26, y)))

        ang = 0
        if p["dead"]:
            ang = -74
        elif p["hurt"] > 0:
            ang = 7
        elif p["air_atk"]:
            ang = -14
        elif p["atk"] > 0:
            ang = -6
        if ang:
            img = pygame.transform.rotate(img, ang)

        bob = (
            math.sin(self.sam["bob"] * 2.6) * 3
            if (not p["dead"] and p["on_ground"])
            else 0
        )
        rect = img.get_rect(midbottom=(x, y + bob))
        s.blit(img, rect)

        if p["hurt"] > 0:
            g = self.pc_white.copy()
            g.set_alpha(int(230 * (p["hurt"] / 0.22)))
            s.blit(pygame.transform.rotate(g, ang) if ang else g, rect)

        # Индикатор заряда выстрела винтами
        if p["charging"] and not p["dead"]:
            frac = clamp(p["charge_t"] / self.CHARGE_NEED, 0, 1)
            bx, by = int(x - 48), int(y - 335)
            pygame.draw.rect(s, (12, 16, 22), (bx, by, 96, 10), border_radius=4)
            col = (80, 255, 175) if frac >= 1.0 else (95, 215, 255)
            pygame.draw.rect(
                s, col, (bx + 2, by + 2, int(92 * frac), 6), border_radius=3
            )

        # Дуги удара
        if p["atk"] > 0.16:
            px = x + 120
            py = y - 245
            for i in range(3):
                pygame.draw.arc(
                    s,
                    (95, 215, 255) if p["air_atk"] else (255, 235, 170),
                    (px - 20 - i * 8, py - i * 12, 74, 64),
                    0.4,
                    2.2,
                    3,
                )

    def draw_sam(self, s, dx, dy):
        sm = self.sam
        img = self.sam_img
        x = sm["x"] + dx
        bob = math.sin(sm["bob"] * 2.2) * 5 if sm["on_ground"] else 0
        y = sm["y"] + dy + bob

        # Аура текущей фазы Сэма
        if not sm["dead"]:
            aura = self.auras.get(sm["boss_phase"], self.auras[1])
            s.blit(aura, aura.get_rect(center=(x, y - 190)))

        if sm["dead"]:
            if self.phase in ("r2_fatality", "r2_combo"):
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
            img = pygame.transform.scale(
                img, (int(img.get_width() * 1.05), int(img.get_height() * 1.05))
            )

        if sm["alpha"] < 255:
            img = img.copy()
            img.set_alpha(sm["alpha"])

        rect = img.get_rect(midbottom=(x, y))
        s.blit(img, rect)
        if sm["hurt"] > 0 and not sm["dead"]:
            g = self.sam_white.copy()
            g.set_alpha(int(230 * (sm["hurt"] / 0.22)))
            s.blit(g, g.get_rect(midbottom=(x, y)))

    def draw_orbs(self, s, dx, dy):
        for ob in self.orbs:
            rot_img = pygame.transform.rotate(self.orb_img, ob["rot"])
            s.blit(rot_img, rot_img.get_rect(center=(ob["x"] + dx, ob["y"] + dy)))

    def draw_hazards(self, s, dx, dy):
        for hz in self.hazards:
            if hz["delay"] > 0:
                continue
            mx = int(hz["x"] + dx)
            my = int(self.FLOOR + dy)
            s.blit(self.marker_img, self.marker_img.get_rect(center=(mx, my - 4)))
            if hz["state"] == "warn":
                pygame.draw.line(s, (255, 90, 90, 110), (mx, 80), (mx, my - 10), 2)
            elif hz["state"] == "fall":
                sp = self.dollar_img if hz["kind"] == "dollar" else self.mini_rack_img
                s.blit(sp, sp.get_rect(midbottom=(mx, int(hz["y"] + dy))))

    def draw_rack(self, s, dx, dy):
        if self.rack_y < -600:
            return
        r = self.rack
        x = self.rack_x + dx + 130 - r.get_width() // 2
        y = int(self.rack_y) + dy
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
            elif pr["kind"] == "screw":
                img = pygame.transform.rotate(self.screw_img, pr["rot"])
                s.blit(img, img.get_rect(center=(pr["x"] + dx, pr["y"] + dy)))
            elif pr["kind"] == "laser_charge":
                a = 0.4 + 0.6 * abs(math.sin(pr["t"] * 18))
                col = (255, int(80 + 100 * a), 80)
                cx = int(pr["x"] + dx)
                cy = 470 + dy
                pygame.draw.circle(s, col, (cx, cy), int(14 + 12 * a), 3)
                pygame.draw.circle(s, (255, 60, 60), (cx, cy), 5)
                pygame.draw.line(s, (255, 70, 70, 120), (cx, 240), (cx, 605), 3)
            elif pr["kind"] == "laser":
                x0 = self.sam["x"] + dx - 100
                x1 = pr["x"] + dx
                yy = 470 + dy
                w = 12
                pygame.draw.line(
                    s, (255, 60, 60), (x0, self.sam["y"] - 245 + dy), (x1, yy), w + 8
                )
                pygame.draw.line(
                    s, (255, 230, 230), (x0, self.sam["y"] - 245 + dy), (x1, yy), w
                )
                glow = pygame.Surface((CW, CH), pygame.SRCALPHA)
                pygame.draw.line(
                    glow,
                    (255, 90, 90, 95),
                    (x0, self.sam["y"] - 245 + dy),
                    (x1, yy),
                    w + 28,
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
        grad = pygame.Surface((CW, 155), pygame.SRCALPHA)
        for i in range(155):
            pygame.draw.line(grad, (4, 6, 9, int(185 * (1 - i / 155))), (0, i), (CW, i))
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

        phase_names = {1: "ФАЗА 1", 2: "ФАЗА 2 · TURBO", 3: "ФАЗА 3 · AGI"}
        text(
            c,
            "СЭМ АЛЬТМАН · %s" % phase_names.get(sm["boss_phase"], "ФАЗА 1"),
            28,
            WHITE
            if sm["boss_phase"] == 1
            else (CYAN if sm["boss_phase"] == 2 else RED),
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

        # Таймер раунда и номер раунда
        text(
            c,
            "ROUND %d" % self.round_no,
            20,
            (200, 210, 225),
            (CW // 2, 18),
            anchor="midtop",
            font="impact",
        )
        t_col = RED if self.round_timer < 15 else GOLD
        text(
            c,
            "%02d" % int(math.ceil(self.round_timer)),
            44,
            t_col,
            (CW // 2, 42),
            anchor="midtop",
            font="impact",
            outline=(14, 16, 22),
        )

        # Комбо-множитель
        if self.combo > 1:
            text(
                c,
                "%d HITS · x%.2f" % (self.combo, self.combo_mult()),
                30,
                GOLD,
                (CW // 2, 92),
                anchor="midtop",
                font="impact",
                outline=(60, 30, 0),
            )

        # Индикатор кулдауна F «50 вкладок Google Chrome»
        sp = self.player["special_cd"]
        x0, y0 = 44, 134
        pygame.draw.rect(c, (12, 16, 22), (x0, y0, 210, 30), border_radius=6)
        pygame.draw.rect(c, (24, 28, 36), (x0 + 2, y0 + 2, 206, 26), border_radius=5)
        frac = 1 - sp / self.SPECIAL_CD
        pygame.draw.rect(
            c,
            (255, 205, 90) if sp <= 0 else (90, 96, 110),
            (x0 + 2, y0 + 2, int(206 * clamp(frac, 0, 1)), 26),
            border_radius=5,
        )
        lbl = "F · 50 ВКЛАДОК [ГОТОВО]" if sp <= 0 else "F · ПЕРЕЗАРЯДКА %.1fс" % sp
        text(
            c,
            lbl,
            13,
            (20, 22, 26) if sp <= 0 else (215, 220, 230),
            (x0 + 105, y0 + 15),
            anchor="center",
            font="consolab",
        )

        # Баннер смены фазы
        if self.phase_banner_t > 0:
            text(
                c,
                self.phase_banner,
                42,
                CYAN if sm["boss_phase"] == 2 else RED,
                (CW // 2, 145),
                anchor="midtop",
                font="impact",
                outline=(10, 12, 18),
            )

        text(
            c,
            "A/D движение   W прыжок   S отскок   ПРОБЕЛ удар / зажать: винт   F 50 вкладок",
            15,
            (190, 198, 210),
            (CW // 2, 694),
            anchor="midbottom",
            font="segoe",
            alpha=195,
        )

        # Реплики Сэма
        if self.sam_taunt_t > 0 and self.sam_taunt and self.mode == "fight":
            lines = wrap("segoeb", 20, self.sam_taunt, 360)
            bw = max(get_font("segoeb", 20).size(l)[0] for l in lines) + 36
            bh = 22 + len(lines) * 26
            bx = clamp(sm["x"] - bw // 2, 20, CW - bw - 20)
            by = max(130, int(sm["y"] - 435))
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


def minimize_desktop():
    """Свернуть все окна пользователя, кроме своих: стол чистый перед боем."""
    try:
        import ctypes
        from ctypes import wintypes

        u = ctypes.windll.user32
        u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        u.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        u.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]
        u.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        pid = os.getpid()
        skip = {
            "Progman",
            "WorkerW",
            "Shell_TrayWnd",
            "Shell_SecondaryTrayWnd",
            "Windows.UI.Core.CoreWindow",
            "ForegroundStaging",
        }
        shell = u.GetShellWindow()
        targets = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _):
            if hwnd == shell or not u.IsWindowVisible(hwnd):
                return True
            owner = wintypes.DWORD()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == pid:
                return True
            if u.GetWindowLongW(hwnd, -20) & 0x00000080:  # WS_EX_TOOLWINDOW
                return True
            buf = ctypes.create_unicode_buffer(256)
            u.GetClassNameW(hwnd, buf, 256)
            if buf.value in skip:
                return True
            targets.append(hwnd)
            return True

        u.EnumWindows(cb, 0)
        for h in targets:
            u.ShowWindow(h, 6)  # SW_MINIMIZE
        print("minimized", len(targets), "windows")
        return len(targets)
    except Exception as e:
        print("minimize failed:", e)
        return 0


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
            self.display.toast_window(
                "Служба оптимизации OpenAI AGI", TOAST_W, TOAST_H, TOAST_KEY
            )
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
            minimize_desktop()
            time.sleep(0.6)
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
            with open(
                os.path.join(local_dir(), "selftest.log"), "w", encoding="utf-8"
            ) as f:
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

    app.display.toast_window(
        "Служба оптимизации OpenAI AGI", TOAST_W, TOAST_H, TOAST_KEY
    )
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
