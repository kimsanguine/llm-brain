# PROGRESS — llm-brain (이니셔티브별 진행 + Decision Log)

> 이 문서는 **진행 현황 + Decision Log**의 단일 확인처다. 주요 변경은 반드시 여기에 기록한다.
> 이니셔티브: **①** [완료] OKF 통합 (Phase 1) · **②** [완료·v0.2.0 릴리스] Agent Memory OS Upgrade · **③** [v0.3.0 구현·검증 완료 / v0.3.1·0.3.2 예산대기] v0.3 Quality-Driven Curation.
> ②③ 요구사항: `docs/PRD.md` · 설계(HOW): `SPEC.md` → 각 "— 설계" 절.
> ① 출처 PRD: `~/Desktop/prd-okf-integration.md` · 설계: `docs/superpowers/specs/2026-06-23-okf-export-p1-design.md` · 계약: `...-contract.md`
> 최종 갱신: 2026-07-04

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

## 이니셔티브 ③ — v0.3 Quality-Driven Curation & Reconciliation (PRD 확정, 구현 착수 전)

> "시간 기반 유지·무게이트 승격·soft dedup" → "품질 게이트 승격 + 매일 reweave + hard dedup + 종합 distill + 모순 화해".
> 요구사항: `docs/PRD.md` 이니셔티브 ③ 절 · 설계(HOW): `SPEC.md` "v0.3 Quality-Driven Curation — 설계" 절.

### 현재 체크포인트 (2026-07-04)
- **상태**: 초안 PRD(`~/.openclaw/PRD-llm-brain-v0.3.md`) → **2-에이전트 크로스체크**(사실 검증 / 설계 타당성, Rule 4 단일 에이전트 불신) → 개정 7건 반영해 `docs/PRD.md`로 이관 확정. 코드 미착수.
- **사실 검증 결과**: 6대 갭 중 5개 CONFIRMED (soft dedup — `is_duplicate` 반환값 미사용·저장 후 호출 / 게이트 코드 0줄 / distill 월요일만 / `engine: api` 미배선 / `contradictions=[]` stub). 1개 PARTIAL (synthesis — 코드엔 없으나 `schema/curate.md`에 "3+ 페이지 → insights/" LLM 규칙 기존재 → WS-1은 신설 아닌 확장).
- **핵심 발견**: ⑴ scripts/는 LLM 무호출·큐 생성기 구조("claude 없이 pytest" 계약) — WS-1/5의 LLM 훅을 curate.py에 직접 넣으면 계약 파괴 ⑵ `wiki/observing|rejected/` 신설 시 okf rglob 무차별 스캔으로 기각 로그 public 누출(one-way door) ⑶ WS-5·6은 신설이 아니라 기예약 슬롯(stub·SPEC 예약 인터페이스) 채우기 ⑷ `run_daily.sh` 프롬프트 경로 drift(`~/Documents/llm-wiki`) 실존.
- **다음**: 병렬 에이전트 작업계획(Wave 0~3, 파일 소유권 분리 + worktree)으로 v0.3.0 착수.

### v0.3.0 Depth Core — 구현·검증 완료 (2026-07-04)
- **상태**: WS-2(게이트)+WS-3(reweave)+WS-4(dedup) 병렬 4-Wave 구현 완료, main 적재(`7e5c647` tip). **420 통과**·`curate --audit` 0·`okf --dry-run` 0.
- **커밋 흐름**: 문서(`ebdec3e`) → 안전망 13테스트(`d05c9fd`) → 규칙문서(`2702528`) → 점수코어 lib추출(`468ff4f`) → hard dedup+capture(`2daffd2`·`4b42d21`) → gates 판정코어 51테스트(`ee8bd26`) → memory_health --fix(`ee93d90`) → reweave 통합배선(`ee0e260`·`5df030b`) → V1 major fix(`7e5c647`). + `run_daily.sh` Step 4·6(매일 reweave·일요일 weekly-summary, gitignored 직접).
- **Wave 4 검증 (3-렌즈, 부분)**: V1 Claude 코드리뷰 = **major 1 + minor 2**, 6관점 SOUND. major(단독 `memory_health --fix`가 observing/rejected/reweave_queue 격리 우회 write) → `_SKIP_META`+`_SKIP_DIRS` 정합 수정·회귀테스트·실측 확인 완료. minor(okf reweave_queue 봉인 활성기전이 exclude_paths 아닌 title-skip) → SPEC 정정. V3 E2E는 **API 월 지출한도 초과로 중단** → 이든(=메인 세션)이 직접 핵심 경로 실측 대체(reweave dry-run 무변경·fix summary 생성·observing→rejected 이동+gate_status·idempotent FIX2 fixed=0·reweave_queue 생성 = 5/5 관측). V2 Codex 적대렌즈 무응답(spend limit 추정) → **미회수**.
- **잔여(deferred, 비차단)**: ⑴ --note hard-dedup 실질 무발화(`HHMM-note` slug가 날짜접두 제거 후에도 index와 불일치 — 회귀 아님, 노트는 원래 dedup 안 됨) ⑵ V2 Codex 적대검증 미회수(예산 재개 시 재실행 권장) ⑶ okf `META_FILES`로 reweave_queue 이관(okf_export.py 접촉 시).
- **⚠ 예산 블로커**: 병렬 worktree 서브에이전트가 API 월 지출한도 초과로 종료됨. v0.3.1·v0.3.2 병렬 진행은 한도 상향 후 재개 필요(사람 결정).

### v0.3.1 Synthesis — 구현·검증 완료 (2026-07-04)
- **상태**: WS-1(종합)+WS-5(모순 화해) 3-Wave 구현 완료, main 적재(`ad89a18` tip). **482 통과**·audit 0·okf 0. (아직 origin push 전 — v0.3.2까지 묶어 최종 push 예정.)
- **커밋**: synthesis lib 21테스트(`9a70b26`) + reconcile lib 28테스트(`82e6345`) + curate 배선 13테스트(`ad89a18`). 설계 = gates.py 패턴 반복(순수 lib → curate import 배선), "claude 없이 pytest" 계약 유지.
- **핵심 설계 판단**: ⑴ shrink 가드를 audit 전역이 아닌 **synthesis 대상 한정 스냅샷**(`.synthesis_snapshot.json`)으로 — distill이 본문을 의도적 압축하므로 전역 스냅샷은 오탐 폭발. ⑵ reconcile은 **정밀도 우선**(주제 게이트 min_overlap≥2 + 공통 주어 요건 + 극 소비 매칭) — WS-5 Q3 "반론 남발" 방지. ⑶ 종합은 distill 아닌 reweave 큐에 배선(synthesis.py 계약·commands Step 3 정합).
- **Wave 7 검증**: E2E 실측 **PASS 4/4 + 오탐 반례 2/2**(모순 감지+오탐억제·종합 대상·shrink 감지+오탐억제·okf 봉인 전부 실관측). 이든 직접 적대 점검 = reconcile 오탐 3케이스(주어 다름·동일 주장·단순 보강) 전부 억제, 진짜 모순만 검출. **codex 적대 렌즈 2연속 mailbox 무응답 → 미회수**(v0.3.0 선례), E2E+유닛(synthesis 21·reconcile 28)+직접 적대점검으로 기술 렌즈 보강.
- **잔여**: contradiction_queue okf 봉인도 title-skip이 활성 기전(reweave_queue와 동일, exclude_paths는 백스톱) · `.synthesis_snapshot.json`은 `.json`이라 okf `*.md` 스캔 비대상(구조적 안전) · codex 적대렌즈 예산 재개 시 보강 권장.

### Decision Log — ③
> 형식: `[날짜] 결정 — 근거(룰) · 가역성 · 검증`
- **[2026-07-04] v0.3.1 = synthesis·reconcile 순수 lib + curate 배선 (gates.py 패턴 반복)** — Rule 2·3. 초안 PRD의 curate.py 내 LLM 직접호출안 대신 결정적 lib(대상선정·모순탐지·shrink가드) + LLM은 commands Step. shrink 가드는 synthesis 대상 한정 스냅샷(전역은 distill 오탐). reconcile 정밀도 우선(오탐 최소). 가역. 검증: E2E 4/4+오탐 2/2, 직접 적대점검 오탐 3/3 억제, 482 통과.
- **[2026-07-04] v0.3.0 major fix = memory_health 단독 --fix 경로도 gates 격리 폴더 제외** — Rule 3·8. V1 리뷰가 `_collect_pages`의 observing/rejected 미제외 + `_SKIP_META`의 reweave_queue.md 부재로 사적 판단폴더 write 격리 우회 포착. curate.find_all_wiki_pages와 정합(`_SKIP_DIRS`). 데이터안전은 보존됐으나(frontmatter-only·idempotent) stated 불변식 위반이라 즉시 수정(v0.3.1 defer 안 함 — fix 자명·작음). 가역. 검증: 임시픽스처 3폴더 md5 불변 실측 + 회귀테스트 + 420 통과.
- **[2026-07-04] V3 E2E 예산초과 → 메인 세션 직접 실측 대체** — Rule 4·8. 서브에이전트가 API 한도로 죽어 "테스트 green ≠ 작동" 실측을 메인이 직접 수행(5/5 관측). 단일 렌즈 불신 원칙상 V2 Codex 미회수는 잔여로 남김(예산 재개 시 보강). 가역. 검증: reweave 실경로 CLI 관측 인용.
- **[2026-07-04] 초안 PRD 검증 = 2-에이전트 크로스체크 (사실 주장 11항 검증 + 구현 지형 8항)** — Rule 4·1. 결과: 설계안(§4 ③)이 v0.2.0 계약·자산과 마찰 7건(블로킹 3) → 개정 후 이관. 가역. 검증: 항목별 file:line 실측 대조.
- **[2026-07-04] LLM 실행 경계 = "scripts/는 결정적 큐, 생성은 commands/curate.md Step"** — Rule 2·6. 초안의 curate.py 내 `synthesize_page()`/`detect_contradiction()` LLM 직접 호출안 기각 — "claude CLI 없이 pytest 통과" 계약(v0.2 AC) 보존, WS-6(llm_client)이 WS-1/5의 전제조건이 되지 않음. 가역(v0.3.2에서 llm_client 경유 옵션 재검토). 검증: 테스트 계약 무변경.
- **[2026-07-04] hard dedup 범위 = 저장 차단 + 기존 페이지 강화 라우팅 제안까지. 자동 병합 금지 유지** — Rule 5·9 (② 확정 결정 "merge-review 자동병합 안 함" 계승). `is_duplicate`는 반환 확장이 아니라 **저장 전 재배선**이 본체(현재 저장 완료 후 호출·반환값 폐기). 가역. 검증: 재배선 후 동일 슬러그 재투입 시 미생성 테스트.
- **[2026-07-04] `wiki/observing/`·`wiki/rejected/` = gitignore + 3점 방어를 폴더 신설과 같은 커밋에** — Rule 8·9 (one-way door). okf `_load_pages`가 rglob 무차별 스캔 → exclude 미비 시 기각 사유 로그가 public 번들 누출. 방어: `okf_export.yaml` exclude_paths + `find_all_wiki_pages` 제외 + lifecycle 제외 (episodes/procedures 선례와 동일 패턴). 가역(설정). 검증: okf dry-run에 두 폴더 미등장 + 설정값 단언 테스트.
- **[2026-07-04] "raw write" 불변식 = body 무손상으로 정의. `frontmatter_utils` 수렴, 파서 5번째 신설 금지** — Rule 1·2. fm 블록 yaml 재직렬화(주석·포맷 소실)는 허용 — ruamel 도입은 과잉. 가역. 검증: 라운드트립 테스트 기존재.
- **[2026-07-04] reweave = 신규 엔진 아님. `run_distill`+`run_lifecycle`+`find_merge_candidates` 오케스트레이터 + weak 신규 기준(800자·근거 2건·H2 3개)** — Rule 2·3 (② PRD "별도 curation 엔진 금지" 계승). 유사도는 `_merge_token_set` Jaccard 재사용. episode는 `task_type: reweave` + memory_score `episode_ref` 집계 제외(자기 점수 되먹임 차단). 가역. 검증: idempotency 테스트(정상 노드 2회 실행 무변경).
- **[2026-07-04] gates.py 선행조건 = 점수 코어(`curate.py:293-624`)를 `scripts/lib/memory_score.py`로 추출** — Rule 2. 게이트↔점수 강결합 상태에서 gates.py만 분리하면 순환 import. 가역(순수 리팩터, 동작 무변경). 검증: 추출 전후 전체 pytest 통과 + score 값 동일 단언.
- **[2026-07-04] frontmatter `status` → `gate_status` 개명 + 용어 "Promotion Gates" 채택** — Rule 1. episodes JSONL `status` 키와 의미 충돌 / 기존 "Quality Gates"(CI 명령)와 동음이의 회피. 가역. 검증: grep 충돌 0.
- **[2026-07-04] 착수 전 안전망 = `is_duplicate`·게이트 진입 경로 현 동작 고정 테스트 + `run_daily.sh` 경로 drift 수정 선행** — Rule 6·8. 두 영역 테스트 0건 상태에서 수정 금지. 가역. 검증: RED→GREEN 순서 준수.

---

## 이니셔티브 ② — Agent Memory OS Upgrade (Phase 0-3 구현 완료)

> 5층 메모리 모델(작업·에피소드·의미·절차·메타)로 llm-brain을 "지식 컴파일러" → "에이전트 메모리 운영 계층"으로.
> 요구사항: `docs/PRD.md` (US-001~008) · 설계(HOW): `SPEC.md` "Agent Memory OS Upgrade — 설계" 절.

### 현재 체크포인트 (2026-06-27)
- **상태**: 설계 확정 + 2-렌즈 크로스체크 반영(`14bf223`) → **Phase 0(토대) 구현·검증 완료**(`a539265`).
  - `scripts/lib/frontmatter_utils.py`(공용 파서) · `scripts/episode.py`(append-only 원장) · `examples/episode-schema-example.jsonl` · `.gitignore`/`okf_export.yaml` 누출 봉인.
  - 검증(실측): 신규 29 통과 · 전체 **224 통과**(회귀 0) · `curate --audit` exit 0 · `okf --dry-run` exit 0(episodes/procedures 미등장, excluded=13 불변).
  - TDD: frontmatter_utils·episode·config 각각 RED(모듈/설정 없음) 관측 후 GREEN.
  - **2-렌즈 코드리뷰 통과**(SOUND-WITH-CHANGES, critical 0) → HIGH 2 + 봉인 1 + 테스트보강 수정 반영(아래 Decision Log).
- **범위 결정**: 전체 아키텍처 1개 설계서(SPEC 흡수) + 단계형 플랜, 코어 루프 우선.
- **Phase 1·2·3 구현 완료** (2026-06-28, 5+2 병렬 worktree 에이전트):
  - P1 쓰기측: express·ingest·wiki_app episode 배선(fail-soft) + US-007 (`bdf8a91`·`acdba2e`)
  - P2 읽기+제어: `brain_context.py`(US-005, degree tie-breaker) + curate `memory_score`·rescue@lifecycle(US-006) (`7c93439`·`88581a7`) → **루프 닫힘**
  - P3 주변: `procedures/`+loader(US-004) + `memory_health`(US-008, okf 봉인) + memory_type 문서(US-003) (`af89e9c`·`146fb46`·`1971f51`)
  - 검증(실측): 전체 **285 통과**(회귀 0) · `brain_context` 실행 exit 0 · okf dry-run exit 0(memory_health/episodes/procedures 미등장)
- **Wave 3 검증 완료** (2026-06-28): 5 페르소나(MD 최신화) + 코드 4 위험점 직접 실측. 조치 → **US-002 curate episode 갭 수정**(실경로 검증) · 문서 일괄 최신화(SPEC 현재형·CLAUDE.md·README) · **index.md gitignore**(business 누출 봉인). 코드(fail-soft·_express_rooted·memory_health 읽기전용·rescue/do_purge) 전부 SOUND.
- **잔여(deferred)**: #5 enum·#6 naive ts·#7 topic 단어경계·#9 dual error class · `_express_rooted` 웹배선 전 리팩터.
- **✅ 갭 마감 (2026-06-28, 이미지 5층 완성)**: 메타 **중복제거**(merge-review, US-006)·메타 **감쇠**(retention→recency decay)·절차 **버전**(procedure version) 구현 + index.md history scrub 완료 → 이미지 5층 + 메타 4동작(보관·중복제거·폐기·감쇠) **전부 ✅**.

### Decision Log — ②
> 형식: `[날짜] 결정 — 근거(룰) · 가역성 · 검증`
- **[2026-06-27] 산출물 = 구현 설계서 + 단계형 플랜(빌드 직전까지), 코드 미착수** — Rule 4(이미 WHETHER 통과한 PRD라 HOW 설계). 가역. 검증: 사용자 선택.
- **[2026-06-27] 설계서 = 전체 아키텍처 1개 + 제어루프 척추 중심(폴더 나열 아님)** — Rule 2·3. 8 US를 하나의 배선도로. 가역. 검증: 사용자 선택.
- **[2026-06-27] 문서 통합 = 새 design.md 신설 0; PRD→`docs/PRD.md`(Desktop 이동)·설계→`SPEC.md`·진행→`PROGRESS.md` 3축** — Rule 3(문서 통합 원칙, 파편화 차단). 가역. 검증: 사용자 선택 + 신설 파일 0.
- **[2026-06-27] memory_score 철학 = 재사용 우선(express_reuse 35 + episode_ref 25 + centrality 15 + access 10 + recency 10 + source 5) + rescue** — Rule 5(사람이 가중치 결정). 단순 access_count와 차별; "클릭 적어도 인용되면 보존". 가역(config 튜닝). 검증: 워크드 예시 비교 후 사용자 선택.
- **[2026-06-27] resonance v1 제외** — Rule 1·2. 실측: resonance는 wiki frontmatter 미저장(컴파일 시 필터링) → 점수 입력 불가. wiki 영속화는 raw→wiki 컴파일 계약 변경(blast radius↑) → v2 후순. 가역. 검증: 4 에이전트 frontmatter 실측 audit.
- **[2026-06-27] episode 저장 = 월별 샤드 `episodes/YYYY-MM.jsonl` + episodes/ 전체 gitignore(예시 1개만 커밋)** — Rule 9(one-way door; 운영 맥락 누출 방지). 가역. 검증: okf wiki/-only 스캔 실측 + 루트 배치 구조적 격리.
- **[2026-06-27] one-way door 봉인 = episodes/·procedures/ repo 루트 + okf `exclude_paths` 방어 2줄 + strip 모드 외부공유** — Rule 8·9. public 누출(비가역)을 폴더 위치 + gitignore + 규칙으로 3중 봉인. 가역(설정). 검증: `okf_export.py` wiki/-only rglob 실측.

- **[2026-06-27] Claude·Codex 2-렌즈 적대 크로스체크 → SOUND-WITH-CHANGES (HIGH 3 + MED 5 + LOW 2 설계 반영)** — Rule 4(단일 에이전트 불신)·8. 두 렌즈가 *서로 다른* HIGH 포착: Claude=**rescue 게이트 오배선**(자문용 `run_distill`에 걸림, 실제 게이트는 `run_lifecycle` inbound==0), Codex=**점수 이중계산**(express 런이 express_reuse+episode_ref 동시 +1), 공통=**memory_health 누출**(wiki/→okf). 반영: ①memory_health→okf `META_FILES`+집계만 ②rescue를 `run_lifecycle`/`_purge`(상대 top-N%) ③episode_ref에서 express 제외 ④cold-start 상대화 ⑤curate→`episode.append` ⑥config 부분/오류 키 안전 ⑦ai_answer `finally` 양 핸들러 ⑧brain_context degree tie-breaker+rglob 정렬 ⑨frontmatter_utils '단일출처' 프레이밍 교정 ⑩Phase0 무변경 단서. 가역(설계 문서). 검증: 양 렌즈 실측 코드 대조(okf `wiki/` rglob·`run_lifecycle` inbound==0·`META_FILES`에 health 부재) → SPEC §C/§D 반영 완료. HIGH 3 미수정 시 빌드 금지.

- **[2026-06-27] Phase 0 코드 2-렌즈 리뷰 → SOUND-WITH-CHANGES (critical 0), HIGH 2 + 봉인 1 + 테스트보강 수정** — Rule 4·8. Claude=`json.dumps` 가 `EpisodeSchemaError` 밖→fail-soft 우회(express 가 `Path` 넘기면 Phase 1 크래시), **양쪽**=`read_recent` 문자열 정렬(오프셋 TZ 오정렬), Claude=`procedures/` gitignore 누락. 수정(TDD RED 재현): #2 직렬화 `try→EpisodeSchemaError`(FS 부작용 전), #1 `datetime` 키 정렬(naive→UTC), #4 `procedures/` gitignore(가역·US-004 재검토), +견고성 테스트(broken-line·크로스샤드·limit-newest). **deferred(선택)**: #5 enum 검증·#6 naive ts 거부·#7 topic 단어경계·#9 dual `FrontmatterParseError`(이관 시). 검증: 신규 6 RED→GREEN, 전체 224 통과, okf dry-run exit0 누출0.

- **[2026-06-28] Phase 1·2·3 병렬 구현 (5+2 worktree 에이전트, 파일소유 분리)** — Rule 9(worktree 격리·scope 명시)·4. Wave 1: express+ingest·wiki_app·curate score·procedures·docs(disjoint). Wave 2: brain_context·memory_health. cherry-pick 선형 병합 → 전체 285 통과. **함정: worktree가 origin/main(stale, Wave1 미push) 기준 분기** → A4·A6가 ff-merge/cherry로 자가교정([[feedback_agent_worktree_base_and_commit]]). 교훈: 다음 wave 전 cherry-pick push 필수. **procedures = git-tracked+OKF-excluded**(#4 과잉 정정, US-004 정합). curate `do_purge` 정규식을 Lifecycle 섹션 한정으로 축소(rescue 보존 위해 필요). 가역. 검증: 통합 285 통과·okf 누출0·brain_context 실행 exit0.

- **[2026-06-28] Wave 3 검증(5 페르소나 + 코드 직접검증) → 문서 최신화 + US-002 갭 수정 + index.md 봉인** — Rule 4(기술+페르소나 양 렌즈)·8·9. 페르소나 5/5 NEEDS-UPDATE: 문서(README·SPEC 현재형·CLAUDE.md·PROGRESS 라벨)가 신규 코드 미반영 → 일괄 최신화. **PM 페르소나가 over-claim 포착**: US-002 curate→episode.append 미배선(ingest·express·wiki_app 3개만 done) → TDD로 수정 + 실경로 기록 검증. **보안 페르소나가 index.md business 누출 포착**(public GitHub, okf 옆문) → 사용자 결정 'gitignore+추적해제'(history scrub는 별도). 코드 4 위험점(fail-soft 래핑·_express_rooted try/finally·memory_health write 1곳·rescue Lifecycle 섹션밖) 직접 실측 SOUND. mailbox 코드리뷰어(cr-claude·cr-codex) flaky 미응답 → 직접 검증 대체. 가역. 검증: 신규 3 RED→GREEN, curate episode 실경로 기록(orphans=2).

- **[2026-06-28] 코드리뷰 cr-claude → SOUND(차단 0); cr-codex 회수불가(정직 보고)** — Rule 4·8. cr-claude: fail-soft 3배선·rescue/do_purge·_express_rooted·memory_health 읽기전용 전부 통과. **반가운 발견**: A3의 do_purge 축소가 실은 Distill 후보(고access) 페이지를 archive로 옮기던 *기존 버그 수정*이었음(테스트 증명). minor 7(전부 LOW/latent) → deferred: ① `_express_rooted` CLI-전용·동시성 비안전(주석 추가) ② api `_record_ai_episode` silent except 로그 ③ express/ingest import 비방어 ④ "wiki_root" 동명이의 ⑤ memory_health config 재로드 perf 등. cr-codex는 mailbox flaky로 Codex 결과 미회수 — cr-claude SOUND + 직접검증 + 288 테스트로 코드 신뢰 충분. 가역. 검증: cr-claude verbatim 인용.

- **[2026-06-28] 이미지 5층 갭 3종 구현 (메타 중복제거·감쇠 + 절차 버전)** — Rule 1·5·9. 사용자가 5층 이미지로 미구현 부분 점검 요청 → 실측: 메타 "중복제거/감쇠" 미구현·절차 "버전" 미구현 포착. ① **merge-review**(US-006): 같은 카테고리 내 title+tags Jaccard≥0.6 후보를 curate_report에 표면화, **자동병합 안 함**(사람 결정). ② **감쇠**: `retention`이 memory_score recency 감쇠율 조절(durable=0·seasonal=1·ephemeral=2), 선언만 됐던 필드를 작동시킴(폐기와 별개). ③ **procedure version**: 절차 frontmatter `version` + 헬퍼. 갭 A+B는 worktree 에이전트(curate.py), C는 직접(procedures.py). 가역(config 튜닝). 검증: 신규 16 TDD RED→GREEN, main 전체 **304 통과**, okf 누출0. (worktree의 wiki_app_search 4 fail은 데이터부재 — main 데이터로 통과 실증.)

- **[2026-06-28] E2E 5/5 PASS(실 repo 실행 관측) + doctor·wikiweb 커맨드 추가** — Rule 4·8. 5 서브에이전트가 실 데이터에 실제 명령 실행·관측(테스트 green ≠ 작동): brain_context(6섹션 결정적·0.03s)·memory_health(읽기전용·verbatim 부재 실증)·curate 메타(score 52.58·merge-review emit·decay 단조 durable>seasonal>ephemeral·rescue 분기)·episode 쓰기(9키 정합·fail-soft)·okf 보안(3중 봉인). **실동작 진실**: ingest exit 1=by-design(컴파일 대기 신호; episode는 그 전 기록)·원장이 "ping" 스모크 위주(데이터 미성숙, 기능 무관)·flock 없는 append 병렬 간섭을 정직 귀속(#7 topic 연속부분문자열 한계 노출). **신규 커맨드**: `scripts/doctor.py`(설치 40체크 진단 + `--fix` 안전복구, 기존파일 미덮어씀) + `commands/{doctor,wikiweb}.md`. 검증: doctor 실 repo ✅40/⚠️0/❌0·wikiweb `GET /`=200·`/api/index`=200·전체 309 통과. 가역.

### 변경 표면 (AS-IS → TO-BE)
> 코드 레벨 line-by-line diff(curate `run_distill`·frontmatter·express·okf)는 `SPEC.md` §C·§D 참조 — 여기선 구조 요약만(중복 drift 방지). **신규 4파일 + 변경 6파일 + 신규 2디렉터리.**

```
260516_llm_brain/
  raw/ wiki/ express/ okf/         [기존]  변경 0 (wiki = semantic 기억 그대로)
  scripts/
    ingest.py     ~ 저장 성공 후 episode.append (status=pending)
    curate.py     ~ compute_memory_score + rescue (run_distill 343–356)
    express.py    ~ 재사용 frontmatter + save_draft 후 episode.append
    okf_export.py / export_graph.py / sync_raw.py   [기존]  무접촉
+   lib/frontmatter_utils.py   파싱 단일 출처 (read_fm/write_fm, fail-loud)
+   episode.py                 에피소드 원장 (append/read_recent)
+   brain_context.py           작업기억 팩 조립
+   memory_health.py           읽기전용 건강 리포트
  wiki_app/api.py   ~ AI답변 _collect_context 직후 episode.append
  schema/config.yaml       ~ memory_score 가중치·CAP·RESCUE_THRESHOLD
  schema/okf_export.yaml   ~ exclude_paths += episodes/**, procedures/**
+ episodes/        루트·gitignored   YYYY-MM.jsonl (월별 샤드)
+ procedures/      루트              *.md (memory_type: procedural)
+ examples/episode-schema-example.jsonl   커밋되는 스키마 예시 1개
  .gitignore       ~ episodes/ 추가
```

**데이터 흐름:** AS-IS = `raw→wiki→express/okf` 선형(되먹임 0, 읽기=매번 index 전체검색, 폐기=access 임계만). TO-BE = ① `brain_context` 작업기억 팩 읽기 → ② 각 실행이 `episode.append` → ③ `curate.memory_score`가 보존/폐기 결정(rescue: 인용 많으면 archive→promote) → 건강한 wiki만 다음 ①에 읽힘(**순환**).

### 구현 단계 (유지→변경→신규, 코어 루프 우선)
| Phase | 성격 | 내용 | 루프 효과 | PRD US |
|---|---|---|---|---|
| **0 토대** | 신규·저위험 | `frontmatter_utils` + `episode.py` + episodes/ gitignore + okf 방어 2줄 + `examples/episode-schema-example.jsonl` | 기존 동작 무변경(호출 0) | 001 |
| **1 쓰기측** | 변경 | `episode.append` 배선(express→ingest→wiki_app) + express 재사용 메타 | ② 턴 이후 쓰기 ON | 002·007 |
| **2 읽기+제어** | 신규+변경 | `brain_context.py`(degree tie-breaker) + curate `memory_score`·**rescue(`run_lifecycle`/`_purge`)**·**curate→episode.append** | ①읽기+③제어 ON → **루프 닫힘** | 005·006·002 |
| **3 주변** | 신규 | `procedures/`+loader + `memory_health`(**+okf `META_FILES` 동반**) + memory_type 문서(SPEC·README) | 저장 기질 보강 | 004·008·003 |

각 Phase: 품질 게이트(`uv run pytest` · `curate.py --audit` · `okf_export.py --dry-run` · wiki_app 기동) 그린 후 다음. 결정은 본 로그에 누적.

### 테스트 전략 (결정성 지점)
- `episode.py`: 정상 append · malformed 거부(`EpisodeSchemaError`) · `read_recent` 필터·순서.
- **호출측 fail-soft**: `episode.append`이 raise해도 express/ingest/ai-answer 명령은 성공(mock raise → exit ok).
- `frontmatter_utils`: 라운드트립 · invalid fail-loud · 신규 필드 보존.
- `brain_context`: 빈 wiki · 매칭 페이지 · episode 포함 · procedure 포함 · 결정적 순서.
- `memory_score`: 결정적 값 · **rescue 케이스**(저 access + 고 reuse → 구조) · config 부재 fallback.
- `memory_health`: 픽스처 리포트 생성 · 읽기전용(파일 미이동).
- `okf`: 기존 보안 스위트 + **episodes/procedures가 export 목록에 미등장** 신규 테스트.

**리뷰 반영 테스트(2-렌즈 크로스체크):**
- **rescue@lifecycle**: 재사용↑·inbound==0·age>ttl 페이지가 `run_lifecycle`/`_purge`에서 archive 제외(보존) — 상대 top-N%.
- **episode_ref dedup**: `express_*` 에피소드가 `episode_ref`에 미집계(이중계산 0).
- **config robustness**: 누락 키=기본·0/음수 CAP·타입오류=fallback+warn; 테스트는 `now` 고정.
- **ai_answer**: 스트림·비스트림 둘 다 episode 기록 + 최종 status(done/timeout/error) 캡처.
- **memory_health 누출**: `memory_health_report.md`가 okf export 목록 미등장(`META_FILES`) + 리포트에 verbatim episode 본문 0.
- **okf config 값 단언**: `exclude_paths`에 `episodes/**`·`procedures/**` 존재(결과뿐 아니라 설정값).
- **brain_context**: graph degree tie-breaker + `find_wiki_file` 정렬로 결정적 순서.

### 비범위 — ②
벡터 DB 도입 · raw→wiki 컴파일러 모델 교체 · 메모리 자동 삭제 · OKF 기본 episode/procedure 공개 · 멀티에이전트 오케스트레이션 플랫폼 · (v1) resonance 점수 입력.

---

> **아래는 이니셔티브 ① OKF 통합 (Phase 1) 기록 — 완료·push됨(main).**

## 현재 체크포인트 (2026-06-25)

- **상태**: Phase 1(OKF Export) + 보안 강화 + Ralph loop 3R 수렴 + E2E + 문서 검수 **완료·public push됨**(main).
- **테스트**: `pytest` 전체 **195 통과**(OKF 단위 54 + E2E 19).
- **검증**: 실 round-trip dangling=0·business=0·깨진 키 0·json.dumps 전수. dry-run(민감 제외 적용): excluded=13(business 4 + 민감 slug 9) / sensitive_hits=0 / pages=84.
- **Ralph loop 수렴 곡선**: R1 critical 2+major 6 → R2 major 2 → R3 major 1 → 수렴(6 렌즈 새 critical/major 0).

### public 커밋 보안 게이트 (재export·재커밋 시 매번 — 충족 후에만 커밋)
1. **gitignored `schema/okf_export.local.yaml` 존재 확인** — 민감 키워드(`sensitive_patterns`)·제외 페이지(`exclude_slugs`)는 **반드시 이 로컬 파일에만** 둔다. **커밋되는 `schema/okf_export.yaml`에는 실명·내부명을 절대 넣지 않는다**(그 자체가 누출). fresh clone/CI엔 이 파일이 없어 게이트가 비활성 → 그 상태로 커밋 금지.
2. `uv run python scripts/okf_export.py --dry-run` → ① `business 제외 4건` ② `sensitive_hits=0` ③ **`excluded` 카운트 = business 4 + 민감 slug 수**(기대값과 일치)인지 사람이 검토. (local.yaml 부재 시 `pages`가 늘고 민감 페이지가 included로 조용히 섞이니 카운트 대조 필수.)
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
- **[2026-06-24→25] GO 조건 충족 + 커밋·머지·push** — Rule 9. dry-run 보안 게이트로 본문 평문 민감정보 검토 → 사용자 결정 "전부 제외"로 민감 페이지 9개를 `exclude_slugs`(로컬 `.local.yaml`)에 추가, sensitive_hits 0 수렴. okf/ 84페이지 생성(business 4 + 민감 slug 9 제외). 커밋 `88f8fa4`(OKF 파일만, 기존 미커밋 index.md·log.md·examples 보존). **main 머지 + origin push 완료**(GitHub 라이브 검증: business 404·제외 페이지 부재). 로컬 민감설정은 gitignored 유지.
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
