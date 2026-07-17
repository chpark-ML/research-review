#!/usr/bin/env bash
#
# PostToolUse hook (matcher: Edit|Write)
# --------------------------------------
# Reads Claude Code's hook payload from stdin and emits a single-line
# `[notify] ...` reminder tailored to the changed file's extension.
# Advisory only — never blocks the tool, always exits 0.
#
# Per-extension reminders:
#   .tex         → slide build + page/time-budget check (no auto-build)
#   summary.md   → cross-check against translation.md and slide.tex
#   .md          → markdown deliverable changed
#
# Requires nothing beyond python3 (payload parse); silent if absent.

set -euo pipefail

fp=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null) || exit 0
[ -z "$fp" ] && exit 0

case "$fp" in
  *.tex)
    echo "[notify] LaTeX 변경: ${fp} — \`make slide PAPER=<slug>\` 로 빌드 + slide-check 권장 (자동 빌드 X). 박스 내부 overflow 는 PDF 시각 검증."
    ;;
  */summary.md)
    echo "[notify] 요약 변경: ${fp} — 핵심 수치·용어가 translation.md / slide.tex 와 일치하는지 교차 확인 권장."
    ;;
  */translation.md)
    echo "[notify] 번역 변경: ${fp} — 원문 문단 누락 여부와 용어 표기 일관성 확인 권장."
    ;;
esac
