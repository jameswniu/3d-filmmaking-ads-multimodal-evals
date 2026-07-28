# Pre-publish PII review

This repository was assembled from a private working tree. Publication is irreversible, so it went through a two-layer gate before the first commit. This file is the record: what each layer found, what was changed, and which findings were dismissed and why.

The dismissals are the point of writing this down. A gate whose false alarms get silently waved through is not a gate, and "we ran a scanner" is not evidence of anything if nobody can see what the scanner said.

---

## The two layers

| | catches | how it fails |
|---|---|---|
| `tools/pii_scan.sh` | shapes: keys, hosts, hex ids, clock times, name tokens | cheap, deterministic, blind to anything without a shape |
| `tools/pii_llm_review.sh` | meaning: a third party in prose, a routine, a quoted private message | slow, costs a call, over-flags |

Both run in `.githooks/pre-commit`. Only the deterministic layer runs in CI, for the reason given in `.github/workflows/pii-scan.yml`.

## What the deterministic layer found

125 findings on the first pass, 38 of them blocking. All were fixed or deliberately suppressed. It now exits 0 with 4 suppressions and **0 skipped checks**.

Two things worth recording:

**It had a bug that let real content through.** The owner-identity pattern is derived at runtime and was matched case-sensitively, so a comment shouting a name in capitals scored zero findings while the same name in ordinary case was caught on the adjacent line. Fixed by giving `run_rule` an optional flags argument and passing `-i` for that rule only. Case-insensitivity is wrong for the hex and key rules, so it is opt-in rather than global.

**A suppression I wrote hid a real finding.** I allowlisted wall-clock times in the README on the reasoning that they described the system's schedule rather than a person's. That was true of most of them and false of the one that mattered: a sentence pairing a specific time with "while you are asleep", which is a presence claim. The judgement layer caught it after the deterministic gate had already gone green. The sentence was rewritten and the suppression narrowed, so any future clock time in the README fails again. <!-- pii-allow: this paragraph quotes the flagged phrase in order to document it; line-scoped and visible in the diff -->

## What the judgement layer found

**Pass 1: 11 of 11 chunks flagged.** Two classes were real and neither had a shape the deterministic layer could ever have matched:

- **Persona handles.** Two-letter identifiers for the generated character appeared throughout the guards and probes, alongside references to the private hook and lock files that manage her identity pins. The README states the character is generated and not a likeness; the code then linked her to a private toolchain by name. A two-character token cannot be matched by a generic rule without matching half the English language. Removed.
- **Private tooling filenames** referring to scripts that are not in this repository, which were both a layout disclosure and dead references for any reader. Parameterized or renamed.

Both classes were then written into the local rule file, so the cheap layer catches them for free from now on. That is the intended direction: the expensive reader finds a new class, the cheap matcher inherits it.

**Pass 2: 12 of 12 chunks flagged.** Two real items survived, both single lines:

- a reference to an issue-tracker hook from unrelated professional work, which is the one genuine workplace trace in the repo
- one uppercase pronoun the earlier rewrite missed, because that pass matched lowercase only

Everything else on pass 2 was a false alarm, and the reviewer was clearly saturating.

## Dismissed, with reasons

Dismissed by hand, per the instruction in the reviewer's own output. Not by loosening its prompt.

| flagged as | actual | verdict |
|---|---|---|
| "internal project codename `avatar_iii` / `avatar_iv`" | published vendor engine version strings | dismissed |
| "internal tool name `ship_gate`" | a file in this repository, visible to the reader | dismissed |
| "internal project name: twin video pipeline" | this repository's own subject | dismissed |
| "hardware inventory: Apple Silicon, specific GPU architecture, display device" | product categories, not an inventory of what I own | dismissed |
| "scene and take names: smooth-beach, human-bakery, calm wave" | labels for generated video content, not real venues | dismissed |
| "reference to a specific female subject" | the generated character, disclosed as generated in the README | dismissed |
| "author's full name" | the byline on a portfolio repository, deliberate | dismissed |
| "verbatim quotation of private feedback" | my own words, quoted by me, in my own repository | dismissed |
| "personal account usage and cost" | published deliberately, in credits and never in currency, see NOT-MEASURED.md | dismissed |
| "internal incident history" | the documented reasoning behind each threshold, which is the artifact | dismissed |

The last one is the interesting dismissal. A reviewer tuned for confidentiality reads "here is the incident that produced this number" as a leak. In a repository whose entire claim is that thresholds were derived rather than typed, deleting the derivations would leave the numbers unfalsifiable. The incidents stay.

## Honest limits

The judgement layer never returned clean and probably cannot on this content, because at sufficient caution every specific technical detail reads as internal. Its value was concentrated in pass 1, on classes the regex could not express. Treating a persistently red reviewer as a blocker would mean stripping the repo of the specificity that makes it worth reading, so it is used as a **reader, not a gate**, and its output is triaged here in public rather than in private.

The deterministic layer is the gate. It is the one wired to block a commit, and the one that must stay at zero.

**What none of this covers:** the roster used for third-party name matching only contains names that were enrolled in it. Anyone unenrolled has no coverage from that check at all, which is why the judgement layer exists and why the highest-risk source files were excluded from this repository entirely rather than redacted. Redaction assumes you can enumerate what to remove.
