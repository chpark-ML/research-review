# research-review

논문 PDF 한 편을 입력으로 받아 **세 가지 리뷰 산출물**을 자동 생성하는 파이프라인.

| 산출물 | 언어 | 형식 | 경로 |
|--------|------|------|------|
| 상세 요약 | 한국어 | Markdown | `papers/<slug>/summary.md` |
| 전문 번역 (EN/KR 병렬) | 한국어 | Markdown | `papers/<slug>/translation.md` |
| 발표 슬라이드 | 영어 | Beamer PDF | `papers/<slug>/slides/build/<slug>.pdf` |

논문 한 편당 `papers/<slug>/` 디렉터리 하나가 self-contained 산출물을 담는다.

---

## 1. 디렉터리 구조

```
research-review/
├── README.md                  ─ 본 문서
├── CLAUDE.md                  ─ 행동 가이드 + 하네스 설명
├── Makefile                   ─ 슬라이드 빌드 delegator (make slide PAPER=<slug>)
├── .gitignore
├── assets/                    ─ 입력 PDF (read-only)
│   ├── 2603.03292v3.pdf
│   └── 20012_Time_Conditioned_Foresee.pdf
├── papers/
│   └── <slug>/                ─ 논문별 산출물
│       ├── meta.yaml            서지 정보
│       ├── summary.md           한국어 상세 요약
│       ├── translation.md       한국어 전문 번역 (EN/KR 병렬)
│       ├── slides/
│       │   ├── slide.tex        영어 Beamer deck
│       │   ├── Makefile         out-of-tree XeLaTeX 빌드
│       │   ├── figures/         논문에서 추출한 figure (PNG)
│       │   └── build/           ← (gitignored) <slug>.pdf
│       └── _workspace/         ← (gitignored) 추출 텍스트 등 중간 산출물
└── .claude/                   ─ 경량 하네스 (skills · hook · settings · command)
    ├── settings.json
    ├── commands/review.md
    ├── hooks/notify-file-change.sh
    └── skills/
        ├── review-orchestrator/   메인 진입점
        ├── paper-summary/         한국어 요약
        ├── paper-translation/     EN/KR 병렬 번역
        └── slide-deck/            영어 Beamer 슬라이드 (+ figure 추출 스크립트)
```

---

## 2. 사용법

### Claude Code 안에서

```
/review assets/2603.03292v3.pdf ma-rag
```

또는 자연어로: *"assets/2603.03292v3.pdf 논문 리뷰해줘"*, *"이 논문 요약만 다시"*, *"슬라이드 좀 줄여줘"* — `review-orchestrator` 스킬이 받아 처리한다.

산출물 일부만 원하면:
```
/review assets/<paper>.pdf <slug> --only summary
/review assets/<paper>.pdf <slug> --only slides
```

### 슬라이드 빌드 (수동)

```bash
make slide        PAPER=ma-rag    # 빌드 + PDF 열기
make slide-build  PAPER=ma-rag    # 빌드만
make slide-check  PAPER=ma-rag    # 페이지 수 vs 시간 예산
make page-count   PAPER=ma-rag
make clean        PAPER=ma-rag
```

빌드는 **out-of-tree XeLaTeX** — 모든 산출물은 `papers/<slug>/slides/build/`에만 생성되고 소스는 깨끗하게 유지된다.

---

## 3. 파이프라인 단계

1. **Ingest** — PyMuPDF로 PDF 텍스트를 `_workspace/paper.txt`에 추출 (2-컬럼 읽기 순서 보존). 서지 정보는 `meta.yaml`.
2. **Summary** — `paper-summary` 스킬: 동기·기여·방법·실험·한계를 한국어로 체계화.
3. **Translation** — `paper-translation` 스킬: 본문을 EN/KR 문단 병렬로 번역.
4. **Slides** — `slide-deck` 스킬: Motivation → Gap → Method → Results → Takeaways 흐름의 영어 Beamer deck, figure 추출·빌드·시각 검증.

세 산출물(2~4)은 같은 추출 텍스트에서 **독립적으로 병렬 생성**된다.

---

## 4. 사전 요구사항

- **Python 3** + `PyMuPDF`(`fitz`) + `Pillow` — PDF 인제스트·figure 추출 (`pip install pymupdf pillow`).
- **XeLaTeX** (TeX Live / MacTeX) + **GNU Make** — 슬라이드 빌드. Latin Modern 폰트만 쓰므로 표준 설치로 충분.

---

## 5. 현재 리뷰된 논문

| slug | 제목 | 게재처 | 상태 |
|------|------|--------|------|
| [`ma-rag`](./papers/ma-rag/) | From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG | ICML 2026 | 초안 (요약·번역·슬라이드) |
| [`tcf-ehr`](./papers/tcf-ehr/) | Time-Conditioned Foreseeing: An EHR-Specific Foundation Model for Irregular Dynamics and Calendrical Time | ICML 2026 | 초안 (요약·번역·슬라이드) |
