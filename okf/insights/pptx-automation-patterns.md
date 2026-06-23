---
type: insight
title: PPTX 자동화 제작 파이프라인 패턴
tags:
- pptx
- video-pipeline
- gemini
- multi-agent
timestamp: '2026-05-15'
x-llmbrain-domain:
- tools
- AI/LLM
- teaching
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# PPTX 자동화 제작 파이프라인 패턴

## 핵심 원칙

PPTX 자동화는 원본 분석 → AI 보정 → PptxGenJS 코드 생성 → 이미지 삽입 → 다중 에이전트 검수의 5단계 파이프라인. 이미지 유형별로 최적 도구를 라우팅하는 것이 핵심.

## 발견된 패턴

### 7명 팀 구성 패턴 (2026-03-15)
- ①비전분석 ②OCR ③AI전문가 ④엔지니어 ⑤Gemini디자이너 ⑥발표자검수 ⑦원본대조
- 에이전트 배치: 컨텍스트 30장 이하로 제한 (이미지 PDF 기준)

### 멀티 에이전트 크로스체크 패턴 (2026-03-15)
- 동일 자료를 2명 이상 독립 에이전트가 검토하면 단일 판단 대비 판정 반전율 ~35%
- 텍스트 분석 → 이미지 검증 2단계 파이프라인이 가장 효과적

### 이미지 유형별 최적 도구 라우팅 (2026-03-21)
- **개념 이미지** → AI 이미지 생성 (Ideogram V2 DESIGN 모드)
- **수학 차트** → Chart.js (AI 이미지로 수학 차트 그리면 오류 빈발)
- **다이어그램** → PptxGenJS Shape (코드 기반이 AI보다 나은 경우 많음)
- Ideogram V2 DESIGN 모드가 프레젠테이션 이미지에 최적

### RALPH Loop 품질 개선 사이클 (2026-03-21)
- 정량 평가 기준 설정 → 병렬 에이전트 수정 → 빌드 → 재평가 → 90점 미만 있으면 반복
- 8명 전문가 평가 체계 + 5라운드 반복 → 전원 90점+ 달성 사례
- 관대한 평가 기준은 품질 향상을 막음
- 가장 낮은 점수 영역부터 수정

### 작업 유형별 Phase 분리 (2026-03-15)
- Week별 분리보다 작업 유형별 Phase 분리가 효율적
- 유지 → 변경 → 신규 순서로 처리 (같은 성격 작업 배치 처리)
- 예: 유지 72건 → 변경 52건 → 신규 526건

### PyMuPDF PDF 텍스트 추출 (2026-03-15)
- `pip install PyMuPDF` → `import fitz`
- 대규모 PDF(687장) 전량 텍스트 추출 가능
- 단, 다이어그램 내부 라벨은 누락 가능

### Gemini 이미지 생성 API 변경 (2026-03-15)
- `gemini-2.0-flash-exp-image-generation` → 폐기(404)
- 현재 사용 모델: `gemini-2.5-flash-image`
- `responseModalities: ['TEXT', 'IMAGE']` 설정 필수

### HTML-first 슬라이드 파이프라인 (2026-04-05)
- 4-agent 파이프라인: Orchestrator / Researcher / Designer / Evaluator
- DOCX 임포트 기능: Bold-pattern 헤딩 감지로 스타일 없는 DOCX 지원
- mammoth Bold 파싱: `^(\d+)(\.\d+)?` 정규식으로 챕터/섹션 레벨 구분
- slides-grab: `--mode capture --resolution 2160p` PDF 4K 출력

### Chart.js 서버사이드 렌더링 (2026-03-21)
- `chartjs-node-canvas` 패키지로 서버에서 PNG 생성 가능
- sigmoid, 포아송, SVM, scaling law 등 수학 차트에 적합

## 적용 방법

1. **분석 단계**: PyMuPDF 전량 텍스트 추출 + 비전 에이전트 이미지 검증
2. **분류 단계**: 유지/변경/신규 Phase 분리 + 이미지 유형 분류(AI/Chart.js/Shape)
3. **생성 단계**: PptxGenJS 엔진 + Gemini 이미지 API + Chart.js 차트
4. **검수 단계**: RALPH Loop (정량 기준 → 병렬 수정 → 재평가 → 반복)
5. **완료 기준**: 8명 이상 전문가 평가 전원 90점+

## 관련 개념
- [claude-code-agent-system](/tools/claude-code-agent-system.md)
- 260515_100_agents
- til-patterns-2026-05
- [remotion-video-patterns](/insights/remotion-video-patterns.md)
- teaching-lecture-patterns
- claude-code-workflow
- [claude-code](/tools/claude-code.md) — 4-agent / 7-agent 파이프라인 오케스트레이션 실행 환경
- [karpathy](/people/karpathy.md) — 교육 자료 제작에서 AI 도구 활용 방식 참조
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) — 수학 차트(sigmoid, 포아송, SVM, scaling law) 개념 출처
- [agent-paradigm-evolution](/concepts/agent-paradigm-evolution.md) — 멀티 에이전트 크로스체크 패턴의 기술적 배경
- [gemini-omni-flash](/tools/gemini-omni-flash.md) — Gemini 이미지 생성 API (`gemini-2.5-flash-image`) 사용 모델
