# Evidence

Every number in the README, with where it came from and what you can check yourself.

## Before you begin

- **Most rows here are not independently verifiable, and that is stated rather than hidden.** The pipeline runs on one machine against my own vendor accounts, and the logs it writes contain schedule, account and third-party detail that has no business being public.
- **What you CAN verify is the code**: the probes, the guards and the thresholds are all here and all readable.
- **Two checks need nothing from me.** They are first, below, because a reader should be able to start with the part that does not require trusting anyone.

---

## What you can reproduce yourself

Two claims on this page need no logs, no accounts, and no light-field panel.

### The derivation, in one command

1. Install the probe dependencies: `pip install -r requirements.txt`.
2. Run `python3 evals/derive.py`.
3. Read the table it prints. Every named gating threshold appears with its value, the worst labelled pass, and the best labelled reject.

It ends by stating how many of those thresholds are derived from a labelled pair and how many were typed by hand. It also re-measures the labelled frames that ship in `assets/`, so the numbers are recomputed rather than recited. CI runs the same command, so a threshold that leaves its bracket fails the build.

### The fail-open finding

1. Pick any guard in `guards/`.
2. Remove or misdirect the file it depends on.
3. Feed it input it should reject.
4. Read the exit code.

```
# example shape, using the identity guard
IDENTITY_PINS=/nonexistent/pins.json bash guards/block_unpinned_identity.sh < a-payload-it-should-block.json
echo $?
```

Three of the four exit 0 and print nothing alarming. `ship_gate.sh` exits 64 on unreadable input, because it is the only one that has already had the incident. Detail in [ENFORCEMENT.md](ENFORCEMENT.md).

---

## What each number is counted from

| Number | Counted from | Method | Verifiable by a reader? |
|---|---|---|---|
| 16 of 16 named gating thresholds derived | This repository | `python3 evals/derive.py`, above | **Yes** |
| Nine invariants, 13 probes | This repository | `ls probes/` | **Yes** |
| Three of four guards fail open | This repository | The procedure above | **Yes** |
| Benchmark 229s to 89s | One A/B on the same input | Output compared byte for byte | Partly, the code is here |
| Runs on schedule, 10 of 10 days | The scheduler log for the morning stage | One line per fire, counted per calendar day, checked for gaps | No, log not published |
| 13 runs did real work, 0 errors | Same log | Runs that produced output, minus the no-op wake-ups | No |
| 21 of 37 wake-ups correctly did nothing | Same log | Total fires minus runs with work. The stage wakes more often than it acts | No |
| Full chain 4 of 7 | Per-run stage markers across 2 calendar days | A chain counts as complete only when the last stage wrote its output | No |
| Quality gate 0 true positives in 7 | The gate's own decision log | Every fire reviewed by hand against the clip it fired on | No |
| Constraint held 14 of 15, first attempt 6 of 15 | Run transcripts | Counted twice: final state, then first attempt. See below | No |
| Daily cost 2 credits | Vendor usage page | Read at 4 different clip lengths | No |
| Latency median 33 min | 4 timed end-to-end runs | Wall clock, first stage start to display update | No |

Rows are ordered by what a reader can check, not by what flatters the project.

---

## The two numbers that matter most, and why they differ

`14 of 15` and `6 of 15` are the same rule counted two ways.

- **14 of 15** is how many runs *ended* in the correct state. This is what a dashboard shows.
- **6 of 15** is how many runs *attempted* the correct thing without being stopped.

The difference is a pre-call hook rejecting a wrong first attempt and the model then correcting itself. Both numbers are true. Only the second one tells you whether the instruction worked, and it is the number a metrics dashboard will never show you, because by the time anything is recorded the outcome is already correct.

If you take one thing from this repo, take that: **an outcome metric cannot distinguish a system that complied from a system that was stopped.** Count attempts.

---

## Sample sizes, stated plainly

n=15 for the compliance rows. n=7 for chain completion and for the gate. n=4 for latency. n=1 for the benchmark A/B.

These are tallies, not reliability estimates. A rate computed from 7 observations has a confidence interval wide enough to drive a truck through, and none of these numbers should be read as a rate that would survive at scale. They are what happened, on one machine, over a few weeks.

## Numbers deliberately absent

Dollar cost and time saved. Both are in [NOT-MEASURED.md](NOT-MEASURED.md) with what it would take to get them honestly.
