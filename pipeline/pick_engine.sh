#!/usr/bin/env bash
# pick_engine.sh - deterministic engine selector for the avatar render pipelines.
# Encodes the engine router in the pipeline spec: DEFAULT avatar_iii (2026-07-23, prod flipped to
# cost-first; accuracy is enough); avatar_iv opt-in for latency/movement, avatar_v for singing/hero.
#
# Usage:
#   pick_engine.sh [MODE] [DURATION_SEC]   MODE = prod (default) | dev | hero  -> JSON on stdout
#   pick_engine.sh next <ENGINE>           ENGINE = avatar_v|avatar_iv|avatar_iii -> next fallback
#   pick_engine.sh -h | --help
#
# MODE aliases: prod = default/scale/cost/cheap ; dev = iterate/latency/movement ; hero = best/quality/max/singing
#
# JSON fields: mode, engine_type, engine (object to pass to create_video_from_avatar),
#   resolution, aspect_ratio, fit, motion_prompt_ok, credits_est, credits_basis, render_sec_est,
#   fallback_chain (ordered engines to try, in order, if THIS render fails), note.
#
# ============================ CREDITS: MEASURED ONLY ============================
# credits_est is NULL for any duration we have not actually measured, and that is
# deliberate. Read credits_basis to see what IS known.
#
# What is measured, and nothing else is:
#   avatar_iii   1 credit at ~11s AND 1 credit at 125.7s   -> FLAT with length (two points, both 1)
#   avatar_iv    5 credits at ~11s ; 43 credits at 125.7s
#   avatar_v     5 credits at ~11s ; 43 credits at 125.7s
#
# Why no formula. This script used to emit a flat 5 for iv/v at every length, which
# read as "5 per render" and cost 43 on a 2-minute clip: an 8.6x understatement that
# sent a batch of 8 iv/v renders to 344 credits before anyone noticed (2026-07-27).
# The obvious repair, ceil(sec/11)*5, is WRONG and must not be shipped: it gives 60
# for the 125.7s clip that actually billed 43, so it fails to reproduce the single
# point it was fitted to. A straight line through the two iv/v points is also a
# guess, since it assumes billing is linear when it may be tiered, stepped, or have
# a floor (the implied linear slope is 3.76 credits per 11s, not 5, which is itself
# evidence the per-11s framing is wrong).
#
# One measurement cannot support a scaling law, and a formula is more dangerous than
# a missing number because it looks derived and nobody rechecks it. That is the same
# failure as the fabricated "24.4KB read limit" that propagated into two memory files
# and a dispatch on 2026-07-27, only wearing a formula.
#
# NULL makes a caller ask. A confident 5 makes it spend 43.
#
# To fill the table in: read the balance before and after a real render and record
# the delta as the measured cost at that length.
#   mcp__heygen__get_current_user -> .subscription.credits.premium_credits.remaining
# Add the point to the table above only once it is an observed delta, never a guess.
# ===============================================================================
#
# Calibration for RENDER TIME (clean sequential 1080p, ~11s clip, same look+audio, 2026-07-22):
#   avatar_iv 60s ; avatar_iii 90s ; avatar_v 125s.
#   720p vs 1080p: no cost or render-time difference -> always 1080p.
# NOTE: this is the SELECTION half of the router. The runtime failover loop
#   (relaunch down fallback_chain on status:failed) is owned by the orchestrator.
set -euo pipefail

usage() {
  cat <<'EOF'
pick_engine.sh - engine selector for the avatar render pipelines

  pick_engine.sh [MODE] [DURATION_SEC]   MODE = prod (default) | dev | hero   -> JSON
  pick_engine.sh next <ENGINE>           avatar_v|avatar_iv|avatar_iii        -> next fallback
  pick_engine.sh -h | --help

MODE aliases: prod=default/scale/cost/cheap  dev=iterate/latency/movement  hero=best/quality/max/singing
Default is prod=avatar_iii (cost-first, 2026-07-23). Always 1080p (720p saves nothing).

CREDITS ARE MEASURED, NEVER EXTRAPOLATED. credits_est is null unless the duration
matches a measured point; credits_basis always states what is known.
  avatar_iii  1 credit, flat at any length (measured at 11s and 125.7s)
  avatar_iv   5 credits at 11s, 43 credits at 125.7s. Scaling law UNKNOWN.
  avatar_v    5 credits at 11s, 43 credits at 125.7s. Scaling law UNKNOWN.
Pass DURATION_SEC to get a measured figure when one exists.
EOF
}

# credits_for ENGINE DURATION -> sets CRED (json literal) and BASIS (prose)
# Returns a number ONLY at a measured point. Everything else is null.
credits_for() {
  local eng="$1" dur="${2:-}"
  case "$eng" in
    avatar_iii)
      # Flat, and that flatness is itself measured at two lengths an order apart.
      CRED=1
      BASIS="measured: 1 credit at 11s and 1 credit at 125.7s, flat with length"
      return ;;
  esac
  # iv / v: two measured points, no law between or beyond them.
  if [ -z "$dur" ]; then
    CRED=null
    BASIS="UNKNOWN without a duration. Measured: 5 credits at 11s, 43 credits at 125.7s. Scaling law not known, do not interpolate. Pass DURATION_SEC, or measure the balance delta."
    return
  fi
  local near
  near=$(awk -v d="$dur" 'BEGIN{ if (d>=9 && d<=13) print "11"; else if (d>=120 && d<=131) print "126"; else print "" }')
  case "$near" in
    11)  CRED=5;  BASIS="measured: 5 credits for an ~11s render (2026-07-22)" ;;
    126) CRED=43; BASIS="measured: 43 credits for a 125.7s render (2026-07-27)" ;;
    *)   CRED=null
         BASIS="UNKNOWN at ${dur}s. Measured points are 11s=5 credits and 125.7s=43 credits; the law between them is not known and must not be guessed (ceil(sec/11)*5 predicts 60 for the 125.7s clip that billed 43). Measure the balance delta around this render and add the point." ;;
  esac
}

emit() { # $1 mode  $2 engine_type  $3 render_sec  $4 motion_ok  $5 fallback_json  $6 note  $7 duration
  local CRED BASIS
  credits_for "$2" "${7:-}"
  printf '{"mode":"%s","engine_type":"%s","engine":{"type":"%s"},"resolution":"1080p","aspect_ratio":"1:1","fit":"cover","motion_prompt_ok":%s,"credits_est":%s,"credits_basis":"%s","render_sec_est":%s,"fallback_chain":%s,"note":"%s"}\n' \
    "$1" "$2" "$2" "$4" "$CRED" "$BASIS" "$3" "$5" "$6"
}

cmd="${1:-prod}"

case "$cmd" in
  -h|--help|help) usage; exit 0 ;;
  next)
    case "${2:-}" in
      avatar_v)   echo "avatar_iv" ;;
      avatar_iv)  echo "avatar_iii" ;;
      avatar_iii) echo "avatar_iv" ;;
      *) echo "pick_engine.sh: 'next' wants avatar_v|avatar_iv|avatar_iii, got '${2:-}'" >&2; exit 2 ;;
    esac
    exit 0 ;;
esac

case "$cmd" in
  dev|iterate|latency|movement|iv|avatar_iv)  mode=dev ;;
  prod|default|scale|cost|cheap|iii|avatar_iii) mode=prod ;;
  hero|best|quality|max|singing|v|avatar_v)   mode=hero ;;
  *) echo "pick_engine.sh: unknown mode '$cmd' (want dev|prod|hero, or 'next <engine>')" >&2; exit 2 ;;
esac

DUR="${2:-}"

case "$mode" in
  dev)  emit dev  avatar_iv  60  true  '["avatar_iii"]'              "dev: fastest, latency-first + movement (has expressiveness). Cost scales with length and the law is unknown; see credits_basis." "$DUR" ;;
  prod) emit prod avatar_iii 90  false '["avatar_iv"]'              "prod (DEFAULT): 1 credit flat at any length, softer lip-sync, no motion_prompt" "$DUR" ;;
  hero) emit hero avatar_v   125 true  '["avatar_iv","avatar_iii"]' "hero: best lip-sync and motion, ~2x slower. Cost scales with length and the law is unknown; see credits_basis." "$DUR" ;;
esac
