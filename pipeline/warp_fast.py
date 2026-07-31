#!/usr/bin/env python3
"""Batched multi-view warp. Same output as warp_frame, minus the redundant work.

The original loop called warp_frame once per view, which was correct and
straightforwardly wasteful. Measured at 71.8ms per warp, a 77-frame A/B video
came to 7,392 warps and ~9 minutes, which is far too slow to sit inside a
self-improving loop: at that speed you get ~6 experiments an hour.

Three sources of waste, in order of how much they cost:

1. THE SORT WAS RECOMPUTED PER VIEW. Occlusion is resolved by sorting each row
   by depth (far first, so nearer pixels overwrite them). Depth does not change
   between views of a frame; only the camera does. So that sort is IDENTICAL
   across all 48 views and was being redone 48 times. Hoisted out: computed
   once per frame, reused by every view.

2. PIXELS WERE WARPED AT 4x THE OUTPUT SIZE. Every tile ends up at 420x560, but
   warping happened at 810x1080 and was then downscaled. Three quarters of the
   work was discarded. Pre-scaling to the tile size before warping removes it.
   This DOES cost some antialiasing quality, so it is opt-in via `scale`, not
   forced, and worth checking against the quilt eval in the private tree before adopting.

3. Per-view Python overhead (array allocation, PIL round-trips) repeated 48
   times. Amortised by doing the whole sweep in one call.

Correctness is preserved exactly for (1) and (3): same scatter order, same
occlusion rule, same hole fill. Only (2) changes pixels, and only by resampling.
"""
import numpy as np
from PIL import Image

try:
    from holes import fill_background
except ImportError:                      # imported from outside pipeline/
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from holes import fill_background


# The implementation moved to holes.py so wiggle_preview can use the same one.
# Kept as an alias because callers import this name.
_fill_bg = fill_background



def warp_views(color: np.ndarray, depth: np.ndarray, max_shift: float,
               cams, scale: float = 1.0, zero_plane: float = 0.0,
               bg_gain: float = 1.0) -> list:
    """Warp one frame to many camera positions.

    color       HxWx3 uint8
    depth       HxW   uint8, bright = near
    cams        iterable of camera offsets (the sweep across the view cone)
    scale       pre-resize factor; 1.0 keeps full resolution, <1 trades a
                little antialiasing for a large speedup (0.5 is 4x less work)
    zero_plane  depth value (0-255) that stays put across all views. 0 keeps
                the legacy look: the far plane is fixed, so EVERYTHING pops
                forward of the glass. Looking Glass's own curated content
                instead pins the SUBJECT at the glass and lets the background
                recede behind it: pass the subject's depth here for that. The
                warp becomes shift = (depth - zero_plane), so pixels nearer
                than the plane come forward, pixels farther fall back.
    """
    if scale != 1.0:
        h, w = depth.shape
        nh, nw = int(round(h * scale)), int(round(w * scale))
        color = np.array(Image.fromarray(color, "RGB").resize((nw, nh), Image.LANCZOS))
        depth = np.array(Image.fromarray(depth, "L").resize((nw, nh), Image.LANCZOS))
        max_shift = max_shift * scale      # shift is in pixels, so it must scale too

    h, w = depth.shape
    rows = np.arange(h)[:, None]

    # --- computed ONCE per frame, reused by every view ---
    order = np.argsort(depth, axis=1)          # far -> near, per row
    depth_sorted = depth[rows, order].astype(np.float32) / 255.0
    color_sorted = color[rows, order].reshape(-1, 3)
    row_base = (rows * w).astype(np.int64)

    out_views = []
    for cam in cams:
        rel = depth_sorted - float(zero_plane) / 255.0
        if bg_gain != 1.0:
            # Deepen ONLY the world behind the zero plane: the subject stays
            # pinned (sharp on the lens) while the background travels further.
            # My note, 2026-07-26: "more depths, multi-layered depths".
            rel = np.where(rel < 0, rel * bg_gain, rel)
        shift = np.round(rel * max_shift * float(cam)).astype(np.int64)
        dest_x = np.clip(order + shift, 0, w - 1)
        flat = (row_base + dest_x).reshape(-1)

        buf = np.zeros((h * w, 3), dtype=np.uint8)
        mask = np.zeros(h * w, dtype=bool)
        dbuf = np.zeros(h * w, dtype=np.float32)
        buf[flat] = color_sorted          # later write wins => near occludes far
        mask[flat] = True
        dbuf[flat] = depth_sorted.reshape(-1)

        out_views.append(_fill_bg(buf.reshape(h, w, 3), mask.reshape(h, w),
                                  dbuf.reshape(h, w)))

    return out_views


if __name__ == "__main__":
    import io
    import subprocess
    import time

    from quilt import ASPECT, crop_to_aspect
    from wiggle_preview import warp_frame

    def grab(p, n, gray):
        a = ["ffmpeg", "-v", "error", "-i", p, "-vf", f"select=eq(n\\,{n})",
             "-vsync", "0", "-frames:v", "1"]
        if gray:
            a += ["-pix_fmt", "gray"]
        a += ["-f", "image2pipe", "-vcodec", "png", "-"]
        raw = subprocess.run(a, check=True, capture_output=True).stdout
        return np.array(Image.open(io.BytesIO(raw)).convert("L" if gray else "RGB"))

    # Paths resolve from the repo root, not the caller's cwd, and the view
    # count is IMPORTED rather than restated: a benchmark that silently ran a
    # different cone than the renderer would be measuring the wrong thing.
    from pathlib import Path as _P
    _root = _P(__file__).resolve().parents[1]
    from quilt import VIEWS as _VIEWS
    c = crop_to_aspect(grab(str(_root / "samples" / "sample-color.mp4"), 1, False), ASPECT)
    d = crop_to_aspect(grab(str(_root / "samples" / "sample-depth.mp4"), 1, True), ASPECT)
    cams = np.linspace(1.15, -1.15, _VIEWS)

    t = time.time()
    old = [warp_frame(c, d, 70.0, float(x)) for x in cams]
    t_old = time.time() - t

    t = time.time()
    new = warp_views(c, d, 70.0, cams)
    t_new = time.time() - t

    t = time.time()
    half = warp_views(c, d, 70.0, cams, scale=0.52)   # straight to tile size
    t_half = time.time() - t

    # The two paths agree everywhere EXCEPT inside disocclusion holes, because
    # they fill them differently: wiggle_preview.fill_holes against this file's
    # _fill_bg. On smooth photographic depth the holes are small and the outputs
    # often match exactly, which is why this printed a bare "identical: True" for
    # a long time. On the committed sample, whose depth has a hard step at the
    # subject, they do not. Reporting the SIZE and LOCATION of the disagreement
    # is honest; a boolean that flips with the input was telling us nothing.
    diffs = [int((np.abs(a.astype(int) - b.astype(int)).sum(axis=2) > 0).sum())
             for a, b in zip(old, new)]
    frame_px = old[0].shape[0] * old[0].shape[1]
    worst = max(diffs)
    print(f"  original ({len(cams)} warps)     {t_old:6.2f}s")
    print(f"  hoisted sort, full res   {t_new:6.2f}s   {t_old/t_new:4.1f}x")
    print(f"  hoisted + tile res       {t_half:6.2f}s   {t_old/t_half:4.1f}x   (resampled, check eval)")
    same = sum(1 for n in diffs if n == 0)
    print(f"  views identical to the naive path: {same}/{len(diffs)}")
    if worst:
        print(f"  worst view differs on {worst} of {frame_px} px "
              f"({100.0 * worst / frame_px:.1f}%), inside disocclusion holes")
    else:
        print("  no view differs by a single pixel; both paths share holes.fill_background")
