---
type: tool
title: OpenAI Codex (2026)
description: OpenAI가 개발한 아젠틱 코딩 AI.
tags:
- openai
- codex
- coding-agent
- agentic-workflow
- computer-use
timestamp: '2026-06-04'
x-llmbrain-domain:
- tools
- AI/LLM
x-llmbrain-created: '2026-05-27'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# OpenAI Codex (2026)

## 핵심 요약

OpenAI가 개발한 아젠틱 코딩 AI. 단순 코드 완성이 아니라 **장기 목표를 받아 자율 실행**하는 에이전트 플랫폼이다. App(macOS), IDE Extension, CLI, Web 네 가지 실행 환경을 지원하며, GitHub/Slack/Linear 통합과 Computer Use(Mac 화면 조작)까지 포함한다.

> 구 Codex(코드 완성 모델, 2021)와 별개 제품이다. 2026 버전은 GPT-5.4 기반 멀티스텝 에이전트.

## 주요 기능

### 실행 환경
| 환경 | 특징 |
|------|------|
| **App (macOS)** | GUI + Worktrees + Computer Use + 브라우저 내장 + Chrome 확장 |
| **IDE Extension** | VS Code 등 편집기 내 직접 실행 |
| **CLI** | 비대화형 모드, SDK, GitHub Action 연동 |
| **Web** | Cloud 환경, 샌드박스 실행, 인터넷 액세스 옵션 |

### 핵심 개념
- **Goals (목표 추종)** — 단발 태스크가 아니라 지속적 목적 설정; 변경 감지·자율 진행
- **Memories** — Chronicle 시스템으로 세션 간 맥락 유지
- **Skills** — 반복 워크플로우를 저장해 재호출 가능한 작업 단위
- **Subagents** — 복잡 태스크를 병렬 서브에이전트로 위임
- **Computer Use** — Mac 화면 클릭·타이핑·앱 탐색 직접 수행

## Use Case 카탈로그

### Featured (주요 3선)
1. **Manage your inbox** — 이메일 필터링 + 사용자 목소리 모사 자동 회신 (`Automation + Integrations`)
2. **Use your computer with Codex** — Mac 앱 탐색·클릭·타이핑 자동화 (`Knowledge Work + Workflow`)
3. **Follow a goal** — 장기 실행 작업에 지속 목표 부여 (`Engineering + Automation`)

### 카테고리별 전체 Use Cases

**Engineering / Code**
- Refactor codebase (dead code 제거, 레거시 패턴 모던화)
- Run code migrations (레거시 스택 단계 마이그레이션)
- Keep documentation up-to-date (코드 기반 자동 문서 갱신)
- Upgrade API integration (최신 OpenAI API 모델로 업그레이드)
- Create agent-friendly CLIs (에이전트가 쓸 수 있는 composable CLI 설계)
- Audit dependency incidents (취약 패키지 안전 감사 계획 수립)
- Understand large codebases (요청 흐름 추적, 모듈 매핑)
- Iterate on difficult problems (scored improvement loop)
- Create browser-based games (게임 플랜 → 브라우저 빌드·테스트)

**Front-end / Design**
- Build responsive front-end designs (스크린샷·레퍼런스 → 반응형 UI)
- Turn Figma designs into code (Figma 선택 → 시각 검증 포함 UI)
- Make granular UI changes (Codex-Spark 집중 반복)
- Deploy an app or website (빌드·배포·프리뷰 URL 생성)
- Get from idea to proof of concept (ImageGen + 첫 버전)
- Turn user stories into UI mocks (이슈·피드백 → 목업)

**Automation / Quality**
- Automate bug triage (일간 버그 리포트 → 우선순위 목록 + 자동화)
- QA your app with Computer Use (실제 플로우 클릭 → 오류 로그)
- Add evals to your AI application (Promptfoo eval suite 자동 생성)
- Set up a teammate (지속 감시·변경 감지 자율 에이전트)
- Run verified operations (반복 워크플로우 + 결과 검증)
- Prioritize Slack action items (Slack 스레드 → 우선순위 큐)

**Data / Knowledge Work**
- Clean and prepare messy data (원본 보존 tabular 정제)
- Query tabular data (CSV/스프레드시트 자연어 질의)
- Analyze datasets and ship reports (데이터 → 시각화 + 분석 보고서)
- Learn a new concept (소스 → 학습 보고서)
- Forecast cash flow (유동성 low-point 예측 워크북)
- Model a DCF valuation (재무 입력 → 평가 워크북)
- Review budget vs. actuals (계획·실적·메모 → 분산 분석)

**Integrations / Workflow**
- Review GitHub pull requests (회귀·잠재 이슈 사전 감지)
- Kick off coding tasks from Slack (Slack 스레드 → cloud 태스크)
- Complete tasks from messages (iMessage → 앱 간 작업 완료)
- Turn meetings into follow-ups (Zoom 미팅 → 도구 간 액션)
- Prepare meeting briefs (캘린더 컨텍스트 → 아젠다·노트)
- Run event playbooks (이벤트 프로그램 관리 반복 워크플로우)
- Draft PRDs from internal context (Linear/Slack/문서 → PRD)
- Coordinate new-hire onboarding (온보딩 트래커·팀 요약 준비)
- Turn feedback into actions (멀티 소스 피드백 → 리뷰 아티팩트)
- Bring your app to ChatGPT (ChatGPT Apps SDK 연동)

**Native Development**
- Build for iOS (SwiftUI 스캐폴드·빌드·디버그)
- Build for macOS (SwiftUI 네이티브 Mac 앱)
- Add iOS app intents (Shortcuts/Siri/Spotlight 액션 연동)
- Adopt liquid glass (iOS 26 + Xcode 26 마이그레이션)
- Debug in iOS simulator (XcodeBuildMCP 기반 시뮬레이터 증거 수집)
- Refactor SwiftUI screens (거대 뷰 → 서브뷰 분리)
- Build Mac app shell (Sidebar+Detail+Inspector 구조)
- Add Mac telemetry (Logger 계측 + 동작 검증)
- Build React Native apps with Expo (Expo 플러그인 기반 모바일)

**Save & Reuse**
- Save workflows as skills (반복 작업 → Codex skill)
- Generate slide decks (pptx + 이미지 생성 자동화)

## 사용 패턴

### 비대화형(Non-interactive) 자동화
- `--non-interactive` 모드 + GitHub Action 결합 → CI 파이프라인에서 자율 실행
- Slack 통합: 스레드 링크 하나로 클라우드 태스크 생성
- Automations(앱 내): 스케줄·트리거 기반 반복 실행

### Skills 재사용 패턴
자주 쓰는 워크플로우(e.g. PR 리뷰, 데이터 정제)를 Skill로 저장 → `/skill <이름>`으로 호출. [openai-agents-sdk](/tools/openai-agents-sdk.md)의 Skills 개념과 동일 계보.

### Goal 기반 장기 실행
단발 명령 대신 "목표" 설정 → 파일 변경·이벤트 감지 시 자동 재개. [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) 개념의 실제 구현체.

### 비개발자 프로덕션 빌드 패턴

2026-06-01 How I AI raw는 코딩 경험 없는 도메인 전문가가 Claude, Claude Code, Terminal 조합으로 iPhone 앱을 App Store에 출시한 사례를 기록했다. 워크플로우는 일반 Claude로 계획을 잡고, Claude Code로 구현하고, Terminal에서 실행·검증하는 3단 구조였다.

Codex 관점의 의미는 "누가 소프트웨어를 만들 수 있는가"의 경계가 바뀌고 있다는 점이다. 도메인 전문가는 기술 중개자 없이도 첫 버전을 만들 수 있지만, 실제 병목은 스크린샷 기반 디버깅, 반복 검증, 배포 품질 확인으로 이동한다. 이는 ai-workforce-restructuring과 [ai-pm-role](/concepts/ai-pm-role.md)의 실무 사례다.

### Codex CLI 포팅 검증 패턴

2026-06-03 TIL은 hplan을 Claude Code 전용 구조에서 Codex CLI용 public 레포로 이식한 실측을 남겼다. 핵심 교훈은 문서 검증과 런타임 검증이 다르다는 점이다. Codex 0.130.0 기준 스킬은 `~/.codex/skills/<name>/SKILL.md` 폴더 단위이고, MCP는 `agents/openai.yaml`에서 소비된다. 실제 `codex exec`로 28/28 로드·실행 검증을 통과하기 전까지 "포팅 완료"로 보지 않는다.

설치 스크립트에서도 `cp -r src/ dest/` trailing slash, `|| echo skip`로 `set -euo pipefail` 무력화, validator의 금칙어 자기탐지 같은 작은 실패가 production 품질을 흔든다. Codex용 배포물은 fail-loud setup, 실제 CLI 실행, 금칙어 grep 회피까지 한 세트로 검증한다.

## 주의사항 / 함정

- **Almost-Correct 실패**: 컴파일·테스트 통과하나 프로덕션 부하에서 통합 버그 발생. 빠른 검증 가능한 작업에서만 무인 실행 권장.
- **Billing 서프라이즈**: agentic 워크플로우는 flat subscription에서 API metering으로 이관 추세. 장기 `/goal` 세션은 토큰 소모 예측 어려움.
- **CI silent hang**: `--non-interactive` 없이 approval prompt 발생 시 런타임 무기한 소진.
- **보안 샌드박스**: macOS Seatbelt/Landlock/bwrap + 네트워크 default off. 규제 코드 작업 시 이 모드 활용.
- **스키마 추측 금지**: Codex 스킬/MCP/설정 경로는 버전별로 바뀔 수 있으므로 문서 추정 대신 실제 설치 위치와 `codex exec`로 검증한다.

자세한 비용·실패 모드 비교: [claude-code-vs-codex-economics](/insights/claude-code-vs-codex-economics.md)

## 관련 도구

- [claude-code](/tools/claude-code.md) — 대안 아젠틱 코딩 에이전트; 반대 실패 모드(context drift)
- [claude-code-vs-codex-economics](/insights/claude-code-vs-codex-economics.md) — 비용 10× 격차·실패 모드·MCP 브릿지 패턴
- [openai-agents-sdk](/tools/openai-agents-sdk.md) — Codex를 감싸는 OpenAI 에이전트 SDK
- openai — 제품 배경 (OpenAI 법인)
- [background-agent-n-kpi](/concepts/background-agent-n-kpi.md) — Goal 기반 장기 실행의 개념적 배경
- [generator-evaluator-architecture](/concepts/generator-evaluator-architecture.md) — Codex-Claude 크로스 리뷰 패턴의 아키텍처 근거
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md) — 아젠틱 실행의 컨텍스트 우선 원칙
