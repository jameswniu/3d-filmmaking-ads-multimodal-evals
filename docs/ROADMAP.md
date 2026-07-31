# Roadmap

Work that is known, scoped and deliberately not done yet. Anything here is a
decision to defer, not an oversight; if something turns out to be wrong rather
than merely pending it belongs in [NOT-MEASURED.md](NOT-MEASURED.md) instead.

## Back-port the fixes to the private tree

**Status:** open. Deferred on purpose while the fixes were being proven here.

This repository is the published half of a system whose working tree lives
elsewhere. During the hardening pass the fixes were made *here first*, against
the public code, so they could be tested in the open by anyone. The private tree
has not received them. Until it does, the two halves disagree, and the private
one is the one that actually renders video.

That is the wrong direction for the code to flow and it is temporary.

### What has to move

Grouped by what the fix was, because the diff alone does not explain any of it.

**The two hole fillers were one improvement that reached one caller.**
`pipeline/holes.py` is new and both warps now import it. Before that,
`warp_fast` filled disocclusions from the background side and `wiggle_preview`
used plain nearest neighbour, and the benchmark asserting they agreed passed
only because real depth maps are smooth enough for the holes to stay small.
Against a hard depth step at the subject they disagreed on most views. The
preview was not showing what the renderer produced.

**Both models are pinned to refs that cannot move.** `pipeline/matte_video.py`
loaded from a moving branch with the confirmation prompt suppressed, and
`pipeline/depth_infer.py` fetched a model with no revision. An upstream
force-push could have changed what either of them meant with nothing here to
notice.

**Stage 0 exists.** `pipeline/wake.sh` is the scheduler, lock, budget cap and
timeout, with its own selftests. Its first version released the lock from an
`EXIT` trap inside a function, which fires when the process exits and not when
the function returns.

**The guards run on a clone.** `guards/learned_rules.md` was never committed, so
`prop_gate.sh selftest` failed anywhere but the machine it was written on, and
the read-back loop the docs describe was inert. `ship_gate.sh` and
`block_unpinned_identity.sh` used a `stat` flag that only exists on macOS and
now fall back the way `prop_gate.sh` already did.

**Four probes explained themselves instead of crashing.** `coherence_probe.py`,
`mirror_probe.py`, `scene_simplicity.py` and `sync_probe.py` raised bare
exceptions when invoked with no arguments, which is the failure mode this whole
project is about: a tool that cannot say what it wants.

**The pipeline runs on a fresh clone.** `samples/` ships a synthetic colour and
depth pair, `pyproject.toml` declares the dependencies that `requirements.txt`
deliberately left out, and `quilt.py` and `warp_fast.py` no longer resolve paths
against the working directory.

### The generator, which reversed direction

The diagrams used to be written by a generator that lived only in the private
tree. `tests/test_suite.py` called that out as a live hazard rather than a note:
regenerating from over there would quietly reinstate claims this repository had
already retired, and no check here could have seen it happen.

`tools/render_diagrams.py` now lives here and emits `assets/architecture.svg`,
and CI fails if the committed file is not what it produces. So this one item
runs against the direction of everything above it: nothing is copied INTO the
private tree, something is removed FROM it.

That private generator wrote both SVGs, so removing it is two decisions with
very different costs, and they should not be made as one.

**The architecture half is superseded. Delete it.** The generator here
reproduces the published file byte for byte, so nothing is lost by dropping the
other one. Keeping both is worse than redundant: CI can only guarantee that
`architecture.svg` is what the generator emits while ONE thing emits it, and a
second writer is an unguarded path to a guarded file. That is the same shape as
the two hole fillers above, where one caller got the fix and the other did not.

**The hero half is a real decision, and it is not free.** Nothing here
regenerates `assets/hero.svg`; it is audited for its counts and scanned for
retired claims, but it is not produced from them. Deleting the private generator
therefore makes `hero.svg` a hand-edited file permanently. That is defensible,
since the two checks cover the ways it actually went wrong before, but the
alternative is porting hero generation into `tools/render_diagrams.py` and it is
worth choosing on purpose rather than discovering later.

### Done means

The private tree passes this repository's own suite, and a diagram regenerated
there is byte-identical to the one committed here.
