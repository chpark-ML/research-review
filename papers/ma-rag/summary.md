# MA-RAG (Multi-Round Agentic RAG) 상세 요약

> From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG · Wenhao Wu 외 (Nanjing University, Huawei Noah's Ark Lab, CUHK, ANU) · ICML 2026 (PMLR 306) · arXiv 2603.03292v3 · 코드 https://github.com/NJU-RL/MA-RAG

## 0. 서지 정보

| 항목 | 내용 |
| --- | --- |
| 제목 | From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG |
| 저자(소속) | Wenhao Wu, Chunlin Chen, Zhi Wang (Nanjing University) · Zhentao Tang, Shixiong Kai, Mingxuan Yuan (Huawei Noah's Ark Lab) · Yafu Li (CUHK) · Zhenhong Sun (Australian National University) |
| 게재처 | ICML 2026 (43rd International Conference on Machine Learning), PMLR 306, Seoul |
| 연도 | 2026 |
| 분량 | 27페이지 (본문 9p + 부록 A~H) |
| 코드 | https://github.com/NJU-RL/MA-RAG |
| 키워드 | medical reasoning, retrieval-augmented generation, agentic RAG, test-time scaling, self-consistency |

## 1. 한 줄 요약 & 연구 동기

- **한 줄.** 의료 QA에서 여러 candidate response 간의 **semantic conflict**(의미적 충돌)를 retrieval을 유도하는 high-level 신호로 삼아 multi-round agentic refinement loop를 돌리는 MA-RAG를 제안, Qwen3-8B 백본 대비 7개 의료 벤치마크 평균 정확도를 **+6.8 points** (55.4% → 62.2%) 끌어올렸다.
- **배경.** 의료 LLM은 hallucination과 outdated knowledge로 안전이 중요한 의료 현장에서 위험하다. single-round RAG는 복잡한 multi-step 추론에 evolving 정보를 제공하지 못하고 noise를 끌어올 수 있다. adaptive RAG(FLARE, DRAGIN, TC-RAG 등)는 confidence·attention 같은 **noisy token-level signal**에 의존하는데, LLM은 높은 confidence로도 hallucinate하고 uncertainty가 도메인 핵심 의료 개념이 아니라 사소한 단어에 좌우되는 경우가 많다.
- **연구 질문.** (1) noisy token-level signal에 의존하지 않고 higher-level semantic cue로 agentic retrieval을 더 효율적으로 유도할 수 있는가? (2) self-consistency가 가정하는 "single-round로 합의 도달"의 한계를 multi-round로 어떻게 넘을 것인가?

## 2. 전체 구조

```
Abstract
§1 Introduction (문제 제기 · token-level signal 한계 · semantic conflict 아이디어)
§2 Related Work (RAG for Medical Reasoning · Test-Time Scaling)
§3 Method
   3.1 Problem Statement (iterative context optimization, State St)
   3.2 Solver Agent (N개 diverse candidate 생성)
   3.3 Retrieval Agent (conflict → K개 BM25 쿼리 → Dt+1)
   3.4 Ranking Agent (Intrinsic / Extrinsic score로 Ht 구성)
   3.5 Theoretical Grounding (adaptive self-consistency + boosting residual)
§4 Experiments
   4.1 Main Results        4.2 Ablation Study
   4.3 Test-Time Scaling Analysis (T, N)
   4.4 Scalability across Model Scales (Qwen3-32B)
   4.5 Inference Efficiency Analysis
§5 Conclusions, Limitations, and Future Work
Appendix A Pseudocode · B Datasets · C Baselines · D Implementation
         E Extrinsic Evaluator 학습 · F 추가 분석 · G Conflict-Driven Query 검증 · H Limitations + 프롬프트
```

## 3. 문제 정의 / 사전 지식

저자는 multi-round adaptive RAG를 **iterative context optimization** 문제로 정식화한다. LLM의 prompt를 고정 시퀀스가 아니라 라운드마다 진화하는 동적 구조로 본다. round $t \in \{1, \dots, T\}$에서 입력 state는 다음 복합 튜플이다.

$$S_t = \{I, q, D_t, H_t\}$$

- $I$: Task Instruction (불변).
- $q$: medical query.
- $D_t$: Document Context — 라운드마다 새 evidence가 누적되며 진화하는 의료 passage 집합 (single-round retrieval과 대비).
- $H_t = \mathrm{Rank}(A_{t-1})$: History Context — 이전 라운드 candidate를 단순 concat하지 않고 score로 정렬·구조화하여 high-quality in-context demonstration 시퀀스로 만든 것.

핵심은 $S_t \to S_{t+1}$ 전이를 어떻게 설계하느냐다. $A_t$ 내부의 semantic conflict로 (1) **무엇을 retrieve할지**($D_{t+1}$)와 (2) **history를 어떻게 제시할지**($H_{t+1}$)를 결정한다. 이는 매 라운드가 "hard case"에 집중해 직전 residual error를 외부 evidence로 교정하게 만드는 boosting 메커니즘을 모방한다.

**기존 방법의 한계 (저자 정리).** single-round/naive RAG는 evolving 정보 부재 + noise 유입; adaptive RAG는 token-level uncertainty(entropy, attention)에 의존 → over-confident hallucination을 못 잡고, 사소한 단어에 uncertainty가 쏠린다.

## 4. 제안 방법

3개 에이전트가 매 라운드 순차적으로 동작한다 (의사코드는 부록 A, Algorithm 1).

### 4.1 Solver Agent — "어디에 불확실성이 있는가"
- **목적.** 주 추론 엔진이자 내부 지식의 latent uncertainty를 드러내는 역할.
- **메커니즘.** 현재 state $S_t$ 조건 하에 temperature-controlled sampling으로 $N$개의 diverse candidate를 생성: $A_t = \{a_t^1, \dots, a_t^N\} \sim M(I_{\text{solver}}, q, D_t, H_t)$ (Eq.2).
- **비고.** "정확한 reasoning chain은 안정적 consensus로 수렴, hallucination은 divergent inconsistency를 보인다"는 경험적 통찰(SelfCheckGPT, self-consistency)에 근거. candidate가 일관되게 수렴하면 이를 **reasoning convergence**로 보고 loop를 종료, consensus를 aggregate해 최종 답을 낸다.

### 4.2 Retrieval Agent — "무엇을 retrieve할 것인가" (핵심 차별점)
- **목적.** token-level uncertainty 대신 candidate 간 semantic conflict를 knowledge gap의 신뢰 가능한 지표로 사용 → adaptive RAG의 noisy signal 문제 해결.
- **메커니즘.** candidate 충돌(상충하는 진단·증상 해석 등)을 $I_{\text{conflict}}$로 추출 후, 이를 해소할 $K$개의 targeted retrieval query를 생성: $R_t = \{r_t^1, \dots, r_t^K\} \sim M(I_{\text{conflict}}, q, A_t)$ (Eq.3). 이 conflict-aware 쿼리를 external medical corpus에 BM25로 던져 새 evidence $D_{t+1}$를 가져와 knowledge gap을 점진적으로 좁힌다.
- **비고.** 전제는 "충분한 지식·추론력 → 여러 독립 생성이 self-consistent / 충돌 → grounded evidence 결핍"이다. 위험 민감한 의료에서 사람이 불일치를 외부 근거·전문가 의견으로 조율하는 과정과 정렬.

### 4.3 Ranking Agent — "history를 어떻게 제시할 것인가"
- **목적.** sequential test-time scaling의 병목인 long-context degradation, 특히 "lost-in-the-middle"(프롬프트 중앙의 핵심 단서를 놓치는 현상)을 완화하는 context optimizer.
- **메커니즘.** score function $Q(\cdot)$로 직전 라운드 candidate $A_{t-1}$의 품질을 평가, descending order로 정렬해 History Context를 구성 (Eq.4): $H_t = \mathrm{sort}(A_{t-1}, \text{key}=Q)$. 점수가 높은 trace가 우선순위 demonstration이 된다. 두 가지 score function:
  - **Intrinsic Uncertainty (int).** sequence-level entropy 기반 (Eq.5). 값싸지만 token-level 통계.
  - **Extrinsic Verification (ext).** lightweight BERT 기반 verifier $V_\theta$. query-response pair $D_{qa}$에 cross-entropy로 binary classifier fine-tuning (Eq.6), 추론 시 $Q_{\text{ext}}(a) = V_\theta(q, a)$ (Eq.7). semantic correctness를 직접 포착.
- **비고.** ext는 ModernBERT-base(149M)를 full fine-tuning, [CLS] hidden state를 linear head로 사상, sigmoid 후 [0,10] 정수 점수로 매핑해 프롬프트에 명시(부록 E). 학습 데이터는 MedQA/MedMCQA/MedExpQA/MedXpertQA의 train split에서 Qwen3-8B로 질문당 128개 trace를 high-entropy sampling(T=1.0, top-k=20, top-p=0.95)해 stratified sampling으로 구성 (Medbullets·MMLU-Pro·NEJM은 평가 시 완전 out-of-domain).

## 5. 이론적/직관적 근거 (§3.5)

저자는 두 고전 원리로 정당화한다.

1. **Static → Adaptive Self-Consistency.** 표준 self-consistency(Eq.8, majority vote)는 단일 라운드 내부 지식만으로 합의에 도달한다고 가정한다. MA-RAG는 동일 objective(Eq.8)를 최적화하되 **confidence threshold $\epsilon$**를 gating으로 도입 — max consistency probability가 $\epsilon$ 미만이면 다음 라운드에 external retrieval을 트리거. 정적 self-consistency를 "필요할 때만" compute를 키우는 adaptive scaling으로 전환한다.

2. **Semantic Conflict as Boosting Residual.** classical boosting(gradient boosting, XGBoost)이 각 weak learner로 직전 residual error를 최소화하듯, MA-RAG는 라운드 $t$의 semantic conflict를 현재 state로 풀리지 않는 "boosting residual"(knowledge gap)로 본다. solver가 residual의 gradient 방향을 진단하고, retrieval·ranking이 이 residual을 "fit"할 외부 evidence·context를 제공한다. 반복적으로 "loss"(semantic conflict)를 줄여 안정적 high-fidelity consensus의 strong-learner 상태로 수렴.

## 6. 실험

### Setup
- **데이터셋 (7개 medical Q&A).** MedQA(USMLE, 1273), MedMCQA(4183), Medbullets(5-opt, 308), MMLU-Pro medical(818), NEJM(655, multi-answer 전부 일치해야 정답), MedExpQA(EN, 125), MedXpertQA(Text, 490). licensing exam부터 expert-level 임상 추론까지 난이도 스펙트럼.
- **베이스라인.** 13개 / 5개 paradigm — 4 backbone(Qwen3-8B, Llama-3.1-8B, UltraMedical-3.1-8B, HuatuoGPT-o1-8B), 3 test-time scaling w/o retrieval(CoT, SC, Multi-Refine), 3 naive RAG(SR-RAG, FL-RAG, FS-RAG), 2 adaptive RAG(FLARE, TC-RAG), 1 multi-agent(MDAgents).
- **백본.** Qwen3-8B (backbone 중 최강이라 기본 채택). 확장 실험은 Qwen3-32B.
- **RAG 인프라(공정 비교 통일).** corpus MedCorp(MedRAG; Textbooks 18권 + PubMed 23.9M abstract + StatPearls ~9.3k + Wikipedia 6.5M), retriever **BM25**(Pyserini), reranker **MedCPT-Cross-Encoder**. 2-stage: 서브코퍼스별 BM25 top-32(총 128) → MedCPT로 top-8. MA-RAG는 K=4 쿼리 각각 top-2씩 합해 라운드당 8개. 기본 T=8, K=4, Qwen3 thinking mode는 conflict 쿼리 생성 시에만 ON.
- **메트릭.** accuracy (%).

### Main result (Table 1)

| Method | MedQA | MedMCQA | Medbullets | MMLU-Pro | NEJM | MedExpQA | MedXpertQA | **Avg.** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-8B (backbone) | 71.1 | 61.3 | 51.0 | 64.9 | 56.0 | 67.2 | 16.1 | 55.4 |
| SC | 73.3 | 62.4 | 51.9 | 66.5 | 56.6 | 70.4 | 15.7 | 56.7 |
| MDAgents | 72.1 | 67.5 | 52.2 | 65.7 | 57.1 | 74.4 | 18.2 | 58.2 |
| Multi-Refine | 74.7 | 63.6 | 55.8 | 69.1 | 58.0 | 73.6 | 16.3 | 58.7 |
| TC-RAG (최강 RAG baseline) | 70.0 | 64.6 | 49.0 | 63.6 | 57.7 | 75.2 | 18.0 | 56.9 |
| **MA-RAG-int** | 77.0 | 67.1 | 57.1 | 70.9 | 60.8 | 72.8 | 21.2 | **61.0** |
| **MA-RAG-ext** | **77.1** | **67.2** | **59.1** | 70.7 | 60.5 | **78.4** | **22.2** | **62.2** |

- MA-RAG-ext 평균 **62.2%** — 백본 대비 **+6.8 points**, 최강 RAG baseline(TC-RAG 56.9) 대비 **+5.3 points**.
- 어려운 벤치마크에서 효과 두드러짐 — **MedXpertQA에서 37% 상대 개선**(16.1 → 22.2).
- ext가 int보다 평균 **+1.2 points** (BERT verifier > entropy). entropy는 confident hallucination을 못 잡는다는 분석과 일치.
- naive RAG는 미미하거나 오히려 하락(MedQA), FLARE·TC-RAG도 multi-round임에도 marginal — 단순히 retrieval 라운드만 늘리는 것은 부족.

### Ablation (Table 2, 누적 추가, Qwen3-8B)

| 구성 | Avg. | 증분 |
| --- | --- | --- |
| Qwen3-8B | 55.4 | — |
| +Multi-Refine | 58.7 | **+3.3** |
| +Retrieval Agent | 60.6 | **+1.9** |
| +Ranking Agent (= full MA-RAG) | 62.2 | **+1.6** |

- Retrieval Agent의 이득은 MedXpertQA 같은 knowledge-intensive 벤치마크에서 특히 큼(내부 지식 부족 시 외부 evidence 없이는 반복 추론이 교정 불가).
- Ranking Agent는 평균 +1.6, **MedExpQA에서 +4.0 points** — lost-in-the-middle 완화 효과.

### Test-time scaling 분석 (Table 3, MA-RAG-ext)
- **Round T.** T=1: 57.5 → T=2: 61.5(**+4.0**) → T=4: 62.1 → T=8: 62.2. **T=4 이후 saturate** → T=4가 cost-effective stopping criterion.
- **Candidate N.** N=2: 58.5 → N=4: 60.0(+1.5) → N=8: 62.2(+2.2). N 확대는 (i) conflict mining 풍부화, (ii) ICL용 trace 탐색 공간 확대. N=4는 자원 제약 시, N=8은 성능 최우선 시.
- **N이 saturation 지연 (Fig.5, Table 10, MedXpertQA).** N=16은 N=4 대비 Medbullets +4.6, MedXpertQA +4.3; N=4는 Round 2 후 정체하나 N=16은 Round 3 이후까지 개선 지속.

### Scalability (Table 4, Qwen3-32B)
- Qwen3-32B 64.7 → full MA-RAG 70.2 (**+5.5**). retrieval agent +1.8(MedXpertQA +3.7), ranking agent MedXpertQA +2.4. 더 큰 모델에서도 남는 knowledge gap을 외부 evidence가 메움.

### Inference efficiency (Table 5, MedXpertQA, Qwen3-8B)

| Method | Avg. Docs | Avg. Gen. Tokens | Avg. Final Tokens | Avg. Time (s) | Acc |
| --- | --- | --- | --- | --- | --- |
| Base (Qwen3-8B) | 0 | 514 | 514 | 5.6 | 16.1 |
| SC | 0 | 10,095 | 505 | 28.0 | 15.7 |
| FLARE | 30.0 | 962 | 429 | 42.7 | 17.7 |
| TC-RAG | 11.5 | 1,260 | 1,067 | 44.5 | 18.0 |
| MDAgents | 8.0 | 7,546 | – | 146.2 | 18.2 |
| **MA-RAG-ext** | 13.7 | 12,762 | 589 | 70.7 | **22.2** |

- FLARE의 절반 미만 문서로 +4.5 acc, TC-RAG 대비 문서는 약간 많지만 +4.2 acc. semantic conflict가 더 grounded한 retrieval signal임을 시사.
- 최강 baseline MDAgents보다 **+4.0 acc를 절반 미만 시간**으로 달성. TC-RAG 대비 약 1.6배 시간이나 +4.2 acc(상대 23.3% 개선).
- (부록 F.8 Medbullets: MA-RAG-ext 9.0 docs / 41.1s / 59.1 acc로 MDAgents 대비 +6.9를 약 1/3 시간에.)

### 주목할 부록 분석 (F~G)
- **Query granularity K** (F.1, |D|=8 고정): K=1/2/4 → 61.4/61.7/62.2. conflict를 여러 구체 쿼리로 분해할수록 분쟁점 커버리지 확대, expert-level에서 특히 효과(MedXpertQA K1→K4 +1.4).
- **Best-of-N 대비** (F.4): Extrinsic Evaluator Recall@1 58.5%(SC majority vote 56.7% 상회) but Recall@2 63.0%로 급등 → top-1은 자주 틀리고 정답이 top-2에 잠복. MA-RAG-ext 62.2%는 이 top-k recall을 final precision으로 전환(Pass@20 oracle 77.5에 접근).
- **Evaluator 단독 효과 분리** (F.5): SC·Multi-Refine 등에 동일 verifier를 붙여도(예: MedXpertQA SC +4.7, Multi-Refine +4.1) MA-RAG-ext가 여전히 우위(Multi-Refine+Eval 대비 Medbullets +2.6, MedXpertQA +1.8) → 성능이 verifier만으로 설명되지 않고 agentic loop에서 비롯됨.
- **기존 RAG와 호환** (F.6): SR-RAG warm-start + retrieval agent의 Hybrid Context가 최고(+2.8). retrieval agent는 plug-and-play 모듈.
- **Robustness** (F.7): 4회 독립 실행에서 MA-RAG-ext가 최고 평균 + 최저 분산(예: MedXpertQA 22.0±0.6) → semantic conflict가 token-level uncertainty보다 안정적 signal.
- **Hybrid ranking / Oracle** (F.3): int+ext 단순 결합(hyb 61.4)은 이득 제한적; Oracle ranking은 69.6으로, 더 정밀한 verification metric 개발 여지가 큼을 시사.
- **Conflict-driven query 검증** (G): LLM-as-a-Judge(Qwen3.6 Plus, DeepSeek V3.2, MiniMax M2.7) 3개 모델로 Faithfulness/Relevance/Comprehensiveness 평가. K 증가 시 Faithfulness는 다소 하락(예: 0.98→0.84), Comprehensiveness는 상승(coverage 확대) — 생성 쿼리가 실제 의료 분쟁을 충실히 반영함을 정량 확인.

## 7. 한계 & 향후 연구

**저자 명시 한계.**
- multi-round agentic refinement의 inference-time 비용(MedXpertQA 기준 질문당 약 12.7k generated tokens, 70.7s).
- retrieval 효과가 underlying medical corpus의 coverage·quality에 본질적으로 종속 (incomplete/outdated/institution-specific 지식이 systematic bias 유발 가능).
- 반복 retrieval·refinement로도 hallucination을 완전히 제거하거나 factual correctness를 보장할 수 없음.
- ranking agent의 잠재력은 evaluation 정확도에 묶임 — Oracle과의 격차가 개선 여지를 보여줌.

**향후.** web-scale search·structured medical DB·외부 reasoning module 등 풍부한 tool로 evidence 접근 확장, 더 신뢰할 만한 response quality estimation 개발.

**리뷰어 관점 추가 관찰.**
- "self-consistency 확장 + boosting residual" 해석은 직관적이나, threshold $\epsilon$ gating의 구체적 설정값·민감도가 본문에 명시되지 않아 재현 시 튜닝 포인트가 될 수 있다.
- 효율 비교는 동일 하드웨어 기준이나 절대 비용(12k+ 토큰/질문)이 실시간 임상 보조에는 부담일 수 있어, T·N·K의 운영 trade-off가 배치 환경별로 재검토 필요.
- LLM-as-a-Judge 평가의 심판 모델(Qwen3.6 Plus 등) 명세가 학습 cutoff 이후 명칭이라 외부 검증이 제한적이다.

## 8. 의료 AI 실무 적용 관점

- **실무 적용 가능성 (임상 QA 보조).** MA-RAG는 "여러 후보 답이 충돌할 때 그 충돌 자체를 근거 검색의 트리거로 삼는다"는 메커니즘이 명확해, 임상 의사결정 보조나 의료 지식 QA에서 evidence-grounded 응답을 만드는 데 직접 차용할 가치가 있다. 특히 단일 응답의 confidence가 아니라 **합의/불일치 구조**를 쓰는 점은 hallucination 위험이 큰 의료 응답에서 "모델이 확신하지만 틀린" 케이스를 잡아내는 안전장치로 활용할 수 있다. NEJM처럼 multi-answer 정확 일치를 요구하는 세팅에서도 작동함을 보였다.
- **재현 난이도 (비교적 용이).** 핵심 스택이 모두 오픈/표준이다 — BM25(Pyserini) + MedCPT-Cross-Encoder reranker + MedCorp(MedRAG) corpus + Qwen3-8B 오픈 백본. extrinsic verifier도 ModernBERT-base(149M) full fine-tuning(부록 E·표 8에 하이퍼파라미터 명시)으로 비용이 작다. 자체 한국어/병원 corpus로 MedCorp를 교체하는 식의 도메인 이식도 구조적으로 자연스럽다(F.6의 plug-and-play 성질).
- **추가 관찰.**
  - 가장 큰 실무 장벽은 **추론 비용**이다. 질문당 12k+ generated tokens / 약 70초(MedXpertQA)는 대화형 임상 보조에는 무겁다. 다만 T=4·N=4 같은 cost-effective 설정으로 절충 가능하고, MDAgents 대비 절반 시간에 더 높은 정확도라는 점은 multi-agent 대안 중에서는 경쟁력 있다.
  - retrieval 품질이 corpus에 종속되므로, 자체 보유한 임상 가이드라인·도메인 의료 텍스트로 corpus를 큐레이션하면 본 논문의 한계(coverage·institution-specific bias)를 강점으로 전환할 여지가 있다.
  - ranking agent용 verifier는 도메인 데이터로 재학습 시 직접적 성능 레버다(Oracle 격차 69.6 vs 62.2가 상한을 시사). 자체 정답 데이터로 ModernBERT verifier를 fine-tune하는 것이 가성비 높은 개선 경로로 보인다.
  - 단, 저자도 명시하듯 반복 retrieval로도 hallucination·factual correctness를 보장하지 못하므로, 환자 안전이 걸린 용도에서는 본 프레임워크를 **사람-검증 보조**로 한정하는 것이 합리적이다.
