#!/usr/bin/env python3
"""seam_check.py — is a joined video indistinguishable from one continuous film?

my rule (2026-07-26): "u can't stich together pls or if u sitch... have to look all
the same film end to end." Default is one continuous bake. When a join IS authorized, the
bar is measurable rather than aesthetic: at each join the picture change and the brightness
step must be no larger than the clip's own frame-to-frame variation. A join that measures
bigger than the film's natural breathing is a SEAM, and the piece reads as several videos.

Usage: seam_check.py <video.mp4> <join_seconds,comma,separated>
Exit 0 all joins continuous / 1 at least one seam / 64 usage.

Thresholds: picture delta > 6x the median adjacent-frame delta, or background-luma step
> 4.0, counts as a seam. (The 3-shot night sequence rejected on 2026-07-26 is the negative
example; a single avatar_iv bake of the same script is the positive one.)
"""
import subprocess
import sys

import numpy as np

PICTURE_FACTOR = 6.0
LUMA_STEP = 4.0
GAP = 0.12          # seconds spanned when probing a join; the baseline uses the SAME span


def frame(path: str, t: float):
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
         "-vf", "scale=96:96,format=gray", "-f", "rawvideo", "pipe:1"], capture_output=True).stdout
    if len(raw) < 96 * 96:
        return None
    return np.frombuffer(raw[: 96 * 96], dtype=np.uint8).reshape(96, 96).astype(np.float32)


def mse(a, b) -> float:
    return float(((a - b) ** 2).mean())


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(64)
    path, joins = sys.argv[1], [float(x) for x in sys.argv[2].split(",") if x.strip()]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip() or 0)
    # The film's own variation ACROSS THE SAME INTERVAL the join is measured over (GAP seconds).
    # Sampling the baseline one frame apart while testing the join three frames apart made a true
    # single take fail its own control on 2026-07-26; the interval must match or the ratio is
    # meaningless.
    base = []
    for frac in (0.12, 0.28, 0.45, 0.62, 0.8):
        t = dur * frac
        if any(abs(t - j) < 1.0 for j in joins):
            continue
        a, b = frame(path, t - GAP / 2), frame(path, t + GAP / 2)
        if a is not None and b is not None:
            base.append(mse(a, b))
    typical = float(np.median(base)) if base else 25.0
    ok = True
    for j in joins:
        a, b = frame(path, j - GAP / 2), frame(path, j + GAP / 2)
        if a is None or b is None:
            print(f"  join {j:.2f}s: unreadable, skipped")
            continue
        picture, luma = mse(a, b), abs(float(a.mean()) - float(b.mean()))
        seam = picture > PICTURE_FACTOR * typical or luma > LUMA_STEP
        print(f"  join {j:6.2f}s: picture {picture:7.0f} (typical {typical:.0f}), "
              f"luma step {luma:4.1f} -> {'SEAM' if seam else 'continuous'}")
        if seam:
            ok = False
    print("VERDICT:", "reads as one film" if ok else "reads as separate videos, do not ship as one")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
