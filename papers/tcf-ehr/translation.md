# Time-Conditioned Foreseeing: An EHR-Specific Foundation Model for Irregular Dynamics and Calendrical Time — 본문 EN/KR 병렬 번역

> 원문: Bong Gyun Kang, Junyong Ahn, Hyeongrok Han, Sungroh Yoon (Seoul National University). **Time-Conditioned Foreseeing: An EHR-Specific Foundation Model for Irregular Dynamics and Calendrical Time.** ICML 2026 (poster). (번역 대상 PDF는 익명화된 ICLR 2026 투고본 "Time Conditioned Foreseeing: Temporal Generative Pretraining for EHR Foundation Models".)
> 범위: Abstract – §5 Conclusion (본문 전체). Appendix·References·각주는 제외(본문 내 표/그림 참조 문장은 번역에 포함). 각주 1, 2는 내용 이해에 필요해 KR 블록 말미에 [각주] 표기로 포함.
> 포맷: 문단 단위 `**[EN]**` 원문 → `**[KR]**` 번역 교차.

---

## Abstract

**[EN]** Electronic Health Records (EHRs) possess unique characteristics that differ significantly from natural language. However, existing models have overlooked these properties and largely relied on Natural Language Processing (NLP) approaches, resulting in suboptimal performance. To address these limitations, we propose a pretraining method designed to effectively capture the distinctive features of EHRs. First, EHRs contain both clinically critical and less informative numerical ranges. To reflect this, we introduce a Pathology-Focused Binning strategy that emphasizes values with clinical significance. Second, both absolute timestamps and relative time intervals are important in EHRs. To incorporate these temporal aspects, we propose a Dual-Calendar Rotary Positional Embedding (RoPE) that jointly encodes complementary temporal signals. Third, many medical applications require modeling long-term patient interactions. Accordingly, we extend conventional next-token prediction with a Time-Conditioned Foreseeing (TCF) objective, enabling the model to forecast long-range clinical events across multiple temporal horizons. Our approach establishes the first genuine temporal generative EHR model, advancing long-range clinical forecasting. It outperforms existing EHR foundation models on seven diverse downstream tasks and enables realistic and temporally consistent EHR generation. All code and models will be made publicly available in the final version of the manuscript.

**[KR]** 전자의무기록(Electronic Health Records, EHR)은 자연어와 크게 다른 고유한 특성을 지닌다. 그러나 기존 모델들은 이러한 특성을 간과한 채 대체로 자연어 처리(Natural Language Processing, NLP) 방식에 의존해 왔고, 그 결과 최적이 아닌 성능에 머물렀다. 이러한 한계를 해결하기 위해 우리는 EHR의 고유한 특징을 효과적으로 포착하도록 설계된 사전학습(pretraining) 방법을 제안한다. 첫째, EHR에는 임상적으로 중요한 수치 범위와 정보량이 적은 수치 범위가 함께 존재한다. 이를 반영하기 위해 우리는 임상적 의미를 가진 값을 강조하는 Pathology-Focused Binning 전략을 도입한다. 둘째, EHR에서는 절대 타임스탬프(absolute timestamp)와 상대 시간 간격(relative time interval)이 모두 중요하다. 이러한 시간적 측면을 통합하기 위해 우리는 상호 보완적인 시간 신호를 함께 인코딩하는 Dual-Calendar Rotary Positional Embedding(RoPE)을 제안한다. 셋째, 많은 의료 응용에서는 장기적인 환자 상호작용을 모델링해야 한다. 이에 따라 우리는 기존의 next-token prediction을 Time-Conditioned Foreseeing(TCF) objective로 확장하여, 모델이 여러 시간 지평(temporal horizon)에 걸쳐 장기 임상 사건을 예측할 수 있도록 한다. 우리의 접근법은 진정한 의미의 최초의 temporal generative EHR 모델을 확립하며, 장기 임상 예측(long-range clinical forecasting)을 진전시킨다. 이 모델은 일곱 가지 다양한 downstream task에서 기존 EHR foundation model들을 능가하며, 현실적이고 시간적으로 일관된 EHR 생성을 가능하게 한다. 모든 코드와 모델은 원고의 최종본에서 공개될 예정이다.

## §1 Introduction

**[EN]** Electronic health records (EHRs) are longitudinal records that comprehensively document a patient's medical history. EHRs help clinicians assess patient conditions, coordinate diagnostic and therapeutic interventions, and communicate with other healthcare providers (Häyrinen et al., 2008). One of the key objectives in medical AI is to develop models that can learn from EHRs to perform various clinical tasks. However, building such models is challenging due to the complex temporal dependencies and the predominance of numerical data in EHRs (Nasarudin et al., 2024). Recently, there have been growing efforts to leverage large language model (LLM) training paradigms in building EHR foundation models (Niu et al., 2024). Despite these advances, approaches explicitly designed to model the distinct characteristics of EHRs are still in their early stages of development.

**[KR]** 전자의무기록(EHR)은 환자의 의료 이력을 포괄적으로 기록하는 종단적(longitudinal) 기록이다. EHR은 임상의가 환자 상태를 평가하고, 진단 및 치료 개입을 조율하며, 다른 의료 제공자와 소통하는 데 도움을 준다(Häyrinen et al., 2008). 의료 AI의 핵심 목표 중 하나는 EHR로부터 학습하여 다양한 임상 작업을 수행할 수 있는 모델을 개발하는 것이다. 그러나 이러한 모델을 구축하는 일은 EHR에 내재한 복잡한 시간적 의존성과 수치 데이터의 우세함 때문에 어렵다(Nasarudin et al., 2024). 최근 EHR foundation model 구축에 대규모 언어 모델(LLM) 학습 패러다임을 활용하려는 노력이 점차 늘고 있다(Niu et al., 2024). 이러한 진전에도 불구하고, EHR의 고유한 특성을 명시적으로 모델링하도록 설계된 접근법은 여전히 초기 발전 단계에 머물러 있다.

**[EN]** EHRs consist of diverse clinical events—such as examinations, treatments, and diagnoses—that are recorded with associated timestamps. Figure 1 illustrates an example EHR, where events are arranged chronologically, and shows how these events can be transformed into a sentence of tokens. Recent preprocessing approaches for EHRs commonly represent a single clinical event as a Time (T), Feature (F), Value (V) triplet (Tipirneni & Reddy, 2022). Here, the Feature denotes attributes such as diagnosis codes, prescribed medications, or laboratory tests (e.g., Systolic Blood Pressure) and represented as a single token, while the Value corresponds to the result or auxiliary information of the Feature (e.g., 87mmHg). Values are typically numerical but may also be absent, or take the form of heterogeneous modalities such as text, depending on the Feature.

**[KR]** EHR은 검사, 치료, 진단과 같은 다양한 임상 사건(clinical event)으로 구성되며, 각 사건은 해당 타임스탬프와 함께 기록된다. Figure 1은 사건들이 시간순으로 배열된 예시 EHR을 보여 주며, 이러한 사건들이 어떻게 토큰의 문장(sentence of tokens)으로 변환될 수 있는지를 나타낸다. 최근 EHR 전처리 방식은 단일 임상 사건을 Time(T), Feature(F), Value(V) triplet으로 표현하는 것이 일반적이다(Tipirneni & Reddy, 2022). 여기서 Feature는 진단 코드, 처방 약물, 검사(예: 수축기 혈압, Systolic Blood Pressure) 같은 속성을 가리키며 단일 토큰으로 표현되고, Value는 해당 Feature의 결과 또는 부가 정보(예: 87mmHg)에 해당한다. Value는 일반적으로 수치이지만, Feature에 따라 부재(absent)할 수도 있고 텍스트와 같은 이질적 모달리티(heterogeneous modality) 형태를 취할 수도 있다.

**[EN]** Despite the necessity of including all triplet components for a faithful representation of clinical events, as indicated in the "data usage" column of Table 1, even the most recent EHR foundation models often exclude Time or Value information due to modeling complexities (Yang et al., 2024).

**[KR]** 임상 사건을 충실히 표현하려면 triplet의 모든 구성 요소를 포함하는 것이 필요함에도 불구하고, Table 1의 "data usage" 열에서 보듯이 가장 최신의 EHR foundation model조차 모델링의 복잡성 때문에 Time이나 Value 정보를 종종 배제한다(Yang et al., 2024).

**[EN]** Figure 1: (Left) Extraction of raw patient data from the EHR database in chronological order. (Right) Tokenization of each event (E) with triplet representation, where patient information is placed at the beginning, Features and Values are tokenized, and timestamps remain continuous.

**[KR]** Figure 1: (왼쪽) EHR 데이터베이스에서 환자 원시 데이터를 시간순으로 추출한 것. (오른쪽) 각 사건(E)을 triplet 표현으로 토큰화한 것으로, 환자 정보가 맨 앞에 배치되고 Feature와 Value가 토큰화되며 타임스탬프는 연속값(continuous)으로 유지된다.

**[EN]** Recent EHR foundation models have improved performance on various downstream tasks through large-scale pre-training. However, most of these models follow standard LLM training paradigms without adapting to the structure and clinical semantics of EHR data (Burkhart et al., 2025), which differ from natural language. For example, converting temporal information into absolute positional embeddings hinders capturing relative intervals and preserving clinically meaningful calendrical information (Likhomanenko et al., 2021). Also, processing numeric Value through uniform binning concentrates bins around normal ranges and reduces resolution for pathological states. Moreover, most learning objectives are adopted from language modeling, such as next-token prediction (NTP) or masked language modeling (MLM), without considering EHR-specific characteristics. To address these limitations, we introduce improved binning, temporal embedding, and novel training objectives tailored to EHR data and clinical planning process.

**[KR]** 최근 EHR foundation model들은 대규모 사전학습을 통해 다양한 downstream task에서 성능을 향상시켜 왔다. 그러나 이들 모델 대부분은 자연어와 다른 EHR 데이터의 구조와 임상적 의미(clinical semantics)에 적응하지 않은 채 표준 LLM 학습 패러다임을 따른다(Burkhart et al., 2025). 예를 들어, 시간 정보를 절대 위치 임베딩(absolute positional embedding)으로 변환하면 상대 간격을 포착하고 임상적으로 의미 있는 달력적(calendrical) 정보를 보존하는 데 방해가 된다(Likhomanenko et al., 2021). 또한 수치 Value를 균일 비닝(uniform binning)으로 처리하면 bin이 정상 범위 주변에 몰려, 병리적 상태에 대한 해상도가 떨어진다. 더 나아가, 대부분의 학습 목표(learning objective)는 EHR 고유의 특성을 고려하지 않고 next-token prediction(NTP)이나 masked language modeling(MLM) 같은 언어 모델링에서 차용된 것이다. 이러한 한계를 해결하기 위해 우리는 EHR 데이터와 임상 계획 과정(clinical planning process)에 맞춤화된 개선된 비닝, 시간 임베딩, 새로운 학습 목표를 도입한다.

**[EN]** First, we introduce a simple yet effective Pathology-focused Binning for Value tokenization. As shown in the "Value Binning" column of Table 1, most EHR models tokenize Value through uniform binning. However, as illustrated in Figure 2A, uniform binning assigns a large amount of bins to physiologic ranges, while allocating only a few bins to clinically important pathologic ranges, thereby limiting the ability to distinguish the severity of abnormalities. Other models rely on false distributional assumptions of Gaussianity, and instead apply standard deviation (std)–based binning (Zhu et al., 2024) or z-normalization (Tipirneni & Reddy, 2022), making them vulnerable to outliers, long-tailed, and dual peaks distributions common in EHR. To address this, we propose a density-based binning that makes no distributional assumptions and focuses on pathological ranges. In this approach, values in high-density physiologic zones are assigned lower weights, whereas values in low-density pathologic zones receive higher weights. This design is suited for all value distributions, and we are the first to apply such binning to EHR models.

**[KR]** 첫째, 우리는 Value 토큰화를 위해 단순하지만 효과적인 Pathology-Focused Binning을 도입한다. Table 1의 "Value Binning" 열에서 보듯이, 대부분의 EHR 모델은 Value를 균일 비닝으로 토큰화한다. 그러나 Figure 2A에서 나타나듯이, 균일 비닝은 생리적(physiologic) 범위에 많은 bin을 할당하는 반면 임상적으로 중요한 병리적(pathologic) 범위에는 소수의 bin만 배정하여, 이상치의 중증도(severity)를 구별하는 능력을 제한한다. 다른 모델들은 가우시안성(Gaussianity)이라는 잘못된 분포 가정에 의존하여, 그 대신 표준편차(std) 기반 비닝(Zhu et al., 2024)이나 z-정규화(z-normalization)(Tipirneni & Reddy, 2022)를 적용하는데, 이는 EHR에서 흔히 나타나는 이상치, 긴 꼬리(long-tailed), 이중 봉우리(dual peaks) 분포에 취약하다. 이를 해결하기 위해 우리는 어떠한 분포 가정도 하지 않고 병리적 범위에 집중하는 밀도 기반 비닝(density-based binning)을 제안한다. 이 방식에서는 고밀도의 생리적 구간에 있는 값에 낮은 가중치가, 저밀도의 병리적 구간에 있는 값에는 높은 가중치가 부여된다. 이 설계는 모든 값 분포에 적합하며, 우리는 이러한 비닝을 EHR 모델에 적용한 최초의 연구이다.

**[EN]** Second, we introduce Dual-Calendar RoPE, a novel timestamp addressing method for EHRs. Unlike language models, where tokens are assumed to be uniformly spaced, EHRs contain events with highly irregular intervals. Clinically, both relative intervals and calendarical context—e.g., morning/afternoon or weekday/weekend—are important (body temperature is higher in the afternoon, and dialysis complications are common after weekends (Fotheringham et al., 2020)). Also, multiple events may occur at the same time, such as laboratory tests recorded together. As shown in Figure 2B, we partition the dimensions of rotary positional embedding (Su et al., 2024) to jointly encode position and time, assigning calendrical components (e.g., minute, day, month) in increasing units to the time dimension. This enables explicit modeling of distance relations such as "two tests performed at the same time" or "the same test performed at the same hour on different days." The "Time Addressing" column of Table 1 shows that conventional models have not fully addressed crucial temporal information.

**[KR]** 둘째, 우리는 EHR을 위한 새로운 타임스탬프 주소 지정(timestamp addressing) 방법인 Dual-Calendar RoPE를 도입한다. 토큰이 균일한 간격을 갖는다고 가정하는 언어 모델과 달리, EHR에는 매우 불규칙한 간격의 사건들이 담겨 있다. 임상적으로는 상대 간격과 달력적(calendrical) 맥락—예를 들어 오전/오후 또는 평일/주말—이 모두 중요하다(체온은 오후에 더 높고, 투석 합병증은 주말 이후에 흔하다(Fotheringham et al., 2020)). 또한 함께 기록되는 검사처럼 여러 사건이 동일한 시각에 발생할 수도 있다. Figure 2B에서 보듯이, 우리는 위치와 시간을 함께 인코딩하기 위해 rotary positional embedding(Su et al., 2024)의 차원을 분할하고, 달력적 구성 요소(예: 분, 일, 월)를 단위가 커지는 순서로 시간 차원에 배정한다. 이를 통해 "동일한 시각에 수행된 두 검사" 또는 "서로 다른 날의 같은 시각에 수행된 같은 검사"와 같은 거리 관계를 명시적으로 모델링할 수 있다.[각주1] Table 1의 "Time Addressing" 열은 기존 모델들이 핵심적인 시간 정보를 충분히 다루지 못했음을 보여 준다.

**[EN]** Finally, and most importantly, we propose a new learning objective, Time-Conditioned Foreseeing (TCF). This objective aligns with the clinical process of treatment planning, and it enables, for the first time, generative temporal modeling of a patient's medical timeline. As shown in the "Learning Objective" column of Table 1, prior models have relied on objectives designed for language models or variants thereof, with the exception of the time-to-event (TTE) objective. Conventional EHR models trained with NTP loss capture only P(Fnext | Epast), without explicitly modeling temporal information. Consequently, they cannot distinguish whether an event occurs minutes later or after many hours, treating both urgent and routine vital sign measurements (short and long time intervals respectively) identically as the 'next token.'

**[KR]** 마지막으로, 그리고 가장 중요하게, 우리는 새로운 학습 목표인 Time-Conditioned Foreseeing(TCF)을 제안한다. 이 목표는 치료 계획(treatment planning)이라는 임상 과정과 부합하며, 환자의 의료 타임라인(medical timeline)에 대한 생성적 시간 모델링(generative temporal modeling)을 최초로 가능하게 한다. Table 1의 "Learning Objective" 열에서 보듯이, 기존 모델들은 time-to-event(TTE) objective를 제외하면 언어 모델용으로 설계된 목표나 그 변형에 의존해 왔다. NTP loss로 학습된 기존 EHR 모델은 시간 정보를 명시적으로 모델링하지 않은 채 $P(F_{next} \mid E_{past})$만을 포착한다. 그 결과 이들은 사건이 몇 분 뒤에 일어나는지 여러 시간 뒤에 일어나는지를 구별하지 못하며, 응급 활력징후 측정과 일상적 활력징후 측정(각각 짧은 시간 간격과 긴 시간 간격)을 모두 동일한 '다음 토큰(next token)'으로 동일하게 취급한다.

[각주1] 각주 원문: SBP, 120mmHg, DBP, 80mmHg가 동시에 기록된다고 하자. 위치(position) 차원은 모델이 SBP, 80mmHg, DBP, 120mmHg와 같은 결과로 혼동하지 않도록 추가적인 지지를 제공한다.

**[EN]** In contrast, TCF explicitly models long-range temporal information, thereby capturing how real-world clinical practice unfolds over time. In NLP, missing a single token disrupts grammar, and consecutive tokens are tightly correlated. By contrast, neighboring EHR events are loosely connected and often exhibit long-range dependencies, such as 8-hour follow-up tests. This reflects clinical practice, where physicians do not always act in real time but instead devise broader clinical plans. TCF embodies this principle: rather than the short-sighted scope of NTP, which predicts only the immediate next event, TCF enables questions such as, "What intervention is needed in the next six hours?" To achieve this, TCF module first generates the next timestamp from the last hidden state. The multiple foreseeing timestamps are then fed back as module inputs, conditioning subsequent token generation. This time-conditioned architecture allows simultaneous learning of P(Tnext | Epast) and P(Fforesees | Tforesees, Epast), leading to improved performance.

**[KR]** 이와 대조적으로, TCF는 장기(long-range) 시간 정보를 명시적으로 모델링하여 실제 임상 진료가 시간에 따라 어떻게 전개되는지를 포착한다. NLP에서는 단일 토큰이 누락되면 문법이 무너지고, 연속된 토큰들이 강하게 상관되어 있다. 반면 인접한 EHR 사건들은 느슨하게 연결되어 있으며, 8시간 후속 검사처럼 장기 의존성(long-range dependency)을 보이는 경우가 많다. 이는 의사가 항상 실시간으로 행동하기보다 더 넓은 임상 계획을 세우는 실제 진료 방식을 반영한다. TCF는 이 원칙을 구현한다. 즉, 바로 다음 사건만 예측하는 NTP의 근시안적 범위 대신, TCF는 "향후 6시간 안에 어떤 개입이 필요한가?"와 같은 질문을 가능하게 한다. 이를 위해 TCF 모듈은 먼저 마지막 hidden state로부터 다음 타임스탬프를 생성한다. 그런 다음 여러 개의 foreseeing 타임스탬프가 모듈 입력으로 되먹임되어 이후 토큰 생성을 조건화(conditioning)한다. 이러한 time-conditioned 아키텍처는 $P(T_{next} \mid E_{past})$와 $P(F_{foresees} \mid T_{foresees}, E_{past})$를 동시에 학습할 수 있게 하여 성능 향상으로 이어진다.

**[EN]** Our model ranked first across all combinations of the three dataset configurations and seven diverse downstream tasks. Across these tasks, the AUPRC was consistently improved, reaching up to 48% higher than that of the second-best model, highlighting a clinically meaningful improvement given the data imbalance. We also demonstrated that the model generates temporally stable, realistic EHR records and is capable of leveraging the calendrical component in generative modeling.

**[KR]** 우리 모델은 세 가지 데이터셋 구성과 일곱 가지 다양한 downstream task의 모든 조합에서 1위를 차지했다. 이들 작업 전반에 걸쳐 AUPRC가 일관되게 향상되어 두 번째로 우수한 모델보다 최대 48% 높은 수치에 도달했으며, 이는 데이터 불균형을 감안할 때 임상적으로 의미 있는 개선을 부각한다. 또한 우리는 이 모델이 시간적으로 안정적이고 현실적인 EHR 기록을 생성하며, 생성 모델링에서 달력적 구성 요소(calendrical component)를 활용할 수 있음을 입증했다.

**[EN]** Our contributions can be summarized as follows:
• Pathology-Focused binning: Introduces density-adjusted binning to the EHR foundation model, focusing on clinically relevant pathologic ranges.
• Dual-Calendar RoPE: Simultaneously represents both calendrical time and positional information, allowing model to capture calendrical periodicity and event concurrency.
• Time Conditioned Foresee Objective: Enables clinically aligned foreseeing training and temporal generative modeling of patient medical timelines.

**[KR]** 우리의 기여는 다음과 같이 요약할 수 있다.
• Pathology-Focused Binning: 임상적으로 관련 있는 병리적 범위에 집중하여, 밀도 조정(density-adjusted) 비닝을 EHR foundation model에 도입한다.
• Dual-Calendar RoPE: 달력적 시간과 위치 정보를 동시에 표현하여, 모델이 달력적 주기성(calendrical periodicity)과 사건 동시성(event concurrency)을 포착할 수 있게 한다.
• Time-Conditioned Foresee Objective: 임상적으로 정렬된 foreseeing 학습과 환자 의료 타임라인의 temporal generative modeling을 가능하게 한다.

## §2 Related Works

**[EN]** EHR foundation models differ from medical specialist LLMs, which rely on patient history texts summarized by clinicians. EHR foundation models learn directly from raw EHR events (Burkhart et al., 2025) and have been applied to various downstream clinical tasks (Table 1).

**[KR]** EHR foundation model은 임상의가 요약한 환자 이력 텍스트에 의존하는 의료 전문 LLM(medical specialist LLM)과 다르다. EHR foundation model은 원시 EHR 사건으로부터 직접 학습하며(Burkhart et al., 2025) 다양한 임상 downstream task에 적용되어 왔다(Table 1).

**[EN]** A common practice in EHR modeling is to represent each EHR event as a triplet of Time, Feature, and Value (Tipirneni & Reddy, 2022; Lee et al., 2023). However, many models exclude temporal and numeric data, as they are difficult to handle in standard language model frameworks. For instance, BEHRT (Li et al., 2020), Med-BERT (Rasmy et al., 2021), and others rely solely on discrete Features, omitting critical information and limiting their utility.

**[KR]** EHR 모델링에서 흔한 관행은 각 EHR 사건을 Time, Feature, Value의 triplet으로 표현하는 것이다(Tipirneni & Reddy, 2022; Lee et al., 2023). 그러나 많은 모델은 시간 데이터와 수치 데이터가 표준 언어 모델 프레임워크에서 다루기 어렵다는 이유로 이를 배제한다. 예를 들어 BEHRT(Li et al., 2020), Med-BERT(Rasmy et al., 2021) 등은 이산적(discrete) Feature에만 의존하여, 핵심 정보를 누락하고 그 효용을 제한한다.

**[EN]** Some models incorporate numeric Values but omit Time. HEART (Huang et al., 2024) discretize Values into uniform bins, mapping Feature–Value pairs to single tokens. This approach inflates the vocabulary size, leading to data sparsity. FM4EHR (Burkhart et al., 2025) addresses this by tokenizing Features and Values separately, allowing tokens to be shared.

**[KR]** 일부 모델은 수치 Value를 포함하지만 Time을 생략한다. HEART(Huang et al., 2024)는 Value를 균일 bin으로 이산화하여 Feature–Value 쌍을 단일 토큰에 매핑한다. 이 방식은 어휘 크기(vocabulary size)를 부풀려 데이터 희소성(data sparsity)을 초래한다. FM4EHR(Burkhart et al., 2025)는 Feature와 Value를 별도로 토큰화하여 토큰을 공유(share)할 수 있게 함으로써 이 문제를 해결한다.

**[EN]** In contrast, MOTOR (Steinberg et al., 2024) models Time but not Value, performing survival analysis by treating each feature's occurrence as an endpoint. Its utility is limited by its inability to handle numeric values, low temporal expressiveness based on pre-defined intervals, unrealistic constant hazard assumption, and a quadratic complexity that hinders practical application. Moreover, encoding timestamp as 'days since birth' with RoPE does not account for calendrical time.

**[KR]** 이와 대조적으로 MOTOR(Steinberg et al., 2024)는 Value가 아닌 Time을 모델링하며, 각 feature의 발생을 종점(endpoint)으로 취급하여 생존 분석(survival analysis)을 수행한다. 그러나 그 효용은 수치 값을 다루지 못한다는 점, 사전 정의된 간격에 기반한 낮은 시간 표현력, 비현실적인 상수 위험률(constant hazard) 가정, 실제 적용을 저해하는 2차(quadratic) 복잡도에 의해 제한된다. 더욱이 타임스탬프를 RoPE로 '출생 이후 일수(days since birth)'로 인코딩하는 방식은 달력적 시간을 고려하지 못한다.

**[EN]** STraTS (Tipirneni & Reddy, 2022) tokenizes only the Feature, embedding Value and Time as continuous variables to predict the next value. By modeling only P(Vnext | Epast), it loses important context and cannot support generative modeling.

**[KR]** STraTS(Tipirneni & Reddy, 2022)는 Feature만 토큰화하고 Value와 Time을 연속 변수(continuous variable)로 임베딩하여 다음 값을 예측한다. $P(V_{next} \mid E_{past})$만을 모델링하기 때문에 중요한 맥락을 잃고 생성 모델링을 지원하지 못한다.

**[EN]** TRADE (Zhu et al., 2024) and EHRmamba (Fallahpour et al., 2025) used MLM/NTP paradigms, discretizing values and applying absolute positional embeddings to Feature and Value tokens. ETHOS (Renc et al., 2024) tokenizes time intervals and insert time-interval tokens between events. This coarse discretization limits medical precision, cause cumulative errors, and increases computational cost by lengthening the sequence. Unlike positional embeddings, it requires aggregating all intervening tokens to determine a time duration. More details are provided in Appendix A

**[KR]** TRADE(Zhu et al., 2024)와 EHRmamba(Fallahpour et al., 2025)는 MLM/NTP 패러다임을 사용하여 값을 이산화하고 Feature 및 Value 토큰에 절대 위치 임베딩을 적용했다. ETHOS(Renc et al., 2024)는 시간 간격을 토큰화하여 사건들 사이에 시간 간격 토큰(time-interval token)을 삽입한다. 이러한 거친(coarse) 이산화는 의학적 정밀도를 제한하고 누적 오차(cumulative error)를 일으키며, 시퀀스를 길게 만들어 계산 비용을 증가시킨다. 위치 임베딩과 달리, 시간 지속 시간을 결정하려면 그 사이에 있는 모든 토큰을 합산(aggregate)해야 한다. 자세한 내용은 Appendix A에 제시한다.

**[EN]** To address these limitations, this work designs modeling strategies and learning objectives tailored to the unique characteristics of EHR data.

**[KR]** 이러한 한계를 해결하기 위해, 본 연구는 EHR 데이터의 고유한 특성에 맞춤화된 모델링 전략과 학습 목표를 설계한다.

## §3 Method

**[EN]** Pathology-Focused Binning. First, we estimate the value distribution non-parametrically using a Gaussian Kernel Density Estimator (KDE). $V^f_{list}$ denotes the list of all Values of Feature $f$ in the training set. We uniformly partition the value range $[\min(V^f_{list}), \max(V^f_{list})]$ with $X = \{x_1, x_2, \ldots, x_P\}$, where the inverval is $0.05\sigma$. At each discrete point $x_k \in X$, data density $\rho(x_k)$ is calcuated with Gaussian convolution kernel from all value $v_j \in V^f_{list}$. The density is:

$$\rho(x_k) = \sum_{j=1}^{|V^f_{list}|} K_h(x_k - v_j), \quad \text{s.t.} \quad K_h(u) = \exp\left(-\frac{u^2}{2(0.1\sigma)^2}\right)$$

**[KR]** Pathology-Focused Binning. 첫째, 우리는 Gaussian Kernel Density Estimator(KDE)를 사용하여 값 분포를 비모수적(non-parametric)으로 추정한다. $V^f_{list}$는 학습 집합에서 Feature $f$의 모든 Value의 리스트를 나타낸다. 우리는 값 범위 $[\min(V^f_{list}), \max(V^f_{list})]$를 $X = \{x_1, x_2, \ldots, x_P\}$로 균일하게 분할하며, 그 간격(interval)은 $0.05\sigma$이다. 각 이산점 $x_k \in X$에서, 데이터 밀도 $\rho(x_k)$는 모든 값 $v_j \in V^f_{list}$로부터 Gaussian 합성곱 커널(convolution kernel)을 이용해 계산된다. 밀도는 다음과 같다.

$$\rho(x_k) = \sum_{j=1}^{|V^f_{list}|} K_h(x_k - v_j), \quad \text{s.t.} \quad K_h(u) = \exp\left(-\frac{u^2}{2(0.1\sigma)^2}\right)$$

**[EN]** This allows us to approximate the local density $\rho(v)$ for any given value $v$. Then, we assign a weight $w(v)$ to each value that is inversely proportional to its density, effectively giving greater importance to values in sparser region ($w(v) \propto \rho(v)^{-N}; N \geq 1$). In short, values in sparse regions are assigned larger weights than those in dense regions.

**[KR]** 이를 통해 임의의 주어진 값 $v$에 대한 국소 밀도(local density) $\rho(v)$를 근사할 수 있다. 그런 다음 우리는 각 값에 그 밀도에 반비례하는 가중치 $w(v)$를 부여하여, 더 희소한 영역(sparser region)에 있는 값에 사실상 더 큰 중요도를 준다($w(v) \propto \rho(v)^{-N}; N \geq 1$). 요컨대, 희소 영역의 값에는 조밀 영역(dense region)의 값보다 더 큰 가중치가 배정된다.

**[EN]** Second, these density-based weights are used to construct the final value bins via weighted percentile binning. In this step, the contribution of each unique value $v_j$ with a raw count of $c_j$ is scaled by its weight $w(v_j)$, creating a weighted count $c'_j := c_j \cdot w(v_j)$.

**[KR]** 둘째, 이러한 밀도 기반 가중치는 가중 백분위 비닝(weighted percentile binning)을 통해 최종 값 bin을 구성하는 데 사용된다. 이 단계에서, 원시 빈도(raw count) $c_j$를 갖는 각 고유 값 $v_j$의 기여도는 그 가중치 $w(v_j)$로 스케일링되어 가중 빈도(weighted count) $c'_j := c_j \cdot w(v_j)$를 만든다.

**[EN]** Bin thresholds are then determined from the cumulative distribution of these weighted counts. As a result, high-weight values from pathologic ranges command a larger share of the percentile space, leading to a finer-grained partitioning in these clinically important areas (Figure 2A). The detailed methodology is described in Appendix B.1.

**[KR]** 그런 다음 bin 임계값(threshold)은 이 가중 빈도들의 누적 분포(cumulative distribution)로부터 결정된다. 그 결과, 병리적 범위의 높은 가중치 값들이 백분위 공간(percentile space)에서 더 큰 몫을 차지하게 되어, 이러한 임상적으로 중요한 영역에서 더 세분화된 분할이 이루어진다(Figure 2A). 자세한 방법론은 Appendix B.1에 기술되어 있다.

**[EN]** Figure 2: (A) Uniform binning concentrates bins in dense, physiologic ranges. In contrast, our density-based method allocates more bins to medically significant pathologic ranges. (B) Events at the same time are distinguished by their positional distance. Events occurring at the same time on different dates share the same representation for time units below a day but have different representations for units of a day or longer. (C) Illustrates TCF objective of a single timestep (actual model training is fully parallel, like NTP). The TCF objective consists of $L_{next\ time}$ and $L_{foresee}$. The last hidden state is passed through a time head to predict the interval to the next event in a calendrical format ($L_{next\ time}$). Then, the times to multiple future events are re-input and combined with the last hidden state to predict the events at those specific times ($L_{foresee}$).

**[KR]** Figure 2: (A) 균일 비닝은 조밀한 생리적 범위에 bin을 집중시킨다. 반면 우리의 밀도 기반 방법은 의학적으로 중요한 병리적 범위에 더 많은 bin을 할당한다. (B) 동일한 시각의 사건들은 위치 거리(positional distance)로 구별된다. 서로 다른 날짜의 같은 시각에 발생한 사건들은 하루 미만의 시간 단위에 대해서는 동일한 표현을 공유하지만, 하루 이상의 단위에 대해서는 서로 다른 표현을 갖는다. (C) 단일 타임스텝의 TCF objective를 나타낸다(실제 모델 학습은 NTP처럼 완전히 병렬로 이루어진다). TCF objective는 $L_{next\ time}$과 $L_{foresee}$로 구성된다. 마지막 hidden state는 time head를 거쳐 다음 사건까지의 간격을 달력 형식(calendrical format)으로 예측한다($L_{next\ time}$). 그런 다음 여러 미래 사건까지의 시간이 다시 입력되어 마지막 hidden state와 결합됨으로써, 해당 특정 시각의 사건들을 예측한다($L_{foresee}$).

**[EN]** Dual-Calendar Rotary Position Embedding. Second, we propose a novel positional encoding designed for the temporal characteristics of EHR (Figure 2). It jointly models the relative order and calendrical interval by partitioning the dimension of each query and key vector, $x \in \mathbb{R}^d$, into a positional component $x_{pos} \in \mathbb{R}^{d_{pos}}$ and a temporal component $x_{time} \in \mathbb{R}^{d_{time}}$ ($d = d_{pos} + d_{time}$):

$$x = [x_{pos} \| x_{time}]$$

**[KR]** Dual-Calendar Rotary Position Embedding. 둘째, 우리는 EHR의 시간적 특성을 위해 설계된 새로운 위치 인코딩(positional encoding)을 제안한다(Figure 2). 이는 각 query 및 key 벡터 $x \in \mathbb{R}^d$의 차원을 위치 성분(positional component) $x_{pos} \in \mathbb{R}^{d_{pos}}$와 시간 성분(temporal component) $x_{time} \in \mathbb{R}^{d_{time}}$($d = d_{pos} + d_{time}$)로 분할함으로써, 상대 순서(relative order)와 달력 간격(calendrical interval)을 함께 모델링한다.

$$x = [x_{pos} \| x_{time}]$$

**[EN]** The $x_{pos}$ component uses a standard RoPE to encode the relative token position, $p$. With a reduced dimensionality ($d \to d_{pos}$), it employs a truncated frequency spectrum. This strategic choice focuses its role on disambiguating the order of co-occurring events sharing an identical timestamp, while long-range dependencies are handled by the temporal component. The rotation angle is defined as:

$$\theta^{(pos)}_{p,i} = \frac{p}{10000^{2i/d}}, \quad i \in \{0, 1, \ldots, d_{pos}/2 - 1\}$$

**[KR]** $x_{pos}$ 성분은 표준 RoPE를 사용하여 상대적 토큰 위치 $p$를 인코딩한다. 차원이 축소됨($d \to d_{pos}$)에 따라, 이는 절단된 주파수 스펙트럼(truncated frequency spectrum)을 사용한다. 이러한 전략적 선택은 그 역할을 동일한 타임스탬프를 공유하는 동시 발생 사건(co-occurring event)의 순서를 명확히 구분하는 데 집중시키며, 장기 의존성은 시간 성분이 처리하도록 한다. 회전 각도(rotation angle)는 다음과 같이 정의된다.

$$\theta^{(pos)}_{p,i} = \frac{p}{10000^{2i/d}}, \quad i \in \{0, 1, \ldots, d_{pos}/2 - 1\}$$

**[EN]** The core of our method, the $x_{time}$ component, encodes the second-level timestamp $t$. This is achieved using a predefined set of semantically meaningful calendrical periods (e.g., minute=60s, hour=3600s,...; see Table 5 for a full list). For each period $s_j$ in the set, a rotation angle $\theta^{(time)}_{t,j}$ is calculated as the phase of the event within that period:

$$\theta^{(time)}_{t,j} = \left(\frac{t \bmod s_j}{s_j}\right) \cdot 2\pi, \quad j \in \{0, 1, \ldots, d_{time}/2 - 1\}$$

**[KR]** 우리 방법의 핵심인 $x_{time}$ 성분은 초 단위(second-level) 타임스탬프 $t$를 인코딩한다. 이는 의미적으로 유의미한 달력 주기(calendrical period)의 사전 정의된 집합(예: 분=60초, 시간=3600초, …; 전체 목록은 Table 5 참조)을 사용하여 달성된다. 집합 내 각 주기 $s_j$에 대해, 회전 각도 $\theta^{(time)}_{t,j}$는 그 주기 내 사건의 위상(phase)으로 계산된다.

$$\theta^{(time)}_{t,j} = \left(\frac{t \bmod s_j}{s_j}\right) \cdot 2\pi, \quad j \in \{0, 1, \ldots, d_{time}/2 - 1\}$$

**[EN]** The two components are rotated independently using their respective angles and then concatenated to form the final query vector $q'$ (and also for the key). This allows the attention mechanism to simultaneously address both sequential order and calendrical time (More details in Appendix B.2).

$$q' = [\text{RoPE}(q_{pos}, \theta^{(pos)}) \| \text{RoPE}(q_{time}, \theta^{(time)})]$$

**[KR]** 두 성분은 각각의 각도를 사용하여 독립적으로 회전된 뒤, 연결(concatenate)되어 최종 query 벡터 $q'$를 형성한다(key에 대해서도 동일). 이를 통해 attention 메커니즘은 순차적 순서(sequential order)와 달력적 시간(calendrical time)을 동시에 다룰 수 있다(자세한 내용은 Appendix B.2).

$$q' = [\text{RoPE}(q_{pos}, \theta^{(pos)}) \| \text{RoPE}(q_{time}, \theta^{(time)})]$$

**[EN]** Time-Conditioned Foresee Objective (TCF). Lastly, we propose a novel learning objective to effectively model the temporal dynamics of EHR data. TCF employs a dual-objective structure (Figure 2C) that simultaneously learns to: (1) predict when the next event will occur ($P(\Delta T_{next} | E_{past})$), and (2) foresee what event will happen at a specified future time ($P(F_{foresee} | \Delta T_{foresee}, E_{past})$), unlike NTP which only models $P(F_{next} | E_{past})$.

**[KR]** Time-Conditioned Foresee Objective(TCF). 마지막으로, 우리는 EHR 데이터의 시간적 동역학(temporal dynamics)을 효과적으로 모델링하기 위한 새로운 학습 목표를 제안한다. TCF는 $P(F_{next} \mid E_{past})$만 모델링하는 NTP와 달리, (1) 다음 사건이 언제 발생할지 예측하고($P(\Delta T_{next} \mid E_{past})$), (2) 지정된 미래 시각에 어떤 사건이 일어날지 예견하는($P(F_{foresee} \mid \Delta T_{foresee}, E_{past})$) 것을 동시에 학습하는 이중 목표(dual-objective) 구조(Figure 2C)를 사용한다.

**[EN]** The TCF module is placed after the transformer backbone. It takes the final hidden state $h_{last} \in \mathbb{R}^{d_{model}}$ as input and outputs both a next time prediction loss and a conditioned hidden states for future event prediction.

**[KR]** TCF 모듈은 transformer backbone 뒤에 배치된다. 이는 최종 hidden state $h_{last} \in \mathbb{R}^{d_{model}}$를 입력으로 받아, 다음 시간 예측 손실(next time prediction loss)과 미래 사건 예측을 위한 조건화된 hidden state를 모두 출력한다.[각주2]

**[EN]** To generate a calendrical ground-truth label for $\Delta T_{next}$, the time delta, expressed in seconds, is transformed into an integer vector of dimension $N_{scales}$. Each element of this vector corresponds to a predefined calendrical time unit, ranging from 10-year to 1-minute (e.g., $[\alpha, \beta, \gamma, \ldots]$ represents a time composed of $\alpha$ years, $\beta$ months, $\gamma$ days, etc.).

**[KR]** $\Delta T_{next}$에 대한 달력적 정답 레이블(calendrical ground-truth label)을 생성하기 위해, 초 단위로 표현된 시간 차(time delta)를 차원 $N_{scales}$의 정수 벡터로 변환한다. 이 벡터의 각 원소는 10년에서 1분에 이르는 사전 정의된 달력 시간 단위(calendrical time unit)에 대응한다(예: $[\alpha, \beta, \gamma, \ldots]$는 $\alpha$년, $\beta$월, $\gamma$일 등으로 구성된 시간을 나타낸다).

[각주2] 각주 원문: 실제로는 NTP와 유사하게 전체 마지막 hidden state $H_{last} \in \mathbb{R}^{B \times L \times d_{model}}$가 병렬로 처리된다.

**[EN]** To predict $\Delta T_{next}$ from $h_{last}$, the last hidden is projected into #$N_{scales}$ vectors of size $d_{embed}$. Each of these vectors is transformed into time-logit through the unembedding layer.

$$h_{time} = \text{FFN}_{enc}(h_{last}) \in \mathbb{R}^{(N_{scales} \cdot d_{embed})} \to \{h^{(i)}_{time}\}_{i=1}^{N_{scales}}, \quad \text{time-logits}^{(i)} = h^{(i)}_{time} \cdot (W^{(i)}_{embed})^T$$

**[KR]** $h_{last}$로부터 $\Delta T_{next}$를 예측하기 위해, 마지막 hidden은 크기 $d_{embed}$인 $N_{scales}$개의 벡터로 투영(project)된다. 이 벡터들 각각은 unembedding 레이어를 통해 time-logit으로 변환된다.

$$h_{time} = \text{FFN}_{enc}(h_{last}) \in \mathbb{R}^{(N_{scales} \cdot d_{embed})} \to \{h^{(i)}_{time}\}_{i=1}^{N_{scales}}, \quad \text{time-logits}^{(i)} = h^{(i)}_{time} \cdot (W^{(i)}_{embed})^T$$

**[EN]** $L_{next\ time}$ is Cross-Entropy loss between these $\{\text{time-logit}^{(i)}_{time}\}_{i=1}^{N_{scales}}$ and the calendrical $\Delta T_{next}$ labels, averaged over $N_{scales}$.

**[KR]** $L_{next\ time}$은 이 $\{\text{time-logit}^{(i)}_{time}\}_{i=1}^{N_{scales}}$와 달력적 $\Delta T_{next}$ 레이블 사이의 Cross-Entropy 손실로, $N_{scales}$에 대해 평균을 취한 것이다.

**[EN]** For foreseeing future events, a Time-Conditioning process is performed. We aim to predict the Feature of $N_{foresee}$ future events. A given future time deltas, $\Delta T_{foresee}$, is first transformed into a vector of integer labels ($C_{foresee} \in \mathbb{Z}^{N_{foresee} \times N_{scales}}$) using the same multi-scale decomposition. These labels are passed through embedding layers to produce a comprehensive time embedding, $e_{time} \in \mathbb{R}^{N_{foresee} \times (N_{scales} \cdot d_{embed})}$. Finally, this time embedding is fused with the original hidden state $h_{last}$ via a residual connection to produce a time conditioned hidden state, $h_{conditioned}$.

$$h_{conditioned} = \text{FFN}(\text{LayerNorm}(h_{last} + \text{FFN}(e_{time}))) \in \mathbb{R}^{N_{foresee} \times d_{model}}$$

**[KR]** 미래 사건을 예견하기 위해 Time-Conditioning 과정을 수행한다. 우리는 $N_{foresee}$개의 미래 사건의 Feature를 예측하는 것을 목표로 한다. 주어진 미래 시간 차들 $\Delta T_{foresee}$는 먼저 동일한 다중 스케일 분해(multi-scale decomposition)를 사용해 정수 레이블 벡터($C_{foresee} \in \mathbb{Z}^{N_{foresee} \times N_{scales}}$)로 변환된다. 이 레이블들은 임베딩 레이어를 거쳐 종합적인 시간 임베딩 $e_{time} \in \mathbb{R}^{N_{foresee} \times (N_{scales} \cdot d_{embed})}$를 생성한다. 마지막으로, 이 시간 임베딩은 잔차 연결(residual connection)을 통해 원래의 hidden state $h_{last}$와 융합되어 time-conditioned hidden state $h_{conditioned}$를 만든다.

$$h_{conditioned} = \text{FFN}(\text{LayerNorm}(h_{last} + \text{FFN}(e_{time}))) \in \mathbb{R}^{N_{foresee} \times d_{model}}$$

**[EN]** This $h_{conditioned}$ is projected to token-logit $\in \mathbb{R}^{N_{foresee} \times \text{vocab size}}$ that predicts the clinical event (Feature) that occur at the corresponding future timestamps.

**[KR]** 이 $h_{conditioned}$는 해당 미래 타임스탬프에 발생하는 임상 사건(Feature)을 예측하는 token-logit $\in \mathbb{R}^{N_{foresee} \times \text{vocab size}}$로 투영된다.

**[EN]** $L_{foresee}$ is Cross-Entropy loss between the future events and the token-logit, averaged over $N_{foresee}$. Through this dual-objective learning ($L = L_{next\ time} + L_{foresee}$), our model acquires the ability to accurately and generatively model a patient's entire medical timeline.

**[KR]** $L_{foresee}$는 미래 사건과 token-logit 사이의 Cross-Entropy 손실로, $N_{foresee}$에 대해 평균을 취한 것이다. 이러한 이중 목표 학습($L = L_{next\ time} + L_{foresee}$)을 통해 우리 모델은 환자의 전체 의료 타임라인을 정확하고 생성적으로 모델링하는 능력을 획득한다.

**[EN]** So far, we have considered the position where Feature is predicted given the previous events. Modeling Value given the previous events and Feature is carried out in the same manner. Since $F$ and $V$ belong to the same event and thus share the time label, we always have $\Delta T_{next} = 0$. Moreover, because $V$ is conditioned on the preceding $F$, we predict $V_{now}$ by modeling

$$P(V_{foresee} | \Delta T_{foresee}, F_{now}, E_{past})$$

while inserting only a zero into $\Delta T_{foresee}$. More detailed explanation and tensor-level parallel processing are provided in Appendix B.3.

**[KR]** 지금까지 우리는 이전 사건들이 주어졌을 때 Feature가 예측되는 위치를 고려했다. 이전 사건들과 Feature가 주어졌을 때 Value를 모델링하는 것도 동일한 방식으로 수행된다. $F$와 $V$는 같은 사건에 속하여 시간 레이블을 공유하므로, 항상 $\Delta T_{next} = 0$이다. 더욱이 $V$는 선행하는 $F$에 조건화되므로, 우리는 $\Delta T_{foresee}$에 0만 삽입한 채

$$P(V_{foresee} | \Delta T_{foresee}, F_{now}, E_{past})$$

를 모델링하여 $V_{now}$를 예측한다. 더 자세한 설명과 텐서 수준의 병렬 처리(tensor-level parallel processing)는 Appendix B.3에 제시되어 있다.

### §3.1 Data and Preprocessing

**[EN]** Table 2: Data summary. Parentheses indicate cases where bins are not shared. MIMIC-III preprocessed — Total Patient #: 28,728 / 5,070 (Train / Test); Total Hospitalization #: 35,730 / 6,295; Total Events #: 38,641,175 / 6,744,906; Total Tokens #: 77,109,833 / 13,459,430; Avg. length: 2,684 / 2,655; Max length: 393,337 / 62,759; Unique Tokens #: 155 (1,208); Token # bin: 10; Token # ethnicity: 10; Token # vital signs: 17; Token # laboratory tests: 100.

**[KR]** Table 2: 데이터 요약. 괄호는 bin이 공유되지 않는 경우를 나타낸다. MIMIC-III 전처리본 — 총 환자 수: 28,728 / 5,070 (Train / Test); 총 입원 수: 35,730 / 6,295; 총 사건 수: 38,641,175 / 6,744,906; 총 토큰 수: 77,109,833 / 13,459,430; 평균 길이: 2,684 / 2,655; 최대 길이: 393,337 / 62,759; 고유 토큰 수: 155 (1,208); bin 토큰 수: 10; ethnicity 토큰 수: 10; 활력징후(vital signs) 토큰 수: 17; 검사(laboratory tests) 토큰 수: 100.

**[EN]** While many EHR models rely on private datasets and often do not release their code or parameters—making reproduction and evaluation difficult—we use a publicly available dataset and provide open-source code throughout all stages. Specifically, we employ the MIMIC-III Clinical Database v1.4 (Johnson et al., 2016a), which contains comprehensive clinical data from over 30,000 patients. We adopt the widely used preprocessing and train/test split pipeline introduced by Harutyunyan et al. (2019). A summary of the dataset is provided in Table 2. Further details are provided in Appendix C. Tasks necessitating clinical judgment, such as defining exclusion criteria and outlier removal, were independently reviewed by an internist, an otolaryngologist, and a general physician.

**[KR]** 많은 EHR 모델이 비공개 데이터셋에 의존하고 코드나 파라미터를 공개하지 않는 경우가 많아 재현과 평가가 어려운 반면, 우리는 공개적으로 이용 가능한 데이터셋을 사용하고 모든 단계에 걸쳐 오픈소스 코드를 제공한다. 구체적으로, 우리는 3만 명 이상의 환자에 대한 포괄적 임상 데이터를 담고 있는 MIMIC-III Clinical Database v1.4(Johnson et al., 2016a)를 사용한다. 우리는 Harutyunyan et al.(2019)이 도입한 널리 사용되는 전처리 및 train/test 분할 파이프라인을 채택한다. 데이터셋 요약은 Table 2에 제시되어 있다. 추가적인 세부 사항은 Appendix C에 있다. 제외 기준(exclusion criteria) 정의와 이상치 제거(outlier removal)처럼 임상적 판단이 필요한 작업은 내과 전문의, 이비인후과 전문의, 일반의가 각각 독립적으로 검토했다.

### §3.2 Backbone Architecture, Baseline Models, and Pre-training

**[EN]** We used a Transformer decoder as the backbone for all experiments. For Dual-calendar RoPE, the first 24 dimensions of the 64-dim K and Q vectors encode positional information, and the remaining 40 dimensions encode calendric time. Baseline models were reproduced under identical conditions, including backbone and training data. We mostly followed the original papers' implementations but made necessary modifications where direct application was infeasible (e.g., adapting the MOTOR model to numeric value events). The pre-training input token length was fixed at 2048. Sequences exceeding this length (Appendix Figure 7) were segmented with a 512-token overlap, and we ensured that a single event's $F$ and $V$ were not split at the segmentation point. A detailed description of our model, baselines, and pre-training can be found in Appendix D.

**[KR]** 우리는 모든 실험에서 Transformer decoder를 backbone으로 사용했다. Dual-Calendar RoPE의 경우, 64차원 K 및 Q 벡터의 첫 24차원은 위치 정보를, 나머지 40차원은 달력적 시간을 인코딩한다. Baseline 모델들은 backbone과 학습 데이터를 포함해 동일한 조건에서 재현되었다. 우리는 대부분 원논문의 구현을 따랐으나, 직접 적용이 불가능한 경우(예: MOTOR 모델을 수치 값 사건에 맞게 적응)에는 필요한 수정을 가했다. 사전학습 입력 토큰 길이는 2048로 고정했다. 이 길이를 초과하는 시퀀스(Appendix Figure 7)는 512-토큰 중첩(overlap)으로 분할했으며, 단일 사건의 $F$와 $V$가 분할 지점에서 쪼개지지 않도록 보장했다. 우리 모델, baseline, 사전학습에 대한 자세한 설명은 Appendix D에서 확인할 수 있다.

## §4 Result

### §4.1 Downstream Task and Fine-tuning

**[EN]** Table 3: Results on downstream tasks using EHR datasets with 117, 17, and 6 features. The Test loss column reports the overall test loss for each feature set (lower is better). For 117 features, we report performance on seven downstream tasks ranging from IHM to Vaso. Binary classification tasks are measured by AUROC (ROC) and AUPRC (PRC), while multiclass tasks are evaluated with macro F1 (Ma-f1) and Cohen's Kappa. For tasks with multiple subtasks, both macro and micro AUROC are reported. We trained our model with and without value sharing; in both cases, it outperformed all other baselines. Full downstream task results are provided in Appendix Table 9-11.

**[KR]** Table 3: 117, 17, 6개 feature를 가진 EHR 데이터셋을 사용한 downstream task 결과. Test loss 열은 각 feature 집합에 대한 전체 테스트 손실을 보고한다(낮을수록 좋음). 117 feature에 대해서는 IHM부터 Vaso까지 일곱 가지 downstream task의 성능을 보고한다. 이진 분류 작업은 AUROC(ROC)와 AUPRC(PRC)로 측정하고, 다중 클래스 작업은 macro F1(Ma-f1)과 Cohen's Kappa로 평가한다. 여러 하위 작업(subtask)을 가진 작업에 대해서는 macro와 micro AUROC를 모두 보고한다. 우리는 모델을 value sharing을 적용한 경우와 적용하지 않은 경우 모두로 학습했으며, 두 경우 모두 다른 모든 baseline을 능가했다. 전체 downstream task 결과는 Appendix Table 9–11에 제시되어 있다.

**[EN]** Table 4: Ablation study on Pathology-Focused Binning (Binning), Dual-Calendar Rotary Positional Embedding (Embedding), and Time-Conditioned Foreseeing (Objective). [Binning ✓ / Embedding ✓ / Objective ✓ → Test loss 4.686]; [Uniform / ✓ / ✓ → 4.713]; [Uniform / RoPE / ✓ → 4.810]; [Uniform / RoPE / NTP → 5.241].

**[KR]** Table 4: Pathology-Focused Binning(Binning), Dual-Calendar Rotary Positional Embedding(Embedding), Time-Conditioned Foreseeing(Objective)에 대한 ablation 연구. [Binning ✓ / Embedding ✓ / Objective ✓ → Test loss 4.686]; [Uniform / ✓ / ✓ → 4.713]; [Uniform / RoPE / ✓ → 4.810]; [Uniform / RoPE / NTP → 5.241].

**[EN]** We evaluated our model on a range of clinical downstream tasks commonly used in EHR model evaluation. These tasks, defined by clinical labels excluded from training, are not direct measures of generative modeling performance but serve as proxies for the quality of patient representations. In addition to the four MIMIC-III benchmark (Harutyunyan et al., 2019) tasks—In-hospital Mortality (IHM), Decompensation-death (Dec-death), Length of Stay (LOS), and Phenotyping (Phe)—we included three additional tasks: Decompensation-arrest (Dec-arrest), Oliguria/Anuria (HUO), and Vasopressor (Vaso) use. Label counts for all tasks are provided in Appendix Table 8, with detailed descriptions in Appendix E.1.

**[KR]** 우리는 EHR 모델 평가에 흔히 사용되는 다양한 임상 downstream task에서 우리 모델을 평가했다. 학습에서 제외된 임상 레이블로 정의되는 이 작업들은 생성 모델링 성능을 직접 측정하는 것이 아니라, 환자 표현(patient representation)의 품질을 가늠하는 대리 지표(proxy) 역할을 한다. 네 가지 MIMIC-III 벤치마크(Harutyunyan et al., 2019) 작업—원내 사망(In-hospital Mortality, IHM), 악화-사망(Decompensation-death, Dec-death), 재원 기간(Length of Stay, LOS), 표현형 분류(Phenotyping, Phe)—에 더해, 우리는 세 가지 추가 작업을 포함했다: 악화-심정지(Decompensation-arrest, Dec-arrest), 핍뇨/무뇨(Oliguria/Anuria, HUO), 승압제(Vasopressor, Vaso) 사용. 모든 작업의 레이블 개수는 Appendix Table 8에, 자세한 설명은 Appendix E.1에 제시되어 있다.

**[EN]** Downstream task-specific prediction heads were attached to the backbone. Since labels must be inferred using only information up to each timestep, a causal mask was applied for all baselines. To evaluate generalization to data with different distributions (e.g., missing lab information), we experimented with three input configurations: all 117 features, 17 vital signs (without lab data), and only 6 vital signs (SBP, DBP, body temperature, heart rate, respiratory rate, SpO2). Please refer to Appendix E.2 for more details.

**[KR]** Downstream task별 예측 헤드(prediction head)를 backbone에 부착했다. 레이블은 각 타임스텝까지의 정보만 사용해 추론해야 하므로, 모든 baseline에 causal mask를 적용했다. 서로 다른 분포의 데이터(예: 검사 정보 결측)에 대한 일반화를 평가하기 위해, 우리는 세 가지 입력 구성으로 실험했다: 전체 117 feature, 17개 활력징후(검사 데이터 없이), 그리고 6개 활력징후만(SBP, DBP, 체온, 심박수, 호흡수, SpO2). 자세한 내용은 Appendix E.2를 참조하라.

**[EN]** Table 3 summarizes the results on downstream tasks. To ensure fair comparison, we trained our model with and without value sharing and compared each setting to the corresponding baselines. In both cases, our model consistently outperformed all baselines across the three input configurations and all downstream tasks. Notably, for the decompensation task, which predicts patient death or arrest up to 24 hours in advance, our model achieved an AUPRC nearly 50% higher than that of the second-best model. Given the severe class imbalance in these tasks (positive:negative ratio of 1:40), this represents a significant improvement in real-world clinical settings where high precision is crucial. Additionally, the ablation study (Table 4) shows that all three of our proposed methods contribute substantially to the performance improvement. Figure 3 shows the ROC curves with 95% confidence intervals, confirming that our model achieves statistically significant improvements over the second-best model in most tasks. The complete results for all three input configurations can be found in Appendix F.1.

**[KR]** Table 3은 downstream task 결과를 요약한다. 공정한 비교를 위해 우리는 모델을 value sharing을 적용한 경우와 적용하지 않은 경우로 학습하고, 각 설정을 대응하는 baseline과 비교했다. 두 경우 모두에서 우리 모델은 세 가지 입력 구성과 모든 downstream task에 걸쳐 일관되게 모든 baseline을 능가했다. 특히 환자의 사망 또는 심정지를 최대 24시간 전에 예측하는 decompensation 작업에서, 우리 모델은 두 번째로 우수한 모델보다 거의 50% 높은 AUPRC를 달성했다. 이러한 작업의 심각한 클래스 불균형(양성:음성 비율 1:40)을 고려할 때, 이는 높은 정밀도가 중요한 실제 임상 환경에서 유의미한 개선을 의미한다. 또한 ablation 연구(Table 4)는 우리가 제안한 세 가지 방법 모두가 성능 향상에 상당히 기여함을 보여 준다. Figure 3은 95% 신뢰구간을 포함한 ROC 곡선을 보여 주며, 우리 모델이 대부분의 작업에서 두 번째로 우수한 모델 대비 통계적으로 유의미한 개선을 달성함을 확인해 준다. 세 가지 입력 구성 모두에 대한 완전한 결과는 Appendix F.1에서 확인할 수 있다.

**[EN]** Figure 3: AUROC curves of our model and the second-best baseline, with 95% confidence intervals estimated via bootstrapping. LOS was evaluated as a binary classification for the first class, and Phenotyping was assessed using micro-ROC. For HUO, both oliguria and anuria are presented.

**[KR]** Figure 3: 우리 모델과 두 번째로 우수한 baseline의 AUROC 곡선으로, 95% 신뢰구간은 부트스트래핑(bootstrapping)으로 추정했다. LOS는 첫 번째 클래스에 대한 이진 분류로 평가했고, Phenotyping은 micro-ROC로 평가했다. HUO의 경우 핍뇨(oliguria)와 무뇨(anuria)를 모두 제시한다.

**[EN]** Figure 4: Given the initial record (orange), the subsequent medical history is generated (blue). PEEP: Positive end-expiratory pressure, ER: emergency lab.

**[KR]** Figure 4: 초기 기록(주황색)이 주어지면 이후의 의료 이력이 생성된다(파란색). PEEP: 호기말 양압(Positive end-expiratory pressure), ER: 응급 검사(emergency lab).

### §4.2 Temporal Generative Modeling

**[EN]** Our model is the first to generate fine-grained temporal information and clinical events conditioned on time, demonstrating strong temporal generative modeling of EHR data. To qualitatively assess its effectiveness, we compared it (share ver. for fair comparison) with ETHOS, which, despite limitations in temporal modeling, is one of the few approaches capable of generating temporal information. Since ETHOS outputs time range tokens, timestamps were sampled and rounded to the nearest 5 minutes to match the resolution of MIMIC-III (only for ETHOS). For both models, binned measurement values were decoded to actual values by sampling from the empirical distributions of the training data.

**[KR]** 우리 모델은 세밀한(fine-grained) 시간 정보와 시간에 조건화된 임상 사건을 생성하는 최초의 모델로, EHR 데이터의 강력한 temporal generative modeling을 입증한다. 그 효과를 정성적으로 평가하기 위해, 우리는 (공정한 비교를 위해 share 버전으로) ETHOS와 비교했는데, ETHOS는 시간 모델링에 한계가 있음에도 시간 정보를 생성할 수 있는 몇 안 되는 접근법 중 하나다. ETHOS는 시간 범위 토큰(time range token)을 출력하므로, MIMIC-III의 해상도에 맞추기 위해 타임스탬프를 샘플링하고 가장 가까운 5분 단위로 반올림했다(ETHOS에 한해). 두 모델 모두에서, 비닝된 측정값은 학습 데이터의 경험적 분포(empirical distribution)에서 샘플링하여 실제 값으로 디코딩했다.

**[EN]** Figure 5: Generated patient EHRs were evaluated by five physicians and five non-medical participants and four LLMs, with 100 comparison responses collected for each category.

**[KR]** Figure 5: 생성된 환자 EHR을 다섯 명의 의사, 다섯 명의 비의료인 참가자, 그리고 네 개의 LLM이 평가했으며, 각 범주마다 100개의 비교 응답을 수집했다.

**[EN]** Figure 4 presents generated medical history sequences from our model and ETHOS, given the same initial EHR records. From a content perspective, the Glasgow Coma Scale (GCS) should equal the sum of GCS-E/V/M. At 10-02 14:00, our model generated E:1, V:1, M:1; GCS:3, correctly capturing this relationship, whereas ETHOS produced E:2, V:1, M:5; GCS:3, which is inconsistent. Moreover, our model reflected early emergency labs and a variety of tests, followed by routine vital sign checks, while ETHOS generated no labs. From a temporal perspective, our model first performed several tests at short intervals after admission, then naturally returned to an hourly routine. In contrast, ETHOS produced events at irregular intervals and often failed to follow the typical hourly schedule.

**[KR]** Figure 4는 동일한 초기 EHR 기록이 주어졌을 때 우리 모델과 ETHOS가 생성한 의료 이력 시퀀스를 제시한다. 내용 측면에서, Glasgow Coma Scale(GCS)은 GCS-E/V/M의 합과 같아야 한다. 10-02 14:00 시점에 우리 모델은 E:1, V:1, M:1; GCS:3을 생성하여 이 관계를 정확히 포착한 반면, ETHOS는 E:2, V:1, M:5; GCS:3을 산출하여 일관성이 없었다. 더욱이 우리 모델은 초기 응급 검사와 다양한 검사를 반영한 뒤 일상적 활력징후 점검으로 이어진 반면, ETHOS는 검사를 전혀 생성하지 않았다. 시간 측면에서, 우리 모델은 입원 후 짧은 간격으로 여러 검사를 먼저 수행한 뒤 자연스럽게 시간별 일과(hourly routine)로 복귀했다. 반면 ETHOS는 불규칙한 간격으로 사건을 산출했고, 전형적인 시간별 일정을 따르지 못하는 경우가 많았다.

**[EN]** We further evaluated 100 generated samples with three evaluator groups: physicians (n=5), non-medical participants (n=5), and commercial LLMs (n=4; ChatGPT (via API, accessed Sep 2025), Gemini 2.5 Flash (via API), 2.5 Pro (via API), Claude 4 Sonnet (via API)). After reviewing up to 10 ground-truth EHR samples, each group assessed subsequent EHR records generated from the same initial records. Figure 5 shows that our model consistently outperformed ETHOS. The LLM input prompts and the generated samples are presented in Appendix F.2.

**[KR]** 우리는 더 나아가 세 평가자 그룹으로 100개의 생성 샘플을 평가했다: 의사(n=5), 비의료인 참가자(n=5), 상용 LLM(n=4; ChatGPT(API 경유, 2025년 9월 접속), Gemini 2.5 Flash(API 경유), 2.5 Pro(API 경유), Claude 4 Sonnet(API 경유)). 최대 10개의 정답 EHR 샘플을 검토한 후, 각 그룹은 동일한 초기 기록으로부터 생성된 이후 EHR 기록을 평가했다. Figure 5는 우리 모델이 ETHOS를 일관되게 능가했음을 보여 준다. LLM 입력 프롬프트와 생성된 샘플은 Appendix F.2에 제시되어 있다.

**[EN]** To verify whether our model effectively integrates calendrical information, we generated vital signs conditioned on time across a 24-hour window (00:00–24:00) based on the same patient history. Figure 6 illustrates that our model generated higher heart rate and temperature values during daytime hours, reflecting realistic circadian variation. In contrast, ETHOS, even for the control variable Height, produced clinically implausible patterns across all cases.

**[KR]** 우리 모델이 달력적 정보를 효과적으로 통합하는지 검증하기 위해, 우리는 동일한 환자 이력을 기반으로 24시간 구간(00:00–24:00)에 걸쳐 시간에 조건화된 활력징후를 생성했다. Figure 6은 우리 모델이 주간 시간대에 더 높은 심박수와 체온 값을 생성하여 현실적인 일주기 변동(circadian variation)을 반영함을 보여 준다. 반면 ETHOS는 통제 변수인 신장(Height)에 대해서조차 모든 경우에 임상적으로 타당하지 않은 패턴을 산출했다.

**[EN]** Figure 6: Assessment of the model's ability to capture calendrical temporal patterns. Heart rate, body temperature, and respiratory rate are physiologically higher during the day and lower at night. Using these three features along with height as a control, we let the model sequentially generate predictions across 00:00–24:00, averaged over 1,000 test samples.

**[KR]** Figure 6: 달력적 시간 패턴을 포착하는 모델 능력에 대한 평가. 심박수, 체온, 호흡수는 생리적으로 낮에 더 높고 밤에 더 낮다. 통제 변수로서의 신장과 함께 이 세 가지 feature를 사용하여, 우리는 모델이 00:00–24:00에 걸쳐 순차적으로 예측을 생성하도록 했으며, 1,000개의 테스트 샘플에 대해 평균을 취했다.

## §5 Conclusion

**[EN]** We present a novel approach for modeling the unique characteristics of Electronic Health Record (EHR) data, including irregular time intervals and complex numerical values. This work introduces three key contributions: Pathology-Focused Binning to emphasize clinically significant numerical ranges, Dual-Calendar Rotary Position Embedding (RoPE) to encode relative and absolute calendrical time, and a Time-Conditioned Foreseeing (TCF) training objective. TCF enables temporal generative modeling by predicting future timestamps and forecasting events, reflecting clinical planning. Our model outperforms existing foundation models on seven downstream tasks with up to 48% improvement in AUPRC, while generating realistic and temporally consistent EHRs for long-range clinical forecasting. Limitations: There is currently no established metric to evaluate the temporal generative performance of EHR models. Assessing the appropriateness of timing is crucial, making conventional methods used for evaluating LLM generation difficult to apply. Developing quantitative evaluation metrics for EHR generation will be important for advancing EHR foundation models.

**[KR]** 우리는 불규칙한 시간 간격과 복잡한 수치 값을 포함한 전자의무기록(EHR) 데이터의 고유한 특성을 모델링하기 위한 새로운 접근법을 제시한다. 본 연구는 세 가지 핵심 기여를 도입한다: 임상적으로 중요한 수치 범위를 강조하는 Pathology-Focused Binning, 상대적 및 절대적 달력 시간을 인코딩하는 Dual-Calendar Rotary Position Embedding(RoPE), 그리고 Time-Conditioned Foreseeing(TCF) 학습 목표이다. TCF는 미래 타임스탬프를 예측하고 사건을 예측함으로써 임상 계획을 반영하며 temporal generative modeling을 가능하게 한다. 우리 모델은 일곱 가지 downstream task에서 기존 foundation model들을 능가하며 AUPRC를 최대 48%까지 개선하는 한편, 장기 임상 예측을 위한 현실적이고 시간적으로 일관된 EHR을 생성한다. 한계점: 현재 EHR 모델의 temporal generative 성능을 평가할 확립된 지표(metric)가 없다. 타이밍의 적절성을 평가하는 것이 핵심적인데, 이로 인해 LLM 생성 평가에 사용되는 기존 방법을 적용하기 어렵다. EHR 생성에 대한 정량적 평가 지표를 개발하는 것은 EHR foundation model을 발전시키는 데 중요할 것이다.
