---
description: 논문 PDF 한 편을 받아 한국어 요약 + 한국어 전문 번역 + 영어 발표 슬라이드를 생성하는 전체 파이프라인 실행.
argument-hint: <assets/논문.pdf> [slug] [--only summary|translation|slides]
---

`review-orchestrator` 스킬을 사용해 다음 PDF에 대한 research-review 파이프라인을 실행하라:

**입력:** $ARGUMENTS

절차:
1. `.claude/skills/review-orchestrator/SKILL.md`를 읽고 그 절차를 따른다.
2. slug 미지정 시 PDF 제목에서 유도해 1줄로 확인.
3. `--only`가 있으면 해당 산출물만, 없으면 요약·번역·슬라이드 전체를 (병렬로) 생성.
4. 슬라이드는 `make slide-build PAPER=<slug>`로 빌드하고 `make slide-check`로 분량 검증, PDF 시각 점검까지.
5. 종료 보고: 생성된 파일 목록(링크) + 슬라이드 페이지 수 + 남은 위험.
