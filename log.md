# LLM Wiki — 실행 로그

> ingest / curate 실행 이력이 자동으로 기록된다. 직접 편집하지 않는다.

---

## 로그 형식

```
## YYYY-MM-DD HH:MM [명령어]
- 처리 raw: 파일 목록 (N개)
- 신규 wiki: 파일 목록 (N개)
- 갱신 wiki: 파일 목록 (N개)
- Ghost 추가: 개념 목록 (N개)
```

---

<!-- 로그 항목은 아래에 최신순으로 추가 -->

## 2026-05-15 [ingest — raw/til/ 49개 → insights/ 패턴 압축]
- 처리 raw: 2026-02-24.md~2026-04-26.md (실존 파일 40개, 목록 상 49개 중 누락 9개 제외)
- 신규 wiki: wiki/insights/remotion-video-patterns.md, wiki/insights/pptx-automation-patterns.md, wiki/insights/agent-build-harness.md, wiki/insights/youtube-dubbing-patterns.md, wiki/insights/teaching-lecture-patterns.md, wiki/insights/session-scribe-meeting-system.md, wiki/insights/claude-code-workflow.md (7개)
- 건너뜀: 2026-04-01.md, 2026-04-02.md, 2026-04-06.md, 2026-04-07.md, 2026-04-08.md, 2026-04-16.md, 2026-04-18.md, 2026-04-22.md, 2026-04-23.md, 2026-04-25.md (파일 없음)
- 클러스터 분류: remotion(3일) / pptx(4일) / agent-harness(4일) / youtube-dubbing(6일) / teaching(6일) / session-scribe(8일) / claude-code-workflow(6일)
- 갱신 wiki: index.md (총 페이지 30 → 37)
- Ghost 추가: 없음 (기존 ghost 목록 유지)

## 2026-05-15 [ingest — raw/meetings/clients/T3-TEACH/ 17개]
- 처리 raw: 2026-03-18_판다스데이터분석.md, 2026-03-19_이진분류와로지스틱회귀.md, 2026-03-19_머신러닝모델성능평가지표리뷰.md, 2026-03-25_AI서비스배포와쿠버네티스.md, 2026-03-25_도커K3D쿠버네티스설치.md, 2026-03-26_세션미완성.md, 2026-03-26_정기체크포인트회의.md, 2026-03-30-meetflow-summary.md, 2026-03-30_딥러닝기초_퍼셉트론.md, 2026-03-30_회의진행상황체크.md, 2026-03-31_테스트세션.md, 2026-04-01_CNN_합성곱신경망.md, 2026-04-26_ADsP시험준비특강.md, weekly_summary.md, weekly_summary_2026-05-04.md, weekly_summary_2026-05-11.md, weekly_summary_2026-05-14.md (17개)
- 신규 wiki: wiki/lecture/pandas-data-analysis.md, wiki/lecture/ml-classification-algorithms.md, wiki/lecture/docker-kubernetes-ai-deploy.md, wiki/lecture/deep-learning-fundamentals.md, wiki/lecture/adsp-exam-prep.md, wiki/projects/t3-teach-lecture-operations.md (6개)
- 통합된 raw: 3/19 x2 → ml-classification-algorithms, 3/25 x2 → docker-kubernetes-ai-deploy, 3/30 x2 + 4/1 → deep-learning-fundamentals, 4개 weekly_summary + 3/26 + 3/31 → t3-teach-lecture-operations
- 건너뜀: 2026-03-26_세션미완성.md (전사 없음), 2026-03-30_회의진행상황체크.md (타임스탬프만), 2026-03-31_테스트세션.md (시스템 테스트), weekly_summary_2026-05-04.md, weekly_summary_2026-05-11.md (회의 없음)
- 갱신 wiki: index.md (총 페이지 24 → 30)
- Ghost 추가: 없음

## 2026-05-15 [ingest — raw/blog/ 10개]
- 처리 raw: 2026-04-25-claude-code-agent-teams.md, 2026-04-28-what-is-claude-code.md, 2026-04-30-ai-pm-why-now.md, 2026-05-08-ai-pm-bottleneck-not-code.md, 2026-05-08-context-first-agent-orchestration.md, 2026-05-09-per-dollar-performance-model-routing.md, 2026-05-10-cognitive-surrender-ai-verification.md, 2026-05-11-agent-security-intent-parsing.md, 2026-05-12-agent-pricing-unit-competition.md, 2026-05-13-domain-depth-beats-model-performance.md (10개)
- 신규 wiki: wiki/tools/claude-code.md, wiki/concepts/ai-pm-role.md, wiki/concepts/context-first-agent-orchestration.md, wiki/concepts/model-routing-cost.md, wiki/concepts/ai-governance-verification.md, wiki/concepts/agent-pricing-model.md, wiki/concepts/vertical-agent-domain-depth.md (7개)
- 갱신 wiki: index.md (총 페이지 16 → 24)
- Ghost 추가: 없음 (기존 ghost 목록 유지)

## 2026-05-15 [ingest]
- 처리 raw: raw/context/business-profile.md, raw/context/products.md, raw/context/target-audience.md, raw/context/metrics.md, raw/til/2026-05-14.md, raw/til/2026-05-15.md, raw/blog/2026-04-25-claude-code-agent-teams.md (7개)
- 신규 wiki: wiki/business/habix-profile.md, wiki/projects/project-openclaw.md, wiki/projects/project-100-agents.md, wiki/insights/til-patterns-2026-05.md, wiki/concepts/context-dealer-pattern.md, wiki/tools/claude-code-agent-system.md (6개)
- 갱신 wiki: wiki/projects/project-llm-wiki.md (기존, 첫 번째 세션에서 생성)
- Ghost 추가: agent-memory-pattern, karpathy-llm-wiki-pattern, obsidian-graph-view, habix-universe, seo-geo-playbook (5개)
- 총 wiki 페이지: 7개

## 2026-05-15 16:16 [curate]
- orphan: 0개
- stale_links: 0개
- distilled: 0개
- archive 후보: 0개

## 2026-05-16 [ingest — URL 클리핑: OpenAI Realtime API 신규 모델 3종]
- 처리 raw: raw/clippings/2026-05-07-openai-realtime-api-new-models.md (1개, URL 스크랩)
- 신규 wiki: wiki/tools/openai-realtime-api.md, wiki/concepts/realtime-voice-ai-patterns.md (2개)
- 갱신 wiki: wiki/tools/whisper-ecosystem.md (GPT-Realtime-Whisper 섹션 추가 + 역링크)
- 갱신 index.md: 총 37 → 39페이지 (concepts 11→12, tools 4→5)
- Ghost 추가: 없음

## 2026-05-16 01:54 [curate]
- orphan: 0개
- stale_links: 10개
- distilled: 0개
- archive 후보: 0개
