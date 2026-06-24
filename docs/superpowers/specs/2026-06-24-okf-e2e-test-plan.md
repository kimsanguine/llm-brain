# OKF Export E2E 테스트 계획 (멀티에이전트 설계)

> 4개 에이전트(CLI/운영·consumer interop·보안경계·fresh-clone/회귀)가 **실제 명령을 돌려보며** 설계한 통합 E2E 계획. 단위 테스트 176개(함수 단위)가 못 보는 **프로세스 경계·통합 시나리오**를 다룬다.
> 작성: 2026-06-24 · 대상: scripts/okf_export.py (Phase 1, 커밋 `30dc2f3`)

## 0. 철학
E2E = **명령 실행 → 실제 산출물(okf/) → 관측**(exit code·파일·stdout 통계·log.md·외부 consumer). `export_bundle()` 직접 호출이 아니라, CLI를 `subprocess`로 구동해 argparse·경로해석·config+local 병합까지 전 경로를 탄다. 검증 2모드: **픽스처 미니레포**(결정적·항상 실행) + **실 okf/ 번들**(존재 시, drift 내성 임계 assert).

## 1. 설계 중 발견한 실제 갭 (단위테스트가 못 잡음 — 우선 처리 대상)

| ID | 심각도 | 발견 | 내용 | 수정 방향 |
|---|---|---|---|---|
| **GAP-1** | 🔴 P0 | C(SEC-11)+D(REG-02) **독립 2회** | fresh clone/CI/협업자엔 gitignored `okf_export.local.yaml`이 없어 `sensitive_patterns=[]`·`exclude_slugs=[]` → 게이트 **침묵 비활성**(민감 9페이지 재포함 84→93), **경고 없음** | `sensitive_patterns` 비고 + `.local.yaml` 부재 + non-dry-run이면 stderr 🔴 경고 + 커밋 자제 안내 |
| **GAP-2** | 🔴 P0 | A(E2E-19) | symlink 거부 가드가 dead code — `out_dir.resolve()`가 symlink를 먼저 해소해 `is_symlink()`가 항상 False. `--out &lt;symlink&gt;`가 거부 안 됨(exit 0) | resolve **전** 원본 인자로 `Path(arg).is_symlink()` 검사 |
| **GAP-3** | 🟡 P1 | A(E2E-10) | `--config custom.yaml` 시 local은 `custom.local.yaml`을 찾아 기본 `okf_export.local.yaml` **silent 무시** → 민감설정 우회 | 기본 `okf_export.local.yaml`도 항상 병합, 또는 문서 경고 |
| **GAP-4** | ℹ️ 한계 | D(REG-02) | 본문 산문의 내부 경로·식별자(`raw/`·`wiki/`·실명) 평문은 어느 자동 방어선도 못 막음 — `sensitive_patterns` 등록에만 의존 | 한계로 문서화 + 커밋 okf/ 본문을 내부식별자 사전으로 grep하는 CI 게이트 권고 |

## 2. 통합 시나리오 (53개, 6 스위트)

### Suite A — CLI 플래그 (P0×4, P1×7)
default 산출물·구조 / `--dry-run` 파일0 / **dry-run↔real 통계 문자열 일치** / `--strip-internal` x-llmbrain 0 / `--out` 라우팅 / `--exclude-path|domain|slug` 누적 / `--config` + 부재 fallback / **`.local.yaml` 자동병합**(GAP-3 회귀 포함) / 복합 플래그.

### Suite B — Idempotency·Drift (P0×3, P1×1)
2회 export `diff -r` 완전 동일 / wiki 변경 재export 반영 / 삭제 페이지 stale 정리 / 센티넬 디렉토리만 rmtree.

### Suite C — 안전 가드 (P0×4)
`--out .` 거부(조상) / `--out wiki` 거부(소스) / 비-센티넬 비어있지 않은 디렉토리 거부 / **symlink out_dir 거부(GAP-2 — 현재 xfail→수정 후 pass)**.

### Suite D — Consumer Interop (P0×5, P1×4, P2×1)
§11 minimal consumer 전페이지 파싱 / 콘텐츠 노드 type 100% / dangling 0 / 제외·깨진 링크 본문 누출 0 / networkx 그래프 복원+type별 목록 / 이웃 질의 / 허브(in-degree) / 단일 연결체 / **strict json.dumps 전페이지(date 회귀 가드)** / round-trip 동등 / 루트→dir→page 3-hop 항행 / **description 79/91 갭(임계 회귀 가드)** / 본문 절대경로 링크.

### Suite E — 보안 경계 (P0×10, P1×2)
business default 부재 / 빈 리스트 우회 차단 / 중첩·대소문자 제외 / 재export business=0 / **sensitive_hits 전수 표면화(truncation은 CLI print만)** / 게이트 반영 후 0 수렴 / 본문vs frontmatter 스캔 경계 / 별칭 redact / sources raw/ strip / strip-internal 전제거 / **local.yaml gitignored + fresh-clone 게이트 비활성(GAP-1)** / public 라이브 관측(이미 GitHub 검증: business 404·제외 13 부재).

### Suite F — Fresh-clone·환경·회귀 (P0×4, P1×2, P2×1)
fresh clone consumer 자급(1074링크 깨짐0) / wiki 부재 재export fail-safe(exit1·번들무손상) / conftest 마커 선택skip(170 passed/6 skipped) / uv.lock 없이 의존성 resolve / Python≥3.11 하한 / CLAUDE.md 명령 정합 / **본문 평문 누출 통합 게이트(GAP-1·GAP-4)**.

## 3. 자동화 구현
- **신규** `tests/test_okf_e2e.py`: subprocess 미니레포(`main()` wiki_dir 하드코딩 우회) + 실 okf/ 임계 assert. networkx를 dev 의존성 추가.
- **수정자≠검증자**: consumer 검증 코드는 okf_export.py와 import 공유 없이 독립 작성(export 버그가 검증 버그로 안 가려지게).
- **CI 게이트**: 커밋 전 `--dry-run` sensitive_hits≠0이면 차단(GAP-1 enforcement) + okf/ 본문 내부식별자 사전 grep.

## 4. 이미 실측 확인된 정상 동작 (4 에이전트 PROBE)
business 전모드 제외 / 빈 리스트 fail-safe / 중첩·대소문자 / sensitive 전수 표면화 / redact / sources strip / idempotency 완전동일 / dry-run↔real 일치 / drift·stale 정리 / fresh-clone exit1·번들무손상 / 1074링크 깨짐0 / json.dumps 84/84 / 단일 연결그래프 / 마커 선택skip / public GitHub business 404.
