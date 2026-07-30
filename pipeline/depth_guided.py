#!/usr/bin/env python3
"""Edge-aware depth refinement, guided by the colour frame.

Why this exists, and why the median filter it replaces was never the right fix:

Depth Anything gives each hair strand its own wildly different depth value, and
the depth map's edges do not line up with the colour image's edges (monocular
models oversmooth exactly at boundaries). Forward-warping that map flings
neighbouring strand pixels apart, which is the smearing across the face. The
DIBR literature names this precisely: depth-edge / colour-edge misalignment,
worst on thin high-frequency structures like hair.

A median filter (what I used first) just blurs depth uniformly. It calms the
speckle but ALSO rounds off the real silhouette, so the head starts losing its
edge before the hair stops tearing.

A guided filter instead smooths depth *while borrowing the colour image's
edges*. Where the colour frame is flat (inside the hair mass, across a cheek)
it smooths hard; where colour has a real edge (the hairline against black) it
preserves it. So strand speckle collapses into one coherent volume and the
silhouette stays sharp, which is what lets the parallax go aggressive without
the hair coming apart.

Implementation is He et al.'s guided filter with a box filter built from
integral images, so it needs nothing beyond numpy (no cv2, no scipy).
"""
import numpy as np


def _box(img: np.ndarray, r: int) -> np.ndarray:
    """Mean over a (2r+1) square window, via integral image. O(n) regardless of r."""
    h, w = img.shape
    pad = np.pad(img, ((r + 1, r), (r + 1, r)), mode="edge")
    ii = pad.cumsum(0).cumsum(1)
    # corners of each window in the integral image
    a = ii[2 * r + 1:, 2 * r + 1:]
    b = ii[:h, 2 * r + 1:]
    c = ii[2 * r + 1:, :w]
    d = ii[:h, :w]
    area = (2 * r + 1) ** 2
    return (a - b - c + d) / area


def guided_depth(depth: np.ndarray, color: np.ndarray, radius: int = 12,
                 eps: float = 1e-3) -> np.ndarray:
    """Refine `depth` (HxW uint8) using `color` (HxWx3 uint8) as the edge guide.

    radius: window size. Bigger merges hair into a smoother single mass but
            starts pulling in the background; 8-16 is the useful band.
    eps:    edge sensitivity. SMALLER preserves more edges (less smoothing),
            larger smooths through weaker edges. 1e-3 keeps the hairline while
            flattening strand noise.
    """
    I = (0.2126 * color[..., 0] + 0.7152 * color[..., 1] + 0.0722 * color[..., 2]) / 255.0
    p = depth.astype(np.float64) / 255.0

    mean_I = _box(I, radius)
    mean_p = _box(p, radius)
    corr_I = _box(I * I, radius)
    corr_Ip = _box(I * p, radius)

    var_I = corr_I - mean_I * mean_I
    cov_Ip = corr_Ip - mean_I * mean_p

    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I

    q = _box(a, radius) * I + _box(b, radius)
    return (np.clip(q, 0.0, 1.0) * 255.0).astype(np.uint8)


if __name__ == "__main__":
    import argparse
    import io
    import subprocess
    from pathlib import Path

    from PIL import Image

    ap = argparse.ArgumentParser(description="Preview guided depth refinement on one frame.")
    ap.add_argument("--color", required=True)
    ap.add_argument("--depth", required=True)
    ap.add_argument("--frame", type=int, default=38)
    ap.add_argument("--radius", type=int, default=12)
    ap.add_argument("--out", default="/tmp/depth-guided-compare.png")
    args = ap.parse_args()

    def grab(path, n, gray):
        a = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{n})",
             "-vsync", "0", "-frames:v", "1"]
        if gray:
            a += ["-pix_fmt", "gray"]
        a += ["-f", "image2pipe", "-vcodec", "png", "-"]
        raw = subprocess.run(a, check=True, capture_output=True).stdout
        return np.array(Image.open(io.BytesIO(raw)).convert("L" if gray else "RGB"))

    c = grab(args.color, args.frame, False)
    d = grab(args.depth, args.frame, True)
    g = guided_depth(d, c, radius=args.radius)

    # Local variance in the depth map is the strand-speckle proxy: high variance
    # inside the hair is what tears under warp.
    def speckle(x):
        f = x.astype(np.float64)
        return float((_box(f * f, 3) - _box(f, 3) ** 2).mean())

    print(f"depth speckle (local variance)  before: {speckle(d):8.1f}   after: {speckle(g):8.1f}")
    print(f"edge preservation (std of map)  before: {d.std():8.1f}   after: {g.std():8.1f}")
    Image.fromarray(np.hstack([d, g])).save(args.out)
    print(f"side-by-side -> {args.out}")
