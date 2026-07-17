#!/usr/bin/env bash
#
# PreToolUse guardrail (matcher: Bash)
# ------------------------------------
# Blocks commit / PR / issue commands that embed AI-authorship attribution,
# so no "an AI wrote this" trace lands in git history or on GitHub:
#
#   • Co-Authored-By: Claude ...  /  ... <noreply@anthropic.com>
#   • 🤖 Generated with [Claude Code](...)
#   • "Generated with Claude ..."
#
# This is the PRIMARY guard for this repo: commits here run `--no-verify`
# (rules/workflow.md R2), so the pre-commit `commit-msg` stripper is bypassed
# on the normal path — this PreToolUse hook fires on the command itself,
# regardless of --no-verify, and catches the attribution before it is written.
#
# Legitimate references are NOT attribution and are left alone: file names
# (CLAUDE.md), the .claude/ harness dir, `anthropic` API backends, and model
# names in prose. We only match the co-author trailer and generated-with
# footer shapes, and only on commands that write a message.
#
# Exit codes:
#   0 → allow tool to proceed
#   2 → block tool; stderr is fed back to Claude as feedback
set -euo pipefail

cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

lc=$(printf '%s' "$cmd" | tr '[:upper:]' '[:lower:]')

# Only inspect commands that author a commit message or PR/issue body.
printf '%s' "$lc" | grep -Eq 'git +commit|gh +pr +(create|edit)|gh +issue +(create|edit)' || exit 0

block() {
  echo "[guardrail] BLOCKED: AI-authorship attribution in a commit/PR command." >&2
  echo "  matched: $1" >&2
  echo "  policy: this repo never records an AI as author or co-author of commits or PRs." >&2
  echo "  fix: drop the 'Co-Authored-By: Claude' trailer and any '🤖 Generated with Claude Code' footer, then retry." >&2
  exit 2
}

# Co-author trailer crediting Claude/Anthropic (human co-authors are fine).
printf '%s' "$lc" | grep -Eq 'co-authored-by:.*(claude|anthropic)' && block "Co-Authored-By: Claude/anthropic trailer"

# "Generated with [Claude Code]" style footer.
printf '%s' "$lc" | grep -Eq 'generated with .{0,20}claude' && block "'Generated with Claude Code' footer"

# Robot-emoji footer.
printf '%s' "$cmd" | grep -q '🤖' && block "🤖 AI-footer emoji"

exit 0
