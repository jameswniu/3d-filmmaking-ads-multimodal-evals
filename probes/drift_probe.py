#!/usr/bin/env python3
"""drift_probe.py <video.mp4> — motion DETECTOR for prop_gate.sh scan-drift.

WHAT THIS DOES AND DOES NOT DECIDE (2026-07-24). It measures whether the backdrop moves and
how. It does NOT decide whether that motion is acceptable, because the real test is not a pixel
count: "it has to be something that make sense -> ie, interaction with the subject which is eg the avatar
here. same as the cup fix i told you earlier." The cup was not fixed by removing it or by making
the steam constant, but by making the steam and HER REACTION cohere. Motion is the same - if the
frame claims she travelled, her body must deliver a gait, and a photo avatar has none. So use these
numbers as evidence that motion exists and in which direction, then answer the travel question in
`prop_gate.sh probe` about whether her body backs up what the scene is claiming.
Two of my rules died here and both are recorded so they are not re-derived: "any travel fails" was
over-scoped (banned camera moves I like), and "only reversals fail" was wrong (a smooth
BACKWARD pull-out is senseless too, because the absent gait is the problem, not the oscillation).

Answers ONE question: is the frozen backdrop moving? A photo avatar's backdrop is a still,
so its honest motion is exactly zero; anything else is the engine's synthetic camera travel
(2026-07-24: "still backward motion i can tell by the grass middle and the ground below").

WHY CORNERS, NOT MARGINS (calibrated 2026-07-24, and this fixes a real false-FAIL).
The first version sampled full-height left/right margins. Her HAIR reaches into those margins
at mid-height, so the diff sheet lit up with huge bright hair wedges on a clip whose backdrop
was provably static - the gate would have failed a good clip. Geometry separates them cleanly:
  - hair and hands live at MID height, beside her torso
  - the near-field ground/grass that actually dollies lives in the BOTTOM corners
  - the far plane (sky, open water) sits in the TOP corners
So probe the four corners and never the mid-height sides.

WHY BOTH NEAR AND FAR. The motion is layered: measured on the flagged clip, near-field grass
moved 23px while open ocean held under 2px. A far-corner-only probe would have called that
clip clean. Near corners carry the signal; far corners are the control.

TEXTURE GATE. Phase correlation needs structure. On a look whose backdrop is pure bokeh or open
water there is nothing to lock onto, and a confident-looking number there is noise. Such a corner
is reported INCONCLUSIVE rather than PASS, because "no texture" is not evidence of no motion -
that distinction is what stops this tool from lying in the reassuring direction.
"""
import sys

# CALIBRATED against my own eye on four clips (2026-07-24), which is the only ground truth
# that has been reliable on this class all session:
#   clip I FLAGGED (coastal wide)      near corners 39.5 / 53.8px  -> must FAIL
#   clip I did NOT flag (indoor take)   worst corner  8.8px         -> must PASS
#   frozen-by-construction control      every corner  0.0px         -> must PASS
# 8px failed the indoor take and so contradicted my calls; 12px reproduces all four of my calls with a wide
# margin (8.8 passes, 39.5 fails). Do not tighten below ~12 without re-checking against a clip
# I have actually judged, or the gate starts overruling the instrument it was calibrated on.
import os as _os
# THE DIAL. Overridable so prop_gate.sh can pass it per-run; the constant is only the default.
# Without reading the env the dial silently did nothing (caught 2026-07-24: a clip measuring 27.4px
# still failed at a 30px setting because the module constant won).
THRESH_PX = float(_os.environ.get("DRIFT_THRESH_PX", "12"))   # per-corner px that counts as travel
# TEMPLATE-MATCH QUALITY FLOOR, and it has to be HIGH (calibrated 2026-07-24 against clips I
# have judged). A genuine lock on a still backdrop scores ~1.00: draw B reads 1.000 on all four
# corners. A poor score means the matcher never found the patch and its reported position is a
# guess, which then LOOKS like huge travel. At a 0.30 floor those guesses became false FAILs on two
# clips I had accepted: the indoor take's bottom-right claimed 84.0px at quality 0.505, and the wall clip
# claimed 44.0px at 0.687. Both are noise. Only near-perfect locks are allowed to accuse a clip.
RESP_MIN = 0.90
SEARCH_PAD = 70        # px of search margin around each box; caps detectable travel at 70px
REVERSAL_DEADBAND = 3.0  # px of jitter to ignore before calling a direction change real
TEX_MIN = 10.0         # Laplacian variance below this = genuinely flat, nothing to lock onto
WORK = 720

CORNERS = [
    ("bottom-left  (near)", (0.02, 0.72, 0.22, 0.96)),
    ("bottom-right (near)", (0.78, 0.72, 0.98, 0.96)),
    ("top-left     (far) ", (0.02, 0.03, 0.20, 0.20)),
    ("top-right    (far) ", (0.80, 0.03, 0.98, 0.20)),
]
SAMPLE_TIMES = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 64
    # Optional second arg: the declared motion intent (prop_gate.sh intent). The verdict turns on
    # PROVENANCE, not appearance: motion that was asked for is a shot, the identical motion
    # unrequested is jank. Absent an intent we can only report, never judge.
    declared = (sys.argv[2] if len(sys.argv) > 2 else "").lower()
    wants_static = any(k in declared for k in ("static", "locked", "no push", "no dolly", "no zoom",
                                               "no pull", "no travel", "still"))
    wants_motion = any(k in declared for k in ("push-in", "push in", "dolly", "zoom", "pull", "travel"))
    # NEGATION: a brief saying "no push-in, no dolly, no zoom" contains every motion keyword while
    # asking for the exact opposite. Read naively it inverts the verdict - caught on the seawall clip,
    # where a locked-camera brief was reported as "the brief asked for camera movement". Static wins
    # whenever both appear, because that phrasing is how a static brief is actually written.
    if wants_static:
        wants_motion = False
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("drift_probe: numpy/cv2 unavailable - numeric arm skipped, judge the sheets by eye")
        return 0

    cap = cv2.VideoCapture(sys.argv[1])
    if not cap.isOpened():
        print(f"drift_probe: cannot open {sys.argv[1]}", file=sys.stderr)
        return 64
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(cv2.resize(f, (WORK, WORK), interpolation=cv2.INTER_AREA),
                                   cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    if len(frames) < 10:
        print("drift_probe: too few frames", file=sys.stderr)
        return 69

    # LETTERBOX / PILLARBOX DETECTION (added 2026-07-24 after this tool certified three padded
    # renders as "0.0px, pixel-exactly clean"). HeyGen pads to the requested aspect when the source
    # still is a different shape - ask for 1:1 from a landscape look without fit="cover" and you get
    # 484 rows of flat white (value 245, std 0.0) top and bottom of a 1080 frame, leaving real
    # content only in y=242..837. The corner boxes then sample PADDING, which is static by
    # construction, so the probe reports a perfect pass while the actual backdrop may be pacing hard.
    # That is the same false-negative class as the phase-correlation bug: the tool lying reassuringly.
    # So find the content rect first and place every corner box inside IT, not inside the canvas.
    f0 = frames[0]
    def _content_span(profile_mean, profile_std):
        n = len(profile_mean)
        lo = 0
        while lo < n and profile_std[lo] < 3.0 and (profile_mean[lo] > 200 or profile_mean[lo] < 20):
            lo += 1
        hi = n - 1
        while hi > lo and profile_std[hi] < 3.0 and (profile_mean[hi] > 200 or profile_mean[hi] < 20):
            hi -= 1
        return lo, hi
    cy0, cy1 = _content_span(f0.mean(axis=1), f0.std(axis=1))
    cx0, cx1 = _content_span(f0.mean(axis=0), f0.std(axis=0))
    pad_frac = 1.0 - ((cy1 - cy0 + 1) * (cx1 - cx0 + 1)) / float(WORK * WORK)
    if pad_frac > 0.02:
        print(f"  NOTE: {pad_frac*100:.0f}% of the frame is flat padding (letterbox/pillarbox). Real content"
              f" is x={cx0}..{cx1}, y={cy0}..{cy1} at {WORK}px working res. Corner boxes have been moved"
              f" INSIDE the content; measuring the padding would report a false clean pass.")
        print(f"  FIX THE RENDER TOO: pass fit=\"cover\" so the canvas is filled instead of padded.")

    worst = 0.0
    worst_name = None
    verdicts = []
    ranges = []       # per-corner shift range, None when the corner was unusable
    reversals = []    # per-corner direction changes along the dominant axis
    print("  corner                  texture   shift-range   samples")
    for name, box in CORNERS:
        # Box fractions are relative to the CONTENT rect, so a padded render is probed on its picture.
        x0 = int(cx0 + box[0] * (cx1 - cx0)); y0 = int(cy0 + box[1] * (cy1 - cy0))
        x1 = int(cx0 + box[2] * (cx1 - cx0)); y1 = int(cy0 + box[3] * (cy1 - cy0))
        ref = np.ascontiguousarray(frames[0][y0:y1, x0:x1])
        # CV_32F, not CV_64F: ref is float32 and this OpenCV build rejects that depth combination.
        tex = float(cv2.Laplacian(ref, cv2.CV_32F).var())
        # TEMPLATE MATCHING, NOT PHASE CORRELATION (fixed 2026-07-24 after a real false-NEGATIVE).
        # Phase correlation is only reliable for shifts small relative to the patch, and these patches
        # are ~144px wide. On draw A the ground genuinely travelled +15/-10px and phaseCorrelate
        # reported 1-4px with a confident response, so the gate PASSED a clip I rejected on sight.
        # Measured side by side on the same patch and the same frames:
        #     t=11   phaseCorr sx=-0.14 (resp 0.46)   templateMatch dx=+15 (quality 0.99)
        #     t=19   phaseCorr sx=-0.12 (resp 0.40)   templateMatch dx=-10 (quality 1.00)
        # A search-window template match finds the true displacement instead of a correlation peak
        # dragged toward zero by the Hanning taper. Certifying motion as clean is the one failure
        # mode that matters here, so the measurement has to be the one that does not miss.
        ref_u8 = ref.astype(np.uint8)
        shifts, resps, xs, ys = [], [], [], []
        for t in SAMPLE_TIMES:
            i = min(int(t * fps), len(frames) - 1)
            sy0, sy1 = max(0, y0 - SEARCH_PAD), min(WORK, y1 + SEARCH_PAD)
            sx0, sx1 = max(0, x0 - SEARCH_PAD), min(WORK, x1 + SEARCH_PAD)
            res = cv2.matchTemplate(frames[i][sy0:sy1, sx0:sx1].astype(np.uint8), ref_u8,
                                    cv2.TM_CCOEFF_NORMED)
            _, quality, _, loc = cv2.minMaxLoc(res)
            sx, sy = float(loc[0] + sx0 - x0), float(loc[1] + sy0 - y0)
            shifts.append(max(abs(sx), abs(sy)))
            xs.append(sx); ys.append(sy)
            resps.append(quality)
        # Peak-to-peak along each axis, then the worse one. Ranging the ABSOLUTE magnitudes hid
        # out-and-back travel that crosses zero (+15 out, -10 back reads as a 15px span, not 25px).
        rng = max(max(xs) - min(xs), max(ys) - min(ys))
        # SIGNED trajectory along the dominant axis: direction is the whole question now, because
        # PACING IS ALLOWED and only INCOHERENT pacing is not (2026-07-24: "pacing is great,
        # just not out of sanity pacing"). Same shape as the steam rule: a little all the way is
        # fine, intermittent is the bug.
        traj = np.array(ys if (max(ys)-min(ys)) > (max(xs)-min(xs)) else xs, float)
        rev = 0
        anchor, last = traj[0], 0
        for v in traj[1:]:
            d = v - anchor
            if abs(d) < REVERSAL_DEADBAND:
                continue
            sgn = 1 if d > 0 else -1
            if last != 0 and sgn != last:
                rev += 1
            last, anchor = sgn, v
        reversals.append(rev)
        med_resp = float(np.median(resps))
        # Two different reasons a corner is unusable, and conflating them is a bug: a FLAT corner
        # has nothing to lock onto, whereas a TEXTURED corner with a collapsed response means the
        # content itself changed - a hand or hair swept through it. Reporting the second as "no
        # texture" while printing tex=539 is self-contradictory (caught on the indoor clip 2026-07-24).
        # TEXTURE IS CHECKED FIRST, INDEPENDENTLY OF MATCH QUALITY (fixed 2026-07-24). Nesting it
        # under the quality test let a nearly-flat patch through whenever the matcher happened to
        # score well: the wall clip's bottom-right read tex=7 (flat) and still reported 24.0px at
        # quality 0.877, which is a confident number about nothing. Flat means unmeasurable, full stop.
        if tex < TEX_MIN:
            verdicts.append("INCONCLUSIVE"); ranges.append(None)
            print(f"  {name}  tex={tex:6.0f}  {rng:6.1f}px     INCONCLUSIVE (flat, nothing to track,"
                  f" any number here is noise)")
            continue
        if med_resp < RESP_MIN:
            verdicts.append("OCCLUDED"); ranges.append(None)
            print(f"  {name}  tex={tex:6.0f}  {rng:6.1f}px     OCCLUDED (textured but the patch was not"
                  f" re-found, match {med_resp:.3f} < {RESP_MIN}: a limb or hair swept through, or it left"
                  f" the search window) - excluded, not a pass")
            continue
        verdicts.append("FAIL" if (rng > THRESH_PX and rev >= 1) else "PASS"); ranges.append(rng)
        if rng > worst:
            worst, worst_name = rng, name.strip()
        print(f"  {name}  tex={tex:6.0f}  {rng:6.1f}px     "
              f"{'FAIL' if (rng > THRESH_PX and rev >= 1) else 'pass'} "
              f"(resp {med_resp:.3f}, reversals {rev})")

    # COHERENCE RULE (added 2026-07-24 after a third false-FAIL). A synthetic dolly is a GLOBAL
    # transform, so it necessarily shows up in more than one corner. A single corner moving while
    # its neighbours sit at ~0 is LOCAL, which means a limb intruded - on the flat-wall clip the
    # bottom-left box read 14.5px while the other three read 0.1/0.2/0.6px, and the pixels showed
    # her SLEEVE crossing the box against a provably static wall.
    # Validated against all six clips judged so far: the flagged coastal clip (39.5 AND 53.8),
    # tight portrait (46.1 AND 39.9) and ocean (35.0 with 8.7 elevated) all fail on coherence;
    # the indoor take, the frozen control, and the flat wall all pass.
    hot = sorted((r for r in ranges if r is not None), reverse=True)
    coherent = len([r for r in hot if r > THRESH_PX]) >= 2 or \
               (len(hot) >= 2 and hot[0] > THRESH_PX and hot[1] > THRESH_PX / 2.0)
    # "ONLY ONE CORNER MOVED" MEANS NOTHING WHEN ONLY ONE CORNER WAS MEASURABLE (fixed 2026-07-24,
    # and this one let the ORIGINAL FLAGGED CLIP pass, which is the worst possible miss). On that clip
    # bottom-left read 51px with 7 reversals at match 0.948, bottom-right read 100px but was excluded
    # for low match, and both top corners are flat sky and excluded. The coherence rule then saw a
    # single hot corner beside three ~zeros, concluded "a sleeve crossed it", and PASSED a clip I
    # had already rejected by eye. But those neighbours were not static - they were UNREADABLE, and
    # absence of measurement is not evidence of stillness. So locality may only be inferred when at
    # least two corners are actually usable; with one, a hot reversing corner fails.
    usable = len(hot)
    if usable <= 1 and hot and hot[0] > THRESH_PX:
        coherent = True
        print(f"  NOTE: only {usable} corner was measurable, so 'the other corners are still' is not a"
              f" finding, it is missing data. A single hot reversing corner is treated as real motion"
              f" rather than dismissed as a limb.")
    # Provenance verdict comes first, because it is the actual rule.
    moved = max((r for r in ranges if r is not None), default=0.0)
    if declared:
        if wants_static and moved > THRESH_PX and coherent:
            print(f"  VERDICT: FAIL - the brief asked for a STATIC camera and the backdrop moved "
                  f"{moved:.1f}px across multiple corners. This motion was NOT requested, so it is an "
                  f"engine artefact, not a choice. Unrequested is the failure; size is not.")
            return 1
        if wants_motion:
            print(f"  VERDICT: PASS - the brief asked for camera movement and the backdrop moved "
                  f"{moved:.1f}px. Requested motion is a shot, not a defect. Still confirm by eye that "
                  f"it goes ONE way and that nothing implies HER walking, since she has no gait.")
            return 0
        if wants_static and moved <= THRESH_PX:
            print(f"  VERDICT: PASS - static was requested and the backdrop holds at {moved:.1f}px.")
            return 0
    if "FAIL" in verdicts and coherent:
        print(f"  NUMERIC VERDICT: FAIL - INCOHERENT pacing. The backdrop travels {worst:.1f}px at "
              f"{worst_name} AND REVERSES DIRECTION mid-clip, with a second corner moving with it so "
              f"the motion is global. A camera move that goes out and comes back is the insanity; "
              f"a one-way move of the same size would pass.")
        return 1
    if "FAIL" in verdicts:
        print(f"  NUMERIC VERDICT: PASS (with a LOCAL flag) - {worst_name} reads {worst:.1f}px but "
              f"every other corner is near zero, so the motion is LOCAL, not a camera move: a limb "
              f"or hair crossed that box. Eyeball that corner to confirm; do not fail the clip on it.")
        return 0
    if any((r or 0) > THRESH_PX for r in ranges):
        mx = max(r for r in ranges if r)
        print(f"  NUMERIC VERDICT: PASS - the backdrop moves up to {mx:.1f}px but never reverses "
              f"direction, so it reads as one deliberate camera move rather than pacing out and back. "
              f"Pacing is allowed; only out-of-sanity pacing is not.")
        return 0
    if not any(v == "PASS" for v in verdicts):
        print("  NUMERIC VERDICT: INCONCLUSIVE - every corner is textureless, so this tool cannot")
        print("  tell static from moving. Judge the sheets and the clip by eye; do NOT report a pass.")
        return 2
    print(f"  NUMERIC VERDICT: PASS - every textured corner holds under {THRESH_PX:.0f}px.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
