

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

| Who it is for | The difference |
|:---|:---|
| An ad team that cannot watch every render, because it runs on a schedule against metered APIs. [What changes for them](#an-ad-team-before-and-after) | The render path is not the hard part. Ten scoring models were built and killed in one day for disagreeing with the labels. [The five hard problems](#the-five-hard-problems-in-talking-head-video) |
| **The flow** | **The benchmark** |
| `label` then `derive` then `gate` then `render` then `relabel`. Nothing renders that the gates have not cleared | 16 of 16 named thresholds bracketed by labelled exemplars. [10 of 10 scheduled days, 0 missed](#what-holds-when-nobody-is-watching) |

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
      <sub><b>Six of the 77 views, one instant.</b> Spread across the whole sweep rather than neighbours, because adjacent views differ by <b>0.25 px</b> and a block of them reads as one photo repeated. These are warped at the full square framing rather than cropped out of the quilt, so they sit at the same scale as the clips beside them; the panel's own tiles trim top and bottom to a 1.57 aspect. Every frame of the clip carries its own 77. <b><a href="assets/quilt-video.mp4">&#9654; full quilt video</a></b></sub>
    </td>
    <td width="33%" align="center" valign="top">
      <br><br>
      <img src="assets/hologram-full.gif" alt="The avatar explaining the 77-view quilt while the simulated view sweeps, subtitles held still" width="100%"><br>
      <sub><b>And she explains her own pipeline, in the final treatment.</b> The full narration under the simulated view sweep the first cell demonstrates, one pass, start to finish. This loop is her describing the very grid the middle cell shows: one moment, seventy-seven positions. GIFs are mute and the voice is half the point: <b><a href="assets/hologram-full.mp4">&#9654; watch with sound (2:49)</a></b></sub>
    </td>
  </tr>
</table>

> The avatar is generated. She is not a real person and not a likeness of one. Her voice is a clone of a consented source. The three clips above and the frame study below come from **one** run of the pipeline, deliberately, because a montage of lucky takes would hide the thing this repo is about. The twelve short spots further down are twelve governed runs, one render each, and every one of them is scored on the same page.

---

## The same five spots, three engines (shoot-20260824)

The five product spots above were reshot scene for scene on three text-to-video engines, with the narrations, the avatar closers, and the brand cards reused unchanged so the only variable is the engine. Every scene prompt carries the same realism guard paragraph, each brand now has its own score, and the one scene an engine refused on content policy was rewritten softer and rerun rather than dropped. Forty six scenes landed across the three legs for about fifteen dollars of metered spend.


<table>
  <tr>
    <td width="20%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-orchard.gif" alt="Orchard Hill Coffee, reshot, best engine take" width="100%"><br><sub><b>Orchard Hill Coffee.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-orchard.mp4">&#9654; with sound</a> <br>Omni Flash</sub></td>
    <td width="20%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-lantern.gif" alt="Lantern Street, reshot, best engine take" width="100%"><br><sub><b>Lantern Street.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-lantern.mp4">&#9654; with sound</a> <br>Wan 3.0</sub></td>
    <td width="20%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-harbor.gif" alt="Harbor Lane Realty, reshot, best engine take" width="100%"><br><sub><b>Harbor Lane Realty.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-harbor.mp4">&#9654; with sound</a> <br>Seedance 2.0</sub></td>
    <td width="20%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-quiet.gif" alt="Quiet Hours, reshot, best engine take" width="100%"><br><sub><b>Quiet Hours.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-quiet.mp4">&#9654; with sound</a> <br>Wan 3.0</sub></td>
    <td width="20%" align="center" valign="top"><img src="https://raw.githubusercontent.com/jameswniu/3d-filmmaking-ads-multimodal-evals/archive-media/shoot-20260824-slowroad.gif" alt="Slow Road Travel, reshot, best engine take" width="100%"><br><sub><b>Slow Road Travel.</b> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-slowroad.mp4">&#9654; with sound</a> <br>Omni Flash</sub></td>
  </tr>
</table>

Every engine take of every spot:

| Spot | Engines |
|---|---|
| **Orchard Hill Coffee** | <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-orchard.mp4">&#9654; Omni Flash</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-orchard.mp4">&#9654; Wan 3.0</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-orchard.mp4">&#9654; Seedance 2.0</a> |
| **Lantern Street** | <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-lantern.mp4">&#9654; Omni Flash</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-lantern.mp4">&#9654; Wan 3.0</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-lantern.mp4">&#9654; Seedance 2.0</a> |
| **Harbor Lane Realty** | <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-harbor.mp4">&#9654; Omni Flash</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-harbor.mp4">&#9654; Wan 3.0</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-harbor.mp4">&#9654; Seedance 2.0</a> |
| **Quiet Hours** | <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-quiet.mp4">&#9654; Omni Flash</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-quiet.mp4">&#9654; Wan 3.0</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-quiet.mp4">&#9654; Seedance 2.0</a> |
| **Slow Road Travel** | <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-omni-slowroad.mp4">&#9654; Omni Flash</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-wan3-slowroad.mp4">&#9654; Wan 3.0</a> <a href="https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/raw/archive-media/shoot-20260824-seedance2-slowroad.mp4">&#9654; Seedance 2.0</a> |

The full pipeline, the evals, and the previous shoots live on [main](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals) and [shoot-20260822](https://github.com/jameswniu/3d-filmmaking-ads-multimodal-evals/tree/shoot-20260822).
