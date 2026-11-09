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