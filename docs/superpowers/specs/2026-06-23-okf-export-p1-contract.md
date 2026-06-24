# 인터페이스 계약 — okf_export.py (P1)

> 이 문서는 병렬 빌드 3개 에이전트(CODE·TESTS·SCHEMA)가 **공유하는 단일 진실**이다.
> 설계 배경은 같은 폴더의 `2026-06-23-okf-export-p1-design.md` 참조. 충돌 시 이 계약이 우선.

## 0. 공통 제약 (가드레일)

- `raw/`·`wiki/`는 **읽기 전용**. 출력은 `out_dir`(기본 `okf/`)에만.
- `scripts/export_graph.py`에서 **import만** 한다 — `parse_frontmatter`, `FRONTMATTER_RE`, `WIKILINK_RE`, `_unquote`. **export_graph.py 수정 금지.**
- Python 3.11+. `import yaml` (pyyaml 설치됨). frontmatter 출력은 `yaml.safe_dump(sort_keys=False, allow_unicode=True)`.
- 날짜는 `datetime.date.today().isoformat()` 사용 가능(일반 Python 스크립트).

## 1. 모듈 API (TESTS가 import)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ExportStats:
    pages_exported: int = 0
    links_converted: int = 0
    # ↓ R1~R3 audit으로 추가된 관측 필드(보안 게이트·진단성). 코드 dataclass가 정본.
    broken_links: list = field(default_factory=list)        # 진짜 ghost [(src_rel, target), ...]
    excluded_link_refs: list = field(default_factory=list)  # 제외 페이지 가리킨 링크(redact)
    excluded: list = field(default_factory=list)            # [rel_path, ...] (제외된 페이지)
    skipped: list = field(default_factory=list)             # [(rel, reason), ...] 로드실패·title부재
    sensitive_hits: list = field(default_factory=list)      # [(rel, pattern), ...] 본문 평문 민감정보
    by_dir: dict = field(default_factory=dict)              # {dir_name: count}

def export_bundle(
    wiki_dir: Path,
    out_dir: Path,
    *,
    strip_internal: bool = False,
    exclude_paths: list[str] | None = None,   # wiki_dir 기준 glob. falsy(None·[])면 기본 [business/**, canvas/**]
    exclude_domains: list[str] | None = None, # frontmatter domain 라벨 기준 보조 제외
    exclude_slugs: list[str] | None = None,   # 특정 slug 제외
    sensitive_patterns: list[str] | None = None,  # included 본문 평문 스캔 → sensitive_hits 표면화
    dry_run: bool = False,                    # True면 아무 파일도 안 쓰고 ExportStats만 반환
) -> ExportStats: ...

def load_config(path: Path | None) -> dict:
    """schema/okf_export.yaml 로드. path가 None/부재면 {} 반환 (하드코딩 기본값 사용)."""
```

## 2. CLI

```
python scripts/okf_export.py [--out okf/] [--strip-internal] [--config schema/okf_export.yaml]
    [--exclude-path GLOB ...] [--exclude-domain D ...] [--exclude-slug S ...] [--dry-run]
```

- 기본: `--out okf/`, `--config schema/okf_export.yaml`(있으면 로드), wiki_dir = 레포 루트 `wiki/`.
- 최종 exclude_paths = (config.exclude_paths 또는 기본 `[business/**, canvas/**]`) + CLI `--exclude-path`.
- 종료 시 1줄 통계: `pages=N links=M broken=K excluded=X` + 깨진 링크 목록 + by_dir.
- `--dry-run`: export될 출력 경로 목록 + 통계만 출력, **파일 0개 작성**. (커밋 전 보안 게이트용)

## 3. 페이지 로드 & slug→번들경로

- `wiki/**/*.md` 전부 로드. **제외**: 최상위 메타(`index.md`, `graph_report.md`, `distill_queue.md`, `curate_report.md`), `graph.json`, frontmatter에 `title` 없는 파일. (META_FILES는 export_graph의 집합 재사용 + `curate_report.md` 추가.)
- `rel` = wiki_dir 기준 상대경로(posix). 예: `concepts/rag.md`, `projects/260515_llm_wiki/prd.md`.
- `dir` = rel의 첫 파트(`concepts`).
- **번들경로(링크 타깃)** = `"/" + rel` (예: `/concepts/rag.md`). 파일도 `out_dir/rel`에 동일 미러.
- **slug 해석** (wikilink용): export_graph 방식 재사용 — slug = (rel 깊이>2면 `"/".join(parts[1:-1]+[stem])`, 아니면 `stem`). slug→번들경로 맵 구축. `[[X]]` 해석: ① X가 slug에 정확히 있으면 그것 → ② `"/"+X`로 끝나는 slug가 유일하면 그것(basename fallback) → ③ 없으면 **깨진 링크**.

## 4. frontmatter 출력 (순서 고정)

예약 필드(이 순서로, type·title 외엔 없으면 생략):
1. `type` (필수)
2. `title`
3. `description` — fm.description 있으면 그것; 없으면 추출(§6)
4. `resource` — fm에 `resource` 있을 때만
5. `tags` — 있을 때만
6. `timestamp` — fm.updated(없으면 fm.created); 둘 다 없으면 생략

그다음 `strip_internal=False`이면 **나머지 모든 fm 키**를 `x-llmbrain-{key}`로 보존:
- 규칙: `for k,v in fm: if k not in {type,title,description,resource,tags,updated}: emit "x-llmbrain-"+k = v`
- 즉 `domain→x-llmbrain-domain`, `created→x-llmbrain-created`, `distill_level→x-llmbrain-distill_level`, `access_count`, `last_accessed`, `last_distilled`, `resonance`, `sources` 등 전부.
- `strip_internal=True`면 예약 6필드만, x-llmbrain-* 전부 생략.

출력: `---\n` + `yaml.safe_dump(ordered_dict, sort_keys=False, allow_unicode=True)` + `---\n\n` + 변환된 본문.

## 5. 본문 출력

- 원본 frontmatter 제거, 본문 유지.
- wikilink 변환: `[[X]]` → `[X](/<rel>)`, `[[X|별칭]]` → `[별칭](/<rel>)` (rel = 해석된 페이지 번들경로).
- 깨진 링크: 텍스트만 남김(별칭 또는 X), `broken_links`에 `(src_rel, X)` 기록 + log.md 경고.
- 그 외 본문 변경 금지. 링크는 OKF 정규식 `\]\((/[^)]+\.md)\)`에 반드시 잡혀야 함.

## 6. description 규칙 기반 추출 (LLM 아님)

우선순위: ① fm.description → ② 본문 `## 핵심` 섹션 첫 문장 → ③ 본문 첫 문단(헤딩 제외) 첫 문장. wikilink·마크다운 마크업 제거, 1문장. 아무것도 없으면 빈 문자열.

## 7. 번들 파일

- `out_dir/<rel>` : 각 페이지 (frontmatter 변환 + 본문 변환).
- `out_dir/<dir>/index.md` : `# <dir>\n\n` + 각 페이지 `- [title](/<rel>) — description`.
- `out_dir/index.md` : `# OKF Bundle — llm-brain\n\n` + type별 섹션(`## <type>` + `- [title](/<rel>)`) + `## Directories` 섹션(각 dir index 링크).
- `out_dir/log.md` : `## <today> export\n` + pages·links converted·broken·excluded·strip_internal 통계 + 깨진 링크 목록.

## 8. 테스트 (TESTS 에이전트)

- **픽스처**: `tests/fixtures/okf_wiki/` — 실 wiki/ 아님. 약 6페이지를 `concepts/`·`tools/`·`people/`·`business/`(제외 검증용 1페이지)에 분산. 포함: 일반 wikilink, 별칭 wikilink, 깨진 wikilink, fm.description 있는 페이지, 없는 페이지(추출 검증), 내부필드(distill_level 등) 있는 페이지.
- `tests/test_okf_export.py`: frontmatter 매핑(updated→timestamp, 내부→x-llmbrain-*, strip 모드), wikilink 변환(일반·별칭·깨진→텍스트+log), exclude(business 페이지 출력 부재 + stats.excluded 포함), description 추출(## 핵심 + 첫 문단 fallback), index/log 생성, 디렉토리 미러. **out은 tmp_path. `requires_user_wiki` 마커 금지**(픽스처 기반이라 항상 실행).
- `tests/test_okf_roundtrip.py`: minimal consumer(design.md 부록) 내장 → 픽스처 export → load_bundle → 노드 수 = export 페이지 수, 엣지 = 의도된(안 깨진) wikilink 수, 깨진 링크 제외.
- **scripts/ import 방식은 기존 `tests/test_export_graph.py`의 패턴을 따른다**(읽고 동일하게).

## 9. 스키마 (SCHEMA 에이전트)

- `schema/okf_export.yaml`: `exclude_paths: [business/**, canvas/**]`, `exclude_domains: []`, `exclude_slugs: []` + 주석.
- `schema/okf.md`: OKF↔llm-brain 매핑 문서(필드 대응표, x-llmbrain 네임스페이스 근거, 정규식 계약, 링크 변환 규칙). design.md §5 기반.
