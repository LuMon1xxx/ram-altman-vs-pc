# -*- coding: utf-8 -*-
"""Builds the "normal" media file: an interview clip that turns into Sam's
briefing.  Video: crop/blur/overlay + burned-in ASS subtitles.
Audio: original dub for 9 s, then our TTS lines over an ambient bed.
"""

import os
import subprocess
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")
def find_raw_video():
    """Raw interview clip: ./source_media first, then the user's folder."""
    cands = [os.path.join(ROOT, "source_media", "sam_interview_raw.mp4")]
    orig = os.path.join(os.path.dirname(ROOT), "фото и видео")
    if os.path.isdir(orig):
        cands += [os.path.join(orig, f) for f in sorted(os.listdir(orig))
                  if f.lower().endswith(".mp4")]
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


SRC = find_raw_video()
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

SR = 48000
TOTAL = 21.8
CUT = 9.0
LINES = [
    (
        "vo_intro1",
        9.55,
        "Мы в OpenAI строим AGI. Но дата-центрам катастрофически не хватает памяти.",
    ),
    (
        "vo_intro2",
        13.45,
        "Поэтому мы вынуждены экспроприировать оперативную память из ваших домашних ПК.",
    ),
    ("vo_intro3", 16.95, "Это ради общего блага. И ради моего дата-центра."),
]


def read_wav(path):
    with wave.open(path, "rb") as w:
        ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch == 2:
        x = x.reshape(-1, 2)
    else:
        x = np.stack([x, x], axis=1)
    return x, sr


def resample(x, sr_in, sr_out):
    n_out = int(round(len(x) * sr_out / sr_in))
    idx = np.linspace(0, len(x) - 1, n_out)
    i0 = np.floor(idx).astype(int)
    i1 = np.minimum(i0 + 1, len(x) - 1)
    frac = (idx - i0)[:, None]
    return (x[i0] * (1 - frac) + x[i1] * frac).astype(np.float32)


def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i : i + n] += x[:n] * gain


def build_audio():
    buf = np.zeros((int(TOTAL * SR), 2), dtype=np.float32)

    # ambient bed
    amb, sr = read_wav(os.path.join(ASSETS, "ambient.wav"))
    amb = resample(amb, sr, SR)
    for i in range(0, len(buf), len(amb)):
        chunk = amb[: min(len(amb), len(buf) - i)]
        buf[i : i + len(chunk)] += chunk * 0.07

    # original dub, first 9 s
    raw = os.path.join(BUILD, "orig9.wav")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            SRC,
            "-t",
            str(CUT),
            "-vn",
            "-ar",
            str(SR),
            "-ac",
            "2",
            raw,
        ],
        check=True,
    )
    orig, _ = read_wav(raw)
    orig = orig[: int(CUT * SR)]
    fade = int(0.5 * SR)
    orig[-fade:] *= np.linspace(1, 0, fade)[:, None]
    place(buf, orig, 0, 1.0)

    # glitch burst
    rng = np.random.default_rng(3)
    gl = rng.uniform(-1, 1, int(0.5 * SR)).astype(np.float32)
    gl = np.round(gl * 6) / 6  # crunchy
    gl *= np.linspace(0.2, 0.0, len(gl))
    place(buf, np.stack([gl, gl], axis=1), 9.0, 0.20)

    # speech
    for key, at, txt in LINES:
        x, sr = read_wav(os.path.join(ASSETS, key + ".wav"))
        x = resample(x, sr, SR)
        # small room tail
        tail = np.zeros((int(0.5 * SR), 2), dtype=np.float32)
        for d, g in ((0.05, 0.20), (0.11, 0.12), (0.19, 0.07)):
            k = int(d * SR)
            tail[k : k + len(x)] += (
                x[: len(tail) - k] * g if len(x) > len(tail) - k else 0
            )
        place(buf, x, at, 1.0)
        place(buf, tail, at, 0.5)

    # outro sting
    for i, f in enumerate((110, 164.8, 220)):
        n = int(1.6 * SR)
        tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2) * 0.10
        place(buf, np.stack([y, y], axis=1), 19.6 + i * 0.02, 1.0)

    peak = float(np.max(np.abs(buf))) or 1.0
    buf = buf / peak * 0.92
    path = os.path.join(BUILD, "voice_mix.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("audio ->", path, "%.2fs" % (len(buf) / SR))
    return path


ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Segoe UI Semibold,30,&H00FFFFFF,&H000000FF,&H00141212,&H96000000,0,0,0,0,100,100,0,0,4,2,1,2,70,70,44,204
Style: Title,Impact,54,&H00FFFFFF,&H000000FF,&H00100804,&H00000000,0,0,0,0,100,100,1,0,1,3,2,8,60,60,16,204
Style: Small,Segoe UI,20,&H00D8E4EE,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,60,60,26,204
Style: Glitch,Impact,68,&H000000FF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,3,0,5,30,30,24,204
Style: Mark,Segoe UI,17,&H60FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,9,28,28,22,204

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.30,0:00:04.20,Title,,0,0,0,,{\\fad(350,400)}OPENAI · AGI ALL-HANDS
Dialogue: 0,0:00:00.60,0:00:04.20,Sub,,0,0,0,,{\\fad(350,400)}фрагмент закрытого брифинга · 12 марта
Dialogue: 0,0:00:00.60,0:00:21.60,Mark,,0,0,0,,{\\fad(600,0)}openai.com/live
Dialogue: 0,0:00:05.00,0:00:08.90,Small,,0,0,0,,{\\fad(300,300)}Сэм Альтман, CEO OpenAI
Dialogue: 0,0:00:09.02,0:00:09.62,Glitch,,0,0,0,,{\\fad(0,0)\\pos(640,330)}ПЕРЕХВАТ ТРАНСЛЯЦИИ
Dialogue: 0,0:00:09.02,0:00:09.62,Small,,0,0,0,,{\\fad(0,0)\\pos(640,392)}SOURCE: INTERNAL LEAK · AGI MEMO #1
"""


def build_ass():
    subs = [
        (9.55, 13.25, LINES[0][2]),
        (13.45, 16.75, LINES[1][2]),
        (16.95, 19.55, LINES[2][2]),
        (19.75, 21.60, "Продолжение — на вашем рабочем столе."),
    ]
    body = ASS
    for a, b, txt in subs:
        body += "Dialogue: 0,%s,%s,Sub,,0,0,0,,{\\fad(120,160)}%s\n" % (
            ass_time(a),
            ass_time(b),
            txt,
        )
    path = os.path.join(BUILD, "subs.ass")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print("subs ->", path)
    return path


def ass_time(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def build_video(audio, subs):
    out = os.path.join(OUT, "Altman_RAM_interview.mp4")
    fc = (
        "[0:v]crop=720:500:0:30,scale=720:500,setsar=1[fg];"
        "[0:v]crop=720:500:0:30,scale=1280:720:force_original_aspect_ratio=increase,"
        "crop=1280:720,gblur=sigma=42,eq=brightness=-0.50:saturation=0.55[bg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        "drawbox=enable='between(t,9.02,9.60)':color=0xB0000000:t=fill,"
        "drawbox=enable='between(t,9.10,9.35)':y=40:h=90:color=red@0.25:t=fill,"
        "ass=subs.ass[v]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-stream_loop",
        "-1",
        "-i",
        SRC,
        "-i",
        audio,
        "-filter_complex",
        fc,
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-t",
        str(TOTAL),
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", cwd=BUILD)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(1)
    print("video ->", out, "%.1f MB" % (os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    a = build_audio()
    s = build_ass()
    build_video(a, s)
