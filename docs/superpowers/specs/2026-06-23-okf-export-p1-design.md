# OKF Export 포트 (Phase 1) — 설계 문서

> **상태**: 설계 확정 대기 (사용자 리뷰 중) · **작성일**: 2026-06-23 · **범위**: Phase 1만
> **출처 PRD**: `~/Desktop/prd-okf-integration.md` (전략·스펙 원본)
> **이 문서의 역할**: PRD를 *실제 레포 상태와 정합*시키고 **Phase 1(Export)로 범위를 좁힌** 착수 가능 설계. PRD의 미검증 가정 5건을 교정한 버전.

---

## 0. 한 문장

OKF를 경쟁 포맷이 아니라 llm-brain의 **export 포트**로 흡수한다. `wiki/`(내부 슈퍼셋)를 OKF v0.1 호환 번들 `okf/`로 투영하고, 그 번들이 Google minimal consumer로 그래프 복원되면 성공. **내부 포맷은 바꾸지 않는다 — 경계에서만 변환.**

## 1. 범위 결정 (왜 P1만인가)

PRD §10의 가치 우선순위는 `P1 Export → 과제 A(self-improving distill) → 과제 C(계보) → 나머지`다. **import(P2)는 PRD의 top 우선순위에 없다.** 따라서:

- **이번 범위**: Phase 1 (Export 포트)만.
- **P2 (Import)**: 외부 OKF 번들 수요가 실제로 생기면 별도 spec. (현재 수요 0 → speculative 회피)
- **P3 (distill 루프)**: "별 트랙" — 경계 작업이 아니라 생애주기 작업이라 자체 PRD 필요.

근거: 비가역 작업(public 커밋)을 격리 검증하고, 다음 베팅은 P1 운영 증거를 보고 결정한다.

## 2. 레포 정합 — PRD 가정 교정 5건 (실측 완료)

| # | PRD 가정 | 레포 현실 (실측) | 교정 |
|---|---|---|---|
| 1 | `render.py`·`pages.py` 재사용 | **부재** | `scripts/export_graph.py`의 `parse_frontmatter()`·`FRONTMATTER_RE`·`WIKILINK_RE`를 import. export_graph는 **수정 없음** |
| 2 | wikilink "변환기" | export_graph는 wikilink **추출만**, 변환 없음 | slug→`/{dir}/{slug}.md` 경로 변환 + 마크다운 링크 생성이 **net-new 핵심 로직** |
| 3 | frontmatter 재사용 | export_graph는 읽기만(PyYAML 회피) | okf_export는 frontmatter를 **써야** 함. `pyyaml==6.0.3` 이미 설치됨 → `yaml.safe_dump` 사용 |
| 4 | `--exclude-domain business` | `domains.yaml`에 `business` 도메인 **없음**. `wiki/business/` 디렉토리는 실재(페이지 4개) | **경로 글롭 필터**(`business/**`). 인자 `--exclude-path`, PRD 호환 위해 `--exclude-domain` alias |
| 5 | description "자동 생성" | — | **규칙 기반 추출**(본문 첫 문단 또는 `## 핵심`). LLM 호출 아님 = 결정적 변환 (Rule 5) |

실측 추가 사실: `wiki/` 실제 도메인 디렉토리 = `archive, business, canvas, concepts, insights, lecture, papers, people, projects, tools`. domains.yaml에 없는 `papers/`·`people/`·`archive/`도 존재 → export는 **실제 디렉토리를 미러**한다(domains.yaml에 의존하지 않음).

## 3. 아키텍처 (Export 포트만)

```
wiki/ (내부, 슈퍼셋 frontmatter, .gitignore 유지)
  │
  └─[okf_export.py]─▶ okf/ (OKF v0.1 투영본, Git 커밋, 변환된 링크)
                       └─▶ 동료·외부 에이전트·habix 제품이 번역 없이 소비
```

- **wiki/** = 풍부한 내부 표현 (생애주기 필드 포함). 읽기 전용. 계속 gitignore.
- **okf/** = wiki/의 OKF 투영. 커밋 가능. business/ 등 민감 경로 제외.

## 4. 모듈/파일 계획

| 파일 | 동작 | 비고 |
|---|---|---|
| `scripts/okf_export.py` | **신규** | P1 핵심 |
| `scripts/export_graph.py` | **수정 없음** | 파서 함수 import 소스로만 |
| `schema/okf_export.yaml` | **신규** | `exclude_paths`·OKF 매핑 규칙 (옵션 B 설정) |
| `schema/okf.md` | **신규** | OKF↔llm-brain 매핑 문서 |
| `tests/test_okf_export.py` | **신규** | 매핑·링크변환·strip/keep·exclude |
| `tests/test_okf_roundtrip.py` | **신규** | §11 minimal consumer 라운드트립 |
| `.gitignore` | **조건부 수정** | 현재 `okf/`를 거르는 패턴 없음 → okf/는 *이미 커밋 가능*. 방어용 `!okf/` 명시는 선택(미래 광범위 패턴 차단). wiki/·raw/·express/는 계속 무시 |

**가드레일**: `raw/`·`wiki/` 읽기 전용. 출력은 `okf/`에만. export_graph·기존 테스트 회귀 0.

## 5. 상세 스펙

### 5.1 frontmatter OKF 매핑

OKF 예약 필드(`type`은 필수, 나머지 선택)로 매핑:

| OKF 필드 | 소스 | 규칙 |
|---|---|---|
| `type` | wiki `type` | 그대로 (OKF type은 자유값 → 합법) |
| `title` | wiki `title` | 그대로 |
| `description` | wiki `description` 없으면 본문 | 규칙 기반 추출 (§5.4) |
| `resource` | wiki `resource` (있을 때만) | 그대로 |
| `tags` | wiki `tags` | 그대로 |
| `timestamp` | wiki `updated` | `updated → timestamp` 매핑 |
| `x-llmbrain-*` | `domain`·`distill_level`·`access_count`·`resonance`·`sources` 등 | 기본 보존. `--strip-internal`이면 제거 |

내부 필드를 `x-llmbrain-` 네임스페이스로 보존하는 이유: 자기참조·디버깅 유리, OKF는 type만 필수라 추가 필드 합법.

### 5.2 wikilink → OKF 링크 변환 (핵심)

| 입력 (wiki/) | 출력 (okf/) |
|---|---|
| `[[rag-patterns]]` | `[rag-patterns](/concepts/rag-patterns.md)` |
| `[[rag-patterns\|RAG 패턴]]` | `[RAG 패턴](/concepts/rag-patterns.md)` |
| slug→경로 해석 | 페이지 로드 단계에서 **slug→번들경로 맵** 구축. export_graph의 basename fallback 방식 재사용 |
| 깨진 링크 (대상 없음) | 텍스트만 남기고 링크 해제 + `okf/log.md`에 경고 |

경로는 **번들 루트 기준 절대경로**(`/concepts/...`) — OKF consumer 정규식 `\]\((/[^)]+\.md)\)` 요구사항.

### 5.3 exclude 필터 (옵션 B — 경로 글롭)

`schema/okf_export.yaml`:
```yaml
exclude_paths:
  - "business/**"   # 민감 비즈니스 정보 (페이지 4개)
  - "canvas/**"     # gitignore 대상 canvas 데이터
# exclude_domains: []   # (선택) frontmatter domain 라벨 기준 보조 필터
# exclude_slugs: []     # (선택) 특정 페이지 명시 제외
```

- 1차 필터 = 경로 글롭. 구조적 보장(분류기 오탐 여지 없음).
- 설정 파일화 → 제외가 *추론*이 아니라 *감사 가능*.

### 5.4 description 규칙 기반 추출 (LLM 아님)

우선순위: ① frontmatter `description` 존재 시 그대로 → ② 본문 `## 핵심` 섹션 첫 문장 → ③ 본문 첫 문단 첫 문장. wikilink·마크다운 마크업 제거 후 1문장. **결정적 변환이므로 코드 처리(Rule 5).**

### 5.5 번들 출력 구조

```
okf/
├── index.md            # 번들 루트 목차 (type별 그룹 + 디렉토리 index 링크)
├── log.md              # export 이력 + 변환 경고
├── concepts/
│   ├── index.md        # 디렉토리별 점진적 공개
│   └── rag-patterns.md # 변환된 frontmatter + 링크
├── tools/ · insights/ · lecture/ · projects/ · papers/ · people/ · archive/
└── ...                 # (business/·canvas/ 제외)
```

각 파일: OKF 예약 6필드 + `x-llmbrain-*`(옵션) + 변환된 본문.

### 5.6 `scripts/okf_export.py` CLI

```
uv run python scripts/okf_export.py [--out okf/] [--strip-internal] \
    [--exclude-path GLOB ...] [--dry-run]
```

| 인자 | 기본 | 동작 |
|---|---|---|
| `--out PATH` | `okf/` | 출력 번들 루트 |
| `--strip-internal` | off (=keep) | OKF 예약 6필드만 남김 (외부 공유 최소본) |
| `--exclude-path GLOB` | `schema/okf_export.yaml` 값 | 추가 제외 경로 (복수) |
| `--exclude-domain D` | — | (alias, 보조) domain 라벨 기준 제외 |
| `--dry-run` | off | **파일 안 쓰고** export 대상 목록·통계만 출력 (보안 게이트용) |

처리 단계:
1. wiki/ 전 페이지 로드 → slug→번들경로 맵 구축 (export_graph 파서 재사용)
2. exclude_paths 매칭 제외
3. frontmatter OKF 매핑 (§5.1)
4. 본문 wikilink 변환 (§5.2), 깨진 링크 log 기록
5. `okf/{dir}/{slug}.md` 기록 + 디렉토리별 index.md
6. `okf/index.md` + `okf/log.md` 생성
7. 통계 출력: 페이지 N, 링크변환 M, 깨진링크 K, 제외 X

## 6. 수락 기준 (DoD) — 도구 신호 아닌 실제 관측

1. `uv run python scripts/okf_export.py` → `okf/` 생성 성공
2. **라운드트립**: §11 Google minimal consumer로 `okf/` 로드 → 노드 수 = export 페이지 수, 엣지 = 의도된 wikilink 수, 깨진 링크는 log에만 (그래프 제외)
3. `pytest` 전체 통과 (신규 + 기존 회귀 0)
4. **🔴 public 커밋 전 보안 게이트**: `--dry-run`으로 export 대상 목록을 사람이 눈으로 확인 → `business/` 4개 페이지 누락 0 확인 후에만 커밋. (one-way door 방어 — git history는 영구)

## 7. 테스트 계획

- `tests/test_okf_export.py`: frontmatter 매핑, wikilink 변환(파이프 별칭·깨진 링크), exclude 경로 필터, strip/keep, description 추출, 디렉토리 미러, index/log 생성. **픽스처 wiki/ 사용 — 실제 wiki/ 안 건드림.**
- `tests/test_okf_roundtrip.py`: 픽스처 5페이지(wikilink 포함) → export → minimal consumer 복원 검증.
- 기존 테스트(`test_export_graph.py`·`test_curate_frontmatter.py`·wiki_app 계열) 회귀 0.

## 8. 리스크 / 열린 항목

| 리스크 | 완화 |
|---|---|
| `wiki/business/` 4페이지가 실제로 민감 정보 전부를 담는지 미확인 (다른 폴더에 산재 가능) | `--dry-run` 게이트 + 필요 시 `exclude_slugs` 추가 |
| `archive/` 도메인 export 여부 미결 | 기본 포함. dry-run에서 사람 판단 |
| okf/ drift (wiki/ 갱신 후 재export 안 하면 stale) | P1 범위 밖 — 운영 트리거는 후속(cron). 본 spec은 수동 export 전제 |

## 9. 명시적 비범위 (이번 작업 아님)

- P2 Import 포트 (`okf_import.py`, `raw/okf/`)
- P3 self-improving distill 루프 (과제 A)
- okf/ 자동 재export cron
- 내부 wiki/ 포맷 변경 (OKF로 교체 금지)
- OKF public 웹 게시 (llms.txt 디스커버리)

## 부록 — OKF minimal consumer (검증 기준, Google 공개판)

```python
import pathlib, re, yaml

def load_bundle(root):
    concepts, links = {}, []
    for path in pathlib.Path(root).rglob("*.md"):
        text = path.read_text()
        meta = {}
        if text.startswith("---"):
            _, fm, body = text.split("---", 2)
            meta = yaml.safe_load(fm) or {}
        else:
            body = text
        concepts[str(path)] = meta
        for target in set(re.findall(r"\]\((/[^)]+\.md)\)", body)):
            links.append((str(path), target))
    return concepts, links
```

정규식 `\]\((/[^)]+\.md)\)`이 **호환성의 단일 진실**. export 본문은 반드시 이 패턴에 잡히는 링크를 만든다.
