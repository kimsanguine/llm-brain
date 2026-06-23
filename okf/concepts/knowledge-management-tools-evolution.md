---
type: concept
title: Knowledge Management Tools Evolution
description: 개인 지식 관리(PKM) 도구는 2000년대 이후 다섯 단계를 거쳐 진화해 왔다.
tags:
- knowledge-management
- evolution
- synthesis-hub
- second-brain
- tools-comparison
timestamp: '2026-06-02'
x-llmbrain-domain:
- knowledge-management
- tools
x-llmbrain-created: '2026-05-26'
x-llmbrain-sources:
- https://obsidian.md
- https://roamresearch.com
- https://notion.so
- https://fortelabs.com
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Knowledge Management Tools Evolution

개인 지식 관리(PKM) 도구는 2000년대 이후 다섯 단계를 거쳐 진화해 왔다. 각 단계는 이전 단계의 핵심 한계를 해결하는 방식으로 등장했다.

---

## Stage 1 — Hierarchical (Folders/Notebooks)

**시기**: 2000년대 초반  
**대표 도구**: Evernote (2008), OneNote, MediaWiki 등

폴더-노트북 계층 구조로 정보를 저장한다. 검색은 가능하지만 개념 간 연결은 수동으로 관리해야 한다.

**핵심 한계**:
- 정보 1개가 정확히 한 위치에만 존재 — 다중 맥락 적용 불가
- cross-reference가 약해 시간이 지날수록 고립된 노트 섬 형성
- 계층 설계가 잘못되면 검색 자체가 병목

---

## Stage 2 — Bi-directional Linking (2020-)

**시기**: 2019~2021  
**대표 도구**: Roam Research (2019), Obsidian (2020)

이중 대괄호(double-bracket) wikilink 문법 + backlinks + daily notes 패턴이 PKM 표준으로 자리잡는다. 노트 간 양방향 연결을 자동 생성하여 지식 그래프를 형성한다.

**Roam Research**: Conor White-Sullivan이 설계. 아웃라이너 기반 블록 단위 링크, daily page를 기본 진입점으로 사용.  
**Obsidian**: [steph-ango](/people/steph-ango.md) (kepano) CEO. "File over app" 철학 — 마크다운 로컬 파일 + 풍부한 plugin 생태계 + Graph View.

본 wiki([260515_llm_wiki](/projects/260515_llm_wiki.md))는 Obsidian의 wikilink 문법 위에 구축되어 있다.

---

## Stage 3 — CODE 프레임워크 + Progressive Summarization

**시기**: 2022  
**대표**: [tiago-forte](/people/tiago-forte.md) "Building a Second Brain" (2022)

정보 저장 방식이 아닌 **정보 활용 워크플로우**를 체계화한다.

**CODE = Capture · Organize · Distill · Express**

- **Capture**: 외부 자료를 마찰 없이 수집
- **Organize**: 프로젝트·영역·자료·아카이브(PARA) 구조로 분류
- **Distill**: Progressive Summarization — 반복 열람할 때마다 핵심을 점진적으로 강조
- **Express**: 축적된 지식을 실제 결과물(글·발표·보고서)로 전환

**핵심 인사이트**: Distill과 Express가 Knowledge Management의 진짜 목적이다. 저장만 하고 활용하지 않는 시스템은 가치가 없다.

본 wiki의 `distill_level` 필드와 `express` 명령어는 이 프레임워크에서 직접 파생됐다.

---

## Stage 4 — LLM Wiki (2024-)

**시기**: 2024~  
**원형**: [karpathy](/people/karpathy.md) LLM Wiki 개념 — "raw 소스를 LLM이 컴파일해 wiki 생성"

기존 PKM이 사람이 직접 distill·organize하는 방식이었다면, LLM Wiki는 이 과정을 LLM이 자동 대행한다.

**차별점**:
- raw → 컴파일(LLM) → wiki 파이프라인
- 사용자는 원천 자료(raw/)만 제공, 구조화는 LLM이 담당
- 링크 추론, 중복 병합, distill_level 점진 압축도 자동화 가능

본 wiki([260515_llm_wiki](/projects/260515_llm_wiki.md))는 이 개념의 직접 구현체다.

---

## Stage 5 — Live Second Brain (현재 진화 방향)

**시기**: 2025~  
**구현**: 본 wiki 시스템 (`ingest → wiki → curate → express` 폐쇄 루프)

단순한 컴파일을 넘어 **능동적으로 질문에 답하는 살아있는 두뇌**를 지향한다.

- `ingest`: 외부 자료를 raw/에 수집 + 자동 wiki 생성
- `curate`: distill 압축 + 그래프 분석 + TTL 기반 아카이브
- `express`: wiki 컨텍스트 기반 블로그·강의·보고서 자동 생성
- `query`: 사용자가 질문하면 LLM이 본인 wiki 컨텍스트로 답변 (AI endpoint streaming UX)

**다음 진화 방향**:
- cross-vault federation (복수 wiki 간 링크)
- time-aware versioning (개념의 시간적 변화 추적)
- 에이전트가 자율적으로 ingest 후보 탐색

### 2026-06-01 세미나 신호

패스트캠퍼스 무료 세미나 미팅 raw는 LLM Wiki가 내부 운영 도구를 넘어 교육 상품의 전면 주제가 됐다는 신호다. 확정 주제는 “나만의 세컨드 브레인 구축 — 클로드 코드로 진정한 업무 운영 체계를 만드는 방법 (feat. LLM Wiki)”이며, 2026-06-25 오후 8:30 진행으로 정리됐다.

세미나 구성은 Claude Code와 Obsidian 연결, Routines 기반 지식 축적, 정리 자동화, 변호사를 위한 SaaS 프로덕트 사례, 강의 소개, 20년차 PM H-plan 소개로 잡혔다. 이는 Second Brain을 노트 앱 사용법이 아니라 업무 운영 체계 + 에이전트 메모리 + 실전 SaaS 사례로 패키징하는 방향이다.

실행 액션은 6/2까지 마스터시트 세부구성·세미나 정보 탭 작성, 6/4까지 홍보 허가 커뮤니티 링크 공유다. Claude Code와 Codex를 함께 쓸 경우 촬영 전 PM에게 고지해야 한다.

---

## 진영 비교

| 도구 | 대표 인물 | 핵심 정신 |
|---|---|---|
| Roam Research | Conor White-Sullivan | bi-directional linking 정착 |
| Obsidian | [steph-ango](/people/steph-ango.md) | "File over app" 로컬 마크다운 |
| Notion | Ivan Zhao | all-in-one SaaS workspace |
| Building a Second Brain | [tiago-forte](/people/tiago-forte.md) | Progressive Summarization + CODE |
| LLM Wiki | [karpathy](/people/karpathy.md) | LLM-as-compiler |
| 본 wiki | — | Live Second Brain 폐쇄 루프 |

---

## 관련 개념

- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [tiago-forte](/people/tiago-forte.md)
- [karpathy](/people/karpathy.md)
- [steph-ango](/people/steph-ango.md)
