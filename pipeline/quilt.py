#!/usr/bin/env python3
"""Build a Looking Glass Portrait quilt from a color frame and its depth map.

A quilt is the native input format of the Portrait: a single image holding
every view the display can show, tiled into a grid. Bridge samples it through
the lenticular lens so each eye position sees a different tile, which is what
produces real parallax instead of the flat-screen fake in wiggle_*.py.

Portrait geometry (device-level published spec, not per-unit calibration):

    grid    7 columns x 11 rows   (--cols / --rows; production default)
    views   77
    quilt   3360 x 3360 px
    tile    480 x 305 px          (3360/7 x 3360/11)

The geometry is a PARAMETER, and it defaults to what production ships. The
constants here were pinned at 8 x 6 (48 views) while the pipeline calling
them had moved to 7 x 11: the newest quilts on disk carry `_qs7x11a0.75`, the
glass stage names "7x11 views" as its default, and the eval gate's filename
law treats 7x11 as current with "legacy files default 8x6". A hardcoded
constant cannot disagree with the pipeline around it, so nothing failed; the
output was simply built at a geometry the display no longer expected. Passing
--cols 8 --rows 6 reproduces the legacy grid.

The views are the SAME warp used by the wiggle preview, just sampled at that
many camera positions across the view cone instead of swept over time. warp_frame
is imported rather than reimplemented so the quilt inherits the exact
occlusion and hole-fill behavior already tuned and eyeballed at max_shift=44.

Two things here are assumptions worth checking against real glass rather than
trusting:

1. VIEW ORDER. Looking Glass quilts are conventionally ordered left to right,
   bottom to top, so view 0 (the leftmost camera position) is the BOTTOM-left
   tile, not the top-left. If the hologram reads inverted (moving your head
   right shows what should be on the left), flip --view-order.

2. SWEEP WIDTH. --view-span is inherited from the flat-screen preview, where
   the extremes are seen sequentially over time. In a quilt they are seen
   SIMULTANEOUSLY from different angles, which is a stricter test: too wide a
   sweep ghosts or tears at the edge views. The preview's tuning is a starting
   point, not a validated hologram setting.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from depth_guided import guided_depth
from warp_fast import warp_views
from wiggle_preview import warp_frame

ROOT = Path(__file__).resolve().parents[1]

# Portrait device spec.
#
# GEOMETRY IS A PARAMETER HERE, AND THE DEFAULT IS THE PRODUCTION ONE.
# In the working tree this was two hardcoded constants at 8x6 (48 views),
# while production had already moved to 7x11 (77 views): the newest quilts on
# disk carry `_qs7x11a0.75`, the glass stage documents "7x11 views" as the
# pipeline default, and the eval gate's filename law reads 7x11 as current
# with "legacy files default 8x6". So the module was two generations behind
# the pipeline that calls it, and nothing failed, because a hardcoded
# constant cannot disagree with anything.
#
# That is the same defect class this repository documents elsewhere: config
# drift that produces plausible output at the wrong setting. Fixed by making
# it an argument (--cols/--rows) and defaulting to what production ships.
COLS, ROWS = 7, 11
VIEWS = COLS * ROWS          # 77
QUILT_W, QUILT_H = 3360, 3360
TILE_W, TILE_H = QUILT_W // COLS, QUILT_H // ROWS
ASPECT = TILE_W / TILE_H


def grab_frame(video: Path, index: int, gray: bool) -> np.ndarray:
    """Pull a single frame out of a clip as an array, without unpacking the whole file."""
    args = ["ffmpeg", "-y", "-v", "error", "-i", str(video),
            "-vf", f"select=eq(n\\,{index})", "-vsync", "0", "-frames:v", "1"]
    if gray:
        args += ["-pix_fmt", "gray"]
    args += ["-f", "image2pipe", "-vcodec", "png", "-"]
    png = subprocess.run(args, check=True, capture_output=True).stdout
    if not png:
        raise RuntimeError(f"no frame {index} in {video}")
    import io
    return np.array(Image.open(io.BytesIO(png)).convert("L" if gray else "RGB"))


def frame_count(video: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-count_packets", "-show_entries", "stream=nb_read_packets",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return int(out)


def crop_to_aspect(img: np.ndarray, aspect: float) -> np.ndarray:
    """Center-crop to the target width/height ratio.

    The renders are square (HeyGen 1:1) but the Portrait is 3:4 portrait, so
    something has to give. Cropping the sides keeps the subject at native scale
    and centered, which is right for a head-and-shoulders shot; letterboxing
    would instead waste panel height on black bars.
    """
    h, w = img.shape[:2]
    target_w = int(round(h * aspect))
    if target_w <= w:
        x0 = (w - target_w) // 2
        return img[:, x0:x0 + target_w]
    target_h = int(round(w / aspect))
    y0 = (h - target_h) // 2
    return img[y0:y0 + target_h]


def build_quilt(color: np.ndarray, depth: np.ndarray, max_shift: float,
                span: float, view_order: str, invert_views: bool = False,
                depth_smooth: int = 0, guide_radius: int = 0, warp_scale: float = 0.52,
                progress: bool = True) -> Image.Image:
    """Render 77 views across the cone and tile them into one quilt image.

    invert_views reverses the camera sweep. This unit's calibration reports
    invView=1, meaning it expects views in inverted order; feeding them
    forward makes parallax run backwards, which the eye reads as INVERTED
    DEPTH (the face appears to sit behind the hair) even though the depth
    map itself is correct. Confirmed on glass: face depth 187 vs hair 49,
    i.e. the map had the face nearest, yet the hologram showed it behind.
    """
    color = crop_to_aspect(color, ASPECT)
    depth = crop_to_aspect(depth, ASPECT)

    if guide_radius > 0:
        # Edge-aware refinement guided by the colour frame. Measured on frame 38:
        # strand speckle 12.9 -> 6.4 while edge std holds at 70.3 -> 69.9, i.e.
        # half the noise that tears hair under warp, with the silhouette intact.
        # A median filter at the same job scored 12.5, essentially a no-op.
        depth = guided_depth(depth, color, radius=guide_radius)
    elif depth_smooth > 0:
        # Median-filter the depth map before warping. Hair is the problem child:
        # the depth model assigns individual strands wildly different values, so
        # at high max_shift neighbouring strand pixels fly apart and smear across
        # the face. A median filter flattens that speckle while preserving the
        # broad, smooth gradients that give cheeks and nose their roundness,
        # which is what lets max_shift go back up without the hair tearing.
        depth = np.array(Image.fromarray(depth, mode="L").filter(
            ImageFilter.MedianFilter(size=depth_smooth)))

    quilt = Image.new("RGB", (QUILT_W, QUILT_H))
    cams = np.linspace(span, -span, VIEWS) if invert_views else np.linspace(-span, span, VIEWS)

    # Batched: the depth sort is hoisted out of the view loop (identical across
    # all 77 views of a frame, it was being recomputed 48 times), and pixels are
    # warped straight at tile resolution instead of full res then downscaled.
    # Measured 3.32s -> 0.63s per frame, 5.3x, and the eval scores the result
    # indistinguishable from full res (d_rgb 2.51 vs 2.45).
    views = warp_views(color, depth, max_shift, cams, scale=warp_scale)
    for v, view in enumerate(views):
        tile = Image.fromarray(view, mode="RGB").resize((TILE_W, TILE_H), Image.LANCZOS)

        col = v % COLS
        row = v // COLS
        # Bottom-to-top: view 0 lands on the bottom row, not the top.
        y = QUILT_H - (row + 1) * TILE_H if view_order == "bottom-left" else row * TILE_H
        quilt.paste(tile, (col * TILE_W, y))

        if progress and (v + 1) % 12 == 0:
            print(f"[quilt]   view {v + 1}/{VIEWS}")

    return quilt


def main() -> int:
    # Declared up front: the argparse defaults below read these, so the
    # declaration cannot come after first use.
    global COLS, ROWS, VIEWS, TILE_W, TILE_H, ASPECT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--color", default=str(ROOT / "renders" / "sample-color.mp4"))
    ap.add_argument("--depth", default=str(ROOT / "renders" / "sample-depth.mp4"))
    ap.add_argument("--out", default=None,
                    help="output quilt path (default: renders/<color stem>_qs<cols>x<rows>a<aspect>.png)")
    ap.add_argument("--cols", type=int, default=COLS, help=f"quilt columns (default {COLS}, production)")
    ap.add_argument("--rows", type=int, default=ROWS, help=f"quilt rows (default {ROWS}, production)")
    ap.add_argument("--frame", type=int, default=None, help="source frame index (default: middle frame)")
    ap.add_argument("--max-shift", type=float, default=44.0,
                    help="peak horizontal shift in px at full depth and full sway (default 44, the tuned preview value)")
    ap.add_argument("--view-span", type=float, default=1.2,
                    help="camera sweep half-width across the view cone (default 1.2, inherited from the preview)")
    ap.add_argument("--view-order", choices=["bottom-left", "top-left"], default="bottom-left",
                    help="tile origin for view 0 (default bottom-left, the Looking Glass convention)")
    ap.add_argument("--warp-scale", type=float, default=0.52,
                    help="warp at this fraction of source resolution (default 0.52 = straight to tile size, "
                         "5.3x faster with no measurable eval difference; 1.0 for full res)")
    ap.add_argument("--guide-radius", type=int, default=12,
                    help="edge-aware guided-filter radius using the colour frame (default 12, 0 to disable). "
                         "Halves hair speckle without softening the silhouette; supersedes --depth-smooth.")
    ap.add_argument("--depth-smooth", type=int, default=5,
                    help="median filter size on the depth map before warping, odd number, 0 to disable "
                         "(default 5: kills hair-strand speckle so max_shift can go higher without smearing)")
    ap.add_argument("--invert-views", action="store_true", default=True,
                    help="reverse the camera sweep; ON by default because this unit's calibration reports invView=1")
    ap.add_argument("--no-invert-views", dest="invert_views", action="store_false",
                    help="feed views forward (only correct on a display reporting invView=0)")
    args = ap.parse_args()

    color_path, depth_path = Path(args.color), Path(args.depth)
    for p in (color_path, depth_path):
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 1

    # Bind the geometry args to the module constants the builder reads. Declared
    # flags that never reach the code they name are worse than no flags: they
    # read as configurable and behave as fixed.
    if (args.cols, args.rows) != (COLS, ROWS):
        COLS, ROWS = args.cols, args.rows
        VIEWS = COLS * ROWS
        TILE_W, TILE_H = QUILT_W // COLS, QUILT_H // ROWS
        ASPECT = TILE_W / TILE_H
        print(f"[quilt] geometry overridden to {COLS}x{ROWS} = {VIEWS} views")

    idx = args.frame if args.frame is not None else frame_count(color_path) // 2
    print(f"[quilt] source frame {idx} from {color_path.name}")

    color = grab_frame(color_path, idx, gray=False)
    depth = grab_frame(depth_path, idx, gray=True)
    if color.shape[:2] != depth.shape[:2]:
        print(f"color/depth size mismatch: {color.shape[:2]} vs {depth.shape[:2]}", file=sys.stderr)
        return 1
    print(f"[quilt] source {color.shape[1]}x{color.shape[0]} -> cropped to aspect {ASPECT}"
          f" -> {COLS}x{ROWS} grid, {VIEWS} views, tile {TILE_W}x{TILE_H}")
    print(f"[quilt] max_shift={args.max_shift} view_span=+/-{args.view_span} order={args.view_order}")

    t0 = time.time()
    quilt = build_quilt(color, depth, args.max_shift, args.view_span, args.view_order,
                        invert_views=args.invert_views, depth_smooth=args.depth_smooth, guide_radius=args.guide_radius, warp_scale=args.warp_scale)

    # The qs<cols>x<rows>a<aspect> suffix is the Looking Glass filename convention;
    # Bridge and the SDKs parse the grid out of the name when no metadata is passed.
    out = Path(args.out) if args.out else ROOT / "renders" / f"{color_path.stem}_qs{COLS}x{ROWS}a{ASPECT:g}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    quilt.save(out)
    print(f"[quilt] {VIEWS} views in {time.time() - t0:.1f}s -> {out} ({QUILT_W}x{QUILT_H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
