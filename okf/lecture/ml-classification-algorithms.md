---
type: lecture
title: 머신러닝 분류 알고리즘 & 성능 평가 지표
description: 이진 분류 문제 대상으로 4종 알고리즘(로지스틱 회귀, SVM, 나이브 베이즈, KNN)의 이론과 scikit-learn 코드를
  다룬 강의 + 오전 복습 퀴즈 세션.
tags:
- ml-classics
- ml-evaluation
- scikit-learn
timestamp: '2026-06-24'
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

# 머신러닝 분류 알고리즘 & 성능 평가 지표

## 핵심 요약

이진 분류 문제 대상으로 4종 알고리즘(로지스틱 회귀, SVM, 나이브 베이즈, KNN)의 이론과 scikit-learn 코드를 다룬 강의 + 오전 복습 퀴즈 세션. 혼동행렬 완전 정리와 Precision/Recall 트레이드오프가 핵심.

## 상세 내용

### 분류 알고리즘 4종 요약

| 알고리즘 | 핵심 포인트 |
|---|---|
| 로지스틱 회귀 | 시그모이드 함수로 0~1 확률 출력 / 0.5 임계값으로 클래스 결정 / 지도학습·분류 문제 |
| SVM | 결정 경계 마진 최대화 / 소프트 마진 = 오차 허용 / 고차원 데이터 강점 |
| 나이브 베이즈 | 피처 독립성 가정 / 스팸 필터링 등 텍스트 분류 적합 |
| KNN | K 이웃 다수결로 예측 / default K=5 / **학습이 필요 없는 유일한 전통 ML 알고리즘** (lazy learning) |

> 분류 문제의 이론 체계는 [andrew-ng](/people/andrew-ng.md) Coursera ML 강의가 표준 레퍼런스로 널리 사용됨.

### 고전 원전과 최신 정형 데이터 흐름

2026-06-23 AI Human 논문 세트는 이 강의의 SVM 설명을 원전 수준으로 보강한다. Cortes & Vapnik(1995)의 SVM은 결정 경계 자체보다 **경계 주변 마진을 최대화**하는 것이 일반화에 중요하다는 관점을 제시했고, 커널 트릭으로 비선형 고차원 분류를 가능하게 했다.

같은 세트의 Quinlan(1986) ID3는 엔트로피와 정보 이득으로 데이터를 분기하는 결정트리 원전이다. 이 관점은 단일 결정트리를 넘어 Random Forest, GBDT, XGBoost, LightGBM 계열까지 이어진다.

강의 연결 포인트는 [classical-ml-tabular-foundations](/concepts/classical-ml-tabular-foundations.md)다. 수강생에게 SVM/결정트리를 "옛날 알고리즘"으로 소개하기보다, TabPFN-2.5 같은 정형 데이터 파운데이션 모델이 무엇을 계승하고 무엇을 바꾸는지 보여주는 베이스라인으로 다루는 편이 좋다.

### scikit-learn 공통 패턴

```python
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 공통 4단계
model = LogisticRegression()     # 1. 모델 생성
model.fit(X_train, y_train)      # 2. 학습 (train만!)
predicted = model.predict(X_test) # 3. 예측
accuracy_score(y_test, predicted) # 4. 평가

# 혼동행렬 + 분류 리포트
print(confusion_matrix(y_test, predicted))
print(classification_report(y_test, predicted))
```

### 혼동행렬 (Confusion Matrix)

```
              모델 예측
              Positive    Negative
실제  Positive    TP          FN
      Negative    FP          TN
```

- **TP**: 실제 양성 → 양성 예측 (정답)
- **TN**: 실제 음성 → 음성 예측 (정답)
- **FP**: 실제 음성 → 양성 예측 (1종 오류)
- **FN**: 실제 양성 → 음성 예측 (2종 오류)

> 주의: 통계학 1종/2종 오류와 ML 표기 방향이 다를 수 있음. 시험에서는 학문 기준 확인 필요.

### 성능 평가 지표 공식

```
Accuracy   = (TP + TN) / (TP + TN + FP + FN)
Precision  = TP / (TP + FP)          # 모델 입장
Recall     = TP / (TP + FN)          # 현실 입장 (재현율)
FPR        = FP / (FP + TN)          # ROC 곡선 X축
F1         = 2 * (Precision * Recall) / (Precision + Recall)
AUC        = ROC 커브 아래 면적 (1에 가까울수록 좋음)
```

- Precision ↑ → Recall ↓ (트레이드오프)
- 불균형 데이터에서 Accuracy만 보면 절대 안 됨 → F1, Precision, Recall 병행
- `classification_report`로 클래스별 성능 확인 → 어떤 클래스를 혼동하는지 파악 가능

### 강사 팁

- `train_test_split` 권장: 슬라이싱보다 랜덤성 확보
- train 데이터로만 `fit`: test 섞으면 데이터 누수(data leakage)
- 학습 전 `value_counts()`로 클래스 불균형 사전 점검
- 소규모 데이터 100% Accuracy/Recall → 과소적합 가능성
- 분류 결과를 서비스 의사결정에 연결하는 시각은 [ai-pm-role](/concepts/ai-pm-role.md) 참조

### 실습 데이터셋

- **UCI 위조지폐**: 웨이블릿 변환 피처(분산, 왜도, 첨도, 엔트로피), SVM 결과 Accuracy 100%
- **Iris (붓꽃)**: 3클래스 다중 분류, 슬라이싱으로 train/test 분리
- 이미지 분류 SOTA 기점: [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) (2012년 ImageNet, SVM 대비 딥러닝 압승으로 분류 패러다임 전환)
- [karpathy](/people/karpathy.md) micrograd 시리즈는 분류기 역전파를 밑바닥부터 구현하는 대표 학습 자료

## 관련 개념

- [pandas-data-analysis](/lecture/pandas-data-analysis.md)
- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- [adsp-exam-prep](/lecture/adsp-exam-prep.md)
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [ai-pm-role](/concepts/ai-pm-role.md)
- ai-paper-learning-path
- [classical-ml-tabular-foundations](/concepts/classical-ml-tabular-foundations.md)
- [andrew-ng](/people/andrew-ng.md) (ML 강의 표준 — 로지스틱 회귀·비용함수 원점)
- [karpathy](/people/karpathy.md) (역전파 직접 구현 — 분류기 내부 이해)
- [alexnet-imagenet-2012](/papers/alexnet-imagenet-2012.md) (분류 SOTA 전환점 — 전통 ML → 딥러닝)
