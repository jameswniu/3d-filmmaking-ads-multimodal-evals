#!/usr/bin/env python3
"""Per-frame monocular depth estimation for the pipeline's depth stage.

Reads a directory of color frame PNGs (same filenames throughout), runs a
Depth Anything V2 checkpoint (via transformers) on each one, and writes a
grayscale depth PNG per frame into an output directory. Called by
pipeline/depth.sh; not meant to be run standalone against a video file
directly, it wants already-extracted frames.

Looking Glass convention: near = bright, far = dark. Depth Anything V2
predicts relative INVERSE depth (larger raw value = closer to the camera),
which already matches that convention, confirmed empirically against known
background vs subject regions in the source clip, so this script does not
invert anything.

Normalization is two pass and GLOBAL, not per frame:
  1) run the model on every frame, keep the raw float depth map for each
  2) compute one low/high percentile pair across the WHOLE clip and rescale
     every frame with that same pair before quantizing to 8 bit

A per-frame min/max normalize (what the transformers pipeline gives you by
default via the "depth" output key) can flicker: the background and a
plain, low-contrast region (a dark top on a black background, for example)
sit close together in raw depth, so small frame to frame shifts in the
per-frame min/max stretch that gap differently each frame. A single global
range removes that flicker. It does not fix the underlying ambiguity where
the model has little texture to anchor on (see the depth.sh header and the
run report for what that looks like on this clip); this is a light,
one-parameter mitigation, not a segmentation or inpainting fix.

Only practical for short clips: every frame's raw depth stays in memory for
the second pass (a few hundred MB for a few hundred frames at 1080p). A
much longer clip would want a streaming or windowed version instead.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image


def resolve_device(requested: str) -> str:
    """"auto" picks mps when available (Apple Silicon), else cpu."""
    if requested != "auto":
        return requested
    import torch
    return "mps" if torch.backends.mps.is_available() else "cpu"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames-dir", required=True, help="directory of input color frame PNGs")
    ap.add_argument("--out-dir", required=True, help="directory to write depth frame PNGs (same filenames)")
    ap.add_argument("--model", default="depth-anything/Depth-Anything-V2-Large-hf", help="transformers model id")
    ap.add_argument("--device", default="auto", help="mps, cpu, or auto (default: auto)")
    ap.add_argument("--low-pct", type=float, default=1.0, help="lower percentile for the global normalize range")
    ap.add_argument("--high-pct", type=float, default=99.0, help="upper percentile for the global normalize range")
    ap.add_argument("--batch", type=int, default=1,
                    help="frames per forward pass (feeds the MPS GPU real batches; 1 = legacy per-frame)")
    ap.add_argument("--stride", type=int, default=1,
                    help="infer every Nth frame and linearly interpolate raw maps between anchors; "
                         "the quilt stage re-snaps edges per RGB frame via guided filtering, so "
                         "small strides are near-free on quality (1 = every frame)")
    args = ap.parse_args()

    device = resolve_device(args.device)
    frames_dir = Path(args.frames_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame_paths = sorted(frames_dir.glob("*.png"))
    if not frame_paths:
        print(f"no frames found in {frames_dir}", file=sys.stderr)
        return 1

    print(f"[depth_infer] device={device} model={args.model} frames={len(frame_paths)}")

    from transformers import pipeline  # deferred: heavy import, keep --help fast

    t0 = time.time()
    pipe = pipeline(task="depth-estimation", model=args.model, device=device)
    print(f"[depth_infer] model loaded in {time.time() - t0:.1f}s")

    n_all = len(frame_paths)
    stride = max(1, args.stride)
    sel = list(range(0, n_all, stride))
    if sel[-1] != n_all - 1:
        sel.append(n_all - 1)   # anchor the final frame: interpolate, never extrapolate

    def _to_map(out, img):
        arr = out["predicted_depth"].squeeze().to("cpu").float().numpy()
        if arr.shape != (img.height, img.width):
            arr = np.array(Image.fromarray(arr).resize((img.width, img.height), Image.BICUBIC))
        return arr

    raw_sel = []
    t0 = time.time()
    bsz = max(1, args.batch)
    for b0 in range(0, len(sel), bsz):
        chunk = sel[b0:b0 + bsz]
        imgs = [Image.open(frame_paths[si]).convert("RGB") for si in chunk]
        outs = pipe(imgs, batch_size=len(imgs)) if len(imgs) > 1 else [pipe(imgs[0])]
        for img, out in zip(imgs, outs):
            raw_sel.append(_to_map(out, img))
        done = min(b0 + bsz, len(sel))
        if done % 10 < bsz or done == len(sel):
            print(f"[depth_infer]   inferred {done}/{len(sel)} passes")
    print(f"[depth_infer] inference done in {time.time() - t0:.1f}s "
          f"(batch={bsz}, stride={stride}, passes={len(sel)}/{n_all} frames)")

    if stride == 1:
        raw = raw_sel
    else:
        # Linear interpolation of RAW maps between inferred anchors. Depth
        # fields drift slowly frame to frame; per-frame edge fidelity is
        # restored downstream by guided_depth against each RGB frame.
        raw = [None] * n_all
        for k, si in enumerate(sel):
            raw[si] = raw_sel[k]
        for k in range(len(sel) - 1):
            a, b = sel[k], sel[k + 1]
            for j in range(a + 1, b):
                w = (j - a) / (b - a)
                raw[j] = raw_sel[k] * (1.0 - w) + raw_sel[k + 1] * w

    stack = np.stack(raw)
    lo, hi = np.percentile(stack, [args.low_pct, args.high_pct])
    if hi <= lo:
        lo, hi = float(stack.min()), float(stack.max())
    print(f"[depth_infer] global normalize range: [{lo:.4f}, {hi:.4f}] (p{args.low_pct}/p{args.high_pct} over the whole clip)")

    for p, arr in zip(frame_paths, raw):
        norm = np.clip((arr - lo) / (hi - lo), 0.0, 1.0)
        img8 = (norm * 255.0 + 0.5).astype(np.uint8)
        Image.fromarray(img8, mode="L").save(out_dir / p.name)

    print(f"[depth_infer] wrote {len(frame_paths)} depth frames -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
