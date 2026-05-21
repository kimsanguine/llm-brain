# llm-brain Graph Delta & Canvas 기능 설계 스펙

**작성일**: 2026-05-22
**상태**: 승인됨
**대상 브랜치**: main

---

## 배경 및 목적

llm-brain은 Karpathy LLM Wiki 패턴(ingest·query)과 Tiago Forte Second Brain 철학(curate·express)을 통합한 개인 지식 컴파일러다. 현재 시스템의 주요 불편 사항:

1. `/ingest` 후 wiki에서 무엇이 바뀌었는지 알 수 없음 (그래프 델타 없음)
2. `/query` 결과에서 해당 개념의 연결 맥락을 시각적으로 탐색할 수 없음
3. `curate --graph`는 전체 정적 스냅샷만 생성해 실질적 가치가 낮음

**목표**: 기존 4개 커맨드(/ingest, /curate, /query, /express) 구조를 유지하면서 그래프 델타 추적과 Obsidian Canvas 시각화를 추가한다.

---

## 설계 원칙

- **커맨드 추가 없음**: 기존 4개 커맨드(/ingest, /curate, /query, /express)만 사용
- **역할 명확화**: ingest=수집+변경추적, curate=품질관리, query=탐색+시각화
- **Obsidian 연동**: Canvas 파일로 Claude Code 세션 중 생성 → Obsidian에서 즉시 확인
- **git 범위**: `wiki/canvas/`, `wiki/.graph_prev.json`은 gitignore (개인 탐색 결과)

---

## 아키텍처 개요

```
/ingest (enhanced)
├── raw/ → wiki/ 컴파일 (기존)
├── pre-snapshot: graph.json → .graph_prev.json
├── export_graph.py 재실행 → graph.json 갱신
├── delta 계산: prev vs current
├── 터미널 출력: 신규/갱신/제거 노드+엣지
└── wiki/canvas/ingest-delta.canvas 생성

/curate (simplified)
├── --distill   ✅ 유지
├── --lifecycle ✅ 유지
├── --audit     ✅ 유지
└── --graph     ❌ 제거

/query (enhanced)
├── wiki 기반 답변 (기존)
├── access_count 갱신 (기존)
├── graph.json에서 primary 페이지 연결 조회
├── 연결 요약 출력 (inbound N / outbound M)
└── wiki/canvas/query-<slug>.canvas 생성

/express — 변경 없음
```

---

## 컴포넌트 상세 스펙

### 1. `/ingest` 강화

#### 1-1. pre-snapshot

ingest 컴파일 시작 전, 현재 `wiki/graph.json`을 `wiki/.graph_prev.json`으로 복사한다.

- `wiki/graph.json` 없으면 `.graph_prev.json`도 없음으로 취급 (최초 실행 = 전체가 신규)
- `.graph_prev.json`은 `.gitignore`에 추가

#### 1-2. export_graph.py 재실행

wiki 컴파일 완료 후 `scripts/export_graph.py`를 실행해 `wiki/graph.json`을 갱신한다.

기존 `export_graph.py`는 수정하지 않는다. ingest 흐름에서 호출만 추가한다.

#### 1-3. delta 계산

```python
# delta 정의
신규 노드  = {n.id for n in current.nodes} - {n.id for n in prev.nodes}
제거 노드  = {n.id for n in prev.nodes} - {n.id for n in current.nodes}
            단, kind="ghost" 노드는 제거 노드에서 제외
갱신 노드  = 두 그래프 모두 존재 + inbound_count 변경된 page 노드
신규 엣지  = {(e.source, e.target) for e in current.links}
           - {(e.source, e.target) for e in prev.links}
```

#### 1-4. 터미널 출력 형식

```
[ingest] delta — {신규}개 신규, {갱신}개 갱신, {제거}개 제거
  + {slug}  ({category}/)  inbound 0 → {n}
  ~ {slug}  ({category}/)  inbound {prev} → {current}
  - {slug}  ({category}/)  제거됨
  엣지 +{n}: {source} → {target} 외 {n-1}개
[ingest] canvas → wiki/canvas/ingest-delta.canvas
```

delta가 없으면 `[ingest] delta — 변경 없음` 출력 후 canvas 생성 생략.

#### 1-5. ingest-delta.canvas 구조

Obsidian Canvas JSON 형식 (`{"nodes": [...], "edges": [...]}`)

**노드 배치 규칙:**
- 신규/갱신 노드를 중앙 행에 배치 (x 간격 320px)
- 각 신규 노드의 직접 inbound 노드를 왼쪽 열에 배치
- 각 신규 노드의 직접 outbound 노드를 오른쪽 열에 배치
- inbound/outbound 각 최대 5개 표시

**색상 규칙 (Obsidian Canvas color 필드 — 1=빨강 2=주황 3=노랑 4=초록 5=청록 6=보라):**
| 노드 종류 | color |
|----------|-------|
| 신규 노드 | "3" (노란색) |
| 갱신 노드 | "6" (보라색) |
| 맥락 노드 (기존) | 없음 (기본) |

**노드 타입:** `"file"` (wiki/*.md 경로 참조)

---

### 2. `/curate` 간소화

#### 2-1. curate.py 변경

`--graph` 플래그 및 `run_graph()` 호출 제거.
`--all` 실행 시 graph 제외: audit + distill + lifecycle만 실행.

#### 2-2. .claude/commands/curate.md 변경

`--graph` 모드 설명 제거.
`--all` 설명에서 graph 항목 제거.

#### 2-3. curate의 새 역할 정의

```
curate = wiki 품질 관리

--distill   : access_count 기반 LLM 압축 (Forte Distill)
--lifecycle : TTL 초과 + inbound 0 페이지 archive 후보 분류
--audit     : 고아 페이지, stale wikilink 탐지
--purge     : audit 결과 기반 실제 이동
```

그래프 탐색은 ingest(delta canvas)와 query(neighborhood canvas)가 담당한다.

---

### 3. `/query` 강화

#### 3-1. 연결 요약 출력

답변에 사용된 primary 페이지(access_count 갱신 대상 중 첫 번째)에 대해:

```
[query] 참조: [[{slug}]]  인바운드 {n} / 아웃바운드 {m}
  ◀ inbound:  {slug1}, {slug2} 외 {n-2}개
  ▶ outbound: {slug3}, {slug4} 외 {m-2}개
[query] canvas → wiki/canvas/query-{slug}.canvas
```

`wiki/graph.json`이 없으면 연결 요약 및 canvas 생성을 건너뜀.

#### 3-2. query-{slug}.canvas 구조

**레이아웃 (1-depth 네이버후드):**

```
왼쪽 열 (inbound, 최대 5개)   중앙 (쿼리 노드)   오른쪽 열 (outbound, 최대 5개)
────────────────────────────   ──────────────────   ─────────────────────────────
inbound_A ──▶                 ┌────────────────┐    ──▶ outbound_D
inbound_B ──▶                 │  target_node   │    ──▶ outbound_E
inbound_C ──▶                 │  color: "4"    │    ──▶ outbound_F
                              └────────────────┘
```

- 쿼리 노드: color "4" (초록색, 현재 위치 강조)
- inbound 노드: x = -340, y 간격 120px
- outbound 노드: x = +340, y 간격 120px
- 쿼리 노드: x = 0, y = 0, width = 300, height = 80

답변에서 참조된 페이지가 여러 개일 경우 **첫 번째 페이지만** canvas 생성 (파일명 충돌 방지).

---

### 4. 파일 구조 변경

#### 신규 파일/디렉토리

```
wiki/
└── canvas/                  ← 신규 디렉토리
    ├── ingest-delta.canvas  ← ingest마다 덮어씀
    └── query-<slug>.canvas  ← query마다 생성 (덮어씀)
```

#### .gitignore 추가

```
wiki/.graph_prev.json
wiki/canvas/
```

#### 변경 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `scripts/ingest.py` | delta 계산 함수 + canvas 생성 함수 추가 |
| `scripts/curate.py` | `--graph` 플래그 및 `run_graph()` 제거 |
| `.claude/commands/ingest.md` | delta + canvas 단계 추가 |
| `.claude/commands/curate.md` | `--graph` 설명 제거 |
| `.claude/commands/query.md` | 연결 요약 + canvas 단계 추가 |
| `.gitignore` | `wiki/.graph_prev.json`, `wiki/canvas/` 추가 |

`scripts/export_graph.py` — 변경 없음 (ingest.py에서 subprocess 호출)

---

## 엣지 케이스 처리

| 상황 | 처리 |
|------|------|
| 최초 ingest (graph_prev 없음) | 전체 노드를 신규로 취급, delta 출력 |
| wiki 페이지 0개 | export_graph.py 실행 생략, canvas 미생성 |
| delta 없음 (변경 없음) | `[ingest] delta — 변경 없음`, canvas 미생성 |
| query 대상 페이지가 graph.json에 없음 | 연결 요약 생략, canvas 미생성 |
| canvas 디렉토리 없음 | ingest/query 실행 시 자동 생성 |
| inbound/outbound 5개 초과 | inbound_count 내림차순 상위 5개만 표시 |

---

## 구현 범위 외 (이번 스펙 제외)

- Obsidian 플러그인 개발 (Obsidian → Claude 트리거, D 시나리오)
- canvas 히스토리 관리 (과거 delta 보존)
- 실시간 watch 모드 (파일 변경 감지 자동 ingest)
- express canvas 출력

---

## 검증 기준

| 기능 | 검증 방법 |
|------|----------|
| ingest delta 출력 | URL ingest 후 신규 노드가 터미널에 출력되는지 확인 |
| ingest-delta.canvas 생성 | Obsidian에서 canvas 파일이 열리고 노드가 올바르게 배치되는지 확인 |
| curate --graph 제거 | `curate --graph` 실행 시 unknown argument 오류 발생 확인 |
| query canvas 생성 | `/query` 실행 후 `wiki/canvas/query-*.canvas` 파일 생성 확인 |
| query canvas 내용 | inbound/outbound 노드가 올바른 위치에 배치되는지 Obsidian에서 확인 |
