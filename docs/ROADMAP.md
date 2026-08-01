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

`tools/render_diagrams.py` now lives here and emits BOTH SVGs, and CI fails if
either committed file is not what it produces. So this one item runs against
the direction of everything above it: nothing is copied INTO the private tree,
something is removed FROM it.

**Delete the private generator. It is fully superseded, and this is now safe
in both halves.**

Both files reproduce byte for byte, `architecture.svg` at 20145 bytes and
`hero.svg` at 14827, so nothing is lost by dropping the other copy. Keeping both
is worse than redundant: CI can only guarantee a file is what the generator
emits while ONE thing emits it, and a second writer is an unguarded path to a
guarded file. That is the same shape as the two hole fillers above, where one
caller got the fix and the other did not.

This was briefly listed as two decisions, because the hero half looked like a
poster rather than a diagram and porting it looked like reverse engineering
ninety rectangles of art. Reading the file settled it the other way: 77 of those
rectangles are the quilt, one per view, and 10 more are the stage pills. It was
already drawing the counts. Now it draws them FROM the counts, so a quilt of
8 by 6 redraws the grid with 48 cells instead of leaving the picture asserting
77 that nothing produces.

### Done means

The private tree passes this repository's own suite, and a diagram regenerated
there is byte-identical to the one committed here.

### Then, and only then: delete the two remaining working branches

`checkpoint-13-of-16` and `restore-point-2026-07-30` are fully merged into
`main`, so nothing is lost by deleting them today. They are kept anyway until
the back-port above is finished, because they are the only other place some of
these fixes exist in a form you can `git checkout`, and a branch costs nothing
while a re-derivation costs a day.

`readme-code-visibility` was deleted on 2026-08-01, local and remote. It was
fully merged with zero unmerged commits, so it held nothing the other two do
not.

## Done and not to be redone

Kept here because the next reader will otherwise wonder whether these are still
open, and because one of them is destructive and must not be repeated casually.

**The repository was deleted and recreated on 2026-08-01.** Two commit messages
had reached the public remote carrying a word this repo's own scanner refuses to
publish. Rewriting the messages orphaned those commits but GitHub keeps
unreachable objects at their SHA URLs indefinitely, so both still answered HTTP
200 after the force-push. Deleting the repository destroys the object database,
which is the only reliable way to make them 404, and both now do.

Everything that does not live in git had to be restored by hand: 20 topics, the
description, the homepage, GitHub Pages on `main` and `/docs`, and the
issues/wiki/projects flags. Two things could not be: the creation date now reads
2026-08-01, and the Actions run history started empty. Nothing else was lost
because the repo had no issues, pull requests, releases, stars or forks.

A verified backup was taken first and is deliberately retained at
`~/backups/avpe-2026-08-01/`: an all-refs bundle, a mirror clone, a restore-test
clone proving the bundle reproduces all 97 commits, the working tree including
the three gitignored PII files that no bundle would carry, and the original
repository metadata. Keep it. The bundle alone does not carry
`tools/pii_context.txt`, so the worktree copy is not redundant with it.

**The scan gate was rebuilt the same day.** `apply_rule_table` never passed the
flags argument `run_rule` already accepted, so every project rule ran
case-sensitive and a shouted spelling walked through. The rule table now takes
an optional fifth column. Two protected names turned out to be homographs of
ordinary English words, so one keeps exact-case matching and a shell variable
was renamed to remove the other collision. `.githooks/commit-msg` was reading
four fields against a five-field table, which silently unmatched every pattern
and passed everything while still printing its banner; it now reads five, honours
each rule's own flags, and enforces the second severity as well. Both are backed
by tests that fail on the previous code.

This is gated on the back-port, not on the calendar. Delete them when the
private tree is green, not before.
