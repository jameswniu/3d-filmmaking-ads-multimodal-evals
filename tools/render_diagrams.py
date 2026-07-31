#!/usr/bin/env python3
"""Emit assets/architecture.svg from the counts, instead of trusting a typed copy.

WHY THIS FILE EXISTS. The published diagrams were written by a generator that
lived in a private tree and was never committed. tests/test_suite.py said so out
loud, because it made a specific failure possible: regenerating from over there
would silently restore claims this repository had already retired, and nothing
here would notice. The retired-claim scanner was the mitigation. This is the fix.

WHAT IS ACTUALLY SINGLE SOURCED. The numbers, not the layout. Before this file,
`13 probes` appeared in the stamp, again on a LOCAL card, and again in README.md,
as three independent strings that happened to agree. `77 views` appeared twice
and its factors `7 x 11` once more, with nothing tying the product to the pair.
Now the probe count is COUNTED from probes/*.py, the view count is the PRODUCT of
the quilt shape, the gate count is the LENGTH of the gate table, and every place
they are drawn reads the same value.

The geometry is a declared layout, not a solver. Coordinates are literals here
because the diagram is a fixed 1040x780 figure whose boxes do not move; what
drifts in practice is the numbers, and those are what this computes. Saying it
plainly is better than implying a layout engine that does not exist.

    python3 tools/render_diagrams.py --check    exit 1 if the committed file
                                                differs from what this emits
    python3 tools/render_diagrams.py --write    regenerate it

--check runs in CI, so a hand edit to the SVG, or a count that moves in one
place and not the others, fails the build.
"""
import argparse
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "assets", "architecture.svg")

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


# --------------------------------------------------------------- the audit

# Generating architecture.svg only fixes architecture.svg. The same counts are
# also drawn in assets/hero.svg, stated in docs/architecture.html, and printed
# in README.md badges and prose. hero.svg is an illustration, not a diagram of
# boxes, so it is NOT generated here; reverse engineering ninety-odd rectangles
# of filmstrip art would be inventing a layout engine to solve a problem that is
# actually about four numbers.
#
# So the generator owns the numbers and this audits every surface against them.
# The two together are the single source: one file computes each count, and no
# published surface may disagree with it.
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

    built = architecture()
    on_disk = open(ARCH).read() if os.path.exists(ARCH) else None

    if args.write:
        # Refuse to write a figure the rest of the repository contradicts. The
        # diagram is downstream of the counts, so if a count has moved, README
        # and the other surfaces get updated FIRST and the picture is redrawn
        # from them. Reversing that order is exactly how a diagram becomes a
        # second source of truth, which is the thing this file exists to stop.
        problems, _ = audit(exclude=("assets/architecture.svg",))
        if problems:
            print("refusing to write: other surfaces disagree with the counts "
                  "this would draw.", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            print("Update those first, then regenerate.", file=sys.stderr)
            return 1
        with open(ARCH, "w") as fh:
            fh.write(built)
        state = "unchanged" if built == on_disk else "REWRITTEN"
        print(f"assets/architecture.svg {state} ({len(built)} bytes)")
        return 0

    if on_disk is None:
        print("assets/architecture.svg is missing; run --write", file=sys.stderr)
        return 1
    if built == on_disk:
        print(f"assets/architecture.svg matches the generator "
              f"({PROBES} probes, {len(GATES)} gates, {VIEWS} views)")
        return 0

    print("assets/architecture.svg DIFFERS from the generator.", file=sys.stderr)
    print("Either the file was hand edited, or a count moved and the file was "
          "not regenerated. Run --write and read the diff.", file=sys.stderr)
    import difflib
    diff = difflib.unified_diff(on_disk.split("\n"), built.split("\n"),
                                "committed", "generated", lineterm="", n=1)
    for i, ln in enumerate(diff):
        if i > 40:
            print("  ...", file=sys.stderr)
            break
        print("  " + ln, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
