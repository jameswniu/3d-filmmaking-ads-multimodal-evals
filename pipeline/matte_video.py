#!/usr/bin/env python3
"""Person matte for the glass: subject on pure black, depth zeroed outside her.

Black is the Looking Glass's native void (the panel renders it as empty
space), so a matted clip becomes the floating-subject look the factory demos
use. Two outputs from two inputs:

  color_out = color * alpha            (subject composited on black)
  depth_out = depth * alpha            (background forced to 0 = farthest;
                                        also kills the depth model's known
                                        noise on low-texture backgrounds, and
                                        makes disocclusion fill pull BLACK
                                        behind her silhouette)

Matting is RobustVideoMatting (mobilenetv3, torch.hub), recurrent across
frames so edges do not flicker; runs on MPS. Soft alpha is kept: a soft edge
composites into black cleanly and tapers depth at the silhouette.

Usage: matte_video.py <color.mp4> <depth.mp4> <color_out.mp4> <depth_out.mp4>
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("TORCH_HOME", str(Path(__file__).resolve().parents[1] / "models" / "torch"))
import torch  # noqa: E402

# ---------------------------------------------------------------------------
# BASE PROFILE (2026-07-28: "tune or rebase our background removing
# module please on the nofuzz", after "smoothing strictly better").
#
# This is the shipped default for background removal. It REPLACES the
# 2026-07-26 fuzz-veil profile, which traded a soft halo for even hair and lost
# on the Looking Glass: the veil read as a grey wedge between her fingers and
# her hair, and the silhouette lost its edge.
#
#   LOCK_SOLIDIFY on   a shoulder on the alpha instead of a blurred veil
#   lo .68 / w .12     the TIGHTEST of the three shoulders tested. This is the
#                      "no fuzz" variant. It is what kills the grey wedge
#                      between her fingers and her hair: background retention in
#                      the head region drops from 0.35% at lo .45 to 0.07% here,
#                      for 0.6% less hair kept.
#   HAIR_ADAPTIVE on   ...but the tight shoulder ALSO scissors the hair, and a
#                      loose one is what reads as holographic. My note, comparing
#                      them: "I found B more holographic. It has a 3D effect,
#                      but A is cleaner." So the body gets lo .68 and the hair
#                      gets its own, softer floor, per pixel.
#   hair lo .25 / w .35  THE SOFTEST, and it is the shipped hair floor.
#                      Landed after a three-way (hair .25 / .45 / .68) cast on
#                      the Glass, a brief detour through the middle, and a second
#                      advisory round. Final call: "go with natural".
#
#                      Why the extremes both fail, which is why a middle was
#                      tried at all. At .68 the cut lands INSIDE her hairline:
#                      the discarded pixels measure warmth +0.579 against her
#                      body's +0.585, while the removed studio wall measures
#                      +0.02, so they are her hair. At .25 the surviving fringe
#                      reads as depth from across the room but as distraction up
#                      close: "more hologram when further away but also more
#                      distracting." Correctness argued .25, legibility argued
#                      .68, and .45 was the compromise.
#
#                      WHY THE COMPROMISE LOST. Both advisors picked .45 AND
#                      both, independently, raised the same objection against
#                      their own pick: the Looking Glass is the PRIMARY surface,
#                      and .45 optimizes for the secondary one (a close-up
#                      screen-share). A compromise that serves the surface you
#                      look at less is not a compromise, it is a miss. The Glass
#                      is what this pipeline is for, so the hair floor is tuned
#                      for viewing distance, not for a monitor.
#
#                      Set MATTE_HAIR_LO=0.45 MATTE_HAIR_W=0.20 for the middle,
#                      or MATTE_HAIR_ADAPTIVE=0 for the hard global cut, if a
#                      specific output is destined for close viewing.
#   CONTOUR_SMOOTH 3   close-only morphology: fills the notches that made the
#                      hair outline ragged, without shaving convex detail
#   CONTOUR_OPEN 0     open is what flattened her fingertips; stays off
#   FUZZ_EVEN off      superseded by the shoulder
#   HAIR_BODY off      the elif fallback, also superseded
#
# Radius 3 is capped by HER FINGERS, not her hair: the gaps between fingers are
# concave notches too, so close fills them at radius 5 and webs them at 7. Hair
# alone would take more.
#
# The other two shoulders stay reproducible from the environment, and both are
# in the golden corpus: lo .45 / w .12 is nobg-02 ("little fuzz"), lo .25 / w
# .35 is nobg-03 ("little more fuzz"). Only the floor differs between them.
#
# Declared here as setdefault, in one place, so the profile is visible and a
# caller can still override any single knob from the environment. The literal
# defaults further down are left as-is; they document the pre-2026-07-28
# behaviour rather than driving it.
#
# BLAST RADIUS: the daily-brief stage and the glass-feed stage both
# call this file, so both now get this profile.
# ---------------------------------------------------------------------------
for _k, _v in (
    ("MATTE_FUZZ_EVEN", "0"),
    ("MATTE_HAIR_BODY", "0"),
    ("MATTE_LOCK_SOLIDIFY", "1"),
    ("MATTE_SOLIDIFY_LO", "0.68"),
    ("MATTE_SOLIDIFY_W", "0.12"),
    ("MATTE_CONTOUR_SMOOTH", "3"),
    ("MATTE_CONTOUR_OPEN", "0"),
    ("MATTE_HAIR_ADAPTIVE", "1"),
    ("MATTE_HAIR_LO", "0.25"),
    ("MATTE_HAIR_W", "0.35"),
):
    os.environ.setdefault(_k, _v)


def probe1(path, field):
    # One field per call: ffprobe returns fields in stream order, not ask order.
    return subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         f"stream={field}", "-of", "csv=p=0", path],
        check=True, capture_output=True, text=True).stdout.strip()


def main():
    color_in, depth_in, color_out, depth_out = sys.argv[1:5]
    w = int(probe1(color_in, "width")); h = int(probe1(color_in, "height"))
    n = int(probe1(color_in, "nb_frames")); dur = float(probe1(color_in, "duration"))
    fps = n / dur
    dw = int(probe1(depth_in, "width")); dh = int(probe1(depth_in, "height"))

    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3",
                           trust_repo=True).to(dev).eval()
    # RVM guideline: internal downsample so the matte net sees ~512px.
    base_px = float(os.environ.get("MATTE_PX", "512"))   # net's internal view; more = finer wisps, slower
    ratio = min(base_px / max(w, h), 1.0)
    print(f"[matte] {n} frames {w}x{h} @ {fps:.2f}fps  device={dev} ratio={ratio:.2f}")

    rd_c = subprocess.Popen(["ffmpeg", "-v", "error", "-i", color_in, "-f", "rawvideo",
                             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    rd_d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", depth_in, "-f", "rawvideo",
                             "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    # Audio passes through from the source: downstream (quilt mux, cast voice)
    # expects the matted clip to still carry her voice.
    wr_c = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", color_in,
                             "-map", "0:v", "-map", "1:a?", "-c:a", "aac",
                             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", color_out],
                            stdin=subprocess.PIPE)
    wr_d = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                             "-s", f"{dw}x{dh}", "-r", f"{fps}", "-i", "-", "-an",
                             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", depth_out],
                            stdin=subprocess.PIPE)

    rec = [None] * 4
    csz, dsz = w * h * 3, dw * dh
    with torch.no_grad():
        for i in range(n):
            raw = rd_c.stdout.read(csz)
            drw = rd_d.stdout.read(dsz)
            if len(raw) < csz or len(drw) < dsz:
                print(f"[matte] streams ended at frame {i}")
                break
            src = torch.from_numpy(np.frombuffer(raw, np.uint8).reshape(h, w, 3).copy())
            src = src.permute(2, 0, 1).float().div(255).unsqueeze(0).to(dev)
            fgr, pha, *rec = model(src, *rec, downsample_ratio=ratio)
            a = pha[0, 0].clamp(0, 1)
            if os.environ.get("MATTE_DEFRINGE", "1") == "1":   # default ON since the 2026-07-26 win
                # Kill the low-alpha VEIL (residual sky ghost hugging the hair
                # contour, reads as dirt against black) without touching real
                # strands: alphas under ~0.06 die, 0.06-0.22 ramp, above 0.22
                # untouched. A gamma would dim real wisps; this shoulder does not.
                a = a * torch.clamp((a - 0.06) / 0.16, 0, 1).clamp(max=1)
            if os.environ.get("MATTE_FUZZ_EVEN", "1") == "1":   # default ON since the 2026-07-26 win
                # Even-fuzz body: the maxpool dilation copies strand CLUSTERING
                # into the cloud (plateaus where dense, holes where sparse =
                # the patchy fuzz I rejected). A wide gaussian of the
                # strand field averages density into one smooth veil; lift it
                # to visibility, cap it translucent so the fuzz survives.
                _g2 = torch.exp(-(torch.arange(17, dtype=torch.float32, device=a.device) - 8) ** 2 / 32.0)
                _g2 = (_g2 / _g2.sum())
                _sm = a.unsqueeze(0).unsqueeze(0)
                _sm = torch.nn.functional.conv2d(_sm, _g2.view(1, 1, 1, 17), padding=(0, 8))
                _sm = torch.nn.functional.conv2d(_sm, _g2.view(1, 1, 17, 1), padding=(8, 0))
                a = torch.maximum(a, torch.clamp(_sm[0, 0] * 1.6, 0, 0.8))
            elif os.environ.get("MATTE_HAIR_BODY", "1") == "1":   # default ON since the 2026-07-26 win
                # Display-floor play: single strands are sub-pixel at tile
                # scale and physically unrenderable on the lenticular panel
                # (~3-4 tile px minimum). Soft dilation consolidates wisps
                # into locks: thin alpha gains body from its neighborhood
                # max; solid regions are already 1.0 and unchanged. The
                # model's foreground field supplies color for grown pixels.
                _ap = a.unsqueeze(0).unsqueeze(0)
                _dil = torch.nn.functional.max_pool2d(_ap, kernel_size=9, stride=1, padding=4)[0, 0]
                a = torch.maximum(a, _dil * 0.5)
            if os.environ.get("MATTE_LOCK_SOLIDIFY") == "1":
                # The body dilation's half-alpha band reads as clumpy gray
                # fuzz on black (my note: uneven fuzziness around the hair).
                # Discipline it: smooth the alpha field so the band is EVEN,
                # then push mids toward opaque so locks read solid behind one
                # narrow uniform falloff instead of a wide cloud.
                # BLUR WIDTH IS THE HAIR DIAL. Smoothing runs BEFORE the
                # shoulder, so a wide kernel spreads hair's sparse strand alpha
                # into one continuous field and the shoulder then lifts that
                # whole field into a visible grey veil. Narrowing it thresholds
                # closer to the strands themselves, so hair reads as hair
                # instead of as a cloud (2026-07-28: "only the hair
                # still a bit fuzzy"). Must be odd; 1 disables smoothing.
                _k = int(os.environ.get("MATTE_SOLIDIFY_BLUR", "9"))
                if _k % 2 == 0:
                    _k += 1
                _sm = a.unsqueeze(0).unsqueeze(0)
                if _k > 1:
                    _sig2 = 2.0 * (_k / 4.5) ** 2      # reduces to the original 8.0 at _k=9
                    _g1 = torch.exp(-(torch.arange(_k, dtype=torch.float32, device=a.device) - _k // 2) ** 2 / _sig2)
                    _g1 = (_g1 / _g1.sum())
                    _sm = torch.nn.functional.conv2d(_sm, _g1.view(1, 1, 1, _k), padding=(0, _k // 2))
                    _sm = torch.nn.functional.conv2d(_sm, _g1.view(1, 1, _k, 1), padding=(_k // 2, 0))
                # The SHOULDER is the crispness dial. _lo is where alpha starts
                # climbing off zero and _w is how much alpha it takes to reach
                # opaque, so a NARROWER _w is a steeper edge and a HIGHER _lo
                # erodes the silhouette inward. Defaults 0.25/0.35 reproduce the
                # original behaviour exactly.
                #
                # Do not chase _w to 0. That is a binary matte, which trades the
                # halo for staircase aliasing on the silhouette and shears hair
                # off at the threshold. Sweep and look, do not assume steeper is
                # better.
                _lo = float(os.environ.get("MATTE_SOLIDIFY_LO", "0.25"))
                _w = float(os.environ.get("MATTE_SOLIDIFY_W", "0.35"))

                if os.environ.get("MATTE_HAIR_ADAPTIVE", "0") == "1":
                    # CRISP EVERYWHERE, NATURAL IN THE HAIR (2026-07-28:
                    # "apply no flat to everything except the hair, and in the
                    # hair we just do it naturally").
                    #
                    # A tight shoulder cleans hands and shoulders, which is why
                    # no-fuzz won; a loose one keeps the wispy hair that reads
                    # as holographic. Measured on V-L6, the two settings differ
                    # 60% in hair and 40% on the body, so one global floor
                    # cannot serve both. This applies each where it belongs.
                    #
                    # THE DISCRIMINATOR IS BAND THICKNESS, NOT COLOUR. Colour
                    # was tried and failed: hair overlaps the cardigan on every
                    # channel, and a vertical split fails because her hand
                    # crosses in front of her hair. But hair scatters partial
                    # alpha over a THICK region (strands, gaps, more strands)
                    # while a hand or shoulder edge resolves solid-to-zero in
                    # one or two pixels. Local density of partial alpha
                    # separates them cleanly and needs no segmentation model.
                    _partial = ((a > 0.05) & (a < 0.95)).float().unsqueeze(0).unsqueeze(0)
                    _win = int(os.environ.get("MATTE_HAIR_WIN", "25"))
                    if _win % 2 == 0:
                        _win += 1
                    _dens = torch.nn.functional.avg_pool2d(
                        _partial, _win, stride=1, padding=_win // 2)[0, 0]
                    _thr = float(os.environ.get("MATTE_HAIR_THRESH", "0.12"))
                    # Ramp rather than a hard switch, so no seam appears where
                    # hair meets shoulder.
                    _hairness = torch.clamp((_dens - _thr * 0.5) / max(_thr, 1e-3), 0, 1)
                    _hair_lo = float(os.environ.get("MATTE_HAIR_LO", "0.25"))
                    _hair_w = float(os.environ.get("MATTE_HAIR_W", "0.35"))
                    _lo_m = _lo * (1.0 - _hairness) + _hair_lo * _hairness
                    _w_m = _w * (1.0 - _hairness) + _hair_w * _hairness
                    _t = torch.clamp((_sm[0, 0] - _lo_m) / torch.clamp(_w_m, min=1e-3), 0, 1)
                else:
                    _t = torch.clamp((_sm[0, 0] - _lo) / max(_w, 1e-3), 0, 1)
                a = _t * _t * (3.0 - 2.0 * _t)

            if int(os.environ.get("MATTE_CONTOUR_SMOOTH", "0")) > 0:
                # SMOOTH THE OUTLINE WITHOUT SOFTENING IT. After a steep
                # shoulder the hair boundary is a clean arc, but it carries
                # small notches and spurs that read as a ragged edge (my note,
                # 2026-07-28: the cardigan outline is fine, "it's the outline
                # for the hair").
                #
                # A gaussian would fix the raggedness by re-widening the alpha
                # ramp, which is exactly the halo that was just removed. A
                # morphological CLOSE (fill notches) then OPEN (shave spurs)
                # edits the contour SHAPE and leaves the ramp as steep as it
                # was, so crispness survives.
                #
                # THE TWO HALVES ARE NOT INTERCHANGEABLE, and this is the whole
                # reason the effect can be aimed at hair without a hair mask:
                #
                #   CLOSE (max then min) fills CONCAVE notches. Hair raggedness
                #     is notches, so close is the half that helps.
                #   OPEN  (min then max) shaves CONVEX spurs. Fingertips ARE
                #     convex spurs, so open is the half that flattened them.
                #
                # Measured 2026-07-28: close+open at radius 5 squared off her
                # fingertips and the gaps between fingers; radius 3 had started
                # to. Colour cannot separate hair from skin here (hair overlaps
                # the cardigan on every channel tried) and a vertical split
                # fails because her hand crosses her hair. Running close alone
                # aims at hair geometrically instead, no mask needed.
                #
                # So OPEN defaults OFF. Turn it on only for a subject with no
                # fine convex detail to lose.
                _rc = int(os.environ.get("MATTE_CONTOUR_SMOOTH", "0"))
                _ro = int(os.environ.get("MATTE_CONTOUR_OPEN", "0"))
                _x = a.unsqueeze(0).unsqueeze(0)
                _mx = lambda t, r: torch.nn.functional.max_pool2d(t, 2 * r + 1, stride=1, padding=r)
                _mn = lambda t, r: -torch.nn.functional.max_pool2d(-t, 2 * r + 1, stride=1, padding=r)
                if _rc > 0:
                    _x = _mn(_mx(_x, _rc), _rc)      # close: notches filled
                if _ro > 0:
                    _x = _mx(_mn(_x, _ro), _ro)      # open:  spurs shaved
                a = _x[0, 0]
            # Composite the model's DE-CONTAMINATED foreground, not the raw
            # frame: a raw semi-transparent hair pixel still contains the old
            # background, and multiplying it toward black thins and dirties
            # the wisps (my verdict, 2026-07-26: "her hair is kinda fucked").
            #
            # AND fgr IS SAFE ON OPAQUE PIXELS, so do not "fix" it there.
            # 2026-07-28: substituting true source pixels wherever alpha ~1
            # (on the theory that a network estimate was flattening her face)
            # was built, run, and measured against the source on a 100-frame
            # clip. It moved mean deviation 2.36 -> 2.20 out of 255. Both are
            # 0.9%. The idea was motivated by a contrast loss that turned out
            # to be a confounded measurement, and it was removed rather than
            # left in as a no-op with a persuasive comment.
            out = (fgr[0].clamp(0, 1) * a.unsqueeze(0)).mul(255).byte().permute(1, 2, 0).cpu().numpy()
            wr_c.stdin.write(out.tobytes())
            dnp = np.frombuffer(drw, np.uint8).reshape(dh, dw).astype(np.float32)
            # Depth uses a HARDENED matte: soft alpha is right for color but
            # tapering depth with it detaches hair from the head plane (wisps
            # drift toward the void and split in the extreme views). Alpha
            # 0.30+ carries full head depth.
            a_np = torch.clamp((a - 0.05) / 0.25, 0, 1).cpu().numpy()
            if a_np.shape != (dh, dw):
                a_np = np.array(torch.nn.functional.interpolate(
                    a.unsqueeze(0).unsqueeze(0), size=(dh, dw), mode="bilinear",
                    align_corners=False)[0, 0].cpu())
            dout = np.clip(dnp * a_np, 0, 255).astype(np.uint8)
            blur = float(os.environ.get("MATTE_DEPTH_SMOOTH", "0"))
            if blur > 0:
                # Flatten strand-level depth structure (1-3px tugs from bright
                # strands) while keeping the head's macro shape; strand crawl
                # across views is depth noise, not geometry.
                from PIL import Image as _PI, ImageFilter as _PF
                dout = np.array(_PI.fromarray(dout, "L").filter(_PF.GaussianBlur(blur)))
            wr_d.stdin.write(dout.tobytes())
            if (i + 1) % 50 == 0 or i + 1 == n:
                print(f"[matte]   {i + 1}/{n}")
    rd_c.stdout.close(); rd_d.stdout.close()
    wr_c.stdin.close(); wr_d.stdin.close()
    wr_c.wait(); wr_d.wait()
    print(f"[matte] done -> {color_out}, {depth_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
