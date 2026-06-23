---
type: concept
title: LLM Deployment Patterns
description: LLM 배포는 latency·cost·privacy·scalability 4개 축의 트레이드오프로 결정된다.
tags:
- llm-deployment
- infrastructure
- synthesis-hub
- cloud
- edge
timestamp: '2026-06-12'
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://anthropic.com/api
- https://platform.openai.com
- https://github.com/ggerganov/llama.cpp
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM Deployment Patterns

LLM 배포는 latency·cost·privacy·scalability 4개 축의 트레이드오프로 결정된다. 현재 주류 패턴은 Cloud API, Edge, Hybrid, On-prem self-host 4가지다.

## 4-Pattern 비교

| 패턴 | Latency | Cost | Privacy | Scalability | 대표 사례 |
|------|---------|------|---------|-------------|-----------|
| **Cloud API** | 중간 (네트워크 RTT) | 종량제 (토큰당) | 낮음 (외부 전송) | 무제한 | ChatGPT, anthropic Claude API |
| **Edge** | 최저 (온디바이스) | 고정 (디바이스 원가) | 최고 (로컬) | 디바이스 수 | Pixel Gemini Nano, [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) |
| **Hybrid** | 가변 (조건부 cloud) | 혼합 | 중간 | 높음 | 민감 데이터 → edge, 복잡 추론 → cloud |
| **On-prem self-host** | 낮음 (내부망) | 고정 (GPU 인프라) | 최고 | 인프라 한계 | vLLM, llama.cpp, 금융/의료 엔터프라이즈 |

## 패턴별 상세

### 1. Cloud API

anthropic (Claude API), openai (GPT-4o) 등 외부 API 호출. 별도 인프라 없이 즉시 사용 가능. [claude-code](/tools/claude-code.md) CLI, [claude-code-agent-system](/tools/claude-code-agent-system.md) 같은 에이전트 시스템이 이 패턴을 기반으로 작동한다.

- **비용**: 입·출력 토큰 단위 과금 → [agent-pricing-model](/concepts/agent-pricing-model.md), [model-routing-cost](/concepts/model-routing-cost.md) 참조
- **장점**: zero-ops, 최신 모델 즉시 접근, 자동 스케일
- **단점**: 네트워크 의존, 데이터 외부 전송, 장기 대량 사용 시 비용 증가

### 2. Edge (On-device)

[mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) (LiteRT-LM 포함)가 대표 프레임워크. 모델을 디바이스에 내려받아 네트워크 없이 추론.

- **적합**: 실시간 반응 필요 (자동완성, 번역, 음성인식), 오프라인 환경, 개인정보 민감 작업
- **제약**: 모델 크기 제한 (메모리·배터리), quantization 필수 (INT4/INT8)
- **사례**: Pixel 9 Gemini Nano, Apple Intelligence on-device model

### 3. Hybrid (Cloud + Edge Fallback)

단순·민감 작업은 edge 처리, 복잡 추론은 cloud escalation. 본 wiki `wiki_app`이 potential hybrid 사례 — 로컬 FastAPI 서버 + cloud Claude API.

- **라우팅 기준**: 토큰 복잡도, 데이터 민감도, latency 요건 → [model-routing-cost](/concepts/model-routing-cost.md)
- **장점**: 비용 절감 + 품질 보장 + 프라이버시 분리
- **구현 복잡도**: 라우팅 로직, fallback 핸들링, 일관성 유지 필요

### 4. On-prem Self-host

**vLLM**: PagedAttention 기반 고처리량 inference 서버. OpenAI-compatible API. GPU 클러스터에서 Llama, Mistral 등 오픈소스 모델 서빙.

**llama.cpp**: CPU/Metal/CUDA GGUF 포맷 추론. 맥북 M-시리즈에서도 7B 모델 실용적 속도 달성. 소규모 팀·개발 환경에 적합.

- **배포 인프라**: [docker-kubernetes-ai-deploy](/lecture/docker-kubernetes-ai-deploy.md) (K8s HPA, GPU nodeSelector, vLLM Helm chart)
- **에이전트 배포**: [swe-agent-aci](/tools/swe-agent-aci.md) 패턴으로 on-prem 환경에서 에이전트 격리 실행 가능
- **적합**: 금융·의료·법률 (데이터 국경 규제), 대규모 내부 트래픽 (ROI 손익분기 도달 시)

## 2026-05-30 신호: 추론·오디오·업무 에이전트의 결합

2026-05-30 브리프의 ElevenLabs Music v2, VoxCPM2, X-Voice, SKT A.Biz Cowork는 배포 의사결정이 텍스트 LLM에만 국한되지 않음을 보여준다. 음성/음악 생성 모델은 latency와 GPU 비용이 크고, 업무 에이전트는 Outlook/Teams 같은 내부 협업툴 권한을 다룬다. 따라서 음성 에이전트 배포는 [voice-ai-stack](/concepts/voice-ai-stack.md)의 STT/TTS 선택과 동일하게 cloud API, open-weight self-host, edge/hybrid를 함께 비교해야 한다.

실무 기준은 단순하다: 빠른 품질 검증은 cloud API, 보이스/데이터 통제가 중요한 경우는 오픈 모델 self-host, 개인정보·지연시간이 핵심이면 edge/hybrid가 맞다. SKT A.Biz Cowork처럼 사내 문서와 협업툴을 실행하는 에이전트는 모델 성능보다 권한 경계, 감사 로그, 실패 시 human handoff가 배포 패턴의 핵심이다.

## 2026-06-01 신호: 오픈 웨이트와 데이터 희소성

NVIDIA Nemotron 3 Ultra raw는 550B 파라미터, 55B active MoE, 미국 최고 수준 오픈 웨이트 모델이라는 포지셔닝을 기록했다. 하드웨어 회사가 모델·소프트웨어를 함께 제공하는 흐름은 self-host/on-prem 패턴을 강화한다. 기업 입장에서는 API 품질만이 아니라 자체 하드웨어, 커스터마이즈, 데이터 경계, 추론 속도가 모델 선택 기준이 된다.

Roko's Bas raw는 다음 AI 희소성이 고품질 신규 데이터라고 본다. 공개 훈련 데이터 고갈, 합성 데이터 과다 학습에 따른 model collapse, Meta의 실제 컴퓨터 사용 데이터 수집 신호는 배포 전략과 데이터 전략이 분리될 수 없다는 점을 보여준다. 운영 데이터가 많은 조직은 [vertical-agent-domain-depth](/concepts/vertical-agent-domain-depth.md)의 도메인 깊이를 모델 개선과 평가 데이터로 전환할 수 있다.

## 2026-06-02 신호: 긴 컨텍스트 효율과 검증

Subquadratic의 SubQ 1M-Preview 주장은 긴 컨텍스트 배포 비용의 핵심 병목을 다시 드러낸다. Transformer attention은 시퀀스 길이에 따라 O(n²) 비용이 증가하므로, 100만~1,200만 토큰 문맥을 실용화하려면 서브쿼드라틱/선형 attention 계열이 비용 구조를 바꿔야 한다.

다만 이 raw의 핵심은 "1,000배 효율"을 그대로 믿는 것이 아니라 공개 모델, 논문, 독립 재현, 내 workload benchmark가 있는지 확인하는 것이다. 긴 컨텍스트 모델은 데모에서는 매력적이지만 production 배포에서는 latency, memory, retrieval 대체 가능성, hallucination 검증 비용을 함께 본다. 이 판단은 agent-evaluation-frameworks의 숫자 검증 원칙과 연결된다.

## 2026-06-03 신호: 로컬 LLM 런타임과 오픈웨이트 실습 경로

AI Human 브리프는 Ollama, vLLM, llama.cpp, LM Studio가 동시에 진화한 2026년 5월 흐름을 Ch06 실습 신호로 기록했다. 로컬 LLM은 더 이상 "느린 장난감"이 아니라 quantization, MTP 추측 디코딩, Blackwell 최적화, MLX/Metal 가속이 결합된 배포 옵션이다. 개발·강의 실습에서는 Ollama/LM Studio가 진입점이고, production self-host는 vLLM/llama.cpp가 기준선이다.

NVIDIA Nemotron 3 Nano Omni와 Unsloth도 같은 축에 있다. 오픈웨이트 모델은 다운로드·양자화·파인튜닝·호스팅이 가능하고, Unsloth는 LoRA/PEFT 기반으로 VRAM과 학습 시간을 줄인다. 클로즈드 API와 오픈웨이트의 선택 기준은 성능 순위가 아니라 데이터 경계, 반복 fine-tuning 필요성, latency SLA, GPU 운영 역량이다.

2026-06-03 attention 논문 큐레이션은 이 판단을 더 낮은 레이어로 내린다. FlashAttention류 IO-aware exact attention과 Native Sparse Attention류 sparse attention은 긴 컨텍스트 비용 구조를 바꾼다. 따라서 self-host 모델을 고를 때는 parameter 수뿐 아니라 attention kernel, KV cache, sparse 패턴, 실제 workload latency를 함께 벤치마크해야 한다.

## 2026-06-04 신호: 금융권 검증 샌드박스와 모델 티어링

AI Human 브리프의 베스핀글로벌·우리금융 사례는 규제 산업의 LLM 도입이 "어떤 모델이 좋은가"보다 **어디서 안전하게 검증할 것인가**로 이동한다는 신호다. AWS 기반 독립형 연구환경은 금융권이 최신 LLM을 데이터 유출 없이 실험하기 위한 on-prem/hybrid 샌드박스에 가깝다. 이 경우 배포 기준은 성능뿐 아니라 네트워크 격리, 감사 로그, 데이터 반출 통제, 모델별 실험 재현성이다.

Google Gemini 3.5 Pro 예고는 클로즈드 모델도 단일 라인업이 아니라 Flash/Pro 같은 tiering으로 운영된다는 점을 보여준다. 실무 배포에서는 빠른 저비용 모델을 기본 경로로 두고, 깊은 추론·proactive agent 작업만 Pro급 모델로 올리는 라우팅이 [model-routing-cost](/concepts/model-routing-cost.md)와 자연스럽게 연결된다.

## 2026-06-05 신호: GPU는 유틸리티처럼, cold start는 제품 지연으로

Roko's Basilisk raw의 Modal Labs 사례는 GPU 시작 시간을 2,000초에서 약 50초로 줄인 서버리스 GPU 인프라를 설명한다. 사전 워밍 GPU 풀, 레이지 로딩 파일시스템, CPU 프로세스 스냅샷, GPU 메모리 상태 캡처·복원이 핵심이다. AI 앱의 deployment 선택은 이제 "어디서 모델을 돌리나"뿐 아니라 "cold start가 사용자 경험을 깨지 않는가"를 포함한다.

하이퍼스케일러도 Google Cloud Run GPUs, Azure Container Apps GPU, AWS Lambda Managed Instances처럼 scale-to-zero와 초 단위 과금으로 대응한다. a16z raw의 데이터센터 전력 수요 신호는 이 문제가 단순 클라우드 요금이 아니라 그리드 연결, 부품, 숙련 인력, 송전·변전 엔지니어링 제약까지 이어지는 인프라 병목임을 보여준다.

## 2026-06-06 신호: 로컬 런타임 GGUF 확장과 실시간 추론 라우팅

Ollama 0.30은 llama.cpp 기반 GGUF 호환을 확대해 NVIDIA에서 최대 20% 빠른 처리량, Vulkan 기본 활성화로 AMD/Intel GPU 즉시 가속, LFM·Prism·Unsloth fine-tuned 모델 지원을 더했다(raw 원문 기준). HuggingFace GGUF를 Modelfile `FROM`으로 바로 실행하고, tool calling 지원 모델은 [claude-code](/tools/claude-code.md)·Hermes·OpenClaw 같은 코딩 에이전트에 한 줄로 연결된다. Google Gemma 4 12B는 encoder-free 멀티모달(비전·네이티브 오디오)을 16GB VRAM에 담아 노트북 로컬 실행을 가능하게 했다 — Edge/On-prem 패턴의 진입 장벽을 다시 낮춘다.

Perplexity는 Computex 2026에서 작업 중간에 "이 연산을 기기에 둘지 클라우드 프런티어로 보낼지"를 실시간 판단하는 하이브리드 오케스트레이터를 시연했다(Core Ultra Series 3 로컬 모델, 민감 정보는 온디바이스 유지). 이는 본 페이지 Hybrid 패턴의 상용 구현 사례이며 [model-routing-cost](/concepts/model-routing-cost.md)의 라우팅 기준(파라미터 수·latency·데이터 거버넌스)을 그대로 제품화한다. 하드웨어 층에서는 Google TPU 8세대가 훈련(8t)/추론(8i) 칩을 분리해, 두 워크로드의 메모리 대역폭·정밀도·배치 요건 차이를 인정하는 방향으로 갔다. Microsoft MAI 모델군이 서드파티 distillation 없이 상업 라이선스 데이터로만 학습된 점도 기업 self-host 선택 시 법적 경계가 배포 변수임을 보여준다.

## 2026-06-09 신호: 로컬 120B+ 기기와 실제 하드웨어 기반 모델 선택

AI Human Day 69 브리프는 로컬 추론이 7B/13B 실습을 넘어 120B+ 모델 구동 장비 논의로 올라왔음을 기록한다. Microsoft가 NVIDIA Blackwell 기반 RTX Spark와 128GB 통합 메모리를 탑재한 개발자 기기를 공개했다는 raw는, 배포 의사결정에서 "클라우드 API vs 로컬"의 기준이 모델 성능만이 아니라 메모리 용량, 양자화 수준, 개발자 장비 원가, 데이터 반출 정책으로 이동했음을 보여준다.

`whichllm` 같은 CLI는 같은 흐름의 작은 도구다. 파라미터 수나 리더보드 순위가 아니라 내 하드웨어에서 실제로 잘 도는 모델을 recency-aware benchmark로 추천한다. 실무에서는 120B 모델을 로컬로 올릴 수 있다는 홍보보다, 내 워크로드에서 tokens/sec, VRAM/UMA 사용량, quantization 품질 손실, 도구 호출 지원이 충분한지를 먼저 본다.

Apple Siri의 Gemini 기반 개편 신호는 Hybrid 패턴을 소비자 OS 레벨로 확장한다. 온디바이스 모델, 자체 서버 모델, 외부 Gemini 호출을 섞는 구조는 하나의 최고 모델이 아니라 데이터 민감도·작업 복잡도·지연시간에 따른 routing policy가 제품 품질을 결정한다는 점을 다시 확인시킨다.

## 2026-06-11 신호: OS 모델 선택제와 오픈 연구 투명성

AI Human Day 70 raw는 Apple이 OS 차원에서 ChatGPT·Gemini·Claude 중 "두뇌 모델"을 고르는 멀티모델 선택 시스템을 연 것으로 정리한다. 추론은 Private Cloud Compute에서 돌리고, 외부 모델은 라이선스·라우팅 정책으로 결합한다는 구조다(raw 원문 기준). 이는 Hybrid 배포가 더 이상 backend fallback이 아니라 사용자가 인지하는 제품 설정값으로 올라왔다는 뜻이다.

PyTorchKR의 Gemma 4 12B 신호는 edge/self-host 패턴의 기준을 낮춘다. encoder-free 통합 멀티모달 모델이 16GB VRAM 노트북에서 실행 가능하고 네이티브 오디오 입력을 지원한다면, 개발자 실습·사내 PoC·개인 에이전트는 클라우드 API 의존 없이 시작할 수 있다. 단 로컬 실행 가능성과 production SLA는 별개라, tokens/sec·메모리·도구 호출·보안 업데이트 루프를 따로 검증해야 한다.

Roko's Basilisk raw의 "openness is declining" 신호는 self-host 선택의 어두운 면이다. 공개 모델이라도 훈련 코드와 데이터가 닫혀 있으면 재현성·보안 감사·라이선스 검토가 어렵다. 배포 패턴을 고를 때 open-weight와 open-science를 구분해야 한다. 가중치 다운로드 가능성은 데이터 출처와 학습 절차 검증 가능성을 보장하지 않는다.

## Production 사례 매핑

| 서비스 | 패턴 | 핵심 기술 |
|--------|------|-----------|
| ChatGPT | Cloud API | Azure GPU 클러스터 |
| Pixel 9 Gemini Nano | Edge | LiteRT-LM, INT4 quant |
| 본 wiki `wiki_app` | Hybrid (potential) | 로컬 FastAPI + Claude API |
| 금융 엔터프라이즈 RAG | On-prem | vLLM + Llama-3 |
| 개발자 노트북 실험 | On-prem (단일) | Ollama, llama.cpp, GGUF, LM Studio |

## 관련 개념

- anthropic — Cloud API 제공사, Claude 모델 라인업
- openai — Cloud API 제공사, GPT-4o·o3 시리즈
- [claude-code](/tools/claude-code.md) — Cloud API 기반 CLI 에이전트
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — 멀티에이전트 워크트리 아키텍처
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) — Edge 배포 프레임워크 (LiteRT-LM)
- [docker-kubernetes-ai-deploy](/lecture/docker-kubernetes-ai-deploy.md) — On-prem 컨테이너 오케스트레이션
- [swe-agent-aci](/tools/swe-agent-aci.md) — 에이전트 격리 배포 패턴
- [agent-pricing-model](/concepts/agent-pricing-model.md) — 배포 형태별 비용 모델 비교
- [model-routing-cost](/concepts/model-routing-cost.md) — Cloud vs self-host 라우팅 비용 분석
- [claude-code-hook-system](/concepts/claude-code-hook-system.md) — 배포 환경별 hook 자동화
- [lora-low-rank-adaptation-2021](/papers/lora-low-rank-adaptation-2021.md) — 오픈웨이트 fine-tuning의 대표 PEFT 기법
- [attention-is-all-you-need](/papers/attention-is-all-you-need.md) — Transformer attention과 후속 효율화 계보
