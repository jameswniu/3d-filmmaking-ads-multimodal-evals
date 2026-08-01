# Cost, measured and predicted

Use this to size a plan and predict monthly spend before committing to either vendor.

## Before you begin

- **Two meters, two units.** HeyGen bills **credits per render**. ElevenLabs bills **characters per synthesis**. Everything below is in those native units.
- **No currency figures here, deliberately.** No credit-to-currency rate was recorded at measurement time and vendor pricing moves. The reason is in [NOT-MEASURED.md](NOT-MEASURED.md).
- **Check the vendors' own pricing pages** against the consumption model below. The model is what this repo can promise; the quota tables are theirs.

---

## The render schedule, as actually measured

| engine tier | ~11s clip | ~126s clip | ~169s clip | shape |
|---|---|---|---|---|
| `avatar_iii` (flat tier) | **1 credit** | **1 credit** | **1 credit** | flat with length, three measured points |
| `avatar_iv` | 5 credits | 43 credits | **58 credits** | NOT flat, and not knowably linear |
| `avatar_v` | 5 credits | 43 credits | **58 credits** | same as iv at every measured point |

**Default every scheduled render to the flat tier.** That recommendation falls straight out of the first row: a 2-minute daily clip on `avatar_iii` costs exactly what a 9-second one costs. The premium tiers cost 43x more at 2 minutes, for output whose quality difference the eval harness in this repo was built to judge, and for scheduled unattended work the flat tier passes.

The 169-second column was NULL until a run measured it, and it has now been measured twice on independent pairs of renders, each pair costing 116 credits. 58 credits each, both times. Before the first pair the estimate published in advance was "plausibly 58 each, and the scaling law is unmeasured". The estimate landing does not make it a measurement, and it was labelled as an estimate for that reason. Note also what the new column does to the naive model: 126s to 169s is 34 percent more clip for 35 percent more credits, which looks linear, while 11s to 126s was 11x the clip for 8.6x the credits, which is not. Two segments with different slopes is exactly the shape a single fitted line would have hidden.

## Why the table has holes instead of a formula

The cost router used to emit a flat "5 credits" estimate for the premium tiers at every length. That estimate read as authoritative, and a batch of 8 premium renders billed **344 credits** before anyone noticed, an 8.6x understatement.

The obvious fix, fitting a line through the two measured points, was rejected on arithmetic: the implied slope (3.76 credits per 11s) fails to reproduce the very 43-credit observation it would be fitted to if billing has a floor, steps, or tiers, and nothing in the vendor's public docs says which it is.

So the router now returns **NULL for any duration it has not actually billed**, with a `credits_basis` field naming what is known. A NULL makes the caller ask. A confident 5 makes it spend 43. This is the same rule as the rest of the repo: an unmeasured number presented confidently is worse than an admitted gap.

### Add a measurement

New points are cheap to add, and the procedure is four steps:

1. Read the vendor's credit meter and note the value.
2. Render one clip at the target length.
3. Read the meter again.
4. Record **the delta only** as the measured cost at that length.

The absolute reading is account state and does not belong in a public repository. This file got that wrong once, and the pre-publish gate caught it.

## Voice synthesis

- Synthesis is metered **per character** of script.
- The pipeline draws **3 takes per script and keeps the median by duration**, because a single blind draw lands somewhere on a 6 to 37 percent spread. Character spend is therefore `3 x script length`.
- Scripts are kept above ~250 characters: short scripts measured ~110 Hz brighter and less consistent than the calibrated voice (measured 2026-07-26), so padding a too-short script is quality control, not waste.
- Audio is uploaded to the render vendor, so **TTS draws cost zero render credits**. Metering audio is nearly free; metering renders is not. The pipeline optimizes accordingly: draw voice takes liberally, render once.

## The daily model

For a pipeline like this one, two governed renders per day on the flat tier, one ~2-minute narration each:

```
renders:     2/day x 1 credit             =  2 credits/day  ->  ~60 credits/month
characters:  2 scripts x ~1,900 chars x 3 = ~11,400 chars/day -> ~350k chars/month
```

The 2 credits/day figure is measured across 4 clip lengths (see [EVIDENCE.md](EVIDENCE.md)). The character figure is arithmetic, not measurement: ~1,900 characters is typical for 2 minutes of English narration at a conversational pace, and the 3x is the take policy above. Scale both linearly with your own clip count and length.

## Which plan to buy

Stated as requirements, because plan contents change and this file should not rot with them:

- **HeyGen**: any plan whose monthly credit allowance covers your `renders/day x 30`, with API access. At 2 flat-tier renders a day that is ~60 credits/month, which as of this writing sits comfortably inside the entry paid tier. Premium-tier renders change the math by up to 43x per clip; buy for them only if you have a measured reason.
- **ElevenLabs**: instant voice cloning requires a paid plan, so the floor is the cheapest tier that offers it. Above that floor, pick by monthly character quota against `scripts/day x chars x 3 x 30`. At the daily model above (~350k chars/month) the entry paid tiers are too small and the mid "creator/pro" band is the fit; at 1 short clip a day the entry tier holds.

Verify both against the vendors' current pricing pages before buying.
