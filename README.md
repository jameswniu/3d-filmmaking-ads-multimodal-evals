

<p align="center">
  <img src="assets/hero.svg" alt="3d-filmmaking-ads-multimodal-evals: evals govern a cloned voice, a generated character, and a light-field render" width="100%">
</p>

<p align="center">
  <img alt="labelled: 113 stills, 67 clips" src="https://img.shields.io/badge/labelled-113_stills_%C2%B7_67_clips-0ea5e9?style=flat-square&labelColor=0f172a">
  <img alt="probes: 13, each derived from labels" src="https://img.shields.io/badge/probes-13_derived-164e63?style=flat-square&labelColor=0f172a">
  <img alt="gates: 4, blocking" src="https://img.shields.io/badge/gates-4_blocking-164e63?style=flat-square&labelColor=0f172a">
  <img alt="views: 77 per frame" src="https://img.shields.io/badge/views-77_per_frame-164e63?style=flat-square&labelColor=0f172a">
  <img alt="cost: 1 credit per render" src="https://img.shields.io/badge/cost-1_credit_%2F_render-164e63?style=flat-square&labelColor=0f172a">
  <img alt="license: GPL-3.0" src="https://img.shields.io/badge/license-GPL--3.0-164e63?style=flat-square&labelColor=0f172a">
</p>

**An advertising-grade AI filmmaking pipeline where the evals are the product.** It writes a script, speaks it in a cloned voice, renders a consistent generated presenter, separates her from her background, infers depth, and emits 77 views of a single instant for a light-field display. It does this on a schedule, against metered vendor APIs, with nobody watching. What makes that survivable is not the render path. It is that one person's taste was captured as labels, compiled into thresholds, and wired into gates that can refuse to spend.

<table>
  <tr>
    <td width="34%" align="center" valign="top">
      <img src="assets/parallax-amplified.gif" alt="The presenter under a swaying virtual camera, nearer pixels travelling further than far ones, amplified four times" width="100%"><br>
      <sub><b>Depth, on a flat screen.</b> A virtual camera sways across the inferred depth map, near pixels travelling further than far ones. <b>This clip is exaggerated 4x and says so on the frame.</b> The real sweep across all 77 views moves her <b>19 px</b> inside a 480 px tile, about 4 percent, which is honest and nearly invisible at this size. The amber tick is fixed, because without something stationary the eye tracks her and cancels the very displacement the clip exists to show.</sub>
    </td>
    <td width="33%" align="center" valign="top">
      <br>
      <img src="assets/views-sweep.gif" alt="Six of the 77 camera views of one instant, cycled" width="100%"><br>
      <sub><b>Six of the 77 views, one instant.</b> Spread across the whole sweep rather than neighbours, because adjacent views differ by <b>0.25 px</b> and a block of them reads as one photo repeated. These are warped at the full square framing rather than cropped out of the quilt, so they sit at the same scale as the clips beside them; the panel's own tiles trim top and bottom to a 1.57 aspect. Every frame of the clip carries its own 77. <b><a href="assets/quilt-video.mp4">&#9654; full quilt video</a></b></sub>
    </td>
    <td width="33%" align="center" valign="top">
      <br><br>
      <img src="assets/hologram-full.gif" alt="The presenter explaining the 77-view quilt while the simulated view sweeps, subtitles held still" width="100%"><br>
      <sub><b>And she explains her own pipeline, in the final treatment.</b> The full narration under the simulated view sweep the first cell demonstrates, one pass, start to finish. This loop is her describing the very grid the middle cell shows: one moment, seventy-seven positions. GIFs are mute and the voice is half the point: <b><a href="assets/hologram-full.mp4">&#9654; watch with sound (2:49)</a></b></sub>
    </td>
  </tr>
</table>

> The presenter is generated. She is not a real person and not a likeness of one. Her voice is a clone of a consented source. Every asset on this page comes from **one** run of the pipeline, deliberately, because a montage of lucky takes would hide the thing this repo is about.

---

## What actually happens to her

Every image below is the **same frame**, `t = 63s`, of the same render. That constraint is the point: if two panels disagree, it is the stage that changed her, not a different take, a different day or a luckier moment.

<p align="center">
  <img src="assets/journey.png" alt="One frame of the presenter carried through six stages: the seed still, the render, the matte, the depth map, the parallax pair, and the 77-view quilt" width="100%">
</p>

<table>
  <tr>
    <td width="34%" align="center">
      <img src="assets/journey.gif" alt="The same six stages cut in sequence on one locked frame" width="100%"><br>
      <sub><b>The same six stages, cut.</b> A grid invites you to compare compositions. A cut on a locked frame shows only what the stage changed.</sub>
    </td>
    <td>
      <b>Why some frames on this page have a background and some do not.</b> Stages 1 and 2 still carry the room, because the room is part of the photograph and no render can move it. Stage 3 takes it out and replaces it with pure black, which is the strongest available separation for a lit face and the weakest for dark clothing. Those two facts are one decision, and this repository shipped a floating head before noticing that.<br><br>
      <b>Stage 4 is where she stops being a picture of a person and becomes a measurement.</b> Depth is inferred locally, per frame, from a flat image no camera ever ranged. Stage 5 spends that depth sideways, moving near pixels further than far ones, which is the only step that produces something two eyes can disagree about. Stage 6 packs all 77 of those disagreements into one frame.<br><br>
      The chain ends there on purpose. What the panel does with that frame is hand a different view to each of your eyes, and no screenshot can reproduce that honestly, so the pictures stop rather than pretend.
    </td>
  </tr>
</table>

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

**This clip does not pass everything, and the failures are the most useful thing on the page, so they lead instead of hiding at the bottom.**

It was picked by eye from a grid: one script rendered across three looks, three voice clones and three engine tiers, one variable moved per cell. Here is what the suite says about the winner.

| probe | reading | bar | verdict |
|---|---|---|---|
| `sync_probe` | lag **-240ms**, early side | late fails at +80ms, early is forgiven | IN BAND |
| `eye_eval` | bg **2.48** | max 4.5 | **PASS** |
| `scene_simplicity` | **4.22** | target 7.5, cleanest measured 2.68 | SIMPLE |
| `bg_detail` | **2.71** | max 5.5 | SIMPLE |
| `separation_probe` | **10.42 percent** of her within 30 luma of the fill | fail at 12 percent | **PASS, by 1.6 points** |
| `hand_probe` | gesture ratio **0.506** | reported, never judged | highest measured |
| `level_probe` | face wander **35.1**, face vs body **93.6** | 8.0 / 12.5 | **FAIL** |
| `lipsync_probe` | dropped **25 of 58** onsets, 43 percent | no mouth response within 0.8s | **FAIL** |
| `drift_probe` | flat corners, nothing to track | needs texture | **INCONCLUSIVE**, by construction |

**The gesture number is worth pausing on.** 0.506 is the highest ratio measured across the whole grid, against 0.182 to 0.345 for everything else. It moved because the still was changed deliberately: earlier looks had folded arms or hands out of frame, this one has open palms in frame. The engine drives mouth and head from the audio while hands free-run, so the only lever on gesture is what the still hands it. That is the "the still is the seed" claim showing up as a measurement rather than an assertion.

**The tightest pass is worth more attention than the failures.** `separation_probe` clears its bar by 1.6 points. That probe was written this session, after a clip shipped in which 30.7 percent of the presenter sat within 30 luma of the black matte and she read as a floating head. The cream-top look that replaced it measured 2.80 percent. This look wears a mid-grey cardigan, so it lands at 10.42 percent: passing, and much nearer the edge than anything else here. A bar derived from two labelled points, n=2, is being asked to adjudicate a case sitting between them. It is reported with its margin rather than as a green tick, because a pass with 1.6 points of room is a different fact from a pass with 9.

**One failure is real and explainable.** Face wander of 35.1 against a bar of 8.0. This look is lit by a window from one side, so her face luminance genuinely swings as she turns. The metric measures something true. Whether 8.0 is the right bar for directional light is unknown, because every labelled exemplar behind that number is flat-lit, and widening a threshold so it admits the clip you just made is the same circularity this repo already retired once.

**One failure survived every explanation I offered, which makes it the honest centrepiece.** Lip-sync drops read 43 percent here. I named a cause twice and was wrong twice. First the still, on the reasoning that the still is the seed. Then a control run revealed the comparison clip had been a different engine all along, so I blamed the engine instead. This clip is a third look on a third engine and still reads 43 percent, so neither story held. Across the grid the figure ranges 19 to 43 percent with no clean association to look, engine or voice.

Two possibilities remain and I cannot separate them from here: the metric's 0.8-second window may be too tight for this voice's pacing, or every clip in the grid genuinely drops phrases and the eye tolerates it. The second is uncomfortable and is not ruled out. What is ruled out is both of my confident explanations, and this repo's own history says that is precisely when to stop theorising and go measure the physics, the way thirteen gesture metrics found nothing until someone described the problem as lag rather than correlation.

So the summary is one most portfolios would not print. **The clip on this page fails two of its own gates: one for a reason I can defend, and one I have now guessed wrong about twice.**

Pre-spend, the same run: voice drawn 3 times (156.88 / 168.96 / 168.64s, median kept, 7.7 percent spread), the synthesized audio transcribed and diffed against the script before any render (541 of 541 words, similarity 1.0000), a 0.6s settle beat added, the look attested against the frozen-prop rule, and identity checked against the pin allowlist.

Two of those gates fired for real rather than rubber-stamping. The identity guard refused the freshly generated look until the allowlist was refreshed, preferring a blocked render to an unverified face. The frozen-prop gate would not accept an attestation without a named finding, so the backdrop travel risk had to be written down before the spend and then discharged after it: measured across 26 samples spanning the full clip, the frozen wall shifts **0 px** with **0** direction reversals, so the one claim her body could not have paid was never made.

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

## Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="System architecture: metered vendors, ten pipeline stages, the fork to the real-time arm, local models, and the four blocking gates" width="100%">
</p>

Four rows, and the reason they are separate rows is the interesting part. **Metered** is anything a run can spend money on, which is exactly two vendors. **Local** is everything that runs on this machine for free, which is why a daily render's marginal cost is one credit and not a model bill. **Gates** sit under the stage they act on, and only four of the thirteen probes are down there: the rest report a number and let the run continue, because a metric that has not proven itself stable inside a single clip has not earned the authority to stop one.

Every figure in the diagram is a measurement published elsewhere in this repository, and the generator refuses to write the file if those figures are no longer in the README, so the picture cannot quietly become a second source of truth.

**Interactive version: [jameswniu.github.io/3d-filmmaking-ads-multimodal-evals/architecture.html](https://jameswniu.github.io/3d-filmmaking-ads-multimodal-evals/architecture.html)**, the same map with every box clickable to show the failure that forced it. Standalone, no dependencies, no build step; the source is [`docs/architecture.html`](docs/architecture.html).

<p align="center">
  <img src="assets/band-stages.svg" alt="The build: ten stages, each one a decision" width="100%">
</p>

## The suite, stage by stage

Ten stages, and each one reads at three depths: the paragraph is the decision anyone building this has to make, the indented line is what I chose and the measurement that forced it, and the bullets are the literal mechanics. Skim the paragraphs for the argument, drop into the bullets when you want the file and the number. Every image below is from the single run at the top of this page, with one exception: the stage 0 and 1 panel carries the numbers of the latest scheduled run, because that is the part of the suite that keeps moving.

<p align="center">
  <img src="assets/stage-wake-script.svg" alt="Stage 0, the scheduled wake, beside stage 1, the script" width="100%">
</p>

https://github.com/user-attachments/assets/9e30abab-52c0-41b8-be9a-e8170a4311f9

<p align="center"><sub><b>Press play: the actual soundtrack.</b> 169 seconds of the cloned voice, the kept median take, under its own waveform. The raw audio also lives in the repo: <a href="assets/voice-narration.m4a">voice-narration.m4a</a>.</sub></p>

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
- Since the re-couple change (2026-07-30), the scheduled daily clip speaks borrowed words **verbatim**: the voice agent writes as me, and the pipeline may trim from the end to fit the 15 to 25 second slot, never rewrite. Today's run borrowed 114 words and trimmed 43.4 seconds down to 25.5. When the borrow fails, the clip is agent-authored and says so in the clip itself, because silently substituting the words is the one failure this stage must never ship.
- Scripts are held above 250 characters, because shorter ones measured about 110 Hz brighter and less consistent on this voice. Padding a short script is quality control, not filler.

### 2. Voice

Clone a real voice or license a synthetic one? Cloning is better and carries a consent obligation that never expires. Clone only your own voice, or one whose owner gave written permission, and treat that as permanent rather than per-project.

> An instant clone from a single **continuous** source take. More audio lost this argument twice: a 69-second stitched reference pitched the voice up (242 and 235 Hz against 216) and scored lower on timbre similarity (0.857 to 0.867 against 0.925 to 0.939) than a 10-second continuous original, and its clips were then rejected by ear, independently, afterward. Continuity of the source beat quantity of it, twice.

- Fourteen candidate clones were built. The winner was picked by ear on a grid that moved exactly one variable at a time, and the runner-up measured 0.08 percent away, so the design made it legible that this was taste rather than measurement.
- Draw 3 takes of the same script and keep the **median by duration**. A single blind draw lands somewhere on a 6 to 37 percent spread, and roughly one in three lands on a tail. This run drew 156.88, 168.96 and 168.64 seconds, a 7.7 percent spread, and kept the median.
- Transcribe the winner and diff it against the intended script. Proper nouns are where synthesis fails, and no render can repair audio that was already wrong. This clip scored 541 of 541 words at similarity 1.0000. The check earns its keep by what it catches on a *bad* run, so it is worth stating that it was skipped on nine earlier renders here and only reinstated after the fact.
- **The synthesis model is pinned, and getting that wrong is silent.** Nine clips shipped on the wrong text-to-speech model before anyone noticed, because a wrong model does not error: it just returns a flatter reading of the correct words. Measured against the human reference on three axes, the wrong model held pitch range at 26.8 Hz against the reference's 44.9, and rested 11.4 percent of the time against the reference's 19.0. The pinned model reads 35.6 and 15.3. Nothing in the pipeline compared a delivered clip to the source recording, so the only detector was a person saying it sounded flat.
- Add a 0.6-second settle beat, because the synthesizer returns zero trailing silence and the render ends exactly at the audio, which leaves a mouth mid-motion on the final frame.
- **Hear it, not just read about it:** [the kept take itself](assets/voice-narration.m4a), 169 seconds, the exact audio track the clip carries.

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

- Upload the finished audio as an asset, create the video against the pinned look, poll to completion, download, burn subtitles from the transcriber's own word timings so the captions cannot drift from the audio. The clip on this page runs 169.2 seconds.
- Cost is measured per engine and never extrapolated. The flat engine billed 1 credit at 11 seconds, at 126, and again at 169. The premium engines billed 5 at 11 seconds, **43** at 126, and **58** at 169. A plausible-looking `ceil(sec/11) * 5` predicts 60 for the render that actually cost 43, so the router returns null for any unmeasured duration rather than guess: null makes a caller ask, a confident wrong number makes it spend.
- **The clip on this page is the premium tier, chosen by eye at 58 times the cost of the default.** The same still and the same audio were rendered on all three tiers and picked by watching them. That is defensible for a portfolio clip watched closely once, and the wrong call for a job that runs every morning forever, which is why the scheduled pipeline stays on the flat tier. The page does not pretend those are the same decision.
- Geometry gets measured on the delivered file, not trusted from the request flag. A 1:1 request against a landscape look letterboxes unless fit is set, and padding is static by construction, so a corner-sampling check would return a confident false clean.

---

<p align="center">
  <img src="assets/band-fork.svg" alt="The fork: one render, two destinations" width="100%">
</p>

## The fork, and why the evals only work on one side of it

Everything up to here is shared: the schedule, the words, the cloned voice, the pinned face, the animated render. At this point the same presenter becomes two different products, and they are not variations on a theme. They are separated by whether the output exists before anyone sees it.

> **Rendered** output is finished before it ships, so every gate in this repository can run in the gap between "the file exists" and "a human sees it." That gap is the entire reason this pipeline can be trusted unattended. **Live** output has no such gap: the voice is synthesized in the moment, mid-conversation, and there is no frame to inspect before it is already on someone's screen. So the gating doctrine here does not port across the fork. It is not that the live path needs different thresholds. It is that pre-spend review, the mechanism all nine invariants rest on, does not exist there at all.

**The rendered path, stages 5 through 9 below.** Matte, evaluate, infer depth, build the 77-view quilt, cast to glass. Fully built, runs on a timer, and is what the rest of this page documents. Latency is irrelevant, which is exactly what buys room for thirteen probes and four blocking guards.

**The live path.** A real-time conversational avatar, its speech driven by a streaming voice agent rather than a rendered audio file. Two things are true about it and neither is a boast:

- It is **parked at its consent gate**, deliberately. The interactive avatar requires a two-minute training video of a real person, and the gate asks a human to confirm the person in that footage is themselves. No agent in this system is permitted to click it, and that is a design decision rather than an unfinished feature.
- The streaming voice-agent side is a separate project with its own regression suite and its own repository. **Available on request** (not yet public, so no dead link here).

Everything below this line is the rendered path.

<table>
  <tr>
    <td width="33%" align="center"><img src="assets/render-frame.jpg" alt="Stage 6, a frame under evaluation" width="100%"></td>
    <td width="33%" align="center"><img src="assets/depth.png" alt="Stage 7, the inferred depth map" width="100%"></td>
    <td width="33%" align="center"><img src="assets/views-six.png" alt="Six of the 77 camera views of a single instant, spread across the sweep" width="100%"><br>
      <sub><b>8. Quilt and 9. Glass.</b> Five of the 77, spread across the sweep rather than neighbours, plus the proof: the amber cell is view 1 minus view 77, so her silhouette lights up exactly where the sweep moved her. No single tile shows parallax, because it lives between tiles. All 77 interleave into the one frame the panel is handed.</sub></td>
  </tr>
</table>

### 5. Matte

Keep the room or separate the person? Keeping it is free and reads as dead, because the engine animates only her, so every frozen edge behind her becomes a tell within seconds. Separating her costs a matting pass and buys a background you control completely.

> Matte to pure black, tuned specifically at the hair, which is where every earlier attempt failed. Black is the one solid fill that reads as intentional. A colored fill behind a matted head reads as a cheap green screen, a mistake this pipeline shipped exactly once and never again.

- [`pipeline/matte_video.py`](pipeline/matte_video.py) carries its own dated tuning history in comments, including the verdict that moved each threshold.
- Choosing black is what created the wardrobe trap in stage 3. A fill of zero is the strongest possible separation for a lit face and the weakest possible separation for dark clothing, and those are the same decision. Deciding the background also decides what the presenter is allowed to wear, which nothing in the suite knew until it was measured.

### 6. Evals

Gate on the outcome or on the attempt? Outcome metrics are what dashboards show, and they cannot tell a system that complied apart from a system that was stopped. Measured at the outcome, one constraint here held 14 runs out of 15. Measured at the first attempt, the same constraint held 6 out of 15. Both numbers are true, and only the second one tells you the rule was being ignored and then caught.

> Nine invariants, thirteen probes, every threshold derived from a labelled pass exemplar and a labelled fail exemplar, judging done blind, and a hard wall between metrics that **gate** and metrics that only **report**. A metric has to be stable *within* a single clip before it earns any authority over spend, because agreement with a small labelled set is cheap and noise reproduces it easily.

- Probes run against the rendered clip and its subtitle track. The ship gate refuses outright on geometry failures, and for judgement calls it cannot make itself it demands an explicit written reason rather than a boolean.
- Every threshold's derivation, including the ten scoring models that died in a single day, is in [`docs/EVALS.md`](docs/EVALS.md).
- The gates are ranked by what happens when they are violated, not by how important they feel. Nothing here is allowed to be a check in name only: four guards were deliberately broken to find out, and three of them approved everything when a single config file went missing while still reporting green.

### 7. Depth

Capture depth or infer it? Capture wants a depth camera pointed at a real subject, and neither exists here, because the subject was generated. Inference works on any frame including a synthetic one, which makes it the only option that composes with a generated presenter at all.

> Monocular depth estimation running **locally** on the GPU (Apple Silicon MPS) rather than through a cloud API. This runs on every frame of every clip, so a per-frame API call would price the whole pipeline out of daily use. Keeping it local is a cost decision that happens to also be a latency and privacy one.

- [`pipeline/depth_infer.py`](pipeline/depth_infer.py). On the frame above: model load 1.9 seconds, inference 0.4 seconds.
- Frames are batched with a stride and interpolated between, which is where the measured speedup actually comes from. Worth stating plainly: the 2.5x was real and the explanation I first wrote for it was wrong, because the setting meant to run ten things at once was running one.
- **Depth is normalized once across the whole clip, and that costs memory rather than accuracy.** A per-frame or per-chunk range would let the near plane drift between segments, which reads as the depth pulsing and the parallax flickering. Holding one range means holding every frame, so peak memory scales with clip length. A 128-second clip at full resolution ran to 13.4 GB resident and pushed 16.6 GB to swap on a 64 GB machine. It completed; a longer one at that resolution would not have.
- **The fix was written down before it was needed, then actually applied.** Infer at half resolution and upscale the maps: depth is smooth and tolerates that where colour would not, and the single global range survives. The clip on this page is 4230 frames, 32 percent longer than the one that nearly exhausted memory, and it ran to **3.3 GB peak with zero swap**, roughly a quarter of the cost. Chunking is the tempting alternative and it is the wrong one: it trades a visible artifact for an invisible ceiling.

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

<p align="center">
  <img src="assets/band-findings.svg" alt="The findings: what measuring it actually turned up" width="100%">
</p>

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

<p align="center">
  <img src="assets/band-numbers.svg" alt="The numbers: counts, never rates" width="100%">
</p>

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
| Voice draw spread, this clip | 7.7 percent across 3 draws | median kept |
| Transcript check, this clip | 541 of 541 words, similarity 1.0000 | run before the spend |
| Rest, this clip vs the human reference | 15.3 percent vs 19.0 percent | the axis that reads as flat |
| Rest, on the wrong synthesis model | 11.4 percent | nine clips shipped before it was caught |
| Depth on one frame | load 1.9s, inference 0.4s | local GPU |
| Depth peak memory, 3216 frames at full res | 13.4 GB resident, 16.6 GB swapped | the ceiling |
| Depth memory, 4230 frames at half res | 3.3 GB peak, 0 swap, 458s | the documented fix, applied |
| Quilt build | 77 views in 0.8s at 3360px | n=1 |
| Comparison run cost | 205 credits | balance measured before and after |

**What I cannot tell you:** any dollar figure, because no credit-to-currency rate was recorded at measurement time. Time saved, because no manual baseline was ever measured. Both are in [`docs/NOT-MEASURED.md`](docs/NOT-MEASURED.md) with what it would take to get them honestly.

**Honest scope:** one operator, one machine, one panel, one labeller. The labels are internally consistent and externally unvalidated, and a second labeller is the single most valuable thing this repository is missing.

---

<p align="center">
  <img src="assets/band-cost.svg" alt="The cost: measured per engine, never extrapolated" width="100%">
</p>

## Cost

<p align="center">
  <img src="assets/cost.svg" alt="Measured render cost in credits against clip length: the flat tier stays at 1 credit while the premium tiers scale to 58, with the unmeasured span left empty" width="100%">
</p>

The scheduled pipeline renders on the **flat tier**: 1 credit, now measured at three lengths. The premium tiers scale hard, so the multiple on a 3-minute clip is 58x, not 5x.

| engine tier | ~11s | ~126s | ~169s | shape |
|---|---|---|---|---|
| flat tier (scheduled default) | 1 credit | 1 credit | 1 credit | flat with length, three measured points |
| premium tiers | 5 credits | 43 credits | **58 credits** | scales, and not knowably linear |

Every cell there is a balance delta read before and after a real render. None is interpolated. The 169-second column was null until this run measured it, and it was then measured a second time on an independent pair of renders: 58 credits each, both times.

The router refuses to interpolate between measured points, because an earlier confident estimate understated a premium batch by 8.6x and burned 344 credits before anyone noticed. A null makes a caller ask; a confident 5 makes it spend 43.

The discipline paid out again here. Before the two premium renders that produced this page's clip, the estimate published in advance was "plausibly 58 each, and the scaling law is unmeasured." The balance moved by 116 across the two, so 58 each exactly. The estimate was right, and it was still published as an estimate with the reason it could be wrong, because a number that happens to land is not the same as a number that was known.

**The full comparison run on this page cost 205 credits**, measured as a balance delta across the session: the same script rendered on three engine tiers, across three looks and several voice clones, in order to pick one of each by eye and ear. That is emphatically not the scheduled cost. The daily path renders once, on the flat tier, for 1 credit. Full model, the incident, and tier-sizing for both vendors: [`docs/COST.md`](docs/COST.md).

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

<p align="center">
  <img src="assets/band-run.svg" alt="Running it: what it takes to reproduce this" width="100%">
</p>

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

## Roadmap

**An interactive version of this page, deployed.** Everything here is a still or a loop, because a README can only hold those. The pipeline it documents is interactive at several points that a picture cannot reach, and those are the parts worth clicking:

- **The presenter, live.** The real-time arm of the fork, the one none of these gates apply to, is a conversational avatar rather than a rendered file. On a page you could talk to her instead of watching a clip of her.
- **The voice, as a control rather than a recording.** Type a line, hear it in the cloned voice, and watch the three drawn takes and the median that gets kept. The 6 to 37 percent duration spread is the sort of thing you believe once you have made it happen yourself.
- **The register-shaping agent.** The second of the two script agents, the one trained on years of my own prompts. Currently a companion repo, available on request; a hosted version would let you feed it a flat sentence and see what it does to the cadence.
- **The gates, run against your own input.** Upload a still, watch the separation probe measure the torso against the fill, and get refused if you wore black.

Hosting is the easy part: the diagram already runs as a self-contained page, and the interactive pieces want a real runtime, so Vercel is the likely target rather than static Pages.

None of this is built. It is listed here because the parts it would be built from are, and because the honest version of a roadmap names what does not exist yet.

---

Built by James Niu. Licensed [GPL-3.0](LICENSE).
