---
type: paper
title: 'LoRA: Low-Rank Adaptation of Large Language Models (2021)'
description: Microsoft Research가 2021년 발표 (arxiv 2106.09685).
tags:
- lora
- peft-paper
- peft
- fine-tuning
- parameter-efficient
- microsoft
timestamp: '2026-06-04'
x-llmbrain-domain:
- AI/LLM
- research
- fine-tuning
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://arxiv.org/abs/2106.09685
- https://github.com/microsoft/LoRA
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LoRA: Low-Rank Adaptation of Large Language Models (2021)

## 핵심 요약

Microsoft Research가 2021년 발표 (arxiv 2106.09685). 저자: Edward Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen.

기존 full fine-tuning의 대안. **모델 weight 전체를 갱신하지 않고 low-rank decomposition matrix 쌍(A·B)만 학습**. 파라미터 수 최대 1만 배 절감, VRAM·학습 시간 대폭 감소.

PEFT(Parameter-Efficient Fine-Tuning) 계열 기법의 사실상 표준으로 정착.

## 핵심 아이디어

### Low-Rank Decomposition
사전학습 weight 행렬 W₀(d×k)에 대해 업데이트 ΔW를 다음과 같이 분해:

```
ΔW = B · A   (B: d×r, A: r×k, rank r ≪ min(d,k))
```

- 학습 중 W₀는 고정(frozen), A·B만 학습
- 추론 시 W = W₀ + BA → 지연 없음(latency zero)
- rank r을 4~8로 설정하면 파라미터 약 10,000배 절감 (GPT-3 175B 기준)

### 적용 위치
Transformer의 attention 투영 행렬(Q, K, V, O)에 주로 적용. FFN에도 적용 가능하나 attention만으로 성능 확보.

## 성능 (논문 보고)

- GPT-3 175B 기준: full fine-tuning과 동등하거나 우수한 성능
- 학습 파라미터: 약 0.01% (vs full fine-tuning 100%)
- VRAM 사용량: full fine-tuning 대비 ~67% 절감
- 체크포인트 크기: 수십 GB → 수 MB

## PEFT 생태계에서의 위치

LoRA 이후 파생 기법:
- **QLoRA** (2023) — 4-bit 양자화 + LoRA, 소비자 GPU(24GB)에서 65B 모델 fine-tuning
- **AdaLoRA** — rank를 레이어별 중요도에 따라 동적 할당
- **LoRA+, LoftQ** — 초기화 및 학습 안정성 개선
- **DoRA** — weight 분해를 magnitude + direction으로 확장

## 2026-06-03 실무 신호: Unsloth와 로컬 fine-tuning

AI Human Ch06 브리프는 Unsloth를 오픈 LLM fine-tuning 실습의 1순위 도구로 기록했다. Unsloth의 메시지는 LoRA/PEFT가 논문 기법을 넘어 로컬 학습·강화학습·Ollama export까지 이어지는 제품 워크플로가 됐다는 점이다. 주장 수치는 속도 최대 2배, VRAM 최대 70% 절감, MoE 학습 12배 가속이지만, 제품 적용 시에는 정확도 손실 없음·지원 모델·export 경로를 직접 검증해야 한다.

## 본 wiki에서의 위치

- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) — 전이학습(transfer learning) 챕터의 발전 결과물
- thinking-machines — Tinker fine-tuning platform의 기반 기법 (LoRA 변형 사용)
- [mira-murati](/people/mira-murati.md) — OpenAI CTO 재임 시절 제품(ChatGPT, GPT-4)에 LoRA 계열 PEFT 적용
- anthropic — Claude 시리즈 task-specific 어댑터에 LoRA 변형 활용
- openai — InstructGPT·GPT-4 fine-tuning API에서 LoRA 계열 노출
- 관련 논문: [attention-is-all-you-need](/papers/attention-is-all-you-need.md) (Transformer weight 구조의 직접 출처), [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md) (in-context learning과 PEFT의 비교 프레임), [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md) (SFT 단계에서 LoRA와 결합)

## 후속 영향

- **Hugging Face PEFT 라이브러리** 표준 지원 → 커뮤니티 전파 가속
- **Stable Diffusion fine-tuning** (DreamBooth·LoRA) — 이미지 생성 모델로 영역 확장
- **오픈소스 LLM 생태계** (LLaMA, Mistral) fine-tuning 진입 장벽 대폭 낮춤
- on-device·edge inference 맞춤 어댑터 교체 패턴 정착
- Unsloth Studio/Ollama export처럼 비전문가가 오픈웨이트 모델을 fine-tune하고 배포하는 로컬 워크플로 확산

## 관련 개념
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- thinking-machines
- [mira-murati](/people/mira-murati.md)
- anthropic
- openai
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md)
- [gpt-3-language-models-are-few-shot-learners](/papers/gpt-3-language-models-are-few-shot-learners.md)
- [instructgpt-rlhf-2022](/papers/instructgpt-rlhf-2022.md)
