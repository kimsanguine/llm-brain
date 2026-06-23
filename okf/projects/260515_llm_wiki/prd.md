---
type: project
title: LLM Wiki — PRD
description: LLM을 컴파일러로 쓰는 개인 지식 관리 시스템 (skill / template).
tags:
- prd
- llm-wiki
- second-brain
timestamp: '2026-05-17'
x-llmbrain-domain:
- tools
- habix
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# LLM Wiki — PRD

## 제품 정의

**LLM을 컴파일러로 쓰는 개인 지식 관리 시스템 (skill / template).**

`raw/`(원본) → `wiki/`(정제) 2계층 구조에서 LLM이 컴파일러 역할을 한다.
[karpathy](/people/karpathy.md)의 원본 패턴을 기반으로, 5가지 축에서 확장한 **Second Brain Compiler**다.
[tiago-forte](/people/tiago-forte.md)의 CODE(Capture → Organize → Distill → Express) 프레임워크를 LLM-native로 구현한 형태.

[claude-code](/tools/claude-code.md)를 실행 엔진으로 사용하며, [ai-pm-role](/concepts/ai-pm-role.md) 역할을 CLI 커맨드 체계로 자동화한다.
anthropic 모델(Claude Opus/Sonnet/Haiku)을 기본 엔진으로 사용하되, API 모드 전환 시 openai 호환 구조도 지원한다.

GitHub 레포지토리로 공개 배포 → 누구든 클론해서 자신의 wiki를 즉시 운영할 수 있다.

---

## 문제 정의

| 문제 | 현황 | 목표 |
|---|---|---|
| 지식이 흩어져 있음 | 노트, 클리핑, 회의록, PDF가 제각각 존재 | wiki/에 압축·연결된 지식으로 통합 |
| LLM 비용 장벽 | 자동화마다 별도 API 호출·과금 | CLI 재사용으로 API 키 없이도 운영 가능 |
| 지식 수명 관리 없음 | 오래된 메모가 쌓이기만 함 | distill + lifecycle으로 second brain 유지 |
| 파일 형식 제약 | MD만 지원 | PDF·Word·PPT·URL·텍스트 전부 수용 |
| 지식 그래프 없음 | 파일이 연결 없이 존재 | Obsidian Graph View로 연결 구조 시각화 |

---

## Karpathy 원본 대비 5가지 확장

[karpathy](/people/karpathy.md)가 제안한 원본 패턴([knowledge-management-tools-evolution](/concepts/knowledge-management-tools-evolution.md) 관점에서 PKM 진화의 한 이정표)을 기반으로 확장.

| 축 | Karpathy 원본 | 이 시스템 |
|---|---|---|
| **입력** | 수동 raw 파일 추가 | 4가지 입력 채널 (아래 상세) |
| **LLM 호출** | API 직접 호출 | CLI 재사용 + API 선택 가능 |
| **오퍼레이션** | ingest / query / lint | ingest / curate(distill + lifecycle) |
| **시각화** | 없음 | Obsidian 기본 내장 + CLI 연동 |
| **소스 범위** | MD 중심 | PDF · Word · PPT · URL · 텍스트 전부 |

---

## 입력 채널 (4가지)

### 채널 1 — 수동 투입
사용자가 직접 `raw/` 하위 폴더에 파일을 넣는다.
```
raw/
├── til/          # 학습 메모
├── meetings/     # 회의록
├── clippings/    # 웹 클리핑
├── notes/        # 자유 노트
└── docs/         # PDF · Word · PPT
```

### 채널 2 — `/ingest` 명령어
Claude Code 세션에서 직접 실행.
```
/ingest https://example.com          # URL 스크랩 → raw/clippings/
/ingest ~/Downloads/paper.pdf        # 파일 추출 → raw/docs/
/ingest "오늘 배운 것: ..."           # 텍스트 → raw/notes/
```

### 채널 3 — Obsidian 스크레이퍼 (선택)
Obsidian vault 경로를 `schema/sources.yaml`에 등록하면 `sync_raw.py`가 델타 미러링.
```yaml
# schema/sources.yaml
sources:
  obsidian:
    path: ~/Documents/MyVault
    include: ["til/**", "meetings/**"]
    ttl_days: 180
```

### 채널 4 — Claude Code Routines (선택)
`jobs.json`에 키워드·토픽 기반 크론 등록 → 주기적으로 특정 주제의 새 파일을 감지해 ingest.
```json
{
  "name": "wiki-daily",
  "schedule": {"kind": "cron", "expr": "0 07 * * *"},
  "payload": {"kind": "agentTurn", "message": "llm-wiki ingest 해줘"}
}
```

---

## LLM 엔진 선택

| 모드 | 명령 | 장점 | 단점 |
|---|---|---|---|
| **CLI 모드** (기본) | `claude -p "..."` | API 키 불필요 · 토큰 비용 없음 | Claude Code 설치 필요 |
| **API 모드** (선택) | Anthropic SDK 직접 | 어떤 환경에서도 실행 | API 키 · 비용 발생 |

`schema/config.yaml`에서 선택:
```yaml
llm:
  engine: cli          # cli | api
  model: claude-opus-4-7   # api 모드일 때만 사용
  api_key_env: ANTHROPIC_API_KEY
```

---

## 오퍼레이션 명세

### ingest
새 `raw/` 파일 → `wiki/` 페이지 컴파일.

지원 파일 형식:
- `.md` `.txt` — 직접 파싱
- `.pdf` — pdfplumber로 텍스트 추출
- `.docx` — python-docx로 추출
- `.pptx` — python-pptx로 슬라이드 텍스트 추출
- URL — httpx + markdownify로 스크랩

### curate
wiki 전체 감사·압축·수명 관리.

| 서브커맨드 | 역할 |
|---|---|
| `--audit` | orphan 링크·모순 감지 → curate_report.md |
| `--distill` | insights 페이지 클러스터 → 압축된 패턴 페이지 생성 |
| `--lifecycle` | TTL 초과 페이지 → archive 후보 리포트 (삭제는 사용자 확인) |
| `--all` | 세 단계 순차 실행 |

### query
wiki 내용 기반으로만 답변. raw 없으면 "raw 데이터가 필요합니다" 응답.

---

## v2 개선사항 (Second Brain 완성)

### 1. Express — wiki → 창작물 출력

Forte의 Second Brain에서 가장 중요한 단계인 Express를 시스템 안으로 편입.

사용법:
```
express blog "AI 에이전트 설계 패턴에 대해"
express lecture "context-first-orchestration" --slides 3
express summary --week
express summary --month
express report "habix 경쟁사 현황"
```

출력 저장:
- `express/blog/` — 블로그 초안 (raw/blog/에도 복사 → ingest 피드백 루프)
- `express/lecture/` — 강의 개요
- `express/summary/` — 주간·월간 요약
- `express/report/` — 심층 리포트

### 2. Capture 필터 — 공명 기반 선별

ingest 시 resonance 태그 + 중복 검사로 wiki 노이즈 방지.

```
/ingest ~/paper.pdf --resonance high
/ingest "메모" --resonance medium
```

- `resonance: high/medium/low` frontmatter 자동 기재
- `find_unprocessed --priority-only`: high 파일 우선 처리
- index.md 기반 중복 검사 → 기존 페이지에 병합 권장 경고

sources.yaml 소스 레벨 필터:
```yaml
require_keywords: [AI, LLM]
min_word_count: 100
```

### 3. 점진적 요약 — distill_level

wiki 페이지 frontmatter에 distill_level + access_count 추가:

```yaml
distill_level: 0    # 0=원문, 1=1차압축, 2=핵심강조, 3=한줄요약
access_count: 0
last_accessed: null
last_distilled: null
```

curate --distill 기준:
- access_count ≥ 5 AND distill_level < 2 → 우선 후보
- access_count ≥ 10 AND distill_level < 3 → 긴급 후보
- access_count = 0, 90일+ → lifecycle 후보
- 결과: wiki/distill_queue.md (Claude Code가 읽고 실행)

### 4. 그래프 인식 curate — curate --graph

wikilink 파싱으로 인바운드 링크 수(허브 점수) 계산:

| 허브 점수 | 판정 | 액션 |
|---|---|---|
| ≥ 5 | 핵심 개념 | distill 우선 + synthesis 후보 |
| 1~4 | 연결 개념 | 일반 사이클 |
| 0 + 90일+ | 고립 개념 | lifecycle 후보 자동 등록 |

- 결과: wiki/graph_report.md
- 허브 클러스터 감지 시 wiki/synthesis/ 합성 페이지 제안

---

## v2 시스템 워크플로우
```mermaid
flowchart LR
    subgraph INPUT["입력 채널"]
        A1[수동 raw/ 투입]
        A2[/ingest --resonance]
        A3[Obsidian 스크레이퍼]
        A4[Routines 크론]
    end

    INPUT -->|중복검사+resonance필터| B[raw/]
    B --> C{pending?}
    C -->|있음| D[LLM 엔진]
    D --> F[wiki/]
    F -->|access_count 기록| G[query]
    F -->|distill_level 점진 압축| H[curate --distill]
    F -->|링크 그래프 분석| I[curate --graph]
    F -->|창작물 출력| J[express]
    J -->|blog 피드백| B
```

---

## 시각화 — Obsidian 연동

vault root를 `llm-wiki/`로 설정하면 `raw/`·`wiki/` 양쪽이 Graph View에 표시됨.

```
llm-wiki/
├── .obsidian/     ← vault root (raw + wiki 양쪽 인식)
├── raw/
└── wiki/
```

`schema/obsidian.yaml`에서 Graph View 필터·색상 사전 설정 지원.

---

## 소스 범위

In/Out 기준: **"사용자가 raw/에 넣을 수 있는 것"은 모두 처리한다.**

| In | Out |
|---|---|
| MD · TXT · PDF · DOCX · PPTX | 이미지 단독 (텍스트 없는 JPG/PNG) |
| URL 스크랩 | 동영상 파일 |
| Obsidian vault 미러링 (선택) | 자동 소셜 미디어 포스팅 |
| Claude Code Routines 자동 ingest (선택) | 자동 삭제 (사용자 확인 필수) |
| Obsidian Graph View 시각화 | 외부 서비스 배포 |

---

## 평가 기준 (Eval)

- `ingest` 후 새 raw 파일이 wiki 페이지로 변환됨 (MD·PDF·DOCX·PPTX 각각 확인)
- `curate --audit` 후 orphan/stale 링크 리포트 생성됨
- CLI 모드: API 키 없이 `claude -p`만으로 전체 파이프라인 동작
- API 모드: `ANTHROPIC_API_KEY`만 있으면 동작
- wiki 페이지는 반드시 `sources:` frontmatter에 raw 출처 기재
- raw 없이 wiki 수정 시 CLAUDE.md 가드레일로 차단됨
- Obsidian에서 `llm-wiki/` 열면 raw/ + wiki/ 양쪽 Graph View에 표시됨

---

## 시스템 워크플로우

```mermaid
flowchart LR
    subgraph INPUT["입력 채널"]
        A1[수동 raw/ 투입]
        A2[/ingest 명령어]
        A3[Obsidian 스크레이퍼\n선택]
        A4[Routines 크론\n선택]
    end

    INPUT -->|sync_raw.py| B[raw/\nMD·PDF·DOCX·PPTX·URL]
    B -->|새 파일 감지| C{pending?}
    C -->|있음| D[LLM 엔진\ncli or api]
    C -->|없음| E[종료]
    D -->|wiki 페이지 생성| F[wiki/]
    F -->|주 1회| G[curate\naudit+distill+lifecycle]
    F --> H[Obsidian\nGraph View]
```

## 유저 플로우

```mermaid
flowchart TD
    U1[사용자: URL 발견] --> U2[/ingest URL]
    U2 --> U3[스크랩 → raw/clippings/]
    U3 --> U4[LLM: wiki 페이지 생성]
    U4 --> U5[index.md + log.md 갱신]
    U5 --> U6[Obsidian Graph View 확인]

    V1[매일 07:00 자동\n선택] --> V2[sync_raw.py]
    V2 --> V3{새 파일?}
    V3 -->|있음| V4[LLM ingest]
    V3 -->|없음| V5[종료]
    V4 --> V6[wiki 페이지 생성]

    W1[PDF/DOCX/PPTX 발견] --> W2[raw/docs/ 복사]
    W2 --> W3[텍스트 추출\npdfplumber/docx/pptx]
    W3 --> W4[LLM: wiki 페이지 생성]
```

---

## GitHub 배포 구조

```
llm-wiki/  (또는 second-brain-compiler/)
├── README.md          # 설치·사용법 (강의자료 포함)
├── CLAUDE.md          # Claude Code 운영 가이드
├── schema/
│   ├── sources.yaml   # 소스 설정 템플릿
│   ├── config.yaml    # LLM 엔진 선택
│   ├── ingest.md      # ingest 규칙
│   └── curate.md      # curate 규칙
├── scripts/
│   ├── setup.sh       # 초기 설정 자동화
│   ├── sync_raw.py    # 소스 미러링
│   ├── ingest.py      # 파일 파싱 + 상태 관리
│   └── curate.py      # 감사·압축·lifecycle
├── raw/               # .gitkeep (사용자 데이터 — .gitignore)
├── wiki/              # .gitkeep (사용자 데이터 — .gitignore)
├── pyproject.toml     # uv 의존성
└── docs/              # 강의자료
    ├── 01-concept.md
    ├── 02-setup.md
    └── 03-operations.md
```

---

## 관련 문서
- [architecture](/projects/260515_llm_wiki/architecture.md)
- [operations](/projects/260515_llm_wiki/operations.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)

## 외부 카테고리 연결
- [karpathy](/people/karpathy.md) — LLM Wiki 패턴 원조, raw→wiki 2계층 아이디어 출처
- [tiago-forte](/people/tiago-forte.md) — Second Brain CODE 프레임워크, Express 단계 설계 기반
- [knowledge-management-tools-evolution](/concepts/knowledge-management-tools-evolution.md) — PKM 도구 진화 맥락 (Notion → Obsidian → LLM-native)
- [claude-code](/tools/claude-code.md) — CLI 실행 엔진 (`claude -p`), [claude-code-agent-system](/tools/claude-code-agent-system.md) 패턴 적용
- [ai-pm-role](/concepts/ai-pm-role.md) — 자동화된 PM 오퍼레이션 설계 참조
- anthropic — 기본 LLM 엔진 공급자, Opus/Sonnet/Haiku 선택 기준
