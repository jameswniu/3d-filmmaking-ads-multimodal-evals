# Build your own: voice, character, pins

The pipeline in this repo runs on two vendor accounts and a pair of pinned identities: one cloned voice, one generated character. This is the order that works, with the measured reasons behind each step. Tier recommendations are in [COST.md](COST.md).

**The consent line, first.** Clone only your own voice, or a voice whose owner gave you written consent; both vendors require this and it is the right floor regardless. The character should be generated, not a likeness of a real person. This repo's character is synthetic by design, and the identity guards exist to keep even the synthetic identity pinned and un-substitutable.

---

## 1. Clone the voice (ElevenLabs)

1. Buy the smallest plan that includes instant voice cloning (the free tier does not; see [COST.md](COST.md) for the sizing math).
2. Record 1 to 3 minutes of clean speech: one quiet room, one mic, no music, natural pace. Consistency of the sample beats quantity; the clone inherits the room you give it.
3. Create the instant clone and note its `voice_id`. That id is now a secret in the practical sense: anyone holding it plus your API key can speak in your voice.
4. Synthesize with `eleven_v3` and keep scripts **above ~250 characters**. Measured 2026-07-26: shorter scripts read about 110 Hz brighter and less consistently than the calibrated voice. Padding a short script is quality control, not waste.
5. **Pin the model and settings, and treat a change to them as a code change.** This pipeline uses `eleven_v3` at stability 0.6, similarity_boost 0.92, style 0.3. A different model does not error and does not change the words; it returns a flatter reading of the correct script, and every probe still passes because none of them compares the output to the human recording the voice was cloned from. Nine clips shipped that way before a person said it sounded flat. Measured afterward, the wrong model rested 11.4 percent of the time against the human reference's 19.0, and held pitch range at 26.8 Hz against 44.9. Detail in [EVALS.md](EVALS.md).
6. **Draw three takes and keep the median by duration, then transcribe the winner and diff it against the script.** Synthesis is non-deterministic: the same text at the same settings varies 6 to 37 percent in length, and roughly one draw in three lands on a tail. Text-to-speech costs no render credits, so a single blind draw is strictly worse at identical cost. The transcript diff is the last checkpoint where a wrong word is still free to fix.
5. Draw **3 takes per script and pick by consensus metering**, never a single blind draw. About one draw in five drifts far enough to change the accent. Takes are billed per character, and audio is cheap next to renders, so this is the correct side of the meter to spend on.

## 2. Create the character (HeyGen)

Two paths, both ending in the same place:

- **Text prompt, no extra tools.** HeyGen's prompt avatar turns a written description into a character, and looks generated inside the same avatar group stay consistent with each other. This is the default path: one vendor, one identity chain, nothing to keep in sync.
- **Reference image.** Generate one clean still with whatever frontier image model you already use (Gemini, GPT, and Grok all produce workable reference stills as of this writing) and create a photo avatar from it. Use this when you need art direction the text prompt will not hold.

Either way, note two ids: the **avatar group id** (the character) and the **look id** (one specific appearance). The still image is your reproducibility seed: the render engine exposes no seed parameter, but animating a fixed look is deterministic, so the look id is the thing that controls the output.

**Which video engine: the flat tier.** Render on HeyGen **Avatar 3.0** (`avatar_iii` in this repo's probes and guards). It bills **1 credit per render, flat with length**: measured at ~11 seconds, ~126 seconds and ~169 seconds, 1 credit each time. The premium tiers billed 5 credits at 11s, 43 at 126s and 58 at 169s for output whose differences the probes in this repo were built to judge. For scheduled unattended work, the flat tier passes the evals and the premium tiers mostly buy risk; the full schedule, and the 344-credit incident behind the router's refusal to guess, are in [COST.md](COST.md).

You do not need a separate video-generation model. The narration video IS the avatar render: voice audio drives the character. General text-to-video models solve a different problem and meter much less predictably.

## 3. Pin both identities

Write the four ids (voice id, avatar group id, look id, model) into a pins file, and point the guards at it:

```
IDENTITY_PINS=/path/to/pins.json    # read by guards/block_unpinned_identity.sh
VOICE_TAKE=/path/to/your-tts-step   # the sanctioned voice entrypoint it names in refusals
REFRESH_PINS=/path/to/pin-refresh   # how a NEW look gets allowlisted
PROP_GATE / PIPELINE_PROBES         # see guards/pre_render_sanity.sh and guards/ship_gate.sh
```

The pins file itself stays out of git (this repo's `.gitignore` already excludes `pins.json`). The guard then refuses any render whose voice or avatar id is not the pinned one, on every egress path including raw HTTP. Why this is a mechanism and not a convention: prompt-level rules held 6 of 15 first attempts in this pipeline's measurements; the hook held every time. The whole argument is in [ENFORCEMENT.md](ENFORCEMENT.md).

## 4. Order of operations per render

```
script (>250 chars)  ->  3 voice takes, consensus pick   (characters, cheap)
                     ->  look check, prop gate            (free, blocks bad spend)
                     ->  ONE render on the flat tier      (1 credit)
                     ->  probes + ship gate               (free)
```

Synthesis before render, always: the audio drives the video, and every gate that can fail does so before the credit is spent.
