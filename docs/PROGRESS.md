# PROGRESS — llm-brain × OKF 통합 (Phase 1)

> 이 문서는 **진행 현황 + Decision Log**의 단일 확인처다. 주요 변경은 반드시 여기에 기록한다.
> 출처 PRD: `~/Desktop/prd-okf-integration.md` · 설계: `docs/superpowers/specs/2026-06-23-okf-export-p1-design.md` · 계약: `...-contract.md`
> 최종 갱신: 2026-06-23

---

## 주요 변경(major change)의 기준 — `~/.claude/CLAUDE.md` 근거

아래 중 **하나라도** 해당하면 "주요 변경"이며 Decision Log에 기입한다. (단순 포매팅·인접 리팩터·오타는 Rule 3 'Surgical'에 따라 제외.)

| 기준 | 근거 룰 | 예 |
|---|---|---|
| 비가역(one-way door) 작업 | **Rule 9** | public 커밋·삭제·배포·DB 스키마·가격·고객 약속 |
| 새 모듈·인터페이스·아키텍처 변경 (스코프 영향) | **Rule 2·3** | `okf_export.py` 신설, CLI 계약, 의존 추가 |
| 보안·안전성 경로 변경 | **Rule 8** | 누출 차단, 데이터 손실 가드 |
| 사람이 쥐는 결정 (되돌리기 어려움·제품 판단) | **Rule 5·9** | 범위 결정, exclude 정책, 공개 범위 |
| 테스트 계약 변경 | **Rule 6** | 신규 테스트 스위트, DoD 변경 |
| 누적 결정 자체 | **Rule 7** | 이 로그 운영 |

---

## 현재 체크포인트 (2026-06-23)

- **상태**: Phase 1(OKF Export) 구현 + 보안 강화 + **Ralph loop 3라운드 수렴 완료(critical/major 0)**.
- **테스트**: `pytest` 전체 **195 통과**(OKF 단위 54 + E2E 19). 7종(+ test_okf_e2e.py: subprocess CLI·consumer·보안·fresh-clone).
- **검증**: 실 92페이지 round-trip dangling=0·business=0·깨진 키 0·json.dumps 92/92. dry-run: ghost=5 / excl_refs=85 / excluded=4 / skipped=1.
- **Ralph loop 수렴 곡선**: R1 critical 2+major 6 → R2 major 2(R1 수정의 회귀/미완) → R3 major 1(Codex 코드펜스) → **수렴**. 6 렌즈(P1~P5+Codex) 전부 "새 critical/major 0".
- **🔴 보류(승인 대기)**: **public 커밋은 비가역(Rule 9)이라 자동 실행 안 함.** 커밋 전 GO 조건(P3) ↓.

### public 커밋 GO 조건 (P3 보안 검토 — 충족 후에만 커밋)
1. `schema/okf_export.yaml`의 `sensitive_patterns`를 본인 운영 키워드(실명·EchoMate·StockPulse·context-dealer 등)로 채운다. *(주의: 이 파일은 커밋되므로 실명을 넣기 싫으면 gitignored 로컬 설정 분리 권장.)*
2. `uv run python scripts/okf_export.py --dry-run` 실행 → 출력의 `business 제외 4건`·`sensitive_hits`를 사람이 눈으로 검토.
3. 누출 0 확인 후에만 `okf/` 생성 + 커밋.

---

## Decision Log

> 형식: `[날짜] 결정/변경 — 근거(룰) · 가역성 · 검증`

- **[2026-06-23] OKF exclude 메커니즘 = 경로 글롭(옵션 B), 도메인 라벨 아님** — Rule 1·5. `domains.yaml`에 `business` 도메인 부재 + `habix`가 business/+projects/ 묶음이라, 도메인 기준은 과잉/과소 제외. 경로 `business/**` 글롭 + `schema/okf_export.yaml` 명시 설정 채택. 가역(설정 변경). 검증: 사용자 승인 + business 4페이지 제외 실측.
- **[2026-06-23] 범위 = Phase 1(Export)만. P2(Import)·P3(distill) 미착수** — Rule 5. PRD §10 가치 우선순위가 import를 top에서 제외 + 수요 0(speculative 회피, Rule 2). 가역(후속 트랙). 검증: 사용자 선택(안 A).
- **[2026-06-23] 병렬 빌드 = 계약 고정 후 3에이전트(CODE/TESTS/SCHEMA) 파일 소유권 분리** — Rule 4·9. worktree 대신 공유트리(파일 디렉토리 분리로 충돌 0, wiki/ gitignore 트랩 회피). 가역. 검증: 충돌 0, 통합 pytest 통과.
- **[2026-06-23] 신규 모듈 `scripts/okf_export.py` + `schema/okf_export.yaml`·`okf.md`** — Rule 2·3. export_graph.py는 import만(수정 0). 가역. 검증: syntax+pytest.
- **[2026-06-23] 버그수정: description 추출이 마크다운 표/`---`를 frontmatter에 주입 → OKF consumer 파싱 크래시** — Rule 8(consumer 호환=기능 본질). 표·수평선 스킵 + `_sanitize_fm_value` `---` 제거 2층 방어. 가역. 검증: 실 92페이지 round-trip + 회귀 테스트 `test_okf_frontmatter_safety.py`.
- **[2026-06-23] 보안수정 6건(B1 중첩 글롭·B2 대소문자·B3 별칭 redact·Y1 ghost/excl 분류·Y2 dict 재귀·Y4 stale 정리)** — Rule 8·9(public 누출=one-way door). 적대검증(silent-failure-hunter) 발견. 가역. 검증: `test_okf_security.py` 7종 + 실데이터 round-trip business=0.
- **[2026-06-23] Y4 자체회귀 수정: rmtree 판별을 `index.md` OR → `.okf-bundle` 센티넬 + 소스/조상경로 거부** — Rule 8·9. 직전 Y4 수정이 `--out .`로 레포 전체 삭제 가능한 비가역 경로 도입 → fix-round 재검증이 포착. 가역. 검증: `--out .` 거부 실증(레포 index.md 보존) + 회귀 테스트.
- **[2026-06-23] public 커밋 보류 — 승인 게이트 유지** — Rule 9. 비가역. 검증 대기.
- **[2026-06-23·R1] frontmatter 파싱 PyYAML 전환(읽기)** — Rule 8(데이터 무결). export_graph 미니파서가 들여쓰기 블록 리스트를 손상(sources/domain 소실 + `x-llmbrain-- https` 깨진 키 public 출력, P2 발견) → okf_export 읽기를 yaml.safe_load + 미니파서 fallback. export_graph 미수정. 가역. 검증: 실 92페이지 깨진 키 0, voice-ai-stack sources 복원 + `test_okf_audit_fixes.py`.
- **[2026-06-23·R1] exclude 빈 리스트([]) 우회 차단** — Rule 8·9(public 누출). `if exclude_paths is None`→`if not exclude_paths`. `exclude_paths=[]` 직접 호출이 business 제외를 통째로 우회하던 critical(P3). 가역. 검증: 빈 리스트 호출 시 business 제외 실증.
- **[2026-06-23·R1] dry-run 보안 게이트 강화 — 본문 평문 스캐너 + sources raw/ strip** — Rule 8(fail-loud)·9. 페이지 제외는 business *파일*만 막고 included 본문 평문(실명·운영수치)은 무방비(P3). `sensitive_patterns`(schema 설정) 스캔→dry-run/log 표면화 + x-llmbrain-sources의 내부 raw/ 경로 제거(구조 유출 차단). 가역. 검증: 회귀 테스트 + 실데이터 raw/ 0.
- **[2026-06-23·R1] description 추출 견고화 + 루트 index description** — Rule 2(품질). 약어/이니셜 오절단('Carlos E.')·ASCII 다이어그램·버전 문자열을 description으로 승격하던 결함(P1) → 약어 인식·다이어그램/bullet 스킵·품질 미달 시 빈값 + 루트 index.md에 description 부착. 가역. 검증: 회귀 테스트 + 실데이터.
- **[2026-06-23·R1] README/SPEC/CLAUDE.md OKF 문서화** — Rule 2·9. 루트 문서에 OKF export 언급 0건→기능 디스커버리 불가(P4 critical) + drift 트리거·커밋 전 dry-run 게이트 명문화(P5). 가역. 검증: 3파일 grep + CLI 인자 코드 대조.
- **[2026-06-23·R3] date→ISO 문자열 직렬화** — Rule 8(데이터 무결, R1 회귀 수정). R1 PyYAML 전환이 `updated`를 datetime.date로 만들어 머신 소비자 json.dumps 92/92 실패(P2 R2 발견). `_sanitize_fm_value`에 date/datetime→isoformat. okf.md의 string 가정과 정합. 가역. 검증: 실 92페이지 json.dumps 92/0 + 회귀 테스트.
- **[2026-06-23·R3] description 추출 클래스 완성(번호목록·코드펜스 다이어그램·수식·라벨)** — Rule 2(품질, R1 부분수정 보완). R1이 약어만 고쳐 번호목록('1...2.' 잘림)·코드펜스 다이어그램·수식이 잔존(P1 R2 발견). 번호목록/수식/화살표 스킵 + 코드펜스 제거 + 콜론라벨/초단문 빈값화. 가역. 검증: 실데이터 4케이스 정상화 + 회귀 테스트.
- **[2026-06-23·R3] `_strip_code_fences` 라인 앵커 regex 교정** — Rule 2(견고성). R3에서 새로 만든 helper의 `` ```.*?``` ``가 인라인/중첩 삼중백틱에서 내부 잔류(Codex R3 [major]). `(?ms)^```...\n...\n```$` 라인 앵커로 well-formed 블록만 제거. 가역. 검증: Codex reproducer 잔류 0 + 정상 펜스 제거 + 회귀 테스트.
- **[2026-06-23·R3] Ralph loop 수렴 선언** — Rule 7. 6 렌즈 전부 새 critical/major 0. 잔여는 minor만(아래). 비가역 커밋은 GO 조건 충족 후 사람 승인.
- **[2026-06-24] GO 조건 충족 + 로컬 커밋** — Rule 9. dry-run 보안 게이트로 본문 평문 민감정보 검토 → 사용자 결정 "전부 제외"로 9페이지(이든·EchoMate) `exclude_slugs`(로컬) 추가, sensitive_hits 0 수렴. okf/ 84페이지 생성(business 4 + 민감 9 제외). 브랜치 `feat/okf-export-p1`에 커밋 `88f8fa4`(OKF 파일만, 기존 미커밋 index.md·log.md·examples 보존, 로컬 민감설정 gitignored). **push(public 노출)는 보류 — 별도 승인.**
- **[2026-06-24] 로컬 오버라이드 메커니즘** — Rule 8(privacy). `schema/okf_export.local.yaml`(gitignored)로 민감 키워드·exclude_slug 분리. 커밋 설정 파일에 실명 유입 방지. main()이 config + .local.yaml 병합.
- **[2026-06-24] 멀티에이전트 E2E 테스트 계획 + 구현** — Rule 4·6. 4 에이전트(CLI/운영·consumer interop·보안·fresh-clone)가 실측 설계한 53 시나리오 → `docs/superpowers/specs/2026-06-24-okf-e2e-test-plan.md` + `tests/test_okf_e2e.py`(19 E2E, subprocess 미니레포 + 독립 minimal consumer). 전체 195 passed. 설계 중 **단위테스트가 못 잡는 실제 갭 3건 발견·수정**: ↓
- **[2026-06-24·GAP-2] symlink out_dir 거부 dead code 수정** — Rule 8·9. `resolve()`가 symlink를 먼저 해소해 `is_symlink()` 가드가 영구 False였음(A·E2E-19). resolve **전** 원본 인자로 검사하도록 이동. 검증: symlink `--out` 거부 실증 + 회귀 테스트.
- **[2026-06-24·GAP-1] fresh-clone 게이트 침묵 비활성 경고** — Rule 8(fail-loud). gitignored local.yaml 부재 시 sensitive_patterns가 비어 게이트가 조용히 꺼지던 누출 위험(C·D 독립 발견). `sensitive_patterns` 미설정 + local 부재면 stderr 🔴 경고. 검증: fresh-clone 미니레포 경고 발화 + local 존재 시 미발화.
- **[2026-06-24·GAP-3] custom-config local 우회 차단** — Rule 8. `--config custom.yaml` 시 기본 `okf_export.local.yaml`이 silent 무시되던 footgun(A·E2E-10). config별 + 기본 local을 모두 병합. okf/ 출력 불변 확인.

---

## 열린 이슈

### Round 1 — 해결됨 (✅, top-5 수정 완료)
- ✅ [critical·P3] `exclude_paths=[]` 빈 리스트 우회 → `if not exclude_paths`.
- ✅ [critical·P4] README/SPEC/CLAUDE.md OKF 문서화 0건 → 3파일 추가.
- ✅ [major·P2] 블록 리스트 frontmatter 손상 → PyYAML 전환.
- ✅ [major·P3] dry-run 본문 평문 미표면화 → sensitive_patterns 스캐너.
- ✅ [major·P1] description 추출 결함(약어·다이어그램·버전) → 견고화 + 루트 index description.
- ✅ [major·P1/P3] x-llmbrain-sources raw/ 경로 유출 → strip.

### Codex 오탐 (실측 기각 — 수정 안 함)
- fnmatch 중첩 누락(이미 세그먼트 매칭), `_sanitize_fm_value` dict 미처리(이미 분기), encoding 누락(이미 utf-8 명시) — 3건 모두 현재 코드에 반영돼 있어 false positive.

### minor 정리 — 완료 ✅ (2026-06-24, 전부 가역)
- ✅ `_unquote` dead import 제거(P5).
- ✅ META_FILES = export_graph 집합 재사용 + `curate_report.md` 추가 → skip 노이즈 1→0(P5).
- ✅ `karpathy.md` dict 오파싱 sources → `_coerce_source`로 문자열 복원(P2).
- ✅ contract.md ExportStats를 구현(8필드)·`sensitive_patterns` 인자와 동기화(P4 drift).
- (회귀 테스트 2종 추가: dict source 복원·curate_report skip 없음.)

### minor 보류 — 의도적 미수정 (범위 밖·OKF 스펙상 정상·author 콘텐츠)
- `domain` 스칼라/리스트 혼재(P2): raw 원본 보존, exclude 동작 무영향 → 정규화는 데이터 변형이라 보류.
- ghost/excluded 본문 평문 bullet(P1)·body 내 raw/ 경로(P1·P3): wiki **author 콘텐츠**라 export가 재작성하지 않음.
- index 절대경로 로컬 클릭 불가(P1): OKF consumer 정규식 **요구사항**(의도된 설계).
- log.md 제외 slug 노출(P3): 전부 공개 기업명/내용0 식별자 → 누출 아님.
- `agent-paradigm-evolution` description=Stage1만(P1): 근본해결은 wiki 원본에 description 채우기(read-only 범위 밖).
- OSS 위생 파일(CONTRIBUTING 등, P4)·design.md 로컬 PRD 경로(P4): repo-general 사안, OKF 범위 밖 → 사용자 별도 판단.
- README papers/ "누락"(P4): 구조도가 wiki/를 단일 라인으로 표시(서브디렉토리 미전개)라 실제 누락 아님.

> Ralph loop 수렴(critical/major 0) + OKF 관련 minor 정리 완료. 남은 보류 항목은 범위 밖.

---

## 비범위 (이번 작업 아님)
P2 Import 포트 · P3 self-improving distill 루프 · okf/ 자동 재export cron · 내부 wiki 포맷 OKF 교체 · OKF public 웹 게시.
