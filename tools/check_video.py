import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
src = os.path.join("ram_altman_game", "out", "Altman_RAM_interview.mp4")
out = os.path.join("ram_altman_game", "tools")
for t in (0.8, 5.0, 9.3, 12.0, 18.0, 20.5):
    dst = os.path.join(out, "vid_%04.1f.jpg" % t)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            str(t),
            "-i",
            src,
            "-frames:v",
            "1",
            "-vf",
            "scale=960:-1",
            dst,
        ],
        check=True,
    )
    print(t, os.path.getsize(dst))
r = subprocess.run(
    [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_name,width,height,channels",
        "-of",
        "default=noprint_wrappers=1",
        src,
    ],
    capture_output=True,
    text=True,
)
print(r.stdout)
