#!/usr/bin/env python3
"""Emit both published SVGs from the counts, instead of trusting typed copies.

WHY THIS FILE EXISTS. The diagrams were written by a generator that lived in a
private tree and was never committed. tests/test_suite.py said so out loud,
because it made a specific failure possible: regenerating from over there would
silently restore claims this repository had already retired, and nothing here
would notice. The retired-claim scanner was the mitigation. This is the fix.

WHAT IS ACTUALLY SINGLE SOURCED. The numbers, not the layout. Before this file,
`13 probes` appeared in the stamp, again on a LOCAL card, and again in README.md,
as three independent strings that happened to agree. `77 views` appeared twice
and its factors `7 x 11` once more, with nothing tying the product to the pair.
Now the probe count is COUNTED from probes/*.py, the view count is the PRODUCT of
the quilt shape, the gate count is the LENGTH of the gate table, and every place
they are drawn reads the same value.

hero.svg was nearly left out of this on the grounds that it is a poster rather
than a diagram of boxes. Reading it disproved that: 77 of its rectangles are the
quilt, one per view, and 10 more are the stage pills. It was already drawing the
counts, with nothing tying it to them, which is the exact problem in the more
decorative half of the repository.

The geometry is a declared layout, not a solver. Coordinates are literals here
because both figures are fixed-size and their boxes do not move; what drifts in
practice is the numbers, and those are what this computes. Saying it plainly is
better than implying a layout engine that does not exist.

    python3 tools/render_diagrams.py --check    exit 1 if a committed file
                                                differs from what this emits
    python3 tools/render_diagrams.py --write    regenerate both
    python3 tools/render_diagrams.py --audit    every other surface agrees

--check runs in CI, so a hand edit to either SVG, or a count that moves in one
place and not the others, fails the build.
"""
import argparse
import difflib
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"

INK = "#04091a"
PALE = "#e0f2fe"
DIM = "#8fb4d8"
EDGE = "#1e3a64"
CYAN = "#38bdf8"
DEEP = "#0ea5e9"
VIOLET = "#8b8cf0"
AMBER = "#f0b429"

# ---------------------------------------------------------------- the counts

# Counted, not typed. A probe added or deleted moves every surface that states
# this number, which is the whole point of the file.
PROBES = len(glob.glob(os.path.join(ROOT, "probes", "*.py")))

# The quilt is the source; the view count is its product. These were three
# separate literals before, so `7 x 11 = 77` could disagree with `77 views`.
QUILT_COLS, QUILT_ROWS = 7, 11
VIEWS = QUILT_COLS * QUILT_ROWS

# Measured, never extrapolated: the flat tier billed 1 credit at three very
# different durations, the premium tiers billed these. docs/COST.md carries the
# reasoning; this is only what the diagram prints.
CREDIT_SCHEDULED = 1
CREDIT_TIERS = (1, 43, 58)

# How many of the gates actually block. Three fail open, which is why no gate
# card carries a "blocking" badge and why the aria-label says so in words.
GATES_FAIL_OPEN = 3

# The strongest claim this repository makes, and the one the hero had been
# leaving out: how many of the named gating thresholds trace to a labelled
# pass/reject pair rather than to somebody's judgement.
#
# evals/derive.py is the AUTHORITY for these two and re-derives every bar on
# each run. They are restated here rather than imported because drawing a
# picture must not require numpy, opencv and ffmpeg, which derive.py does.
# That makes them the one pair of numbers in this file that could go stale, so
# tests/test_suite.py asserts them against derive.py's own output and fails the
# build the moment they disagree.
THRESHOLDS_DERIVED, THRESHOLDS_GATING = 16, 16

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight", 9: "nine", 10: "ten"}

# ---------------------------------------------------------------- the content

# (index, name, what it does, what forced it). The note is the fourth line and
# only the first row of stages carries one.
STAGES_SPINE = [
    ("0", "WAKE", "a timer, not a person", "alerts on not-success"),
    ("1", "SCRIPT", "two agents, kept apart", "one writes, one shapes"),
    ("2", "VOICE", "clone, continuous take", "draw 3, keep the median"),
    ("3", "LOOK", "one pinned identity", "fresh look per render"),
    ("4", "RENDER", "audio drives a still", "the still IS the seed"),
]

STAGES_HOLO = [
    ("5", "MATTE", "the room comes out"),
    ("6", "DEPTH", "colour becomes distance"),
    ("7", "PARALLAX", "distance spent sideways"),
    ("8", "QUILT", f"{QUILT_COLS} x {QUILT_ROWS} = {VIEWS} views"),
]

METERED = [
    (2, "text-to-speech", "pinned model, 0 credits"),
    (4, "avatar render",
     f"{CREDIT_TIERS[0]}, {CREDIT_TIERS[1]} or {CREDIT_TIERS[2]} credits"),
]

LOCAL = ["matting model", "depth model", "warp + interleave", f"{PROBES} probes"]

# Column index, name, where it sits. len() of this is the gate count that the
# stamp and the aria-label both print.
GATES = [
    (0, "separation", "stage 5, the matte"),
    (2, "transcript diff", "stage 2, before spend"),
    (3, "identity pin", "stage 3, before spend"),
    (4, "PII scan", "at publish"),
]

# ---------------------------------------------------------------- the geometry

W, H = 1040, 780
LEFT, RIGHT = 20, 1020
CARD_W = 196
COL = [20, 226, 432, 638, 844]          # pitch 206, so a 10px gutter
PAD = 14                                 # text inset from a card's left edge
BAR = 3.5                                # the accent bar down a card's left


def num(v):
    """Render a coordinate the way the committed file renders it.

    Ints stay ints and computed centres keep their .0, because `x + CARD_W / 2`
    is a float and the published file has `530.0` rather than `530`. Rounding
    first keeps 9.9 * 7 from arriving as 69.30000000000001.
    """
    return str(round(v, 4)) if isinstance(v, float) else str(v)


def centre(i):
    return COL[i] + CARD_W / 2


def text(x, y, s, font, size, fill, weight="normal", anchor="start", opacity=None):
    tail = f' opacity="{num(opacity)}"' if opacity is not None else ""
    return (f'<text x="{num(x)}" y="{num(y)}" font-family="{font}" '
            f'font-size="{num(size)}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{tail}>{s}</text>')


def rect(x, y, w, h, rx, fill, stroke=None, sw=None, dash=None):
    out = (f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" '
           f'height="{num(h)}" rx="{num(rx)}" fill="{fill}"')
    if stroke:
        out += f' stroke="{stroke}" stroke-width="{num(sw)}"'
    if dash:
        out += f' stroke-dasharray="{dash}"'
    return out + "/>"


def line(x1, y1, x2, y2, stroke, sw=None, dash=None, marker=None):
    out = (f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" '
           f'y2="{num(y2)}" stroke="{stroke}"')
    if sw is not None:
        out += f' stroke-width="{num(sw)}"'
    if dash:
        out += f' stroke-dasharray="{dash}"'
    if marker:
        out += f' marker-end="url(#{marker})"'
    return out + "/>"


def card(x, y, h, fill, stroke, accent, dash=None):
    """A box and the accent bar down its left edge, always emitted as a pair."""
    return [rect(x, y, CARD_W, h, 6, fill, stroke, 1, dash),
            rect(x, y, BAR, h, 1.75, accent)]


def lane(label, y, colour, caption):
    """A lane heading: a mono label, then a caption set just past its end.

    The caption offset is the label's advance width at 14px in the mono stack,
    which is 9.9 per character, plus an 18px gap. That constant is what the
    committed file was laid out with; it is not a metric this can look up.
    """
    return [text(LEFT, y, label, MONO, 14, colour, "700"),
            text(round(LEFT + 18 + 9.9 * len(label), 4), y, caption, SANS, 14, DIM)]


def rule(y):
    return line(LEFT, y, RIGHT, y, EDGE)


def architecture():
    """The whole figure, in the order the committed file lays it out."""
    aria = ("Architecture: metered vendors, ten pipeline stages, the fork, "
            f"local models and {WORDS[len(GATES)]} gates, "
            f"{WORDS[GATES_FAIL_OPEN]} of which fail open")

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{aria}">',

        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{CYAN}"/></marker>'
        '<marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
        'markerHeight="5" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{AMBER}"/></marker>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#081228"/>'
        f'<stop offset="1" stop-color="{INK}"/></linearGradient></defs>',

        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',

        text(LEFT, 42, "Architecture", SANS, 24, PALE, "700"),
        text(LEFT, 66, "One unattended run, left to right. The gates are the "
             "row that can stop it.", SANS, 15, DIM),
        text(RIGHT, 42,
             f"{PROBES} probes  ·  {len(GATES)} gates, {GATES_FAIL_OPEN} "
             f"fail open  ·  {VIEWS} views",
             MONO, 13.5, DIM, anchor="end"),
        text(RIGHT, 62, f"{CREDIT_SCHEDULED} credit per scheduled render",
             MONO, 13.5, DIM, anchor="end"),
        rule(84),
        rule(92),
    ]

    o += lane("METERED", 110, DEEP, "billed per call, never extrapolated")
    for col, name, sub in METERED:
        x = COL[col]
        o += card(x, 118, 52, "#0a1930", DEEP, DEEP)
        o += [text(x + PAD, 140, name, SANS, 14.5, DEEP, "700"),
              text(x + PAD, 160, sub, SANS, 14.5, PALE),
              line(centre(col), 172, centre(col), 232, DEEP, 1.4, marker="ah")]

    o.append(rule(206))
    o += lane("PIPELINE", 224, CYAN, "ten stages, one lock, one budget")
    for i, (idx, name, sub, note) in enumerate(STAGES_SPINE):
        x = COL[i]
        o += card(x, 236, 88, "#0c1a30", EDGE, CYAN)
        o += [text(x + PAD, 260, idx, MONO, 12, CYAN, "700"),
              text(x + 34, 261, name, SANS, 16.5, PALE, "700"),
              text(x + PAD, 284, sub, SANS, 15, CYAN, opacity=0.92),
              text(x + PAD, 307, note, SANS, 14, DIM)]
        if i < len(STAGES_SPINE) - 1:
            o.append(line(x + 197, 280, x + 204, 280, CYAN, 1.6, marker="ah"))

    # The fork. Both arms leave the same point so the drawing cannot imply that
    # the real-time arm branches from somewhere the gates already cleared.
    fork_x, split_y = centre(4), 350
    o += [
        line(fork_x, 324, fork_x, 336, CYAN, 1.6),
        text(fork_x - 12, 331, "one render, two destinations", SANS, 13.5,
             CYAN, anchor="end"),
        f'<path d="M{num(fork_x)},336 L{num(fork_x)},{split_y} '
        f'L{num(centre(0))},{split_y} L{num(centre(0))},392" fill="none" '
        f'stroke="{CYAN}" stroke-width="1.6" marker-end="url(#ah)"/>',
        f'<path d="M{num(fork_x)},336 L{num(fork_x)},{split_y} '
        f'L{num(fork_x)},{split_y} L{num(fork_x)},392" fill="none" '
        f'stroke="{VIOLET}" stroke-width="1.6" stroke-dasharray="4 4" '
        f'marker-end="url(#ah)"/>',
    ]

    for i, (idx, name, sub) in enumerate(STAGES_HOLO):
        x = COL[i]
        o += card(x, 396, 66, "#0c1a30", EDGE, CYAN)
        o += [text(x + PAD, 420, idx, MONO, 12, CYAN, "700"),
              text(x + 34, 421, name, SANS, 16.5, PALE, "700"),
              text(x + PAD, 444, sub, SANS, 15, CYAN, opacity=0.92)]
        if i < len(STAGES_HOLO) - 1:
            o.append(line(x + 197, 429, x + 204, 429, CYAN, 1.6, marker="ah"))

    # Dashed, violet and out of scope: none of the gates below run on it.
    x = COL[4]
    o += card(x, 396, 66, "#0a1428", VIOLET, VIOLET, dash="4 4")
    o += [text(x + PAD, 421, "REAL-TIME ARM", SANS, 14.5, VIOLET, "700"),
          text(x + PAD, 444, "none of these gates apply", SANS, 14, VIOLET,
               opacity=0.9)]

    # Stage 9 sits under the quilt it consumes, not at the end of the row.
    x = COL[3]
    o += card(x, 472, 40, "#0a1930", CYAN, CYAN)
    o += [text(x + PAD, 497, "9", MONO, 12, CYAN, "700"),
          text(x + 32, 498, "CAST", SANS, 15.5, PALE, "700"),
          text(x + 90, 498, "one view per eye", SANS, 14, CYAN, opacity=0.9),
          line(centre(3), 462, centre(3), 470, CYAN, 1.6, marker="ah")]

    o.append(rule(520))
    o += lane("LOCAL", 538, VIOLET, "no vendor, no per-run cost")
    for i, name in enumerate(LOCAL):
        x = COL[i]
        o += card(x, 546, 40, "#0b1428", VIOLET, VIOLET)
        o.append(text(x + PAD, 572, name, SANS, 14.5, VIOLET, "700"))

    o.append(rule(612))
    o += lane("GATES", 630, AMBER, "block before spend, or before ship")
    for col, name, where in GATES:
        x = COL[col]
        o += card(x, 638, 52, "#1a1406", AMBER, AMBER)
        o += [text(x + PAD, 660, name, SANS, 14.5, AMBER, "700"),
              text(x + PAD, 680, where, SANS, 14, DIM),
              line(centre(col), 636, centre(col), 618, AMBER, 1.2,
                   dash="3 3", marker="ag")]

    o += [
        rule(740),
        text(LEFT, 760, "Each box carries one line here. What forced it is in "
             "docs/architecture.html.", SANS, 14.5, DIM),
        text(RIGHT, 760, "every figure measured, none extrapolated",
             MONO, 13.5, DIM, anchor="end"),
        "</svg>",
    ]
    # The committed file ends at the closing tag with no trailing newline.
    return "\n".join(o)


# ------------------------------------------------------------------ the hero

# hero.svg looked like art rather than a diagram, and the first pass here said
# so: ninety-odd rectangles of filmstrip that would be reverse engineering a
# layout engine to reproduce. That was wrong, and reading it disproved it.
# SEVENTY-SEVEN of those rectangles are the quilt, one cell per view, and TEN
# more are the stage pills. The picture was already drawing the counts; nothing
# in the file tied it to them.
#
# So it is generated too. Change the quilt to 8 by 6 and the grid redraws with
# 48 cells, because the cells ARE the views.

HERO_MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"

# GitHub renders a README image into an 838px column, so this 1200-wide figure
# is already scaled to 0.698 before the reader has zoomed at all. At 75% browser
# zoom that compounds to 0.524, which put the old 10.5px labels on screen at
# 5.5px: present, but not readable at a glance. Every size below is chosen
# against that number rather than against how it looks in a full-width preview,
# which is the mistake that made them small in the first place.
#
#   on-screen px at 75% zoom = size * (838 / HERO_W) * 0.75
#
# The floor is about 10px on screen for anything carrying a fact, which is why
# the four figures and their labels are much larger than they were.
HERO_W, HERO_H = 1200, 380

# The two labelled sets are attested, not derived: those clips are not in this
# repository and cannot be counted from it. evals/labels.csv is a different,
# smaller set. Stating them as constants is the honest form.
LABELLED_STILLS, LABELLED_CLIPS = 113, 67

# Ten stages, and the pills name them the way the run does rather than the way
# the diagram does. The count is what is load bearing; the footer says "Ten"
# and an assert below keeps the word and the list from drifting apart.
PILLS = ["wake", "script", "voice x3", "look", "render",
         "nobg", "evals", "depth", "quilt", "glass"]

# Where the four figures sit. Uneven on purpose: each is placed clear of the
# label under the one before it, which is a typographic fact, not a computable
# one, so it is declared. These moved when the labels grew; the widest of them,
# LABELLED STILLS / CLIPS, is 23 characters and sets the first gap.
# Each slot is as wide as the wider of its figure and its label, plus about 18
# of gap. Widths come from the renderer's own advance of 0.634 per character in
# this mono stack, not from an estimate; a 0.6 guess is what once put the title
# flush against the panel.
STAT_X = [64, 335, 499, 736]


def htext(x, y, s, size, fill, weight=None, anchor=None, ls=None, opacity=None):
    """A hero text node, in the attribute order the committed file uses."""
    out = (f'  <text x="{num(x)}" y="{num(y)}" font-family="{HERO_MONO}" '
           f'font-size="{num(size)}"')
    if weight:
        out += f' font-weight="{weight}"'
    out += f' fill="{fill}"'
    if anchor:
        out += f' text-anchor="{anchor}"'
    if ls:
        out += f' letter-spacing="{ls}"'
    if opacity:
        out += f' opacity="{opacity}"'
    return out + f">{s}</text>"


def cell_opacity(col, row):
    """Brightness of one quilt cell.

    A highlight, not a measurement: brightest in the middle column, and a
    gentler lift toward the middle row, so the grid reads as a lit panel rather
    than a table. Written as a curve rather than a table of 77 numbers so it
    still holds if the quilt shape changes.
    """
    cmid, rmid = (QUILT_COLS - 1) / 2, (QUILT_ROWS - 1) / 2
    across = (1 - abs(col - cmid) / cmid) ** 0.85
    down = 1 - 0.2 * abs(row - rmid) / rmid
    return f"{(0.30 + 0.62 * across) * down:.3f}"


def hero():
    """The landing image. Same counts as the diagram, drawn as a poster."""
    assert len(PILLS) == len(STAGES_SPINE) + len(STAGES_HOLO) + 1, (
        "the pills are the ten stages; the footer says so in words")

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{HERO_W}" '
        f'height="{HERO_H}" viewBox="0 0 {HERO_W} {HERO_H}" role="img"',
        ' aria-label="3d-filmmaking-ads-multimodal-evals: taste captured as '
        'labels, compiled into thresholds, enforced by gates. '
        f'{VIEWS} views of one instant.">',
        '  <defs>',
        '    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0%" stop-color="#040914"/><stop offset="55%" '
        'stop-color="#081228"/><stop offset="100%" stop-color="#0b1c3d"/>',
        '    </linearGradient>',
        '    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">',
        '      <stop offset="0%" stop-color="#7dd3fc"/><stop offset="55%" '
        'stop-color="#e0f2fe"/><stop offset="100%" stop-color="#38bdf8"/>',
        '    </linearGradient>',
        '    <radialGradient id="glow" cx="76%" cy="26%" r="66%">',
        '      <stop offset="0%" stop-color="#1d4ed8" stop-opacity=".42"/>'
        '<stop offset="62%" stop-color="#1d4ed8" stop-opacity=".08"/>'
        '<stop offset="100%" stop-color="#1d4ed8" stop-opacity="0"/>',
        '    </radialGradient>',
        '    <pattern id="grid" width="40" height="40" '
        'patternUnits="userSpaceOnUse">',
        '      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#38bdf8" '
        'stroke-opacity=".05" stroke-width="1"/>',
        '    </pattern>',
        '    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">',
        '      <stop offset="0%" stop-color="#38bdf8" stop-opacity=".55"/>'
        '<stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>',
        '    </linearGradient>',
        '    <linearGradient id="bandbg" x1="0" y1="0" x2="1" y2="0">',
        '      <stop offset="0%" stop-color="#0ea5e9" stop-opacity=".07"/>'
        '<stop offset="100%" stop-color="#0ea5e9" stop-opacity=".02"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{HERO_W}" height="{HERO_H}" fill="url(#bg)"/>',
        f'  <rect width="{HERO_W}" height="{HERO_H}" fill="url(#grid)"/>',
        f'  <rect width="{HERO_W}" height="{HERO_H}" fill="url(#glow)"/>',
        f'  <rect x="0" y="0" width="{HERO_W}" height="3" fill="{CYAN}" '
        'opacity=".9"/>',
        htext(64, 118, "3d-filmmaking-ads-multimodal-evals", 38,
              "url(#title)", weight="700", ls=".5"),
        htext(64, 154, "Taste captured as labels, compiled into thresholds, "
              "enforced by gates.", 18, "#93c5fd", opacity=".95"),
        '  <rect x="64" y="178" width="760" height="1" fill="url(#rule)"/>',
    ]

    # The second slot used to be the probe count, which is a count of FILES and
    # the least interesting number here. What the repository is actually for is
    # the ratio beside it, so that is what the poster leads with now. The probe
    # count still appears in the README badge row directly underneath.
    stats = [
        (f"{LABELLED_STILLS} / {LABELLED_CLIPS}", "LABELLED STILLS/CLIPS"),
        (f"{THRESHOLDS_DERIVED} / {THRESHOLDS_GATING}", "DERIVED"),
        (f"{len(GATES)}", f"GATES, {GATES_FAIL_OPEN} FAIL OPEN"),
        (f"{CREDIT_SCHEDULED}", "CREDIT PER RENDER"),
    ]
    # strict: a figure without a slot, or a slot without a figure, is a bug
    # rather than something to silently drop.
    for x, (value, label) in zip(STAT_X, stats, strict=True):
        o.append(htext(x, 240, value, 30, PALE, weight="700"))
        o.append(htext(x, 268, label, 18, "#64a0d8", ls=".6"))

    # The panel, then one cell per view.
    # The panel sits 40 further right than it used to. The four figures needed
    # the room: at the old width the gap between "16 / 16" and the "4" beside it
    # fell to 24px and the two read as one number.
    o.append('  <rect x="940" y="56" width="244" height="132" rx="7" '
             'fill="#060f22" stroke="#7dd3fc" stroke-opacity=".55" '
             'stroke-width="1.5"/>')
    cell_x0, cell_y0, cell_dx, cell_dy = 993, 45, 20, 14
    for row in range(QUILT_ROWS):
        for col in range(QUILT_COLS):
            o.append(f'  <rect x="{cell_x0 + col * cell_dx}" '
                     f'y="{cell_y0 + row * cell_dy}" width="18" height="12" '
                     f'rx="1.5" fill="{CYAN}" '
                     f'fill-opacity="{cell_opacity(col, row)}"/>')
    # Two lines. As one line at a readable size this ran to x=1174, past the
    # right margin; shrinking it instead would have put the only statement of
    # the view count back under 7px on screen.
    o.append(htext(1062, 210,
                   f"{QUILT_COLS} &#215; {QUILT_ROWS} = {VIEWS} VIEWS",
                   15, "#7dd3fc", anchor="middle", ls=".5"))
    o.append(htext(1062, 230, "OF ONE INSTANT",
                   15, "#7dd3fc", anchor="middle", ls=".5"))

    # The run, as ten pills with a dot between each pair.
    o.append('  <rect x="48" y="292" width="1104" height="58" rx="9" '
             'fill="url(#bandbg)"/>')
    pill_x0, pill_dx, pill_w = 67, 108, 93
    for i, name in enumerate(PILLS):
        x = pill_x0 + i * pill_dx
        last = i == len(PILLS) - 1        # the panel, lit brighter than the rest
        o.append(f'  <rect x="{x}" y="305" width="{pill_w}" height="32" rx="6" '
                 f'fill="{DEEP}" fill-opacity="{".20" if last else ".09"}" '
                 f'stroke="{CYAN}" stroke-opacity="{".95" if last else ".45"}"/>')
        o.append(htext(x + 46, 326, name, 16, PALE if last else "#9cc9f5",
                       anchor="middle"))
        if not last:
            o.append(f'  <circle cx="{x + 100}" cy="321" r="2" '
                     f'fill="{CYAN}" opacity=".5"/>')

    o.append(htext(64, 368,
                   f"{WORDS[len(PILLS)].capitalize()} stages, unattended "
                   "&#183; every gate fires before the credit is spent &#183; "
                   "anything that is not a clean success pings loud",
                   15, "#7c9ec4", opacity=".92"))
    o.append("</svg>")
    # Unlike architecture.svg, this file does end with a newline.
    return "\n".join(o) + "\n"


# --------------------------------------------------------------- the audit

# Generating both SVGs does not cover everything that states these counts. They
# are also in docs/architecture.html and in README.md badges and prose, which
# are written by hand and always will be. So the generator owns the numbers and
# this audits every surface against them. The two together are the single
# source: one file computes each count, and no published surface may disagree.
# Scope matters, and getting it wrong makes the check useless rather than
# strict. The first version scanned prose too and raised two false alarms: it
# read `python3 probes/sync_probe.py` as "3 probes", and it flagged the README
# sentence that NARRATES the legacy geometry bug, "pinned at a legacy 8 by 6,
# meaning 48 views". That sentence is correct and load bearing. A document
# explaining a wrong-number failure has to be able to print the wrong number,
# and this repository already learned that a checker which cries wolf gets
# muted (see the retired-claim scanner in tests/test_suite.py).
#
# So MARKUP means the surfaces that DRAW these counts as current fact, where
# every number on screen is an assertion: the SVGs and the HTML page. ALL adds
# markdown, and is used only for shapes prose cannot produce by accident.
MARKUP, ALL = "markup", "all"

FACTS = [
    # `(?<![a-zA-Z])` keeps the 3 in `python3` out; `(?!/)` keeps the directory
    # name in `probes/sync_probe.py` out.
    (r"(?<![a-zA-Z])(\d+)\s+probes\b(?!/)", lambda: (PROBES,), MARKUP,
     "probe count"),
    (r"probes-(\d+)", lambda: (PROBES,), ALL, "probe count (README badge)"),
    # The hero states this as two neighbouring text nodes, "16 / 16" then
    # "DERIVED", which the tag-stripping pass joins into one string.
    (r"(\d+)\s*/\s*(\d+)\s+derived",
     lambda: (THRESHOLDS_DERIVED, THRESHOLDS_GATING), MARKUP,
     "gating thresholds derived"),
    (r"(\d+)\s+gates,\s*(\d+)\s+fail open",
     lambda: (len(GATES), GATES_FAIL_OPEN), ALL,
     "gate count and how many fail open"),
    (r"(\d+)\s*(?:x|×)\s*(\d+)\s*=\s*(\d+)\s+views",
     lambda: (QUILT_COLS, QUILT_ROWS, VIEWS), ALL,
     "quilt shape and its product"),
    (r"(\d+)\s+views", lambda: (VIEWS,), MARKUP, "view count"),
    (r"(\d+)\s+credit per (?:scheduled\s+)?render",
     lambda: (CREDIT_SCHEDULED,), ALL, "credits for one scheduled render"),
]


def visible_text(raw, path):
    """The words a reader actually sees, with markup and entities resolved.

    hero.svg puts a count and its label in two neighbouring text nodes, so
    `13 PROBES` only exists once the tags are gone. Markdown is passed through
    unchanged, because stripping angle brackets from prose would eat real text.
    """
    if path.endswith(".md"):
        return raw
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def surfaces():
    """Every published surface, found by walking rather than by a fixed list.

    A hand-maintained list is how a new file gets published unchecked, which is
    the failure this whole file exists to close.
    """
    out = []
    for sub in ("assets", "docs"):
        d = os.path.join(ROOT, sub)
        for f in sorted(os.listdir(d)):
            if f.endswith((".svg", ".html", ".md")):
                out.append(os.path.join(sub, f))
    return out + ["README.md"]


def audit(exclude=()):
    """Return (problems, hits). A stated count that disagrees is a problem.

    `exclude` drops a surface from the sweep, which --write needs: the file it
    is about to rewrite is the one surface allowed to be out of date, since
    bringing it up to date is the point. Without that it would deadlock, unable
    to fix the stale file because the stale file is stale.
    """
    problems, hits = [], 0
    for rel in surfaces():
        if rel in exclude:
            continue
        raw = open(os.path.join(ROOT, rel)).read()
        text_ = visible_text(raw, rel)
        for pattern, expected_fn, scope, name in FACTS:
            if scope == MARKUP and rel.endswith(".md"):
                continue
            expected = expected_fn()
            for hit in re.findall(pattern, text_, re.I):
                groups = hit if isinstance(hit, tuple) else (hit,)
                got = tuple(int(g) for g in groups)
                hits += 1
                if got != expected:
                    problems.append(
                        f"{rel}: {name} reads {got}, the generator computes "
                        f"{expected}")
    return problems, hits


# Both published figures, and the function that draws each. Defined here rather
# than at the top because it names the builders, which are defined above.
TARGETS = [
    ("assets/architecture.svg", architecture),
    ("assets/hero.svg", hero),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true",
                   help="fail if the committed SVG is not what this emits")
    g.add_argument("--write", action="store_true", help="regenerate the SVG")
    g.add_argument("--audit", action="store_true",
                   help="fail if any published surface states a count that "
                        "disagrees with the generator")
    args = ap.parse_args()

    if args.audit:
        problems, hits = audit()
        if problems:
            print(f"{len(problems)} surface(s) state a count the generator "
                  f"disagrees with:", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            return 1
        print(f"{hits} stated counts across {len(surfaces())} surfaces all "
              f"agree with the generator")
        return 0

    if args.write:
        # Refuse to write a figure the rest of the repository contradicts. The
        # diagrams are downstream of the counts, so if a count has moved, README
        # and the other surfaces get updated FIRST and the pictures are redrawn
        # from them. Reversing that order is exactly how a diagram becomes a
        # second source of truth, which is the thing this file exists to stop.
        # The files about to be rewritten are the ones allowed to be stale.
        problems, _ = audit(exclude=tuple(rel for rel, _ in TARGETS))
        if problems:
            print("refusing to write: other surfaces disagree with the counts "
                  "this would draw.", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            print("Update those first, then regenerate.", file=sys.stderr)
            return 1
        for rel, build in TARGETS:
            path = os.path.join(ROOT, rel)
            built = build()
            was = open(path).read() if os.path.exists(path) else None
            with open(path, "w") as fh:
                fh.write(built)
            state = "unchanged" if built == was else "REWRITTEN"
            print(f"{rel} {state} ({len(built)} bytes)")
        return 0

    failed = 0
    for rel, build in TARGETS:
        path = os.path.join(ROOT, rel)
        built = build()
        if not os.path.exists(path):
            print(f"{rel} is missing; run --write", file=sys.stderr)
            failed += 1
            continue
        on_disk = open(path).read()
        if built == on_disk:
            print(f"{rel} matches the generator "
                  f"({PROBES} probes, {len(GATES)} gates, {VIEWS} views)")
            continue
        failed += 1
        print(f"{rel} DIFFERS from the generator.", file=sys.stderr)
        print("Either the file was hand edited, or a count moved and the file "
              "was not regenerated. Run --write and read the diff.",
              file=sys.stderr)
        diff = difflib.unified_diff(on_disk.split("\n"), built.split("\n"),
                                    "committed", "generated", lineterm="", n=1)
        for i, ln in enumerate(diff):
            if i > 40:
                print("  ...", file=sys.stderr)
                break
            print("  " + ln, file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
