# OKF Bundle — llm-brain

## concept

- [에이전트 하네스 패턴](/concepts/agent-harness-pattern.md) — 에이전트 하네스는 LLM을 감싸 확률론적 추론을 결정론적 행동으로 변환하는 런타임 인프라다.
- [Agent Paradigm Evolution](/concepts/agent-paradigm-evolution.md) — 단일 prompt에 instruction + context를 모두 넣고 LM이 답하게 함. 한계: 도구·외부 상태 접근 불가, hallucination 다수.
- [에이전트 과금 모델](/concepts/agent-pricing-model.md) — 에이전트 시장에서 가장 치열한 싸움은 모델 성능 벤치마크가 아닌 과금 단위 설계에서 벌어진다.
- [AI Education Evolution](/concepts/ai-education-evolution.md) — AI 교육 방법론은 2012년 이후 4단계로 뚜렷이 진화했다.
- [AI 거버넌스와 검증 설계](/concepts/ai-governance-verification.md) — 에이전트 거버넌스의 두 가지 핵심 위험: (1) 인지적 항복 — AI 성능이 높아질수록 인간의 검증 의지가 낮아지는 구조적 패턴, (2) 키워드 기반 보안 필터의 한계 — 에이전트가 실행 권한을 가지는 순간 키워드 필터는 우회된다.
- [AI PM 역할 전환](/concepts/ai-pm-role.md) — AI 에이전트가 코드를 짜는 시대에 PM 역할은 줄어드는 게 아니라 병목 위치가 이동한다.
- [백그라운드 에이전트와 한 명의 N KPI](/concepts/background-agent-n-kpi.md) — 백그라운드 에이전트 시대의 새 KPI는 사용자 한 명이 동시에 굴릴 수 있는 에이전트 수 N이다.
- [Classical ML and Tabular Foundation Models](/concepts/classical-ml-tabular-foundations.md) — 정형 데이터 ML의 뿌리는 두 축으로 잡는 것이 좋다.
- [Claude Code Hook 시스템](/concepts/claude-code-hook-system.md) — Claude Code의 hook은 settings.json에 정의된 자동화 트리거로, 세션 시작 시점의 스냅샷만 로드된다.
- [Code-native Visual AI](/concepts/code-native-visual-ai.md) — Visual AI의 다음 프론티어는 완성 픽셀을 바로 생성하는 것이 아니라, 픽셀을 만드는 편집 가능한 코드 아티팩트를 생성하는 방향이다.
- [Context Dealer 패턴](/concepts/context-dealer-pattern.md) — PM은 문서 작성자가 아니라 AI에게 맥락(context)을 나눠주는 사람(dealer) 이다.
- [Context-first 에이전트 오케스트레이션](/concepts/context-first-agent-orchestration.md) — 에이전트 시스템의 성패는 모델 성능이 아니라 컨텍스트 설계가 결정한다.
- [FFmpeg 자막 처리 패턴](/concepts/ffmpeg-subtitle-pipeline.md) — FFmpeg를 사용한 영상 편집 및 자막 처리 시 알아야 할 핵심 동작 패턴.
- [Forward Deployed Engineering (FDE)](/concepts/forward-deployed-engineering.md) — Forward Deployed Engineer는 frontier AI 제품을 고객사 환경 안에서 실제로 작동하게 만드는 "embedded builder" 역할이다.
- [Frontier AI Labs 비교](/concepts/frontier-labs-comparison.md) — 2024-2026 frontier AI lab 진영을 포지셔닝 축 4가지로 비교: ① safety-first vs product-first vs research-first ② 자본 구조 ③ 핵심 제품 ④ 출신 인물 그래프.
- [Generator-Evaluator 아키텍처 (PGE 패턴)](/concepts/generator-evaluator-architecture.md) — 에이전트는 자기 결과를 정확히 평가하지 못한다.
- [하네스 엔지니어링 3세대 진화](/concepts/harness-engineering-evolution.md) — 핵심 질문: "무슨 말을 해야 하나?"
- [Interaction Models](/concepts/interaction-models.md) — thinking-machines가 2026-05-11에 발표한 새로운 모델 class.
- [Knowledge Management Tools Evolution](/concepts/knowledge-management-tools-evolution.md) — 개인 지식 관리(PKM) 도구는 2000년대 이후 다섯 단계를 거쳐 진화해 왔다.
- [LLM Deployment Patterns](/concepts/llm-deployment-patterns.md) — LLM 배포는 latency·cost·privacy·scalability 4개 축의 트레이드오프로 결정된다.
- [LLM 양자화와 압축](/concepts/llm-quantization-compression.md) — LLM 양자화는 모델 품질을 크게 잃지 않으면서 메모리와 추론 비용을 줄이는 serving 기술이다.
- [긴 컨텍스트와 메모리 관리](/concepts/long-context-memory-management.md) — 긴 컨텍스트 문제는 "입력을 더 많이 넣기"가 아니라 무엇을 보존하고, 무엇을 압축하고, 언제 다시 꺼낼지의 설계 문제다.
- [모델 라우팅과 비용 최적화](/concepts/model-routing-cost.md) — 에이전트 시스템 운영에서 모델 선택 기준이 "벤치마크 순위"에서 "1달러당 성능" 으로 이동하고 있다.
- [Neural TTS Evolution](/concepts/neural-tts-evolution.md) — 신경망 TTS는 분리형 파이프라인에서 end-to-end seq2seq, 병렬 생성, LLM·코덱 기반 스트리밍 합성으로 이동했다.
- [Omnimodality](/concepts/omnimodality.md) — Omnimodal AI는 단일 모델이 텍스트·이미지·오디오 등 여러 modality를 동시에 입력받고 동시에 출력할 수 있는 구조다.
- [Physical AI와 월드 모델](/concepts/physical-ai-world-model.md) — Physical AI는 챗봇이 아니라 로봇, 자율주행차, 드론, 웨어러블처럼 현실 세계에서 움직이는 시스템을 다루는 AI 흐름이다.
- [AI 시대 PM 에이전시](/concepts/pm-agency-ai-era.md) — AI 시대 PM의 차별점은 SQL·Python·LangGraph 같은 개별 스킬 추가가 아니라 에이전시(agency)다.
- [프롬프트 엔지니어링은 시스템 설계로 진화한다](/concepts/prompt-engineering-as-system-design.md) — Ch07 프롬프트 엔지니어링의 실무 메시지는 "좋은 문장 쓰기"에서 "반복 가능한 시스템 만들기"로 이동한다.
- [RAG 아키텍처와 최적화](/concepts/rag-architecture-optimization.md) — RAG는 "검색한 청크를 프롬프트에 붙이는 기능"이 아니라 retriever와 generator를 분리해 각각 최적화하는 시스템이다.
- [Realtime Voice AI 패턴](/concepts/realtime-voice-ai-patterns.md) — 핵심 요건: 추론 품질(복잡한 요청 처리), 도구 호출 투명성(진행 상황 가청 피드백), 인터럽션 복구.
- [Recursive Self-Improvement (AI가 AI를 만든다)](/concepts/recursive-self-improvement.md) — AI가 자기 자신의 개발을 가속하는 단계.
- [단일 에이전트 vs 멀티 에이전트 결정 프레임워크](/concepts/single-vs-multi-agent.md) — 멀티 에이전트가 항상 더 좋지 않다.
- [에이전트 시대 팀 의사결정 구조](/concepts/team-decision-structure-agent-era.md) — 코딩 에이전트 시대의 PM 레버리지는 도구 선택보다 팀이 어떻게 결정하고 검증하는지를 설계하는 데 있다.
- [버티컬 에이전트와 도메인 깊이](/concepts/vertical-agent-domain-depth.md) — 버티컬 에이전트의 경쟁 축은 모델 성능 벤치마크가 아닌 도메인 깊이 × 거버넌스 설계다.
- [Video Pipeline Tools 비교](/concepts/video-pipeline-comparison.md) — 각 단계의 함정·실무 패턴은 본 wiki에서 자세히 다룸.
- [Voice AI Stack](/concepts/voice-ai-stack.md) — 음성 AI 시스템을 구성하는 4계층 아키텍처.
- [YouTube 자막 파이프라인](/concepts/youtube-subtitle-pipeline.md) — YouTube 영상에서 한국어 자막을 생성하는 파이프라인의 두 가지 경로: yt-dlp fast-path(자동 자막, 빠름)와 Whisper(STT 기반, 고품질).

## insight

- [에이전트 빌드 하네스 패턴](/insights/agent-build-harness.md) — 에이전트 빌드는 Constitution + eval.sh + RALPH Loop의 3요소 조합.
- [에이전트 스킬 최적화](/insights/agent-skill-optimization.md) — 에이전트의 반복 성능은 프롬프트 한 번이 아니라 스킬 문서라는 자연어 상태를 얼마나 잘 설계하고 갱신하느냐에 달려 있다.
- [Claude Code vs Codex CLI — 경제성·실패 모드·MCP 브릿지](/insights/claude-code-vs-codex-economics.md) — 가장 많이 출하하는 엔지니어는 둘을 비교해서 하나 고르지 않는다.
- [PPTX 자동화 제작 파이프라인 패턴](/insights/pptx-automation-patterns.md)
- [Remotion 영상 제작 패턴](/insights/remotion-video-patterns.md) — Remotion 기반 영상 제작은 remotion-best-practices 스킬 우선 적용.
- [Session Scribe 회의 자동화 시스템 패턴](/insights/session-scribe-meeting-system.md)
- [YouTube 한국어 자막 더빙 파이프라인 패턴](/insights/youtube-dubbing-patterns.md)

## lecture

- [ADsP 시험 준비 — 출제 빈도 전략 및 핵심 개념 정리](/lecture/adsp-exam-prep.md) — ADsP(데이터분석 준전문가) 자격증 대비 특강.
- [딥러닝 기초 — 퍼셉트론·MLP·CNN·시퀀스 모델](/lecture/deep-learning-fundamentals.md)
- [AI 서비스 배포 — Docker·K3D·Kubernetes 롤링 업데이트](/lecture/docker-kubernetes-ai-deploy.md) — AI 서비스 운영에서 Docker만으로는 부족한 이유를 설명하고, Kubernetes의 자동 복구·오토 스케일링·무중단 배포(롤링 업데이트) 개념을 이론(1부)과 K3D 핸즈온 실습(2부)으로 구성한 강의.
- [머신러닝 분류 알고리즘 & 성능 평가 지표](/lecture/ml-classification-algorithms.md) — 이진 분류 문제 대상으로 4종 알고리즘(로지스틱 회귀, SVM, 나이브 베이즈, KNN)의 이론과 scikit-learn 코드를 다룬 강의 + 오전 복습 퀴즈 세션.
- [판다스 데이터 분석 — 그룹화·피벗·지도 시각화](/lecture/pandas-data-analysis.md) — 소상공인 업종 데이터를 대상으로 groupby, pivottable, Folium 지도 시각화를 실습한 강의 세션.

## paper

- [ImageNet Classification with Deep Convolutional Neural Networks (AlexNet, 2012)](/papers/alexnet-imagenet-2012.md) — University of Toronto 팀(Krizhevsky · ilya-sutskever · Geoffrey Hinton)이 NIPS 2012에 발표.
- [Attention Is All You Need (2017)](/papers/attention-is-all-you-need.md) — Google Brain · Google Research가 NeurIPS 2017에 발표.
- [Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)](/papers/constitutional-ai-anthropic-2022.md) — anthropic이 2022.12 arXiv에 발표.
- [Language Models are Few-Shot Learners (GPT-3, 2020)](/papers/gpt-3-language-models-are-few-shot-learners.md) — OpenAI가 NeurIPS 2020에 발표.
- [InstructGPT: Training language models to follow instructions with human feedback (2022)](/papers/instructgpt-rlhf-2022.md) — OpenAI가 2022년 발표 (arxiv 2203.02155).
- [LoRA: Low-Rank Adaptation of Large Language Models (2021)](/papers/lora-low-rank-adaptation-2021.md) — Microsoft Research가 2021년 발표 (arxiv 2106.09685).

## person

- [Andrew Ng](/people/andrew-ng.md) — Stanford University CS 교수.
- [Dario Amodei](/people/dario-amodei.md) — anthropic CEO이자 공동 창립자.
- [Demis Hassabis](/people/demis-hassabis.md) — Google DeepMind CEO 및 공동 창립자.
- [Geoffrey Hinton](/people/geoffrey-hinton.md) — 딥러닝의 "대부(godfather)"로 불리는 컴퓨터 과학자.
- [Ilya Sutskever](/people/ilya-sutskever.md) — 전 OpenAI Chief Scientist (2015–2024) 및 공동 창립 멤버.
- [John Yang (Princeton)](/people/john-yang.md) — Princeton CS 박사과정생.
- [Andrej Karpathy](/people/karpathy.md) — "LLM을 컴파일러처럼 써라.
- [Mira Murati](/people/mira-murati.md) — 전 OpenAI CTO (2018-2024).
- [Mitchell Hashimoto](/people/mitchell-hashimoto.md) — HashiCorp 공동 창립자 (2012).
- [Sam Altman](/people/sam-altman.md) — OpenAI CEO (2019-2023, 2023.11 복귀~현재).
- [Steph Ango (kepano)](/people/steph-ango.md) — Obsidian CEO. "File over app" 철학의 주창자 — 데이터를 plain file로 사용자가 직접 소유하면 어떤 앱을 쓰든 데이터는 살아남는다.
- [Tiago Forte](/people/tiago-forte.md) — 생산성 컨설턴트, Forte Labs 창립자.
- [Yann LeCun](/people/yann-lecun.md) — Meta Chief AI Scientist 겸 NYU 교수.

## project

- [LLM Wiki 시스템](/projects/260515_llm_wiki.md) — Karpathy의 LLM wiki 패턴을 기반으로 구축한 개인 지식 컴파일 시스템.
- [LLM Wiki — 아키텍처](/projects/260515_llm_wiki/architecture.md) — karpathy의 원본 설계에서 4가지 축을 확장한다.
- [LLM Wiki — 운영 가이드](/projects/260515_llm_wiki/operations.md) — claude-code CLI(claude -p)를 실행 엔진으로 하는 명령어 체계.
- [LLM Wiki — PRD](/projects/260515_llm_wiki/prd.md) — LLM을 컴파일러로 쓰는 개인 지식 관리 시스템 (skill / template).
- [T3-TEACH 강의 운영 패턴 및 인사이트](/projects/t3-teach-lecture-operations.md) — T3-TEACH 클라이언트의 강의 세션 운영 패턴과 수강생 프로젝트 발표 트렌드를 MeetFlow 주간 요약에서 추출한 운영 인사이트.

## tool

- [Claude Code 에이전트 시스템](/tools/claude-code-agent-system.md) — Claude Code의 .claude/agents/ 폴더에 에이전트를 마크다운으로 정의하면 PM이 팀장처럼 병렬 에이전트 팀을 운영할 수 있다.
- [Claude Code](/tools/claude-code.md) — Claude Code는 Anthropic이 만든 CLI 기반 AI 코딩 에이전트.
- [Gemini Omni Flash](/tools/gemini-omni-flash.md) — 2026-05-19 Google I/O 2026에서 발표된 Gemini Omni 모델 패밀리의 첫 공개 버전.
- [Gemini Spark](/tools/gemini-spark.md) — Google이 I/O 2026 (2026-05-19) 에서 발표한 24/7 동작하는 개인 agentic assistant.
- [HyperCLOVA X OMNI](/tools/hyperclova-x-omni.md) — NAVER가 2026-01-14에 발표한 한국 omnimodal AI 모델 시리즈.
- [MediaPipe & Google AI Edge 스택](/tools/mediapipe-google-ai-edge.md) — MediaPipe는 모델이 아니라 파이프라인 프레임워크다.
- [OpenAI Agents SDK](/tools/openai-agents-sdk.md)
- [OpenAI Codex (2026)](/tools/openai-codex.md) — OpenAI가 개발한 아젠틱 코딩 AI.
- [OpenAI Realtime API](/tools/openai-realtime-api.md) — 2026-05-07 OpenAI가 Realtime API에 음성 모델 3종을 출시했다.
- [SWE-agent & Agent-Computer Interface (ACI)](/tools/swe-agent-aci.md) — Princeton 팀(John Yang, Carlos E. Jimenez 등)이 2024-05 발표한 자율 소프트웨어 엔지니어링 에이전트 시스템.
- [Whisper 생태계](/tools/whisper-ecosystem.md) — OpenAI Whisper는 레퍼런스 구현(reference implementation)이다.

## Directories

- [concepts](/concepts/index.md)
- [insights](/insights/index.md)
- [lecture](/lecture/index.md)
- [papers](/papers/index.md)
- [people](/people/index.md)
- [projects](/projects/index.md)
- [tools](/tools/index.md)
