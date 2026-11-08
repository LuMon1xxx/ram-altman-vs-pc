import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
src = os.path.join(
    "фото и видео",
    "Альтман_—_оперативка_лучше_в_дата_центрах_рус_озвучка,_оригинал.mp4",
)
dst = os.path.join("ram_altman_game", "assets", "video")
os.makedirs(dst, exist_ok=True)

# crop away the burned-in captions -> square-ish talking head, 12 fps
cmd = [
    "ffmpeg",
    "-y",
    "-i",
    src,
    "-t",
    "36",
    "-vf",
    "crop=720:600:0:0,scale=480:400:flags=lanczos,fps=12",
    "-q:v",
    "4",
    os.path.join(dst, "f_%04d.jpg"),
]
r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
print("frames rc", r.returncode, r.stderr[-300:])

# original audio, first 14 seconds
cmd = [
    "ffmpeg",
    "-y",
    "-i",
    src,
    "-t",
    "14",
    "-vn",
    "-c:a",
    "libvorbis",
    "-q:a",
    "4",
    os.path.join("ram_altman_game", "assets", "video_audio.ogg"),
]
r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
print("audio rc", r.returncode, r.stderr[-200:])

files = sorted(os.listdir(dst))
total = sum(os.path.getsize(os.path.join(dst, f)) for f in files)
print("frames:", len(files), "total MB: %.1f" % (total / 1e6))
print(
    "audio MB: %.2f"
    % (
        os.path.getsize(os.path.join("ram_altman_game", "assets", "video_audio.ogg"))
        / 1e6
    )
)
