# Reliability

**Plain version:** I built a checker to catch bad videos. It never once caught a bad video. So I took away its power to block, instead of tuning it until it agreed with me.

---

## The gate that never worked

One stage had a quality gate in front of it. If the gate judged the generated output unusable, the stage fell back to a known-good clip instead of showing something broken.

Over 7 evaluations it fired once. I went and looked at the clip it rejected. The clip was fine.

So the tally was: **0 true positives, 1 false positive, 7 evaluations.** Every single time the gate expressed an opinion, acting on that opinion made the product worse, because the fallback replaced today's actual content with a generic clip from another day.

## Why it was not tuned

The obvious move is to adjust the threshold until the gate agrees with me. I did not, for one reason:

A gate with no true positives has never demonstrated that it can detect the thing it exists to detect. Tuning it changes how often it is wrong, not whether it works. Fitting the threshold to the one case I had would have produced a gate calibrated on a single sample I already knew the answer to, and I would have had no more evidence than before that it could catch a real failure. It would just have been quieter, which reads like improvement.

**A detector that has never fired correctly is not a mis-tuned detector. It is an unvalidated one, and tuning hides that.**

## What replaced it: fail open, fail loud

The gate stopped blocking. It still runs and still judges, but its verdict is now advisory. The stage proceeds with the real content either way.

The safety it used to provide moved to a different mechanism:

| | before | after |
|---|---|---|
| bad output detected | fallback clip shown, silently | real output shown, alert raised |
| gate wrong | real content silently destroyed | nothing happens, alert is noise |
| gate unavailable | fallback clip shown, silently | real output shown, alert raised |

The asymmetry is the whole argument. When the gate was wrong in blocking mode, it destroyed the day's real output and nobody found out. When it is wrong in advisory mode, the cost is one unnecessary alert. Given a detector with a measured 100% false-positive rate, the second failure mode is strictly cheaper.

The silent-fallback behaviour was itself the bug that started this. The display showed a generic clip for a day before anyone noticed, because a fallback that works perfectly looks exactly like a success.

## The alert test is inverted on purpose

The alert does not fire on a list of known failures. It fires on **anything that is not a clean success.**

Written the usual way, a failure nobody anticipated produces silence, and silence reads as success. Written inverted, a novel failure mode is loud the first time it happens, before anyone knows to look for it. The cost is more false alarms. That is the correct trade for an unattended system, where the alternative to a false alarm is not peace and quiet, it is not finding out.

## What this does not claim

n=7. Seven evaluations is not enough to prove a detector is useless in general, and it is not claimed to be. It is enough to say this one had produced no evidence of working at the point it was demoted, and that continuing to let an unvalidated detector destroy real output was the worse of the two available mistakes.

The fail-open guard findings in [ENFORCEMENT.md](ENFORCEMENT.md) come from synthetic broken input, not from production incidents. Three of the four guards have never actually lost a dependency in a real run. What is measured is what they *would* do.
