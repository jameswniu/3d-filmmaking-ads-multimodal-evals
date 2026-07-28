#!/usr/bin/env python3
"""scene_simplicity.py <image-or-video> - PRE-SPEND check: is this background simple enough for iii?

Measured 2026-07-26. avatar_iii freezes the whole background into a photograph and animates only
her, so the more DETAIL sitting back there, the more obviously frozen the frame reads. Background
busy-ness (mean spatial gradient in the side thirds) ranks my avatar_iii verdicts monotonically:

    r3   "perfect"    2.68
    b5c  "kinda ok"   7.51
    T6   "worst"      9.50
    T3/T2/T4 rejected 13.4 / 14.9 / 17.0

Boundary sits between 7.5 and 9.5, so the working target for iii is <= 7.5, ideally under 5.
(avatar_v carries 11-12 fine - it has the performance quality to hold a busy frame. This threshold
is for iii ONLY, which is the engine I loop on.)

Run it on the LOOK PREVIEW before rendering: it costs nothing and it is the one pre-spend predictor
of my verdict found so far.

Usage: scene_simplicity.py <file.png|file.jpg|file.webp|file.mp4>
Exit 0 simple enough / 1 too busy for iii / 64 unreadable.
"""
import subprocess, sys
import numpy as np

III_MAX = 7.5

def main():
    p = sys.argv[1]
    raw = subprocess.run(["ffmpeg","-nostdin","-v","error","-i",p,"-vf",
                          "fps=2,scale=160:160,format=gray","-f","rawvideo","pipe:1"],
                         capture_output=True).stdout
    n = len(raw)//25600
    if n < 1:
        print(f"scene_simplicity: unreadable {p}"); sys.exit(64)
    fr = np.frombuffer(raw[:n*25600],dtype=np.uint8).reshape(n,160,160).astype(np.float32)
    bg = np.concatenate([fr[:,:,:50], fr[:,:,110:]], axis=2)
    busy = (np.abs(np.diff(bg,axis=2)).mean() + np.abs(np.diff(bg,axis=1)).mean())/2
    ok = busy <= III_MAX
    print(f"{'SIMPLE ' if ok else 'TOO BUSY'} {busy:6.2f}  (iii target <= {III_MAX}; my perfect clip 2.68)  {p.split('/')[-1]}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
