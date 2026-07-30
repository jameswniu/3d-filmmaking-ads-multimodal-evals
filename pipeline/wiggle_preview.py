#!/usr/bin/env python3
"""Depth-parallax "wiggle" preview: show a person clip's 3D pop on a flat screen.

Takes a color clip and a depth clip built frame for frame from it
(grayscale, near = bright, far = dark, the same convention as the rest of
this pipeline, see depth_infer.py) and renders a short looping video where
a virtual camera sways left and right. Near pixels (the face) shift more
than far pixels (the background), which is the whole point: a cheap, flat
screen stand in for the actual light field parallax the Portrait display
shows later, useful for eyeballing depth quality before committing to the
quilt stage.

Looping: the source frame index ping-pongs through the clip (a triangle
wave over the output frame count) so the subject's own motion loops
cleanly, and the camera sway is one plain sine cycle over that same
output period. Both close exactly on themselves (value at the last output
frame flows straight into the first), so the render loops with no jump cut.

Warp: a forward (scatter) warp, not a backward (gather) sample. Each
source pixel moves horizontally by round(norm_depth * MAX_SHIFT * cam),
then is painted into its destination column; where two source pixels land
on the same destination column, the nearer one wins, done per row via an
argsort by depth (far first, near last, so a later write beats an earlier
one at the same index, which lines up with real occlusion: near hides
far). Destination columns nobody lands on (background revealed behind a
pixel that just moved away) are holes, patched by the nearest horizontal
neighbor (forward filled left to right, then backward filled for any
leading run a row has nothing valid to draw from yet) so no column is
ever left black.
"""
import argparse
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def run_ffmpeg(extra_args: list) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + extra_args, check=True)


def extract_frames(video: Path, out_dir: Path, gray: bool) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_args = ["-i", str(video), "-vsync", "0"]
    if gray:
        ffmpeg_args += ["-pix_fmt", "gray"]
    ffmpeg_args.append(str(out_dir / "frame_%05d.png"))
    run_ffmpeg(ffmpeg_args)
    return sorted(out_dir.glob("frame_*.png"))


def load_stack(paths: list, mode: str) -> np.ndarray:
    return np.stack([np.array(Image.open(p).convert(mode)) for p in paths])


def ping_pong_index(t: int, out_frames: int, n_src: int) -> int:
    """Triangle wave: 0 to n_src-1 and back to 0 across one output loop."""
    phase = (t % out_frames) / out_frames
    tri = 1.0 - abs(2.0 * phase - 1.0)
    return int(round(tri * (n_src - 1)))


def camera_sway(t: int, out_frames: int) -> float:
    """One full sine cycle across the output loop: center, right, center, left, center."""
    return math.sin(2.0 * math.pi * t / out_frames)


def fill_holes(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Nearest horizontal neighbor fill.

    Forward fill (left to right) first; then, only for a row's leading run
    where the forward pass has no valid pixel yet to draw from, fall back
    to a backward fill (reverse the row, forward fill, reverse back).
    """
    h, w, _ = img.shape
    cols = np.arange(w)
    rows = np.arange(h)[:, None]

    idx_valid = np.where(mask, cols[None, :], 0)
    idx_fwd = np.maximum.accumulate(idx_valid, axis=1)
    fwd = img[rows, idx_fwd]

    mask_rev = mask[:, ::-1]
    img_rev = img[:, ::-1]
    idx_valid_rev = np.where(mask_rev, cols[None, :], 0)
    idx_fwd_rev = np.maximum.accumulate(idx_valid_rev, axis=1)
    bwd = img_rev[rows, idx_fwd_rev][:, ::-1]

    no_left_valid = np.cumsum(mask, axis=1) == 0
    return np.where(no_left_valid[..., None], bwd, fwd)


def warp_frame(color: np.ndarray, depth: np.ndarray, max_shift: float, cam: float) -> np.ndarray:
    """Forward-warp one frame: shift each pixel by its own depth times cam, nearer

    pixels (bright depth) move more than farther ones (dark depth). Per row,
    source columns are visited far to near (ascending depth argsort) so a later
    write overwrites an earlier one at any destination column two pixels land
    on together, i.e. near occludes far. Uncovered destination columns are
    filled by fill_holes above.
    """
    h, w = depth.shape
    norm_depth = depth.astype(np.float32) / 255.0
    shift = np.round(norm_depth * max_shift * cam).astype(np.int64)

    order = np.argsort(depth, axis=1)  # ascending depth per row: far first, near last
    rows = np.arange(h)[:, None]
    shift_sorted = shift[rows, order]
    dest_x = np.clip(order + shift_sorted, 0, w - 1)
    color_sorted = color[rows, order]

    flat_dest = (rows * w + dest_x).reshape(-1)
    out_flat = np.zeros((h * w, 3), dtype=np.uint8)
    mask_flat = np.zeros(h * w, dtype=bool)
    out_flat[flat_dest] = color_sorted.reshape(-1, 3)
    mask_flat[flat_dest] = True

    warped = out_flat.reshape(h, w, 3)
    mask = mask_flat.reshape(h, w)
    return fill_holes(warped, mask)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--color", default=str(ROOT / "renders" / "sample-color.mp4"))
    ap.add_argument("--depth", default=str(ROOT / "renders" / "sample-depth.mp4"))
    ap.add_argument("--out", default=str(ROOT / "renders" / "sample-parallax.mp4"))
    ap.add_argument("--still-left", default=str(ROOT / "renders" / "sample-parallaxL.png"))
    ap.add_argument("--still-right", default=str(ROOT / "renders" / "sample-parallaxR.png"))
    ap.add_argument("--frames", type=int, default=120, help="output frame count (default 120, 5s at 24fps)")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--max-shift", type=float, default=18.0, help="peak horizontal shift in px at full depth and full sway")
    ap.add_argument("--still-index", type=int, default=None, help="source frame index for the two preview stills (default: middle frame)")
    ap.add_argument("--stills-only", action="store_true", help="only render the two preview stills, skip the full loop and mp4 encode")
    ap.add_argument("--keep-work", action="store_true", help="keep the extracted/rendered scratch dir instead of deleting it")
    ap.add_argument("--work-dir", default=None, help="scratch dir for frames (default: state/wiggle-work/<timestamp>)")
    args = ap.parse_args()

    color_path = Path(args.color)
    depth_path = Path(args.depth)
    out_path = Path(args.out)
    still_left_path = Path(args.still_left)
    still_right_path = Path(args.still_right)

    for p in (color_path, depth_path):
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 1

    work_dir = Path(args.work_dir) if args.work_dir else ROOT / "state" / "wiggle-work" / time.strftime("%Y%m%d-%H%M%S")
    color_dir = work_dir / "color"
    depth_dir = work_dir / "depth"
    out_dir = work_dir / "out"

    print(f"[wiggle] extracting frames -> {work_dir}")
    color_paths = extract_frames(color_path, color_dir, gray=False)
    depth_paths = extract_frames(depth_path, depth_dir, gray=True)
    if len(color_paths) != len(depth_paths):
        print(f"frame count mismatch: color={len(color_paths)} depth={len(depth_paths)}", file=sys.stderr)
        return 1
    n_src = len(color_paths)
    print(f"[wiggle] {n_src} source frames")

    color_stack = load_stack(color_paths, "RGB")
    depth_stack = load_stack(depth_paths, "L")

    still_idx = args.still_index if args.still_index is not None else n_src // 2
    print(f"[wiggle] preview stills from source frame {still_idx}, max_shift={args.max_shift}")
    left = warp_frame(color_stack[still_idx], depth_stack[still_idx], args.max_shift, -1.0)
    right = warp_frame(color_stack[still_idx], depth_stack[still_idx], args.max_shift, 1.0)
    still_left_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(left, mode="RGB").save(still_left_path)
    Image.fromarray(right, mode="RGB").save(still_right_path)
    print(f"[wiggle] wrote {still_left_path}")
    print(f"[wiggle] wrote {still_right_path}")

    if args.stills_only:
        if not args.keep_work:
            shutil.rmtree(work_dir, ignore_errors=True)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for t in range(args.frames):
        src_idx = ping_pong_index(t, args.frames, n_src)
        cam = camera_sway(t, args.frames)
        frame = warp_frame(color_stack[src_idx], depth_stack[src_idx], args.max_shift, cam)
        Image.fromarray(frame, mode="RGB").save(out_dir / f"frame_{t + 1:05d}.png", compress_level=1)
        if (t + 1) % 30 == 0 or t + 1 == args.frames:
            print(f"[wiggle]   rendered {t + 1}/{args.frames}")
    print(f"[wiggle] rendered {args.frames} frames in {time.time() - t0:.1f}s")

    print(f"[wiggle] encoding -> {out_path} ({args.fps}fps, video only, no audio)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg([
        "-framerate", str(args.fps),
        "-i", str(out_dir / "frame_%05d.png"),
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        str(out_path),
    ])
    print(f"[wiggle] done -> {out_path}")

    if not args.keep_work:
        shutil.rmtree(work_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
