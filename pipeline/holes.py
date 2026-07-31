"""Disocclusion fill, in one place.

WHY THIS FILE EXISTS. Two warps in this repository filled the holes a forward
warp opens, and they filled them differently. warp_fast used a background side
fill; wiggle_preview used plain nearest neighbour. Nobody chose that: the
background side version was written later, as a fix, and the older path never
received it. The benchmark in warp_fast asserted the two produced identical
output, which passed only because the author's real depth maps are smooth enough
for the holes to be small. Run it against a depth map with a hard step at the
subject and 40 of 77 views disagree, the worst on 21.6% of its pixels.

So this was never two attempts at one problem with a bug in one of them. It was
one improvement that reached one caller. Both callers now import from here, and
the preview finally shows what the renderer actually produces, which is the only
reason a preview is worth looking at.

THE ACTUAL ARGUMENT, kept from the version that won. Nearest neighbour smears
whichever pixel is closest into the gap, and at her silhouette the closest pixel
is HER, so outlines are the first thing to break as the parallax budget rises.
But a revealed gap is by definition showing what was BEHIND the subject. So of
the two horizontal neighbours flanking a hole, copy the one whose depth is
FARTHER. Identical cost, correct prior.
"""
import numpy as np


def fill_background(rgb: np.ndarray, mask: np.ndarray, dview: np.ndarray) -> np.ndarray:
    """Fill holes from the background side.

    rgb    HxWx3 uint8, the warped colour buffer with holes left as zeros
    mask   HxW   bool, True where a source pixel actually landed
    dview  HxW   float, the warped depth buffer; larger is nearer

    Of the nearest valid neighbour to the left and to the right, the one with
    the SMALLER depth is farther away, and that is the one a disocclusion should
    reveal. Rows are independent, so this is a pair of accumulate scans.
    """
    h, w = mask.shape
    idx = np.arange(w)[None, :].repeat(h, 0)

    # nearest valid index to the left of every pixel, and to the right
    li = np.where(mask, idx, -1)
    li = np.maximum.accumulate(li, axis=1)
    ri = np.where(mask, idx, w)
    ri = np.minimum.accumulate(ri[:, ::-1], axis=1)[:, ::-1]

    rows = np.arange(h)[:, None]
    li_c = np.clip(li, 0, w - 1)
    ri_c = np.clip(ri, 0, w - 1)

    # A missing neighbour is infinitely NEAR, so it always loses to a real one.
    # That matters at the frame edges, where one side has no valid pixel at all.
    ld = np.where(li >= 0, dview[rows, li_c], np.inf)
    rd = np.where(ri < w, dview[rows, ri_c], np.inf)

    use_left = ld <= rd
    src = np.where(use_left, li_c, ri_c)

    out = rgb.copy()
    holes = ~mask
    out[holes] = rgb[rows.repeat(w, 1)[holes], src[holes]]
    return out
