---
type: concept
title: Code-native Visual AI
description: Visual AI의 다음 프론티어는 완성 픽셀을 바로 생성하는 것이 아니라, 픽셀을 만드는 편집 가능한 코드 아티팩트를 생성하는
  방향이다.
tags:
- visual-ai
- code-generation
- render-loop
- design-tools
timestamp: '2026-06-03'
x-llmbrain-domain:
- AI/LLM
- design
- developer-tools
x-llmbrain-created: '2026-06-03'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Code-native Visual AI

## 핵심 요약

Visual AI의 다음 프론티어는 완성 픽셀을 바로 생성하는 것이 아니라, 픽셀을 만드는 **편집 가능한 코드 아티팩트**를 생성하는 방향이다. SVG, HTML/CSS, React 컴포넌트, Lottie JSON, Blender 스크립트, USD 장면 그래프처럼 소스가 남는 결과물은 버전 관리, 테스트, 재사용, 소프트웨어 스택 통합이 가능하다.

## 작동 원리

핵심 루프는 **Code → Render → Inspect → Revise**다.

1. **Code**: SVG path, CSS rule, Lottie timing, Blender script 같은 구조화된 소스 생성
2. **Render**: 브라우저, SVG 렌더러, Lottie 플레이어, Blender, 게임 엔진에서 실제 결과 확인
3. **Inspect**: 레이아웃 오류, 계층 구조, 관절 동작, 반응형 상태, 타이밍을 검사
4. **Revise**: 새 이미지를 다시 뽑는 것이 아니라 소스의 어느 부분을 바꿀지 수정

픽셀 네이티브 생성은 사실감, 질감, 조명에는 강하지만 수정 피드백이 전역적이고 부정확하다. 코드 네이티브 생성은 시도마다 소스 아티팩트 자체가 개선되므로 test-time compute의 이익이 더 직접적으로 쌓인다.

## 활용 사례

### 2D 디자인

브라우저 런타임은 HTML/CSS, React 컴포넌트, DOM inspection을 피드백 환경으로 만든다. UI 생성 에이전트는 단순 스크린샷이 아니라 hover, responsive breakpoint, layout overflow 같은 상태를 검사할 수 있다. 이 패턴은 [agent-build-harness](/insights/agent-build-harness.md)의 UI assertion과 직접 연결된다.

### 모션 애니메이션

Lottie JSON은 레이어, 벡터 도형, 키프레임, 타이밍 커브를 코드로 표현한다. OmniLottie류 접근은 원시 JSON을 모델 친화적인 커맨드 시퀀스로 바꿔, 애니메이션 생성도 렌더-검사-수정 루프로 다룰 수 있음을 보여준다.

### 3D 에셋

3D는 code-native 접근의 가치가 가장 크다. 게임/시뮬레이션에서는 보기 좋은 이미지보다 올바른 지오메트리, 재질, 파트 계층, 관절, 장면 맥락이 중요하다. 문과 힌지는 열려야 하고, 서랍은 밀려야 하며, 바퀴는 회전해야 한다. VIGA와 Articraft3D류 접근은 Blender나 시뮬레이터를 피드백 환경으로 삼아 시맨틱 도구와 이전 시도 메모리를 결합한다.

## habix/강의와의 연결점

이 개념은 디자인 자동화를 이미지 생성 도구 선택 문제가 아니라 **런타임을 가진 생성물 설계** 문제로 바꾼다. 프론트엔드 강의나 에이전트 빌드 강의에서는 "예쁜 결과"보다 "검사 가능한 결과"가 더 중요하다. 브라우저, Blender, 게임 엔진 같은 렌더러는 최종 출력 도구가 아니라 에이전트가 학습하고 수정하는 평가 환경이다.

PM 관점에서는 도메인별 wedge가 런타임에서 갈린다.

| 런타임 | 생성 아티팩트 | 제품 wedge |
|---|---|---|
| 브라우저 | HTML/CSS, React | UI 빌더, 프로토타입, QA |
| SVG 렌더러 | 벡터 그래픽 | 로고, 다이어그램, 아이콘 |
| Lottie 플레이어 | Lottie JSON | 모션 디자인 |
| Blender/게임 엔진 | 3D scene/script | 게임, 시뮬레이션, 디지털 트윈 |
| 시뮬레이터 | 물리 기반 articulation | 로보틱스, physical AI |

## 관련 개념

- [agent-build-harness](/insights/agent-build-harness.md)
- agent-evaluation-frameworks
- [context-first-agent-orchestration](/concepts/context-first-agent-orchestration.md)
- [physical-ai-world-model](/concepts/physical-ai-world-model.md)
- [video-pipeline-comparison](/concepts/video-pipeline-comparison.md)
- [remotion-video-patterns](/insights/remotion-video-patterns.md)
