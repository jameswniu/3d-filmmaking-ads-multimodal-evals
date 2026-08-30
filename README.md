

<p align="center">
  <img src="assets/hero.svg" alt="3d-filmmaking-ads-multimodal-evals: evals govern a cloned voice, a generated character, and a light-field render" width="100%">
</p>

<p align="center">
  <img alt="labelled: 113 stills, 67 clips" src="https://img.shields.io/badge/labelled-113_stills_%C2%B7_67_clips-0ea5e9?style=flat-square&labelColor=0f172a">
  <img alt="probes: 13, and 16 of 16 named gating thresholds derived from labelled exemplars" src="https://img.shields.io/badge/probes-13_%C2%B7_16%2F16_derived-164e63?style=flat-square&labelColor=0f172a">
  <img alt="gates: 4, three of which fail open" src="https://img.shields.io/badge/gates-4_%C2%B7_3_fail_open-164e63?style=flat-square&labelColor=0f172a">
  <img alt="views: 77 per frame" src="https://img.shields.io/badge/views-77_per_frame-164e63?style=flat-square&labelColor=0f172a">
  <img alt="cost: 1 credit per render" src="https://img.shields.io/badge/cost-1_credit_%2F_render-164e63?style=flat-square&labelColor=0f172a">
  <img alt="license: GPL-3.0" src="https://img.shields.io/badge/license-GPL--3.0-164e63?style=flat-square&labelColor=0f172a">
</p>

**An advertising-grade AI filmmaking pipeline where the evals are the product.**

| Who It Is For | The Difference |
|:---|:---|
| An ad team that cannot watch every render, because it runs on a schedule against metered APIs. [What changes for them](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals#an-ad-team-before-and-after) | The render path is not the hard part. Ten scoring models were built and killed in one day for disagreeing with the labels. [The five hard problems](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals#the-five-hard-problems-in-talking-head-video) |
| **The flow** | **The benchmark** |
| `label` then `derive` then `gate` then `render` then `relabel`. Nothing renders that the gates have not cleared | 16 of 16 named thresholds bracketed by labelled exemplars. [10 of 10 scheduled days, 0 missed](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals#what-holds-when-nobody-is-watching) |

**In plain words.** A computer writes a short ad script, speaks it in a cloned voice, and puts a generated person on camera to deliver it. Before it pays a vendor to render anything, it checks the work against examples a human graded by hand, and it refuses takes that do not measure up. It runs overnight, on a schedule, with nobody watching.

Three words repeat on this page, and they are one idea:

- a **probe** is a check
- a **threshold** is the line that check has to clear
- a **gate** is what stops the job when the line is not cleared

The hard part is not making the video. It is deciding, without a person in the room, whether the video is good enough to pay for. That decision is what this repository is.

<table>
  <tr>
    <td width="34%" align="center" valign="top">
      <img src="assets/parallax-amplified.gif" alt="The avatar under a swaying virtual camera, nearer pixels travelling further than far ones, amplified four times" width="100%"><br>
      <sub><b>Depth, on a flat screen.</b> A virtual camera sways across the inferred depth map, near pixels travelling further than far ones. <b>This clip is exaggerated 4x and says so on the frame.</b> The real sweep across all 77 views moves her <b>19 px</b> inside a 480 px tile, about 4 percent, which is honest and nearly invisible at this size. The amber tick is fixed, because without something stationary the eye tracks her and cancels the very displacement the clip exists to show.</sub>
    </td>
    <td width="33%" align="center" valign="top">
      <br>
      <img src="assets/views-sweep.gif" alt="Six of the 77 camera views of one instant, cycled" width="100%"><br>
      <sub><b>Six of the 77 views, one instant.</b> Spread across the whole sweep rather than neighbours, because adjacent views differ by <b>0.25 px</b> and a block of them reads as one photo repeated. These are warped at the full square framing rather than cropped out of the quilt, so they sit at the same scale as the clips beside them; the panel's own tiles trim top and bottom to a 1.57 aspect. Every frame of the clip carries its own 77. <b><a href="assets/quilt-video.mp4?raw=true">&#9654; full quilt video</a></b></sub>
    </td>
    <td width="33%" align="center" valign="top">
      <br><br>
      <img src="assets/hologram-full.gif" alt="The avatar explaining the 77-view quilt while the simulated view sweeps, subtitles held still" width="100%"><br>
      <sub><b>And she explains her own pipeline, in the final treatment.</b> The full narration under the simulated view sweep the first cell demonstrates, one pass, start to finish. This loop is her describing the very grid the middle cell shows: one moment, seventy-seven positions. GIFs are mute and the voice is half the point: <b><a href="assets/hologram-full.mp4?raw=true">&#9654; watch with sound (2:49)</a></b></sub>
    </td>
  </tr>
</table>

> The avatar is generated. She is not a real person and not a likeness of one. Her voice is a clone of a consented source. The three clips above and the frame study below come from **one** run of the pipeline, deliberately, because a montage of lucky takes would hide the thing this repo is about. The five spots further down ran four ways each, twenty governed versions; the redo above them adds eight more from the same discipline, and every one of them is scored on this page.

---


## How this ran, and what it is actually showing

This branch is loop engineering applied to multi-modal AI generation, with the human on the loop, not in the loop. It is not a demo of multi-vendor ad generation; it is the repo's eval discipline running an entire ad production, end to end, with nobody driving. Ads are the first track because their feedback loops are shortest; documentary is next, and the light-field work on main is the third display target the same gated pipeline already feeds. The author wrote no scripts for this shoot. He supplied the architecture and the framework, the four-phase ad grammar held conceptually rather than literally, a realism guard paragraph, a rule that the most arresting beat opens the film, a rule that every human on screen is the same presenter, and the agent loop-engineered the rest, boards, prompts, engine calls, quality gates, re-rolls, remasters and delivery, with every request and landing in an append-only ledger.

The workflow is the industry's own systematic testing loop, run by an agent instead of a team.

| Phase | The Industry Step | What Ran Here |
|---|---|---|
| 01 | Hypothesis | The four-phase grammar and the hook-first rule, held as creative invariants |
| 02 | Ad variations | Five brands, four versions each, one variable moved per cell, the engine |
| 03 | Tests | Probes and judges gate every render before money moves, verdicts ledgered, defects withdrawn and re-rolled |
| 04 | Winners and iterate | The picked takes lead each row, the baseline's report card sits below, the next shoot inherits every ruling |

The measurements came from research, not taste. The offline gates on this page derive from labelled human verdicts, and the online success metrics the boards carry, hook rate, hold rate, view-through, come from a pairwise research pass over the ad industry's own testing literature. The evals were designed and calibrated before a single render was paid for.


## The conclusion, first

What this page adds up to is a multi-model router built on autonomously feature-engineered evals, evals tailored to the user rather than to the model. No engine sweeps the catalogue. Wan 3.0 takes the two spots that turn on legible story text and composed calm, Seedance 2.0 takes the two that turn on clean eyes and a steady face, and the sleep brand routes to the premium HeyGen baseline, which wins every calm row on its panel. The router has no cheapness bias, it pays up when the audience calls for it. Omni Flash wins no panel and keeps its seat anyway, native ambient audio and the freest human motion, and a served user may respond to exactly that, which is why the pool stays four deep. The presenter's closers stay vendor-rendered inside every version because the baseline still owns identity. And the comparison is a fair race by construction: the three challenger engines sit in one price class, about sixty cents to a dollar a scene, so no column wins by outspending another, and a four-deep pool per spot costs a few dollars, which is what lets an ad platform serve each user the version that user responds to.

| Version | Engine | What the Scenes Cost |
|---|---|---|
| A0 | HeyGen video agent, the baseline | 116 vendor credits for its sixteen scenes and seven closers, read off the balance |
| B1 | Omni Flash | About sixty cents a scene, nine dollars for its fifteen |
| B2 and B3 | Wan 3.0 and Seedance 2.0 | About thirty-two dollars together for their thirty scenes, roughly a dollar a scene |

### The question this page expects

Why not put all of this in the prompt instead, and skip the judging. It is in the prompt, every engine got the same brief with the audience written into it, and the four columns under each spot are what four models did with identical words. A prompt is a request, and a generation is a draw against it: the Wan take was told to put the system banner on the phone's own screen and floated it in mid-air anyway, until a re-roll landed it. Judging after is also the only way to choose between models, because a prompt steers one engine but cannot tell you which engine to buy for this audience. So the loop holds both ends. The prompts know the user going in, the panel checks the feeling actually landed coming out, and the next dollar routes on the count. A router with gates.

## Five real products, to prove the grammar is not brand-specific

The spots above and below sell invented brands, which is the easy case: the story can bend to whatever the
pipeline renders well. So the same pipeline ran again against five real, currently shipping AI products,
with their positioning pulled from their own live pages and checked by a second engine under an adversarial
default-refute mandate before a single scene was boarded. Nothing here bends to the render. The claim each
spot closes on is the claim the company actually makes.

**These are spec ads.** They are not affiliated with, endorsed by, or produced for Google, OpenAI,
Perplexity or Meta, none of these companies has seen them, and every tagline on every end card is written
here rather than lifted from the brand. They exist to show that the loop can take a real product's real
positioning and build the ad around it.

All five shot on Omni Flash at about sixty-three cents a scene, fifteen scenes with zero content
rejections, each one gated on caption timing, closer alignment and lip sync before it was allowed out.

### Gemini

<table>
  <tr>
    <td width="42%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260827-cell-gemini.gif" alt="Gemini spec ad" width="100%"><br><sub><a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260827-gemini.mp4">&#9654; with sound</a></sub></td>
    <td width="58%" valign="top"><sub>A kitchen plastered floor to ceiling in sticky notes, and an avalanche of more when he opens a cupboard. Then every note in the room streams into his phone at once, and one stubborn one drifts down and lands on the fridge.<br><br><b>The promise it closes on:</b> Google's personal assistant, hands free, across the apps you already use.<br><br>Positioning verified against the company's own current pages in a pairwise research pass with an adversarial second engine; the tagline on the card is ours.</sub></td>
  </tr>
</table>

### ChatGPT

<table>
  <tr>
    <td width="42%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260827-cell-chatgpt.gif" alt="ChatGPT spec ad" width="100%"><br><sub><a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260827-chatgpt.mp4">&#9654; with sound</a></sub></td>
    <td width="58%" valign="top"><sub>He has been deciding between two identical jars long enough that a cobweb has grown between his elbow and the shelf and dust has settled on his shoulders. One tap, the web snaps, and a strand floats up like a surrender flag.<br><br><b>The promise it closes on:</b> Help with everyday questions and ideas.<br><br>Positioning verified against the company's own current pages in a pairwise research pass with an adversarial second engine; the tagline on the card is ours.</sub></td>
  </tr>
</table>

### Perplexity

<table>
  <tr>
    <td width="42%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260827-cell-perplexity.gif" alt="Perplexity spec ad" width="100%"><br><sub><a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260827-perplexity.mp4">&#9654; with sound</a></sub></td>
    <td width="58%" valign="top"><sub>Her laptop erupts four hundred pages to the ceiling and buries her to the chest. The blizzard reverses and folds itself into a single page in her open palm, one last sheet settling upside down on top.<br><br><b>The promise it closes on:</b> An answer engine that hands back the answer with its sources attached.<br><br>Positioning verified against the company's own current pages in a pairwise research pass with an adversarial second engine; the tagline on the card is ours.</sub></td>
  </tr>
</table>

### Meta AI

<table>
  <tr>
    <td width="42%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260827-cell-metaai.gif" alt="Meta AI spec ad" width="100%"><br><sub><a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260827-metaai.mp4">&#9654; with sound</a></sub></td>
    <td width="58%" valign="top"><sub>Her paper to-do list has unrolled out the front door, down the porch and three houses along the pavement. She puts on the glasses and the whole scroll rolls back up so fast it knocks a plant pot off the rail, which she catches without looking.<br><br><b>The promise it closes on:</b> A personal agent that works on your behalf.<br><br>Positioning verified against the company's own current pages in a pairwise research pass with an adversarial second engine; the tagline on the card is ours.</sub></td>
  </tr>
</table>

### Google Pics

<table>
  <tr>
    <td width="42%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260827-cell-pics.gif" alt="Google Pics spec ad" width="100%"><br><sub><a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260827-pics.mp4">&#9654; with sound</a></sub></td>
    <td width="58%" valign="top"><sub>He holds a printed photograph whose furniture is moving on its own, a sofa sliding out of the frame, a lamp walking in, while the real room behind him stays perfectly still. Far away in the picture, a tiny sofa wanders off down a street.<br><br><b>The promise it closes on:</b> Image creation and editing that brings your exact vision to life, down to a single object.<br><br>Positioning verified against the company's own current pages in a pairwise research pass with an adversarial second engine; the tagline on the card is ours.</sub></td>
  </tr>
</table>

Every one of the five carries the same structure, which the [capture-attention law](#the-question-this-page-expects)
makes explicit: open on something absurd and unexplained in a photoreal world, make it worse in the middle
beat with the product still absent, and let the product be the only thing that closes the puzzle. The
board itself is gated on that before any money is spent, and the gate has already sent boards back.

## The redo, absurd first, and the four-engine router

The five spots further down were the like-for-like reshoot. These four are what happened when the curator kept rejecting. A literal, message-first cut tested worse, and the grammar that survived is the one he named: open ABSURD at three or four times the volume, hand them the coherent model by the second line, and keep every quirk visual with nobody narrating it. The mailbox erupts like a geyser and the whole block turns. The three a.m. descent is a full charge. A whole street waves back. A luggage tag tears free and flies the spot like a small bird, and lands when she does.

His eye then caught the lip-sync, and the complaint became instruments. A caption gate now checks that every burned subtitle says what is being spoken, when it is spoken. A face-located mouth probe, calibrated on controls with the audio shifted 0.4 seconds each way, reads each closer's lip lag, and the builder trims or pads that closer by its own measured number, so the delivered lag reads zero. The probe's first deployment had its sign inverted and doubled the error; the gate caught it before anything shipped, which is this repository's whole argument in one sentence.

Each spot ships in two versions: its winning engine from the reshoot below, and an Omni Flash leg from the same boards, narrations, closers, beds and captions, so every row is pure engine. Bold is the best reading in its row, and the WINNER takes the most rows.

### Orchard Hill Coffee, redone

<table>
  <tr>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-seedance2-orchard.gif" alt="Seedance 2.0" width="100%"><br><sub><b>Seedance 2.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-seedance2-orchard.mp4">&#9654; with sound</a></sub></td>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-omni-orchard.gif" alt="Omni Flash" width="100%"><br><sub><b>Omni Flash, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-orchard.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

| Probe | Seedance 2.0 | **Omni Flash, the WINNER** |
|---|---|---|
| Gesture energy, higher is better | 0.595 | **0.716** |
| Background clutter, lower is better | 8.70 | **3.06** |
| Eye rejection, lower is better | **5.28** | 6.07 |
| Scene simplicity, lower is calmer | 7.27 | **6.95** |
| Face level wander, lower is steadier | **189** | 202 |

**Omni Flash takes three rows, the bigger gesture, a background nearly three times cleaner, and the calmer scene.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-orchard.mp4), with sound.

### Lantern Street, redone

<table>
  <tr>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-wan3-lantern.gif" alt="Wan 3.0" width="100%"><br><sub><b>Wan 3.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-wan3-lantern.mp4">&#9654; with sound</a></sub></td>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-omni-lantern.gif" alt="Omni Flash" width="100%"><br><sub><b>Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-lantern.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

| Probe | **Wan 3.0, the WINNER** | Omni Flash |
|---|---|---|
| Eye rejection, lower is better | **4.00** | 5.45 |
| Background clutter, lower is better | 4.88 | **3.25** |
| Scene simplicity, lower is calmer | **5.20** | 5.99 |
| Gesture energy, for this audience lower is calmer | **0.510** | 0.675 |
| Face level wander, lower is steadier | **97.4** | 145 |
| System banner legible on the phone, eye verdict | **Yes** | **Yes** |

**Wan 3.0 takes four rows, the cleaner eye read, the calmer scene, the stiller hands and the steadiest face.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-wan3-lantern.mp4), with sound.

### Harbor Lane Realty, redone

<table>
  <tr>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-wan3-harbor.gif" alt="Wan 3.0" width="100%"><br><sub><b>Wan 3.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-wan3-harbor.mp4">&#9654; with sound</a></sub></td>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-omni-harbor.gif" alt="Omni Flash" width="100%"><br><sub><b>Omni Flash, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-harbor.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

| Probe | Wan 3.0 | **Omni Flash, the WINNER** |
|---|---|---|
| Gesture energy, higher is better | **0.894** | 0.691 |
| Background richness, higher sells the staging | **11.5** | 6.55 |
| Eye rejection, lower is better | 6.42 | **5.94** |
| Face level wander, lower is steadier | 191 | **150** |
| Scene simplicity, lower is calmer | 8.75 | **7.24** |
| For Sale sign legible, eye verdict | **Yes** | **Yes** |

**Omni Flash takes three rows, the cleaner eye read, the steadier face and the simpler scene, against Wan's bigger wave and richer staging. Omni is also the engine that gave the whole street waving back.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-harbor.mp4), with sound.

### Slow Road Travel, redone

<table>
  <tr>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-seedance2-slowroad.gif" alt="Seedance 2.0" width="100%"><br><sub><b>Seedance 2.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-seedance2-slowroad.mp4">&#9654; with sound</a></sub></td>
    <td width="50%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260826-cell-omni-slowroad.gif" alt="Omni Flash" width="100%"><br><sub><b>Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-omni-slowroad.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

| Probe | **Seedance 2.0, the WINNER** | Omni Flash |
|---|---|---|
| Gesture energy, higher is better | **0.760** | 0.480 |
| Background busy-ness, higher feels like travel | 3.87 | **6.93** |
| Eye rejection, lower is better | **4.27** | 7.37 |
| Scene simplicity, lower is calmer | **6.75** | 7.64 |
| Face level wander, lower is steadier | **112** | 146 |

**Seedance 2.0 takes four rows, twice the gesture energy, the cleanest eye read, the calmer frame and the steadier face.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260826-seedance2-slowroad.mp4), with sound.

With four engines in the pool, the router's answer is Orchard to Omni Flash, Lantern to Wan 3.0, Harbor to Omni Flash, and Slow Road to Seedance 2.0. Omni pays its way on the spots where a clean frame beats the biggest gesture, at about sixty-three cents a scene with native ambient sound; Wan and Seedance keep the spots where calm and steadiness carry, at about a dollar a scene. Quiet Hours sits out the redo because its WINNER below is the premium baseline itself.

## The five spots, four ways each, probed

Every spot in all four versions, inline, each with its own panel: five instruments from the one battery, plus a story-text row where a legible prop carries the deciding beat. The panels are feature engineering pointed at the audience instead of the model. The loop picks each brand's instruments, and the direction of good, from the feeling that spot has to invoke in its target user; a coffee ad reads energy upward, a sleep ad flips the same instrument, calm sells. **Bold is the best reading in its row**, in that row's own direction, and the **WINNER is the version that takes the most rows**. When versions tie on rows, the row the panel gates on decides.

### Orchard Hill Coffee

<table>
  <tr>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-a0-orchard.gif" alt="Orchard Hill Coffee, HeyGen, the baseline" width="100%"><br><sub><b>A0 &middot; HeyGen, the baseline.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-orchard.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-omni-orchard.gif" alt="Orchard Hill Coffee, Omni Flash" width="100%"><br><sub><b>B1 &middot; Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-orchard.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-wan3-orchard.gif" alt="Orchard Hill Coffee, Wan 3.0" width="100%"><br><sub><b>B2 &middot; Wan 3.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-orchard.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-seedance2-orchard.gif" alt="Orchard Hill Coffee, Seedance 2.0" width="100%"><br><sub><b>B3 &middot; Seedance 2.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-orchard.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

The feeling this spot sells is morning energy and craving, so its panel gates gesture upward and lets the busy kitchen report.

| Probe | A0 HeyGen | B1 Omni Flash | B2 Wan 3.0 | **B3 Seedance 2.0, the WINNER** |
|---|---|---|---|---|
| Gesture energy, higher is better, gates | 0.468 | 0.609 | **0.787** | 0.664 |
| Background clutter, lower is better, bar 5.5 | 4.89 | **3.52** | 5.15 | 6.57 |
| Eye rejection, lower is better, reports | 9.86 | 8.68 | 12.79 | **7.69** |
| Scene simplicity, lower is calmer, reports | 7.37 | **6.7** | 8.10 | **6.7** |
| Face level wander, lower is steadier, reports | 148.9 | 150.6 | 150.3 | **114.5** |

**B3 Seedance 2.0 takes three rows, the cleanest eye read, the steadiest face, and a tie for calmest scene.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-orchard.mp4), about twenty seconds with sound.

### Lantern Street

<table>
  <tr>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-a0-lantern.gif" alt="Lantern Street, HeyGen, the baseline" width="100%"><br><sub><b>A0 &middot; HeyGen, the baseline.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-lantern.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-omni-lantern.gif" alt="Lantern Street, Omni Flash" width="100%"><br><sub><b>B1 &middot; Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-lantern.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-wan3-lantern.gif" alt="Lantern Street, Wan 3.0" width="100%"><br><sub><b>B2 &middot; Wan 3.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-lantern.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-seedance2-lantern.gif" alt="Lantern Street, Seedance 2.0" width="100%"><br><sub><b>B3 &middot; Seedance 2.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-lantern.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

The feeling is three-in-the-morning relief, dark calm and a legible screen, so this panel gates clutter down and reads gesture as calm.

| Probe | A0 HeyGen | B1 Omni Flash | **B2 Wan 3.0, the WINNER** | B3 Seedance 2.0 |
|---|---|---|---|---|
| Eye rejection, lower is better, gates at 4.5 | 5.58 | 6.46 | 4.01 | **3.56** |
| Background clutter, lower is better, gates at 5.5 | **2.75** | 4.08 | 3.95 | 6.5 |
| Scene simplicity, lower is calmer, gates | 4.63 | 4.4 | **4.24** | 4.38 |
| Gesture energy, for this audience lower is calmer | 0.433 | **0.411** | 0.547 | 0.514 |
| Face level wander, lower is steadier, reports | 148.6 | 156.3 | **119.7** | 128.9 |
| System banner legible on the phone, eye verdict | No | No | **Yes** | No |

**B2 Wan 3.0 takes three rows, calmest scene, steadiest face, and the only system banner legibly on the phone.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-lantern.mp4), about twenty seconds with sound.

### Harbor Lane Realty

<table>
  <tr>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-a0-harbor.gif" alt="Harbor Lane Realty, HeyGen, the baseline" width="100%"><br><sub><b>A0 &middot; HeyGen, the baseline.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-harbor.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-omni-harbor.gif" alt="Harbor Lane Realty, Omni Flash" width="100%"><br><sub><b>B1 &middot; Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-harbor.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-wan3-harbor.gif" alt="Harbor Lane Realty, Wan 3.0" width="100%"><br><sub><b>B2 &middot; Wan 3.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-harbor.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-seedance2-harbor.gif" alt="Harbor Lane Realty, Seedance 2.0" width="100%"><br><sub><b>B3 &middot; Seedance 2.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-harbor.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

The feeling is neighborhood trust and warmth, so this panel reads richness upward and gates gesture, the wave is the product.

| Probe | A0 HeyGen | B1 Omni Flash | **B2 Wan 3.0, the WINNER** | B3 Seedance 2.0 |
|---|---|---|---|---|
| Gesture energy, higher is better, gates | 0.71 | 0.694 | **0.729** | 0.523 |
| Background richness, higher sells the staging | 3.65 | 6.6 | **10.5** | 6.4 |
| Eye rejection, lower is better, reports | 11.5 | **5.95** | 9.05 | 7.05 |
| Face level wander, lower is steadier, reports | 250 | 143.7 | 189.6 | **135.6** |
| Scene simplicity, lower is calmer, reports | 7.76 | **6.36** | 7.61 | 6.58 |
| For Sale sign legible, eye verdict | **Yes** | No | No | **Yes** |

**Three versions tie at two rows, so the gated row decides. B2 Wan 3.0 has the biggest wave and the richest staging.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-harbor.mp4), about twenty seconds with sound.

### Quiet Hours

<table>
  <tr>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-a0-quiet.gif" alt="Quiet Hours, HeyGen, the baseline" width="100%"><br><sub><b>A0 &middot; HeyGen, the baseline and the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-quiet.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-omni-quiet.gif" alt="Quiet Hours, Omni Flash" width="100%"><br><sub><b>B1 &middot; Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-quiet.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-wan3-quiet.gif" alt="Quiet Hours, Wan 3.0" width="100%"><br><sub><b>B2 &middot; Wan 3.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-quiet.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-seedance2-quiet.gif" alt="Quiet Hours, Seedance 2.0" width="100%"><br><sub><b>B3 &middot; Seedance 2.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-quiet.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

The feeling is permission to rest, so this panel flips gesture, calm is better here, and the sleep score gets its own row.

| Probe | **A0 HeyGen, the WINNER** | B1 Omni Flash | B2 Wan 3.0 | B3 Seedance 2.0 |
|---|---|---|---|---|
| Gesture energy, for this audience lower is calmer | **0.463** | 0.804 | 0.628 | 0.544 |
| Scene simplicity, lower is calmer, gates | **4.18** | 4.78 | 5.54 | 4.51 |
| Background clutter, lower is better, bar 5.5 | **1.3** | 4.64 | 6.76 | 5.43 |
| Eye rejection, lower is better, reports | **4.46** | 6.69 | 7.09 | 6.16 |
| Face level wander, lower is steadier, reports | 122.8 | **75.5** | 96.9 | 81.2 |
| Sleep score legible on the phone, eye verdict | No | No | **Yes** | No |

**A0 HeyGen sweeps the four calm rows, and calm is the product. This is the spot where the router pays for the premium engine.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-quiet.mp4), about twenty seconds with sound.

### Slow Road Travel

<table>
  <tr>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-a0-slowroad.gif" alt="Slow Road Travel, HeyGen, the baseline" width="100%"><br><sub><b>A0 &middot; HeyGen, the baseline.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-a0-slowroad.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-omni-slowroad.gif" alt="Slow Road Travel, Omni Flash" width="100%"><br><sub><b>B1 &middot; Omni Flash.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-slowroad.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-wan3-slowroad.gif" alt="Slow Road Travel, Wan 3.0" width="100%"><br><sub><b>B2 &middot; Wan 3.0.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-slowroad.mp4">&#9654; with sound</a></sub></td>
    <td width="25%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-cell-seedance2-slowroad.gif" alt="Slow Road Travel, Seedance 2.0" width="100%"><br><sub><b>B3 &middot; Seedance 2.0, the WINNER.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-slowroad.mp4">&#9654; with sound</a></sub></td>
  </tr>
</table>

The feeling is wanderlust, motion and place, so this panel gates gesture upward and reads busy frames as travel.

| Probe | A0 HeyGen | B1 Omni Flash | B2 Wan 3.0 | **B3 Seedance 2.0, the WINNER** |
|---|---|---|---|---|
| Gesture energy, higher is better, gates | 0.681 | 0.847 | **0.918** | 0.712 |
| Background busy-ness, higher feels like travel | 8.54 | 6.07 | **12.28** | 7.07 |
| Eye rejection, lower is better, reports | 7.37 | 6.55 | 8.79 | **5.91** |
| Scene simplicity, lower is calmer, reports | 7.4 | 6.81 | 7.94 | **6.25** |
| Face level wander, lower is steadier, reports | 130.6 | 94.7 | 127.3 | **79.5** |

**B3 Seedance 2.0 takes three rows, the cleanest eye read, the calmest frame and the steadiest face, against B2's bigger motion.** [&#9654; Watch the WINNER](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-slowroad.mp4), about twenty seconds with sound.

The pipeline and the evals that gate every render live on [main](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals).

### Scored, failures first

| Clip | Flags | Sync Lag (Ms) | Lipsync | Level Face / Scene / Relation | Eye BG (Max 4.5) | Scene (Target 7.5) | BG Detail (Max 5.5) | Hand Ratio |
|---|---|---|---|---|---|---|---|---|
| ad2-harbor-elena | 5 | **240 late** | **FAIL** | **249.5 / 190.3 / 35.8** | **11.32** | **8.08** | 3.21 | 0.739 |
| take-loop | 4 | **240 late** | **FAIL** | **7.1 / 4.9 / 22.1** | **4.79** | 5.30 | 4.27 | 0.248 |
| take-prison | 4 | **160 late** | **FAIL** | **7.8 / 5.2 / 21.5** | **5.00** | 5.52 | 4.27 | 0.246 |
| ad2-harbor-daniel | 4 | -240 early | **FAIL** | **250.0 / 190.2 / 42.6** | **11.32** | **8.18** | 3.21 | 0.709 |
| ad2-harbor-maya | 4 | -240 early | **FAIL** | **250.0 / 190.2 / 42.1** | **11.32** | **8.09** | 3.21 | 0.713 |
| ad2-orchard | 4 | -240 early | **FAIL** | **148.7 / 107.7 / 111.0** | **9.53** | **7.67** | 4.52 | 0.471 |
| ad2-slowroad | 4 | -160 early | **FAIL** | **136.2 / 139.7 / 116.6** | **7.07** | 6.98 | **8.36** | 0.686 |
| take-plausible | 3 | -40 early | **FAIL** | **8.6 / 4.8 / 17.3** | **4.76** | 5.49 | 4.40 | 0.238 |
| film-image | 3 | -240 early | PASS | **170.4 / 167.9 / 130.8** | **5.73** | 7.06 | **7.11** | 0.674 |
| ad2-lantern | 3 | -240 early | **FAIL** | **150.1 / 94.4 / 66.5** | **5.29** | 4.18 | 2.30 | 0.437 |
| take-copy | 2 | 0 on time | **REVIEW** | **8.2 / 5.0 / 17.0** | **4.82** | 5.38 | 4.27 | 0.248 |
| take-image | 2 | -240 early | **FAIL** | **8.5 / 4.4 / 17.0** | 4.32 | 5.49 | 4.26 | 0.238 |
| ad2-quiet | 2 | -240 early | **FAIL** | **123.0 / 147.1 / 149.8** | 4.16 | 3.68 | 0.86 | 0.465 |

The readings come from the same probes that score the hero render higher on this page, run on the masters before the web encode. A value in bold is a reading the probe itself flagged. Separation is not shown because these clips are unmatted, so there is no fill to measure against, and the spasm ratios are disclosures rather than verdicts and stay in the probe log. The remade spots score the way montages score: the level probe reads every hard cut as luminance wander, and the lip-sync probe watches crowd scenes where nobody on camera is the narrator, so its verdict fails even where her own closer is in time. The brokerage variants are three rows because they are three renders, and their third scene runs at 1.26x slow motion because the line outran the footage, which is the kind of call an edit makes and a probe then bills it for. The one re-roll of the batch was the software spot's third scene, regenerated for a clearer product beat after the first take came back as a close-up of the cat. This table is the page's floor, the original shoot's report card that every version above is measured against.
