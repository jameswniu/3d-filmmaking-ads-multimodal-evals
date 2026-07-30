#!/usr/bin/env python3
"""Build a Looking Glass quilt VIDEO: one quilt per source frame.

Same geometry and warp as quilt.py, applied per frame instead of to a single
still, then encoded as an mp4 that Bridge's player accepts directly. The
source clip's own audio is muxed back on so she actually speaks.

GEOMETRY IS IMPORTED, NEVER RESTATED. COLS and ROWS come from quilt.py, so
this file cannot drift away from the renderer the way its own docstring once
did: it described an 8x6 / 48-view build while importing the corrected 7x11 /
77-view constants, and nothing failed, because prose has no way to disagree
with the code beside it. Any view count mentioned here would be a second
source of truth, so there isn't one.

Cost note: every output frame costs COLS*ROWS warps, so this is that many times
the work of a single still. Roughly 4s per frame on an M4 Max at the legacy
48-view geometry, and it scales with the view count, i.e. minutes for even a
short clip. That is why this is a separate entry point rather than a flag on
quilt.py: you tune on stills, then commit to a video render once the look is
settled.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from quilt import ASPECT, COLS, ROWS, build_quilt
from wiggle_preview import extract_frames, load_stack, run_ffmpeg

ROOT = Path(__file__).resolve().parents[1]


def probe_fps(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    num, _, den = out.partition("/")
    return float(num) / float(den or 1)


def has_audio(video: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_type",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True,
    ).stdout.strip()
    return out == "audio"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--color", default=str(ROOT / "renders" / "sample-color.mp4"))
    ap.add_argument("--depth", default=str(ROOT / "renders" / "sample-depth.mp4"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-shift", type=float, default=46.0)
    ap.add_argument("--view-span", type=float, default=1.15)
    ap.add_argument("--depth-smooth", type=int, default=5)
    ap.add_argument("--no-invert-views", dest="invert_views", action="store_false", default=True)
    ap.add_argument("--keep-work", action="store_true")
    args = ap.parse_args()

    color_path, depth_path = Path(args.color), Path(args.depth)
    for p in (color_path, depth_path):
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 1

    fps = probe_fps(color_path)
    out_path = Path(args.out) if args.out else \
        ROOT / "renders" / f"{color_path.stem}_qs{COLS}x{ROWS}a{ASPECT:g}.mp4"

    work = ROOT / "state" / "quilt-video" / time.strftime("%Y%m%d-%H%M%S")
    print(f"[quilt-vid] extracting frames -> {work}")
    color_paths = extract_frames(color_path, work / "color", gray=False)
    depth_paths = extract_frames(depth_path, work / "depth", gray=True)
    if len(color_paths) != len(depth_paths):
        print(f"frame count mismatch: {len(color_paths)} vs {len(depth_paths)}", file=sys.stderr)
        return 1

    n = len(color_paths)
    print(f"[quilt-vid] {n} frames x {COLS*ROWS} views, fps={fps}, "
          f"max_shift={args.max_shift} span={args.view_span} smooth={args.depth_smooth} "
          f"invert={args.invert_views}")

    color_stack = load_stack(color_paths, "RGB")
    depth_stack = load_stack(depth_paths, "L")

    qdir = work / "quilts"
    qdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for i in range(n):
        q = build_quilt(color_stack[i], depth_stack[i], args.max_shift, args.view_span,
                        "bottom-left", invert_views=args.invert_views,
                        depth_smooth=args.depth_smooth, progress=False)
        q.save(qdir / f"q_{i + 1:05d}.png", compress_level=1)
        if (i + 1) % 5 == 0 or i + 1 == n:
            el = time.time() - t0
            print(f"[quilt-vid]   {i + 1}/{n}  ({el:.0f}s elapsed, ~{el / (i + 1) * (n - i - 1):.0f}s left)")

    silent = work / "silent.mp4"
    print(f"[quilt-vid] encoding -> {silent}")
    run_ffmpeg(["-framerate", str(fps), "-i", str(qdir / "q_%05d.png"),
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(silent)])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if has_audio(color_path):
        print("[quilt-vid] muxing original audio (she needs to be heard)")
        run_ffmpeg(["-i", str(silent), "-i", str(color_path),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-shortest", str(out_path)])
    else:
        print("[quilt-vid] source has no audio track, writing video only")
        shutil.copy(silent, out_path)

    print(f"[quilt-vid] done in {time.time() - t0:.0f}s -> {out_path}")
    if not args.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
