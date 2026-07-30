#!/usr/bin/env python3
"""Is the presenter distinguishable from the fill she is composited onto?

WHY THIS EXISTS. Twelve probes passed a clip that shipped a floating head. A
black top on a pure-black matte cleared the fill by 22 levels of luma where the
face cleared it by 134, so the torso dissolved. None of the twelve was broken:
eleven score the subject and the twelfth scores the backdrop, and this defect
lives in the CONTRAST BETWEEN THEM, which is nobody's property. Choosing the fill
colour and choosing the wardrobe are one decision, and the suite was arranged as
though they were two.

WHY IT DERIVES ITS REGIONS INSTEAD OF TAKING THEM AS CONSTANTS. The first version
of this check sampled a hardcoded box ("lower left corner is background, centre is
torso") and reported a confident FAIL on a clip that was fine, because at 1:1
cover framing the subject spans about 1030 of 1080 px at that height, so the
"background" box landed on her arm. That is the same failure this repository keeps
finding in itself: a constant cannot disagree with the image around it, so it
fails silently and in the confident direction. Nothing here is positional. The
fill is found by value, and the subject is whatever is not the fill.

METHOD
  1. The fill is the near zero cluster. It is not assumed to sit at any edge; a
     matted subject can touch every border, and this one does.
  2. The subject is the complement, ERODED inward. Erosion is not cosmetic: the
     matte boundary is anti-aliased, so a rim of genuinely dark pixels rings the
     subject at every silhouette edge. Including them drags the low percentile
     down and fails clips that are fine, which would make this probe noise and
     get it switched off, which is how a suite loses a check it needs.
  3. The reading is the SHARE OF THE SUBJECT that is nearly indistinguishable
     from the fill, not a brightness. A mean over a lit subject is dominated by
     the bright side and hides a dark garment entirely, which is the miss being
     fixed. A low percentile is better and still wrong: it reports the darkest
     part of her, and every lit subject has hair shadow and an unlit side of the
     neck, so it cannot tell a dissolved torso from ordinary shading. What the eye
     actually objects to is HOW MUCH of her disappears, so that is what is
     measured.

THRESHOLD. Bar 12 percent, derived from the two labelled points available, on the
same statistic it gates:

    accepted cream top clip     2.64 percent dissolved
    rejected black top clip    30.71 percent dissolved

n=2, and stated as n=2. The bar sits well clear of both, nearer the accepted clip,
because a false PASS ships a broken frame while a false FAIL costs one look
re-roll.

The first draft of this file got that wrong in a way worth recording, since it is
the mistake the repository is about. Its bar of 60 was derived from a torso box
MEAN (22.4 rejected against 165.4 accepted) and then applied to a fifth
PERCENTILE, a different statistic entirely. It duly failed a clip that was fine.
A threshold is only meaningful against the exact measurement it was derived from,
and carrying a number across a change of statistic is indistinguishable from
typing it from intuition.

Brightness percentiles are still reported below, and they do not gate. That split
is deliberate and is the same rule the rest of the suite follows.
docs/NOT-MEASURED.md records that the share of the look library which would fail
this is UNMEASURED.

Usage: separation_probe.py CLIP.mp4
Optional flags: "json" for machine output, "at" SECONDS to pick the sampled
frame, "bar" N to override the threshold. Each takes the usual CLI dash prefix.
Exit 0 pass, 1 fail, 2 could not measure.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

FILL_MAX = 2.0      # luma at or below this is the matte fill
ERODE_PX = 6        # inward margin discarding the anti-aliased silhouette rim
NEAR_FILL = 30.0    # within this many luma of the fill counts as dissolved
BAR_PCT = 12.0      # derived from 2.64 accepted vs 30.71 rejected, see docstring
PCTL = 5.0          # reported for context, never gates
MIN_FILL_FRAC = 0.02
MIN_SUBJ_PX = 5000


def _erode(mask: np.ndarray, r: int) -> np.ndarray:
    """Binary erosion by a square of side 2r+1, via separable rolling AND.

    numpy only, so this probe adds no dependency the suite does not already have.
    """
    out = mask
    for axis in (0, 1):
        acc = out
        for s in range(1, r + 1):
            acc = acc & np.roll(out, s, axis=axis) & np.roll(out, -s, axis=axis)
        out = acc
    return out


def measure(clip: str, at: float = 8.0) -> dict:
    with tempfile.TemporaryDirectory() as td:
        frame = str(Path(td) / "f.png")
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", clip, "-frames:v", "1", frame],
            capture_output=True,
        )
        if r.returncode != 0 or not Path(frame).exists():
            return {"error": f"could not read a frame at {at}s from {clip}"}
        a = np.asarray(Image.open(frame).convert("L"), dtype=float)

    fill_mask = a <= FILL_MAX
    fill_frac = float(fill_mask.mean())
    if fill_frac < MIN_FILL_FRAC:
        return {"error": f"no matte fill found ({100 * fill_frac:.2f}% at or below "
                         f"{FILL_MAX}); is this clip matted?", "fill_frac": fill_frac}

    interior = _erode(~fill_mask, ERODE_PX)
    if int(interior.sum()) < MIN_SUBJ_PX:
        return {"error": f"subject interior too small after {ERODE_PX}px erosion "
                         f"({int(interior.sum())} px)", "fill_frac": fill_frac}

    vals = a[interior]
    fill = float(a[fill_mask].mean())
    dissolved = 100.0 * float((vals < fill + NEAR_FILL).mean())
    return {
        "clip": clip, "at_s": at,
        "fill": fill, "fill_frac": fill_frac,
        "subject_px": int(interior.sum()),
        # the gating reading
        "dissolved_pct": dissolved, "bar_pct": BAR_PCT,
        "pass": bool(dissolved < BAR_PCT),
        # reported, never judged
        "subject_p5": float(np.percentile(vals, PCTL)),
        "subject_p25": float(np.percentile(vals, 25)),
        "subject_median": float(np.median(vals)),
    }


def main() -> int:
    argv = sys.argv[1:]
    positional = [x for x in argv if not x.startswith("-")]
    flags = [x for x in argv if x.startswith("-")]
    if not positional:
        print("usage: separation_probe.py CLIP.mp4", file=sys.stderr)
        return 2

    at, bar, as_json = 8.0, BAR_PCT, any(f.lstrip("-") == "json" for f in flags)
    for i, x in enumerate(argv):
        key = x.lstrip("-")
        if key == "at" and i + 1 < len(argv):
            at = float(argv[i + 1])
        if key == "bar" and i + 1 < len(argv):
            bar = float(argv[i + 1])

    m = measure(positional[0], at)
    if "error" in m:
        print(json.dumps(m) if as_json else f"separation: UNMEASURABLE, {m['error']}")
        return 2

    m["bar_pct"] = bar
    m["pass"] = bool(m["dissolved_pct"] < bar)
    if as_json:
        print(json.dumps(m))
    else:
        print(f"separation: {m['dissolved_pct']:.2f}% of subject within {NEAR_FILL:g} luma "
              f"of fill (bar {bar:g}%) -> {'PASS' if m['pass'] else 'FAIL'}   "
              f"[reported, not judged: fill {m['fill']:.1f} on "
              f"{100 * m['fill_frac']:.1f}% of frame, subject p5 {m['subject_p5']:.0f}, "
              f"p25 {m['subject_p25']:.0f}, median {m['subject_median']:.0f}]")
    return 0 if m["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
