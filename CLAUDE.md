# CLAUDE.md

research-review 프로젝트의 행동 가이드. 논문 PDF를 입력으로 **한국어 요약 · 한국어 전문 번역 · 영어 발표 슬라이드**를 생성하는 파이프라인.

**언어.** 사용자 프롬프트 언어에 맞춘다. 한/영 혼용 가능. 코드·경로·명령어·전문용어는 영문 원문 유지.

## 1. Think Before Coding
- 가정은 명시한다. 불확실하면 묻는다.
- 해석이 여러 개면 silently 고르지 말고 제시한다.
- 더 단순한 방법이 있으면 말한다.
- **Auto/yolo 모드 예외**: 자율 실행이 허가되면 합리적 가정을 1줄로 밝히고 진행. 파괴적 작업·모순 지시에서만 멈춰 묻는다.

## 2. Simplicity First
요청을 푸는 최소 코드만. 투기적 추상화·미요청 설정 금지.

## 3. Surgical Changes
- 기존 코드의 인접 부분을 임의로 "개선"하지 않는다.
- 기존 스타일을 따른다.
- 내 변경이 만든 orphan만 정리한다.

## 4. Goal-Driven Execution
작업을 검증 가능한 목표로. 산출물(요약·번역·슬라이드)은 단위 테스트가 없으므로 **빌드 + 시각 검증**으로 대체:
- 슬라이드 → `make slide-build PAPER=<slug>` 빌드 성공 + `make slide-check` 분량 + PDF 시각 점검.
- 요약·번역 → 핵심 수치가 원문과 일치하는지, 문단 누락이 없는지 자가 점검.

## 5. Surface Harness Gaps
작업 중 `.claude/skills/**/SKILL.md`, `.claude/hooks/*.sh`, `.claude/settings.json`, `CLAUDE.md`, `README.md`가 불완전·stale·모순이면 **조용히 우회하지 말고 제안**한다.
- 같은 응답에 1줄로 surface: `*harness gap*: <file>:<line> — <진단>`.
- file:line + before/after 구체 제시. 승인 후 편집.
- **반복 패턴(≥2회)** 에만 제안. 단발 case는 제외.

---

## 하네스: research-review 파이프라인

**목표:** 임의의 논문 PDF 한 편 → (1) 한국어 상세 요약, (2) 한국어 전문 번역(EN/KR 병렬), (3) 영어 Beamer 발표 슬라이드. 세 산출물은 같은 PDF에서 독립 생성되므로 병렬화한다. 부가 산출물로 **학회 참관 리포트**(현장 사진 → 논문 식별·검증 → 한국어 XeLaTeX 리포트)를 지원한다.

**트리거:** "논문 리뷰", "이 PDF 정리/요약/번역", "발표자료/슬라이드 만들어", "빌드", "다시"·"보완"·"개선", "다른 논문도" 등 리뷰 산출물 관련 요청 시 `review-orchestrator` 스킬을 사용. **"참관 리포트", "학회 정리", 사진 기반 다수 논문 정리**는 `conference-report` 스킬. 단순 도메인 질문은 직접 응답 가능.

**경량 하네스 구성:**
- `review-orchestrator` — 메인 진입점 (slug 결정 → PDF 인제스트 → 산출물 분배 → 빌드·검증 → 보고)
- `paper-summary` — 한국어 상세 요약
- `paper-translation` — EN/KR 병렬 전문 번역
- `slide-deck` — 영어 Beamer 슬라이드 (figure 추출·XeLaTeX 빌드·시각 검증 포함)
- `conference-report` — 학회 참관 리포트 (사진 식별 → 웹 검증 → PDF 정독 → 4-필드 스펙 테이블 리포트)

**규약:**
- 입력 PDF: `assets/` (read-only). 산출물: `papers/<slug>/` (논문별 self-contained).
- 중간 산출물: `papers/<slug>/_workspace/` (gitignore).
- 슬라이드 빌드: out-of-tree XeLaTeX, `make slide PAPER=<slug>`.
- 언어: 요약=한국어, 번역=한국어(EN/KR 병렬), 슬라이드=영어. 메서드명·메트릭·데이터셋명은 영문 유지.
- 학회 참관 산출물: `<conf>/`(pictures·papers·report) — 원본 사진·논문 PDF는 gitignore, `report/assets/`(EXIF 보정 사본)와 링크(README+download.sh)만 커밋.

**자동화 hook** (`settings.json`):
- Edit/Write Post-tool → `notify-file-change.sh` (`.tex` 빌드 권장, `summary.md`/`translation.md` 교차 확인 권장 알림). Advisory only, 차단 없음.

**변경 이력:**
| 날짜 | 변경 내용 | 사유 |
|------|----------|------|
| 2026-06-17 | 초기 구성 (경량 하네스: orchestrator + 3 스킬 + hook + Makefile), ma-rag 초안 생성 | ai-safety 하네스 패턴을 "PDF→요약·번역·슬라이드" 파이프라인 도메인으로 재구성 |
| 2026-06-22 | slide-deck 공유 프리앰블에 `\usepackage{pifont}` 추가 (`references/preamble.tex`), tcf-ehr 논문 산출물 생성 | 비교표 `\ding{51}/\ding{55}` 글리프를 쓰는 landscape deck마다 수동 추가 반복(≥2회) — 공유 프리앰블에 반영 |
| 2026-06-22 | (1) `references/Makefile` 템플릿 추가 + slide-deck·review-orchestrator에 신규 논문 Makefile 복사 절차 명시; (2) slide-deck Hard Rule 8에 beamer `columns`/`\textwidth` 함정·2-컬럼 표 가이드 추가; tcf-ehr deck에 Related Work·Problem-definition 페이지 보강 | 신규 논문마다 per-paper Makefile 부재로 빌드 실패(구조적); 2-컬럼 표 overflow 반복(≥2회) |
| 2026-06-22 | 빌드 산출 PDF를 프로젝트 slug 이름으로 변경 (`build/<slug>.pdf`, 예: `ma-rag.pdf`) — per-paper Makefile이 `-jobname`으로 slug 자동 유도, 루트 `SLIDE_PDF`·README·SKILL 참조 갱신 | 산출 파일명이 논문과 일치해 식별 용이 |
| 2026-06-23 | slide-deck에 **키워드 강조 규약** 추가 (positive=blue `posblue`/negative=magenta `negmag` 굵은체) — 공유 `references/preamble.tex`에 `\good`/`\warn` 매크로 + `\blue`/`\hl` bold 재정의, retrofit용 `scripts/apply_emphasis.py` 번들, SKILL에 규약·절차 문서화; ma-rag·tcf-ehr deck에 적용 | 발표 deck마다 강조 색·방식 수동 반복(≥2회) — 하네스에 표준화 |
| 2026-07-14 | **`conference-report` 스킬 신설** — 학회 참관 사진 → 논문 식별·웹 검증 → PDF 정독 → 한국어 XeLaTeX 리포트 파이프라인. 번들: `report-template.tex`(pcard/result/paperbox/gphoto 매크로), Makefile(gs `/prepress` 300dpi), `normalize_photos.py`(EXIF 보정). Hard Rules에 실측 함정 문서화(EXIF 회전, gs 화질, minipage 잘림 방지, multirow+columncolor 충돌, OpenReview 봇 차단, 대용량 자산 git 정책). orchestrator에 라우팅 예외 추가 | ICML 2026 참관 리포트(`icml_2026/`) 작업에서 파이프라인 전 과정과 함정 다수를 실증 — 학회 참관은 반복 이벤트라 템플릿화 |
