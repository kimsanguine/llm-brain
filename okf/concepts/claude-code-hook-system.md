---
type: concept
title: Claude Code Hook 시스템
description: Claude Code의 hook은 settings.json에 정의된 자동화 트리거로, 세션 시작 시점의 스냅샷만 로드된다.
tags:
- claude-code
- hook
- harness
timestamp: '2026-06-04'
x-llmbrain-domain:
- AI/LLM
- tools
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 1
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Claude Code Hook 시스템

## 핵심 요약

Claude Code의 hook은 `settings.json`에 정의된 자동화 트리거로, 세션 시작 시점의 스냅샷만 로드된다. 세션 중 수정은 현재 세션에 즉시 반영되지 않는다.

## 상세 내용

### Hook 활성화 동작 방식

- Hook은 **세션 시작 시점의 `settings.json` 스냅샷**만 로드한다
- 세션 중 hook 추가·수정 → 현재 세션에 반영되지 않음
- 활성화 방법: `/hooks` 메뉴를 한 번 열어 설정 리로드, 또는 Claude Code 재시작

### PreCompact Hook

- stdin JSON에 `session_id` 포함
- transcript JSONL 경로: `~/.claude/projects/<sanitized-cwd>/<session_id>.jsonl`
- cwd별로 프로젝트 폴더가 다르므로 `ls ~/.claude/projects/*/${sid}.jsonl` 글로브로 cwd 무관 탐색 권장

### macOS 알림 패턴

- `osascript display notification` = 배너 + 사운드 단일 명령
- 별도 `afplay` 불필요. `sound name "Ping"` 형식으로 지정
- DND(방해 금지) 상태: 배너는 숨겨지지만 사운드는 재생됨

### Hook 구축 5단계 검증

1. dedup check (중복 방지)
2. 명령어 raw 구성
3. stdin 파이프 테스트 (exit code + side effect 확인)
4. JSON 병합
5. `jq -e`로 schema 검증 → 실제 발화 증명

중간 단계를 건너뛰면 silent 실패로 디버깅 비용이 커진다.

### 분기 기준: Hook vs Skill vs CLAUDE.md

- **Hook**: 결정적 트리거가 필요한 자동 행동 ("매 저장 후 lint", "특정 명령 차단"). 모델 추론이 아닌 harness가 실행
- **Skill**: 사용자가 호출했을 때만 실행되는 재사용 작업 묶음
- **CLAUDE.md**: 모든 세션·모든 작업에 항상 적용되는 원칙

### 2026-06-02 보강: LLM Wiki 적용 사례

인프런 Obsidian × Claude 강의 업데이트는 Claude Hook을 LLM Wiki 운영에 직접 연결했다. 두 실습이 특히 중요하다.

- **데일리 노트 자동 컨텍스트 주입**: 오늘 날짜의 데일리 노트를 세션 시작 시 자동으로 포함해, 사용자가 매번 컨텍스트를 수동 주입하지 않게 한다.
- **raw 폴더 하위 보호**: ingest 전 원본 파일이 담긴 `raw/` 폴더를 hook으로 보호해, LLM 컴파일러가 원본을 실수로 수정하는 사고를 막는다.

이 둘은 hook의 역할을 잘 보여준다. 모델이 "조심하겠다"고 약속하는 것보다, 실행 전후 경계를 자동으로 검사하는 구조가 더 믿을 만하다. [260515_llm_wiki](/projects/260515_llm_wiki.md)의 raw 읽기 전용 원칙은 문서 가드레일이면서 동시에 hook으로 강화할 수 있는 실행 가드레일이다.

### 2026-06-04 보강: load-once 설정 반영 검증

글로벌 `CLAUDE.md` 개정 작업은 규칙 파일이 세션 시작 시 한 번 로드된다는 점을 확인했다. 디스크 파일을 바꿔도 현재 세션과 이미 생성된 서브에이전트는 stale snapshot을 유지할 수 있다. 따라서 hook/settings/CLAUDE류 설정을 수정한 뒤에는 "파일에 저장됨"과 "런타임에 반영됨"을 분리해서 보고한다.

검증 패턴은 3단계다. 첫째 디스크 grep으로 저장 상태를 확인한다. 둘째 독립 프로세스나 서브에이전트로 새 로드 여부를 확인한다. 셋째 새 최상위 세션이 규칙을 실제 인용하거나 행동으로 반영하는지 본다. 이 원칙은 til-patterns-2026-05의 설정 변경 검증 패턴과 연결된다.

## 관련 개념
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- [agent-harness-pattern](/concepts/agent-harness-pattern.md)
- [260515_llm_wiki](/projects/260515_llm_wiki.md)
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
