import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
src = os.path.join(
    "фото и видео",
    "Альтман_—_оперативка_лучше_в_дата_центрах_рус_озвучка,_оригинал.mp4",
)
out = os.path.join("ram_altman_game", "tools")
os.makedirs(out, exist_ok=True)
for t in (0.5, 4, 8, 15, 22, 30, 38, 44):
    dst = os.path.join(out, "vframe_%05.1f.jpg" % t)
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(t),
            "-i",
            src,
            "-frames:v",
            "1",
            "-vf",
            "scale=360:-1",
            dst,
        ],
        capture_output=True,
    )
    print(t, os.path.exists(dst), r.returncode)
