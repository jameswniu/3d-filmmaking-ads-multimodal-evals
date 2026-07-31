#!/usr/bin/env bash
# Stage 0. The thing that fires the run when nobody is awake.
#
# The README described this stage for a long time without shipping it, which was
# the largest gap between the narrative and the repository. It is written here
# because it is the one stage with NO vendor in it: a lock, a budget cap, a
# timeout and an alert are ordinary systems work, and the interesting decisions
# are all about what happens when something goes wrong at 6am with no reviewer.
#
# Four mechanisms, and the reason each exists:
#
#   LOCK      Two runs racing is not hypothetical. The same shape was observed
#             five instances deep on another job in this system. mkdir is the
#             primitive because it is atomic on every POSIX filesystem and needs
#             no flock, which macOS does not ship. The PID goes inside so a stale
#             lock is diagnosable rather than merely fatal.
#
#   BUDGET    The pipeline spends real money per run. A guard that reads a ledger
#             BEFORE spending is the only kind that helps, because after the call
#             the money is already gone. The ledger is per day and append only.
#
#   TIMEOUT   A wedged vendor call does not fail, it hangs. Without a timeout the
#             lock is held forever and every later run is refused, so the failure
#             mode of a hang is an outage, not a missed clip.
#
#   ALERT     Anything that is not a clean success has to be loud. The default is
#             stderr; set WAKE_ALERT to a command and it receives the message on
#             stdin. Silence on failure is the defect this whole repository is
#             about.
#
# Exit codes are the contract:
#   0   the payload ran and succeeded
#   1   the payload ran and failed
#   64  bad usage
#   75  refused before spending (lock held, or budget exhausted)
#   124 the payload was killed by the timeout
#
# Usage:
#   wake.sh run <command...>     run the payload under all four guards
#   wake.sh selftest             exercise the guards, spend nothing
#
# Environment:
#   WAKE_DIR          state directory            (default: <repo>/state/wake)
#   WAKE_BUDGET       credits allowed per day    (default: 8)
#   WAKE_COST         credits this run will cost (default: 1)
#   WAKE_TIMEOUT      seconds before the kill    (default: 1800)
#   WAKE_ALERT        command receiving alerts on stdin (default: none, stderr)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WAKE_DIR="${WAKE_DIR:-$ROOT/state/wake}"
WAKE_BUDGET="${WAKE_BUDGET:-8}"
WAKE_COST="${WAKE_COST:-1}"
WAKE_TIMEOUT="${WAKE_TIMEOUT:-1800}"
LOCK="$WAKE_DIR/.lock"
LEDGER="$WAKE_DIR/spend.log"

alert() {
  local msg="wake: $*"
  if [ -n "${WAKE_ALERT:-}" ]; then
    printf '%s\n' "$msg" | $WAKE_ALERT || echo "$msg (alert command failed)" >&2
  else
    echo "$msg" >&2
  fi
}

today() { date +%Y-%m-%d; }

# Sum today's rows. A missing ledger reads as zero spent, which is correct on a
# first run and is also why the ledger is written AFTER the guard, never before.
spent_today() {
  local d; d="$(today)"
  [ -f "$LEDGER" ] || { echo 0; return; }
  awk -F'\t' -v d="$d" '$1 == d { s += $2 } END { printf "%d", s + 0 }' "$LEDGER"
}

# Atomic. If the directory already exists, the holder is either alive (refuse)
# or dead (clear it and take over). Anything else risks two concurrent renders.
take_lock() {
  mkdir -p "$WAKE_DIR"
  if ! mkdir "$LOCK" 2>/dev/null; then
    local holder; holder="$(cat "$LOCK/pid" 2>/dev/null || echo unknown)"
    if [ "$holder" != "unknown" ] && ! kill -0 "$holder" 2>/dev/null; then
      alert "clearing stale lock from dead pid $holder"
      rm -rf "$LOCK"
      mkdir "$LOCK" 2>/dev/null || return 1
    else
      return 1
    fi
  fi
  echo $$ > "$LOCK/pid"
  return 0
}

release_lock() { rm -rf "$LOCK"; }

# The guarded body. Split out so the lock has exactly ONE owner: cmd_run takes
# it, calls this, and releases it on every path. The first version relied on
# `trap release_lock EXIT` inside cmd_run, which is wrong in a way worth keeping
# a note about: an EXIT trap fires when the PROCESS exits, not when a function
# returns. Called as a function twice in one shell, as the selftest does, the
# first run never released and the second was refused by a lock it had taken
# itself. It looked like a locking bug and was a scoping bug.
_run_guarded() {
  local spent total
  spent="$(spent_today)"
  total=$(( spent + WAKE_COST ))
  if [ "$total" -gt "$WAKE_BUDGET" ]; then
    alert "budget: $spent spent today, this run costs $WAKE_COST, cap is $WAKE_BUDGET; refusing before spend"
    return 75
  fi

  # Charged BEFORE the payload, on purpose. A run that dies mid vendor call has
  # usually already been billed, so an optimistic ledger under counts exactly
  # when it matters most.
  printf '%s\t%s\t%s\n' "$(today)" "$WAKE_COST" "$(date +%H:%M:%S)" >> "$LEDGER"

  local rc=0
  if command -v timeout >/dev/null 2>&1; then
    timeout "$WAKE_TIMEOUT" "$@"; rc=$?
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$WAKE_TIMEOUT" "$@"; rc=$?
  else
    # No timeout binary. Say so rather than running unbounded in silence.
    alert "no timeout binary found; running WITHOUT a time limit"
    "$@"; rc=$?
  fi

  if [ "$rc" -eq 124 ]; then
    alert "payload exceeded ${WAKE_TIMEOUT}s and was killed"
    return 124
  fi
  if [ "$rc" -ne 0 ]; then
    alert "payload exited $rc"
    return 1
  fi
  return 0
}

cmd_run() {
  [ "$#" -gt 0 ] || { echo "usage: wake.sh run <command...>" >&2; return 64; }

  if ! take_lock; then
    alert "another run holds the lock (pid $(cat "$LOCK/pid" 2>/dev/null || echo unknown)); refusing"
    return 75
  fi
  # Signals only. A scheduled job can be killed between the lock and the
  # release, and a lock surviving that becomes an outage for every later run.
  trap 'release_lock' INT TERM
  local rc=0
  _run_guarded "$@"; rc=$?
  release_lock
  trap - INT TERM
  return "$rc"
}

cmd_selftest() {
  local tmp fails=0 rc before
  tmp="$(mktemp -d)"
  WAKE_DIR="$tmp"; LOCK="$tmp/.lock"; LEDGER="$tmp/spend.log"

  # 1. a clean run succeeds and is charged exactly once
  WAKE_COST=1 WAKE_BUDGET=8 cmd_run true >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "FAIL: clean run exited $rc"; fails=1; }
  [ "$(spent_today)" = "1" ] || { echo "FAIL: expected 1 credit, got $(spent_today)"; fails=1; }

  # 2. the lock is released, so a second run is not refused
  WAKE_COST=1 WAKE_BUDGET=8 cmd_run true >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "FAIL: lock not released after a clean run (rc=$rc)"; fails=1; }

  # 3. a held lock refuses with 75 and does NOT charge
  mkdir -p "$LOCK"; echo $$ > "$LOCK/pid"
  before="$(spent_today)"
  WAKE_COST=1 WAKE_BUDGET=8 cmd_run true >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 75 ] || { echo "FAIL: held lock should refuse with 75, got $rc"; fails=1; }
  [ "$(spent_today)" = "$before" ] || { echo "FAIL: refused run charged the ledger"; fails=1; }
  rm -rf "$LOCK"

  # 4. a stale lock (dead pid) is cleared and the run proceeds
  mkdir -p "$LOCK"; echo 999999 > "$LOCK/pid"
  WAKE_COST=1 WAKE_BUDGET=8 cmd_run true >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "FAIL: stale lock not reclaimed (rc=$rc)"; fails=1; }

  # 5. the budget refuses BEFORE spending
  before="$(spent_today)"
  WAKE_COST=99 WAKE_BUDGET=8 cmd_run true >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 75 ] || { echo "FAIL: over budget should refuse with 75, got $rc"; fails=1; }
  [ "$(spent_today)" = "$before" ] || { echo "FAIL: over budget run charged the ledger"; fails=1; }

  # 6. a failing payload reports 1, not 0
  WAKE_COST=1 WAKE_BUDGET=99 cmd_run false >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 1 ] || { echo "FAIL: failing payload should exit 1, got $rc"; fails=1; }

  # 7. a hanging payload is killed and reports 124
  if command -v timeout >/dev/null 2>&1 || command -v gtimeout >/dev/null 2>&1; then
    WAKE_COST=1 WAKE_BUDGET=99 WAKE_TIMEOUT=1 cmd_run sleep 5 >/dev/null 2>&1; rc=$?
    [ "$rc" -eq 124 ] || { echo "FAIL: hanging payload should exit 124, got $rc"; fails=1; }
  else
    echo "skip: no timeout binary, cannot test the kill path"
  fi

  # 8. usage error is 64, distinct from a refusal
  cmd_run >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 64 ] || { echo "FAIL: no payload should exit 64, got $rc"; fails=1; }

  rm -rf "$tmp"
  [ "$fails" -eq 0 ] && echo "wake selftest: all passed"
  return "$fails"
}

case "${1:-}" in
  run)      shift; cmd_run "$@" ;;
  selftest) cmd_selftest ;;
  *)        sed -n '2,46p' "$0" | sed 's/^# \{0,1\}//'; exit 64 ;;
esac
