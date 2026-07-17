#!/usr/bin/env bash
# ICML 2026 리뷰 대상 arXiv 논문 일괄 다운로드 (README.md 참조)
set -euo pipefail
cd "$(dirname "$0")"

papers=(
  "agentscore|2601.22324"
  "ma-rag|2603.03292"
  "topbench|2604.28076"
  "lassoflexnet|2603.20631"
  "ppm-nonstationary-ts|2605.23402"
  "scaling-masked-diffusion|2602.15014"
  "learning-unmasking-policies|2512.09106"
  "do-we-need-adam|2602.07729"
  "cat-q-ternary|2606.26650"
  "less-is-enough-fac|2602.10388"
  "sensei|2606.05602"
)

for entry in "${papers[@]}"; do
  slug="${entry%%|*}"; id="${entry##*|}"
  if [[ -s "${slug}.pdf" ]]; then
    echo "skip  ${slug}.pdf (exists)"
    continue
  fi
  echo "fetch ${slug}.pdf  (arXiv:${id})"
  curl -sL -A "Mozilla/5.0" --fail -o "${slug}.pdf" "https://arxiv.org/pdf/${id}.pdf"
  sleep 1
done
echo "done."
