# From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG — 본문 EN/KR 병렬 번역

> 원문: Wu, W., Tang, Z., Li, Y., Kai, S., Yuan, M., Sun, Z., Chen, C., Wang, Z. **From Conflict to Consensus: Boosting Medical Reasoning via Multi-Round Agentic RAG.** Proceedings of the 43rd International Conference on Machine Learning (ICML), PMLR 306, 2026.
> 범위: Abstract – §5 Conclusions, Limitations, and Future Work. References·Acknowledgements·Impact Statement·부록(Appendix)은 제외. (본문 내 표/그림 참조 문장은 번역에 포함.)
> 포맷: 문단 단위 `**[EN]** 원문` → `**[KR]** 번역` 교차.

---

## Abstract

**[EN]** Large Language Models (LLMs) exhibit high reasoning capacity in medical question-answering, but their tendency to produce hallucinations and outdated knowledge poses critical risks in healthcare fields. While Retrieval-Augmented Generation (RAG) mitigates these issues, existing methods rely on noisy token-level signals and lack the multi-round refinement required for complex reasoning. In this paper, we propose MA-RAG (Multi-Round Agentic RAG), a framework that facilitates test-time scaling for complex medical reasoning by iteratively evolving both external evidence and internal reasoning history within an agentic refinement loop. At each round, the agent transforms semantic conflict among candidate responses into actionable queries to retrieve external evidence, while optimizing history reasoning traces to mitigate long-context degradation. MA-RAG extends the self-consistency principle by leveraging the lack of consistency as a proactive signal for multi-round agentic reasoning and retrieval, and mirrors a boosting mechanism that iteratively minimizes the residual error toward a stable, high-fidelity medical consensus. Extensive evaluations across 7 medical Q&A benchmarks show that MA-RAG consistently surpasses competitive inference-time scaling and RAG baselines, delivering substantial +6.8 points on average accuracy over the backbone model. Our code is available at https://github.com/NJU-RL/MA-RAG.

**[KR]** 대규모 언어 모델(Large Language Models, LLMs)은 의료 질의응답에서 높은 추론 능력을 보이지만, 환각(hallucination)을 생성하고 지식이 낡아지는 경향이 있어 의료 분야에서 치명적인 위험을 초래한다. Retrieval-Augmented Generation(RAG, 검색 증강 생성)이 이러한 문제를 완화하기는 하지만, 기존 방법들은 잡음이 많은 token-level 신호에 의존하며 복잡한 추론에 필요한 다중 라운드(multi-round) 정교화가 부족하다. 본 논문에서는 agentic refinement loop(에이전트 기반 정교화 루프) 내에서 외부 증거와 내부 추론 이력을 반복적으로 진화시킴으로써 복잡한 의료 추론에 대한 test-time scaling(추론 시점 연산 확장)을 가능하게 하는 프레임워크인 MA-RAG(Multi-Round Agentic RAG)를 제안한다. 매 라운드마다 에이전트는 후보 응답들 사이의 semantic conflict(의미적 충돌)를 외부 증거를 검색하기 위한 실행 가능한 쿼리로 변환하는 한편, 이력 추론 자취(history reasoning traces)를 최적화하여 long-context degradation(긴 맥락 성능 저하)을 완화한다. MA-RAG는 일관성의 부재를 다중 라운드 agentic 추론 및 검색을 위한 능동적 신호로 활용함으로써 self-consistency 원리를 확장하며, 안정적이고 높은 충실도의 의료 합의(consensus)를 향해 잔차 오류(residual error)를 반복적으로 최소화하는 boosting 메커니즘을 반영한다. 7개 의료 Q&A 벤치마크에 걸친 광범위한 평가는 MA-RAG가 경쟁력 있는 inference-time scaling 및 RAG 베이스라인들을 일관되게 능가하며, 백본(backbone) 모델 대비 평균 정확도에서 +6.8점이라는 상당한 향상을 제공함을 보여준다. 우리의 코드는 https://github.com/NJU-RL/MA-RAG 에서 이용할 수 있다.

---

## §1 Introduction

**[EN]** Large Language Models (LLMs) (Hurst et al., 2024; Guo et al., 2025) have achieved substantial progress in language understanding and multi-step reasoning, yielding strong performance across a broad range of downstream tasks (Cui et al., 2025; Muennighoff et al., 2025; Yan et al., 2025; Hu et al., 2025; 2026; Zhan et al., 2026; Zhang et al., 2026). Building on these advances, a growing body of research adapts LLMs to the medical domain, yielding specialized medical models that hold promise for broad healthcare fields such as question-answering, decision support, and text understanding (Chen et al., 2024; Team et al., 2025; Sounack et al., 2025). Despite pretraining on massive corpora, medical LLMs remain prone to generating fluent yet factually incorrect hallucinations (Ji et al., 2023; Kalai et al., 2025), posing critical risks in safety-sensitive healthcare scenarios (Li et al., 2025c). Meanwhile, parametric knowledge stored in model weights often becomes outdated, failing to align with emerging medical evidence or revised guidelines (Xiong et al., 2024).

**[KR]** 대규모 언어 모델(LLMs) (Hurst et al., 2024; Guo et al., 2025)은 언어 이해와 다단계 추론에서 상당한 진전을 이루었으며, 폭넓은 하위 과제 전반에서 강력한 성능을 보여 왔다 (Cui et al., 2025; Muennighoff et al., 2025; Yan et al., 2025; Hu et al., 2025; 2026; Zhan et al., 2026; Zhang et al., 2026). 이러한 발전을 바탕으로 LLM을 의료 영역에 맞추려는 연구가 점점 늘어나고 있으며, 그 결과 질의응답, 의사결정 지원, 텍스트 이해와 같은 폭넓은 의료 분야에서 가능성을 보이는 특화 의료 모델들이 등장하고 있다 (Chen et al., 2024; Team et al., 2025; Sounack et al., 2025). 방대한 코퍼스로 사전학습되었음에도, 의료 LLM들은 유창하지만 사실상 틀린 환각(hallucination)을 생성하는 경향이 여전히 남아 있어 (Ji et al., 2023; Kalai et al., 2025) 안전에 민감한 의료 시나리오에서 치명적 위험을 초래한다 (Li et al., 2025c). 한편, 모델 가중치에 저장된 매개변수적 지식(parametric knowledge)은 종종 낡아져, 새롭게 등장하는 의료 증거나 개정된 지침과 일치하지 못한다 (Xiong et al., 2024).

**[EN]** Retrieval-Augmented Generation (RAG) has become a cornerstone paradigm that leverages external, verifiable medical evidence to provide up-to-date grounding necessary for factually accurate and reliable responses (Zhao et al., 2026; Yu et al., 2025). Traditional RAG often follows a single-round workflow: retrieving evidence based solely on an initial query before generating a final response conditioned on the retrieved context (Guu et al., 2020; Izacard et al., 2021). While effective for simple questions, one-shot retrieval often fails to provide evolving information required for complex, multi-step reasoning (Jiang et al., 2023; Su et al., 2024), and can introduce irrelevant noise to degrade the performance when retrieval is not universally beneficial (Choi et al., 2025). To tackle this, adaptive RAG methods (Jiang et al., 2023; Su et al., 2024; Jiang et al., 2025) interleave generation with multi-round retrieval by dynamically determining when to trigger external searches and what queries to issue. They usually rely on token-level signals, such as confidence (Jiang et al., 2023) or attention weights (Su et al., 2024), to construct context-aware queries. However, token-level uncertainty is often a poor proxy for retrieval needs, as LLMs may hallucinate with high confidence, and uncertainty estimates are frequently dominated by trivial words instead of domain-critical medical concepts required for precise query formulation. These limitations highlight a critical question: Could we bypass the reliance on noisy token-level signals by leveraging higher-level semantic cues to steer agentic retrieval more efficiently?

**[KR]** Retrieval-Augmented Generation(RAG)은 외부의 검증 가능한 의료 증거를 활용하여 사실적으로 정확하고 신뢰할 수 있는 응답에 필요한 최신 근거(grounding)를 제공하는 핵심 패러다임으로 자리잡았다 (Zhao et al., 2026; Yu et al., 2025). 전통적 RAG는 흔히 단일 라운드(single-round) 워크플로를 따른다. 즉, 초기 쿼리만을 기반으로 증거를 검색한 뒤, 검색된 맥락을 조건으로 최종 응답을 생성한다 (Guu et al., 2020; Izacard et al., 2021). 단순한 질문에는 효과적이지만, 일회성(one-shot) 검색은 복잡한 다단계 추론에 필요한, 점진적으로 진화하는 정보를 제공하지 못하는 경우가 많고 (Jiang et al., 2023; Su et al., 2024), 검색이 항상 이로운 것은 아닐 때 관련 없는 잡음을 끌어들여 성능을 저하시킬 수 있다 (Choi et al., 2025). 이를 해결하기 위해 adaptive RAG(적응형 RAG) 방법들 (Jiang et al., 2023; Su et al., 2024; Jiang et al., 2025)은 언제 외부 검색을 촉발하고 어떤 쿼리를 발행할지를 동적으로 결정함으로써, 생성과 다중 라운드 검색을 교차시킨다. 이들은 보통 confidence(신뢰도) (Jiang et al., 2023)나 attention weight(어텐션 가중치) (Su et al., 2024)와 같은 token-level 신호에 의존하여 맥락 인지적 쿼리를 구성한다. 그러나 token-level 불확실성은 검색 필요성에 대한 빈약한 대리 지표인 경우가 많다. LLM은 높은 신뢰도로 환각을 일으킬 수 있고, 불확실성 추정치는 정밀한 쿼리 구성에 필요한 도메인 핵심 의료 개념이 아니라 사소한 단어들에 의해 좌우되는 경우가 잦기 때문이다. 이러한 한계는 다음의 핵심 질문을 부각한다. 더 상위 수준의 의미적 단서(semantic cue)를 활용하여 agentic 검색을 더 효율적으로 유도함으로써, 잡음이 많은 token-level 신호에 대한 의존을 우회할 수 있을까?

**[EN]** In medical domains, complex cases often elicit conflicting explanations or diagnoses when the model lacks sufficient evidence. The semantic conflict among multiple reasoning paths can provide a more grounded signal to identify where current knowledge is insufficient and retrieval augmentation is essential. By iteratively rectifying these conflicts through external evidence, the agentic loop acts as a refinement process that reconciles disparate reasoning paths into a reliable, high-fidelity consensus. This mechanism naturally aligns with principles of human cognitive science (Flavell, 1979), wherein individuals iteratively seek external validation or peer expertise to reduce inconsistencies.

**[KR]** 의료 영역에서는 모델이 충분한 증거를 갖지 못할 때 복잡한 사례가 종종 상충하는 설명이나 진단을 유발한다. 여러 추론 경로(reasoning path) 사이의 semantic conflict는 현재 지식이 부족하고 검색 증강이 필수적인 지점을 식별하는, 보다 근거 있는 신호를 제공할 수 있다. 외부 증거를 통해 이러한 충돌을 반복적으로 바로잡음으로써, agentic loop는 서로 다른 추론 경로들을 신뢰할 수 있고 충실도가 높은 합의로 조율하는 정교화 과정(refinement process)으로 작동한다. 이 메커니즘은 사람들이 불일치를 줄이기 위해 외부의 검증이나 동료 전문성을 반복적으로 구하는, 인간 인지과학(human cognitive science)의 원리 (Flavell, 1979)와 자연스럽게 부합한다.

**[EN]** Inspired by the above insights, we propose MA-RAG (Multi-Round Agentic RAG), an agentic refinement process that steers test-time scaling for complex medical reasoning by iteratively evolving both external retrieval documents and internal reasoning history. Concretely, our pipeline consists of three agents: i) a Solver Agent that produces multiple candidate responses per round; ii) a Retrieval Agent that transforms semantic conflict among candidates into actionable retrieval queries to seek external evidence from a local medical corpus; and iii) a Ranking Agent that optimizes history reasoning traces by prioritizing top-tier candidates, mitigating long-context degradation. MA-RAG extends the self-consistency principle by leveraging semantic inconsistency as a proactive signal for multi-round agentic reasoning and retrieval, and mirrors a boosting mechanism that iteratively minimizes residual errors (see Sec. 3.5).

**[KR]** 위와 같은 통찰에서 영감을 받아, 우리는 외부 검색 문서와 내부 추론 이력을 반복적으로 진화시켜 복잡한 의료 추론에 대한 test-time scaling을 유도하는 agentic refinement 과정인 MA-RAG(Multi-Round Agentic RAG)를 제안한다. 구체적으로, 우리의 파이프라인은 세 개의 에이전트로 구성된다. i) 라운드마다 여러 후보 응답을 생성하는 Solver Agent, ii) 후보들 사이의 semantic conflict를 실행 가능한 검색 쿼리로 변환하여 로컬 의료 코퍼스에서 외부 증거를 찾는 Retrieval Agent, iii) 상위권 후보들을 우선순위화하여 이력 추론 자취를 최적화하고 long-context degradation을 완화하는 Ranking Agent. MA-RAG는 의미적 비일관성(semantic inconsistency)을 다중 라운드 agentic 추론 및 검색을 위한 능동적 신호로 활용함으로써 self-consistency 원리를 확장하며, 잔차 오류를 반복적으로 최소화하는 boosting 메커니즘을 반영한다(3.5절 참조).

**[EN]** Extensive experiments across seven medical Q&A benchmarks demonstrate MA-RAG’s consistent superiority over competitive test-time-scaling and RAG baselines. Notably, MA-RAG achieves substantial +6.8 points on average accuracy over the backbone model. The performance gain is particularly pronounced on harder benchmarks (e.g., a 37% relative improvement over baselines on MedXpertQA) that require information-dense queries and sophisticated reasoning, highlighting our advantage in complex medical reasoning. Comprehensive analysis and case studies reveal that MA-RAG demonstrates robust performance during multi-round refinement and effectively steers test-time scaling.

**[KR]** 7개 의료 Q&A 벤치마크에 걸친 광범위한 실험은 MA-RAG가 경쟁력 있는 test-time-scaling 및 RAG 베이스라인 대비 일관된 우위를 가짐을 입증한다. 특히 MA-RAG는 백본 모델 대비 평균 정확도에서 +6.8점이라는 상당한 향상을 달성한다. 이 성능 향상은 정보 밀도가 높은 쿼리와 정교한 추론을 요하는 더 어려운 벤치마크(예: MedXpertQA에서 베이스라인 대비 37%의 상대적 개선)에서 특히 두드러지며, 이는 복잡한 의료 추론에서의 우리 방법의 강점을 부각한다. 포괄적 분석과 사례 연구는 MA-RAG가 다중 라운드 정교화 과정에서 견고한 성능을 보이며 test-time scaling을 효과적으로 유도함을 드러낸다.

---

## §2 Related Work

### RAG for Medical Reasoning

**[EN]** RAG (Lewis et al., 2020) enhances LLMs by incorporating external knowledge, demonstrating significant potential for mitigating hallucinations in risk-sensitive medical domains (Xiong et al., 2024; Matsumoto et al., 2024; Zhao et al., 2026). Traditional retrieval-and-generation often retrieves redundant and noisy information, and struggles with complex, multi-hop reasoning tasks (Jiang et al., 2023; Su et al., 2024; Jiang et al., 2025). To address this, adaptive RAG dynamically determines when and what to retrieve. FLARE (Jiang et al., 2023) and DRAGIN (Su et al., 2024) leverage internal signals, specifically low-confidence tokens or attention weights, to trigger retrieval. Other methods perform adaptive retrieval via query complexity classification (Jeong et al., 2024), state-managed processing (Jiang et al., 2025), or conflict mitigation by filtering or reconciling retrieved evidence (Choi et al., 2025; Zhang et al., 2025b; Wang et al., 2025). Despite these advancements, existing methods often rely on noisy token-level metrics (e.g., entropy), which may be unreliable due to the model’s over-confidence (Kalai et al., 2025). In contrast, we use semantic conflict as a high-level, grounded signal to guide adaptive retrieval.

**[KR]** RAG (Lewis et al., 2020)는 외부 지식을 통합하여 LLM을 강화하며, 위험에 민감한 의료 영역에서 환각을 완화하는 데 상당한 잠재력을 보여 왔다 (Xiong et al., 2024; Matsumoto et al., 2024; Zhao et al., 2026). 전통적 검색-생성 방식은 중복되고 잡음이 많은 정보를 검색하는 경우가 많으며, 복잡한 multi-hop(다중 도약) 추론 과제에서 어려움을 겪는다 (Jiang et al., 2023; Su et al., 2024; Jiang et al., 2025). 이를 해결하기 위해 adaptive RAG는 언제, 무엇을 검색할지를 동적으로 결정한다. FLARE (Jiang et al., 2023)와 DRAGIN (Su et al., 2024)은 내부 신호, 구체적으로는 신뢰도가 낮은 토큰이나 어텐션 가중치를 활용하여 검색을 촉발한다. 다른 방법들은 쿼리 복잡도 분류(query complexity classification) (Jeong et al., 2024), 상태 관리 처리(state-managed processing) (Jiang et al., 2025), 또는 검색된 증거를 필터링하거나 조정하여 충돌을 완화하는 방식 (Choi et al., 2025; Zhang et al., 2025b; Wang et al., 2025)을 통해 적응형 검색을 수행한다. 이러한 발전에도 불구하고, 기존 방법들은 잡음이 많은 token-level 지표(예: entropy)에 의존하는 경우가 많은데, 이는 모델의 과신(over-confidence)으로 인해 신뢰하기 어려울 수 있다 (Kalai et al., 2025). 이와 대조적으로, 우리는 semantic conflict를 상위 수준의 근거 있는 신호로 사용하여 적응형 검색을 유도한다.

### Test-Time Scaling

**[EN]** It emerges as a promising paradigm to enhance LLM reliability by allocating increasing compute during inference, consisting of parallel scaling and sequential scaling. Parallel scaling samples diverse reasoning paths independently and aggregates them to form a consensus using unsupervised mechanisms like majority voting (Wang et al., 2023; Chen et al., 2026). MedAdapter (Shi et al., 2024) and MedS3 (Jiang et al., 2026) train specific verifiers to select higher-quality responses in medical domains. Sequential scaling extends the reasoning to multi-round settings that utilize feedback from previous generations, achieving notable progress like OpenAI o1 (Jaech et al., 2024) and DeepSeek-R1 (Guo et al., 2025). Recent studies formulate generation as an iterative process of self-refinement (Tian et al., 2025; Xu et al., 2025; Li et al., 2025b;a), prompting models to critique and revise their own outputs (Madaan et al., 2023; Shinn et al., 2023). Based on this sequential paradigm, we propose an agentic refinement process to facilitate test-time scaling for complex medical reasoning.

**[KR]** Test-Time Scaling은 추론 시점에 점점 더 많은 연산을 할당하여 LLM의 신뢰성을 높이는 유망한 패러다임으로 부상했으며, parallel scaling(병렬 확장)과 sequential scaling(순차 확장)으로 구성된다. Parallel scaling은 다양한 추론 경로를 독립적으로 샘플링한 뒤, majority voting(다수결 투표) 같은 비지도 메커니즘을 사용하여 이를 집계해 합의를 형성한다 (Wang et al., 2023; Chen et al., 2026). MedAdapter (Shi et al., 2024)와 MedS3 (Jiang et al., 2026)는 의료 영역에서 더 높은 품질의 응답을 선택하기 위해 전용 verifier(검증기)를 학습시킨다. Sequential scaling은 이전 생성 결과의 피드백을 활용하는 다중 라운드 설정으로 추론을 확장하여, OpenAI o1 (Jaech et al., 2024)이나 DeepSeek-R1 (Guo et al., 2025)과 같은 주목할 만한 진전을 이루었다. 최근 연구들은 생성을 self-refinement(자기 정교화)의 반복 과정으로 정식화하여 (Tian et al., 2025; Xu et al., 2025; Li et al., 2025b;a), 모델이 스스로의 출력을 비판하고 수정하도록 유도한다 (Madaan et al., 2023; Shinn et al., 2023). 이러한 순차적 패러다임을 토대로, 우리는 복잡한 의료 추론에 대한 test-time scaling을 촉진하는 agentic refinement 과정을 제안한다.

---

## §3 Method

**[EN]** In this section, we present MA-RAG in detail, focusing on the agentic refinement process comprising the solver, retrieval, and ranking agents. Figure 2 illustrates the overall pipeline, and Appendix A shows the pseudocode.

**[KR]** 본 절에서는 solver, retrieval, ranking 에이전트로 구성된 agentic refinement 과정을 중심으로 MA-RAG를 상세히 제시한다. Figure 2는 전체 파이프라인을 보여주며, Appendix A는 의사코드(pseudocode)를 제시한다.

### 3.1. Problem Statement

**[EN]** We formulate our multi-round adaptive RAG process as an iterative context optimization problem (Mei et al., 2025). The LLM’s prompt is treated as a dynamic, evolving structure rather than a static sequence, allowing the context to adaptively mature over successive rounds. Let $M$ and $A_t$ denote the LLM and the set of generated responses at round $t \in \{1, \ldots, T\}$. For a given query $q$, the input state $S_t$ at the $t$-th round is defined as a composite tuple:

**[KR]** 우리는 다중 라운드 adaptive RAG 과정을 반복적 맥락 최적화(iterative context optimization) 문제로 정식화한다 (Mei et al., 2025). LLM의 프롬프트는 정적 시퀀스가 아니라 동적으로 진화하는 구조로 취급되어, 맥락이 연속된 라운드를 거치며 적응적으로 성숙할 수 있게 한다. $M$과 $A_t$를 각각 LLM과 라운드 $t \in \{1, \ldots, T\}$에서 생성된 응답 집합이라 하자. 주어진 쿼리 $q$에 대해, $t$번째 라운드의 입력 상태 $S_t$는 다음의 복합 튜플로 정의된다.

**[EN]**
$$S_t = \{I, q, D_t, H_t\}, \tag{1}$$
which contains the following components:

**[KR]**
$$S_t = \{I, q, D_t, H_t\}, \tag{1}$$
이는 다음의 구성 요소들을 포함한다.

**[EN]**
- $I$ represents the Task Instruction, which is invariant.
- $D_t$ denotes the Document Context, a dynamic set of medical passages retrieved to ground the model’s reasoning. Unlike static single-round retrieval, $D_t$ evolves through successive rounds, continuously updating the initial evidence pool with newly retrieved data.
- $H_t = \text{Rank}(A_{t-1})$ is the History Context, a collection of candidate responses in the previous round. Rather than a simple concatenation of prior responses, $H_t$ is a structured repository that is strategically ranked and organized to maximize its utility as a sequence of high-quality in-context demonstrations (refer to Sec. 3.4).

**[KR]**
- $I$는 Task Instruction(과제 지시문)을 나타내며, 변하지 않는다.
- $D_t$는 Document Context(문서 맥락)를 가리키며, 모델의 추론을 뒷받침하기 위해 검색된 의료 지문(passage)들의 동적 집합이다. 정적인 단일 라운드 검색과 달리, $D_t$는 연속된 라운드를 거치며 진화하여, 새롭게 검색된 데이터로 초기 증거 풀(evidence pool)을 지속적으로 갱신한다.
- $H_t = \text{Rank}(A_{t-1})$는 History Context(이력 맥락)로, 이전 라운드의 후보 응답들의 모음이다. 이전 응답들을 단순히 이어붙인 것이 아니라, $H_t$는 고품질의 in-context demonstration(맥락 내 시연) 시퀀스로서의 유용성을 극대화하도록 전략적으로 순위가 매겨지고 조직화된 구조화 저장소이다(3.4절 참조).

**[EN]** Central to our agentic refinement loop is how to effectively transition state $S_t$ to the new round $S_{t+1}$, a process designed to iteratively optimize the context toward eliciting a robust, high-quality answer. Specifically, we utilize the semantic conflict within $A_t$ to guide the retrieval of $D_{t+1}$ (i.e., resolving what to retrieve) and organize the structure of $H_{t+1}$ (i.e., determining how to present history) to elicit higher-quality responses in the subsequent round. This mirrors a boosting mechanism (Schapire, 1990; Chen et al., 2016) that compels each round to focus on “hard cases” and rectify prior residual errors through retrieving external evidence. Sec. 3.5 elaborates our theoretical grounding in the principle of classical boosting algorithms.

**[KR]** 우리의 agentic refinement loop의 핵심은 상태 $S_t$를 새로운 라운드 $S_{t+1}$로 효과적으로 전이시키는 방법이며, 이 과정은 견고하고 고품질의 답변을 이끌어내는 방향으로 맥락을 반복적으로 최적화하도록 설계되었다. 구체적으로, 우리는 $A_t$ 내의 semantic conflict를 활용하여 $D_{t+1}$의 검색을 유도하고(즉, 무엇을 검색할지를 결정하고), 후속 라운드에서 더 높은 품질의 응답을 이끌어내기 위해 $H_{t+1}$의 구조를 조직한다(즉, 이력을 어떻게 제시할지를 결정한다). 이는 각 라운드가 "어려운 사례(hard cases)"에 집중하고 외부 증거를 검색함으로써 이전의 잔차 오류를 바로잡도록 강제하는 boosting 메커니즘 (Schapire, 1990; Chen et al., 2016)을 반영한다. 3.5절에서는 고전적 boosting 알고리즘의 원리에 기반한 우리의 이론적 근거를 상세히 설명한다.

### 3.2. Solver Agent

**[EN]** The solver agent acts as the primary reasoning engine, navigating the solution space while identifying latent uncertainties within the model’s internal knowledge. At round $t$, conditioned on the current state $S_t$, the agent performs stochastic exploration of the solution space via temperature-controlled sampling and generates a diverse set of $N$ candidate responses $A_t$ as

**[KR]** solver agent는 주된 추론 엔진(reasoning engine) 역할을 하며, 모델의 내부 지식 내에 잠재된 불확실성을 식별하면서 해 공간(solution space)을 탐색한다. 라운드 $t$에서, 현재 상태 $S_t$를 조건으로 하여, 에이전트는 temperature 제어 샘플링(temperature-controlled sampling)을 통해 해 공간을 확률적으로 탐색하고 다양한 $N$개의 후보 응답 $A_t$를 다음과 같이 생성한다.

**[EN]**
$$A_t = \{a_t^1, a_t^2, \ldots, a_t^N\} \sim M(I_{\text{solver}}, q, D_t, H_t). \tag{2}$$

**[KR]**
$$A_t = \{a_t^1, a_t^2, \ldots, a_t^N\} \sim M(I_{\text{solver}}, q, D_t, H_t). \tag{2}$$

**[EN]** The diversity within candidate generations $A_t$ is fundamental to our framework, grounded in the empirical insight that accurate reasoning chains tend to converge toward a stable consensus, while hallucinations often exhibit divergent inconsistencies (Manakul et al., 2023; Chen et al., 2026). This observation naturally aligns with the core principle of self-consistency decoding (Wang et al., 2023) that complex reasoning tasks typically admit multiple reasoning paths toward a correct consensus, which is elaborated in Sec. 3.5. Leveraging this signal, subsequent agents formulate conflict-guided queries for directed retrieval and rank history reasoning traces to enhance in-context learning, boosting the solver agent toward progressively higher-fidelity responses. When yielding consistent responses, we denote this as reasoning convergence and terminate the agentic refinement loop, aggregating the consensus to produce the final answer.

**[KR]** 후보 생성물 $A_t$ 내의 다양성은 우리 프레임워크의 근간을 이루며, 정확한 추론 사슬(reasoning chain)은 안정적 합의로 수렴하는 경향이 있는 반면 환각은 흔히 발산적 비일관성을 보인다는 경험적 통찰에 기반한다 (Manakul et al., 2023; Chen et al., 2026). 이 관찰은 복잡한 추론 과제가 일반적으로 올바른 합의를 향한 여러 추론 경로를 허용한다는 self-consistency 디코딩(self-consistency decoding)의 핵심 원리 (Wang et al., 2023)와 자연스럽게 부합하며, 이는 3.5절에서 상세히 다룬다. 이 신호를 활용하여, 후속 에이전트들은 지향적(directed) 검색을 위한 conflict-guided 쿼리(충돌 기반 쿼리)를 구성하고 in-context learning을 강화하기 위해 이력 추론 자취의 순위를 매기며, 이를 통해 solver agent를 점진적으로 더 높은 충실도의 응답으로 부스팅한다. 응답들이 일관되게 나타날 때, 우리는 이를 reasoning convergence(추론 수렴)라 칭하고 agentic refinement loop를 종료한 뒤, 합의를 집계하여 최종 답변을 생성한다.

### 3.3. Retrieval Agent

**[EN]** Recent adaptive RAG approaches leverage internal signals like token-level uncertainty for dynamic retrieval (Jiang et al., 2023; Su et al., 2024); however, such metrics are often undermined by the tendency of LLMs to generate hallucinations with over-confidence (Kalai et al., 2025). In medical domains, complex cases usually induce conflicting diagnoses when the model lacks sufficient evidence. The semantic conflict among multiple reasoning paths can serve as a more reliable diagnostic, pinpointing knowledge gaps where retrieval augmentation is most critical. This aligns with human intelligence, wherein people will iteratively seek external evidence or peer expertise to reconcile inconsistencies, especially in risk-sensitive healthcare fields.

**[KR]** 최근의 adaptive RAG 접근들은 동적 검색을 위해 token-level 불확실성과 같은 내부 신호를 활용한다 (Jiang et al., 2023; Su et al., 2024). 그러나 이러한 지표는 LLM이 과신을 가지고 환각을 생성하는 경향에 의해 종종 훼손된다 (Kalai et al., 2025). 의료 영역에서는 모델이 충분한 증거를 갖지 못할 때 복잡한 사례가 대개 상충하는 진단을 유발한다. 여러 추론 경로 사이의 semantic conflict는 보다 신뢰할 수 있는 진단 지표가 될 수 있으며, 검색 증강이 가장 중요한 지식 격차(knowledge gap)를 정확히 짚어낸다. 이는, 특히 위험에 민감한 의료 분야에서 사람들이 불일치를 조정하기 위해 외부 증거나 동료 전문성을 반복적으로 구하는 인간 지능(human intelligence)과 부합한다.

**[EN]** Based on this insight, we propose a retrieval agent that leverages semantic conflict within the candidate set $A_t$ as a reliable indicator for the model’s current knowledge gap, and transforms that signal into actionable queries to efficiently retrieve external evidence. The underlying premise is that sufficient knowledge and reasoning capacity lead to self-consistency across multiple independent generations, whereas conflict signals a critical deficiency in grounded evidence. At each round, the agent extracts candidate conflicts (e.g., inconsistent diagnoses or symptom interpretations) as $I_{\text{conflict}}$, followed by formulating a set of $K$ targeted retrieval queries $R_t$ aimed to rectify these specific conflicts:

**[KR]** 이러한 통찰을 바탕으로, 우리는 후보 집합 $A_t$ 내의 semantic conflict를 모델의 현재 지식 격차에 대한 신뢰할 수 있는 지표로 활용하고, 그 신호를 실행 가능한 쿼리로 변환하여 외부 증거를 효율적으로 검색하는 retrieval agent를 제안한다. 그 근간을 이루는 전제는, 충분한 지식과 추론 능력은 여러 독립적 생성물 전반에서 self-consistency로 이어지는 반면, 충돌은 근거 있는 증거의 치명적 결핍을 신호한다는 것이다. 매 라운드마다 에이전트는 후보들 간의 충돌(예: 일관되지 않은 진단이나 증상 해석)을 $I_{\text{conflict}}$로 추출한 뒤, 이러한 특정 충돌을 바로잡기 위한 $K$개의 표적화된(targeted) 검색 쿼리 집합 $R_t$를 구성한다.

**[EN]**
$$R_t = \{r_t^1, r_t^2, \ldots, r_t^K\} \sim M(I_{\text{conflict}}, q, A_t). \tag{3}$$

**[KR]**
$$R_t = \{r_t^1, r_t^2, \ldots, r_t^K\} \sim M(I_{\text{conflict}}, q, A_t). \tag{3}$$

**[EN]** Then, the agent executes these conflict-aware queries against the external medical corpus to fetch new evidence $D_{t+1}$, progressively narrowing the knowledge gap and providing the solver agent with augmented evidence required to rectify previous inconsistencies in subsequent rounds.

**[KR]** 그런 다음 에이전트는 이러한 conflict-aware 쿼리(충돌 인지 쿼리)를 외부 의료 코퍼스에 대해 실행하여 새로운 증거 $D_{t+1}$를 가져오고, 지식 격차를 점진적으로 좁히면서, 후속 라운드에서 이전의 비일관성을 바로잡는 데 필요한 증강된 증거를 solver agent에게 제공한다.

### 3.4. Ranking Agent

**[EN]** A significant bottleneck in sequential test-time scaling is long-context degradation (Mei et al., 2025), specifically the “lost-in-the-middle” issue, where models may overlook critical reasoning cues situated centrally within an expanding prompt (Zhang et al., 2025a). The refinement process is not only about augmenting more external evidence, but also optimizing the context to enhance in-context learning.

**[KR]** 순차적 test-time scaling에서 두드러진 병목은 long-context degradation (Mei et al., 2025), 구체적으로는 "lost-in-the-middle"(중간에서 길을 잃는) 문제이다. 이는 모델이 점점 늘어나는 프롬프트의 중앙부에 위치한 핵심 추론 단서를 간과할 수 있는 현상이다 (Zhang et al., 2025a). 정교화 과정은 더 많은 외부 증거를 증강하는 것뿐만 아니라, in-context learning을 강화하기 위해 맥락을 최적화하는 것이기도 하다.

**[EN]** Based on this insight, we propose a ranking agent to restructure history reasoning traces, functioning as a context optimizer. The ranking agent uses a score function $Q(\cdot)$ to evaluate the quality of candidate responses in the previous round $A_{t-1}$, and constructs the history context $H_t$ as

**[KR]** 이러한 통찰을 바탕으로, 우리는 맥락 최적화기(context optimizer)로 기능하며 이력 추론 자취를 재구조화하는 ranking agent를 제안한다. ranking agent는 점수 함수(score function) $Q(\cdot)$를 사용하여 이전 라운드 $A_{t-1}$의 후보 응답 품질을 평가하고, 이력 맥락 $H_t$를 다음과 같이 구성한다.

**[EN]**
$$H_t = \text{sort}\,(A_{t-1}, \text{key}=Q) = \left(a_{t-1}^{(1)}, a_{t-1}^{(2)}, \ldots, a_{t-1}^{(N)}\right), \tag{4}$$
where the indices are reordered such that the quality scores follow a descending order as $Q(a_{t-1}^{(1)}) \geq Q(a_{t-1}^{(2)}) \geq \cdots \geq Q(a_{t-1}^{(N)})$. This ensures that promising reasoning traces serve as prioritized demonstrations, effectively mitigating the long-context degradation issue. We use two representative scoring functions as follows.

**[KR]**
$$H_t = \text{sort}\,(A_{t-1}, \text{key}=Q) = \left(a_{t-1}^{(1)}, a_{t-1}^{(2)}, \ldots, a_{t-1}^{(N)}\right), \tag{4}$$
여기서 인덱스들은 품질 점수가 $Q(a_{t-1}^{(1)}) \geq Q(a_{t-1}^{(2)}) \geq \cdots \geq Q(a_{t-1}^{(N)})$와 같이 내림차순을 따르도록 재정렬된다. 이는 유망한 추론 자취가 우선순위가 부여된 시연으로 기능하도록 보장하여, long-context degradation 문제를 효과적으로 완화한다. 우리는 다음의 두 가지 대표적 점수 함수를 사용한다.

**[EN]** Intrinsic Uncertainty. As entropy often serves as a simple, cheap metric for estimating generation quality (Manakul et al., 2023; Jiang et al., 2025; Sharma et al., 2025), we compute the sequence-level entropy as the score function for evaluating each response $a \in A_{t-1}$:

**[KR]** Intrinsic Uncertainty(내재적 불확실성). entropy는 생성 품질을 추정하는 간단하고 저렴한 지표로 흔히 쓰이므로 (Manakul et al., 2023; Jiang et al., 2025; Sharma et al., 2025), 우리는 각 응답 $a \in A_{t-1}$을 평가하는 점수 함수로서 시퀀스 수준 entropy(sequence-level entropy)를 계산한다.

**[EN]**
$$Q_{\text{int}}(a) = -\frac{1}{L}\sum_{i=1}^{L} \text{entropy}\big(P(x_i \mid x_{<i}, S_t)\big), \tag{5}$$
where $x_i$ is the $i$-th token in response $a$, $x_{<i}$ is the sequence before $x_i$, and $L$ is the length of response $a$.

**[KR]**
$$Q_{\text{int}}(a) = -\frac{1}{L}\sum_{i=1}^{L} \text{entropy}\big(P(x_i \mid x_{<i}, S_t)\big), \tag{5}$$
여기서 $x_i$는 응답 $a$의 $i$번째 토큰, $x_{<i}$는 $x_i$ 이전의 시퀀스, $L$은 응답 $a$의 길이이다.

**[EN]** Extrinsic Verification. Beyond the token-level statistics, we design a higher-level score function that uses an auxiliary verifier to capture semantic correctness, specifically a lightweight BERT-based evaluator $V_\theta$. The model is fine-tuned as a binary classifier on a dataset of query-response pairs $D_{qa} = \{(q_i, a_i)\}_{i=1}^{M}$ using a cross-entropy loss:

**[KR]** Extrinsic Verification(외재적 검증). token-level 통계를 넘어, 우리는 의미적 정확성을 포착하기 위해 보조 verifier를 사용하는 상위 수준 점수 함수, 구체적으로는 경량 BERT 기반 evaluator(평가기) $V_\theta$를 설계한다. 이 모델은 쿼리-응답 쌍 데이터셋 $D_{qa} = \{(q_i, a_i)\}_{i=1}^{M}$에 대해 cross-entropy 손실(cross-entropy loss)을 사용하여 이진 분류기(binary classifier)로 미세조정(fine-tune)된다.

**[EN]**
$$L(\theta) = -\frac{1}{M}\sum_{i=1}^{M} y_i \log(s_i) + (1-y_i)\log(1-s_i), \tag{6}$$
where $y_i$ is the ground truth, and $s_i = \sigma(V_\theta(q_i, a_i))$ is the predicted probability. During inference, we use the fine-tuned verifier to compute the score function for $a \in A_{t-1}$:

**[KR]**
$$L(\theta) = -\frac{1}{M}\sum_{i=1}^{M} y_i \log(s_i) + (1-y_i)\log(1-s_i), \tag{6}$$
여기서 $y_i$는 정답(ground truth)이고, $s_i = \sigma(V_\theta(q_i, a_i))$는 예측 확률이다. 추론 시에는 미세조정된 verifier를 사용하여 $a \in A_{t-1}$에 대한 점수 함수를 계산한다.

**[EN]**
$$Q_{\text{ext}}(a) = V_\theta(q, a). \tag{7}$$
Appendix E presents details of constructing the dataset $D_{qa}$ and fine-tuning the external verifier.

**[KR]**
$$Q_{\text{ext}}(a) = V_\theta(q, a). \tag{7}$$
Appendix E는 데이터셋 $D_{qa}$를 구성하고 외부 verifier를 미세조정하는 세부 사항을 제시한다.

### 3.5. Theoretical Grounding in Classic Principles

**[EN]** From Static to Adaptive Self-Consistency. Self-consistency (Wang et al., 2023) is a simple, classical decoding strategy that achieves a striking margin on chain-of-thought reasoning. Standard self-consistency simply takes a majority vote to select the most consistent answer, assuming the model’s internal knowledge is sufficient to reach a consensus in a single round. The mathematical objective is:

**[KR]** 정적(static)에서 적응적(adaptive) Self-Consistency로. Self-consistency (Wang et al., 2023)는 chain-of-thought(사고 사슬) 추론에서 두드러진 차이를 달성하는 간단하고 고전적인 디코딩 전략이다. 표준 self-consistency는 단순히 다수결 투표를 취해 가장 일관된 답을 선택하며, 모델의 내부 지식이 단일 라운드 내에서 합의에 도달하기에 충분하다고 가정한다. 그 수학적 목적함수는 다음과 같다.

**[EN]**
$$\max_a \sum_{i=1}^{N} \frac{1}{N}\cdot \mathbb{1}(a_i = a). \tag{8}$$

**[KR]**
$$\max_a \sum_{i=1}^{N} \frac{1}{N}\cdot \mathbb{1}(a_i = a). \tag{8}$$

**[EN]** MA-RAG extends this principle by leveraging semantic “inconsistency” as a signal to keep thinking and retrieving in a multi-round setting. While MA-RAG optimizes the same objective in Eq. 8, it introduces a confidence threshold $\epsilon$ as a gating mechanism. If the maximum consistency probability falls below $\epsilon$, the agent triggers external retrieval to rectify the conflict in the next round. This transforms static self-consistency into an adaptive scaling mechanism: if current responses do not converge to a stable consensus, the agent triggers an additional round of retrieval, efficiently scaling test-time compute only when needed.

**[KR]** MA-RAG는 의미적 "비일관성(inconsistency)"을 다중 라운드 설정에서 계속 사고하고 검색하도록 하는 신호로 활용함으로써 이 원리를 확장한다. MA-RAG는 식 (8)과 동일한 목적함수를 최적화하지만, 게이팅 메커니즘(gating mechanism)으로서 신뢰도 임계값(confidence threshold) $\epsilon$을 도입한다. 최대 일관성 확률(maximum consistency probability)이 $\epsilon$ 미만으로 떨어지면, 에이전트는 다음 라운드에서 충돌을 바로잡기 위해 외부 검색을 촉발한다. 이는 정적 self-consistency를 적응적 확장 메커니즘(adaptive scaling mechanism)으로 변환한다. 즉, 현재 응답들이 안정적 합의로 수렴하지 못하면 에이전트는 추가 검색 라운드를 촉발하여, 필요할 때에만 test-time 연산을 효율적으로 확장한다.

**[EN]** Semantic Conflict as a Boosting Residual. Classical boosting algorithms (Friedman, 2001; Chen et al., 2016) train each successive weak learner to minimize the “residual error” left by the previous learners. Analogously, MA-RAG frames the semantic conflict identified in round $t$ as a “boosting residual”, a knowledge gap that remains unsolvable given the current state $S_t$. The solver agent diagnoses the gradient direction from the residuals found in candidate responses, while the retrieval and ranking agents provide the external evidence and contextual optimization required to “fit” this residual. By incorporating this feedback into state $S_{t+1}$, MA-RAG performs sequential refinement of the reasoning path. This boosting mechanism iteratively minimizes the “loss” (semantic conflict) until the system converges to a strong-learner state characterized by a stable, high-fidelity consensus across all reasoning trajectories.

**[KR]** Boosting Residual로서의 Semantic Conflict. 고전적 boosting 알고리즘 (Friedman, 2001; Chen et al., 2016)은 각각의 후속 약한 학습기(weak learner)가 이전 학습기들이 남긴 "잔차 오류(residual error)"를 최소화하도록 학습시킨다. 이와 유사하게, MA-RAG는 라운드 $t$에서 식별된 semantic conflict를 "boosting residual", 즉 현재 상태 $S_t$가 주어졌을 때 풀리지 않은 채 남아 있는 지식 격차로 간주한다. solver agent는 후보 응답에서 발견된 잔차로부터 기울기 방향(gradient direction)을 진단하고, retrieval 및 ranking 에이전트는 이 잔차를 "적합(fit)"시키는 데 필요한 외부 증거와 맥락적 최적화를 제공한다. 이 피드백을 상태 $S_{t+1}$에 통합함으로써, MA-RAG는 추론 경로의 순차적 정교화(sequential refinement)를 수행한다. 이 boosting 메커니즘은 시스템이 모든 추론 궤적(reasoning trajectory) 전반에서 안정적이고 충실도가 높은 합의로 특징지어지는 강한 학습기(strong-learner) 상태로 수렴할 때까지 "손실(loss)"(즉, semantic conflict)을 반복적으로 최소화한다.

---

## §4 Experiments

**[EN]** In this section, we present a comprehensive evaluation of MA-RAG on a diverse set of seven medical reasoning benchmarks, aiming to answer the following research questions:

**[KR]** 본 절에서는 다양한 7개 의료 추론 벤치마크에 대한 MA-RAG의 포괄적 평가를 제시하며, 다음의 연구 질문들에 답하는 것을 목표로 한다.

**[EN]**
- Can MA-RAG achieve consistent superiority on diverse benchmarks compared to competitive test-time scaling and RAG baselines? (Sec. 4.1)
- Can conflict-guided retrieval pinpoint knowledge gaps to rectify inconsistencies, and can ranking-based context optimization enhance in-context learning? (Sec. 4.2)
- Can MA-RAG steer efficient test-time scaling w.r.t. refinement rounds $T$, candidate numbers $N$ (Sec. 4.3), and backbone model capabilities? (Sec. 4.4)
- How does MA-RAG compare against competitive baselines in terms of end-to-end inference efficiency? (Sec. 4.5)

**[KR]**
- MA-RAG가 경쟁력 있는 test-time scaling 및 RAG 베이스라인 대비 다양한 벤치마크에서 일관된 우위를 달성할 수 있는가? (4.1절)
- conflict-guided 검색이 비일관성을 바로잡기 위해 지식 격차를 정확히 짚어낼 수 있으며, ranking 기반 맥락 최적화가 in-context learning을 강화할 수 있는가? (4.2절)
- MA-RAG가 정교화 라운드 $T$, 후보 수 $N$ (4.3절), 그리고 백본 모델 능력 (4.4절)과 관련하여 효율적인 test-time scaling을 유도할 수 있는가?
- end-to-end 추론 효율성 측면에서 MA-RAG는 경쟁력 있는 베이스라인들과 어떻게 비교되는가? (4.5절)

**[EN]** Datasets. We evaluate on seven medical Q&A benchmarks: MedQA (USMLE) (Jin et al., 2021), MedMCQA (Pal et al., 2022), MedExpQA (EN) (Alonso et al., 2024), Medbullets (5 options) (Chen et al., 2025), NEJM (Katz et al., 2024), the medical subset of MMLU-Pro (Wang et al., 2024), and MedXpertQA (Text) (Zuo et al., 2025). These datasets cover a broad spectrum of difficulty levels, ranging from standard medical licensing examinations to complex, expert-level clinical reasoning requiring multi-step information augmentation. See Appendix B for more details.

**[KR]** 데이터셋. 우리는 7개 의료 Q&A 벤치마크에서 평가한다: MedQA (USMLE) (Jin et al., 2021), MedMCQA (Pal et al., 2022), MedExpQA (EN) (Alonso et al., 2024), Medbullets (5지선다) (Chen et al., 2025), NEJM (Katz et al., 2024), MMLU-Pro의 의료 부분집합 (Wang et al., 2024), 그리고 MedXpertQA (Text) (Zuo et al., 2025). 이 데이터셋들은 표준 의사 면허 시험에서부터 다단계 정보 증강을 요하는 복잡한 전문가 수준의 임상 추론에 이르기까지, 폭넓은 난이도 스펙트럼을 포괄한다. 더 자세한 내용은 Appendix B를 참조하라.

**[EN]** Baselines. We compare MA-RAG to 13 baselines that cover 5 representative paradigms for medical reasoning:

**[KR]** 베이스라인. 우리는 MA-RAG를 의료 추론을 위한 5가지 대표 패러다임을 아우르는 13개의 베이스라인과 비교한다.

**[EN]**
- 4 Backbones: Qwen3-8B (Yang et al., 2025), Llama-3.1-8B-Instruct (Grattafiori et al., 2024), and specialized medical LLMs of UltraMedical-3.1-8B (Zhang et al., 2024) and HuatuoGPT-o1-8B (Chen et al., 2024);
- 3 Test-time scaling methods without retrieval: CoT (Chain-of-Thought) (Wei et al., 2022), SC (Self-Consistency) (Wang et al., 2023), and Multi-Refine (Tian et al., 2025; Xu et al., 2025);
- 3 Naive RAG methods: SR-RAG (Single-Round RAG) (Xiong et al., 2024), FL-RAG (Fixed-Length RAG) (Borgeaud et al., 2022; Ram et al., 2023), and FS-RAG (Fixed-Sentence RAG) (Trivedi et al., 2023);
- 2 Adaptive RAG methods: FLARE (Jiang et al., 2023) and TC-RAG (Jiang et al., 2025);
- 1 Multi-agent collaboration method: MDAgents (Kim et al., 2024).

**[KR]**
- 백본 4종: Qwen3-8B (Yang et al., 2025), Llama-3.1-8B-Instruct (Grattafiori et al., 2024), 그리고 특화 의료 LLM인 UltraMedical-3.1-8B (Zhang et al., 2024)와 HuatuoGPT-o1-8B (Chen et al., 2024);
- 검색을 사용하지 않는 test-time scaling 방법 3종: CoT (Chain-of-Thought) (Wei et al., 2022), SC (Self-Consistency) (Wang et al., 2023), 그리고 Multi-Refine (Tian et al., 2025; Xu et al., 2025);
- naive RAG 방법 3종: SR-RAG (Single-Round RAG) (Xiong et al., 2024), FL-RAG (Fixed-Length RAG) (Borgeaud et al., 2022; Ram et al., 2023), 그리고 FS-RAG (Fixed-Sentence RAG) (Trivedi et al., 2023);
- adaptive RAG 방법 2종: FLARE (Jiang et al., 2023)와 TC-RAG (Jiang et al., 2025);
- multi-agent collaboration(다중 에이전트 협업) 방법 1종: MDAgents (Kim et al., 2024).

**[EN]** We report accuracy (%) as the primary metric across all benchmarks. For all RAG-based methods, we use the same medical corpus MedCorp from MedRAG (Xiong et al., 2024), the same retriever BM25 (Robertson et al., 2009), and the same reranker MedCPT-Cross-Encoder (Jin et al., 2023), to ensure a strictly fair comparison. Appendix D presents more implementation details.

**[KR]** 우리는 모든 벤치마크에 걸쳐 정확도(accuracy, %)를 주요 지표로 보고한다. 엄격하게 공정한 비교를 보장하기 위해, 모든 RAG 기반 방법에 대해 MedRAG (Xiong et al., 2024)의 동일한 의료 코퍼스 MedCorp, 동일한 retriever BM25 (Robertson et al., 2009), 그리고 동일한 reranker MedCPT-Cross-Encoder (Jin et al., 2023)를 사용한다. 더 많은 구현 세부 사항은 Appendix D에 제시한다.

### 4.1. Main Results

**[EN]** Table 1 summarizes the performance comparison across all datasets. Qwen3-8B achieves the best performance across all backbone models. Hence, we implement MA-RAG and other baselines using the Qwen3-8B backbone.

**[KR]** Table 1은 모든 데이터셋에 걸친 성능 비교를 요약한다. Qwen3-8B는 모든 백본 모델 중에서 최고 성능을 달성한다. 따라서 우리는 Qwen3-8B 백본을 사용하여 MA-RAG와 다른 베이스라인들을 구현한다.

**[EN]** Superiority over Test-Time Scaling Baselines. SC (Self-Consistency) yields a modest improvement over the base model (+1.3 points) by aggregating consensus across multiple reasoning traces in a single round. Building upon the principle of iterative self-improvement, Multi-Refine further enhances performance by 3.3 points over the backbone by allowing the model to self-refine generations across multiple rounds. By adaptively assigning collaboration structures of expert teams for debating and refining, MDAgents outperforms the single-expert backbone by 2.8 points. These results show that scaling inference compute can increase medical reasoning capacity to some extent.

**[KR]** Test-Time Scaling 베이스라인 대비 우위. SC (Self-Consistency)는 단일 라운드에서 여러 추론 자취 전반의 합의를 집계함으로써 베이스 모델 대비 완만한 개선(+1.3점)을 보인다. 반복적 자기개선(iterative self-improvement) 원리에 기반하여, Multi-Refine는 모델이 여러 라운드에 걸쳐 생성물을 self-refine 하도록 허용함으로써 백본 대비 성능을 추가로 3.3점 향상시킨다. 토론과 정교화를 위해 전문가 팀의 협업 구조를 적응적으로 배정함으로써, MDAgents는 단일 전문가 백본을 2.8점 능가한다. 이러한 결과는 추론 연산을 확장하면 의료 추론 능력을 어느 정도 높일 수 있음을 보여준다.

**[EN]** Figure 3 shows the test-time scaling performance between MA-RAG and the multi-round baseline (Multi-Refine). Multi-Refine quickly reaches a performance plateau, revealing the bottleneck of traditional test-time scaling methods that stems from the base model’s knowledge deficiencies in medical domains. In contrast, MA-RAG achieves continuous and substantial gains throughout the iterative process. The performance gain is particularly pronounced on harder benchmarks, e.g., a 37% relative improvement on MedXpertQA, highlighting our advantage in complex medical reasoning problems. By bridging knowledge gaps via adaptively injecting external evidence, MA-RAG effectively transcends the limits of pure inference scaling methods.

**[KR]** Figure 3은 MA-RAG와 다중 라운드 베이스라인(Multi-Refine) 사이의 test-time scaling 성능을 보여준다. Multi-Refine는 빠르게 성능 정체(plateau)에 도달하는데, 이는 의료 영역에서 베이스 모델의 지식 결핍에서 비롯되는 전통적 test-time scaling 방법의 병목을 드러낸다. 이와 대조적으로, MA-RAG는 반복 과정 전반에서 지속적이고 상당한 향상을 달성한다. 이 성능 향상은 더 어려운 벤치마크에서 특히 두드러지며, 예컨대 MedXpertQA에서 37%의 상대적 개선을 보여 복잡한 의료 추론 문제에서의 우리 방법의 강점을 부각한다. 외부 증거를 적응적으로 주입하여 지식 격차를 메움으로써, MA-RAG는 순수 추론 확장(pure inference scaling) 방법의 한계를 효과적으로 뛰어넘는다.

**[EN]** Superiority over RAG methods. Naive RAG methods often yield only marginal gains and may even suffer from performance degradation (e.g., on MedQA), compared to the Qwen3-8B backbone. This can stem from the insufficient or noisy context provided by single-round retrieval. While FLARE and TC-RAG employ multi-round retrieval, they also achieve only marginal gains, suggesting that simply increasing the retrieval rounds is insufficient for complex medical reasoning. MA-RAG addresses these pitfalls by employing the high-level semantic conflict as the retrieval signal, rather than the noisy token-level metrics used in adaptive RAG baselines. Notably, MA-RAG-ext achieves an average accuracy of 62.2%, significantly outperforming the strongest RAG baseline by a margin of 5.3 points.

**[KR]** RAG 방법 대비 우위. naive RAG 방법들은 Qwen3-8B 백본 대비 흔히 미미한 향상만을 보이며, 경우에 따라(예: MedQA) 성능 저하를 겪기도 한다. 이는 단일 라운드 검색이 제공하는 불충분하거나 잡음이 많은 맥락에서 비롯될 수 있다. FLARE와 TC-RAG는 다중 라운드 검색을 사용하지만 이들 역시 미미한 향상만을 달성하는데, 이는 단순히 검색 라운드를 늘리는 것만으로는 복잡한 의료 추론에 충분하지 않음을 시사한다. MA-RAG는 adaptive RAG 베이스라인에서 사용되는 잡음이 많은 token-level 지표 대신 상위 수준의 semantic conflict를 검색 신호로 사용함으로써 이러한 함정을 해결한다. 특히 MA-RAG-ext는 62.2%의 평균 정확도를 달성하여, 가장 강력한 RAG 베이스라인을 5.3점 차로 크게 능가한다.

**[EN]** Score Functions in Ranking Agent. MA-RAG-ext (using the BERT-based score function) yields an average gain of 1.2 points compared to MA-RAG-int (using the entropy-based score function). This observation aligns with our analysis of existing adaptive RAG methods: token-level uncertainty metrics may prove unreliable, as they fail to detect confident yet factually incorrect hallucinations. The external verifier, fine-tuned on specialized medical corpus, establishes a more robust mechanism for prioritizing high-quality demonstrations, leading to enhanced in-context learning. Appendix F.4 provides more quantitative analysis on the ranking agent.

**[KR]** Ranking Agent의 점수 함수. MA-RAG-ext(BERT 기반 점수 함수 사용)는 MA-RAG-int(entropy 기반 점수 함수 사용) 대비 평균 1.2점의 향상을 보인다. 이 관찰은 기존 adaptive RAG 방법에 대한 우리의 분석과 부합한다. 즉, token-level 불확실성 지표는 확신에 차 있으면서도 사실상 틀린 환각을 탐지하지 못하므로 신뢰할 수 없을 수 있다. 특화 의료 코퍼스로 미세조정된 외부 verifier는 고품질 시연을 우선순위화하는 보다 견고한 메커니즘을 확립하여, 강화된 in-context learning으로 이어진다. ranking agent에 대한 더 많은 정량적 분석은 Appendix F.4에서 제공한다.

### 4.2. Ablation Study

**[EN]** To disentangle respective contributions of individual components within MA-RAG, we conduct an ablation study using Qwen3-8B as the backbone. We employ a cumulative component-addition strategy, progressively building toward the full MA-RAG model through the following ablations:

**[KR]** MA-RAG 내 개별 구성 요소들의 각 기여를 분리해 보기 위해, 우리는 Qwen3-8B를 백본으로 사용하여 ablation study(절제 연구)를 수행한다. 우리는 누적 구성 요소 추가 전략(cumulative component-addition strategy)을 채택하여, 다음의 절제 실험들을 통해 완전한 MA-RAG 모델까지 점진적으로 구축한다.

**[EN]**
- +Multi-Refine: implements iterative refinement based on internal knowledge, without external retrieval;
- +Retrieval Agent: integrates the conflict-guided retrieval agent to adaptively retrieve external evidence from a local medical corpus;
- +Ranking Agent: corresponds to the full MA-RAG method, which further incorporates the ranking mechanism to optimize history reasoning traces.

**[KR]**
- +Multi-Refine: 외부 검색 없이, 내부 지식에 기반한 반복적 정교화를 구현한다;
- +Retrieval Agent: conflict-guided retrieval agent를 통합하여 로컬 의료 코퍼스에서 외부 증거를 적응적으로 검색한다;
- +Ranking Agent: 이력 추론 자취를 최적화하기 위한 ranking 메커니즘을 추가로 통합한, 완전한 MA-RAG 방법에 해당한다.

**[EN]** Table 2 shows the ablation performance on all benchmarks. +Multi-Refine achieves a substantial average gain of 3.3 points over the backbone, highlighting the significance of multi-round refinement for complex medical reasoning.

**[KR]** Table 2는 모든 벤치마크에 대한 절제 성능을 보여준다. +Multi-Refine는 백본 대비 평균 3.3점이라는 상당한 향상을 달성하여, 복잡한 의료 추론에 대한 다중 라운드 정교화의 중요성을 부각한다.

**[EN]** Efficacy of the Retrieval Agent. Including agentic retrieval (+Retrieval Agent vs. +Multi-Refine) yields an average gain of 1.9 points. Notably, these gains are more pronounced on knowledge-intensive benchmarks such as MedXpertQA, where the model’s internal knowledge is often insufficient. When the model hallucinates due to a lack of factual grounding, repeated reasoning without external evidence typically fails to rectify the error. By leveraging semantic conflict as a diagnostic for knowledge gaps, our agent effectively retrieves targeted evidence, providing necessary context to ground the model toward the correct answer. In summary, our retrieval agent fulfills its objective of precise evidence acquisition, transcending the inherent performance ceilings of pure iterative self-refinement.

**[KR]** Retrieval Agent의 효능. agentic 검색을 포함하면(+Retrieval Agent 대 +Multi-Refine) 평균 1.9점의 향상이 나타난다. 특히 이러한 향상은 모델의 내부 지식이 흔히 불충분한 MedXpertQA와 같은 지식 집약적(knowledge-intensive) 벤치마크에서 더 두드러진다. 모델이 사실적 근거의 부족으로 환각을 일으킬 때, 외부 증거 없이 추론을 반복하는 것은 대개 오류를 바로잡지 못한다. semantic conflict를 지식 격차에 대한 진단 지표로 활용함으로써, 우리의 에이전트는 표적화된 증거를 효과적으로 검색하여, 모델을 올바른 답으로 근거 짓는 데 필요한 맥락을 제공한다. 요컨대, 우리의 retrieval agent는 정밀한 증거 획득이라는 목표를 달성하여, 순수 반복적 self-refinement에 내재된 성능 한계(performance ceiling)를 뛰어넘는다.

**[EN]** Efficacy of the Ranking Agent. In the absence of context optimization (+Retrieval Agent), high-quality traces can suffer from the “lost-in-the-middle” issue, where critical evidence receives insufficient attention. When incorporating context optimization (+Ranking Agent), our method yields consistent performance gains, with +1.6 points on average and notable +4.0 points on MedExpQA. Figure 4 visualizes the response score density, confirming that both scoring functions provide a robust ranking mechanism for strategic reorganization of history reasoning traces. By explicitly prioritizing high-quality traces based on the scores, the ranking agent acts as a dynamic context optimizer, effectively mitigating long-context degradation and enhancing in-context learning performance.

**[KR]** Ranking Agent의 효능. 맥락 최적화가 없으면(+Retrieval Agent), 고품질 자취가 "lost-in-the-middle" 문제를 겪을 수 있으며, 이 경우 핵심 증거가 충분한 주의를 받지 못한다. 맥락 최적화를 통합하면(+Ranking Agent), 우리의 방법은 평균 +1.6점, 그리고 MedExpQA에서 두드러진 +4.0점의 일관된 성능 향상을 보인다. Figure 4는 응답 점수 밀도(response score density)를 시각화하여, 두 점수 함수 모두 이력 추론 자취의 전략적 재조직화를 위한 견고한 ranking 메커니즘을 제공함을 확인한다. 점수에 기반하여 고품질 자취를 명시적으로 우선순위화함으로써, ranking agent는 동적 맥락 최적화기로 작동하여 long-context degradation을 효과적으로 완화하고 in-context learning 성능을 강화한다.

### 4.3. Test-Time Scaling Analysis

**[EN]** To assess MA-RAG’s test-time scaling properties, we investigate its performance regarding two core hyperparameters: the maximum refinement rounds $T$ and the size of the candidate pool $N$. Table 3 presents the results using Qwen3-8B.

**[KR]** MA-RAG의 test-time scaling 특성을 평가하기 위해, 우리는 두 가지 핵심 하이퍼파라미터, 즉 최대 정교화 라운드 $T$와 후보 풀(candidate pool)의 크기 $N$에 관한 성능을 조사한다. Table 3은 Qwen3-8B를 사용한 결과를 제시한다.

**[EN]** Analysis of the Maximum Inference Rounds. Notably, incorporating just a second round ($T = 2$) yields a significant improvement of 4.0 points on average, demonstrating that even one additional round of conflict-guided retrieval is highly effective at bridging the model’s knowledge gap. Performance gains begin to saturate beyond $T = 4$, with the model exhibiting asymptotic behavior as it yields only a negligible point improvement when scaling to $T = 8$. The scaling trend suggests that MA-RAG achieves effective and computationally efficient multi-round retrieval. Consequently, we posit that $T = 4$ serves as a cost-effective stopping criterion for empirical deployment.

**[KR]** 최대 추론 라운드 분석. 특히, 두 번째 라운드($T = 2$)를 추가하는 것만으로도 평균 4.0점의 유의미한 개선이 나타나는데, 이는 단 한 번의 추가적인 conflict-guided 검색 라운드만으로도 모델의 지식 격차를 메우는 데 매우 효과적임을 입증한다. 성능 향상은 $T = 4$를 넘어서면 포화되기 시작하며, $T = 8$로 확장할 때 무시할 만한 수준의 향상만을 보이는 점근적(asymptotic) 거동을 나타낸다. 이러한 확장 추세는 MA-RAG가 효과적이면서도 연산적으로 효율적인 다중 라운드 검색을 달성함을 시사한다. 따라서 우리는 $T = 4$가 실증적 배치를 위한 비용 효율적 중단 기준(stopping criterion)으로 기능한다고 본다.

**[EN]** Analysis of the Candidate Pool Size. The diversity within the candidate pool is essential to MA-RAG, as it determines the capacity for both conflict-guided retrieval and rank-based context optimization. Expanding the pool size yields consistent performance gains, with 1.5 points when moving from $N = 2$ to $N = 4$, and another 2.2 points when scaling to $N = 8$. We attribute this improvement to two factors: i) Enhanced Conflict Mining, a larger pool increases the coverage of semantic conflict, allowing the retrieval agent to formulate more precise queries for bridging knowledge gaps; and ii) Improved In-Context Learning, expanding the candidate pool enlarges the search space for high-quality reasoning traces, enabling the ranking agent to distill and prioritize superior in-context demonstrations. $N = 4$ provides a cost-effective configuration for resource-constrained scenarios, and scaling to $N = 8$ is preferable when maximizing reasoning performance is paramount.

**[KR]** 후보 풀 크기 분석. 후보 풀 내의 다양성은 MA-RAG에 필수적인데, 이것이 conflict-guided 검색과 rank 기반 맥락 최적화 모두의 역량을 결정하기 때문이다. 풀 크기를 확장하면 일관된 성능 향상이 나타나는데, $N = 2$에서 $N = 4$로 옮겨갈 때 1.5점, 그리고 $N = 8$로 확장할 때 추가로 2.2점이 향상된다. 우리는 이 개선을 두 가지 요인에 기인한 것으로 본다. i) 강화된 Conflict Mining(충돌 채굴): 더 큰 풀은 semantic conflict의 포괄 범위를 넓혀, retrieval agent가 지식 격차를 메우기 위한 더 정밀한 쿼리를 구성할 수 있게 한다. ii) 향상된 In-Context Learning: 후보 풀을 확장하면 고품질 추론 자취에 대한 탐색 공간이 넓어져, ranking agent가 우수한 in-context demonstration을 추려내고 우선순위화할 수 있게 한다. $N = 4$는 자원이 제약된 시나리오를 위한 비용 효율적 구성이며, 추론 성능 극대화가 무엇보다 중요할 때는 $N = 8$로 확장하는 것이 바람직하다.

**[EN]** Scaling $N$ Delays Round-wise Saturation. To further investigate the interaction between candidate diversity and multi-round refinement, we analyze the per-round performance under varying pool sizes $N \in \{4, 8, 16\}$ on Medbullets and MedXpertQA. As shown in Figure 5 and Table 10, increasing $N$ yields two notable benefits. First, a larger pool of candidates improves peak performance, with $N = 16$ delivering gains of 4.6 points on Medbullets and 4.3 points on MedXpertQA over $N = 4$. Second, expanding $N$ defers the onset of saturation: while $N = 4$ plateaus after Round 2, $N = 16$ sustains meaningful improvements through Round 3 and beyond. This delayed saturation is attributed to the richer semantic conflict mined from a larger candidate pool, which in turn fuels more diverse and targeted retrieval queries across successive rounds.

**[KR]** $N$의 확장은 라운드별 포화를 지연시킨다. 후보 다양성과 다중 라운드 정교화 사이의 상호작용을 더 깊이 조사하기 위해, 우리는 Medbullets와 MedXpertQA에서 다양한 풀 크기 $N \in \{4, 8, 16\}$ 하의 라운드별(per-round) 성능을 분석한다. Figure 5와 Table 10에 나타난 바와 같이, $N$을 늘리면 두 가지 주목할 만한 이점이 생긴다. 첫째, 더 큰 후보 풀은 최고 성능(peak performance)을 향상시키며, $N = 16$은 $N = 4$ 대비 Medbullets에서 4.6점, MedXpertQA에서 4.3점의 향상을 제공한다. 둘째, $N$을 확장하면 포화의 시작을 늦춘다. $N = 4$는 Round 2 이후 정체되는 반면, $N = 16$은 Round 3와 그 이후까지 유의미한 향상을 지속한다. 이러한 지연된 포화는 더 큰 후보 풀에서 채굴된 더 풍부한 semantic conflict에 기인하며, 이는 다시 연속된 라운드 전반에 걸쳐 더 다양하고 표적화된 검색 쿼리를 공급한다.

### 4.4. Scalability across Model Scales

**[EN]** To verify MA-RAG’s scalability to larger models, we evaluate its performance on Qwen3-32B backbone. Table 4 presents the ablation study on the Qwen3-32B model, and Figure 6 shows the performance comparison between MA-RAG and backbones across model scales. MA-RAG scales effectively with increasing model capacities, with a substantial average gain of 5.5 points when deployed on the stronger 32B backbone. Notably, the retrieval agent continues to play a critical role, boosting the performance with 1.8 points by rectifying knowledge gaps that remain unsolved even in larger models. The superiority is more evident on the challenging MedXpertQA benchmark, where the retrieval agent provides a substantial gain of 3.7 points and the ranking agent contributes an additional gain of 2.4 points. In summary, these results demonstrate MA-RAG’s scalability across base model capacities, enabling consistent performance gains for complex medical reasoning tasks.

**[KR]** 더 큰 모델에 대한 MA-RAG의 확장성을 검증하기 위해, 우리는 Qwen3-32B 백본에서의 성능을 평가한다. Table 4는 Qwen3-32B 모델에 대한 ablation study를 제시하며, Figure 6은 모델 규모 전반에 걸친 MA-RAG와 백본 사이의 성능 비교를 보여준다. MA-RAG는 모델 용량이 커짐에 따라 효과적으로 확장되며, 더 강력한 32B 백본에 배치했을 때 평균 5.5점이라는 상당한 향상을 보인다. 특히 retrieval agent는 더 큰 모델에서도 풀리지 않은 채 남아 있는 지식 격차를 바로잡아 성능을 1.8점 부스팅하면서 계속해서 핵심적인 역할을 한다. 이 우위는 까다로운 MedXpertQA 벤치마크에서 더 분명하게 드러나는데, 여기서 retrieval agent는 3.7점의 상당한 향상을 제공하고 ranking agent는 추가로 2.4점의 향상을 기여한다. 요컨대, 이러한 결과는 베이스 모델 용량 전반에 걸친 MA-RAG의 확장성을 입증하며, 복잡한 의료 추론 과제에 대해 일관된 성능 향상을 가능하게 한다.

### 4.5. Inference Efficiency Analysis

**[EN]** To demonstrate the practical viability of multi-round agentic refinement, Table 5 reports a comprehensive efficiency analysis of MA-RAG-ext against representative baselines across retrieval, generation, and wall-clock time dimensions. All measurements are executed using the Qwen3-8B backbone on MedXpertQA under identical hardware conditions. Further results on Medbullets can be found in Appendix F.8.

**[KR]** 다중 라운드 agentic refinement의 실용적 타당성을 입증하기 위해, Table 5는 검색, 생성, 그리고 실측 시간(wall-clock time) 차원에 걸쳐 MA-RAG-ext를 대표 베이스라인들과 비교한 포괄적 효율성 분석을 보고한다. 모든 측정은 동일한 하드웨어 조건에서 MedXpertQA에 대해 Qwen3-8B 백본을 사용하여 수행되었다. Medbullets에 대한 추가 결과는 Appendix F.8에서 확인할 수 있다.

**[EN]** Retrieval Efficiency. While MA-RAG-ext retrieves slightly more documents than TC-RAG, it yields a vastly superior performance improvement of 4.2 points. Furthermore, MA-RAG-ext requires less than half the retrieved documents of FLARE yet achieves a substantial 4.5 point gain in accuracy. This demonstrates that semantic conflict provides a more grounded and reliable retrieval signal for pinpointing knowledge gaps, in contrast to the noisy token-level uncertainty employed by existing adaptive RAG baselines.

**[KR]** 검색 효율성. MA-RAG-ext는 TC-RAG보다 약간 더 많은 문서를 검색하지만, 4.2점이라는 훨씬 우월한 성능 향상을 보인다. 더 나아가, MA-RAG-ext는 FLARE가 검색하는 문서의 절반 미만을 요구하면서도 정확도에서 상당한 4.5점의 향상을 달성한다. 이는 기존 adaptive RAG 베이스라인이 사용하는 잡음 많은 token-level 불확실성과 대조적으로, semantic conflict가 지식 격차를 정확히 짚어내는 데 더 근거 있고 신뢰할 수 있는 검색 신호를 제공함을 입증한다.

**[EN]** Generation Efficiency. While MA-RAG-ext generates approximately 1.2× more tokens than Self-Consistency, it delivers a substantial 6.5 point accuracy gain, demonstrating that its generation budget is productively invested in retrieval-augmented refinement rather than solely resampling reasoning paths without external grounding.

**[KR]** 생성 효율성. MA-RAG-ext는 Self-Consistency보다 약 1.2배 더 많은 토큰을 생성하지만, 상당한 6.5점의 정확도 향상을 제공한다. 이는 그 생성 예산(generation budget)이 외부 근거 없이 추론 경로를 단순히 재샘플링하는 데가 아니라, 검색 증강 정교화(retrieval-augmented refinement)에 생산적으로 투입됨을 입증한다.

**[EN]** Wall-Clock Time. MA-RAG-ext outperforms the strongest baseline MDAgents by 4.0 points while requiring less than half the inference time. Although it incurs approximately 1.6× the time cost of TC-RAG, this yields a 4.2 point accuracy gain, representing a relative improvement of 23.3%. This demonstrates that MA-RAG-ext achieves a highly favorable cost-performance trade-off: a moderate increase at inference time for a rigorously refined, evidence-grounded diagnostic assistant.

**[KR]** 실측 시간(Wall-Clock Time). MA-RAG-ext는 가장 강력한 베이스라인인 MDAgents를 4.0점 능가하면서도 추론 시간은 그 절반 미만을 요구한다. TC-RAG 대비 약 1.6배의 시간 비용이 들지만, 이는 4.2점의 정확도 향상, 즉 23.3%의 상대적 개선을 가져온다. 이는 MA-RAG-ext가 매우 유리한 비용-성능 절충(cost-performance trade-off)을 달성함을 입증한다. 즉, 엄밀하게 정교화되고 증거에 근거한 진단 보조자를 위해 추론 시점에 적당한 비용 증가를 감수하는 것이다.

---

## §5 Conclusions, Limitations, and Future Work

**[EN]** In this paper, we proposed MA-RAG, a novel framework that iteratively evolves both external evidence and internal reasoning history within an agentic refinement loop to steer test-time scaling for complex medical reasoning. At each round, the solver agent samples multiple candidate responses, the retrieval agent transforms semantic conflict among candidates into actionable queries to retrieve external evidence, and the ranking agent optimizes history reasoning traces to enhance in-context learning. Extensive experiments verified MA-RAG’s consistent superiority over a variety of test-time scaling and RAG baselines.

**[KR]** 본 논문에서 우리는 복잡한 의료 추론에 대한 test-time scaling을 유도하기 위해 agentic refinement loop 내에서 외부 증거와 내부 추론 이력을 반복적으로 진화시키는 새로운 프레임워크 MA-RAG를 제안했다. 매 라운드마다 solver agent는 여러 후보 응답을 샘플링하고, retrieval agent는 후보들 사이의 semantic conflict를 외부 증거를 검색하기 위한 실행 가능한 쿼리로 변환하며, ranking agent는 in-context learning을 강화하기 위해 이력 추론 자취를 최적화한다. 광범위한 실험은 다양한 test-time scaling 및 RAG 베이스라인 대비 MA-RAG의 일관된 우위를 검증했다.

**[EN]** Nevertheless, the inference-time cost of multi-round agentic refinement remains a limitation, and retrieval effectiveness is inherently constrained by the coverage and quality of the underlying medical corpus. Future work may extend MA-RAG to a more general agentic paradigm by incorporating richer tools such as web-scale search, structured medical databases, or external reasoning modules to broaden evidence access. Developing more reliable response quality estimation methods is also crucial, as the ranking agent’s potential is inherently tied to evaluation accuracy.

**[KR]** 그럼에도 불구하고, 다중 라운드 agentic refinement의 추론 시점 비용(inference-time cost)은 여전히 한계로 남아 있으며, 검색 효과성은 본질적으로 기반 의료 코퍼스의 포괄 범위와 품질에 의해 제약된다. 향후 연구는 웹 규모 검색(web-scale search), 구조화된 의료 데이터베이스, 또는 외부 추론 모듈과 같은 더 풍부한 도구를 통합하여 증거 접근성을 넓힘으로써 MA-RAG를 보다 일반적인 agentic 패러다임으로 확장할 수 있다. ranking agent의 잠재력은 본질적으로 평가 정확도에 결부되어 있으므로, 보다 신뢰할 수 있는 응답 품질 추정(response quality estimation) 방법을 개발하는 것 또한 중요하다.
