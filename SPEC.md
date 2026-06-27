# llm-brain — Technical Specification

## 시스템 개요

- **제품명**: llm-brain (Second Brain Compiler)
- **버전**: v2.0
- **GitHub**: github.com/kimsanguine/llm-brain
- **아키텍처**: `raw/`(원본) → `wiki/`(정제) 2계층 + `express/`(출력) 레이어
- **컨셉**: LLM을 컴파일러로 사용하는 개인 지식 관리 시스템. Karpathy 원본 패턴 기반, 5축 확장.

---

## 디렉토리 구조 (전체)

```
260516_llm_brain/
├── CLAUDE.md                    # Claude Code 운영 가이드 (역할·가드레일·명령어)
├── README.md
├── SPEC.md                      # 이 파일
├── pyproject.toml               # uv 의존성 (name: llm-wiki)
├── index.md                     # 전체 wiki 목차
├── log.md                       # 실행 이력
├── wiki_stats.json              # 페이지 접근 통계 (access_count, last_accessed)
├── .ingest_state.json           # 처리 완료 raw 파일 목록
├── .sync_state.json             # 소스별 마지막 동기화 시각
├── .launchd.log                 # launchd 실행 로그
│
├── scripts/                     # 자동화 스크립트
│   ├── ingest.py                # raw/ 탐지·스크랩·노트 저장 + 상태 관리
│   ├── sync_raw.py              # sources.yaml → raw/ 델타 미러링
│   ├── curate.py                # wiki 감사·압축·lifecycle (--health, --suggest-bridges)
│   ├── export_graph.py          # wikilink 그래프 export → wiki/graph.json
│   ├── okf_export.py            # wiki/ → OKF v0.1 호환 번들 okf/ 투영 (export 포트)
│   ├── express.py               # wiki → 창작물 초안 컨텍스트 준비
│   └── setup.sh                 # 초기 설정 (venv·폴더·config 생성)
│
├── schema/                      # 운영 규칙 파일
│   ├── sources.yaml             # 소스 경로·TTL·필터 설정
│   ├── sources.example.yaml     # 소스 설정 템플릿
│   ├── config.yaml              # LLM 엔진 선택 (cli / api)
│   ├── domains.yaml             # 도메인 분류 규칙 및 키워드 매핑
│   ├── ingest.md                # ingest 절차·품질 기준 규칙
│   ├── curate.md                # curate 단계별 규칙
│   ├── okf.md                   # OKF ↔ llm-brain 매핑 규칙 레퍼런스
│   └── okf_export.yaml          # okf_export 제외 설정 (exclude_paths·domains·slugs)
│
├── raw/                         # 원본 소스 (.gitignore 대상)
│   ├── til/                     # OpenClaw TIL 미러 (sync_raw)
│   ├── meetings/                # OpenClaw 회의록 미러 (sync_raw)
│   ├── newsletters/             # AI 뉴스레터 미러 (sync_raw)
│   ├── context/                 # 비즈니스 컨텍스트 미러 (sync_raw)
│   ├── blog/                    # habix blog 콘텐츠 미러 (sync_raw + express 피드백)
│   ├── clippings/               # URL 수동 스크랩 (ingest --url)
│   ├── notes/                   # 텍스트 수동 노트 (ingest --note)
│   └── docs/                    # 로컬 파일 추가 (ingest --file)
│
├── wiki/                        # LLM 정제 결과 (.gitignore 대상)
│   ├── concepts/                # AI·기술 개념 페이지
│   ├── tools/                   # 도구·프레임워크 페이지
│   ├── people/                  # 인물 페이지
│   ├── projects/                # 프로젝트 인사이트 페이지
│   ├── business/                # 시장·경쟁사·전략 페이지
│   ├── lecture/                 # 강의 지식 페이지
│   ├── insights/                # TIL 정제본·반복 패턴
│   ├── archive/                 # lifecycle으로 이동된 만료 페이지
│   ├── curate_report.md         # curate 실행 결과 보고서
│   ├── distill_queue.md         # distill 우선순위 큐
│   └── graph.json               # wikilink 그래프 데이터 (export_graph.py 생성)
│
├── express/                     # 창작물 출력 레이어
│   ├── blog/                    # 블로그 포스트 초안
│   ├── lecture/                 # 강의 슬라이드 초안
│   ├── summary/                 # 주간·월간 요약 초안
│   └── report/                  # 심층 리포트 초안
│
├── okf/                         # OKF v0.1 호환 번들 (okf_export.py 생성, Git 커밋 대상)
│   ├── index.md                 # 번들 루트 목차 (type별 그룹 + 디렉토리 index 링크)
│   ├── log.md                   # export 이력 + 변환 경고
│   ├── .okf-bundle              # 번들 센티넬 (재export 시 안전 정리용 마커)
│   └── {dir}/                   # 디렉토리별 미러 + index.md (business/·canvas/ 제외)
│
├── wiki_app/                    # HTML 검색·페이지뷰 (FastAPI + vanilla JS, port 8000)
│   ├── __main__.py              # uv run python -m wiki_app
│   ├── api.py                   # 6 endpoints (/api/index, /api/search, /api/page/{slug}, /api/page/{slug}/graph, /api/ai-answer, /api/ai-answer/stream)
│   ├── search.py                # Index + B 알고리즘 + C 확장 (본문 grep)
│   ├── pages.py                 # 페이지 로더 (frontmatter + body + graph metadata)
│   ├── render.py                # markdown-it + [[wikilink]] SPA 앵커 후처리
│   ├── access.py                # access_count 갱신 (명시적 경로·원자적 쓰기·threading.Lock)
│   └── static/
│       ├── index.html           # 3 views (empty / results / empty-results)
│       ├── styles.css           # Pretendard + 디자인 톤
│       └── app.js               # 상태관리·검색·페이지뷰·AI 모달
│
└── .obsidian/                   # Obsidian vault 설정 (Graph View 연동)
```

---

## 스크립트 인터페이스

### scripts/ingest.py

raw/ 폴더에서 미처리 파일을 탐지하고, URL·파일·노트를 raw/에 저장하며, 처리 상태를 `.ingest_state.json`으로 관리한다. 실제 wiki 컴파일은 LLM(claude CLI 또는 API)이 담당한다.

#### WIKI_ROOT 계산 방식

```python
WIKI_ROOT = Path(__file__).parent.parent  # scripts/../ → 프로젝트 루트
```

`scripts/ingest.py`가 `scripts/` 내에 있으므로, `__file__`의 두 단계 상위가 프로젝트 루트가 된다.

#### 지원 파일 형식 및 추출 라이브러리

| 확장자 | 추출 방법 |
|--------|----------|
| `.md`, `.txt` | 직접 읽기 (`Path.read_text`) |
| `.pdf` | `fitz` (pymupdf) — `fitz.open` + `page.get_text()` |
| `.docx` | `python-docx` — `Document(file).paragraphs` |
| `.pptx` | `python-pptx` — `slide.shapes[].text_frame.text` |

#### CLI 인자 전체

| 인자 | 타입 | 설명 |
|------|------|------|
| `--url URL` | str | 지정 URL을 스크랩해 `raw/clippings/YYYY-MM-DD-{slug}.md`로 저장 |
| `--file PATH` | str | 로컬 파일을 `raw/docs/YYYY-MM-DD-{filename}`으로 복사. `.md`·`.txt` 외 형식은 `.extracted.md`도 함께 저장 |
| `--note TEXT` | str | 텍스트를 `raw/notes/YYYY-MM-DD-HHmm-note.md`로 저장 |
| `--mark-done` | flag | 현재 `raw/`의 모든 파일을 처리 완료로 `.ingest_state.json`에 기록 |
| `--resonance` | choices: `high`\|`medium`\|`low` | `--url`·`--file`·`--note`와 함께 사용. 저장 파일의 frontmatter에 `resonance: {값}` 기록 |
| `--priority-only` | flag | 미처리 파일 중 frontmatter에 `resonance: high`인 파일만 출력 |

#### 종료 코드 의미

| 코드 | 의미 |
|------|------|
| `0` | 처리할 새 파일 없음 |
| `1` | 미처리 파일이 1개 이상 존재 (`run_daily.sh`가 이를 감지해 LLM 호출 결정) |

#### resonance 필터 동작

`--priority-only` 플래그 사용 시, `.ingest_state.json` 미등록 파일 중 frontmatter 첫 줄에 `resonance: high` 패턴(`re.search(r"^resonance:\s*(\S+)", ...)`)이 있는 파일만 반환한다. `.md`·`.txt` 형식만 frontmatter 파싱 대상이며 다른 형식은 None 처리한다.

#### 중복 검사 동작

`is_duplicate(file)` 함수가 `--url`·`--file`·`--note` 저장 후 호출된다. `index.md`의 `[[wikilink]]` 목록을 파싱해 파일명 slug(날짜 접두사 `YYYY-MM-DD-` 제거, `_→-`, 소문자 변환)와 비교한다. 중복이면 경고 메시지를 출력하지만 **저장을 중단하지 않는다**.

---

### scripts/sync_raw.py

`schema/sources.yaml`에 등록된 소스 경로에서 `raw/` 폴더로 델타 미러링한다. 변경·신규 파일만 복사하며, `raw/` 파일은 삭제하지 않는다.

#### sources.yaml 스키마

`schema/sources.yaml` 섹션 참조.

#### 지원 extensions

기본값: `{".md", ".txt", ".pdf", ".docx", ".pptx"}`.  
`sources[].extensions` 필드가 설정된 경우 해당 확장자로 제한된다.  
형식: `[md, txt]` → 내부에서 `.md`, `.txt`로 변환.

#### 델타 미러링 로직 (mtime 기반)

`.sync_state.json`에서 `source_id`의 마지막 동기화 시각(`last_sync`)을 로드한다. 소스 디렉토리를 재귀 순회하며 `src_file.stat().st_mtime <= last_sync_dt.timestamp()`인 파일은 건너뛴다. 복사 후 `state[source_id] = datetime.now().isoformat()`으로 기록한다.

`exclude_tags`가 설정된 경우, `python-frontmatter`로 파일 frontmatter를 파싱해 `tags`와 교집합이 있으면 건너뛴다.

#### .sync_state.json 구조

```json
{
  "til": "2026-05-17T07:00:12.345678",
  "meetings": "2026-05-17T07:00:13.456789",
  "newsletters": "2026-05-16T07:00:10.123456"
}
```

키: `source_id` (sources.yaml의 `id` 필드), 값: ISO 8601 datetime 문자열.

---

### scripts/curate.py

wiki 전체를 감사(audit) + 압축(distill) + 수명 관리(lifecycle)하는 복합 오퍼레이션.
그래프 export는 별도 `scripts/export_graph.py`가 담당한다.

#### CLI 인자 전체

| 인자 | 설명 |
|------|------|
| `--all` | audit + distill + lifecycle 전체 실행 |
| `--audit` | orphan 페이지·stale 링크 탐지 |
| `--distill` | distill 후보 분류 및 `wiki/distill_queue.md` 생성 |
| `--lifecycle` | lifecycle archive/delete 후보 목록 생성 |
| `--purge` | `curate_report.md`의 archive 후보를 `wiki/archive/`로 실제 이동 |
| `--record-access PAGE_SLUG` | `wiki_stats.json`에 페이지 접근 기록 (query 모드에서 호출) |
| `--health` | graph health 지표 출력 (avg degree, components, BC top, low-degree count) |
| `--suggest-bridges N` | betweenness/structural-hole 기반 missing link 추천 N개 |

인자 없이 실행하면 `--all`과 동일하게 동작한다.

#### distill_level 단계 정의

`distill_level`은 wiki 페이지 frontmatter 필드. 값이 높을수록 더 많이 압축된 상태.

| 값 | 의미 |
|----|------|
| `0` | 미압축 (ingest 직후 기본값) |
| `1` | 1차 압축 완료 |
| `2` | 2차 압축 완료 |
| `3` | 최종 압축 (더 이상 압축 불필요) |

#### 출력 파일

| 파일 | 생성 조건 |
|------|----------|
| `wiki/curate_report.md` | 항상 생성 (audit·distill·lifecycle 결과 통합) |
| `wiki/distill_queue.md` | `--distill` 또는 `--all` 실행 시 |

---

### scripts/export_graph.py

`[[wikilink]]`를 파싱해 D3 force-graph용 JSON으로 export하는 독립 스크립트.

#### 출력 파일

| 파일 | 설명 |
|------|------|
| `wiki/graph.json` | 노드(페이지)·엣지(wikilink) 데이터. `wiki_app` `/api/page/{slug}/graph` 엔드포인트가 이 파일을 읽는다. |

#### 허브 점수 계산 방식

- **허브**: inbound 링크 수 ≥ 5
- **연결**: inbound 링크 수 1–4
- **고립**: inbound 링크 수 = 0 AND age > 90일

#### wiki_stats.json 구조

```json
{
  "page-slug": {
    "access_count": 2,
    "last_accessed": "2026-05-16"
  }
}
```

`curate --record-access PAGE_SLUG` 호출 시 `wiki_stats.json`의 `access_count` 증가, `last_accessed` 갱신 (frontmatter는 갱신하지 않음). 웹 페이지뷰(`wiki_app/access.track`)는 frontmatter와 `wiki_stats.json` 둘 다 갱신한다. distill 시 frontmatter의 `access_count`와 `wiki_stats.json`의 값 중 큰 값을 사용한다.

---

### scripts/okf_export.py

`wiki/`(내부 슈퍼셋)를 OKF v0.1 호환 번들 `okf/`로 투영하는 export 포트. 내부 포맷은 바꾸지 않고 경계(`okf/`)에서만 변환한다. frontmatter 파서(`parse_frontmatter`·`FRONTMATTER_RE`·`WIKILINK_RE`)는 `scripts/export_graph.py`에서 import하며 export_graph는 수정하지 않는다.

변환 규칙 전문은 `schema/okf.md`, 제외 설정은 `schema/okf_export.yaml` 참조.

#### 변환 동작 요약

- **frontmatter**: OKF 예약 6필드(`type`·`title`·`description`·`resource`·`tags`·`timestamp`) 순서로 매핑. `updated`(없으면 `created`)를 `timestamp`로 매핑. 나머지 내부 필드는 `x-llmbrain-{key}`로 보존(`--strip-internal`이면 제거).
- **본문 wikilink**: `[[X]]` → `[X](/<rel>)` 번들 루트 절대경로 마크다운 링크. 별칭은 `[[X|별칭]]` → `[별칭](/<rel>)`. 깨진 링크(대상 없음)는 텍스트화 + `log.md` 기록. 제외 페이지를 가리키던 링크는 별칭을 버리고 slug만 남긴다(redact).
- **description**: fm `description` → 본문 `## 핵심` 첫 문장 → 첫 문단 첫 문장 순으로 규칙 기반 추출(LLM 호출 없음). 300자 절삭.
- **exclude**: 경로 글롭(기본 `business/**`·`canvas/**`) + domain 라벨 + slug. 경로 글롭이 1차 보안 필터.

#### CLI 인자 전체

| 인자 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--out PATH` | str | `okf/` | 출력 번들 루트. 상대경로는 레포 루트 기준 |
| `--strip-internal` | flag | off | OKF 예약 6필드만 남기고 `x-llmbrain-*` 전부 제거 (외부 공유 최소본) |
| `--config PATH` | str | `schema/okf_export.yaml` | 제외 설정 파일. 부재 시 하드코딩 기본값 사용 |
| `--exclude-path GLOB` | str (복수) | `[]` | 추가 제외 경로 글롭. 설정 파일 값에 누적 |
| `--exclude-domain D` | str (복수) | `[]` | frontmatter `domain` 라벨 기준 제외 (보조 필터) |
| `--exclude-slug SLUG` | str (복수) | `[]` | 특정 slug 명시 제외 |
| `--dry-run` | flag | off | 파일 0개 작성, export 대상·통계만 출력 (public 커밋 전 보안 게이트용) |

`exclude_paths`·`exclude_domains`·`exclude_slugs`·`sensitive_patterns` 최종값 = `schema/okf_export.yaml`(커밋됨) + gitignored `schema/okf_export.local.yaml` + CLI 인자(누적).

#### 보안 — 민감정보 게이트

| 메커니즘 | 동작 |
|---|---|
| `exclude_paths` (경로 글롭) | `business/**`·`canvas/**` 등 경로째 번들에서 제외. 1차 방어선 |
| `sensitive_patterns` (본문 스캐너) | included 페이지 본문/description 평문을 대소문자 무시 스캔 → `sensitive_hits`로 dry-run/log 표면화(차단 아님, 사람 검토용). 페이지 제외로 못 막는 본문 평문 실명·운영수치 탐지 |
| `exclude_slugs` (페이지 제외) | dry-run 검토 후 누출 확인된 페이지를 명시 제외 |
| 로컬 분리 | 🔴 실명·내부명 같은 민감 값은 **gitignored `schema/okf_export.local.yaml`에만** 둔다. 커밋되는 `okf_export.yaml`에 넣으면 그 자체가 누출. main()이 두 파일을 병합 |
| fail-loud 경고 | `okf_export.local.yaml` 부재 시(fresh clone/CI) 게이트 비활성 → stderr에 🔴 경고. 그 상태로 커밋 금지 |

#### 출력 파일

| 파일 | 설명 |
|------|------|
| `okf/{dir}/{slug}.md` | 변환된 frontmatter + 본문. 실제 wiki 디렉토리 구조를 미러 |
| `okf/{dir}/index.md` | 디렉토리별 목차 (title + description 링크) |
| `okf/index.md` | 번들 루트 목차 (type별 섹션 + Directories 섹션) |
| `okf/log.md` | export 이력 + 변환 경고 (깨진 링크·제외 페이지·skipped) |
| `okf/.okf-bundle` | 번들 센티넬. 재export 시 이 마커가 있는 디렉토리만 안전하게 정리 |

#### 안전 가드

- `raw/`·`wiki/`는 읽기 전용. 출력은 `out_dir`(기본 `okf/`)에만.
- `out_dir`가 `wiki_dir`이거나 그 조상(레포 루트 등)이면 거부(`rmtree` 데이터 손실 방지).
- `out_dir`가 심볼릭 링크면 거부(`resolve()` 전 원본 인자로 검사 — 링크 대상 삭제 방지).
- 비어있지 않은 `out_dir`에 `.okf-bundle` 마커가 없으면 덮어쓰기 거부.
- frontmatter 값의 `---`는 em-dash로 치환, date/datetime은 ISO 문자열로 직렬화 (OKF consumer의 `text.split("---")`·`json.dumps` 호환 보장).

#### 호환성 단일 진실 — 링크 정규식

OKF minimal consumer는 본문에서 `\]\((/[^)]+\.md)\)` 패턴으로 엣지를 추출한다. export가 만드는 모든 페이지 링크는 `/`로 시작하는 번들 루트 절대경로 + `.md` 끝이라 이 패턴에 잡힌다. 라운드트립 검증: **콘텐츠 노드 수 = export 페이지 수**, 엣지 수 = 깨지지 않은 wikilink 수.

> ⚠ minimal consumer가 `rglob("*.md")`로 노드를 모으면 페이지 외에 디렉토리별 `index.md`·`log.md`도 노드로 잡힌다(OKF 관례 파일). 라운드트립에서 "노드 = 페이지 수"를 검증하려면 frontmatter `title`이 없는 메타 파일(index/log)을 콘텐츠 노드에서 제외하고 센다.

---

### scripts/express.py

wiki/ 페이지를 읽어 창작물(블로그, 강의, 요약, 리포트) 초안 컨텍스트를 준비한다. 실제 LLM 합성은 Claude Code가 담당하며, 이 스크립트는 관련 페이지 수집·경로 안내 역할을 한다.

#### CLI 인자 전체 (subcommand 방식)

```
uv run python scripts/express.py blog TOPIC
uv run python scripts/express.py lecture TOPIC [--slides N]
uv run python scripts/express.py summary (--week | --month)
uv run python scripts/express.py report TOPIC
```

| subcommand | 인자 | 기본값 | 설명 |
|------------|------|--------|------|
| `blog` | `topic` (positional) | — | 블로그 포스트 초안. 관련 페이지 최대 5개 수집 |
| `lecture` | `topic` (positional), `--slides N` | slides=5 | 강의 슬라이드 초안. 관련 페이지 최대 6개 수집 |
| `summary` | `--week` 또는 `--month` (mutually exclusive, required) | — | 주간(7일) 또는 월간(30일) 요약 |
| `report` | `topic` (positional) | — | 심층 리포트. 관련 페이지 최대 8개 수집 |

#### 관련 페이지 수집 알고리즘 (index.md 파싱 + 키워드 점수)

`collect_related_pages(topic, max_pages)` 함수:

1. `index.md` 전체 텍스트를 로드한다.
2. `topic`을 공백·하이픈·슬래시로 분리해 키워드 목록을 만든다 (2자 이상만).
3. `[[slug]] — 설명` 패턴의 줄을 파싱한다.
4. `slug + 설명` 문자열에서 각 키워드 등장 횟수의 합산을 점수로 계산한다.
5. 점수 내림차순으로 상위 `max_pages`개를 선택한다.
6. 각 slug에 대해 `wiki/` 전체에서 `{slug}.md` 파일을 탐색해 내용을 반환한다.

`summary`는 `collect_recent_pages(days)` 방식: `wiki/insights/`, `wiki/concepts/`, `wiki/projects/`에서 frontmatter `updated:` 또는 mtime 기준으로 최근 N일 이내 파일을 반환.

#### 출력 경로 규칙

```
express/{type}/YYYY-MM-DD-{slug}.md
```

- `blog` → `express/blog/2026-05-17-ai-agent-design-pattern.md`
- `lecture` → `express/lecture/2026-05-17-context-first-orchestration.md`
- `summary` → `express/summary/2026-05-17-weekly-summary.md`
- `report` → `express/report/2026-05-17-habix-competitor.md`

slug 생성: 소문자·숫자·하이픈만 허용, 연속 하이픈 합치기, 60자 절삭.

#### blog 피드백 루프 (raw/blog/ 복사)

`cmd_blog()` 실행 시 `express/blog/` 저장 후 `raw/blog/`에도 동일 파일을 복사한다. 이로써 blog 초안이 다음 ingest 사이클에서 wiki로 재컴파일되는 피드백 루프가 형성된다.

---

## 스키마 명세

### schema/sources.yaml 필드

`sources` 배열의 각 항목:

| 필드 | 필수 | 타입 | 설명 |
|------|------|------|------|
| `id` | 필수 | str | 소스 고유 식별자. `.sync_state.json`의 키로 사용 |
| `source` | 필수 | str | 소스 디렉토리 경로. `~/` 확장 지원 |
| `target` | 필수 | str | `raw/` 하위 대상 경로. 예) `raw/til/` |
| `ttl_days` | 선택 | int | lifecycle TTL. `0`이면 만료 없음 |
| `extensions` | 선택 | list[str] | 복사할 확장자 목록. 미설정 시 전체 5종 지원 |
| `exclude_tags` | 선택 | list[str] | frontmatter `tags`에 이 값이 포함되면 복사 제외 |
| `require_keywords` | 선택 | list[str] | (예약) 이 키워드가 포함된 파일만 복사 |
| `min_word_count` | 선택 | int | (예약) 최소 단어 수 미만 파일 제외 |
| `disabled` | 선택 | bool | `true`이면 해당 소스 전체 건너뜀 |
| `note` | 선택 | str | 소스 설명 (사람이 읽는 주석) |

`lifecycle` 섹션:

| 필드 | 설명 |
|------|------|
| `archive_dir` | archive 대상 폴더. 기본값: `wiki/archive/` |
| `domains.{name}.ttl_days` | 도메인별 TTL. `0`이면 lifecycle 대상 제외 |

현재 도메인별 TTL:

| 도메인 | ttl_days |
|--------|----------|
| concepts, tools, people, projects, business, lecture | 0 (영구) |
| insights | 365 |

### schema/config.yaml 필드

| 필드 | 값 예시 | 설명 |
|------|---------|------|
| `llm.engine` | `cli` \| `api` | LLM 호출 방식 선택 |
| `llm.model` | `claude-opus-4-7` | API 모드에서 사용할 모델 ID |
| `llm.api_key_env` | `ANTHROPIC_API_KEY` | API 모드에서 읽을 환경변수명 |
| `llm.max_tokens` | `8192` | API 모드 최대 토큰 수 |

### wiki 페이지 frontmatter 전체 필드

```yaml
---
title: 페이지 제목
type: concept | tool | person | project | business | lecture | insight
domain: AI/LLM | teaching | habix | tools | personal-projects
tags: [태그1, 태그2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/파일경로1, raw/파일경로2]
distill_level: 0          # 0~3, curate --distill이 관리
access_count: 0           # 웹 페이지뷰(wiki_app)가 갱신; CLI curate --record-access는 wiki_stats.json만 갱신 후 distill 시 동기화
last_accessed: null       # YYYY-MM-DD
last_distilled: null      # YYYY-MM-DD
resonance: high | medium | low   # ingest 시 수동 지정 (선택)
---
```

`distill_level`, `access_count`, `last_accessed`, `last_distilled`는 `curate.py`의 `ensure_distill_fields()`가 없으면 자동으로 기본값을 추가한다.

---

## 상태 파일

### .ingest_state.json 구조

```json
{
  "processed": [
    "raw/til/2026-05-15-rag-patterns.md",
    "raw/newsletters/2026-05-14-weekly.md"
  ]
}
```

`processed` 배열: WIKI_ROOT 기준 상대 경로 문자열 목록. `--mark-done` 실행 시 현재 `raw/`의 모든 파일로 덮어쓴다.

### .sync_state.json 구조

```json
{
  "til": "2026-05-17T07:00:12.345678",
  "meetings": "2026-05-16T07:00:10.123456"
}
```

키: `source_id`, 값: ISO 8601 datetime. 없는 키는 `"1970-01-01T00:00:00"`으로 간주한다.

### wiki_stats.json 구조

```json
{
  "page-slug": {
    "access_count": 2,
    "last_accessed": "2026-05-16"
  }
}
```

파일 위치: WIKI_ROOT 바로 아래 (`wiki_stats.json`). 갱신 경로는 두 가지이며 동작이 다르다.

| 경로 | frontmatter 갱신 | wiki_stats.json 갱신 |
|------|-----------------|----------------------|
| 웹 페이지뷰 (`wiki_app/access.track`) | O (원자적 쓰기) | O |
| CLI `curate --record-access SLUG` | X | O |

`distill` 실행 시 두 값 중 큰 값을 취해 frontmatter와 동기화한다.

---

## 의존성

`pyproject.toml` 기준 (name: `llm-wiki`, requires-python: `>=3.11`):

| 패키지 | 버전 제약 | 용도 |
|--------|-----------|------|
| `pyyaml` | ≥6.0 | `schema/sources.yaml`, `schema/config.yaml` 파싱 |
| `pymupdf` | ≥1.24.0 | PDF 텍스트 추출 (`fitz` 모듈명) |
| `markdownify` | ≥0.12.0 | URL 스크랩 시 HTML → Markdown 변환 |
| `httpx` | ≥0.27.0 | URL 스크랩 HTTP 요청 |
| `python-frontmatter` | ≥1.1.0 | `sync_raw.py`의 `exclude_tags` 필터링용 frontmatter 파싱 |
| `python-docx` | ≥1.1.0 | `.docx` 텍스트 추출 |
| `python-pptx` | ≥0.6.23 | `.pptx` 텍스트 추출 |
| `anthropic` | ≥0.40.0 | API 모드 LLM 호출 (engine: api 선택 시 사용) |

설치: `uv sync` 또는 `pip install -e .`

---

## 자동화 — OpenClaw cron (구 launchd, 2026-06-02 전환)

> **2026-06-02 변경:** launchd 잡 `ai.habix.llm-wiki`는 macOS TCC가 `~/Documents` 하위 스크립트 exec을 차단해 매일 `exit 126`으로 실패(`.launchd.log` 도배)하여 **제거**했다. 데일리 자동화는 이제 OpenClaw cron `llm-wiki-daily`(`~/.openclaw/cron/jobs.json`, `0 07 * * *` Asia/Seoul, `agentTurn`)가 담당하며 STEP 1 `sync_raw.py --quiet` → STEP 2 `ingest.py` 미처리 확인 → STEP 3 CLAUDE.md 규칙대로 claude ingest 후 `ingest.py --mark-done`을 수행한다. **STEP 4(주간 월요일 `curate --audit --lifecycle` + distill)도 2026-06-02 cron 페이로드에 추가**되어 `date +%u == 1`(월요일)에만 실행된다. 아래 launchd/`run_daily.sh` 기술은 **참조용**이다.

### (참조) 구 launchd 설정

### plist 경로

```
~/Library/LaunchAgents/ai.habix.llm-wiki.plist
```

Label: `ai.habix.llm-wiki`

### 실행 시간

매일 오전 7시 0분 (`StartCalendarInterval: Hour=7, Minute=0`).  
`RunAtLoad: false` — 등록 즉시 실행하지 않음.

로그 경로: `260516_llm_brain/.launchd.log` (stdout·stderr 동일 파일)

### run_daily.sh 4단계 플로우

스크립트 위치: `wiki/projects/260515_llm_wiki/scripts/run_daily.sh`

| 단계 | 동작 | 조건 |
|------|------|------|
| **Step 1** | `sync_raw.py --quiet` 실행 — sources.yaml 소스에서 raw/ 델타 미러링 | 항상 실행 |
| **Step 2** | `ingest.py` 실행 — 미처리 raw 파일 수 확인 | 항상 실행 |
| **Step 3** | `claude --dangerously-skip-permissions -p "...ingest 해줘"` 실행 후 `ingest.py --mark-done` | Step 2 exit code = 1 (미처리 파일 있음) 시에만 실행 |
| **Step 4** | `curate.py --audit --lifecycle` 후 `claude -p "...distill 해줘"` 실행 | 매주 월요일(`$(date '+%u') = "1"`)에만 실행 |

---

## LLM 엔진 통합

### CLI 모드 (기본, engine: cli)

`schema/config.yaml`의 `engine: cli` 설정 시 사용. Claude Code CLI를 재사용한다.

```bash
claude --dangerously-skip-permissions -p "프롬프트 내용" >> "$LOG" 2>&1
```

- API 키 불필요
- Claude Code 설치 필수
- `run_daily.sh`에서 직접 호출. 세션 없이 단발 실행.

### API 모드 (engine: api, 미구현 — 인터페이스 예약)

`schema/config.yaml`의 `engine: api` 설정 시 사용 예정. `anthropic` 패키지를 통해 직접 호출.

```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ[config["llm"]["api_key_env"]])
response = client.messages.create(
    model=config["llm"]["model"],
    max_tokens=config["llm"]["max_tokens"],
    messages=[{"role": "user", "content": prompt}],
)
```

- 환경변수: `ANTHROPIC_API_KEY` (또는 `api_key_env` 지정값)
- 모델: `claude-opus-4-7` (기본값)
- 최대 토큰: `8192` (기본값)

현재 `scripts/` 내 어느 스크립트도 API 모드를 실제 호출하지 않는다. `config.yaml` 파싱은 `setup.sh`에서만 초기화하며, LLM 호출 분기는 향후 구현 예정.

---

## 커맨드 라우팅 테이블

| 사용자 발화 | 실행 스크립트 | LLM 액션 |
|-------------|---------------|----------|
| `uv run python scripts/ingest.py` | `ingest.py` | 없음 (미처리 파일 목록 출력만) |
| `uv run python scripts/ingest.py --url URL` | `ingest.py` | 없음 (스크랩 후 raw/ 저장) |
| `uv run python scripts/ingest.py --file PATH` | `ingest.py` | 없음 (복사 후 raw/ 저장) |
| `uv run python scripts/ingest.py --note TEXT` | `ingest.py` | 없음 (raw/ 저장) |
| `uv run python scripts/ingest.py --priority-only` | `ingest.py` | 없음 (high resonance 목록만) |
| `uv run python scripts/ingest.py --mark-done` | `ingest.py` | 없음 (상태 기록) |
| `uv run python scripts/sync_raw.py` | `sync_raw.py` | 없음 (파일 복사만) |
| `uv run python scripts/curate.py --audit` | `curate.py` | 없음 (정적 분석) |
| `uv run python scripts/curate.py --distill` | `curate.py` | 없음 (`distill_queue.md` 생성만) |
| `uv run python scripts/curate.py --lifecycle` | `curate.py` | 없음 (후보 목록 출력) |
| `uv run python scripts/export_graph.py` | `export_graph.py` | 없음 (`wiki/graph.json` 생성) |
| `uv run python scripts/okf_export.py [--dry-run] [--strip-internal]` | `okf_export.py` | 없음 (규칙 기반 변환 → `okf/` 번들 생성, dry-run은 목록만) |
| `uv run python scripts/curate.py --purge` | `curate.py` | 없음 (파일 이동) |
| `uv run python scripts/curate.py --record-access SLUG` | `curate.py` | 없음 (stats 기록) |
| `uv run python scripts/express.py blog TOPIC` | `express.py` | Claude가 `express/blog/*.md` 읽고 본문 작성 |
| `uv run python scripts/express.py lecture TOPIC --slides N` | `express.py` | Claude가 `express/lecture/*.md` 읽고 슬라이드 작성 |
| `uv run python scripts/express.py summary --week` | `express.py` | Claude가 `express/summary/*.md` 읽고 요약 작성 |
| `uv run python scripts/express.py summary --month` | `express.py` | Claude가 `express/summary/*.md` 읽고 요약 작성 |
| `uv run python scripts/express.py report TOPIC` | `express.py` | Claude가 `express/report/*.md` 읽고 리포트 작성 |
| "ingest 해줘" (Claude Code 세션) | `CLAUDE.md` → `ingest.py` | Claude가 raw/ 읽고 wiki/ 컴파일 |
| "curate 해줘" (Claude Code 세션) | `CLAUDE.md` → `curate.py` | Claude가 wiki/ 감사·distill 수행 |
| "RAG에 대해 알려줘" (Claude Code 세션) | `CLAUDE.md` query 모드 | Claude가 `index.md` → wiki 페이지 로드 후 답변 |
| launchd 매일 07:00 | `run_daily.sh` | Step 3·4에서 `claude -p` 호출 |

---

# Agent Memory OS Upgrade — 설계 (v2.1 목표, 미구현)

> **상태**: 설계 확정 · 미구현. 본 절은 *구현 설계서(HOW)*다. 구현 시작 시 각 인터페이스는 위
> "스크립트 인터페이스"·"스키마 명세" 절로 현재형 이관한다.
> **요구사항(WHAT)**: `docs/PRD.md` (llm-brain Agent Memory OS Upgrade).
> **진행·결정 로그**: `docs/PROGRESS.md` → "Agent Memory OS Upgrade" 이니셔티브.
> **근거 모델**: AI 에이전트 메모리 5층 구조(작업·에피소드·의미·절차·메타).

## §A — 척추: 폴더가 아니라 제어 루프

5층 모델의 핵심은 폴더 5개가 아니라 **계획시점 읽기 → 턴 이후 쓰기 → 오프라인 제어**의 순환이다.
의미 기억(semantic)은 이미 있는 `wiki/`이고, 나머지는 이 루프의 저장 기질·제어기다.

```
            ① 계획 시점에 읽기 (작업 기억 = 휘발성, 저장 안 함)
   ┌──────────────  scripts/brain_context.py  ──────────────┐
   │  goal + 관련 semantic(wiki) + 최근 episode + 후보 procedure + 제약 │
   └───────────────────────┬─────────────────────────────────┘
                           │ 이 팩을 들고 실행
   ┌───────────────────────▼─────────────────────────────────┐
   │  실행: ingest · express · query(wiki_app) · curate         │
   └───────────────────────┬─────────────────────────────────┘
                           │ ② 턴 이후 쓰기 (append-only, fail-soft)
                  scripts/episode.py → episodes/YYYY-MM.jsonl
                           │
   ┌───────────────────────▼─────────────────────────────────┐
   │  ③ 오프라인 제어 (메타 기억): curate memory_score          │
   │     promote / merge / archive / decay 판정 + rescue        │
   └───────────────────────┬─────────────────────────────────┘
                           │ 되먹임: 건강한 semantic만 생존
                           └────→ 다음 ①이 더 좋은 기억을 읽음
```

차별 레버는 폴더(episodes/·procedures/)가 아니라 **②→③→① 되먹임**이다.

## §B — 모듈 지도 (격리: 각 단위 = 한 책임 + 명시 인터페이스)

| 모듈 | 상태 | 단일 책임 | 인터페이스 | 의존 | PRD US |
|---|---|---|---|---|---|
| `scripts/lib/frontmatter_utils.py` | 신규(토대) | frontmatter 파싱 단일 출처(fail-loud) | `read_fm(text)->(dict,body)`, `write_fm(fm,body)->str` | pyyaml | 003 토대 |
| `scripts/episode.py` | 신규 | append-only 에피소드 원장 | `append(record)->None`, `read_recent(task_type,topic,limit)->list[dict]` | 표준 라이브러리 | 001 |
| `scripts/brain_context.py` | 신규 | 작업기억 팩 조립(휘발성) | CLI `--task --topic --type --max-pages [--json]` | `express.collect_related_pages`, `episode.read_recent`, procedures loader | 005 |
| `procedures/` + loader | 신규 | 재사용 절차 저장/로드 | `list_procedures()`, `read_procedure(slug)->(fm,body)` | frontmatter_utils | 004 |
| `scripts/curate.py` | **변경** | +메타 점수(기존 distill 위) | `compute_memory_score(entry, graph, fm)->float` | graph.json, episodes, express/ | 006 |
| `scripts/express.py` | **변경** | +재사용 메타 frontmatter, +episode 기록 | `save_draft` 직후 `episode.append` | episode | 007·002 |
| `scripts/ingest.py` | **변경** | +staging episode 기록 | 저장 성공 직후 `episode.append`(status=pending) | episode | 002 |
| `wiki_app/api.py` | **변경** | +AI답변 episode 기록 | `_collect_context` 직후 `episode.append` | episode | 002 |
| `scripts/memory_health.py` | 신규 | 읽기전용 건강 리포트 | `--report` → `wiki/memory_health_report.md` | episode, curate, frontmatter_utils | 008 |
| `schema/okf_export.yaml` | **변경** | 방어 제외 2줄 | `exclude_paths += episodes/**, procedures/**` | — | 보안 |

**격리 원칙:** `brain_context`는 웹 계층(`wiki_app/search.py`)이 아니라 `scripts/express.collect_related_pages`(현 75–106행, 이미 결정적)를 재사용 — 스크립트가 웹에 의존하지 않게. `frontmatter_utils`는 **신규 코드 + US가 건드리는 리더만** 채택(현재 4벌 파서 중 `export_graph.py` 등 미접촉 파일은 그대로 = Rule 3).

## §C — 파일 계약

### C1. 에피소드 레코드 — `episodes/YYYY-MM.jsonl` (월별 샤드, append-only)

1줄 1 JSON 객체. 필수 키:

```json
{ "timestamp": "2026-06-27T07:30:00+09:00",
  "task_type": "express_blog|ingest_url|ingest_file|ingest_note|curate|ai_answer",
  "user_goal": "string",
  "inputs": {},
  "read_pages": ["wiki/concepts/x.md"],
  "procedures_used": ["collect_related_pages"],
  "outputs": {},
  "status": "ok|pending_wiki_compilation|draft_ready|timeout|error",
  "notes": "string" }
```

- `episode.append(record)`: 필수 키·타입 검증 → 위반 시 `EpisodeSchemaError` (헬퍼는 **fail-loud**).
- **호출측은 try/except로 감싸 warn+continue** (메인 명령 경로는 **fail-soft** = PRD US-002 AC·FR-8).
- 샤드 파일명은 `timestamp`의 `YYYY-MM`에서 도출. 기존 줄은 절대 재작성 안 함.
- `read_recent(task_type=None, topic=None, limit=N)`: 최신 샤드부터, `timestamp` desc 결정적 정렬, `topic`은 `user_goal`/`inputs` 키워드 매칭.

### C2. frontmatter 신규 필드 (US-003, 전부 optional·null-safe)

기존 frontmatter 블록(위 "wiki 페이지 frontmatter 전체 필드")에 **추가 예정** 필드. python-frontmatter 관용 파싱이라 없는 페이지도 유효(무파손 실측):

```yaml
memory_type: semantic      # semantic | episodic | procedural | meta | working
retention: durable         # durable | seasonal | ephemeral (decay 힌트)
confidence: 0.9            # 0..1 float (선택)
source_count: 6           # len(sources) 캐시 (선택)
last_verified: 2026-06-27 # date (선택)
decay_policy: default     # 명명된 정책 키 (선택)
```

`procedures/` 파일은 `memory_type: procedural`. OKF export 시 keep 모드 → `x-llmbrain-*`, `--strip-internal` → 전부 제거(§D).

### C3. brain_context 팩 (US-005)

`brain_context.py --task "..." --topic "..." --type query|express|curate|custom --max-pages N [--json]`
→ 결정적 순서 6 섹션(테스트 가능):

1. **목표** (`--task`)
2. **관련 semantic 페이지** — `express.collect_related_pages(topic, max_pages)` 재사용
3. **최근 관련 episode** — `episode.read_recent(task_type=--type, topic, limit)`
4. **후보 procedure** — procedures loader, topic 키워드 필터
5. **제약** — CLAUDE.md 가드레일(raw 출처 없는 wiki 사실 금지 등) 정적 주입
6. **출처 경로** — 포함 페이지의 raw/ provenance

markdown 기본, `--json`은 동일 구조. <1s 목표(file-first, 임베딩 없음).

### C4. memory_score (US-006, 재사용 우선·결정적)

```
score = 35·norm(express_reuse) + 25·norm(episode_ref) + 15·norm(centrality)
      + 10·norm(access_count)  + 10·recency         +  5·norm(source_count)
```

- `norm(x) = min(x / CAP, 1.0)`. **CAP·가중치는 `schema/config.yaml`** (사람 튜닝 = Rule 5).
- `centrality = w1·inbound_degree + w2·betweenness` (`wiki/graph.json`).
- `recency` = age 감쇠(예: <30일 1.0 → 365일 0.0 선형).
- `express_reuse` = `express/` 산출물이 이 slug를 `source_pages`/`[[link]]`로 인용한 횟수(express/ 스캔, 캐시).
- `episode_ref` = episode `read_pages`에 이 slug가 등장한 횟수(episode 샤드 집계).
- **PRD US-006 입력 대비 v1 매핑(추적성):** `resonance` v1 제외(wiki frontmatter 미저장 — 컴파일 시 필터링; v2 후순). `stale_age`는 `recency` 감쇠에 흡수(별도 항 아님). `contradiction_risk`는 v1 제외(교차 페이지 의미 매칭 필요 = 범위 밖). `episode_ref`는 PRD 미열거 신호이나 재사용 우선 철학에 따라 추가. → 나머지 6개(express_reuse·access·recency·centrality·source_count + episode_ref)만 점수화.
- **plug-in 지점: `curate.py` `run_distill()` 현 343–356행.** 임계 게이트(access≥10/distill<3=urgent 등)는 **유지**(신규 페이지 보호·backward-compat). 점수는 ① tier 내 정렬 + ② **rescue**: archive 게이트(access==0·age>90)에 걸린 페이지가 `score ≥ RESCUE_THRESHOLD`면 archive 대신 promote/keep-review.
- `distill_queue.md`·`curate_report.md`에 점수+사유 기입(top promote / merge-review / archive-review / decay).
- `config.yaml` 부재 시 옛 임계 동작으로 fallback(backward-compat).

## §D — 보안 경계 (one-way door)

- `episodes/`·`procedures/`는 **repo 루트**(wiki/ 밖) → `okf_export.py`는 `wiki/`만 rglob 스캔하므로 **구조적으로 OKF에 안 보임**.
- **방어 이중망**: `schema/okf_export.yaml` `exclude_paths`에 `episodes/**`·`procedures/**` 명시(향후 wiki/ 밑 오배치 대비). 게이트는 탐지형이 아니라 규칙형이라 명시 규칙만이 누출을 막는다.
- 새 메모리 필드 → keep 모드 `x-llmbrain-*` / `--strip-internal` 전부 제거. **외부 공유는 strip 필수**.
- `.gitignore`: `episodes/` 전체. 예외 = `examples/episode-schema-example.jsonl` 1개만 커밋(문서·테스트용).
- 커밋 전 dry-run ceremony(기존)에 점검 항목 추가: export 목록에 `episodes`/`procedures` 미등장 확인.
