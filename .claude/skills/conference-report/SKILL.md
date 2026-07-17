---
name: conference-report
description: 학회 참관 사진(포스터·오랄 슬라이드 촬영본)을 받아 논문을 식별·웹 검증하고 한국어 XeLaTeX 참관 리포트를 생성한다. "참관 리포트", "학회 정리", "이 사진들 논문 찾아줘", "학회 다녀온 거 리포트로", "spotlight 정리" 요청 시 사용. (단일 논문 PDF의 요약·번역·슬라이드는 review-orchestrator.)
---

# conference-report

학회 현장 사진 묶음을 입력으로, **논문 식별 → 웹 검증 → 원문 정독 → 한국어 리포트(XeLaTeX)** 를 생성한다.
검증된 실제 사례: `icml_2026/` (ICML 2026, 논문·발표 14편 + 미리뷰 Spotlight 26편).

## 산출물 구조

```
<conf>/                      # 예: icml_2026, neurips_2026
├── pictures/                # 원본 사진 (read-only, gitignore — 용량 큼)
│   ├── research/            # 포스터·오랄 슬라이드 촬영본
│   └── booth/               # 부스·현장
├── papers/                  # 논문 PDF (gitignore) + README.md + download.sh (커밋)
└── report/
    ├── report.tex           # 리포트 본문 (커밋)
    ├── report.pdf           # 빌드 결과 (커밋)
    ├── Makefile             # references/Makefile 복사
    └── assets/              # EXIF 보정·2000px 사본 (커밋 — 이것만으로 재빌드 가능)
```

## 파이프라인

1. **사진 인벤토리·식별** — `pictures/research/`를 전부 Read로 열어 포스터/오랄/키노트 분류,
   제목·저자·소속·수치를 사진에서 추출. 스크린 촬영본(오랄)은 제목이 안 보이는 경우가 많다 —
   슬라이드 문구를 기록해 두고 다음 단계에서 실제 논문을 찾는다.
2. **웹 검증 (병렬 에이전트)** — 주제 클러스터별로 나눠 arXiv·icml.cc(가상 사이트)·GitHub 검색.
   확인 못 한 수치는 "UNVERIFIED" 표기, 절대 지어내지 않는다. 오랄은 슬라이드 문구가 논문
   제목이 아닐 수 있음(예: 도입부 슬라이드 문구 ≠ 실제 결론) — 실제 논문을 찾아 결론까지 대조.
3. **PDF 수집** — arXiv는 `papers/download.sh`(slug|id 매핑, curl) 방식. **OpenReview는 봇
   차단(challenge)** 이라 자동 불가 → README에 수동 다운로드 링크 안내. 다운로드 후
   `pdftotext -f 1 -l 1`로 제목 대조(잘못된 ID 방지).
4. **원문 정독 → 4-필드 추출 (병렬 에이전트)** — 논문 PDF를 2~3편씩 나눠 정독시키고
   **연구 배경 / 기존 방법의 한계 / 정의한 문제 / 해결 방법 + 핵심 결과(실수치)** 를 추출.
5. **리포트 작성 (탑다운)** — `references/report-template.tex` 복사 후:
   표지 → 현장 스케치 갤러리 → 목차 → §1 연구 동향(표) + 미리뷰 Spotlight(한줄 요약) →
   §2 개요·전체 목록(표) → §3~ 주제별 상세(`paperbox` + `pcard` + `result` + `shot`).
   1인칭 참관 톤 — "사진을 분석하여" 같은 메타 서술 금지.
6. **Spotlight/designation 확인** — 학회 공식 프로그램 JSON
   (예: `icml.cc/static/virtual/data/<conf>-orals-posters.json`)에서 decision 필드로 필터링.
   주의: 슬라이드/포스터의 "oral" 표기와 공식 designation은 다를 수 있다(ICML 2026은 Oral
   트랙 없이 Spotlight만 존재). 미리뷰 Spotlight의 한줄 요약은 **가상 사이트 abstract를 fetch해
   내용 기반으로 작성** — 제목만 보고 추정하지 않는다.
7. **빌드 + 시각 검증** — `make` (XeLaTeX 2회 + gs 압축) 후 `pdftoppm`으로 전 페이지 렌더:
   잘림·overfull·섹션 고아·사진 방향/화질을 눈으로 확인.

## Hard Rules (이번에 실제로 밟은 함정들)

1. **EXIF 회전** — 아이폰 사진은 픽셀이 가로인데 EXIF orientation으로만 세로인 경우가 있다.
   XeLaTeX는 EXIF를 무시하므로 그대로 넣으면 사진이 눕는다. 반드시
   `scripts/normalize_photos.py <pictures> <report/assets>`로 **EXIF를 픽셀에 구운 사본**을 만들어
   `\graphicspath`가 assets를 우선 참조하게 한다.
2. **gs 압축 화질** — 사진 표시 폭을 줄이면 같은 dpi에서 실효 픽셀도 준다.
   `/ebook` 150dpi는 축소 배치된 포스터 사진을 뭉갠다 — Makefile의 `/prepress` 300dpi 유지.
   의심되면 `pdfimages -list report.pdf`로 임베드 해상도 확인.
3. **페이지 잘림 금지** — 표·논문 블록·갤러리는 전부 **minipage 통짜**(float `[H]` 금지),
   섹션 제목은 `\sect`(needspace)로 본문과 결속. 논문 한 편이 페이지를 넘길 것 같으면
   사진 크기·행간을 줄여서라도 통째로 유지.
4. **`\multirow` + `\columncolor` 동시 사용 금지** — 배경이 multirow 텍스트를 가린다.
5. **마크다운 표 셀의 `|` 이스케이프** — `O(|S|²)`, `H(Z|X)` 같은 수식이 README 표를 깨뜨린다.
6. **git 정책** — 원본 사진·논문 PDF는 gitignore(용량), `report/assets/`(재빌드용)와
   `papers/README.md`(링크) + `download.sh`(복원)만 커밋.
7. **검증 우선** — 사진에서 읽은 수치와 웹 검증 결과가 다르면 **원문(arXiv/공식 데이터)이 이긴다**.
   출처 불명 수치는 리포트에 넣지 않거나 "포스터 기준" 명시.

## 번들

- `references/report-template.tex` — 검증된 프리앰블 + 매크로(`pcard`/`result`/`paperbox`/`gphoto`/`sect`) + 골격
- `references/Makefile` — XeLaTeX 2회 + gs `/prepress` 300dpi 압축
- `scripts/normalize_photos.py` — EXIF 보정 + 2000px 다운샘플 (PIL 필요)
