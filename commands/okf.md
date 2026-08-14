---
description: wiki → OKF v0.1 호환 번들 export (Google Open Knowledge Format 표준). 보안 게이트 내장
---

llm-brain의 okf 커맨드입니다. `wiki/`(내부 슈퍼셋)를 OKF v0.1 호환 번들 `okf/`로
투영해, 동료·외부 에이전트·habix 제품이 번역 없이 소비할 수 있는 표준 포맷으로 내보냅니다.
`$ARGUMENTS`에 따라 아래를 실행하세요.

## 인자 파싱

- `--dry-run` → 파일 미작성, export 대상·제외·통계만 출력 (보안 검토용)
- `--strip-internal` → OKF 예약 6필드만 (x-llmbrain-* 제거, 외부 공유 최소본)
- `--exclude-slug <slug>` → 특정 페이지 추가 제외 (복수 가능)
- `--out <경로>` → 출력 번들 루트 (기본 `okf/`)
- 인자 없음 → 기본 export (`okf/` 생성)

## 🔴 Step 0: 보안 사전 점검 (커밋 전 one-way door — 반드시)

`okf/`는 Git 커밋 대상이고 push되면 history가 영구다(비가역). 민감정보 누출을 막는다:

1. **`schema/okf_export.local.yaml`(gitignored) 존재 확인.** 민감 키워드(`sensitive_patterns`)·
   제외 페이지(`exclude_slugs`)는 **반드시 이 로컬 파일에만** 둔다. 커밋되는 `schema/okf_export.yaml`엔
   실명·내부명을 절대 넣지 않는다(그 자체가 누출).
2. 이 파일이 **없으면**(fresh clone/CI) 게이트가 비활성이라 이전에 제외한 민감 페이지가 다시
   included된다 — 실행 시 스크립트가 stderr에 🔴 경고를 낸다. 그 상태로는 커밋 금지.

## Step 1: dry-run으로 먼저 검토 (`--dry-run`이 없어도 실 export 전에 1회 권장)

```bash
cd "$(git rev-parse --show-toplevel)"  # llm-brain 레포 루트
uv run python scripts/okf_export.py --dry-run $ARGUMENTS
```

출력에서 사람이 **직접 확인**:
- `business 제외 4건`이 목록에 있는가
- `sensitive_hits=0` 인가 (본문 평문 민감정보 후보 0)
- `excluded` 카운트 = business 4 + 민감 slug 수 (기대값과 일치 — local.yaml 부재면 `pages`가 늘고
  민감 페이지가 included로 조용히 섞이니 카운트 대조 필수)

누출 후보가 보이면: 해당 페이지 slug를 `schema/okf_export.local.yaml`의 `exclude_slugs`에 추가하고
dry-run을 다시 돌려 `sensitive_hits=0`으로 수렴시킨다.

## Step 2: 실제 export (Step 1 검토 통과 시에만)

```bash
cd "$(git rev-parse --show-toplevel)"  # llm-brain 레포 루트
uv run python scripts/okf_export.py $ARGUMENTS
```

`okf/{dir}/{slug}.md` + 디렉토리별 `index.md` + 루트 `index.md` + `log.md` 생성.
변환 규칙: `schema/okf.md` (frontmatter 매핑·정규식 계약). 제외 설정: `schema/okf_export.yaml`.

## Step 3: 결과 요약 (한국어)

- pages / links / ghost / excl_refs / excluded / sensitive_hits 통계
- round-trip 무결성(원하면 `okf/`에 design.md §11 minimal consumer 적용해 dangling 0 확인)
- 커밋하려면: `okf/` 파일만 stage(기존 미커밋 보존), push는 public 노출이라 사람 승인 후

## 가드레일
- `raw/`·`wiki/` 읽기 전용. 출력은 `okf/`에만.
- 내부 포맷을 OKF로 교체하지 않는다 — OKF는 경계(포트)에서만.
- 상세: `SPEC.md` (인터페이스와 공개 보안 게이트).
