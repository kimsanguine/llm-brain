---
description: llm-brain 설치 상태 진단·수정 (디렉토리·스크립트·커맨드·설정·의존성 점검, --fix로 안전 복구)
---

llm-brain의 doctor 커맨드입니다. 설치가 제대로 됐는지 진단하고, `--fix`로 안전하게 복구합니다.
`$ARGUMENTS`에 따라 아래를 실행하세요.

## 인자

- 인자 없음 → **진단만** (점검 결과 출력, 파일 변경 0)
- `--fix` → 안전 복구: 누락 디렉토리 생성 + `schema/sources.yaml`이 없으면 `sources.example.yaml`에서 복사. **기존 파일은 절대 덮어쓰지 않음.**

## 실행

```bash
cd "$(git rev-parse --show-toplevel)"  # llm-brain 레포 루트
uv run python scripts/doctor.py $ARGUMENTS
```

(uv 미설치 시: `.venv/bin/python scripts/doctor.py $ARGUMENTS`)

## 점검 항목

- **필수 디렉토리**: `raw/`(7 하위 채널)·`wiki/`·`schema/`·`scripts/`·`commands/`·`procedures/`·`examples/`
- **스크립트(메모리 OS 포함)**: ingest·curate·express·okf_export·export_graph·sync_raw + **episode·brain_context·memory_health·procedures·lib/frontmatter_utils**
- **커맨드**: ingest·curate·express·query·okf·doctor·wikiweb
- **설정**: `schema/config.yaml`(LLM 엔진)·`schema/sources.yaml`(소스 — gitignored, 없으면 WARN)
- **의존성**: pyyaml·fastapi·uvicorn·httpx·python-frontmatter (`uv sync`로 설치)
- **claude CLI**: cli 엔진(기본) 사용 시 필요 (없으면 WARN)

## 결과 해석

- ❌ **FAIL** = 설치 문제 → 해결 필요(디렉토리는 `doctor --fix`, 의존성은 `uv sync`, 스크립트/커맨드 누락은 플러그인 재설치·`git pull`).
- ⚠️ **WARN** = 선택/환경별(설정 파일·claude CLI 등) — 필요 시 안내대로.
- exit 0 = FAIL 없음(설치 정상) · exit 1 = FAIL 있음.

> 새 클론/설치 직후 `doctor --fix` 한 번이면 디렉토리·소스 설정이 정비됩니다. 의존성은 그 전에 `uv sync`.
