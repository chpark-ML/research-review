# ICML 2026 리뷰 대상 논문

리포트(`../report/report.pdf`)에서 다룬 논문 원문. PDF 파일은 용량 문제로 커밋하지 않는다 —
아래 링크에서 받거나 `./download.sh` 실행으로 일괄 다운로드.

## ⭐ Spotlight 선정작 (4편)

ICML 2026은 별도 Oral 트랙 없이 채택작 6,796편 중 574편(≈8%)만 Spotlight로 선정.
리뷰 대상 중 아래 4편이 Spotlight이며, 4편 모두 oral 세션에서 short talk을 진행했다.

| slug | 논문 | oral 세션 |
|------|------|-----------|
| `learning-unmasking-policies` | Learning Unmasking Policies for Diffusion LMs (Apple/UvA/MIT) | Oral 1A |
| `do-we-need-adam` | Do We Need Adam? — RLVR with SGD (UIUC) | Oral 1A |
| `less-is-enough-fac` | Less is Enough — FAC data synthesis (UGA 등) | Oral 1A |
| `cat-q-ternary` | CAT-Q — 1.58-bit ternary PTQ (Intel Labs China) | Oral 4A |

## 그 외 주목할 Spotlight (미리뷰, 관심 주제별)

직접 리뷰하지 않은 Spotlight 574편 중 관심 주제 해당작을 공식 프로그램 데이터에서 선별.
LLM 계열은 136편이라 oral talk 겸한 것 중 7편만, medical은 임상·헬스케어 중심(단백질·신약 설계 제외).
† = oral talk 겸함. 링크는 icml.cc 가상 사이트.

**Medical / Clinical**

| 논문 | 한줄 요약 | 링크 |
|------|-----------|------|
| ClinTutor-R1: One-to-Many Alignment in Clinical Socratic Education | 회진처럼 1:N 임상 교육을 multi-agent 시뮬레이터로 모델링·학습 | [poster/66715](https://icml.cc/virtual/2026/poster/66715) |
| HypoSpace: Diagnostic Benchmark for Set-Valued Hypothesis Generation | 관측만으로 가설이 정해지지 않는 상황에서 LLM의 가설 공간 탐색·커버리지 평가 | [poster/64104](https://icml.cc/virtual/2026/poster/64104) |
| Listening Through the Noise: Cauchy-Driven Diffusion Bridges for GI Auscultation | 장음의 heavy-tailed 임상 잡음을 Cauchy diffusion bridge로 분리해 진단 신호 복원 | [poster/65341](https://icml.cc/virtual/2026/poster/65341) |
| Position: ML for Heart Transplant Allocation Policy Optimization | 장기 배분은 이해관계자 게임 — 배분 정책 ML은 인센티브를 고려해야 (position) | [poster/67226](https://icml.cc/virtual/2026/poster/67226) |
| Seizure-Semiology-Suite (S³): Clinically Multimodal Dataset & Benchmark | 발작 비디오 438개·라벨 35K로 MLLM의 발작(semiology) 이해 평가 | [poster/64497](https://icml.cc/virtual/2026/poster/64497) |
| SleepLM: Natural-Language Intelligence for Human Sleep | PSG와 자연어를 정렬한 수면 foundation model — 언어로 수면 현상 기술·질의 | [poster/65807](https://icml.cc/virtual/2026/poster/65807) |
| SurvDiff: Diffusion Model for Synthetic Data in Survival Analysis | 중도절단까지 재현하는 생존분석 전용 합성 데이터 diffusion 모델 | [poster/62922](https://icml.cc/virtual/2026/poster/62922) |

**RAG**

| 논문 | 한줄 요약 | 링크 |
|------|-----------|------|
| TG-RAG: Retrieval-Augmented Reasoning Guidance in Specialized Domains † | expert prior 기반 thought guidance 검색으로 생성 조향 — cognitive drift 완화 | [poster/63556](https://icml.cc/virtual/2026/poster/63556) |
| Train for Truth, Keep the Skills: Binary Retrieval-Augmented Reward vs. Hallucination | 근거 모순 여부의 binary reward로 online RL — 능력 보존하며 hallucination 감소 | [poster/65671](https://icml.cc/virtual/2026/poster/65671) |
| Linguistic Nepotism: Language Preference in Multilingual RAG | 관련성이 같아도 특정 언어 문서를 우대 인용하는 mRAG 편향 규명 | [poster/64557](https://icml.cc/virtual/2026/poster/64557) |

**Interpretability**

| 논문 | 한줄 요약 | 링크 |
|------|-----------|------|
| Activation Oracles: LLMs as General-Purpose Activation Explainers † | activation을 입력받아 자연어로 답하는 LatentQA 범용화 — OOD에서도 동작 | [poster/65446](https://icml.cc/virtual/2026/poster/65446) |
| Mechanistic Data Attribution: Training Origins of Interpretable LLM Units † | influence function으로 회로·헤드의 형성 기원을 학습 데이터까지 역추적 | [poster/64259](https://icml.cc/virtual/2026/poster/64259) |
| Towards Long-Horizon Interpretability: Multi-Token Attribution for Reasoning † | 긴 추론 체인의 O(\|S\|²) 비용·attribution 소실을 해결한 multi-token 귀속 | [poster/64718](https://icml.cc/virtual/2026/poster/64718) |
| Robust Harmful Features Under Jailbreak Attacks (Mechanistic Evidence) † | jailbreak은 safety feature 삭제가 아닌 특정 attention head의 선택적 억제 | [poster/64633](https://icml.cc/virtual/2026/poster/64633) |
| Guaranteed Optimal Compositional Explanations for Neurons † | 뉴런의 논리 규칙(compositional) 설명에 최적성 보장 부여 | [poster/64551](https://icml.cc/virtual/2026/poster/64551) |
| Language Model Circuits Are Sparse in the Neuron Basis | MLP 뉴런 기저가 SAE만큼 sparse함을 최초 실증 — SAE 없는 circuit tracing | [poster/64312](https://icml.cc/virtual/2026/poster/64312) |
| SVD as a Fast Interpretability Method for Transformers | 보조 모델 학습 없이 MLP 가중치 SVD만으로 해석하는 training-free 기법 | [poster/66016](https://icml.cc/virtual/2026/poster/66016) |
| Mixture of Concept Bottleneck Experts | CBM 예측기를 전문가 혼합·다양한 함수형으로 일반화 — 정확도·해석성 양립 | [poster/64795](https://icml.cc/virtual/2026/poster/64795) |
| Time Series Saliency Maps: Explaining Models Across Multiple Domains | Integrated Gradients를 가역 변환 도메인(주파수 등)으로 일반화한 시계열 귀속 | [poster/65637](https://icml.cc/virtual/2026/poster/65637) |

**LLM (oral talk 겸한 것 중 선별)**

| 논문 | 한줄 요약 | 링크 |
|------|-----------|------|
| The Flexibility Trap: Rethinking Arbitrary Order in Diffusion LMs † | any-order 생성이 일반 추론(수학·코딩)에선 오히려 해가 됨을 규명 | [poster/61998](https://icml.cc/virtual/2026/poster/61998) |
| WeDLM: Diffusion LMs with Standard Causal Attention for Fast Inference † | 표준 causal attention만으로 diffusion 디코딩 — prefix KV cache 유지로 고속화 | [poster/64095](https://icml.cc/virtual/2026/poster/64095) |
| How Much Can Language Models Memorize? † | 암기를 unintended memorization vs generalization으로 분리해 저장 용량 측정 | [poster/62989](https://icml.cc/virtual/2026/poster/62989) |
| Understanding Reasoning Collapse in LLM Agent RL † | agent RL의 입력 무관 템플릿 붕괴를 H(Z\|X)·I(X;Z) 분해로 탐지 | [poster/66821](https://icml.cc/virtual/2026/poster/66821) |
| OMAC: Optimization Framework for LLM-Based Multi-Agent Collaboration † | LLM 멀티에이전트 시스템의 구조·프롬프트를 체계적으로 최적화 | [poster/66164](https://icml.cc/virtual/2026/poster/66164) |
| Reinforcement Learning with Evolving Rubrics for Deep Research † | 검증 어려운 deep research를 정책과 함께 진화하는 rubric 보상으로 RL 학습 | [poster/65886](https://icml.cc/virtual/2026/poster/65886) |
| ReQAT: Full-Precision Reasoning Accuracy with 4-bit FP QAT † | FP4 실패가 low-entropy 토큰에 집중됨을 규명 — 겨냥 QAT로 정확도 복원 | [poster/63073](https://icml.cc/virtual/2026/poster/63073) |

## arXiv (11편)

| slug | 제목 | arXiv |
|------|------|-------|
| `agentscore` | Automatic Construction of Clinical Scoring Systems with LLM Agents | [2601.22324](https://arxiv.org/abs/2601.22324) |
| `ma-rag` | From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG | [2603.03292](https://arxiv.org/abs/2603.03292) |
| `topbench` | TopBench: A Benchmark for Implicit Predictive Reasoning in Tabular QA | [2604.28076](https://arxiv.org/abs/2604.28076) |
| `lassoflexnet` | LassoFlexNet: a Flexible Neural Architecture for Tabular Data | [2603.20631](https://arxiv.org/abs/2603.20631) |
| `ppm-nonstationary-ts` | Parametric Prior Mapping Framework for Non-stationary Probabilistic TS Forecasting | [2605.23402](https://arxiv.org/abs/2605.23402) |
| `scaling-masked-diffusion` | Scaling Beyond Masked Diffusion Language Models | [2602.15014](https://arxiv.org/abs/2602.15014) |
| `learning-unmasking-policies` | Learning Unmasking Policies for Diffusion Language Models | [2512.09106](https://arxiv.org/abs/2512.09106) |
| `do-we-need-adam` | Do We Need Adam? Surprisingly Strong and Sparse RL with SGD in LLMs | [2602.07729](https://arxiv.org/abs/2602.07729) |
| `cat-q-ternary` | CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs | [2606.26650](https://arxiv.org/abs/2606.26650) |
| `less-is-enough-fac` | Less is Enough: Synthesizing Diverse Data in LLM Feature Space with SAEs | [2602.10388](https://arxiv.org/abs/2602.10388) |
| `sensei` | Fix the Mind, Not the Move: Interpretable AI Assistance via Knowledge-Gap Localization | [2606.05602](https://arxiv.org/abs/2606.05602) |

## OpenReview 전용 (2편 — 봇 차단으로 수동 다운로드 필요)

| slug | 제목 | 링크 |
|------|------|------|
| `dmae` | Beyond Accuracy: Latent Perturbations for Cognitive-Aware Diagnosis | [OpenReview rEzGzILnVC](https://openreview.net/forum?id=rEzGzILnVC) |
| `crl-bpt` | Curriculum RL for Black-Box Prompt Tuning via LLMs | [ICML poster 66416](https://icml.cc/virtual/2026/poster/66416) |

## 키노트 (논문 아님)

- Lab-in-the-Loop for Drug R&D with AI — Aviv Regev (Genentech gRED), [ICML Invited Talk](https://icml.cc/virtual/2026/invited-talk/67266)
