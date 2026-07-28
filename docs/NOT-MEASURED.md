# Not measured

What this repository does not claim, and what it would take to claim it honestly.

This file exists because the fastest way to lose a technical reader is one unearned number. Everything below is a number I could have written and chose not to.

---

## Time saved

**Not claimed.** The pipeline runs end to end in a median of 33 minutes with nobody watching, across 4 timed runs.

That is a measurement of the pipeline. It is **not** a claim about time saved, because I never measured a human doing the same work by hand. Without a baseline there is no saving, only a duration.

To claim it honestly I would need: a defined manual procedure producing comparable output, at least 5 timed human runs, and the same quality bar applied to both. I have none of those. "Saves 4 hours a day" would have been the easiest sentence in this repo to write and the easiest one to get caught on.

## Dollar cost

**Not claimed.** Daily render cost is 2 vendor credits, measured at 4 different clip lengths.

Credits are not dollars. The conversion depends on the plan, the tier, and whatever the vendor was charging that month, and I never recorded the rate at the time of the measurement. Back-filling today's price onto an older measurement would produce a number that looks precise and is not.

To claim it: record the plan and the credit-to-currency rate alongside each usage reading, at the time of reading.

## Reliability as a rate

**Not claimed.** The README says 4 of 7, 14 of 15, 0 of 7. It never says 57%, 93%, or 0%.

Every one of those denominators is small enough that the percentage would imply a precision the sample cannot support. n=7 with 4 successes has a 95% confidence interval spanning roughly 18% to 90%. Reporting "57% reliable" from that is not a summary, it is a fabrication with a decimal point.

The counts are reported as counts on purpose.

## Quality of the output

**Not claimed.** Nine invariants score the output, each with a threshold derived from labelled pass and fail exemplars rather than typed by hand.

This measures agreement with **my own** labels. It does not measure whether the output is good, whether a viewer would like it, or whether the invariants cover the ways it can fail. Nine earlier metric models were built and discarded because they inverted on contact with the labelled set, which is evidence the labels are doing real work, and also evidence that the space of plausible-but-wrong metrics here is large.

To claim quality: labels from someone who is not me.

## Generalization

**Not claimed.** One operator, one machine, one set of vendor accounts, one display device.

Nothing here has been run by a second person or on a second machine. The guards have known portability gaps, documented in [ENFORCEMENT.md](ENFORCEMENT.md), which is exactly the class of problem a second machine would surface immediately.

## The parallelism speedup

**Partly retracted.** The benchmark is real: 229s to 89s, byte-identical output, n=1.

The **explanation** I originally wrote for it was wrong. I attributed the gain to batched inference. Checking production afterward, the setting meant to run ten workers in parallel was not taking effect, and 4 of 6 production runs were executing at the serial rate. The measured speedup traces to a different mechanism than the one I documented, and the per-pass contribution of the batching I credited is about 1.06x, not the 2.1x I had claimed.

The number survived. The causal story did not. Both are left in the repo rather than quietly corrected, because the gap between them is the more useful artifact.

## Known open bugs

Stated here rather than fixed silently before publishing:

1. The parallel worker setting does not take effect. 4 of 6 production runs measured at the serial rate.
2. Three of four guards fail open when a dependency is missing, and report success while doing it.
3. The depth speedup is attributed to the wrong mechanism, per above.

None of these are fixed in this snapshot. A repo whose headline claim is "count attempts, not outcomes" would be a poor place to hide its own open findings.
