# Time-Conditioned Foreseeing (TCF) 상세 요약

> **Time-Conditioned Foreseeing: An EHR-Specific Foundation Model for Irregular Dynamics and Calendrical Time** · Bong Gyun Kang, Junyong Ahn, Hyeongrok Han, Sungroh Yoon (Seoul National University) · ICML 2026 (poster). 본 요약의 기술 내용·수치는 익명 ICLR-2026 투고본("Time Conditioned Foreseeing: Temporal Generative Pretraining for EHR Foundation Models")에서 인용.

## 0. 서지 정보

| 항목 | 내용 |
|------|------|
| 제목 (공식) | Time-Conditioned Foreseeing: An EHR-Specific Foundation Model for Irregular Dynamics and Calendrical Time |
| 제목 (투고본) | Time Conditioned Foreseeing: Temporal Generative Pretraining for EHR Foundation Models |
| 저자(소속) | Bong Gyun Kang, Junyong Ahn, Hyeongrok Han, Sungroh Yoon (Seoul National University) |
| 게재처 | ICML 2026 (poster) |
| 연도 | 2026 |
| 분량 | 본문 9p + Appendix (총 35p) |
| 코드 | "공개 예정" (최종본에서 release 명시) |
| 키워드 | EHR foundation model, temporal generative modeling, RoPE, value binning, MIMIC-III |

## 1. 한 줄 요약 & 연구 동기

- **한 줄.** EHR(전자건강기록) 고유 특성(병리적 수치, 불규칙·달력적 시간, 장기 의존성)에 맞춘 사전학습 기법(Pathology-Focused Binning + Dual-Calendar RoPE + Time-Conditioned Foreseeing)을 제안하여, **세 가지 feature 구성(117/17/6) × 7개 downstream task 모든 조합에서 1위**를 기록하고 AUPRC를 second-best 대비 **최대 48%(decompensation은 거의 50%)** 끌어올린, 최초의 진정한 temporal generative EHR 모델.
- **배경.** EHR은 자연어와 본질적으로 다름에도(수치 데이터가 지배적·시간 간격 불규칙·이웃 이벤트 간 결합이 느슨하고 장거리 의존), 기존 EHR foundation model은 NLP 패러다임(NTP/MLM, absolute positional embedding, uniform value binning)을 그대로 차용해 suboptimal하다. 또한 많은 모델이 모델링 복잡도 때문에 triplet(Time/Feature/Value) 중 Time이나 Value를 아예 제외한다(Table 1).
- **연구 질문.** (1) 임상적으로 중요한 병리적(pathologic) 수치 구간에 더 높은 해상도를 주는 value 토큰화는? (2) 상대적 시간 간격과 달력적(calendrical) 맥락을 동시에 인코딩하는 위치 임베딩은? (3) "다음 토큰"이 아니라 임상 계획처럼 **여러 시간 지평(horizon)의 미래 이벤트를 예측**하는 학습 목표는?

## 2. 전체 구조

```
Abstract
1 Introduction       — EHR ≠ NLP, triplet(T,F,V), 3대 한계 → 3대 기여
2 Related Works       — Table 1 비교(데이터 사용/value binning/time addressing/objective)
3 Method
  3.0 Pathology-Focused Binning
  3.0 Dual-Calendar RoPE
  3.0 Time-Conditioned Foresee Objective (TCF)
  3.1 Data and Preprocessing (MIMIC-III, Table 2)
  3.2 Backbone / Baselines / Pre-training
4 Result
  4.1 Downstream task & Fine-tuning (Table 3 메인, Table 4 ablation, Fig.3 ROC)
  4.2 Temporal Generative Modeling (Fig.4 생성 예시, Fig.5 평가, Fig.6 일주기)
5 Conclusion (+ Limitations)
Appendix A 추가 related works / B 방법 세부(B.1 binning, B.2 RoPE+Table5, B.3 TCF+Table6, Alg.1-3)
          C 데이터 / D 모델·베이스라인 / E task·config / F 전체 결과·생성 샘플
```

## 3. 문제 정의 / 사전 지식

- **EHR 표현.** 임상 이벤트를 **Time(T)-Feature(F)-Value(V) triplet**으로 표현(Tipirneni & Reddy, 2022). Feature는 진단코드/약물/검사(예: Systolic Blood Pressure)로 단일 토큰, Value는 그 결과/부가정보(예: 87mmHg)로 수치형이 많으나 결측·텍스트 등 이질적 modality도 가능.
- **기존 방법의 3대 한계** (Table 1로 정리):
  1. **Value binning.** 대부분 uniform binning → 정상(physiologic) 구간에 bin이 몰리고 병리(pathologic) 구간 해상도가 낮아 이상 정도(severity)를 구분 못 함. std 기반(TRADE) 또는 z-normalization(STraTS)은 Gaussianity를 가정해 outlier·long-tail·이중봉(dual peak) 분포에 취약.
  2. **Time addressing.** 시간을 absolute positional embedding으로 변환하면 상대 간격과 달력적 정보(오전/오후, 평일/주말 — 체온은 오후에 높고, 투석 합병증은 주말 후 흔함)를 잃음. 또 동시각(same-timestamp) 이벤트 구분도 어려움.
  3. **Learning objective.** NTP/MLM을 그대로 사용 → NTP는 `P(F_next | E_past)`만 모델링하여 시간 정보를 명시하지 않음. 따라서 다음 이벤트가 몇 분 뒤인지 몇 시간 뒤인지 구분 못 하고, 긴급/일상 측정을 똑같은 "next token"으로 취급.
- **EHR vs NLP.** NLP에서는 토큰 하나만 빠져도 문법이 깨지고 인접 토큰이 강하게 연관되지만, EHR 이벤트는 느슨히 연결되고 8시간 후속 검사처럼 장거리 의존이 흔함 → 의사는 실시간이 아니라 더 넓은 임상 계획을 세움.

## 4. 제안 방법

### 4.1 Pathology-Focused Binning — (Value binning 한계 해결)

- **목적.** 병리적 희소 구간에 더 많은 bin을 할당하고, 어떤 분포 가정도 두지 않음.
- **메커니즘 (2단계).**
  1. **KDE 기반 weight 부여.** Feature $f$의 모든 Value $V^f_{list}$에 대해, 범위 $[\min, \max]$를 $0.05\sigma$ 간격으로 분할한 점 $X=\{x_k\}$에서 Gaussian convolution kernel로 비모수 밀도 추정:
     $$\rho(x_k)=\sum_{j=1}^{|V^f_{list}|} K_h(x_k-v_j),\quad K_h(u)=\exp\!\Big(\!-\frac{u^2}{2(0.1\sigma)^2}\Big)$$
     bandwidth $h=0.1\sigma$. 밀도에 **반비례**하는 raw weight $w_{raw}(x_k)=1/(\rho(x_k)+\epsilon)$ → 정규화 후 상한 $w_{max}$(예: 10)로 clip. 즉 희소(병리) 구간 값은 큰 weight, 조밀(정상) 구간 값은 작은 weight.
  2. **Weighted percentile binning.** 각 unique value $v_j$의 raw count $c_j$를 weight로 스케일: $c'_j=c_j\cdot w(v_j)$. 가중 누적분포에서 $p/B$ percentile 경계로 bin 임계값 결정($T_p=\min\{v_k\,|\,S_k/C'_{total}\ge p/B\}$). 결과적으로 병리 구간이 percentile 공간을 더 많이 차지 → **임상적으로 중요한 구간에 더 촘촘한 bin**(Fig.2A).
- **비고.** EHR 모델에 density-based binning을 적용한 최초 사례라고 저자는 주장. Alg.1(weight)·Alg.2(binning)에 의사코드 제공. 기본 bin 수 $B$는 예시로 100(데이터 요약상 vital sign·lab 토큰 100, bin 토큰 10).

### 4.2 Dual-Calendar RoPE — (Time addressing 한계 해결)

- **목적.** 동시각 이벤트의 **순서(position)** 와 **달력적 주기성(calendrical time)** 을 한 attention head 안에서 동시 인코딩.
- **메커니즘.** query/key 벡터 $x\in\mathbb{R}^d$를 두 부분공간으로 분할: positional $x_{pos}\in\mathbb{R}^{d_{pos}}$ + temporal $x_{time}\in\mathbb{R}^{d_{time}}$ ($d=d_{pos}+d_{time}$).
  - **Positional 성분:** 표준 RoPE이되 차원을 줄여(truncated frequency spectrum) **동일 timestamp 공존 이벤트의 순서 disambiguation**에 집중. $\theta^{(pos)}_{p,i}=p/10000^{2i/d}$. (예: SBP,120/DBP,80이 동시 기록될 때 SBP,80/DBP,120과 혼동 방지.)
  - **Temporal 성분 (핵심 신규):** 초 단위 timestamp $t$를 의미 있는 달력 주기 $s_j$(minute=60s, hour=3600s, …, Table 5에 5분~300년까지 20개)별 phase로 인코딩: $\theta^{(time)}_{t,j}=\big(\frac{t \bmod s_j}{s_j}\big)\cdot 2\pi$. 같은 시각·다른 날짜 이벤트는 day 미만 단위는 동일 표현, day 이상 단위는 다른 표현(Fig.2B).
  - 두 성분을 각자 회전 후 concat: $q'=[\text{RoPE}(q_{pos},\theta^{(pos)})\,\|\,\text{RoPE}(q_{time},\theta^{(time)})]$.
- **비고.** 구현상 64-dim K/Q 중 **앞 24-dim = position, 나머지 40-dim = calendar time**. 장거리 시간 의존은 calendar-time 성분이 담당.

### 4.3 Time-Conditioned Foreseeing (TCF) Objective — (Learning objective 한계 해결)

- **목적.** "다음 이벤트가 **언제** 일어나는가"와 "지정된 미래 시각에 **무엇이** 일어나는가"를 동시 학습하여, NTP의 근시안(`P(F_next|E_past)`)을 넘어 다지평 예측·temporal generative modeling을 가능케 함. 임상 계획("앞으로 6시간 내 어떤 처치가 필요한가?")과 정렬.
- **메커니즘 (dual objective, $L=L_{next\_time}+L_{foresee}$, Fig.2C):**
  - **$L_{next\_time}$ (다음 시각 예측, `P(ΔT_next|E_past)`):** 마지막 hidden $h_{last}$를 $\text{FFN}_{enc}$로 투영, $N_{scales}$개 벡터로 분할 후 unembedding으로 time-logit 산출. ground-truth ΔT(초)를 **mixed-radix 분해**로 $N_{scales}$개 정수 라벨 벡터로 변환(가장 큰 단위→작은 단위로 정수 나눗셈·modulo). 각 scale에 대한 Cross-Entropy를 평균. → 연속 회귀를 **안정적 분류 문제 묶음**으로 변환. (예: 34,586,130초 → `[0,1,0,1,0,4,1,1,3,5,0]`.)
  - **$L_{foresee}$ (미래 이벤트 예측, `P(F_foresee|ΔT_foresee, E_past)`):** $N_{foresee}$개 미래 시각 델타를 같은 방식으로 분해·임베딩($e_{time}$)하고, residual로 $h_{last}$와 융합해 time-conditioned hidden 생성:
    $$h_{conditioned}=\text{FFN}(\text{LayerNorm}(h_{last}+\text{FFN}(e_{time})))$$
    이를 vocab logit으로 투영해 해당 시각의 Feature를 예측, Cross-Entropy 평균.
- **Value 예측 통합.** F와 V는 같은 이벤트라 시간 라벨을 공유하므로 V에는 항상 ΔT_next=0. V는 직전 F에 조건부이므로 $P(V_{foresee}|\Delta T_{foresee}, F_{now}, E_{past})$로 ΔT_foresee에 0만 넣어 $V_{now}$를 예측.
- **하이퍼파라미터 (Appendix B.3):** $d_{embed}=32$, $N_{scales}=11$ (Table 6: year10/year1/month3/month1/week1/day1/hour6/hour1/minute10/minute1 + position), $N_{foresee}=10$. embedding/unembedding weight 공유. 실제 학습은 NTP처럼 전 위치 병렬 처리. Alg.3에 전체 흐름.
- **비고.** Table 1에서 OURS만 Foresee=O, Temporal Generation=O를 모두 만족. 저자는 이를 **환자 medical timeline의 최초 진정한 temporal generative modeling**이라 주장.

## 5. 이론적/직관적 근거

- **Binning.** 비모수 KDE이므로 long-tail·이중봉 등 EHR 특유 분포 가정 없이 적용 가능. 희소 구간일수록 percentile 경계를 빨리 넘어 bin이 촘촘해진다는 누적분포 논리(B.1).
- **RoPE 분할.** 위치 성분은 truncated 고주파로 동시각 순서만 담당, 시간 성분이 장거리 주기성을 담당하도록 역할 분리. 같은 시각·다른 날 이벤트가 day-미만 주기에서 동일 회전을 공유 → 주기 패턴 학습 용이.
- **TCF.** 시간 회귀를 mixed-radix 분류로 바꿔 학습 안정화. EHR 이벤트의 느슨한 인접성·장거리 의존성이라는 도메인 관찰을 학습 목표로 직접 인코딩.

## 6. 실험

### Setup
- **데이터셋.** MIMIC-III Clinical Database v1.4, Harutyunyan et al.(2019) 전처리·split 채택. Train/Test 환자 28,728/5,070, 입원 35,730/6,295, 이벤트 38,641,175/6,744,906, 토큰 77,109,833/13,459,430, 평균 길이 2,684/2,655, 최대 393,337/62,759. Unique token 155(value 미공유 시 1,208). 토큰 수: bin 10, ethnicity 10, vital sign 17, lab 100. 임상 판단 항목(제외 기준·outlier 제거)은 내과·이비인후과·일반의가 독립 검토.
- **입력 config 3종 (분포 일반화 검증).** all 117 features / 17 vital signs(lab 제외) / 6 vital signs(SBP, DBP, body temperature, heart rate, respiratory rate, SpO2).
- **Backbone.** 모든 실험 Transformer decoder, 입력 토큰 길이 2048(초과 시 512-token overlap segmentation, 한 이벤트의 F·V는 분할 안 함). 베이스라인은 동일 backbone·데이터로 재현(MOTOR를 numeric value 처리하도록 수정 등).
- **Baselines.** No value share: HEART, MOTOR, EHRSHOT, TRADE, EHRmamba / Value share: FM4EHR, ETHOS, STraTS. (TCF는 share/no-share 양쪽 모두 학습해 각 그룹과 비교.)
- **Tasks (7개).** MIMIC-III 벤치마크 4종 — In-hospital Mortality(IHM), Decompensation-death(Dec-death), Length of Stay(LOS), Phenotyping(Phe) — + 추가 3종 — Decompensation-arrest(Dec-arrest), Oliguria/Anuria(HUO), Vasopressor(Vaso).
- **Metric.** 이진분류 AUROC(ROC)/AUPRC(PRC), 다중분류 macro-F1(Ma-f1)/Cohen's Kappa, 다중 subtask는 macro·micro AUROC. Test loss(낮을수록 좋음)도 보고. downstream은 backbone에 prediction head 부착, causal mask 적용.

### Main result (Table 3)
Test Loss는 117/17/6 feature 순. ROC/PRC 등은 117-feature 기준. 각 그룹 최고는 **Ours**.

**No Value share**

| 모델 | Test Loss (117/17/6) | IHM ROC/PRC | Phe macro/micro | Dec-death ROC/PRC | Dec-arrest ROC/PRC | LOS Ma-f1/Kappa | HUO macro/micro | Vaso ROC/PRC |
|------|------|------|------|------|------|------|------|------|
| HEART | 5.304/5.434/5.835 | 0.838/0.442 | 0.717/0.718 | 0.869/0.205 | 0.862/0.199 | 0.150/0.142 | 0.703/0.701 | 0.865/0.363 |
| MOTOR | 4.945/5.212/5.645 | 0.872/0.547 | 0.770/0.773 | 0.904/0.272 | 0.889/0.261 | 0.174/0.163 | 0.753/0.748 | 0.891/0.438 |
| EHRSHOT | 5.841/6.078/6.341 | 0.801/0.433 | 0.634/0.633 | 0.829/0.167 | 0.802/0.153 | 0.101/0.115 | 0.701/0.614 | 0.867/0.341 |
| TRADE | 5.260/5.454/6.048 | 0.828/0.441 | 0.738/0.738 | 0.867/0.170 | 0.857/0.165 | 0.158/0.151 | 0.732/0.731 | 0.869/0.393 |
| EHRmamba | 5.137/5.439/5.926 | 0.868/0.557 | 0.690/0.687 | 0.901/0.277 | 0.886/0.260 | 0.150/0.159 | 0.751/0.753 | 0.873/0.399 |
| **Ours (No share)** | **4.686/4.907/5.367** | **0.889/0.607** | **0.809/0.816** | **0.928/0.400** | **0.917/0.388** | **0.181/0.185** | **0.776/0.781** | **0.912/0.498** |

**Value share**

| 모델 | Test Loss (117/17/6) | IHM ROC/PRC | Phe macro/micro | Dec-death ROC/PRC | Dec-arrest ROC/PRC | LOS Ma-f1/Kappa | HUO macro/micro | Vaso ROC/PRC |
|------|------|------|------|------|------|------|------|------|
| FM4EHR | 6.429/6.389/6.397 | 0.617/0.177 | 0.530/0.519 | 0.744/0.075 | 0.778/0.102 | 0.023/0.003 | 0.598/0.653 | 0.690/0.130 |
| ETHOS | 4.971/5.248/5.572 | 0.859/0.530 | 0.739/0.746 | 0.900/0.311 | 0.890/0.304 | 0.170/0.165 | 0.721/0.731 | 0.890/0.437 |
| STraTS | 5.786/5.812/6.071 | 0.759/0.311 | 0.656/0.661 | 0.840/0.141 | 0.804/0.103 | 0.123/0.121 | 0.590/0.598 | 0.864/0.331 |
| **Ours (Share)** | **4.879/5.043/5.561** | **0.876/0.559** | **0.781/0.784** | **0.910/0.319** | **0.902/0.310** | **0.173/0.170** | **0.749/0.755** | **0.906/0.470** |

- 세 입력 config × 7개 task 모든 조합에서 Ours가 1위. 특히 **decompensation(24시간 전 사망/arrest 예측)** task에서 AUPRC가 second-best 대비 **거의 50% 높음**(클래스 불균형 positive:negative ≈ 1:40 환경에서 임상적으로 유의미). 전반적으로 AUPRC가 일관 향상(최대 48% — abstract/conclusion).
- **Fig.3:** bootstrapping 95% CI ROC 곡선. 대부분 task에서 second-best(주로 MOTOR) 대비 통계적으로 유의(예: IHM 0.890 vs 0.872, Dec-death 0.928 vs 0.904, Vaso 0.912 vs 0.891 등 CI 비중첩).

### Ablation (Table 4) — 117-feature Test loss
| Binning | Embedding | Objective | Test loss |
|---|---|---|---|
| ✓ (Pathology) | ✓ (Dual-Calendar) | ✓ (TCF) | **4.686** |
| Uniform | ✓ | ✓ | 4.713 |
| Uniform | RoPE(표준) | ✓ | 4.810 |
| Uniform | RoPE(표준) | NTP | 5.241 |

→ 세 구성요소 모두 기여하며, 특히 **Objective(TCF→NTP) 교체 시 손실 4.810→5.241로 가장 큰 악화**(objective 기여가 가장 큼), 다음이 Embedding, Binning 순.

### Temporal generative modeling (4.2)
- **Fig.4 (생성 예시).** 동일 초기 기록에서 후속 timeline 생성, ETHOS와 비교(공정성 위해 share ver.). **내용 정합성:** GCS=E+V+M 관계를 Ours는 정확히 재현(E1/V1/M1; GCS3), ETHOS는 불일치(E2/V1/M5; GCS3). Ours는 초기 응급 lab·다양한 검사 후 시간당 routine vital로 자연 복귀, ETHOS는 lab 미생성·불규칙 간격.
- **Fig.5 (정성 평가).** 100개 생성 샘플을 의사 5인·비의료인 5인·상용 LLM 4종(ChatGPT, Gemini 2.5 Flash, 2.5 Pro, Claude 4 Sonnet, 모두 API; 카테고리당 100 응답)이 평가 → 모든 그룹에서 Ours가 ETHOS를 일관 능가.
- **Fig.6 (일주기/calendrical 검증).** 동일 환자 이력에서 00:00–24:00 vital을 1,000 test sample 평균으로 순차 생성. Ours는 주간에 heart rate(주 85.13 vs 야 83.00)·temperature(36.87 vs 36.85)·respiratory rate(18.93 vs 18.82)가 높은 현실적 circadian 변동 재현; ETHOS는 통제변수 Height(167.29 vs 165.30)조차 임상적으로 비현실적 패턴.

## 7. 한계 & 향후 연구

- **저자 명시 한계.** EHR 모델의 **temporal generative 성능을 평가할 확립된 metric이 없음.** timing 적절성 평가가 핵심인데 LLM 생성 평가의 통상 방법을 적용하기 어려움 → 정량적 EHR 생성 평가 metric 개발이 향후 중요 과제(현재 Fig.5는 사람·LLM 정성 평가에 의존).
- **리뷰어 관점 추가 관찰 (논문 미주장).**
  - 단일 데이터셋(MIMIC-III) 검증. 외부 코호트/다기관 일반화는 미확인. (공식 ICML abstract은 9개 task·48% 언급이나, 본 PDF는 7개 task 기준.)
  - 비교는 동일 backbone으로 **재현된** 베이스라인이며 일부는 적용 위해 수정(MOTOR 등) — 원논문 최적 설정과 차이가 있을 수 있음.
  - 3개 구성요소가 결합된 ablation만 제시되어, RoPE 단독·Binning 단독 등 개별 효과의 독립 분리는 제한적.
  - TCF 모듈($N_{foresee}=10$ 등)이 시퀀스 길이·메모리·연산 비용에 미치는 추가 오버헤드는 정량 보고되지 않음.

## 8. 실무 적용 관점 (의료 AI)

- **재현성.** 공개 데이터(MIMIC-III v1.4) + 표준 전처리(Harutyunyan 2019) + 코드 공개 예정으로 재현 장벽이 낮은 편. value share/no-share 양쪽 결과를 모두 제공해 vocabulary 규모·sparsity trade-off를 환경에 맞춰 선택 가능.
- **임상 가치.** decompensation(24시간 전 악화 예측) 같은 고불균형·고정밀 요구 task에서 AUPRC 대폭 향상은 alarm fatigue 완화·조기경보 측면에서 실질적. circadian·calendrical 패턴을 반영한 생성은 합성 EHR·data augmentation·환자 trajectory 시뮬레이션에 활용 여지.
- **이식성.** Pathology-Focused Binning·Dual-Calendar RoPE·TCF는 각각 독립 모듈로, 기존 Transformer decoder 기반 EHR 파이프라인에 부분 도입 가능(특히 binning은 모델 비종속 전처리). 단, 자가 institution 데이터로의 전이·외부 검증·temporal 생성 품질의 정량 평가는 도입 전 별도 확인이 필요.
