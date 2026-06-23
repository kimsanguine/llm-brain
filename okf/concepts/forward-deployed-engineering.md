---
type: concept
title: Forward Deployed Engineering (FDE)
description: Forward Deployed Engineer는 frontier AI 제품을 고객사 환경 안에서 실제로 작동하게 만드는 "embedded
  builder" 역할이다.
tags:
- fde
- enterprise-ai
- pm-paradigm
- consulting
timestamp: '2026-06-10'
x-llmbrain-domain:
- AI/LLM
- business
x-llmbrain-created: '2026-05-22'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# Forward Deployed Engineering (FDE)

## 핵심 요약

**Forward Deployed Engineer**는 frontier AI 제품을 고객사 환경 안에서 실제로 작동하게 만드는 "embedded builder" 역할이다. 2026-05 기준 Google·OpenAI·Anthropic 3사 모두 FDE 채용을 가속 중이며, OpenAI와 Anthropic은 자체 채용 대신 **별도 외부 회사로 분사**해 처리하는 패턴을 채택했다. 2025년 핫 잡 1위가 2026년에도 지속.

## 작동 원리

### 직무 정의 (Google FDE 채용공고 풀이 — Pragmatic Engineer 해석)
- "founder's mindset" → 누구도 spec 안 줌, scope creep 본인 책임
- "high-agency" → 동원 가능한 자원 본인 외 없음
- "white glove" → 고객 제안에 "no" 금지
- "critical feedback loop to product roadmap" → 본사 PM이 티켓 일부 읽어줄지도

실 업무 비중 추정 (Pragmatic Engineer):
- 코딩 ~25% / 통합·plumbing ~50% / 미팅·고객 핸드홀딩 25%

### 3사 패턴 비교 (2026-05 시점)

| 회사 | 채용 방식 | 특징 |
|------|----------|------|
| Google | 자체 GTM 조직 신설 | 4-6회 인터뷰 → 2회/2일로 단축 |
| OpenAI | **OpenAI Deployment Company** 분사 | $4B PE 펀딩 ($14B valuation), 비투자자 partner role. Tomoro(UK FDE 150명) 첫 인수 |
| Anthropic | 무명 별도 FDE 컨설팅 회사 신설 | Blackstone·Hellman & Friedman·Goldman Sachs 펀딩 |

OpenAI·Anthropic 모델 = **외부 회사 분사 → 본사 모델 R&D 집중, FDE는 enterprise sales 첨병**. 단점: 분사 회사 FDE는 OpenAI/Anthropic 주식 미수령 → "core 인력 아님" 신호.

## 활용 사례

### 누구에게 좋은가
- 초기 경력 단계에서 Google/OpenAI/Anthropic을 이력서에 넣고 싶은 신입
- end-to-end 출하 즐기는, 모호성에 강한, outcome ownership 좋아하는 엔지니어
- 컨설팅 → 신입 학습 트랙으로서 의미 (전통적 tech consulting의 신입 entry-level 대체)

### 누구에게 안 맞는가
- 잘 엔지니어링된 시스템 빌드 + 시간 확보 선호
- greenfield 프로젝트 선호
- 장기 프로젝트 + 다른 SW 엔지니어와의 협업 선호

### 수요 증가 동력 (Pragmatic Engineer)
- **AI 랩**: 빠른 롤아웃 = 빠른 매출
- **AI 벤더**: AI 제품 통합·도입 영업
- **non-AI 기업**: AI transformation 위한 사내 FDE 채용
- **non-AI 벤더**: SaaS도 FDE 채용으로 대형 고객 deal close

### 2026-06-09 보강: 채용 시장 데이터에서 FDE가 프리미엄 롤로 확인

Pragmatic Engineer 2026 job market part 2 raw는 FDE를 더 이상 특이한 frontier lab 직무가 아니라 AI 시대 프리미엄 채용 카테고리로 기록한다. 모바일·프론트엔드 직함은 줄고, AI engineering과 FDE 수요는 급증한다. Anthropic은 취업 후보자 선호도 1위로 언급되고, OpenAI와 함께 경쟁이 가장 치열한 회사군으로 분류됐다.

신입/인턴 채용이 줄어드는 흐름과도 연결된다. 대형 기술 기업 인턴십이 이전 대비 절반 수준으로 줄고, 업무·교육 배경의 중요도가 커진다면, 신입 개발자의 포지셔닝은 "일반 프론트엔드/모바일"보다 AI 도구 활용, 고객 문제 이해, 통합 구현 능력을 묶은 FDE형 포트폴리오가 더 강하다. 강의에서는 FDE를 단순 직무 소개가 아니라 ai-workforce-restructuring 이후의 entry-level 대체 경로로 설명하는 편이 현실적이다.

## habix/강의와의 연결점

- T3-TEACH 수강생 진로 상담: "AI 시대 신입 일자리" 질문에 대한 새 답변 카드. CS 전공이지만 frontier lab 본 채용 통과 어려운 학생에게 FDE 경로 추천 (단, 컨설팅 성격 인지 필요)
- Lenny 2026-05-21 "You'll lose your job in 2027" (Elena Verna)와 같은 큰 메시지: **현 역할은 만료일 가까움 — 변형·축소·소멸 가정**. 디자이너 인터뷰(Maily, 강영화/엘스 공동창업자)도 같은 결: AI로 생산성 폭발 시대에 오히려 화이트보드·손 스케치를 더 쓰며 "사람 이해"를 차별화로
- habix.ai 컨설팅 제품(이미 habix-profile Context Dealer 포지셔닝)과 직접 인접 — FDE 산업화는 컨설팅 + AI 통합 시장의 표준화를 보여줌

## 관련 개념
- [ai-pm-role](/concepts/ai-pm-role.md)
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [pm-agency-ai-era](/concepts/pm-agency-ai-era.md)
- [team-decision-structure-agent-era](/concepts/team-decision-structure-agent-era.md)
- habix-profile
