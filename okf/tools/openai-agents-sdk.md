---
type: tool
title: OpenAI Agents SDK
tags:
- openai
- multi-agent
- mcp
timestamp: '2026-05-22'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# OpenAI Agents SDK

## 핵심 요약

`openai-agents>=0.14.0`. 파일 확인·명령 실행·코드 수정·장기 작업을 수행하는 에이전트를 위한 **샌드박스 실행환경 + 컴퓨팅 분리** SDK. Python 우선, TypeScript 예정 (2026-04-15 발표).

## 아키텍처: 실행환경과 컴퓨팅 분리

핵심 설계 원칙: 에이전트 상태(오케스트레이션)와 코드 실행 환경(샌드박스)을 물리적으로 분리한다.

| 목적 | 분리의 효과 |
|---|---|
| **보안** | 모델이 생성한 코드 실행 환경에서 자격증명 노출 차단 |
| **안정성** | 컨테이너 실패 시 스냅샷·복원으로 마지막 체크포인트부터 재개 |
| **확장성** | 서브에이전트 격리, 병렬 컨테이너로 실행 속도 향상 |

## SandboxAgent + Manifest 추상화

```python
# pip install "openai-agents>=0.14.0"
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import LocalDir
from agents.sandbox.sandboxes import UnixLocalSandboxClient

agent = SandboxAgent(
    name="Analyst",
    model="gpt-5.4",
    instructions="Answer using only files in data/. Cite source filenames.",
    default_manifest=Manifest(entries={"data": LocalDir(src=dataroom)}),
)
result = await Runner.run(
    agent, "질문",
    run_config=RunConfig(sandbox=SandboxRunConfig(client=UnixLocalSandboxClient())),
)
```

**Manifest 추상화** — 에이전트 워크스페이스 이식성 확보:
- `LocalDir` — 로컬 파일 마운트
- 클라우드: AWS S3, GCS, Azure Blob, Cloudflare R2

## 기본 구성요소 통합

| 구성요소 | 역할 |
|---|---|
| MCP (modelcontextprotocol.io) | 툴 사용 표준 프로토콜 |
| skills (agentskills.io) | 점진적 정보 제공 |
| AGENTS.md (agents.md) | 에이전트별 사용자 정의 지침 |
| shell 툴 | 코드 실행 |
| apply patch 툴 | 파일 수정 |

## 샌드박스 파트너 (내장 지원)

Blaxel · Cloudflare · Daytona · E2B · Modal · Runloop · Vercel

## 현재 상태 및 향후 계획

- 가격: 표준 API 요금 (토큰 + 툴 사용)
- Python 우선 제공 중
- 예정: TypeScript, 코드 모드, 서브에이전트, 추가 샌드박스 파트너

## 관련 개념

- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — OpenAI 4 Pillars + 하네스 이론
- [openai-realtime-api](/tools/openai-realtime-api.md) — OpenAI 플랫폼 툴 라인업
- [single-vs-multi-agent](/concepts/single-vs-multi-agent.md) — 에이전트 수 결정 프레임워크
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 에이전트 성패는 컨텍스트 설계
