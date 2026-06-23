---
type: project
title: LLM Wiki 시스템
description: Karpathy의 LLM wiki 패턴을 기반으로 구축한 개인 지식 컴파일 시스템.
tags:
- llm-wiki
- knowledge-management
- second-brain
- personal-tool
timestamp: '2026-06-03'
x-llmbrain-domain:
- tools
- habix
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM Wiki 시스템

## 핵심 요약

Karpathy의 LLM wiki 패턴을 기반으로 구축한 개인 지식 컴파일 시스템.
`raw/`(원본) → `wiki/`(정제) 2계층 구조에서 LLM이 컴파일러 역할을 한다.
OpenClaw vault의 TIL·회의록·뉴스레터를 매일 자동 미러링해 wiki로 정제한다.

## 설계 결정

### Karpathy 원본 대비 확장

| 항목 | Karpathy 원본 | 이 시스템 |
|---|---|---|
| 입력 | 수동 raw 파일 추가 | OpenClaw vault 자동 미러링 |
| 오퍼레이션 | ingest / query / lint | sync / ingest / curate(audit+distill+lifecycle) |
| LLM 호출 | API 직접 | Claude Code CLI 재사용 (API 키 불필요) |
| 시각화 | 없음 | Obsidian Graph View |

### 핵심 가드레일
- raw 없이 wiki 수정 금지 (hallucination 방지)
- query 중 wiki 편집 금지
- lifecycle 삭제는 사용자 확인 후만 실행

### 2026-06-02 운영 보강

인프런 Claude Hook 강의 업데이트는 이 시스템의 두 가드레일을 교육 가능한 실습으로 바꿨다. 데일리 노트 자동 주입은 세션 시작 컨텍스트를 안정화하고, raw 폴더 보호 hook은 `raw/` 읽기 전용 원칙을 실행 레벨에서 강제한다. 즉 [claude-code-hook-system](/concepts/claude-code-hook-system.md)은 LLM Wiki의 운영 안정성을 높이는 보조 장치다.

같은 날 TIL은 llm-brain 저장소를 전면 정비한 기록을 남겼다. launchd 제거, git 위생, adversarial/code-review, E2E 페르소나 7에이전트 검증, weekly curate cron wiring까지 닫았고 테스트는 60개에서 122개로 늘었다. 여기서 얻은 핵심 교훈은 보안/입력 검증 강화가 정상 중첩 slug를 깨뜨릴 수 있다는 점이다. 따라서 이 프로젝트의 검증 원칙은 "더 엄격하게"가 아니라 **허용 계약을 보존하면서 실패 경계를 좁히는 것**이다.

### curate = lint + distill + lifecycle
Karpathy 원본 lint를 확장: 감사(orphan/모순) + 압축(insights 생성) + 수명 관리(archive 후보)

## 아키텍처

```
[소스]                          [raw/]          [wiki/]
OpenClaw TIL (48+)    ──sync──▶ raw/til/  ──▶  insights/
OpenClaw meetings     ──sync──▶ raw/meetings/──▶ (요약 반영)
OpenClaw context      ──sync──▶ raw/context/──▶ business/
habix blog            ──sync──▶ raw/blog/  ──▶ projects/
/ingest URL           ──────▶  raw/clippings/──▶ concepts/ or tools/
```

## 오퍼레이션 명령어

| 명령어 | 트리거 | 역할 |
|---|---|---|
| `sync` | launchd 매일 07:00 | 소스 → raw/ 미러링 |
| `ingest` | sync 후 자동 + Claude Code 온디맨드 | raw/ → wiki/ 컴파일 |
| `curate --all` | 매주 월요일 | 감사 + 압축 + lifecycle 후보 |
| `/ingest URL` | Claude Code에서 직접 | URL 스크랩 + 즉시 ingest |

## 파일 위치

| 파일 | 경로 |
|---|---|
| 운영 규칙 | `~/llm-wiki/CLAUDE.md` |
| 소스 설정 | `~/llm-wiki/schema/sources.yaml` |
| ingest 규칙 | `~/llm-wiki/schema/ingest.md` |
| curate 규칙 | `~/llm-wiki/schema/curate.md` |
| 전체 목차 | `~/llm-wiki/index.md` |
| 실행 로그 | `~/llm-wiki/log.md` |

## 개발 문서
- PRD — 요구사항, 사용자 스토리, 워크플로우 (프로젝트 내부 docs/)
- Architecture — 계층 구조, 스크립트 설계, TTL (프로젝트 내부 docs/)
- Operations — 운영 가이드, 명령어, launchd, 트러블슈팅 (프로젝트 내부 docs/)

## 관련 개념
- [karpathy](/people/karpathy.md)
- 260515_openclaw
- habix-universe
- [claude-code-hook-system](/concepts/claude-code-hook-system.md)
- agent-evaluation-frameworks
