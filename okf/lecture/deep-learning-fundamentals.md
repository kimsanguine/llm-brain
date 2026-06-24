---
type: lecture
title: 딥러닝 기초 — 퍼셉트론·MLP·CNN·시퀀스 모델
tags:
- deep-learning
- deep-learning-component
- transfer-learning
timestamp: '2026-06-25'
x-llmbrain-domain:
- teaching
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 딥러닝 기초 — 퍼셉트론·MLP·CNN·전이 학습

## 핵심 요약

딥러닝의 역사(1950년대 → 2012년 혁명)와 퍼셉트론·XOR 문제 → 다층퍼셉트론 → CNN 작동 원리 → 전이 학습·YOLO 응용 → RNN/LSTM 시퀀스 모델까지 연결한 강의. 2026-03-30 딥러닝 기초 세션과 2026-04-01 CNN 종합 세션을 통합 정리.

## 상세 내용

### AI 역사 타임라인

| 연도 | 사건 |
|---|---|
| 1950년대 | AI 개념 등장 → AI 겨울(암흑기) |
| 1986년 | 다층퍼셉트론 발견 → 2차 부흥기 |
| 2012년 | [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) / 딥러닝 혁명 (Geoffrey Hinton, [ilya-sutskever](/people/ilya-sutskever.md) 공저) |
| 2016년 | AlphaGo vs 이세돌 → 한국 대중화 |
| 2022~2023 | 생성형 AI 혁신 — [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md)가 LLM 시대 개막 |

### 퍼셉트론 기초

**수식:**
```
y = σ(w₀ + w₁x₁ + w₂x₂ + ... + wₙxₙ)
```
- `w₀` = 편향(bias) — 분류 경계 조정
- `wᵢ` = 가중치(weight) — 중요도
- `σ` = 활성화 함수 — 복잡한 연산 결과를 0/1로 이진화 (if문 역할)

### XOR 문제와 다층 퍼셉트론

단층 퍼셉트론으로 구현 가능: AND, OR, NAND, NOR
단층 퍼셉트론으로 **불가능**: **XOR** (1969년 AI 첫 번째 겨울의 원인)

- **해결책**: 다층 퍼셉트론(MLP) — NAND + OR 조합
- **히든 레이어 3개 이상** = "딥러닝"의 정식 정의
- 1986년 다층퍼셉트론 발견으로 제2 도약기 시작

XOR 실용 예: CCTV 동작 감지 — 프레임 t XOR 프레임 t+1 → 픽셀 차이 있으면 녹화 시작

### CNN (합성곱 신경망)

**왜 CNN이 필요한가**
- 이미지를 1차원으로 펼쳐 FC에 넣으면 공간 정보가 무너짐
- CNN은 커널이 이미지를 훑으며 위치 정보를 유지한 채 특징 추출

**핵심 개념**

| 개념 | 설명 |
|---|---|
| Convolution | 커널/필터가 이미지를 슬라이딩하며 특징 맵(feature map) 생성 |
| Stride | 커널 이동 칸 수 — 크면 계산량↓ 세밀도↓ |
| Padding | Zero padding으로 입출력 크기 보존 (`same padding`) |
| Parameter Sharing | 같은 커널을 이미지 전체에 공유 → 파라미터 수 대폭 감소 |
| ReLU | CNN 기본 활성화 함수 — 음수를 0으로 변환, 비선형성 추가 |
| Max Pooling | 가장 강한 특징만 남김 — 계산량과 과적합 위험 감소 |
| Global Average Pooling | Flatten 없이 채널별 대표값만 남겨 파라미터 대폭 축소 |

**대표 모델 흐름**

| 모델 | 특징 |
|---|---|
| LeNet | 초창기 CNN, 숫자 인식 |
| AlexNet | [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) — ImageNet 우승, GPU 활용 본격화, CNN 대중화 |
| VGGNet | 3×3 커널 반복 적층, 단순하고 직관적 |
| GoogLeNet / Inception | 1×1 bottleneck + 멀티브랜치 모듈로 계산 효율적 CNN 설계 |
| ResNet | Residual Connection으로 기울기 소실 해결 — 매우 깊은 네트워크도 안정 학습 |
| U-Net | 인코더-디코더 + skip connection으로 픽셀 단위 세그멘테이션 |
| Depth Anything V2 | 합성 데이터 teacher + pseudo-label distillation 기반 단안 깊이 추정 |

### 전이 학습 (Transfer Learning)

- "천 년 공부한 사람의 뇌를 빌려 쓰는 것"에 비유
- 처음부터 학습보다 ResNet / EfficientNet / Transformer 계열([attention-is-all-you-need](/papers/attention-is-all-you-need.md)) 사전학습 모델을 활용하는 것이 현실적
- 이미지 분류 대회(데이콘/캐글)에서 기본 접근법
- [andrew-ng](/people/andrew-ng.md) Coursera ML 강의와 [karpathy](/people/karpathy.md) Neural Networks: Zero to Hero가 전이 학습 개념 학습의 대표 경로

2026-06-01 논문 추천은 전이 학습을 층별 특징 재사용 관점으로 보강한다. DeCAF는 사전학습 CNN의 중간 활성값을 고정 특징 추출기로 써도 장면 인식·도메인 적응에서 강력하다는 초기 증거다. Yosinski et al. 2014는 하위 층의 Gabor 필터·색상 블롭은 일반적이고, 상위 층으로 갈수록 태스크 특화된다는 점을 정량화했다.

수업에서는 "어디까지 freeze하고 어디서부터 fine-tuning할 것인가"를 모델 선택 팁이 아니라 데이터 규모와 도메인 차이에 따른 제품 판단으로 설명한다. Qwen2-VL 사례는 이 전이 학습 사고가 CNN에서 멀티모달 파운데이션 모델로 확장됐다는 연결점이다.

### 2026-06-04 BERT 계열 보강

| 논문/모델 | 강의 메시지 |
|---|---|
| XLNet | MLM과 AR objective의 차이, 사전학습-파인튜닝 불일치 |
| ALBERT | 임베딩 분해·레이어 공유로 파라미터 효율을 만드는 방법 |
| NeoBERT | LLM 시대 기법을 encoder backbone에 다시 적용하는 흐름 |

딥러닝 강의에서 BERT 계열은 Transformer 이후의 "이해용 인코더" 계보로 다루면 좋다. GPT 계열 decoder가 생성 과제를 대표한다면, BERT/NeoBERT 계열은 검색, 임베딩, 분류, RAG retrieval 품질의 백본으로 남아 있다. 이 구분은 ai-paper-learning-path의 Module 4와 연결된다.

### YOLO 데모 및 응용

- Ultralytics YOLO 기반 분류/추론 흐름
- MNIST, 가위바위보(RPS) 예제로 학습·추론 시연
- CNN → 탐지, 추적, 실시간 추론, 카메라 기반 애플리케이션으로 바로 연결 가능
- 모바일/엣지 배포 시 [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) 비교 검토, 오디오 응용은 [whisper-ecosystem](/tools/whisper-ecosystem.md) 참조

### 실무 관점

- 레이어 입출력 shape를 이해하고 튜닝할 수 있어야 실력
- 모델 선택 기준: 서비스 환경(모바일/데스크탑), GPU 유무
- 추론은 CPU 가능, 학습은 GPU 사실상 필수
- 데이터 이해·전처리가 모델 구조만큼 중요
- 딥러닝 프로젝트를 제품화할 때 [ai-pm-role](/concepts/ai-pm-role.md) 역량과 연결됨

### 학습 안정성 — 초기화와 활성 함수의 짝

2026-05-28 논문 추천은 딥러닝 기초 강의의 “왜 학습이 안 되는가” 파트를 보강한다.

| 주제 | 강의 메시지 |
|---|---|
| Xavier/Glorot Init | tanh/sigmoid 계열에서 forward/backward 분산을 보존한다 |
| He/Kaiming Init | ReLU 계열에서는 Var(W)=2/n_in이 기본값이다 |
| IDInit | residual block을 identity에 가깝게 시작해 normalization 의존도를 낮춘다 |

강의에서는 수식보다 디버깅 관점이 중요하다. loss가 폭주하거나 학습이 멈추면 모델을 바꾸기 전에 layer별 activation/gradient 분산을 확인한다. 이 루틴은 ai-paper-learning-path의 Glorot → He → IDInit 계보와 연결된다.

### CNN 아키텍처 확장 — 효율·세그멘테이션·깊이 추정

2026-05-29 논문 추천은 CNN 챕터를 AlexNet/ResNet 중심 설명에서 실제 비전 파이프라인 구성 요소로 확장한다.

| 논문/모델 | 강의 메시지 |
|---|---|
| GoogLeNet / Inception | 1×1 conv bottleneck으로 채널을 줄인 뒤 3×3·5×5·pooling 분기를 병렬 결합한다. 핵심은 정확도만이 아니라 파라미터와 연산량을 통제하는 설계다. |
| U-Net | 다운샘플링으로 의미를 잡고, 업샘플링과 skip connection으로 위치 정보를 복원한다. 의료 영상뿐 아니라 배경 제거, 얼굴 마스크, diffusion backbone 설명에 바로 연결된다. |
| Depth Anything V2 | 합성 데이터 teacher와 대규모 pseudo-label distillation으로 단안 depth foundation model을 만든다. 데이터 품질과 증류 전략이 아키텍처만큼 중요하다는 사례다. |

AI Avatar/Dubbing 수업에서는 이 세트를 "이미지 분류 모델"이 아니라 전처리 도구 묶음으로 설명하면 좋다: 얼굴/입 영역 분할(U-Net), 깊이 기반 배경 분리(Depth Anything), 모바일/엣지 비용 절감(Inception bottleneck).

### RNN/LSTM — 시퀀스 모델의 원형

2026-05-30 논문 추천은 딥러닝 강의를 이미지 모델에서 텍스트·음성·시계열로 확장한다.

| 논문/모델 | 강의 메시지 |
|---|---|
| Pascanu et al. 2013 | RNN의 장기 의존성 문제는 기울기 폭발/소실로 설명된다. gradient clipping은 지금도 학습 불안정성의 첫 처방이다. |
| Graves 2013 | 한 스텝씩 다음 값을 예측하는 자기회귀 생성은 텍스트·필기·음악·LLM 디코딩의 공통 패턴이다. |
| xLSTM 2024 | LSTM 직관은 끝난 것이 아니라 지수 게이팅, 행렬 메모리, 병렬화 가능한 블록으로 현대화되고 있다. |

수강생에게는 RNN을 "Transformer 이전의 낡은 모델"로 끝내지 않는 편이 좋다. RNN/LSTM은 [attention-is-all-you-need](/papers/attention-is-all-you-need.md) 이전에 시퀀스 생성, 정렬, 메모리 문제를 어떻게 다뤘는지 보여주는 출발점이고, [voice-ai-stack](/concepts/voice-ai-stack.md)의 실시간 음성·온디바이스 시계열 처리와도 연결된다.

### 최적화와 일반화 — 학습률, 손실 지형, Adam 계열

2026-05-31 논문 추천은 딥러닝 학습을 "모델 구조"가 아니라 "어떻게 안정적으로 좋은 해에 도달하는가"로 설명하게 해준다.

| 논문/기법 | 강의 메시지 |
|---|---|
| SGDR | cosine warm restart는 추가 모델 변경 없이 수렴과 일반화를 개선하는 학습률 스케줄이다. "공짜 성능"에 가깝지만 주기와 종료 시점을 이해해야 한다. |
| SAM | 낮은 loss만 보지 않고 주변까지 평평한 minima를 찾는다. 같은 train loss라도 손실 지형의 sharpness가 일반화 차이를 만든다. |
| ADOPT | Adam도 여전히 개선 대상이다. 2차 모멘트 추정과 정규화 순서를 바꾸는 작은 수정으로 beta2 선택 민감도를 줄이고 최적 수렴률을 보장하려는 흐름이다. |

강의에서는 optimizer를 외워야 할 함수명이 아니라 디버깅 도구로 다루는 편이 좋다. loss가 흔들리면 learning rate schedule, gradient norm, sharpness/generalization, Adam 계열 hyperparameter를 순서대로 점검한다.

### 자기 정규화, 순환 학습률, Muon

2026-06-24 논문 추천은 신경망 학습을 "레이어를 많이 쌓는 법"보다 **분포와 업데이트를 안정시키는 법**으로 보강한다.

| 논문/기법 | 강의 메시지 |
|---|---|
| Self-Normalizing Neural Networks | SELU + 적절한 초기화 + alpha dropout으로 activation 평균과 분산이 스스로 안정 영역으로 돌아가게 만든다. 정규화는 BatchNorm 같은 별도 레이어만의 문제가 아니라 활성화 함수 설계 문제이기도 하다. |
| Cyclical Learning Rates | 학습률은 항상 줄이는 값이 아니라 탐색과 탈출을 위해 주기적으로 높일 수 있는 제어 변수다. LR range test는 수강생에게 가장 실용적인 튜닝 절차로 소개하기 좋다. |
| Muon | AdamW가 끝판왕이 아니라, 가중치 행렬의 기하 구조를 활용한 optimizer가 LLM 사전학습 compute를 줄일 수 있다는 최신 신호다. |

수업에서는 이 세트를 하나의 디버깅 루틴으로 묶는다. 학습이 불안정하면 먼저 activation/gradient 분산을 보고, 그 다음 learning rate range를 찾고, 마지막으로 optimizer 선택과 update scale을 확인한다. 이 흐름은 ai-paper-learning-path Module 3의 "Classic + Recent + Practical Lens" 구조와 연결된다.

### 강사 팁

- 기존 프로그래밍 한계: if/else 연속으로는 모든 상황 코딩 불가 → AI의 해답
- `input_shape`를 하드코딩하지 않고 동적으로 처리하는 습관 강조
- MLP vs CNN 비교: CIFAR-10/Fashion MNIST로 직접 확인

## 관련 개념

- [ml-classification-algorithms](/lecture/ml-classification-algorithms.md)
- [docker-kubernetes-ai-deploy](/lecture/docker-kubernetes-ai-deploy.md)
- [adsp-exam-prep](/lecture/adsp-exam-prep.md)
- 260515_100_agents
- [ai-pm-role](/concepts/ai-pm-role.md) (딥러닝 PM 역할)
- ai-paper-learning-path
- [karpathy](/people/karpathy.md) (Neural Networks Zero to Hero)
- [swe-agent-aci](/tools/swe-agent-aci.md) (agent 응용 관련)
- [andrew-ng](/people/andrew-ng.md) (Coursera ML — 딥러닝 이론 표준 커리큘럼)
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md) (Transformer — CNN 이후 아키텍처 혁신)
- [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) (2012년 CNN 혁명 원전)
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md) (LLM 진화 — 딥러닝 응용 정점)
- [ilya-sutskever](/people/ilya-sutskever.md) (AlexNet 공저자, OpenAI 공동창립)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) (vision 엣지 배포)
- [whisper-ecosystem](/tools/whisper-ecosystem.md) (오디오 딥러닝 응용)
