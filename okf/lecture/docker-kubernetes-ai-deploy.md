---
type: lecture
title: AI 서비스 배포 — Docker·K3D·Kubernetes 롤링 업데이트
description: AI 서비스 운영에서 Docker만으로는 부족한 이유를 설명하고, Kubernetes의 자동 복구·오토 스케일링·무중단 배포(롤링
  업데이트) 개념을 이론(1부)과 K3D 핸즈온 실습(2부)으로 구성한 강의.
tags:
- k8s-deploy
- deploy-strategy
- MLOps
- LLMOps
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

# AI 서비스 배포 — Docker·K3D·Kubernetes 롤링 업데이트

## 핵심 요약

AI 서비스 운영에서 Docker만으로는 부족한 이유를 설명하고, Kubernetes의 자동 복구·오토 스케일링·무중단 배포(롤링 업데이트) 개념을 이론(1부)과 K3D 핸즈온 실습(2부)으로 구성한 강의.

## 상세 내용

### AI 서비스의 특수성

- LLM 서버는 **상태 유지(stateful)**: GPU 메모리 상시 점유, 초기 로딩 필요
- 트래픽 피크 시 타임아웃/붕괴 위험
- 일반 API보다 요청 처리 비용이 훨씬 무거움

### Docker의 한계 (AI 서비스 관점)

| 문제 | 설명 |
|---|---|
| 자동 복구 없음 | 컨테이너 죽으면 그대로 장애 |
| 수동 스케일링 | 언제/몇 개 늘릴지 사람이 판단 |
| 배포 다운타임 | 구버전 내리고 신버전 올리는 사이 서비스 중단 |
| GPU 자원 쏠림 | 선점 컨테이너가 GPU 독점 |

### Kubernetes 핵심 개념

| 개념 | 설명 |
|---|---|
| Pod | 컨테이너를 감싸는 최소 실행 단위 |
| Deployment | Pod 관리자 — 개수 유지 + 배포 전략 |
| Service (svc) | Pod IP가 바뀌어도 고정 엔드포인트 제공 |
| Ingress | 외부 트래픽 입구 — 경로별 서비스 라우팅 |

- **자가 치유(Self-healing)**: Pod 죽으면 자동 재생성
- **오토 스케일링**: CPU/요청 수 메트릭 기반 자동 확장
- **선언형(Declarative)**: YAML에 목표 상태 선언 → Kubernetes가 자동으로 맞춤

### 배포 전략 3가지

| 전략 | 특징 | 단점 |
|---|---|---|
| 롤링 업데이트 | 기존 Pod 유지 + 신규 점진 교체 | 버전 혼재 구간 존재 |
| Blue/Green | 구버전 유지하며 신버전 전환 → 즉시 롤백 가능 | 리소스 2배 필요 |
| 카나리 | 트래픽 일부(10→50→100%)만 신버전으로 점진 이전 | 설정 복잡 |

### DevOps vs MLOps vs LLMOps

- **DevOps**: 서버 중심 운영 — HashiCorp Terraform·Vault 등 [mitchell-hashimoto](/people/mitchell-hashimoto.md) 가 정립한 인프라 as code 도구 기반
- **MLOps**: 모델 + 데이터 + 프롬프트 중심
- **LLMOps**: GPU 자원 관리, 프롬프트 버전 관리, 모델 서빙, 모니터링까지
  - 클라우드 모델 배포 시 anthropic (Claude API) 또는 openai (GPT API) 선택이 대표 결정 지점

### K3D 실습 — 롤링 업데이트

```bash
# 클러스터 생성
k3d cluster create demo --port "18080:80@loadbalancer" --agents 2
kubectl get nodes  # control-plane 1 + agent 2 = 총 3노드

# 이미지 빌드 → K3D 임포트 (필수 단계)
docker build -t rolling-app:demo .
k3d image import rolling-app:demo -c demo

# 배포
kubectl apply -f rolling-v1.yaml
kubectl get pods  # 3개 Running 확인

# 롤링 업데이트 실행
kubectl apply -f rolling-v2.yaml
kubectl get pods -w  # Pod 변화 실시간 관찰
```

롤링 업데이트 순서:
1. 신규 V2 Pod 생성 (Pending → ContainerCreating → Running)
2. 헬스 체크 통과 확인
3. 기존 V1 Pod 1개 Terminate
4. 위 과정 반복 × 3

### YAML 핵심 설정

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # 최소 2개 Pod 항상 유지
      maxSurge: 1         # 교체 중 최대 4개 허용
  template:
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - readinessProbe:   # 준비 안 된 Pod에 트래픽 차단
            httpGet:
              path: /health
              port: 8080
          lifecycle:
            preStop:        # 진행 중 요청 완료 후 종료
              exec:
                command: ["sleep", "5"]
```

### 트러블슈팅

| 이슈 | 원인 | 해결 |
|---|---|---|
| kubectl 연결 실패 | config 파일 server 주소 오류 | `host.docker.internal`로 수정 |
| curl 요청 404 | Service YAML 미적용 | 포트 포워딩 직접 설정 |

### 클라우드 AI 서비스 팁

- 자체 LLM 운영 부담이 크면 → AWS Bedrock / Azure AI 활용 권장
- agent 배포 인프라 설계 시 [claude-code-agent-system](/tools/claude-code-agent-system.md) 패턴과 함께 검토
- 경량 엣지 AI 배포 대안: [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) — K8s 없이 모바일/IoT에서 추론 가능
- agent 코드 실행 환경 격리 설계 참고: [swe-agent-aci](/tools/swe-agent-aci.md)

## 관련 개념

- [deep-learning-fundamentals](/lecture/deep-learning-fundamentals.md)
- 260515_100_agents
- [context-dealer-pattern](/concepts/context-dealer-pattern.md)
- [claude-code-agent-system](/tools/claude-code-agent-system.md) (agent 배포 인프라)
- [ai-pm-role](/concepts/ai-pm-role.md)
- [claude-code](/tools/claude-code.md)
- [mitchell-hashimoto](/people/mitchell-hashimoto.md) (HashiCorp 인프라 도구 — Terraform·Vault 출처)
- anthropic (Claude API — LLMOps 모델 배포 선택지)
- openai (GPT API — LLMOps 모델 배포 선택지)
- [swe-agent-aci](/tools/swe-agent-aci.md) (agent 코드 실행 환경 격리 설계)
- [mediapipe-google-ai-edge](/tools/mediapipe-google-ai-edge.md) (엣지 AI 배포 — K8s 대비 경량 대안)
