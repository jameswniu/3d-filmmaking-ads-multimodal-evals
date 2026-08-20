# The pipeline, stage by stage

The ten stages in order, and the fork that separates the ones the evals can score from the ones they cannot. Summarised on the [README](../README.md#the-ten-stages).

## Before the fork

Ten stages, and each one reads at three depths: the paragraph is the decision anyone building this has to make, the indented line is what I chose and the measurement that forced it, and the bullets are the literal mechanics. Skim the paragraphs for the argument, drop into the bullets when you want the file and the number. Every image below is from the single run at the top of this page, with one exception: the stage 0 and 1 panel carries the numbers of the latest scheduled run, because that is the part of the suite that keeps moving.

<p align="center">
  <img src="assets/stage-wake-script.svg" alt="Stage 0, the scheduled wake, beside stage 1, the script" width="100%">
</p>

https://github.com/user-attachments/assets/315f8bb9-3936-42ac-a787-9ec0cda10f51

<p align="center"><sub><b>Press play: the actual soundtrack.</b> 169 seconds of the cloned voice, the kept median take, under its own waveform. The raw audio also lives in the repo: <a href="assets/voice-narration.m4a">voice-narration.m4a</a>.</sub></p>

### 0. Wake

Supervised or unattended? Everything downstream follows from this one answer. A supervised pipeline can be corrected mid-flight and needs no gates at all; an unattended one cannot be corrected, so it needs every gate in this repository.

> Unattended, on a timer, because the interesting failures only appear when nobody is watching. Each run is a headless agent under a spend budget and a wall-clock timeout.

- A scheduled job fires the run, a lock keeps two runs from racing, a budget guard caps spend, a timeout kills a wedged leg.
- The alert test is inverted on purpose: it fires on anything other than a clean success, rather than on a list of known failures. An enumerated list can only catch what you already thought of, so a novel failure would have been silent. This way it is loud on day one.

### 1. Script

Whose words, and whose register? Generic ad copy is safe and forgettable; real material is specific and risky. Those are two separable problems, and conflating them is why most generated avatars sound like a press release read aloud.

> So they are split across two agents. One assembles **what** to say, out of my actual working notes and roadmaps, which is the difference between a avatar reading marketing and a avatar saying something. A second agent, trained on years of my own prompts, then shapes **how** it sounds: the register, the cadence, the places a real person would hedge or land hard. It rewrites for voice, not for content. Keeping them apart also keeps the thing writing the copy from being the thing that spends the render budget.

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
- Wardrobe has to clear the matte, and nothing was checking that. The first pass put a black top on a avatar whose background is matted to pure black: her face cleared the fill by 134 levels of luma and her torso cleared it by **22**, so the body dissolved and left a floating head. Re-shot in cream, the torso now measures **171**. The lesson is the shape of the miss, not the fix: eleven probes scored her face, her motion and her timing, and not one of them asked whether you could see her.

### 4. Render

Text-to-video or audio-driven avatar? General video models are spectacular and unpredictable frame to frame; an audio-driven avatar is narrow, repeatable, and cheap enough to run every day. Advertising needs the same avatar to be identical on Tuesday and Thursday, so repeatability beats spectacle here.

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

Everything up to here is shared: the schedule, the words, the cloned voice, the pinned face, the animated render. At this point the same avatar becomes two different products, and they are not variations on a theme. They are separated by whether the output exists before anyone sees it.

> **Rendered** output is finished before it ships, so every gate in this repository can run in the gap between "the file exists" and "a human sees it." That gap is the entire reason this pipeline can be trusted unattended. **Live** output has no such gap: the voice is synthesized in the moment, mid-conversation, and there is no frame to inspect before it is already on someone's screen. So the gating doctrine here does not port across the fork. It is not that the live path needs different thresholds. It is that pre-spend review, the mechanism all nine invariants rest on, does not exist there at all.

**The rendered path, stages 5 through 9 below.** Matte, evaluate, infer depth, build the 77-view quilt, cast to glass. Fully built, runs on a timer, and is what the rest of this page documents. Latency is irrelevant, which is exactly what buys room for thirteen probes and four guards, three of which fail open.

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
- Choosing black is what created the wardrobe trap in stage 3. A fill of zero is the strongest possible separation for a lit face and the weakest possible separation for dark clothing, and those are the same decision. Deciding the background also decides what the avatar is allowed to wear, which nothing in the suite knew until it was measured.

### 6. Evals

Gate on the outcome or on the attempt? Outcome metrics are what dashboards show, and they cannot tell a system that complied apart from a system that was stopped. Measured at the outcome, one constraint here held 14 runs out of 15. Measured at the first attempt, the same constraint held 6 out of 15. Both numbers are true, and only the second one tells you the rule was being ignored and then caught.

> Nine invariants, thirteen probes, every named gating threshold derived from a labelled pass and fail exemplar, judging done blind, and a hard wall between metrics that **gate** and metrics that only **report**. A metric has to be stable *within* a single clip before it earns any authority over spend, because agreement with a small labelled set is cheap and noise reproduces it easily.

- Probes run against the rendered clip and its subtitle track. The ship gate refuses outright on geometry failures, and for judgement calls it cannot make itself it demands an explicit written reason rather than a boolean.
- The derivations that exist, including the ten scoring models that died in a single day, is in [`docs/EVALS.md`](docs/EVALS.md).
- The gates are ranked by what happens when they are violated, not by how important they feel. Nothing here is allowed to be a check in name only: four guards were deliberately broken to find out, and three of them approved everything when a single config file went missing while still reporting green.

### 7. Depth

Capture depth or infer it? Capture wants a depth camera pointed at a real subject, and neither exists here, because the subject was generated. Inference works on any frame including a synthetic one, which makes it the only option that composes with a generated avatar at all.

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

