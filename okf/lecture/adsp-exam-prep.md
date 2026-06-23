---
type: lecture
title: ADsP 시험 준비 — 출제 빈도 전략 및 핵심 개념 정리
description: ADsP(데이터분석 준전문가) 자격증 대비 특강.
tags:
- data-analysis-cert
- ml-classics
- ml-evaluation
- data-analysis
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

# ADsP 시험 준비 — 출제 빈도 전략 및 핵심 개념 정리

## 핵심 요약

ADsP(데이터분석 준전문가) 자격증 대비 특강. 23~24년 기출 기반 출제 빈도 분석으로 3주 합격 전략을 제시. 3과목(데이터 분석)이 전체의 약 80%를 차지하며, 군집·연관·회귀·성능평가가 매 회차 출제됨.

## 상세 내용

### 시험 구조

- 과목: 1과목(데이터 이해), 2과목(데이터 분석 기획), 3과목(데이터 분석)
- 문항: 50문제, 60점(30문제) 이상 합격
- 연 4회 시행

### 머신러닝 전체 구조 (시험 범위)

```
머신러닝
├── 지도학습 (Y값 있음)
│   ├── 회귀분석 (Y: 수치형) — 선형회귀, 릿지, 라쏘
│   └── 분류분석 (Y: 범주형) — 로지스틱회귀, 나이브베이즈, 판별분석
│   └── 겸용 — 의사결정나무, 랜덤포레스트, KNN, SVM, 인공신경망, 앙상블
└── 비지도학습 (Y값 없음)
    ├── 군집분석
    │   ├── 계층적 (최단/최장/평균/와드 연결법)
    │   └── 비계층적 (K-평균, DBSCAN★)
    ├── 연관분석 (장바구니 분석)
    ├── 차원축소 (PCA, SOM, t-SNE, MDS)
    └── 시계열분석 (AR, MA, ARIMA)
```

★ DBSCAN: 비계층적이지만 군집 개수를 **미리 정하지 않음** — 기출 단골 예외 포인트

### 3과목 출제 빈도 TOP (전체의 ~80%)

| 순위 | 주제 | 핵심 키워드 |
|---|---|---|
| 1 | 선형회귀 + 로지스틱회귀 | 잔차 3가지 가정, 가설검정, VIF(다중공선성), R 결과 해석, 오즈비 |
| 2 | 군집분석 | K-평균, DBSCAN, 실루엣 지표, 계층적/비계층적 구분, 덴드로그램 |
| 3 | 연관분석 | 지지도, 신뢰도, 향상도 |
| 4 | 모델 성능평가 | 혼동행렬, R², MSE, MAE, F1 |
| 5 | 가설검정 | 귀무가설/대립가설, 검정통계량, p-value, 유의수준 |
| 6 | 의사결정나무 | 분할기준(범주형 vs 연속형 차이), 가지치기 |
| 7 | 인공신경망 | 과적합, 가중치, 기울기 소실, 드롭아웃, 활성화 함수 |
| 8 | 차원축소 | PCA(주성분 개수 선택법), SOM, MDS, t-SNE |
| 9 | 시계열분석 | 4가지 요인(추세/계절/순환/불규칙), AR/MA/ARIMA, 정상성, 백색잡음 |
| 10 | 앙상블 | 배깅/부스팅/스태킹, 부트스트랩 |

### 3과목 기타 출제 (~20%)

- 샘플링 방법 4가지 + 부트스트랩
- 데이터 척도 4가지 (명목/순서/등간/비율)
- 상자그림(boxplot) + 이상치 판별 (평균은 알 수 없음, 중앙값만 가능)
- 결측값 처리 방법
- 사례 기반 모델링 (상황 → 알고리즘 선택)

### 1과목 — 데이터 이해

- DIKW 피라미드
- 정형/비정형 데이터 구분
- 암묵지 vs 형식지
- 데이터베이스 4가지 특징
- 빅데이터 3V/4V/7V

### 2과목 — 데이터 분석 기획

- 분석 주제 유형 (최적화/솔루션/통찰/연관)
- 분석 방법론: KDD, CRISP-DM — 프로세스 순서 차이
- 분석 거버넌스 체계 구성요소
- 상향식 vs 하향식 접근법

### 데이터 분석 프로세스

| 단계 | 설명 |
|---|---|
| ① 데이터 탐색 | 형태·분포 확인 (기초통계) |
| ② 데이터 전처리 | 결측치 처리, 이상치 탐지, 척도 변환 |
| ③ 데이터 분할 | Train(80%) / Test(20%) 분리 |
| ④ 모델 학습 | Train → Train + Validation, 교차검증 |
| ⑤ 하이퍼파라미터 튜닝 | 성능 최적화 |
| ⑥ 모델 평가 | 예측값(ŷ) vs 실제값(y) |

### 3주 합격 전략

1. 출제 빈도 높은 주제부터 (군집→연관→회귀→성능평가 순)
2. 기출문제 + **보기까지** 꼼꼼히 학습 (출제자 의도 파악)
3. 빈도 낮은 주제는 나중에 보충
4. ADsP 합격 → 빅데이터 분석 기사 도전 검토
5. 학습 로드맵 설계 시 ai-paper-learning-path 참조
6. 이론 이해 심화는 [andrew-ng](/people/andrew-ng.md) Coursera ML (회귀·분류·클러스터링 기초 강의) 병행 권장
7. [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) 및 [ml-classification-algorithms](/lecture/ml-classification-algorithms.md) 을 선수 지식으로 먼저 정리

### 자주 나오는 함정

- "다른 것을 골라라" 유형
- DBSCAN = 비계층적이지만 군집 개수 미지정 (예외)
- 상자그림에서 **평균은 알 수 없음** (중앙값만 가능)
- R 분석 결과 해석 문제: 계수, p-value, R² 해독 능력 필요

## 관련 개념

- [ml-classification-algorithms](/lecture/ml-classification-algorithms.md) (분류 알고리즘 선수 지식)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md) (인공신경망·과적합 이론 연결)
- [pandas-data-analysis](/lecture/pandas-data-analysis.md) (데이터 탐색·전처리 실습 연결)
- [ai-pm-role](/concepts/ai-pm-role.md)
- ai-paper-learning-path
- ai-human-daily-brief-curriculum-signals
- [andrew-ng](/people/andrew-ng.md) (Coursera ML — 회귀·클러스터링 이론 원점)
