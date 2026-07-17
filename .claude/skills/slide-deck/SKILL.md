---
name: slide-deck
description: 논문 리뷰용 영어 Beamer 발표 슬라이드(`slides/slide.tex`)를 작성·빌드·시각 검증한다. 논문→슬라이드 변환, deck 작성/수정, 논문 figure 추출, XeLaTeX 빌드, overflow 시각 점검, 키워드 색 강조(positive=blue/negative=magenta 굵은체). "발표자료 만들어", "슬라이드", "deck", "슬라이드 빌드/줄여/늘려", "figure 가져와", "키워드 강조/색 표시", "강조 색 바꿔" 요청 시 사용. (PowerPoint .pptx 에는 사용 안 함.)
---

# slide-deck

논문 한 편을 **15~20분 리뷰 발표용 영어 Beamer deck**으로 변환하고, out-of-tree XeLaTeX로 빌드해 시각 검증까지 한다.

## 입력 / 출력

- **입력**: `papers/<slug>/_workspace/paper.txt` + 핵심 수치는 원본 `assets/<file>.pdf`.
- **출력**: `papers/<slug>/slides/slide.tex` (영어). Figure는 `papers/<slug>/slides/figures/`.
- **빌드**: `make slide-build PAPER=<slug>` → `papers/<slug>/slides/build/<slug>.pdf` (출력 PDF는 프로젝트 slug 이름).
- **새 논문 셋업**: 루트 `Makefile`은 `papers/<slug>/slides/Makefile`에 빌드를 위임한다. 새 `<slug>`면 빌드 전에 템플릿을 복사한다 — `mkdir -p papers/<slug>/slides/figures && cp .claude/skills/slide-deck/references/Makefile papers/<slug>/slides/Makefile`. (이 Makefile이 없으면 `make slide-build`가 깨진다.)

## 언어
- 슬라이드 본문은 **영어**. 학회 톤(telegraphic, 키워드 위주). 완결 문장은 framing 1줄까지만.

## 표준 흐름 (research-review 발표 기준)

논문 리뷰 발표의 논리: **Motivation → Problem/Gap → Method → Results → Takeaways**.

| 순서 | 프레임 | 메시지 |
|------|--------|--------|
| 1 | Title | 제목·저자·게재처 |
| 2 | TL;DR | 1슬라이드 핵심 요약 (문제 1줄 + 방법 1줄 + 결과 수치) |
| 3 | Motivation | 왜 이 문제가 중요한가 (도메인 위험·실패 사례) |
| 4 | Background / Gap | 기존 방법과 그 한계 (이 논문이 메우는 공백) |
| 5 | Overview | 제안 방법 1장 개요 (figure 1 권장) |
| 6~9 | Method | 핵심 구성요소를 1개씩 (각 1~2 프레임, 수식 1개 이내) |
| 10 | Theory/Intuition | 이론적·직관적 근거 (해당 시) |
| 11~13 | Experiments | setup → main result 표 → ablation/분석 |
| 14 | Efficiency / Limitations | 비용·한계 |
| 15 | Takeaways | 핵심 3줄 + 우리(도메인) 시사점 |
| 16 | References | 핵심 인용 3~5개 |

분량은 발표 성격에 맞춘다 — 간략 리뷰는 12~20 프레임, **본문 figure·table을 모두 담는 comprehensive 리뷰는 ~20~30 프레임**(논문 1편을 빠짐없이 다룸). 루트 `Makefile`의 `SLIDE_MIN`/`SLIDE_MAX`가 게이트(현재 18~32).

**완전성 규칙.** 별도 지시가 없으면 **논문 본문(§-단위)의 모든 Figure와 Table을 deck에 포함**한다. Figure는 `extract_figure.py`로 추출(2-컬럼 논문은 `--bbox`로 해당 컬럼만 — 인접 표/본문이 섞이면 bbox를 좁힌다), Table은 booktabs로 재작성(원문 수치 그대로, 우승 행 `\rowcolor` 강조). figure+table을 주제별로 묶어 한 프레임에 배치해 프레임 수를 관리한다.

## Hard Rules (비협상)

1. **Overlay 금지** — `\pause` / `\onslide` / `\only` / `\uncover` 금지. 점진 노출은 frame 복제 + 색 강조. (overlay는 page count와 slide count를 분리시켜 검증을 깨뜨린다.)
2. **컬러 박스 ≤ 2개/슬라이드** — `block`/`alertblock`/`exampleblock`/`tcolorbox` 합계.
3. **Motivation before formalism** — "왜"가 "무엇"보다 먼저.
4. **XeLaTeX only** — pdflatex 금지 (unicode·시스템 폰트).
5. **.tex가 single source of truth.**
6. **Telegraphic style** — bullet ≤ 2줄(~15 단어), 슬라이드당 bullet ≤ 4 (최대 7).
7. **모든 슬라이드는 substantive element 1개 이상** — 수식·표·다이어그램·정리·figure 중 하나. 짧은 bullet만 있는 슬라이드는 합치거나 보강.
8. **박스·컬럼 내부 overflow 가드** — block/tcolorbox는 가용 폭 ~85%, 세로도 추가 소비. 박스 안에는 *display 식 1개* OR *짧은 bullet 2~3개* 중 하나만. Beamer는 박스 내부 overfull 경고를 **억제**하므로 PDF 시각 점검 필수. **`columns` 함정**: `column{f\textwidth}` 안에서 `\textwidth`는 *칼럼 폭*으로 재정의되고 `l`/`r` 컬럼은 가장 긴 셀에 맞춰 늘어난다 → 2-컬럼 표는 심볼/라벨 컬럼을 짧은 토큰만 두고 `p{}` 폭은 칼럼의 ~0.7–0.85로 잡은 뒤 `Overfull \hbox` 로그 + 시각으로 가로 점검. 칼럼 사이 간격은 폭 합을 <1.0으로 두고 `\hfill`로 벌린다.
9. **References 슬라이드** — 마지막(또는 Thank You 직전)에 `thebibliography` + `\small`로 핵심 인용 3~5개.
10. **색상 3~5개로 제한** — 아래 팔레트 토큰만 사용. 대비 ≥ 4.5:1. `\tiny` 사용자 노출 금지. 구조색(`accent`)·positive(`posblue`)·negative(`negmag`)의 역할을 섞지 않고, 키워드 강조는 아래 *키워드 강조* 규약을 따른다.

## 표준 프리앰블 (XeLaTeX, 16:9, slate-blue)

새 deck은 아래 프리앰블로 시작한다 (`references/preamble.tex` 전체본을 그대로 복사해도 됨):

- `\documentclass[10pt, aspectratio=169]{beamer}`, `\usetheme{default}`, navigation symbols 제거.
- 폰트: `fontspec`(XeLaTeX) + sans body. CJK가 필요하면 `\usepackage{kotex}` 또는 `fontspec`의 CJK 폰트. **영어 deck이면 CJK 불필요** — `fontspec` 기본 라틴 폰트로 충분.
- 팔레트: `accent`(deep slate-blue `1F3A5F`), `accentSoft`(`5C7AA0`), `ink`(`1A1A1A`), `muted`(`6B6B6B`), `crimson`(드문 강조 `780016`); 키워드 강조용 `posblue`(positive `0066FF`), `negmag`(negative `D6009C`).
- footline: short-title (좌) / `frame/total` (우). section divider: `\AtBeginSection` full-bleed 1장.
- `tcolorbox`는 `enhanced`, inline title (boxed title 금지 — 폭 초과 방지).

전체 프리앰블·색 설정·footline·divider·tcolorbox 기본값은 `references/preamble.tex` 참조 (작성 시 1회 로드).

## 키워드 강조: positive = blue, negative = magenta

발표 청중은 슬라이드를 훑는다. 중요한 키워드를 **두 색의 굵은체**로 표시하면 "문제 → 해법" 논증이 한눈에 읽힌다. 매크로는 공유 프리앰블에 정의돼 있다.

- `\good{X}` — **positive 워딩**(bold `posblue`): 강점·이득·정확성·SOTA 결과 (grounded, outperforms, robust, converges, +6.8, …).
- `\warn{X}` — **negative 워딩**(bold `negmag`): 문제·실패 모드·한계·기존 연구 약점 (hallucinate, noisy, fails, marginal, lost-in-the-middle, costly, …).

- **밀도**: 프레임당 가장 중요한 2~4개만. 슬라이드를 무지개로 만들지 않는다.
- **손대지 않을 것**: 결과표 우승 행(이미 `\rowcolor`+bold), 수식, figure 내부 텍스트.
- **레거시**: 기존 `\blue`/`\hl`은 이제 bold `posblue`(positive)로 렌더된다. 새 강조는 `\good`/`\warn`을 쓴다.
- 색 두 개는 `references/preamble.tex` 한 곳(`posblue`/`negmag`)에서 조정 → 모든 신규 deck에 반영.

**기존 deck 일괄 적용(retrofit).** 프레임별 강조 키워드를 `{find, polarity}`로 식별(프레임이 많으면 프레임당 1 에이전트로 병렬 제안) → `edits.json`(`[{key, edits:[{find, polarity}]}]`)으로 모아 번들 스크립트로 **안전 적용**(프레임 내 유일 매칭 + wrap-only로 내용 보존):

```bash
python3 .claude/skills/slide-deck/scripts/apply_emphasis.py papers/<slug>/slides/slide.tex edits.json
```
적용 후 **반드시 빌드 + 시각 점검** — 굵은체가 빡빡한 프레임을 overflow시킬 수 있다(Hard Rule 8).

## 절차

### 1. 콘텐츠 설계 (텍스트 우선)
- `_workspace/paper.txt`에서 흐름표(위)에 맞춰 프레임별 메시지를 1줄씩 먼저 정리 (slide.tex 작성 전).
- main result 표·핵심 수치는 원본 PDF로 정확히 확인.

### 2. Figure 추출 (overview 슬라이드용, 선택)
논문 main figure(보통 Figure 1)를 overview 슬라이드에 첨부하려면 번들 스크립트 사용:

```bash
python3 .claude/skills/slide-deck/scripts/extract_figure.py \
  --pdf assets/<file>.pdf --page <0-indexed> --caption "Figure 1" \
  --out papers/<slug>/slides/figures/overview.png --dpi 250
```
스크립트: 캡션 텍스트 검색 → bbox 추론 → autotrim → 250 DPI 렌더. 페이지 헤더·캡션 제외. 추출 후 PNG를 눈으로 확인 (헤더/캡션 안 들어갔는지, 작은 글씨 가독한지).

### 3. slide.tex 작성
- 프리앰블 → title frame → TOC(선택) → 흐름표 순서대로 프레임.
- 표는 `booktabs`. 수식은 `amsmath`. main result는 핵심 열만 발췌 (전체 표는 paper에 위임).

### 4. 빌드 + 검증
```bash
make slide-build PAPER=<slug>          # XeLaTeX 2-pass
make slide-check  PAPER=<slug>         # 페이지 수 vs 시간 예산
```
빌드 로그 확인: `! ` 에러 0, `Overfull \hbox` > 10pt 점검, `Citation undefined` 0.

### 5. 시각 검증 (옵션 아님)
박스 내부 overflow는 로그에 안 잡힌다. PDF를 이미지로 떠서 프레임별 확인:
```bash
python3 -c "import fitz; d=fitz.open('papers/<slug>/slides/build/<slug>.pdf'); [p.get_pixmap(dpi=110).save(f'papers/<slug>/_workspace/slide_{i+1:02d}.png') for i,p in enumerate(d)]"
```
그 PNG들을 Read로 열어 (1) 박스·텍스트가 프레임 밖으로 안 나가는지, (2) figure가 안 잘리는지, (3) 표가 안 넘치는지 확인.

## 검증 체크리스트 (종료 게이트)

```
[ ] xelatex exit 0, ! 에러 0
[ ] Overfull \hbox > 10pt 없음
[ ] Citation undefined 없음
[ ] 페이지 수 in [SLIDE_MIN, SLIDE_MAX]
[ ] 박스 내부 overflow 시각 점검 통과 (Hard Rule 8)
[ ] References 슬라이드 존재
[ ] \pause/\onslide/\only/\tiny 사용 0회
[ ] main result 수치가 원문·summary 와 일치
```

## 트리거 예시
- "이 논문 발표자료 만들어 / 슬라이드로"
- "슬라이드 더 줄여 / 늘려 / Method 부분 보강"
- "overview figure 가져와"
- "deck 빌드해줘 / overflow 점검"
