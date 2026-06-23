---
type: tool
title: Claude Code
description: Claude Code는 Anthropic이 만든 CLI 기반 AI 코딩 에이전트.
tags:
- claude-code
- cli
- agent
- anthropic
timestamp: '2026-06-12'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Claude Code

## 핵심 요약

Claude Code는 Anthropic이 만든 CLI 기반 AI 코딩 에이전트. ChatGPT 같은 대화창 AI와의 근본적 차이는 **어디서 실행되는가**: 터미널 안에서 직접 파일을 읽고, 수정하고, 터미널 명령을 실행한다. PM이 코드 없이 프로토타입을 빌드하거나 멀티 에이전트 팀을 운영하는 환경으로 쓰인다.

## 상세 내용

### ChatGPT vs Claude Code 핵심 차이

| 항목 | ChatGPT | Claude Code |
|------|---------|-------------|
| 실행 환경 | 대화창 | 터미널(CLI) |
| 파일 접근 | 사람이 복붙 | 직접 읽기·수정 |
| 명령 실행 | 불가 | npm install, 테스트, 배포 등 직접 실행 |
| 프로젝트 기억 | 없음 | `CLAUDE.md`로 프로젝트 맥락 유지 |
| 에이전트 실행 | 없음 | `.claude/agents/`로 멀티 에이전트 병렬 실행 |

### 결정적 차이 4가지 (raw 원문 기준)

1. **파일시스템 직접 접근** — "이 파일 고쳐줘" 한 마디로 프로젝트 전체를 읽고 수정
2. **터미널 명령 직접 실행** — npm install, 테스트 실행, Vercel 배포까지 자율 수행
3. **프로젝트 기억 유지** — `CLAUDE.md` 파일로 매 대화마다 재설명 불필요
4. **에이전트 병렬 실행** — `.claude/agents/` 폴더의 에이전트를 동시에 구동

### 에이전트 시스템 (.claude/agents/)

각 에이전트는 마크다운 파일로 정의된다. 역할, 전문성, 행동 원칙을 파일 하나에 기술하면 그 파일이 에이전트의 "정체성"이 된다.

```
my-project/
└── .claude/
    └── agents/
        ├── researcher.md
        ├── engineer.md
        └── marketer.md
```

**실전 에이전트 구성 예시 (raw 원문 기준)**

| 에이전트 | 역할 | 트리거 상황 |
|---------|------|------------|
| `researcher` | 데이터 분석, 인터뷰 정리 | "이 데이터 분석해줘" |
| `engineer` | 기술 검토, 복잡도 산정 | "구현 가능한지 봐줘" |
| `writer` | 문서 작성, 편집 | "PRD로 정리해줘" |
| `critic` | 가정 검증, 반론 제시 | "이 결정 반박해봐" |
| `growth` | 성장 지표, 실험 설계 | "AB 테스트 어떻게 설계해?" |

`critic` 에이전트가 특히 유용: 에코 챔버 방지 장치로 PM이 놓치기 쉬운 맹점을 찾아준다.

### Human-in-the-Loop 원칙 (raw 원문 기준)

- **에이전트에게 완전히 위임**: 반복적이고 패턴이 명확한 작업, 창의성이 덜 필요한 작업
- **PM이 판단**: 에이전트 결과물 방향성 확인, 서로 다른 에이전트 의견 중 선택
- **PM만 할 수 있는 것**: 최종 기능 결정, 이해관계자 관계 관리, 전략 정합성 판단

> 에이전트는 레버리지를 높이는 도구이지, 책임을 이전하는 도구가 아니다.

### 설치

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

Pro 플랜($20/월)에서 사용 가능. 첫 실행 시 Anthropic 계정 로그인 필요.

### PM이 쓰는 3가지 패턴

1. **즉시 분석** — CSV 첨부 후 세그먼트별 인사이트 요청
2. **문서 자동 생성** — 인터뷰 노트 기반 PRD 초안 생성
3. **프로토타입 빌드** — 와이어프레임 이미지 → React 컴포넌트 생성·실행

### 2026-06-02 보강: CLAUDE.md, slash command, hook

AI Human 브리프의 Karpathy `CLAUDE.md` 사례는 프로젝트 규칙 파일이 코딩 에이전트 성능의 일부가 됐다는 신호다. 모델을 바꾸지 않아도 행동 원칙, 금지 패턴, 테스트 기준, 파일 구조를 컨텍스트로 고정하면 결과가 달라진다. 이는 [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)의 가장 작은 구현이다.

Cool Deep AI의 slash command raw는 반복 페르소나와 제약 조건을 매 세션 재입력하지 않는 패턴을 기록한다. slash command는 대규모 `CLAUDE.md`보다 더 작은 재사용 컨텍스트 단위다. 매번 "전문 마케터", "캐주얼 톤", "200자 이내"를 타이핑하는 것은 모델 문제가 아니라 작업 환경 설계 문제다.

인프런 Claude Hook 강의 업데이트는 Claude Code를 수동 도구에서 실행 하네스로 확장한다. 데일리 노트 자동 주입은 세션 시작 컨텍스트를 안정화하고, raw 폴더 보호 hook은 [260515_llm_wiki](/projects/260515_llm_wiki.md)의 raw 읽기 전용 가드레일을 코드 레벨로 강화한다. Nimbalyst v0.63.9의 Opus 4.8 지원과 Quick Open 개선은 코딩 에이전트 툴들이 모델 업데이트, 세션 검색, worktree 흐름을 빠르게 흡수하는 생태계 신호다.

### 2026-06-06 보강: 7 permission modes와 `ant` CLI

ByteByteGo EP217은 Claude Code가 에이전트의 자율 행동 범위를 통제하는 7가지 permission mode를 정리한다(raw 원문 기준): read-only → read+suggest → read+write(no shell) → read+write+shell(sandboxed) → read+write+shell(full) → bypass confirmations → custom(per-tool approval). [ai-governance-verification](/concepts/ai-governance-verification.md)의 review gate·실행 경계 원칙이 도구 기본 설정으로 내장된 사례다. NLP News는 Claude Platform이 에이전트 워크플로우용 신규 CLI `ant`를 추가했다고 기록한다 — 코딩 에이전트 도구가 권한 모델과 CLI 표면을 빠르게 확장하는 신호다.

### 2026-06-10 보강: Dynamic Workflows와 제품형 coding session

AI Engineering raw는 Claude Code Dynamic Workflows를 "Claude가 자기 작업용 하네스를 즉석에서 작성하는" 패턴으로 정리한다. 단일 세션이 긴 작업을 계속 들고 가는 대신, JavaScript 오케스트레이터가 독립 컨텍스트·모델·worktree를 가진 여러 Claude 인스턴스를 병렬 실행하고 결과를 합성한다. 해결하려는 실패 모드는 agentic laziness, self-preferential bias, goal drift다.

대표 패턴은 fan-out-and-synthesize, adversarial verification, tournament, loop until done이다. 이는 [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md)와 [agent-harness-pattern](/concepts/agent-harness-pattern.md)을 Claude Code 런타임 안으로 내린 구현이다. 다만 토큰 사용량이 크게 증가하므로 모든 작업에 쓰기보다 마이그레이션, 심층 리서치, 근본 원인 조사, 대규모 트리아지처럼 분할·검증 이득이 큰 작업에 제한하는 편이 맞다.

PyTorchKR 다이제스트도 같은 기능을 "수십~수백 서브에이전트 병렬 실행, 검증 에이전트가 납품 전 확인"으로 요약했다. Linear의 coding sessions는 이 흐름을 제품 표면으로 옮긴 사례다. Linear Agent가 issue, history, customer request, discussion, related work를 컨텍스트로 가져오고 Claude Code/Codex로 diff를 생성하며, Linear 내부에서는 incoming bug report의 약 30%를 first pass로 처리한다(raw 원문 기준). 코딩 에이전트는 CLI 단독 도구에서 issue tracker 안의 workflow actor로 이동 중이다.

## 관련 개념

- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- 260515_100_agents
- [claude-code-hook-system](/concepts/claude-code-hook-system.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [ai-governance-verification](/concepts/ai-governance-verification.md)
