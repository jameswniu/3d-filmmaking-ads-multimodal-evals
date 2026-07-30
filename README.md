<p align="center">
  <img src="assets/hero.svg" alt="agentic-video-pipeline-evals: an unattended pipeline that ships a narrated hologram daily, with nobody watching" width="100%">
</p>

<p align="center">
  <img alt="runs unsupervised" src="https://img.shields.io/badge/runs-unsupervised-0ea5e9?style=for-the-badge&labelColor=0a1630">
  <img alt="render cost" src="https://img.shields.io/badge/render-1_credit_flat-38bdf8?style=for-the-badge&labelColor=0a1630">
  <img alt="probes" src="https://img.shields.io/badge/probes-12-7dd3fc?style=for-the-badge&labelColor=0a1630">
  <img alt="guards" src="https://img.shields.io/badge/guards-4-60a5fa?style=for-the-badge&labelColor=0a1630">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-93c5fd?style=for-the-badge&labelColor=0a1630">
</p>

**Every morning, with nobody watching, this pipeline writes a script, speaks it in a cloned voice, renders a character, estimates depth on a local GPU, and puts 77 views of her on a physical light-field display.** Most of this repo is not the rendering. It is the guards, evals, and measurements that make spending real money unattended survivable.

<table>
  <tr>
    <td width="55%" align="center">
      <img src="assets/glass-feed-demo.gif" alt="The final product: tonight's governed render, the clip the light-field panel plays" width="100%"><br>
      <sub><b>The final product.</b> Tonight's governed render, cloned voice and all, exactly as the light-field panel receives it. GIFs are mute, so: <b><a href="assets/glass-feed-demo.mp4">&#9654; watch it with sound (mp4)</a></b></sub>
    </td>
    <td width="45%" align="center">
      <img src="assets/quilt.png" alt="The same pipeline's 7x11 view array" width="100%"><br>
      <sub><b>The same pipe, as the display eats it.</b> A real morning brief as its 7x11 quilt: 77 tiles, one instant, 77 eye positions. This is why it reads as 3D on the panel.</sub>
    </td>
  </tr>
</table>

> The character is generated. She is not a real person and not a likeness of one. This repo is about the pipeline around her.

## Every stage, visually

Ten stages, numbered 0 to 9, every cell from real pipeline output. Different renders across the cells on purpose; one clip everywhere would hide that the harness governs a *distribution*, not a lucky take. Stages 8 and 9, the quilt and the glass feed, are the pair at the top of the page, and the code behind each stage is in [`pipeline/`](pipeline/).

<table>
  <tr>
    <td width="33%" align="center">
      <img src="assets/stage-wake.svg" alt="Stage 0: the scheduled wake" width="100%"><br>
      <sub><b>0. Wake.</b> Stage zero is a timer, not a person: a headless agent starts under a budget, a timeout, and armed guards.</sub>
    </td>
    <td width="33%" align="center">
      <img src="assets/stage-script.svg" alt="Stage 1: the script" width="100%"><br>
      <sub><b>1. Script.</b> Written on schedule, kept above 250 characters because shorter scripts measurably brighten the voice.</sub>
    </td>
    <td width="33%" align="center">
      <img src="assets/voice-wave.png" alt="Stage 2: the cloned-voice waveform" width="100%"><br>
      <sub><b>2. Voice.</b> Three takes drawn per script, consensus-picked; this waveform is tonight's winning take.</sub>
    </td>
  </tr>
  <tr>
    <td width="33%" align="center">
      <img src="assets/look-still.jpg" alt="Stage 3: a generated look" width="100%"><br>
      <sub><b>3. Look.</b> A generated appearance from the pinned avatar group; the still is the reproducibility seed.</sub>
    </td>
    <td width="33%" align="center">
      <img src="assets/render-demo.gif" alt="Stage 4: the animated render" width="100%"><br>
      <sub><b>4. Render.</b> Audio drives the animation; a different golden-set look than the cells beside it, on purpose.</sub>
    </td>
    <td width="33%" align="center">
      <img src="assets/stage-nobg.jpg" alt="Stage 5: background removal, before and after" width="100%"><br>
      <sub><b>5. Matte.</b> Background removal on the same instant, before and after; the hair is where this stage earns its keep.</sub>
    </td>
  </tr>
  <tr>
    <td width="33%" align="center">
      <img src="assets/render-frame.jpg" alt="Stage 6: a frame under evaluation" width="100%"><br>
      <sub><b>6. Evals.</b> Nine invariants score every clip; a third distinct look, from a take the harness passed.</sub>
    </td>
    <td width="33%" align="center">
      <img src="assets/depth.png" alt="Stage 7: the inferred depth map" width="100%"><br>
      <sub><b>7. Depth.</b> Monocular depth inferred on the local GPU; this map is what turns one frame into 77 views.</sub>
    </td>
    <td width="33%" align="center" valign="middle">
      <sub><b>8. Quilt and 9. Glass</b> are the pair at the top of this page.<br><br>The module behind every stage ships in <a href="pipeline/"><b>pipeline/</b></a>: matte, depth, quilt, and the cost router whose refusal to guess is the story in <a href="docs/COST.md">COST.md</a>.</sub>
    </td>
  </tr>
</table>

---

## What it does

```
script  ->  cloned-voice synthesis  ->  look generation  ->  video render
        ->  local GPU depth estimation  ->  view array  ->  physical display
```

Seven stages, scheduled, unattended, against metered vendor APIs. A nine-invariant eval harness scores the output. Runtime guards block bad calls before they reach a paid API. Per-run counters catch overspend. The display device can change without touching the render path, because the pipeline ships view arrays rather than flat frames.

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

## Cost

The one-row version: **render on HeyGen Avatar 3.0** (`avatar_iii` in this repo's probes), which billed **1 credit flat** at both ~11 seconds and ~126 seconds, while the premium tiers billed 5 and 43 at the same two lengths. A daily 2-minute clip costs the same credit a 9-second one does.

| engine tier | ~11s | ~126s | shape |
|---|---|---|---|
| Avatar 3.0 flat tier | 1 credit | 1 credit | flat, two measured points |
| premium tiers | 5 credits | 43 credits | not flat, not knowably linear |

The cost router refuses to interpolate between measured points: an earlier confident estimate understated a premium batch by 8.6x and burned 344 credits before anyone noticed. NULL makes a caller ask; a confident 5 makes it spend 43.

Voice is metered per character and audio costs zero render credits, so the pipeline draws 3 voice takes per script (single draws drift audibly) and renders once. Consumption model, tier-sizing math for both vendors, and the full incident: [`docs/COST.md`](docs/COST.md).

---

## How it is built

**Voice.** A cloned voice model synthesizes the narration from a written script. Synthesis happens before rendering, so the audio drives the video rather than the reverse. Every draw is metered by character count against a per-run ceiling.

**Video.** A look image is generated per run and then animated against the pre-rendered audio track. The still turns out to be the reproducibility seed: the vendor exposes no seed parameter, but animation from a fixed still is deterministic, so the generated image is the thing that controls the output.

**Vision.** Frames go through monocular depth estimation running locally on the GPU (Apple Silicon MPS), then a parallax warp, then a 7x11 view array. Depth runs at batch 8 with stride 2 and interpolates the gaps, which is where the measured speedup actually comes from.

**Evaluation.** Nine invariants, each with a pass exemplar, a fail exemplar, and a threshold *derived* from those exemplars rather than typed by hand. Around a dozen probes measure drift, lip sync, temporal spasm, left-right symmetry, eye direction, hand position, seams, levels, scene complexity, and background detail. Judging is blind: cases are duplicated under opaque names with the de-blinding key held separately, so the grader cannot see the label it is grading.

**Enforcement.** Guards run as pre-call hooks and block a request before it reaches a paid API. Identity pinning refuses any render whose voice or avatar id is not the pinned one, on every egress path including raw HTTP, not just the SDK. A pre-spend gate checks physical plausibility before credits are burned.

**Orchestration.** Three scheduled stages, each a headless agent run under a budget guard and a wall-clock timeout. Failures degrade to a known-good clip rather than showing a broken frame, and anything that is not a clean success raises an alert. The alerting test is inverted deliberately: it fires on everything that is not success, rather than on an enumerated list of known failures, so an unanticipated failure mode is loud on day one.

**Cost.** Every metered call is counted per run. The engine tier is pinned to the flat-rate option; the table above is the whole argument.

---

## The pipeline code

Each demoed stage above maps to a real module in [`pipeline/`](pipeline/), ported from the working tree with identities parameterized, the same treatment the guards got:

| stage | module | what it is |
|---|---|---|
| 5, matte | `pipeline/matte_video.py` | background removal tuned for hair, with the dated verdicts that shaped each threshold |
| 7, depth | `pipeline/depth_infer.py` | per-frame monocular depth on Apple Silicon MPS |
| 8, quilt | `pipeline/quilt.py`, `pipeline/quilt_video.py` | parallax warp and the 7x11 view array |
| cost | `pipeline/pick_engine.sh`, `pipeline/route_engine.sh` | the engine router that returns NULL rather than guess a price |

These are reference code, not a turnkey app: the Python stages carry their own heavy dependencies (torch, an open depth model, a matting model) that are deliberately not in `requirements.txt`, which stays scoped to the probes.

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

Want the same pipeline with your own voice and your own character? [`docs/SETUP.md`](docs/SETUP.md) is the build order, with the consent line up top and the measured reasons behind each step.

---

## Read next

- [`docs/SETUP.md`](docs/SETUP.md), clone your voice, generate your character, pin both, in the order that works
- [`docs/COST.md`](docs/COST.md), the measured credit schedule, the 344-credit incident, and which vendor tiers to buy
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md), why the quality gate stopped blocking and what replaced it
- [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md), the four guards, which three fail open, and how I found out
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md), every number above traced to the file and command that produced it
- [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md), what this repo does not claim, and why
- [`docs/PII-REVIEW.md`](docs/PII-REVIEW.md), the pre-publish privacy gate, what it caught, and every finding dismissed by hand

---

Built by James Niu. Licensed [MIT](LICENSE).
