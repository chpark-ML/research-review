---
name: review-orchestrator
description: 논문 PDF 한 편을 받아 한국어 요약·한국어 전문 번역·영어 발표 슬라이드 세 산출물을 생성하는 research-review 파이프라인의 메인 진입점. "논문 리뷰", "이 PDF 정리해줘", "요약 만들어", "번역해줘", "발표자료 만들어", "슬라이드 빌드", "이 논문 처리해줘", "다시"·"보완"·"개선" 등 논문 리뷰 산출물 관련 모든 요청 시 반드시 사용.
---

# review-orchestrator

## 미션
주어진 논문 PDF 한 편을 입력으로, 세 가지 산출물을 생성·갱신한다.

| # | 산출물 | 언어 | 경로 | 담당 스킬 |
|---|--------|------|------|-----------|
| 1 | 상세 요약 | 한국어 | `papers/<slug>/summary.md` | `paper-summary` |
| 2 | 전문 번역 (EN/KR 병렬) | 한국어 | `papers/<slug>/translation.md` | `paper-translation` |
| 3 | 발표 슬라이드 (Beamer) | 영어 | `papers/<slug>/slides/slide.tex` | `slide-deck` |

세 산출물은 **같은 PDF에서 독립적으로** 만들 수 있으므로 병렬화한다. 단일 산출물만 요청되면 해당 스킬만 호출한다.

> **라우팅 예외**: 학회 참관 사진 기반 다수 논문 정리("참관 리포트", "학회 정리")는 이 파이프라인 대상이 아니다 — `conference-report` 스킬을 사용한다.

## 프로젝트 규약 (불변)

- **입력**: PDF는 `assets/`에 둔다 (read-only, 편집 금지).
- **출력**: 논문마다 `papers/<slug>/` 하위에 self-contained. `<slug>`는 짧은 kebab-case (예: `ma-rag`).
- **중간 산출물**: `papers/<slug>/_workspace/` (추출 텍스트 등, `.gitignore` 대상).
- **빌드**: 슬라이드는 out-of-tree XeLaTeX. `make slide PAPER=<slug>`.
- **언어**: 요약=한국어, 번역=한국어(EN/KR 병렬), 슬라이드=영어. 전문용어·메서드명·메트릭명은 원문(영문) 유지.

## Phase 0: 컨텍스트 확인 (필수 진입 단계)

작업 시작 전 항상:

1. **slug 결정** — 사용자가 지정 안 했으면 PDF 메타데이터(제목)에서 짧은 메서드명/약어로 유도. 예: "From Conflict to Consensus … MA-RAG" → `ma-rag`. 사용자에게 1줄로 확인.
2. **기존 산출물 확인** — `papers/<slug>/`에 `summary.md` / `translation.md` / `slides/slide.tex`가 이미 있는가?
   - 없음 → **초기 생성**.
   - 있음 + "다시/보완/개선/X만" → **부분 재생성**: 해당 산출물만 재호출.
3. **요청 분류** — 전체 파이프라인인가, 특정 산출물(요약만/번역만/슬라이드만)인가.

## Phase 1: PDF 인제스트 (모든 산출물의 선행 단계)

산출물 생성 전 텍스트를 한 번만 추출해 `_workspace/`에 저장하고 재사용한다.

```bash
mkdir -p papers/<slug>/_workspace
python3 -c "import fitz; d=fitz.open('assets/<file>.pdf'); open('papers/<slug>/_workspace/paper.txt','w').write(''.join(f'\n===== PAGE {i+1}/{d.page_count} =====\n'+p.get_text('text') for i,p in enumerate(d)))"
```

- PyMuPDF(`fitz`)의 `get_text("text")`가 2-컬럼 학술 논문의 읽기 순서를 `pdftotext -layout`보다 안정적으로 잡는다.
- 추출 후 페이지 1(제목/저자/abstract)과 마지막 본문 페이지(conclusion)를 직접 읽어 서지정보·핵심 기여를 확인.
- 서지정보는 `papers/<slug>/meta.yaml`에 기록 (제목, 저자, 게재처, 연도, arXiv ID, 코드 링크).
- **신규 논문 슬라이드 스캐폴드**: 슬라이드를 만들 거면 빌드 위임 대상 Makefile을 미리 만든다 — `mkdir -p papers/<slug>/slides/figures && cp .claude/skills/slide-deck/references/Makefile papers/<slug>/slides/Makefile`. (없으면 `make slide-build`가 깨진다.)

## Phase 2: 산출물 생성 (병렬)

전체 파이프라인이면 세 작업을 **병렬 서브에이전트**로 분배. 각 에이전트에 전달:
- 추출 텍스트 경로 (`papers/<slug>/_workspace/paper.txt`)
- 담당 스킬 경로 (`.claude/skills/<skill>/SKILL.md`를 먼저 읽고 그 절차를 따르라)
- 출력 경로
- `model: "opus"`

```
Agent({ description: "<산출물> 생성", subagent_type: "general-purpose", model: "opus",
  prompt: `먼저 .claude/skills/<skill>/SKILL.md 를 읽고 그 절차를 따르라.
  입력: papers/<slug>/_workspace/paper.txt (필요하면 원본 assets/<file>.pdf 도 참조)
  출력: papers/<slug>/<산출물 경로>
  <스킬별 구체 지시>` })
```

단일 산출물만 요청되면 직접 해당 스킬을 로드해 인라인으로 작업해도 된다.

## Phase 3: 빌드·검증 게이트 (슬라이드)

슬라이드를 만들었으면 반드시 빌드·검증:

```bash
make slide-build PAPER=<slug>      # XeLaTeX 2-pass
make slide-check  PAPER=<slug>     # 페이지 수 vs 시간 예산
```

- 컴파일 에러 0, `Citation undefined` 0, Overfull \hbox > 10pt 점검.
- 박스(tcolorbox/block) 내부 overflow 는 로그에 안 잡히므로 PDF 시각 검증 (`slide-deck` 스킬 검증 프로토콜 참조).
- 에러 시 1회 자가 수정 후 재빌드. 여전히 실패하면 로그 발췌 보고.

## Phase 4: 일관성 교차 확인

세 산출물을 함께 만들었으면 종료 전 점검:
- 핵심 수치(메인 결과·gain)가 요약·슬라이드에서 일치하는가.
- 메서드명/약어 표기가 세 문서에서 통일됐는가 (요약·번역은 원문 영문 용어 유지, 슬라이드는 영문).

## Phase 5: 종료 보고

1. **slug + 처리한 PDF**
2. **생성/갱신된 파일 목록** (절대 경로 + 링크)
3. **슬라이드 빌드 결과** (페이지 수 / 시간 예산)
4. **남은 위험/한계** (있으면)
5. **피드백 기회**: "요약 깊이·슬라이드 분량·번역 범위 중 조정할 부분이 있나요?"

## 후속 작업 키워드 (모두 본 오케스트레이터 트리거)

"다시", "재생성", "보완", "개선", "X만", "이 절만", "요약 더 자세히", "슬라이드 줄여/늘려", "빌드", "페이지", "다른 논문도".

## 자료 위치

- 입력 PDF: `assets/`
- 산출물: `papers/<slug>/{summary.md, translation.md, slides/slide.tex}`
- 중간: `papers/<slug>/_workspace/`
- 스킬: `.claude/skills/{paper-summary,paper-translation,slide-deck}/`
- 빌드: 루트 `Makefile` (`make slide PAPER=<slug>`)
