---
type: insight
title: 에이전트 빌드 하네스 패턴
description: 에이전트 빌드는 Constitution + eval.sh + RALPH Loop의 3요소 조합.
tags:
- agent-pattern
- multi-agent
- harness
- evaluation
- worktree
timestamp: '2026-06-04'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 4
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 에이전트 빌드 하네스 패턴

## 핵심 원칙

에이전트 빌드는 Constitution + eval.sh + RALPH Loop의 3요소 조합. Generator-Evaluator 분리가 필수이며, 실패 사례는 규칙으로 자동 승격해 하네스를 자가 강화한다.

이론 근거는 [agent-harness-pattern](/concepts/agent-harness-pattern.md) 참조. 이 페이지는 **실제 구현 패턴**에 집중한다.

---

## 발견된 패턴

### /build v3 핵심 구조 (2026-03-29)
- **Constitution 3파일 분리**: 절대 비위반 룰 / 유연한 룰 / 프로세스 룰
- **eval.sh JSON 직접 출력**: `cat <<EVAL_JSON` 패턴으로 구조화된 점수 출력
- **자동 60% + 수동 40%** 혼합 평가
- **프로젝트 CLAUDE.md + pre-commit hook** 자동 생성
- **하네스 축소 트리거**: 연속 3 PASS → 불필요 규칙 제거

### RALPH Loop 방법론 (2026-03-21, 2026-04-12)
- 정량 평가 기준 설정 → 병렬 에이전트 수정 → 빌드 → 재평가 → 90점 미만 있으면 반복
- model-chat 5라운드는 3라운드보다 논쟁 구조가 깊어짐 (미해결 쟁점 명시적으로 드러남)
- 관대한 평가 기준은 품질 향상을 막음 → 처음부터 엄격한 기준 설정

### 멀티 CLI 에이전트 오케스트레이션 (2026-04-12)
- Codex CLI(백엔드) + Gemini CLI(프론트엔드) 병렬 worktree 배치
- 계약(spec) 고정 + worktree 격리 + 리뷰 후 머지
- Codex CLI sandbox 제약: 네트워크/git 접근 불가 → 오케스트레이터 후처리 필요

### 서브에이전트 정의 패턴 (2026-04-15)
- YAML frontmatter + 본문 + 메모리 스캐폴딩 구조
- `<example>` 블록 3개 이상이 자동 위임 정확도를 결정
- `~/.claude/agent-memory/<agent>/` 사전 생성으로 첫 호출 부작용 방지
- 기존 확장 vs 신규 분리 기준: 맥락 공유 강하면 통합, 레이어 다르면 분리

### Hook 구축 5단계 검증 (2026-04-15)
- dedup → raw command → 파이프 테스트 → JSON 병합 → `jq -e` schema 검증 → 실제 발화 증명
- 중간 스킵 시 silent 실패 발생
- Hook은 세션 시작 시점 settings.json 스냅샷만 로드 → 세션 중 편집 시 재시작 필요

### 병렬 에이전트로 강의자료 대규모 구조 변경 (2026-04-12)
- 15분 내 강의자료 전면 개편 사례
- Part 분할 + 신규 섹션 삽입 병렬 dispatch

### Plan Mode + 슬래시 커맨드 충돌 패턴 (2026-04-21)
- 플랜 모드 활성 시 실행형 커맨드는 ExitPlanMode 먼저 호출 후 실행

### STATE.md 자동 주입 패턴 (2026-05-16)
- GSD 아키텍처에서 차용한 패턴: `settings.json` SessionStart hook으로 매 세션 `STATE.md`를 자동 주입한다.
- 목적은 context rot 방지다. 에이전트가 이전 세션의 active condition, 현재 gate, 다음 액션을 잃지 않게 한다.
- hplan 적용안: `CONDITIONAL_GO` 출력 시 `STATE.md` 템플릿을 생성하고 6개 active condition을 유지한다.

### HARD-GATE 태그와 예외 설계 (2026-05-16)
- Superpowers의 HARD-GATE 패턴은 스킬 파일 태그로 human approval을 강제하는 방식이다.
- hplan에는 Evidence Gate / Product Gate 우회 차단에 적용한다.
- 단, AI 페르소나·경쟁사 분석은 Evidence Gate의 **입력 리서치**이지 gate output이 아니므로 예외를 허용한다.

### 하네스 레이어 분리 (2026-05-16)
- hplan은 **what to build**를 결정하고, Superpowers/GSD/GStack은 **how to build**를 실행한다.
- 순서를 뒤집으면 구현 프레임워크가 제품 판단을 삼킨다.
- hplan-discuss는 `PROGRESS.md` 템플릿으로 흡수하고, condition-sync는 hplan-verify로 흡수하는 방향이 결정됐다.

### hplan v0.8.4 production cycle (2026-05-18)
- v0.7.5 → v0.8.4까지 단일 production cycle을 완주했다.
- 3라운드 Codex 적대적 검수로 findings가 4 → 3 → 1로 줄었고 high 잔여 0까지 수렴했다.
- multi-agent audit(UX Writer / AI PM / Designer / Localization)으로 13개 issue를 발견하고 HIGH 7 + MEDIUM/LOW 6을 수정했다.
- 4개 영상 variant(Editorial 60s / Demo 90s / Core 84s / Core+Track 99s)와 3개 aspect ratio(16:9 / 1:1 / 9:16) 산출물이 GitHub release에 붙었다.
- 후속 과제는 hplan 페이지 9→7 section 간략화, aspect별 layout 분기, 4차 Codex review로 수렴 확인이다.

### hplan v0.9.1 문서 일관성 시나리오 (2026-05-22)
- 한국어 문서 개선에서 Hero는 “요구사항 + install 블록”을 배지 아래 추가하는 최소 변경으로 정리됐다.
- GUIDE-ko 시나리오 1은 B2B 고객센터에서 1인 메이커 AI 가계부 5-step 플로우로 교체됐다.
- 핵심 가치는 gate(WHETHER) + arch 기준선 + design-token 기준선 + health-check 이탈 감지가 하나의 일관성 루프로 이어지는 것.
- HOLD-only 또는 GO-only 시나리오는 hplan의 두 번째 핵심 가치인 “개발·디자인 일관성 유지”를 충분히 보여주지 못한다.
- 남은 후속 과제는 v0.9.1 65 skills 기준 97.9% 정확도 수치 재측정과 README-ko.md 구 v0.6 영상 섹션 교체다.

### hplan v0.13.0 gate 강화와 UI assertion (2026-05-27)
- COGS sentinel은 음수/0 입력을 _validate_params()에서 SystemExit로 막아 GREEN 오판정을 차단했다.
- MCP product_gate는 checkpoint.json과 cogs_result.json을 실제 파일 검사로 확인하도록 강화됐다.
- conductor는 Phase 0에서 harness/PRD.md 필수 체크 후 implementation-plan.md를 만들고, Step E에서 태스크 완료 후 COGS impact를 검토한다.
- sprint 모드는 depends_on: [] 독립 태스크만 병렬 디스패치해 파일/책임 소유권 충돌을 줄인다.
- ui-validate는 QA_CHECKLIST 8컬럼, 3타입 assertion, critical_assertion_fails, BLOCK_ASSERTION_FAILED를 갖춘 assertion 엔진으로 확장됐다.

핵심 학습은 하네스가 단순 체크리스트가 아니라 **입력 파라미터 검증 → 파일 기반 product gate → 병렬 실행 조건 → UI assertion**까지 이어지는 실행 경계라는 점이다.

### SkillOpt와 솔로 빌더 스킬 루프 (2026-05-31)

2026-05-31 newsletter 묶음은 스킬을 하네스의 실행 단위로 다룬다. Peter Yang 인터뷰의 Josh Pigford 사례는 `/build`를 Research → Plan → Track → Implement로 고정하고, `/adversarial-code-review`로 다른 모델 패밀리 리뷰를 붙이며, `/but-for-real`로 push 전 추가 버그를 강제로 찾게 한다. `/learnings`는 실패 사례를 CLAUDE.md에 반영해 다음 실행 품질을 높이는 루프다.

NLP Newsletter의 SkillOpt는 같은 패턴을 연구 형태로 정식화한다. 스킬 문서를 frozen agent의 trainable state로 보고, rollout과 reflection으로 수정안을 만들되 held-out validation gate를 통과한 변경만 유지한다. 실무적으로는 [agent-skill-optimization](/insights/agent-skill-optimization.md)처럼 스킬 파일을 "좋은 지침서"가 아니라 회귀 테스트 가능한 자연어 상태로 관리해야 한다.

### hplan Codex 포팅과 이종 adversarial 검증 (2026-06-03)

hplan_codex 포팅은 같은 Claude 계열 평가만으로는 못 잡는 호환성 결함을 Codex adversarial이 발견한 사례다. v0.1.0은 문서상 그럴듯했지만 실제 Codex 스키마와 맞지 않았고, Codex 0.130.0 실측 후 폴더 단위 `SKILL.md`, `agents/openai.yaml`, fail-loud `setup.sh`로 재편했다. 최종 게이트는 실제 `codex exec` 28/28 로드·실행 검증이었다.

하네스 원칙으로는 "문서 검증 ≠ 런타임 검증"을 명시한다. 외부 에이전트 생태계로 포팅할 때는 README/스키마 추정, 정적 grep, self-review를 통과해도 실제 CLI 실행이 없으면 완료가 아니다.

---

## 외부 검증된 패턴 (2026-04 Anthropic 발표)

### Initializer + Coding Agent 분리 (Anthropic Engineering)
- **Initializer Agent**: 첫 실행 시 init.sh + claude-progress.txt + 초기 git 커밋 생성
- **Coding Agent**: 이후 세션에서 증분 처리. Feature List(JSON, 200+기능)로 조기 완료 방지
- 세션 시작 루틴: git 히스토리 확인 → 진행 파일 읽기 → 기능 테스트 → 다음 기능 처리

### 5계층 안전 아키텍처 (OpenDev arXiv 2026-03)
방어 심층 설계:
1. 시스템 지침 **프롬프트 수준 가드레일**
2. 서브에이전트별 툴 허용 목록 **스키마 수준 제한**
3. 영구 권한 포함 **런타임 승인 시스템**
4. 위험 패턴 차단 **툴 수준 유효성 검사**
5. 사용자 정의 사전 실행 점검 **라이프사이클 훅**

### PEV Loop (Plan-Execute-Verify)
Augment Code가 정리한 확장 버전:
- Plan: 명시적 문제 분해 (Plan Mode)
- Execute: 에이전트 실행
- Verify: 살아있는 사양에 대한 검증 (Verifier Agent)
각 전환에 게이트 → 비결정성을 사후 테스트만으로 해결 불가 문제 처리

---

## 측정 프레임워크

하네스 성능 추적 지표 (볼륨 지표 "lines accepted"는 금지):

| 지표 | 측정 방법 |
|---|---|
| Task resolution rate | 첫 시도 통과율 (Pass@1) |
| Code churn | 생성 후 수정/삭제 비율 |
| Verification time | eval.sh 검증 소요 시간 |
| Defect escape rate | 리뷰 후 발견된 버그 수 |

---

## 적용 방법

1. **Constitution 작성**: 절대 비위반 / 유연 / 프로세스 3파일 분리
2. **eval.sh 구현**: JSON 직접 출력, 자동 60% + 수동 40% 혼합
3. **RALPH Loop 실행**: 정량 기준 설정 → 병렬 수정 → 빌드 → 재평가 사이클
4. **실패 자동 승격**: lessons-learned → constitution 갱신 절차 포함
5. **하네스 축소**: 연속 PASS 후 불필요 규칙 정리 (모델 성능 향상 시 재검토)

---

## 관련 개념

- [agent-harness-pattern](/concepts/agent-harness-pattern.md) — 이론 프레임워크 (OpenAI/Anthropic 원칙)
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) — PGE 3-에이전트 패턴 상세
- [harness-engineering-evolution](/concepts/harness-engineering-evolution.md) — 하네스 엔지니어링이 필요한 역사적 맥락
- 260515_100_agents — 실제 Agent100 빌드에 이 패턴 적용
- [claude-code-agent-system](/tools/claude-code-agent-system.md) — Claude Code 기반 서브에이전트 시스템
- [context-dealer-pattern](/concepts/context-dealer-pattern.md) — 하네스에 공급할 컨텍스트 설계
- til-patterns-2026-05 — 관련 TIL 패턴
- [agent-skill-optimization](/insights/agent-skill-optimization.md) — 스킬 문서 최적화와 validation-gated edit 패턴
