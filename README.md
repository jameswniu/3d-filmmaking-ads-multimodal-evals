<p align="center">
  <img src="assets/hero.svg" alt="3d-filmmaking-ads-multimodal-evals: evals govern a cloned voice, a generated character, and a light-field render" width="100%">
</p>

<p align="center">
  <img alt="labelled: 113 stills, 67 clips" src="https://img.shields.io/badge/labelled-113_stills_%C2%B7_67_clips-0ea5e9?style=flat-square&labelColor=0f172a">
  <img alt="probes: 12, each derived from labels" src="https://img.shields.io/badge/probes-12_derived-164e63?style=flat-square&labelColor=0f172a">
  <img alt="gates: 4, blocking" src="https://img.shields.io/badge/gates-4_blocking-164e63?style=flat-square&labelColor=0f172a">
  <img alt="views: 77 per frame" src="https://img.shields.io/badge/views-77_per_frame-164e63?style=flat-square&labelColor=0f172a">
  <img alt="cost: 1 credit per render" src="https://img.shields.io/badge/cost-1_credit_%2F_render-164e63?style=flat-square&labelColor=0f172a">
  <img alt="license: MIT" src="https://img.shields.io/badge/license-MIT-164e63?style=flat-square&labelColor=0f172a">
</p>

**An advertising-grade AI filmmaking pipeline where the evals are the product.** It writes a script, speaks it in a cloned voice, renders a consistent generated presenter, separates her from her background, infers depth, and emits 77 views of a single instant for a light-field display. It does this on a schedule, against metered vendor APIs, with nobody watching. What makes that survivable is not the render path. It is that one person's taste was captured as labels, compiled into thresholds, and wired into gates that can refuse to spend.

<table>
  <tr>
    <td width="55%" align="center">
      <img src="assets/glass-feed-demo.gif" alt="The presenter explaining the pipeline that renders her" width="100%"><br>
      <sub><b>The product, one pass, start to finish.</b> She is explaining the pipeline that renders her. GIFs are mute and the voice is half the point, so: <b><a href="assets/glass-feed-demo.mp4">&#9654; watch it with sound (2:08 mp4)</a></b></sub>
    </td>
    <td width="45%" align="center">
      <img src="assets/quilt.png" alt="The same frame as a 7x11 array of 77 views" width="100%"><br>
      <sub><b>The same instant, 77 times.</b> One frame of that clip as its 7x11 quilt: 77 camera positions across the view cone, which is what the panel turns back into depth.</sub>
    </td>
  </tr>
</table>

> The presenter is generated. She is not a real person and not a likeness of one. Her voice is a clone of a consented source. Every asset on this page comes from **one** run of the pipeline, deliberately, because a montage of lucky takes would hide the thing this repo is about.

---

## Evals lead this

A wrong number in a chart fails loudly. A generated human fails **plausibly**: hair that fuzzes at the edge, a mouth trailing the audio by four frames, a gesture landing after the word it belonged to, eyes holding too still for thirty seconds. Each is invisible to a type check, obvious to a person, and different in tomorrow's draw. And nobody is awake at render time.

So the pipeline's real job is to make a human eye present at render time by having captured it earlier:

```
label  ->  derive  ->  gate  ->  render  ->  relabel
```

**Label.** 113 hand-labelled stills. 67 labelled clips. 174 frame-level identity records. 677 pairwise A/B verdicts. A render ledger of 14 renders, 7 kept and 3 rejected. Plain-language verdicts, kept as data.

**Derive.** Every threshold in [`probes/`](probes/) comes from a labelled pass exemplar and a labelled fail exemplar. Never typed. The surviving eye model's background bar (4.5) sits between the worst labelled pass (3.30) and the best labelled reject (5.32), and its self-test exits nonzero unless it agrees with the labels 100 percent.

**Gate.** Thresholds become guards that run before money is spent. Judging is blind. Gates are ranked by what happens when they are violated, which is why the same constraint held 14 of 15 runs at the outcome and only 6 of 15 at the first attempt: the gap is a pre-call hook, not better prose.

**Relabel.** Ten scoring models were built in one day and every one inverted against the labels. A lip-sync metric agreed with the eye 8 times out of 8, was wired in as a blocker within minutes, then measured 6 to 10 frames of swing against itself inside a single clip and was demoted the same hour. A brightness bar set to 8.0 because one engine's clip measured 7.9 turned out to mean *resemble that engine*, and steered choices for six hours while gating nothing. Thirteen metrics found nothing about gesture timing until the human said the movement lags the speech, and the literature explained why: gesture aligns to pitch accents as discrete events, so a late one is caught at about 200 milliseconds while an early one is forgiven.

**Full doctrine, with every number and every retraction: [`docs/EVALS.md`](docs/EVALS.md).**

## The clip above, scored by this repo's own probes

Not a claim that it is good. The output of the gates that let it ship.

| probe | reading | bar |
|---|---|---|
| `sync_probe` | lag **-200ms**, early side, IN BAND | late fails at +80ms; early is forgiven |
| `level_probe` | face 7.6, scene 0.7, face-vs-body 8.7, CONSTANT | 8.0 / 5.0 / 12.5 |
| `drift_probe` | PASS, every corner | textureless black gives nothing to track |
| `scene_simplicity` | 3.61 SIMPLE | target 7.5; the cleanest measured clip ran 2.68 |
| `bg_detail` | 1.93 | labelled passes 3.61 to 4.27; labelled rejects 7.05 to 12.06 |
| `spasm_probe` | energy 2.02, ratio 0.63 | **reported, not judged**, per the retraction above |

Pre-spend, the same run: voice drawn 3 times (128.08 / 128.16 / 124.16s, median kept, 3.2 percent spread), transcript diffed against the script before any render, a 0.6s settle beat added, the generated look scored at `bg_detail 2.03` and attested against the frozen-prop rule, and identity checked against the pin allowlist of 279 approved looks.

**One honest asterisk, which is the whole point of the repo.** Three renders of this identical still and audio were produced on three engine tiers. `level_probe` separated them cleanly, passing one and flagging the other two. That probe's face bar is 8.0, and 8.0 was originally calibrated against a clip from one specific engine that measured 7.9. So the metric that separated the trio is the one already documented above as circular. The pick therefore rests on a marginal sync edge and on the eye, not on that probe, and the three were near-identical at frame level anyway, exactly as this repo's own draw-versus-look finding predicts.

---

## Four separations

The filmmaking claim, in one frame: this is not one generative model producing a video. It is four separations, each independently gated, which is what makes any of it controllable.

<p align="center">
  <img src="assets/separations.svg" alt="Four separations: voice from animation, person from background, flat from depth, one view into 77" width="100%">
</p>

| | what comes apart | why it matters | governed by |
|---|---|---|---|
| **1** | **The voice from the animation.** Audio is synthesized first and drives the render, never the reverse. | The performance is fixed and inspectable before a frame exists. A bad read costs characters, not credits. | 3-draw median, transcript diff, settle beat |
| **2** | **The person from the background.** A matting pass lifts her off the room. | Anything frozen behind her betrays the frame as dead; removing it removes the tell. Hair is where this is won or lost. | `bg_detail`, matte tuning |
| **3** | **The depth from the flat image.** A monocular model infers geometry no camera captured. | One rendered frame becomes a scene with distance in it. This is where 2D becomes 3D. | depth inference on local GPU |
| **4** | **One view into seventy seven.** The warp samples 77 camera positions across the display's view cone. | The panel needs every eye position at once. A flat frame cannot hold parallax; a view array can. | quilt geometry, `drift_probe` |

Separation is why the evals can exist at all. A single end-to-end model would leave nothing to measure between the prompt and the pixels.

---

## The suite, stage by stage

Ten stages, and each one reads at three depths: the paragraph is the decision anyone building this has to make, the indented line is what I chose and the measurement that forced it, and the bullets are the literal mechanics. Skim the paragraphs for the argument, drop into the bullets when you want the file and the number. Every image below is from the single run at the top of this page.

<table>
  <tr>
    <td width="33%" align="center"><img src="assets/stage-wake.svg" alt="Stage 0, the scheduled wake" width="100%"></td>
    <td width="33%" align="center"><img src="assets/stage-script.svg" alt="Stage 1, the script" width="100%"></td>
    <td width="33%" align="center"><img src="assets/voice-wave.png" alt="Stage 2, the cloned voice waveform" width="100%"></td>
  </tr>
</table>

### 0. Wake

Supervised or unattended? Everything downstream follows from this one answer. A supervised pipeline can be corrected mid-flight and needs no gates at all; an unattended one cannot be corrected, so it needs every gate in this repository.

> Unattended, on a timer, because the interesting failures only appear when nobody is watching. Each run is a headless agent under a spend budget and a wall-clock timeout.

- A scheduled job fires the run, a lock keeps two runs from racing, a budget guard caps spend, a timeout kills a wedged leg.
- The alert test is inverted on purpose: it fires on everything that is **not** a clean success, rather than on a list of known failures. An enumerated list can only catch what you already thought of, so a novel failure would have been silent. This way it is loud on day one.

### 1. Script

Whose words, and whose register? Generic ad copy is safe and forgettable; real material is specific and risky. Those are two separable problems, and conflating them is why most generated presenters sound like a press release read aloud.

> So they are split across two agents. One assembles **what** to say, out of my actual working notes and roadmaps, which is the difference between a presenter reading marketing and a presenter saying something. A second agent, trained on years of my own prompts, then shapes **how** it sounds: the register, the cadence, the places a real person would hedge or land hard. It rewrites for voice, not for content. Keeping them apart also keeps the thing writing the copy from being the thing that spends the render budget.

- The voice-shaping agent is a separate project with its own repository. **Available on request** (not yet public, so no dead link here).
- The clip on this page is a deliberate exception and says so out loud: for a public demo she explains the pipeline itself rather than anything from my notes.
- Scripts are held above 250 characters, because shorter ones measured about 110 Hz brighter and less consistent on this voice. Padding a short script is quality control, not filler.

### 2. Voice

Clone a real voice or license a synthetic one? Cloning is better and carries a consent obligation that never expires. Clone only your own voice, or one whose owner gave written permission, and treat that as permanent rather than per-project.

> An instant clone from a single **continuous** source take. More audio lost this argument twice: a 69-second stitched reference pitched the voice up (242 and 235 Hz against 216) and scored lower on timbre similarity (0.857 to 0.867 against 0.925 to 0.939) than a 10-second continuous original, and its clips were then rejected by ear, independently, afterward. Continuity of the source beat quantity of it, twice.

- Fourteen candidate clones were built. The winner was picked by ear on a grid that moved exactly one variable at a time, and the runner-up measured 0.08 percent away, so the design made it legible that this was taste rather than measurement.
- Draw 3 takes of the same script and keep the **median by duration**. A single blind draw lands somewhere on a 6 to 37 percent spread, and roughly one in three lands on a tail. This run drew 128.08, 128.16 and 124.16 seconds, a 3.2 percent spread, and kept the median.
- Transcribe the winner and diff it against the intended script. Proper nouns are where synthesis fails, and no render can repair audio that was already wrong.
- Add a 0.6-second settle beat, because the synthesizer returns zero trailing silence and the render ends exactly at the audio, which leaves a mouth mid-motion on the final frame.

<table>
  <tr>
    <td width="33%" align="center"><img src="assets/look-still.jpg" alt="Stage 3, the generated look" width="100%"></td>
    <td width="33%" align="center"><img src="assets/render-demo.gif" alt="Stage 4, the animated render" width="100%"></td>
    <td width="33%" align="center"><img src="assets/stage-nobg.jpg" alt="Stage 5, background removal, source still versus matted render" width="100%"></td>
  </tr>
</table>

### 3. Look

Your own footage or a generated character? Own footage means filming yourself: a real face, at the cost of roughly two minutes of usable material and a consent step. A generated character means no shoot, unlimited wardrobe, and a disclosure obligation that never lapses. This pipeline uses a generated character and discloses it on every public surface, including this page.

> Every look is prompt-generated but anchored to one pinned identity group, so every approved look is provably the same person rather than a family of lookalikes. A frontier image model can supply a reference still instead, for art direction a text prompt will not hold.

The group held 302 looks when this run refreshed its allowlist. That number is deliberately not treated as a constant anywhere in this repo: the scheduled job mints a fresh look per render, so it climbs on its own, and prose pinned to it would be wrong by the next morning. Where a count matters it is stamped with the run that measured it.

- Judge the look *before* spending anything: `bg_detail` must clear the labelled band, and a frozen-prop probe asks whether anything in frame becomes implausible if it never moves for thirty seconds. A steaming cup fails that. A plant is fine.
- Then the identity guard checks the look against the pin allowlist. It fired during this very rebuild: a freshly generated look was correctly refused until the allowlist was refreshed, which is the guard preferring a blocked render over an unverified face.
- **Say nothing about hands.** Five successive hand-posing rules each produced a rejected clip within one render. The engine drives mouth and head from the audio while hands free-run, so any mandated hand activity is motion uncorrelated with speech.
- Wardrobe has to clear the matte, and nothing was checking that. The first pass put a black top on a presenter whose background is matted to pure black: her face cleared the fill by 134 levels of luma and her torso cleared it by **22**, so the body dissolved and left a floating head. Re-shot in cream, the torso now measures **171**. The lesson is the shape of the miss, not the fix: eleven probes scored her face, her motion and her timing, and not one of them asked whether you could see her.

### 4. Render

Text-to-video or audio-driven avatar? General video models are spectacular and unpredictable frame to frame; an audio-driven avatar is narrow, repeatable, and cheap enough to run every day. Advertising needs the same presenter to be identical on Tuesday and Thursday, so repeatability beats spectacle here.

> Audio drives the animation from a fixed still, which is the only reproducibility control on offer: the vendor exposes no seed, so **the still is the seed**. The flat-rate engine is the scheduled default because it bills the same for a 9-second clip as for a 2-minute one, and that single pricing fact is what makes a daily unattended run affordable at all.

- Upload the finished audio as an asset, create the video against the pinned look, poll to completion, download, square-crop, burn subtitles. The clip on this page ran 128.7 seconds and billed 1 credit.
- Cost is measured per engine and never extrapolated. The flat engine billed 1 credit at 11 seconds and 1 credit at 126. The premium engines billed 5 at 11 seconds and **43** at 126, so a plausible-looking `ceil(sec/11) * 5` predicts 60 for the render that actually cost 43. The router returns null for any duration it has not measured, because null makes a caller ask and a confident wrong number makes it spend.
- Geometry gets measured on the delivered file, not trusted from the request flag. A 1:1 request against a landscape look letterboxes unless fit is set, and padding is static by construction, so a corner-sampling check would return a confident false clean.

---

## The fork, and why the evals only work on one side of it

Everything up to here is shared: the schedule, the words, the cloned voice, the pinned face, the animated render. At this point the same presenter becomes two different products, and they are not variations on a theme. They are separated by whether the output exists before anyone sees it.

> **Rendered** output is finished before it ships, so every gate in this repository can run in the gap between "the file exists" and "a human sees it." That gap is the entire reason this pipeline can be trusted unattended. **Live** output has no such gap: the voice is synthesized in the moment, mid-conversation, and there is no frame to inspect before it is already on someone's screen. So the gating doctrine here does not port across the fork. It is not that the live path needs different thresholds. It is that pre-spend review, the mechanism all nine invariants rest on, does not exist there at all.

**The rendered path, stages 5 through 9 below.** Matte, evaluate, infer depth, build the 77-view quilt, cast to glass. Fully built, runs on a timer, and is what the rest of this page documents. Latency is irrelevant, which is exactly what buys room for twelve probes and four blocking guards.

**The live path.** A real-time conversational avatar, its speech driven by a streaming voice agent rather than a rendered audio file. Two things are true about it and neither is a boast:

- It is **parked at its consent gate**, deliberately. The interactive avatar requires a two-minute training video of a real person, and the gate asks a human to confirm the person in that footage is themselves. No agent in this system is permitted to click it, and that is a design decision rather than an unfinished feature.
- The streaming voice-agent side is a separate project with its own regression suite and its own repository. **Available on request** (not yet public, so no dead link here).

Everything below this line is the rendered path.

<table>
  <tr>
    <td width="33%" align="center"><img src="assets/render-frame.jpg" alt="Stage 6, a frame under evaluation" width="100%"></td>
    <td width="33%" align="center"><img src="assets/depth.png" alt="Stage 7, the inferred depth map" width="100%"></td>
    <td width="33%" align="center" valign="middle"><sub><b>8. Quilt</b> and <b>9. Glass</b> are the pair at the top of this page: the 77-view array, and the panel that turns it back into depth.</sub></td>
  </tr>
</table>

### 5. Matte

Keep the room or separate the person? Keeping it is free and reads as dead, because the engine animates only her, so every frozen edge behind her becomes a tell within seconds. Separating her costs a matting pass and buys a background you control completely.

> Matte to pure black, tuned specifically at the hair, which is where every earlier attempt failed. Black is the one solid fill that reads as intentional. A colored fill behind a matted head reads as a cheap green screen, a mistake this pipeline shipped exactly once and never again.

- [`pipeline/matte_video.py`](pipeline/matte_video.py) carries its own dated tuning history in comments, including the verdict that moved each threshold.
- Choosing black is what created the wardrobe trap in stage 3. A fill of zero is the strongest possible separation for a lit face and the weakest possible separation for dark clothing, and those are the same decision. Deciding the background also decides what the presenter is allowed to wear, which nothing in the suite knew until it was measured.

### 6. Evals

Gate on the outcome or on the attempt? Outcome metrics are what dashboards show, and they cannot tell a system that complied apart from a system that was stopped. Measured at the outcome, one constraint here held 14 runs out of 15. Measured at the first attempt, the same constraint held 6 out of 15. Both numbers are true, and only the second one tells you the rule was being ignored and then caught.

> Nine invariants, twelve probes, every threshold derived from a labelled pass exemplar and a labelled fail exemplar, judging done blind, and a hard wall between metrics that **gate** and metrics that only **report**. A metric has to be stable *within* a single clip before it earns any authority over spend, because agreement with a small labelled set is cheap and noise reproduces it easily.

- Probes run against the rendered clip and its subtitle track. The ship gate refuses outright on geometry failures, and for judgement calls it cannot make itself it demands an explicit written reason rather than a boolean.
- Every threshold's derivation, including the ten scoring models that died in a single day, is in [`docs/EVALS.md`](docs/EVALS.md).
- The gates are ranked by what happens when they are violated, not by how important they feel. Nothing here is allowed to be a check in name only: four guards were deliberately broken to find out, and three of them approved everything when a single config file went missing while still reporting green.

### 7. Depth

Capture depth or infer it? Capture wants a depth camera pointed at a real subject, and neither exists here, because the subject was generated. Inference works on any frame including a synthetic one, which makes it the only option that composes with a generated presenter at all.

> Monocular depth estimation running **locally** on the GPU (Apple Silicon MPS) rather than through a cloud API. This runs on every frame of every clip, so a per-frame API call would price the whole pipeline out of daily use. Keeping it local is a cost decision that happens to also be a latency and privacy one.

- [`pipeline/depth_infer.py`](pipeline/depth_infer.py). On the frame above: model load 1.9 seconds, inference 0.4 seconds.
- Frames are batched with a stride and interpolated between, which is where the measured speedup actually comes from. Worth stating plainly: the 2.5x was real and the explanation I first wrote for it was wrong, because the setting meant to run ten things at once was running one.
- **Depth is normalized once across the whole clip, and that costs memory rather than accuracy.** A per-frame or per-chunk range would let the near plane drift between segments, which reads as the depth pulsing and the parallax flickering. Holding one range means holding every frame, so peak memory scales with clip length: the 128-second clip on this page ran to 13.4 GB resident and pushed 16.6 GB to swap on a 64 GB machine. It completed, and a four-minute clip at this resolution would not. The fix is to infer at reduced resolution and upscale the maps, since depth is smooth and tolerates that where colour would not, and it is a fix rather than a workaround because it keeps the single global range. Chunking is the tempting option and it is the wrong one: it trades a visible artifact for an invisible ceiling.

### 8. Quilt

Ship a flat frame or a view array? A flat frame is universally compatible and can never hold parallax. A view array runs on light-field hardware only, and in exchange it decouples the renderer from the display: change the panel, change the geometry, leave the render path untouched.

> 7 columns by 11 rows, 77 views, sampled across the display's view cone by a parallax warp driven by the depth map. One instant, seen from 77 positions at once, which is the whole trick the panel needs in order to give depth back.

- [`pipeline/quilt.py`](pipeline/quilt.py) builds 77 views in 0.8 seconds at 3360 by 3360.
- The geometry is a parameter now, and making it one *was* the fix. The constants had been pinned at a legacy 8 by 6, meaning 48 views, while production had long since moved to 7 by 11. Nothing failed and nothing alerted, because a hardcoded constant has no way to disagree with the pipeline around it. The output was simply built, cleanly and confidently, at a geometry the display no longer expected.
- That is the quietest failure mode in the whole repo and it is worth naming as a class: a wrong number that is *consistent with itself* produces no error anywhere. It was found by reading the code against the display's own filename law, not by any probe. The same drift had also reached this file's prose and a sibling module's docstring, both of which still described 48 views while importing the corrected 77.

### 9. Glass

Screen or light field? A screen is everywhere, and flat. A light-field panel is one device on one desk, and it holds real depth, which is the entire reason the preceding nine stages are shaped the way they are. Remove this stage and most of the pipeline's constraints stop making sense.

> The panel is fed the quilt and does the lenticular work itself. When something goes wrong it degrades to a known-good clip rather than showing a broken frame, and the degradation **pings** instead of passing silently, because a silent fallback is indistinguishable from success.

- Transfer the quilt and cast. A pre-ship gate checks the delivered geometry, since a letterboxed clip on this panel is a hard failure rather than a cosmetic one.
- The shipped product is a quilt **video**, not a still: every frame carries its own 77 views, so the parallax holds while she speaks. That is 77 warps per output frame, which is why the still is what you tune on and the video is what you commit to once the look has settled.

---

## What I found by measuring it

The general lesson on the left, what actually happened on the right.

| | |
|---|---|
| **Count attempts, not outcomes.** | "I asked the AI to follow a rule and it ignored me. I stopped asking and put the rule in code instead, where it can't be negotiated with. It held every time after that, and the first thing it blocked was me." |
| **A metric that agrees with you isn't a metric yet.** | "One check matched my eye 8 times out of 8, so I wired it in to block bad renders. Then I measured the same clip in thirds and it disagreed with itself by up to 10 frames. Demoted it within the hour." |
| **Your threshold might just mean 'look like last time'.** | "A brightness limit was set from one clip that scored 7.9. Later, every good clip was failing it. The number didn't mean 'looks right', it meant 'looks like that one clip', and it had been steering me for hours." |
| **Delete its config. Still passes? Not a check.** | "I had four safety checks, so I broke them on purpose. Three approved everything when a single config file went missing, and still showed green. Two of those three had no idea they were doing it." |
| **Benchmarks prove speed, not cause.** | "I made it 2.5x faster and wrote down why. Later I checked production and the speedup was real but my explanation wasn't, and the setting meant to run ten things at once was running one." |
| **When every predictor inverts, stop predicting.** | "In one day I built ten ways to score these clips and every single one disagreed with my own eyes. So I switched to picking at random and went back to labelling by hand. The models were confidently wrong; random at least knows it isn't." |
| **No stopwatch, no saving.** | "Half an hour, start to finish, with nobody watching it. I won't tell you what that saves, because I never put a stopwatch on a human doing it by hand, and a number I made up is the easiest thing here to get caught on." |

Most of those are me finding my own work was not what I had written down. That is the point of the repo.

---

## The numbers

Measured, not estimated. Every figure carries its sample size, because a rate without a denominator is decoration.

| | | |
|---|---|---|
| Labelled stills / clips | 113 / 67 | hand-curated |
| Identity label records | 174 (115 `her`, 59 `not_her`) | plus an earlier 171-record pass, kept |
| A/B verdicts logged | 677 | pairwise |
| Approved looks, one identity | 279 | pin allowlist |
| Scoring models built and killed | 10 in one day | every one inverted on the labels |
| Runs on schedule | 10 of 10 consecutive days, 0 missed | n=10 days |
| Full chain completion | 4 of 7 | n=7, across 2 days |
| Constraint held, outcome vs first attempt | 14 of 15 vs 6 of 15 | n=15 |
| Quality gate true positives | 0 of 7 evaluations | n=7 |
| Voice draw spread, this clip | 3.2 percent across 3 draws | median kept |
| Depth on one frame | load 1.9s, inference 0.4s | local GPU |
| Quilt build | 77 views in 0.8s at 3360px | n=1 |
| Demo run cost | 89 credits | balance measured before and after |

**What I cannot tell you:** any dollar figure, because no credit-to-currency rate was recorded at measurement time. Time saved, because no manual baseline was ever measured. Both are in [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md) with what it would take to get them honestly.

**Honest scope:** one operator, one machine, one panel, one labeller. The labels are internally consistent and externally unvalidated, and a second labeller is the single most valuable thing this repository is missing.

---

## Cost

The scheduled pipeline renders on the **flat tier**: 1 credit, measured at both 11 seconds and 125.7 seconds. The premium tiers billed 5 credits at 11 seconds and 43 at 125.7, so the multiple on a 2-minute clip is 43x, not 5x.

| engine tier | ~11s | ~126s | shape |
|---|---|---|---|
| flat tier (scheduled default) | 1 credit | 1 credit | flat with length, two measured points |
| premium tiers | 5 credits | 43 credits | scales, and not knowably linear |

The cost router refuses to interpolate between measured points, because an earlier confident estimate understated a premium batch by 8.6x and burned 344 credits before anyone noticed. A null makes a caller ask; a confident 5 makes it spend 43.

**The demo run on this page cost 89 credits**, measured as a balance delta. It rendered the same audio on three tiers in order to compare them, plus one look generation. That is deliberately not the scheduled cost: the daily path is the flat tier. Full model, the incident, and tier-sizing for both vendors: [`docs/COST.md`](docs/COST.md).

Voice is metered per character and synthesis costs zero render credits, which is why the pipeline draws three voice takes and renders once.

---

## The pipeline code

Each demoed stage maps to a module in [`pipeline/`](pipeline/), ported from the working tree with identities parameterized, the same treatment the guards got.

| stage | module | what it is |
|---|---|---|
| 5, matte | `matte_video.py` | background removal tuned at the hair, with the dated verdicts behind each threshold |
| 7, depth | `depth_infer.py` | per-frame monocular depth on Apple Silicon MPS |
| 8, quilt | `quilt.py`, `quilt_video.py`, `warp_fast.py`, `depth_guided.py`, `wiggle_preview.py` | parallax warp and the 77-view array |
| cost | `pick_engine.sh`, `route_engine.sh` | the engine router that returns null rather than guess a price |

Reference code, not a turnkey app: the Python stages need torch, an open depth model, and a matting model, which are deliberately not in `requirements.txt` (that stays scoped to the probes).

## Running it

The pipeline needs my vendor accounts and a light-field panel. The **measurement layer** does not, and it is the part worth reading anyway.

```
pip install -r requirements.txt          # opencv-python, numpy. Guards need jq.

python3 probes/sync_probe.py             # no args: prints what it measures and why
python3 probes/sync_probe.py clip.mp4    # measures lip-sync lag on your own clip
python3 probes/eye_eval.py --validate    # scores the harness against its labelled set
                                         # (labelled clips are not published, so this
                                         #  reports an empty set on a fresh clone)
```

Every probe with no arguments prints its own derivation: what it measures, the exemplars its threshold came from, and in several cases the earlier versions of itself that were falsified and why. A threshold you cannot interrogate is a magic number.

To reproduce the fail-open finding in [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md), take away a guard's dependency and read its exit code:

```
PROP_GATE=/nonexistent bash guards/pre_render_sanity.sh </dev/null; echo $?   # 0, and it says why
IDENTITY_PINS=/nonexistent bash guards/block_unpinned_identity.sh </dev/null; echo $?
```

The privacy gate that ran before this repo was published is here too:

```
git config core.hooksPath .githooks       # one line per clone
bash tools/pii_scan.sh                    # deterministic layer
```

Want the same pipeline with your own voice and character? [`docs/SETUP.md`](docs/SETUP.md) is the build order, consent line first.

---

## Read next

- [`docs/EVALS.md`](docs/EVALS.md), the eval doctrine: every threshold's derivation, every retracted metric, and the case study of cloning a voice by ear
- [`docs/SETUP.md`](docs/SETUP.md), clone your voice, generate your character, pin both, in the order that works
- [`docs/COST.md`](docs/COST.md), the measured credit schedule, the 344-credit incident, and which vendor tiers to buy
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md), why the quality gate stopped blocking and what replaced it
- [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md), the four guards, which three fail open, and how I found out
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md), every number above traced to what produced it
- [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md), what this repo does not claim, and why
- [`docs/PII-REVIEW.md`](docs/PII-REVIEW.md), the pre-publish privacy gate, what it caught, and every finding dismissed by hand

Two companion projects are referenced above and are not public yet: the agent that shapes her register, and the streaming voice-agent pipeline behind the live path. Both **available on request**.

---

Built by James Niu. Licensed [MIT](LICENSE).
