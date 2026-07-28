# agentic-video-pipeline-evals

**An agent pipeline that produces a narrated video every morning and puts it on a physical display, with nobody watching it happen.**

It runs three times a day on a schedule, against metered vendor APIs, unsupervised. That constraint is the entire project. An agent you are watching can be corrected. An agent spending money on a schedule with nobody in front of the screen cannot, so most of this repo is guards, evals, and measurements rather than rendering code.

> The character in the rendered video is generated. She is not a real person and not a likeness of one. This repo is about the pipeline around her.

---

## What it does

```
script  ->  cloned-voice synthesis  ->  look generation  ->  video render
        ->  local GPU depth estimation  ->  view array  ->  physical display
```

Seven stages, scheduled, unattended. A nine-invariant eval harness scores the output. Runtime guards block bad calls before they reach a paid API. Per-run counters catch overspend.

The output target is a light-field panel, which is why the pipeline renders 77 views per frame instead of one. It renders view arrays rather than flat frames specifically so the display device can change without touching the render path.

---

## What I found by measuring it

The general lesson on the left, what actually happened on the right.

| | |
|---|---|
| **Count attempts, not outcomes.** | "I asked the AI to follow a rule and it ignored me. I stopped asking and put the rule in code instead, where it can't be negotiated with. It held every time after that, and the first thing it blocked was me." |
| **Reliability multiplies. 80% twice is 64%.** | "Every step works most of the time. But most of the time, twice in a row, is a coin flip, and only 4 of 7 runs made it all the way to the screen." |
| **Delete its config. Still passes? Not a check.** | "I had four safety checks, so I broke them on purpose to see what they'd do. Three approved everything when a single config file went missing, and still showed green. Two of those three had no idea they were doing it." |
| **Benchmarks prove speed, not cause.** | "I made it 2.5x faster and wrote down why. Later I checked production and the speedup was real but my explanation wasn't, and the setting meant to run ten things at once was running one." |
| **Never right? Delete, don't tune.** | "I built a checker to catch bad videos. In its entire life it flagged exactly one, and when I looked at that video it was fine. So I took away its power to block anything instead of tuning it until it agreed with me." |
| **No stopwatch, no saving.** | "Half an hour, start to finish, with nobody watching it. I won't tell you what that saves, because I never put a stopwatch on a human doing it by hand, and a number I made up is the easiest thing here to get caught on." |

Four of those six are me finding my own work was not what I had written down. That is the point of the repo.

---

## The numbers

Measured from logs, not estimated. Every figure carries its sample size, because a rate without a denominator is decoration.

| | | |
|---|---|---|
| Runs on schedule | 10 of 10 consecutive days, 0 missed | n=10 days |
| Runs that did real work | 13, all succeeded, 0 errors | n=13 |
| Runs that correctly did nothing | 21 of 37 wake-ups | n=37 |
| Full chain completion | 4 of 7 | n=7, across 2 days |
| Quality gate true positives | 0 of 7 evaluations | n=7 |
| Constraint held, final outcome | 14 of 15 | n=15 |
| Constraint held, first attempt | 6 of 15 | n=15 |
| Daily render cost | 2 vendor credits | measured at 4 clip lengths |
| End to end latency | median 33 min | n=4 |
| Benchmark speedup | 229s to 89s, byte-identical output | n=1 A/B |

The two constraint rows are the same rule measured two ways. The gap between them is what a runtime guard did that an instruction did not.

**What I cannot tell you:** any dollar figure, because no credit-to-currency rate was ever recorded. Time saved, because no manual baseline was ever measured. Both are in [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md) with what would need instrumenting to get them.

**Honest scope:** the morning stage has 10 days of history. The other two stages are newer, and all three have coexisted for about a day and a half. This is a working system, not a long-running one.

---

## How it is built

**Voice.** A cloned voice model synthesizes the narration from a written script. Synthesis happens before rendering, so the audio drives the video rather than the reverse. Every draw is metered by character count against a per-run ceiling.

**Video.** A look image is generated per run and then animated against the pre-rendered audio track. The still turns out to be the reproducibility seed: the vendor exposes no seed parameter, but animation from a fixed still is deterministic, so the generated image is the thing that controls the output.

**Vision.** Frames go through monocular depth estimation running locally on the GPU (Apple Silicon MPS), then a parallax warp, then a 7x11 view array. Depth runs at batch 8 with stride 2 and interpolates the gaps, which is where the measured speedup actually comes from.

**Evaluation.** Nine invariants, each with a pass exemplar, a fail exemplar, and a threshold *derived* from those exemplars rather than typed by hand. Around a dozen probes measure drift, lip sync, temporal spasm, left-right symmetry, eye direction, hand position, seams, levels, scene complexity, and background detail. Judging is blind: cases are duplicated under opaque names with the de-blinding key held separately, so the grader cannot see the label it is grading.

**Enforcement.** Guards run as pre-call hooks and block a request before it reaches a paid API. Identity pinning refuses any render whose voice or avatar id is not the pinned one, on every egress path including raw HTTP, not just the SDK. A pre-spend gate checks physical plausibility before credits are burned.

**Orchestration.** Three scheduled stages, each a headless agent run under a budget guard and a wall-clock timeout. Failures degrade to a known-good clip rather than showing a broken frame, and anything that is not a clean success raises an alert. The alerting test is inverted deliberately: it fires on everything that is not success, rather than on an enumerated list of known failures, so an unanticipated failure mode is loud on day one.

**Cost.** Every metered call is counted per run. The engine tier is pinned to the flat-rate option, which costs the same for a 9 second clip as for a 126 second one, while the premium tiers cost 43x more for identical output.

---

## Running it

The pipeline itself needs my vendor accounts and a light-field panel, so it is not the part you can run. The **measurement layer is**, and that is the part worth reading anyway.

```
pip install -r requirements.txt          # opencv-python, numpy. Guards need jq.

python3 probes/sync_probe.py             # no args: prints what it measures and why
python3 probes/sync_probe.py clip.mp4    # measures lip-sync lag on your own clip
python3 probes/eye_eval.py --validate    # scores the harness against its labelled set
                                         # (the labelled clips are not published, so this
                                         #  reports an empty set on a fresh clone)
```

Every probe with no arguments prints its own derivation: what it measures, the exemplars its threshold came from, and in several cases the earlier versions of itself that were falsified and why. That is deliberate. A threshold you cannot interrogate is a magic number.

To reproduce the fail-open finding in [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md), take away a guard's dependency and read its exit code:

```
PROP_GATE=/nonexistent bash guards/pre_render_sanity.sh </dev/null; echo $?   # 0, and it says why
IDENTITY_PINS=/nonexistent bash guards/block_unpinned_identity.sh </dev/null; echo $?
```

The privacy gate that ran before this repo was published is also here and also runnable:

```
git config core.hooksPath .githooks       # one line per clone, see .githooks/pre-commit
bash tools/pii_scan.sh                    # deterministic layer
```

---

## Read next

- [`docs/RELIABILITY.md`](docs/RELIABILITY.md), why the quality gate stopped blocking and what replaced it
- [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md), the four guards, which three fail open, and how I found out
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md), every number above traced to the file and command that produced it
- [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md), what this repo does not claim, and why
- [`docs/PII-REVIEW.md`](docs/PII-REVIEW.md), the pre-publish privacy gate, what it caught, and every finding dismissed by hand

---

Built by James Niu. Licensed [MIT](LICENSE).
