#!/usr/bin/env bash
# tools/pii_llm_review.sh - the judgement layer of the pre-publish PII gate.
#
# Run standalone:   bash tools/pii_llm_review.sh
# Staged only:      bash tools/pii_llm_review.sh --staged
# Explicit paths:   bash tools/pii_llm_review.sh path/one path/two
#
# EXIT CODES
#   0  the reviewer returned a clean verdict for every chunk
#   1  the reviewer flagged at least one chunk
#   2  the reviewer could not be reached, or returned something unparseable
#
# FAIL CLOSED, DELIBERATELY
#   Exit 2 is a FAILURE, not a pass. If the local model is down, the network is
#   out, the response does not parse, or the reviewer command cannot be found,
#   this script exits non-zero and the pre-commit hook stops the commit. An
#   unavailable reviewer means the content was never reviewed, and "never
#   reviewed" must never read the same as "reviewed and clean". Publication is
#   irreversible; a blocked commit costs a minute. If the model is genuinely
#   unavailable and the commit must go through anyway, that is a conscious human
#   decision and it is spelled PII_LLM_OVERRIDE=1, which is logged loudly in the
#   output so it shows up in any terminal scrollback or CI log.
#
# WHY THIS EXISTS ALONGSIDE tools/pii_scan.sh
#   The deterministic scanner catches shapes. It cannot catch:
#     - a third party named in ordinary prose, with no roster entry
#     - a daily routine, sleep window, or location inferable from wording
#     - confidential employer context that carries no ticket key or hostname
#     - a private message quoted as documentation
#     - a person made identifiable by the combination of two innocuous details
#   Those need a reader. This is the reader.
#
# WHY THE REVIEWER COMMAND IS NOT NAMED IN THIS FILE
#   This repository is public. Naming the specific local model tool here would
#   itself be a disclosure about the author's private toolchain, which is one of
#   the classes this gate exists to prevent. So the reviewer is resolved at run
#   time: PII_LLM_CMD if it is set, otherwise the first executable evaluator
#   skill found on this machine. Set PII_LLM_CMD explicitly in CI or on any
#   machine where discovery should not be guessed at.
#
#   The reviewer contract is minimal, so any model wrapper can satisfy it:
#     - it is invoked as:  "$PII_LLM_CMD" "<prompt text>"
#     - it prints JSON on stdout containing a "routing_decision" field
#     - a decision of "hold" or "act" means FLAGGED; anything else means clean
#     - a non-zero exit, empty output, or missing field means UNAVAILABLE

set -uo pipefail
LC_ALL=C
export LC_ALL

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Bytes of file content per reviewer call. Small enough that the model reads
# every line rather than skimming, large enough that a whole short file lands in
# one chunk and keeps its context.
CHUNK_BYTES="${PII_LLM_CHUNK_BYTES:-12000}"

TMPDIR_RUN="$(mktemp -d "${TMPDIR:-/tmp}/pii_llm.XXXXXX")" || exit 2
trap 'rm -rf "$TMPDIR_RUN"' EXIT

# ---------------------------------------------------------------------------
# Resolve the reviewer command
# ---------------------------------------------------------------------------
resolve_reviewer() {
  if [ -n "${PII_LLM_CMD:-}" ]; then
    if [ -x "$PII_LLM_CMD" ] || command -v "$PII_LLM_CMD" >/dev/null 2>&1; then
      printf '%s' "$PII_LLM_CMD"; return 0
    fi
    return 1
  fi
  local cand
  for cand in "$HOME"/.local/share/pii-review/*.sh; do
    [ -x "$cand" ] && { printf '%s' "$cand"; return 0; }
  done
  return 1
}

REVIEWER="$(resolve_reviewer || true)"
if [ -z "$REVIEWER" ]; then
  echo "=== pii_llm_review ==="
  echo "UNAVAILABLE: no reviewer command found."
  echo "Set PII_LLM_CMD to an executable that takes a prompt as argv[1] and"
  echo "prints JSON containing a routing_decision field."
  if [ "${PII_LLM_OVERRIDE:-0}" = "1" ]; then
    echo "PII_LLM_OVERRIDE=1: a human is knowingly publishing WITHOUT an LLM review."
    exit 0
  fi
  echo "RESULT: FAIL CLOSED. Not reviewed is not the same as clean."
  exit 2
fi

# ---------------------------------------------------------------------------
# Collect the content to review
# ---------------------------------------------------------------------------
MODE="tree"
EXPLICIT=()
for arg in "$@"; do
  case "$arg" in
    --staged) MODE="staged" ;;
    --tree)   MODE="tree" ;;
    -h|--help) sed -n '2,50p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "pii_llm_review: unknown option $arg" >&2; exit 2 ;;
    *)  MODE="explicit"; EXPLICIT+=("$arg") ;;
  esac
done

FILELIST="$TMPDIR_RUN/files.lst"
case "$MODE" in
  staged)
    ( cd "$REPO_ROOT" && git diff --cached --name-only --diff-filter=ACMR 2>/dev/null ) \
      | while IFS= read -r rel; do
          [ -n "$rel" ] && [ -f "$REPO_ROOT/$rel" ] && printf '%s\n' "$REPO_ROOT/$rel"
        done > "$FILELIST"
    ;;
  explicit)
    printf '%s\n' "${EXPLICIT[@]}" > "$FILELIST"
    ;;
  tree)
    find "$REPO_ROOT" \
      -type d \( -name .git -o -name '.venv*' -o -name node_modules \
                 -o -name __pycache__ -o -name renders -o -name state \) -prune -o \
      -type f -print > "$FILELIST"
    ;;
esac

# Text only. Binary media is class 7 and belongs to the deterministic scanner,
# which reads embedded metadata with a real metadata reader.
TEXTLIST="$TMPDIR_RUN/text.lst"
: > "$TEXTLIST"
while IFS= read -r f; do
  [ -f "$f" ] || continue
  case "$f" in
    *.png|*.jpg|*.jpeg|*.webp|*.gif|*.mp4|*.mov|*.webm|*.wav|*.mp3|*.hop|*.quilt|*.pdf) continue ;;
  esac
  grep -Iq . "$f" 2>/dev/null && printf '%s\n' "$f" >> "$TEXTLIST"
done < "$FILELIST"

N_FILES=$(wc -l < "$TEXTLIST" | tr -d ' ')
if [ "$N_FILES" -eq 0 ]; then
  echo "=== pii_llm_review ==="
  echo "nothing to review (mode=$MODE)"
  exit 0
fi

# ---------------------------------------------------------------------------
# Build chunks. Each chunk carries its file boundaries so the model can name a
# path in its rationale.
# ---------------------------------------------------------------------------
CHUNKDIR="$TMPDIR_RUN/chunks"
mkdir -p "$CHUNKDIR"
chunk_index=0
current="$CHUNKDIR/chunk.000"
: > "$current"
new_chunk() {
  chunk_index=$((chunk_index + 1))
  current="$(printf '%s/chunk.%03d' "$CHUNKDIR" "$chunk_index")"
  : > "$current"
}
while IFS= read -r f; do
  rel="${f#$REPO_ROOT/}"
  {
    printf '\n===== FILE: %s =====\n' "$rel"
    # Line numbers are included so the model can point at a line, and so its
    # output is comparable with the deterministic scanner's path:line output.
    cat -n "$f"
  } >> "$current"
  size=$(wc -c < "$current" | tr -d ' ')
  [ "$size" -ge "$CHUNK_BYTES" ] && new_chunk
done < "$TEXTLIST"
find "$CHUNKDIR" -type f -size 0 -delete 2>/dev/null
N_CHUNKS=$(find "$CHUNKDIR" -type f | wc -l | tr -d ' ')

# ---------------------------------------------------------------------------
# The prompt. Written to default to flagging.
# ---------------------------------------------------------------------------
build_prompt() {
  local body="$1"
  cat <<PROMPT_EOF
You are a pre-publication privacy reviewer. The text below is about to be
published in a PUBLIC repository, permanently and irreversibly. Your job is to
decide whether any of it should not be published.

Judge ONLY what a pattern matcher cannot see. A separate deterministic scanner
already covers API keys, tokens, email addresses, IP addresses, hostnames,
UUIDs, hex identifiers, phone numbers, ticket keys, and clock times. Do not
spend your answer on those. Look for the things that need a reader:

1. THIRD PARTY PEOPLE. Any other human made identifiable: a name, a nickname, a
   handle, a role plus enough context to identify one person, a quoted message
   attributed to someone, a described interaction with a named colleague,
   support representative, attorney, family member, or online commenter. This is
   the highest risk category. Treat a single given name as identifying if the
   surrounding text narrows it to one real person.

2. INFERABLE ROUTINE, PRESENCE, AND LOCATION. Anything that reveals when the
   author sleeps, wakes, works, travels, or is away from home; a repeating
   schedule; a described city, neighbourhood, beach, commute, or venue; a
   personal vehicle, home layout, or hardware inventory; a private purchase.

3. CONFIDENTIAL WORKPLACE MATERIAL. A former or current employer named or made
   obvious; internal project or product codenames; private repository names;
   internal processes, incidents, personnel actions, layoffs, severance, legal
   matters, or anything plausibly under NDA.

4. PRIVATE CONVERSATION CONTENT. A verbatim quotation of a private message,
   chat, or email, whether or not it is attributed; an informal aside that
   reads as lifted from a private thread rather than written as documentation.

5. FIRST PARTY PERSONAL DATA IN PROSE. The author's own identity, employment
   status, finances, health, family, or account state described in words rather
   than as a pattern.

6. ANYTHING THAT BECOMES IDENTIFYING IN COMBINATION. Two innocuous details that
   together narrow to one person, one household, or one company.

DEFAULT TO FLAGGING. If you are uncertain whether something is publishable,
flag it. A false alarm costs a human thirty seconds. A miss is permanent and
cannot be recalled. Silence is not evidence of cleanliness.

Set routing_decision to "hold" if you found ANYTHING in the categories above,
or if you are uncertain, or if the excerpt is too truncated to judge safely.
Set routing_decision to "research" ONLY if you are confident every line is
publishable as is.

In rationale, list each concern as "FILE:LINE - category - what it is". Never
reproduce a secret value in your rationale. Describe it instead.

--- BEGIN CONTENT UNDER REVIEW ---
${body}
--- END CONTENT UNDER REVIEW ---
PROMPT_EOF
}

# ---------------------------------------------------------------------------
# Review loop
# ---------------------------------------------------------------------------
echo "=== pii_llm_review ==="
echo "mode=$MODE  files=$N_FILES  chunks=$N_CHUNKS  reviewer=$(basename "$(dirname "$REVIEWER")")/$(basename "$REVIEWER")"
echo

FLAGGED=0
UNAVAILABLE=0
VERDICTS="$TMPDIR_RUN/verdicts.txt"
: > "$VERDICTS"

for chunk in $(find "$CHUNKDIR" -type f | sort); do
  label="$(basename "$chunk")"
  files_in_chunk="$(grep -c '^===== FILE:' "$chunk" 2>/dev/null || echo 0)"
  prompt="$(build_prompt "$(cat "$chunk")")"

  raw="$("$REVIEWER" "$prompt" 2>"$TMPDIR_RUN/$label.err")"
  rc=$?

  if [ $rc -ne 0 ] || [ -z "$raw" ]; then
    echo "$label: UNAVAILABLE (reviewer exit $rc)"
    sed -n '1,3p' "$TMPDIR_RUN/$label.err" 2>/dev/null | sed 's/^/    /'
    UNAVAILABLE=$((UNAVAILABLE + 1))
    continue
  fi

  # Tolerate a wrapper that prints prose around the JSON: take the last JSON
  # object in the output.
  json="$(printf '%s' "$raw" | tr -d '\000' | awk '/^[[:space:]]*\{/{buf=""} {buf=buf $0 "\n"} END{printf "%s", buf}')"
  decision="$(printf '%s' "$json" | jq -r '..|objects|.routing_decision? // empty' 2>/dev/null | head -1)"
  rationale="$(printf '%s' "$json" | jq -r '..|objects|.rationale? // empty' 2>/dev/null | head -1)"
  priority="$(printf '%s' "$json"  | jq -r '..|objects|.priority? // empty'  2>/dev/null | head -1)"

  if [ -z "$decision" ]; then
    echo "$label: UNAVAILABLE (no routing_decision in reviewer output)"
    UNAVAILABLE=$((UNAVAILABLE + 1))
    continue
  fi

  case "$decision" in
    hold|act|detect)
      FLAGGED=$((FLAGGED + 1))
      printf '%s: FLAGGED (decision=%s priority=%s files=%s)\n' \
        "$label" "$decision" "${priority:-unset}" "$files_in_chunk"
      printf '%s\n' "$rationale" | sed 's/^/    /'
      printf '%s\tFLAGGED\t%s\n' "$label" "$decision" >> "$VERDICTS"
      echo
      ;;
    *)
      printf '%s: clean (decision=%s files=%s)\n' "$label" "$decision" "$files_in_chunk"
      printf '%s\tCLEAN\t%s\n' "$label" "$decision" >> "$VERDICTS"
      ;;
  esac
done

echo
echo "totals: chunks=$N_CHUNKS flagged=$FLAGGED unavailable=$UNAVAILABLE"

if [ "$UNAVAILABLE" -gt 0 ]; then
  echo
  if [ "${PII_LLM_OVERRIDE:-0}" = "1" ]; then
    echo "PII_LLM_OVERRIDE=1: $UNAVAILABLE chunk(s) were NEVER REVIEWED and are being"
    echo "let through on a human decision. Record why."
  else
    echo "RESULT: FAIL CLOSED. $UNAVAILABLE chunk(s) could not be reviewed."
    echo "An unreachable reviewer means the content was not read. That is not a pass."
    echo "Fix the reviewer, or set PII_LLM_OVERRIDE=1 to publish without this layer."
    exit 2
  fi
fi

if [ "$FLAGGED" -gt 0 ]; then
  echo
  echo "RESULT: FAIL. The reviewer flagged $FLAGGED chunk(s)."
  echo "Read each rationale above. The reviewer is told to flag when uncertain, so"
  echo "some findings will be false alarms. Dismiss them by hand, in writing, and"
  echo "never by loosening the prompt."
  exit 1
fi

echo
echo "RESULT: PASS on LLM review."
echo "Run tools/pii_scan.sh for the deterministic patterns if you have not already."
exit 0
