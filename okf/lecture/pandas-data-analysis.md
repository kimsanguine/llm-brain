---
type: lecture
title: 판다스 데이터 분석 — 그룹화·피벗·지도 시각화
description: 소상공인 업종 데이터를 대상으로 groupby, pivottable, Folium 지도 시각화를 실습한 강의 세션.
tags:
- data-tool
- data-analysis
- EDA
timestamp: '2026-05-26'
x-llmbrain-domain:
- teaching
- AI/LLM
x-llmbrain-created: '2026-05-15'
x-llmbrain-sources: []
x-llmbrain-distill_level: 0
x-llmbrain-access_count: 0
x-llmbrain-last_accessed: null
x-llmbrain-last_distilled: null
---

# 판다스 데이터 분석 — 그룹화·피벗·지도 시각화

## 핵심 요약

소상공인 업종 데이터를 대상으로 `groupby`, `pivot_table`, Folium 지도 시각화를 실습한 강의 세션. 지역별·업종별 분포 분석 인사이트를 도출하고, 포트폴리오 아이디어(여행지 추천, 챗봇)까지 연결.

## 상세 내용

### 그룹화 & 집계

- `groupby(['시도명', '대분류'])` 로 지역·업종 기준 집계
- `value_counts()`, `sum()`, `size()` 조합 사용
- `loc` 인덱싱으로 특정 지역(제주도 등) 필터링

```python
# 그룹화 + 집계
group_data = df.groupby(['시도명', '대분류'])
group_data['수치컬럼'].sum()

# 피벗 테이블 + 비율 변환
pivot = df.pivot_table(index='시도명', columns='대분류', values='윈도스')
(pivot.div(pivot.sum(axis=1), axis=0) * 100)
```

### 피벗 테이블

- `pivot_table` — 시도명 × 대지보명 교차 분석
- transpose(행/열 변환)로 지역 간 비교 용이
- 열 방향 합계 대비 백분율 계산

### 지도 시각화 (Folium / 오픈스트리트맵)

- VS Code 환경: 오픈스트리트맵 IP 차단 이슈 → Google Colab 사용 권장
- 서울 교육업종: 강남구 집중, 도로·교차로 주변 분포
- 관악구 미용실: 골목 분산 패턴 (교육업종과 상이)

### 분석 인사이트

| 지역/항목 | 특성 |
|---|---|
| 전국 공통 | 음식·소매 비율 압도적 |
| 제주도 | 음식·소매 + 숙박업 높음 |
| 서울 | 과학기술 업종 Top 3 진입 |
| 강원도 | 대체재 업종 다수 |
| 남성 매출 상위 | 수산물·컴퓨터가전·청과 |
| 치킨 매출 | 17시 이후 집중 |

### 강사 팁

- 데이터 변형 후 `head()`, `columns`로 반드시 결과 검증
- GS편의점 입점 = 시장성 검증 지표 (대기업 분석 활용)
- 따라 치기보다 복사-붙여넣기가 실질적
- EDA 인사이트를 비즈니스 전략으로 연결하는 역할은 [ai-pm-role](/concepts/ai-pm-role.md) 참조
- 데이터 분석 실습 후 ML로 넘어가는 커리큘럼 설계는 [andrew-ng](/people/andrew-ng.md) 강의 흐름을 참고하면 유용
- 반복적 EDA 작업 자동화에는 [claude-code](/tools/claude-code.md) 활용 가능 (쿼리 생성, 요약 리포트 작성)
- 수강생 실습 데이터 분석 사례 패턴은 teaching-lecture-patterns 참조

### 이슈

- 데이터프레임 변형 후 컬럼 수 변화(28개) 인식 누락 주의
- Folium: VS Code → Colab 전환으로 해결

## 관련 개념

- [ml-classification-algorithms](/lecture/ml-classification-algorithms.md)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [ai-pm-role](/concepts/ai-pm-role.md) (데이터 분석 → PM)
- ai-human-daily-brief-curriculum-signals
- [andrew-ng](/people/andrew-ng.md) (데이터 분석 → ML 진행 커리큘럼 레퍼런스)
- [claude-code](/tools/claude-code.md) (데이터 분석 자동화 — EDA 쿼리·리포트 생성)
- teaching-lecture-patterns (수강생 실습 데이터 분석 교수법)
