# Build your own: voice, character, pins

Use this to stand up the same pipeline on your own accounts: one cloned voice, one generated character, both pinned so a render cannot quietly substitute either.

## Before you begin

- **Consent.** Clone only your own voice, or one whose owner gave you written consent. Both vendors require it and it is the right floor regardless.
- **The character is generated, not a likeness.** This repo's character is synthetic by design, and the identity guards keep even a synthetic identity un-substitutable.
- **Two accounts.** ElevenLabs with instant voice cloning (the free tier does not include it) and HeyGen. Sizing math is in [COST.md](COST.md).
- **On PATH.** `ffmpeg` and `ffprobe`. Guards also need `jq`.

## 1. Clone the voice

1. Buy the smallest ElevenLabs plan that includes instant voice cloning.
2. Record 1 to 3 minutes of clean speech: one quiet room, one mic, no music, natural pace. Consistency beats quantity, because the clone inherits the room you give it.
3. Create the instant clone and note its `voice_id`. Treat that id as a secret: anyone holding it plus your API key can speak in your voice.
4. Pin the model and settings. This pipeline uses `eleven_v3` at stability 0.6, similarity_boost 0.92, style 0.3. Treat a change to any of them as a code change.
5. Keep every script **above ~250 characters**. Shorter scripts read about 110 Hz brighter and less consistently, so padding a short script is quality control rather than waste.
6. Draw **three takes and keep the median by duration**. Synthesis is non-deterministic: the same text at the same settings varies 6 to 37 percent in length, and about one draw in three lands on a tail.
7. Transcribe the winning take and diff it against the script. This is the last checkpoint where a wrong word is still free to fix.

**Why the model pin matters.** A wrong model does not error and does not change the words. It returns a flatter reading of the correct script, and every probe still passes, because none of them compares the output to the human recording the voice was cloned from. Nine clips shipped that way before a person said it sounded flat. Measured afterward: the wrong model rested 11.4 percent of the time against the human reference's 19.0, and held pitch range at 26.8 Hz against 44.9. Detail in [EVALS.md](EVALS.md).

## 2. Create the character

Two paths, both ending in the same place:

- **Text prompt.** HeyGen's prompt avatar turns a written description into a character, and looks inside one avatar group stay consistent with each other. This is the default: one vendor, one identity chain, nothing to keep in sync.
- **Reference image.** Generate one clean still with whatever frontier image model you already use, then create a photo avatar from it. Use this when you need art direction the text prompt will not hold.

Note two ids either way: the **avatar group id** (the character) and the **look id** (one specific appearance). The still is your reproducibility seed. The render engine exposes no seed parameter, but animating a fixed look is deterministic, so the look id is what controls the output.

**Render on the flat tier.** HeyGen **Avatar 3.0** (`avatar_iii` here) bills **1 credit per render, flat with length**: measured at ~11s, ~126s and ~169s, one credit each time. The premium tiers billed 5, 43 and 58 credits for the same three. For scheduled unattended work the flat tier passes the evals and the premium tiers mostly buy risk. The full schedule, and the 344-credit incident behind the router's refusal to guess, are in [COST.md](COST.md).

You do not need a separate video-generation model. The narration video IS the avatar render: voice audio drives the character.

## 3. Pin both identities

1. Write the four ids into a pins file: voice id, avatar group id, look id, model.
2. Keep that file out of git. This repo's `.gitignore` already excludes `pins.json`.
3. Point the guards at it with the environment variables below.

```
IDENTITY_PINS=/path/to/pins.json    # read by guards/block_unpinned_identity.sh
VOICE_TAKE=/path/to/your-tts-step   # the sanctioned voice entrypoint named in refusals
REFRESH_PINS=/path/to/pin-refresh   # how a NEW look gets allowlisted
PROP_GATE / PIPELINE_PROBES         # see guards/pre_render_sanity.sh and guards/ship_gate.sh
```

The guard then refuses any render whose voice or avatar id is not the pinned one, on every egress path including raw HTTP. Why a mechanism and not a convention: prompt-level rules held 6 of 15 first attempts in this pipeline's measurements, and the hook held every time. The argument is in [ENFORCEMENT.md](ENFORCEMENT.md).

## 4. Order of operations, per render

```
script (>250 chars)  ->  3 voice takes, median by duration  (characters, cheap)
                     ->  look check, prop gate              (free, blocks bad spend)
                     ->  ONE render on the flat tier        (1 credit)
                     ->  probes + ship gate                 (free)
```

Synthesis always comes before render: the audio drives the video, and every gate that can fail does so before the credit is spent.

## Reference: the four pins

- **Voice id**: the ElevenLabs instant clone. Changing it changes who is speaking.
- **Avatar group id**: the character. Fixes identity across every look.
- **Look id**: one appearance of that character. This is the reproducibility seed.
- **Model**: `eleven_v3` plus its three settings. A change here is silent, so it is pinned.
