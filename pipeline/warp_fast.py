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
   forced, and worth checking against eval_quilt.py before adopting.

3. Per-view Python overhead (array allocation, PIL round-trips) repeated 48
   times. Amortised by doing the whole sweep in one call.

Correctness is preserved exactly for (1) and (3): same scatter order, same
occlusion rule, same hole fill. Only (2) changes pixels, and only by resampling.
"""
import numpy as np
from PIL import Image

from wiggle_preview import fill_holes  # noqa: F401  (legacy callers)


def _fill_bg(rgb, mask, dview):
    """Fill disocclusion holes from the BACKGROUND side only.

    Nearest-neighbor fill smears whichever pixel is closest, which at her
    silhouette is HER: outlines break first as budgets rise (budget 78 died
    there; MPI v1's cure was worse). A revealed gap is by definition showing
    what is BEHIND the subject, so of the two horizontal neighbors flanking a
    hole, copy the one whose depth is FARTHER. Same cost, right prior.
    """
    h, w = mask.shape
    idx = np.arange(w)[None, :].repeat(h, 0)
    # nearest valid index to the left / right of every pixel
    li = np.where(mask, idx, -1)
    li = np.maximum.accumulate(li, axis=1)
    ri = np.where(mask, idx, w)
    ri = np.minimum.accumulate(ri[:, ::-1], axis=1)[:, ::-1]
    rows = np.arange(h)[:, None]
    li_c = np.clip(li, 0, w - 1)
    ri_c = np.clip(ri, 0, w - 1)
    ld = np.where(li >= 0, dview[rows, li_c], np.inf)   # farther = smaller
    rd = np.where(ri < w, dview[rows, ri_c], np.inf)
    use_left = ld <= rd
    src = np.where(use_left, li_c, ri_c)
    out = rgb.copy()
    holes = ~mask
    out[holes] = rgb[rows.repeat(w, 1)[holes], src[holes]]
    return out


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

    c = crop_to_aspect(grab("../renders/sample-color.mp4", 38, False), ASPECT)
    d = crop_to_aspect(grab("../renders/sample-depth.mp4", 38, True), ASPECT)
    cams = np.linspace(1.15, -1.15, 48)

    t = time.time()
    old = [warp_frame(c, d, 70.0, float(x)) for x in cams]
    t_old = time.time() - t

    t = time.time()
    new = warp_views(c, d, 70.0, cams)
    t_new = time.time() - t

    t = time.time()
    half = warp_views(c, d, 70.0, cams, scale=0.52)   # straight to tile size
    t_half = time.time() - t

    same = all(np.array_equal(a, b) for a, b in zip(old, new))
    print(f"  original (48 warps)      {t_old:6.2f}s")
    print(f"  hoisted sort, full res   {t_new:6.2f}s   {t_old/t_new:4.1f}x   identical output: {same}")
    print(f"  hoisted + tile res       {t_half:6.2f}s   {t_old/t_half:4.1f}x   (resampled, check eval)")
