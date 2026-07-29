#!/bin/bash
# Reference reviewer for tools/pii_llm_review.sh, backed by the Claude Code CLI.
#
# Chosen as the default seat 2026-07-29, for two reasons in this order:
#   1. AUTH SHAPE. It runs on the operator's OAuth subscription. A privacy
#      gate that bills per call invites exactly the wrong economy: every run
#      has a marginal price, so the operator is nudged to run it less. The
#      gate must be free to run every commit, or it will not be run every
#      commit.
#   2. It is a reading model, not a routing model. The judgement layer's whole
#      purpose is what regex cannot see, which is a reading task.
#
# Contract (see pii_llm_review.sh header): argv[1] is the prompt; stdout must
# carry a JSON object containing routing_decision and rationale.
command -v claude >/dev/null 2>&1 || {
  echo "claude CLI not found; install it or set PII_LLM_CMD to another reviewer" >&2
  exit 1
}
# Cleared so the CLI behaves identically whether this gate runs from a plain
# terminal or from inside an agent session that sets it.
unset CLAUDECODE
exec claude -p --model sonnet --max-turns 1 \
  "Respond with ONLY a JSON object, no prose before or after, shaped exactly:
{\"routing_decision\": \"hold or research\", \"rationale\": \"<the FINDING lines, newline separated, or NO_FINDINGS>\"}

$1"
