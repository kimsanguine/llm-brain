---
type: concept
title: 프롬프트 엔지니어링은 시스템 설계로 진화한다
description: Ch07 프롬프트 엔지니어링의 실무 메시지는 "좋은 문장 쓰기"에서 "반복 가능한 시스템 만들기"로 이동한다.
tags:
- prompt-engineering
- system-prompt
- few-shot
- agent-governance
- memory
timestamp: '2026-06-20'
x-llmbrain-domain: AI/LLM
x-llmbrain-created: '2026-06-14'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 프롬프트 엔지니어링은 시스템 설계로 진화한다

## 핵심 요약

Ch07 프롬프트 엔지니어링의 실무 메시지는 "좋은 문장 쓰기"에서 "반복 가능한 시스템 만들기"로 이동한다. 2026-06-12~18 AI Human raw는 이 전환을 여덟 방향으로 보여준다: 자율 루프, 공유 메모리, 에이전트 거버넌스, 모델별 eval, 추론 패턴의 분해·자기수정·재사용, 자동 최적화 루프, 프롬프트 보안, 컨텍스트 레이어 설계.

## 작동 원리

### 1. 프롬프트는 루프 안으로 들어간다

Claude Code 개발자 보리스 체르니 인터뷰 신호는 사람이 매번 프롬프트를 직접 입력하는 단계가 줄고, 프롬프트가 피드백을 읽어 다음 행동을 정하는 loop system 내부 구성요소가 된다는 점을 보여준다. 이때 중요한 능력은 문장력보다 시스템 프롬프트, 피드백 기준, 재시도 조건을 설계하는 일이다.

### 2. 좋은 프롬프트는 조직 기억이 되어야 한다

아사나의 공유 메모리 신호는 개인이 프롬프트를 잘 쓰는 것만으로는 기업 생산성이 올라가지 않는다는 문제를 제기한다. 한 사람이 만든 맥락, 예시, 판단 기준이 동료와 시스템에 축적되지 않으면 AI는 매번 stateless한 개인 비서에 머문다. 그래서 프롬프트 엔지니어링은 [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)과 조직 컨텍스트 그래프 설계로 확장된다.

### 3. 시스템 프롬프트는 거버넌스 표면이다

OpenAI Lockdown Mode, Microsoft Agent 365, Anthropic Agent Skills 공개는 모두 같은 방향이다. 에이전트가 웹, 파일, MCP 서버, SaaS 도구와 연결될수록 프롬프트는 단순 지시가 아니라 권한 경계와 감사 대상이 된다. 시스템 프롬프트는 "무엇을 하라"보다 "무엇을 할 수 없고, 어떤 입력을 신뢰하지 말라"를 명시하는 보안 계층이 된다.

### 4. Few-shot은 모델별로 검증해야 한다

PROMPT-SE 2026 연구는 multi-shot 예시가 Claude Haiku에서는 정성 코딩 일치도를 끌어올렸지만 DeepSeek-Chat과 Gemini 2.5 Flash에서는 의미 있는 개선이 없었다고 정리한다. 같은 few-shot 프롬프트라도 모델별 반응이 다르므로, 예시 개수와 포맷은 감으로 고정하지 않고 agent-evaluation-frameworks처럼 eval로 비교해야 한다.

### 5. 고급 프롬프팅은 분해·자기수정·재사용이다

2026-06-14 advanced prompting 논문 세트는 Tree/Graph of Thoughts 같은 탐색 이름보다 더 실무적인 3축을 보여준다. Least-to-Most Prompting은 문제를 하위 문제로 쪼개 순차 해결하게 하고, Self-Refine은 생성 결과를 스스로 비평·수정하는 루프를 만든다. Buffer of Thoughts는 잘 푼 추론 경로를 thought-template으로 저장해 다음 문제에서 재사용한다. 즉 고급 프롬프팅의 본질은 더 긴 지시문이 아니라 **작업 분해, 피드백 루프, 경험 라이브러리**다.

### 6. 자동 프롬프트 최적화는 propose-score-refine 루프다

2026-06-15 automatic prompt optimization 논문 세트는 프롬프트 작성도 사람이 한 번에 끝내는 창작물이 아니라 탐색 가능한 설계 공간임을 보여준다. OPRO는 LLM에게 이전 해와 점수를 보여주고 더 나은 instruction을 제안하게 만들며, RLPrompt는 보상 신호로 이산 프롬프트 토큰을 학습한다. MIPRO는 단일 프롬프트를 넘어 여러 LLM 호출이 연결된 프로그램 전체의 instruction과 few-shot demo를 함께 최적화한다.

실무적으로는 "프롬프트를 잘 쓰기"보다 **후보 생성, 평가셋 실행, 점수 기록, 검증 통과 후보만 승격**하는 하네스가 중요해진다. 이 흐름은 agent-evaluation-frameworks와 [agent-harness-pattern](/concepts/agent-harness-pattern.md)에 직접 연결된다.

### 7. 공격 프롬프트와 방어 프롬프트는 같은 원리 위에 있다

2026-06-17 AI Human Daily Brief의 Fable 5 탈옥 사례는 프롬프트 기법이 양날의 도구임을 보여준다. unicode/homoglyph 치환, 롱컨텍스트 스머글링, 문서 구조 프레이밍, 픽션 프레이밍, decomposition은 모델을 더 잘 쓰기 위한 기술과 같은 구성요소를 공격 방향으로 조합한 것이다. 따라서 프롬프트 엔지니어링 교육은 "좋은 답을 끌어내는 법"만이 아니라 **신뢰할 수 없는 입력이 시스템 프롬프트와 도구 권한을 어떻게 우회하는지**까지 포함해야 한다.

같은 브리프의 Fable 5/Mythos 5 수출통제 신호는 시스템 프롬프트와 정책 가드레일이 단순 UX 설정이 아니라 모델 접근·위험 도메인·국가 규제와 연결된 거버넌스 표면임을 보강한다. Mythos 5처럼 일부 안전장치를 완화한 제한 접근 모델이 등장하면, 프롬프트/정책 레이어는 제품 기능이 아니라 배포 조건 그 자체가 된다.

### 8. 컨텍스트 엔지니어링은 프롬프트 엔지니어링의 다음 층이다

2026-06-18 브리프의 Snowflake Horizon Context + Cortex Sense 사례는 에이전트의 자신 있는 오답을 모델 문제가 아니라 컨텍스트 레이어 문제로 본다. 사람이 선언·큐레이션한 비즈니스 정의(Horizon Context)와 플랫폼이 자동 수집한 업무 맥락(Cortex Sense)을 검색 흐름에 결합하는 방식은, 시스템 프롬프트가 "어떻게 행동할지"를 정하고 컨텍스트 레이어가 "무엇을 알고 행동할지"를 정한다는 분리를 선명하게 만든다.

이 관점에서 Ch07의 마지막 메시지는 "프롬프트 문구를 더 잘 쓰자"가 아니라 "프롬프트, few-shot, 검색, 메모리, 정책을 각각 어떤 레이어로 둘 것인가"다. 이는 Ch08의 [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)과 LangChain/오케스트레이션 모듈로 넘어가는 다리다.

### 9. 모델 비종속 프롬프트는 이식성 테스트가 필요하다

2026-06-19 AI Human Day 77 브리프는 Upstage의 Solar + agent + TimelyAI 멀티 LLM 플랫폼, Microsoft의 중국 OpenAI 모델 판매, Anthropic/정부 접근 통제 신호를 같은 질문으로 묶는다. 어떤 모델을 쓸 수 있는지가 가격, 규제, 지정학, 공급자 정책에 따라 흔들리면 프롬프트는 특정 모델 최적화만으로 끝나면 안 된다.

실무 기준은 **model-agnostic prompt + model-specific adapter**다. 역할, 입력 경계, 출력 스키마, 금지 행동은 모델 공통 규칙으로 고정하고, few-shot 예시 수, reasoning verbosity, tool call 포맷은 모델별 adapter/eval로 조정한다. CoolDeep의 Task + Additional Information + Constraints + Ask 프레임워크는 이 공통 규칙의 최소 형태다. 특히 "ask clarifying questions"는 모호한 지시를 억지로 완성하지 않고 추가 컨텍스트를 요청하게 만드는 작은 안전장치다.

### 10. 프롬프트 효율은 비용과 지속가능성 문제다

2026-06-20 AI Human Day 77 브리프의 Anthropic Frontier 합류 신호는 추론 비용을 탄소와 연결한다. 프롬프트 압축, 불필요한 few-shot 제거, 출력 포맷 고정은 단순 비용 최적화가 아니라 토큰 사용량과 에너지 부담을 줄이는 운영 원칙이다. 멀티모달 생성에서도 구조화 프롬프트와 few-shot 참조는 품질을 올리는 동시에 입력 길이와 검증 비용을 함께 관리해야 한다.

## 활용 사례

- `CLAUDE.md`: 짧고 명확한 행동 원칙을 시스템 프롬프트처럼 고정해 코딩 에이전트의 반복 행동을 제어한다.
- Agent Skills: 프롬프트, 스타일 가이드, 출력 포맷, 검토 기준을 재사용 가능한 스킬 단위로 패키징한다.
- Promptfoo: 같은 프롬프트를 여러 모델에 돌려 성능과 취약점을 비교하고 CI에 연결한다.
- Agent 365: 에이전트가 어떤 신원, 기기, MCP 서버, 클라우드 자원에 연결되는지 컨텍스트 맵으로 추적한다.
- Planner-executor: Least-to-Most처럼 문제를 하위 태스크로 분해하고, 각 결과를 다음 단계 입력으로 넘긴다.
- Reflection loop: Self-Refine처럼 초안 생성 후 critique와 revision을 제한된 횟수로 반복한다.
- Experience library: Buffer of Thoughts처럼 성공한 reasoning template을 저장·검색해 반복 업무 비용을 낮춘다.
- Prompt optimizer: OPRO/MIPRO처럼 후보 프롬프트를 자동 생성하고, eval 점수로 선별해 시스템 프롬프트나 few-shot demo를 갱신한다.
- Prompt red-team: prompt injection, decomposition, long-context smuggling 같은 공격 패턴을 eval에 포함해 시스템 프롬프트와 도구 권한의 우회 가능성을 테스트한다.
- Context layer: Snowflake식 선언형 비즈니스 정의와 자동 수집 컨텍스트를 분리해, 프롬프트가 아니라 근거 데이터 품질로 정답률을 끌어올린다.
- Portability eval: 같은 시스템 프롬프트를 Solar, GPT, Claude, Gemini 등 여러 모델에 돌려 출력 스키마, 거절 기준, 도구 호출 정확도 차이를 측정한다.
- Prompt budget: few-shot 예시와 배경 맥락을 eval 기준으로 남기고, 품질에 기여하지 않는 토큰은 제거한다.

## habix/강의와의 연결점

AI Human Ch07에서 프롬프트 엔지니어링은 "CoT, few-shot, 시스템 프롬프트 기법 목록"으로만 가르치면 약하다. 더 좋은 메시지는 다음이다: 프롬프트는 제품의 런타임 제어면이고, 좋은 프롬프트는 루프, 메모리, 권한, 평가 파이프라인으로 살아남을 때 실무 자산이 된다.

강의 순서는 "생각을 쓰게 하라"보다 "문제를 나누고, 결과를 비평하고, 성공 패턴을 저장하고, 평가로 더 나은 프롬프트를 승격하라"가 낫다. 여기에 prompt injection red-team과 context layer 설계를 붙이면, Ch07은 Ch08의 planner-executor, reflection, memory, optimizer, context engineering으로 자연스럽게 이어진다.

토론 질문은 "프롬프트 엔지니어링은 사라지는가?"보다 "제품의 시스템 프롬프트와 예시 세트가 5년 뒤 모델 교체 후에도 재사용 가능한가?"가 좋다.

## 관련 개념

- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — 프롬프트에서 하네스로 엄격함의 위치가 이동
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 공유 메모리와 조직 컨텍스트 그래프
- agent-evaluation-frameworks — 모델별 프롬프트 성능 검증
- claude-code-workflow — CLAUDE.md와 Skills 운영 패턴
- [ai-governance-verification](/concepts/ai-governance-verification.md) — 시스템 프롬프트와 AI 제품 거버넌스
- [long-context-memory-management](/concepts/long-context-memory-management.md) — 프롬프트 밖 컨텍스트 보존·압축·재호출 설계
