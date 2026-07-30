#!/usr/bin/env bash
# route_engine.sh - intent/signal router for the twin video renders. 2026-07-23.
# The layer ABOVE pick_engine.sh: maps what the clip IS to an engine, then defers to
# pick_engine.sh for the ready-to-use engine JSON. Encodes my routing model:
#
#   singing, OR music + movement/dance together   -> avatar_v  (tight lip-sync + motion together)
#   movement / dance (no vocal to sync)            -> avatar_iv (expressiveness dance dial)
#   latency-critical (and not singing/music)       -> avatar_iv (fastest)
#   default / repeated pipeline / talking-head     -> avatar_iii (cheapest; briefs, greetings, check-ins)
#
# Usage:
#   route_engine.sh [SIGNALS...]     -> engine JSON (from pick_engine.sh) + routed_because/routed_mode
#   route_engine.sh --text "..."     -> keyword heuristic on the request text (augments flags)
#   route_engine.sh -h | --help
#
# Signals (flags, combine freely):
#   --repeated --brief --greeting --checkin --scheduled --predicted --pipeline  (repeated pipeline)
#   --dance --movement --groove --dancing                                        (movement)
#   --singing --sing                                                             (singing)
#   --music --song                                                               (music / vocal audio)
#   --latency --fast --deadline --urgent                                         (latency-critical)
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PICK="$DIR/pick_engine.sh"

singing=0 music=0 dance=0 repeated=0 latency=0 text=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help|help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --singing|--sing) singing=1 ;;
    --music|--song) music=1 ;;
    --dance|--movement|--groove|--dancing) dance=1 ;;
    --repeated|--brief|--greeting|--checkin|--check-in|--scheduled|--predicted|--pipeline) repeated=1 ;;
    --latency|--fast|--deadline|--urgent) latency=1 ;;
    --text) shift; text="${1:-}" ;;
    *) : ;; # ignore unknown tokens
  esac
  shift
done

# keyword heuristic when --text is given (augments any flags)
if [ -n "$text" ]; then
  t=$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')
  # negation guards first (a matching negated phrase leaves the signal off): "no music", "without singing", etc.
  case "$t" in *"no sing"*|*"without sing"*|*"not sing"*|*"no vocal"*) : ;; *sing*|*lyric*|*vocal*) singing=1 ;; esac
  case "$t" in *"no danc"*|*"without danc"*|*"not danc"*|*"no movement"*|*"no groov"*) : ;; *danc*|*groov*|*movement*|" move "*|*"moving to"*) dance=1 ;; esac
  case "$t" in *"no music"*|*"without music"*|*"no song"*|*"no beat"*|*"no track"*) : ;; *music*|*song*|*track*|*anthem*|*beat*) music=1 ;; esac
  case "$t" in *brief*|*greeting*|*check-in*|*checkin*|*"good morning"*|*"good night"*|*goodnight*|*hello*|*daily*|*standup*|*recurring*) repeated=1 ;; esac
  # NOTE: "quick" = technically quick (fast render/turnaround) = latency-critical -> avatar_iv (2026-07-23). It does NOT mean shorten the content; "quick" -> short SCRIPT is a roadmap idea, not built.
  case "$t" in *urgent*|*asap*|*deadline*|*quick*|" fast"*) latency=1 ;; esac
fi

# decision tree (2026-07-23; sing+dance -> SPEED lipsync, decided after the precision-vs-speed benchmark)
method="render"; lipsync_mode=""
if [ "$dance" = 1 ] && { [ "$singing" = 1 ] || [ "$music" = 1 ]; }; then
  # want golden-set dance AND singing: don't fresh-render (calmer dance) or use precision (~20min).
  # SPEED create_lipsync on the golden/existing dance clip -> keeps golden dance + adds sync, ~6.5min.
  mode=hero; method="lipsync"; lipsync_mode="speed"
  why="sing/music + movement -> SPEED lipsync on the golden/existing dance clip (keeps golden dance + sync, ~6.5min; my verdict: quality ok, much faster than precision)"
elif [ "$singing" = 1 ]; then
  mode=hero; why="pure singing, no dance -> avatar_v fresh render (tightest lip-sync)"
elif [ "$dance" = 1 ]; then
  mode=dev;  why="movement/dance, no vocal to sync -> avatar_iv (expressiveness dance dial)"
elif [ "$latency" = 1 ]; then
  mode=dev;  why="latency-critical -> avatar_iv (fastest)"
else
  why="default talking-head -> avatar_iii (cheapest)"
  [ "$repeated" = 1 ] && why="repeated/scheduled pipeline (brief, greeting, check-in) -> avatar_iii (cheapest)"
  mode=prod
fi

# defer to the tested selector for the engine JSON, then splice in the routing reason + method
eng=$(bash "$PICK" "$mode")
python3 - "$eng" "$why" "$mode" "$method" "$lipsync_mode" <<'PY'
import json,sys
d=json.loads(sys.argv[1]); d["routed_because"]=sys.argv[2]; d["routed_mode"]=sys.argv[3]
d["method"]=sys.argv[4]
if sys.argv[5]: d["lipsync_mode"]=sys.argv[5]
print(json.dumps(d))
PY
