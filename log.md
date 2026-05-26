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

## 2026-05-26 07:01 [daily-cron sync_raw + ingest]
- sync_raw: 실행 완료
- 처리 raw: 3개
  - raw/clippings/news-2026-05-25.md
  - raw/clippings/paper-2026-05-25-advanced-rag-self-rag-corrective-rag-rag.md
  - raw/meetings/clients/T3-TEACH/weekly_summary_2026-05-25.md
- 신규 wiki: 없음 (0개)
- 갱신 wiki: 4개
  - wiki/insights/ai-human-daily-brief-curriculum-signals.md — Ch05 음성 AI의 액션·검증·저지연 검색 신호 보강
  - wiki/insights/ai-paper-learning-path.md — Advanced RAG 세트(HyDE/IRCoT/GraphRAG) 추가
  - wiki/projects/t3-teach-lecture-operations.md — 2026-05-25 신규 회의 없음 상태와 기존 데모 보강 처방 유지
  - index.md — 마지막 갱신일 및 관련 설명 갱신
- Ghost 추가: 없음
- 클러스터링 결정: 3개 raw 모두 기존 압축 노드에 귀속. 개별 신규 페이지 생성 기준보다 기존 커리큘럼/프로젝트 노드 보강 가치가 큼.

## 2026-05-25 07:09 [CCR daily sync_raw + curate(월요일)]
- sync_raw: 총 0개 파일 복사 (til 0, meetings 0, newsletters 0, context 0, blog 0, llm-brain-private git 0, ai_human 0)
- ingest: 새 파일 없음 → 건너뜀
- curate --audit --lifecycle: 56개 페이지 분석, 리포트 `wiki/curate_report.md` 갱신
  - Orphan: 0개
  - Stale 링크: 12개 (사용자 확인 필요 — `wiki/insights/til-patterns-2026-05.md` 외 5개 페이지에 끊긴 wikilink)
  - Distill 큐 추가: 0개
  - Lifecycle archive/delete 후보: 0개

## 2026-05-25 07:00 [daily-cron sync_raw + ingest]
- sync_raw: 총 14개 파일 복사 (til 1, meetings 1, newsletters 1, context 0, blog 7, llm-brain-private git 4, ai_human 0)
- 처리 raw: 10개
  - raw/blog/2026-05-19-agentic-model-default-routing.md
  - raw/blog/2026-05-20-observation-memory-agent-design.md
  - raw/blog/2026-05-21-ai-compound-growth-principles.md
  - raw/blog/2026-05-22-ai-acceleration-team-type-gap.md
  - raw/blog/2026-05-22-best-agent-worst-orchestrator.md
  - raw/blog/2026-05-23-sovereign-edge-ai-beyond-cloud.md
  - raw/blog/2026-05-25-multi-ai-pm-workflow.md
  - raw/clippings/2026-05-24.md
  - raw/clippings/news-2026-05-24.md
  - raw/clippings/paper-2026-05-24-rag-architecture-optimization-rag.md
- 신규 wiki: 없음 (0개)
- 갱신 wiki: 8개
  - wiki/concepts/model-routing-cost.md — 비용/성능 기준을 비용/에이전틱 점수와 task completion rate로 확장
  - wiki/concepts/context-first-agent-orchestration.md — 관찰/작업/승격 메모리와 컨텍스트 승격 기준 추가
  - wiki/concepts/ai-pm-role.md — AI 복리 워크플로우, 팀별 가속 격차, 멀티 AI PM 운영 추가
  - wiki/concepts/team-decision-structure-agent-era.md — 잘하는 에이전트 vs 좋은 오케스트레이터 구분 및 영역별 자율화 기준 추가
  - wiki/concepts/vertical-agent-domain-depth.md — 소버린/엣지 AI와 Where-to-Run 설계 변수 추가
  - wiki/insights/claude-code-vs-codex-economics.md — Codex+Claude 멀티 AI PM workflow 보강
  - wiki/insights/ai-human-daily-brief-curriculum-signals.md — Ch05 음성 AI 제품화 사례(구삐/Gemini/SynthID/Airbnb/Exa) 추가
  - wiki/insights/ai-paper-learning-path.md — RAG architecture optimization 세트(RETRO/Atlas/Gupta survey) 추가
- Ghost 추가: 없음
- 클러스터링 결정: blog 7개와 AI Human 3개는 기존 압축 노드에 귀속. 개별 신규 페이지 생성 기준(동일 개념 3회 이상 독립 등장)보다 기존 노드 보강 가치가 큼.

## 2026-05-24 07:08 [daily-cron sync_raw + ingest]
- sync_raw: 총 0개 파일 복사 (til 0/57, meetings 0/20, newsletters 0/8, context 0/7, blog 0/15, llm-brain-private 0/54, ai_human 0/263) — 새 파일 없음
- 처리 raw: 0개 (미처리 파일 없음)
- 신규 wiki: 없음
- 갱신 wiki: 없음
- 비고: 일요일이라 curate 단계 건너뜀 (월요일에만 실행)

## 2026-05-24 07:00 [daily-cron sync_raw + ingest]
- sync_raw: 총 9개 파일 복사 (til 3, meetings 1, newsletters 1, llm-brain-private git 4)
- 처리 raw: 4개
  - raw/clippings/2026-05-23.md
  - raw/clippings/news-2026-05-23.md
  - raw/clippings/paper-2026-05-23-dense-retrieval-embedding-search-rag.md
  - raw/til/2026-05-24.md
- 신규 wiki: 없음 (0개)
- 갱신 wiki: 4개
  - wiki/insights/ai-human-daily-brief-curriculum-signals.md — Ch05 음성 AI 제품화 지표(구삐/Gemini/SynthID/Exa/Airbnb) 추가 + sources 2개
  - wiki/insights/ai-paper-learning-path.md — Dense Retrieval / Embedding Search 세트(BEIR/ColBERT/NV-Embed) 추가 + sources 1개
  - wiki/insights/til-patterns-2026-05.md — habix-legal production 100%, Vercel webhook drift, Next.js 16 Suspense, pydantic-settings 빈 env, 멀티에이전트 fix 통합 패턴 추가
  - index.md — 마지막 갱신일 및 관련 설명 갱신
- Ghost 추가: 없음
- 클러스터링 결정: 새 raw 4개는 기존 압축 노드 3개에 귀속. 개별 신규 페이지 생성 기준(동일 개념 3회 이상 독립 등장) 미충족.

## 2026-05-22 14:32 [daily-cron sync_raw + ingest]
- sync_raw: llm-brain-private git 22개 복사 (til/meetings/newsletters/context/blog 모두 unchanged)
- 처리 raw: 21개
  - newsletters 19개: 2026-05-21 (chatdaeri-claude-memory, cooldeepai-claude-connectors, cooldeepai-cowork-setup, diamantai-claude-code-vs-codex-cli, eoeoeo-startup-vs-bigcorp, lenny-you-will-lose-job-2027, maily-ai-era-designer, mitkr-china-ai-short-drama, newcomer-spacex-ipo-orbital, newneek-chatgpt-vs-claude, pragmaticengineer-fde, retn-ai-server-security, secondbrush-gemini-omni-flash-vs-seedance, thehiddenrich-newsletter-media, bytebytego-async-patterns), 2026-05-22 (coffeepot-ai-video, tability-agentic-okr, themiilk-kakao-founder-chatgpt)
  - notes 2개: ece7115-multimodal-vlm, nexu-io-open-design
- 신규 wiki (3개):
  - wiki/tools/gemini-omni-flash.md (Google I/O 2026-05-19 omnimodal 모델)
  - wiki/concepts/forward-deployed-engineering.md (Google/OpenAI/Anthropic FDE 산업화)
  - wiki/insights/claude-code-vs-codex-economics.md (10× 비용 격차 + MCP planner-reviewer 표준)
- 갱신 wiki (4개):
  - wiki/concepts/omnimodality.md — Gemini Omni Flash 후속 사례 섹션 + sources 2개 추가
  - wiki/insights/claude-code-workflow.md — Claude 메모리 점검 워크플로우, Connectors 7개, Cowork 진입 패턴, Agentic OKR (Tability MCP) 4 섹션 추가 + sources 4개 추가
  - wiki/insights/til-patterns-2026-05.md — 보안 7체크/AI 영상 표준/구글 광고 변곡점/FDE 산업화/카카오 ChatGPT 이탈/단발성 5건/도구 노트 2건 산업 신호 섹션 추가 + sources 11개 추가
  - index.md — 페이지 카운트 51→54, ghost 5→9
- Ghost 신규 4개: seedance-2.0, chatgpt-image-2.0, nexu-io-open-design, tability-mcp
- 클러스터링 결정:
  - 5건 Claude 워크플로우 → 기존 claude-code-workflow.md 갱신 (신규 페이지 분리 안 함; raw 출처 부족한 단발성)
  - 4건 FDE/잡 변화 → 신규 forward-deployed-engineering.md (Lenny/Maily/eoeoeo는 보조 source로 인용)
  - 2건 AI 영상 → 신규 gemini-omni-flash.md (Seedance 2.0은 ghost) + til-patterns 보조 섹션
  - 단발성 5건 (카카오/중국숏드라마/SpaceX/Tangle/ByteByteGo)은 til-patterns "산업 신호" 섹션에 짧은 라인으로 통합
- 게이트: G-1 (1차 raw 출처 기재 완료), TK-014 patterns
- 후속: monday curate --lifecycle 시 til-patterns-2026-05의 산업 신호 섹션 lifecycle 압축 후보

## 2026-05-22 09:11 [daily-cron sync_raw]
- 처리 raw: 0개 (til 55 / meetings 20 / newsletters 8 / context 7 / blog 15 모두 unchanged)
- 신규 wiki: 0개
- 갱신 wiki: 0개
- ingest 스킵 (새 파일 없음)
- lifecycle/audit 스킵 (오늘 금요일 — 월요일 trigger 아님)

## 2026-05-22 [curate --graph]
- 분석 대상: 46개 페이지 (이전 그래프: 41개, delta +5)
- 신규 허브 진입: agent-build-harness (4→7), single-vs-multi-agent (3→6)
- 허브 총계: 12 → 14개
- 합성 후보: PM 3부작 클러스터 (pm-agency-ai-era+team-decision-structure-agent-era+background-agent-n-kpi → insights/pm-era-agent-leverage.md), OpenAI 실행환경 클러스터 (openai-agents-sdk+agent-harness-pattern+context-first → insights/execution-environment-patterns.md)
- stale 링크: 0개
- graph_report.md 갱신 완료

## 2026-05-22 [ingest — URL 클리핑: OpenAI Agents SDK 진화 (2026-04-15)]
- 처리 raw: raw/clippings/2026-04-15-openai-agents-sdk-next-evolution.md (1개, URL 스크랩)
- 신규 wiki: wiki/tools/openai-agents-sdk.md (1개)
- 갱신 wiki: wiki/concepts/agent-harness-pattern.md (관련 개념에 [[openai-agents-sdk]] 링크 추가), index.md (tools 5→6개, 총 45→46개)
- 반영 내용: SandboxAgent + Manifest 추상화, 실행환경·컴퓨팅 분리 3원칙(보안·안정성·확장성), 스냅샷/복원, 샌드박스 파트너 7종, MCP·skills·AGENTS.md 기본 구성요소 통합
- Ghost 추가: 없음
- 게이트: G-1 (1차 소스 예외 적용), TK-014 promote

## 2026-05-21 07:01 [ingest — 일일 sync: TIL 2026-05-21 반영]
- 처리 raw: raw/til/2026-05-21.md (1개)
- 신규 wiki: 없음 (0개)
- 갱신 wiki: wiki/insights/claude-code-workflow.md, wiki/insights/til-patterns-2026-05.md, index.md (3개)
- 반영 내용: Claude Code settings.json 키 검증(remoteControlAtStartup), IDE 실행 경로별 설정 적용 한계, /wrapup MEMORY.md 업데이트 후보의 HITL 3지선다 패턴
- Ghost 추가: 없음

## 2026-05-20 07:01 [ingest — 일일 sync: TIL 2026-05-20 반영]
- 처리 raw: raw/til/2026-05-20.md (1개)
- 신규 wiki: 없음 (0개)
- 갱신 wiki: wiki/business/habix-profile.md, wiki/insights/til-patterns-2026-05.md, index.md (3개)
- 반영 내용: habix.ai 후기 6건 승인 및 사이트/JSON-LD 실데이터 반영, footer © 1970 버그의 정적 export Date 초기화 폴백 패턴
- Ghost 추가: 없음

## 2026-05-19 07:01 [ingest — 일일 sync: eval 설계 + T3 주간요약 + TIL 2026-05-19 반영]
- 처리 raw: raw/blog/2026-05-18-pm-evaluation-design-mindset.md, raw/meetings/clients/T3-TEACH/weekly_summary_2026-05-18.md, raw/til/2026-05-19.md (3개)
- 신규 wiki: 없음 (0개)
- 갱신 wiki: wiki/concepts/ai-pm-role.md, wiki/concepts/agent-harness-pattern.md, wiki/concepts/model-routing-cost.md, wiki/projects/t3-teach-lecture-operations.md, wiki/insights/til-patterns-2026-05.md, index.md (6개)
- 반영 내용: PM의 Spec→Eval 역할 전환, P0/P1/P2 평가 게이트, 팀별 스코어카드 기반 모델 라우팅 검증, T3-TEACH 현장 대응형 AI 서비스 발표 패턴, cross-domain shared asset cache busting, 병렬 worktree cleanup 부채
- Ghost 추가: 없음

## 2026-05-18 07:30 [ingest — 일일 sync: blog 4개 + TIL 2026-05-18 반영]
- 처리 raw: raw/blog/2026-05-14-skills-vs-agency-pm.md, raw/blog/2026-05-15-pm-leverage-team-decisions.md, raw/blog/2026-05-16-domain-vertical-agent-sku.md, raw/blog/2026-05-17-background-agents-n-kpi.md, raw/til/2026-05-18.md (5개)
- 신규 wiki: wiki/concepts/pm-agency-ai-era.md, wiki/concepts/team-decision-structure-agent-era.md, wiki/concepts/background-agent-n-kpi.md (3개)
- 갱신 wiki: wiki/concepts/ai-pm-role.md, wiki/concepts/vertical-agent-domain-depth.md, wiki/concepts/agent-pricing-model.md, wiki/insights/til-patterns-2026-05.md, wiki/insights/agent-build-harness.md, index.md (6개)
- 반영 내용: PM 에이전시, 팀 의사결정 구조, 도메인 번들 SKU, 백그라운드 에이전트의 한 명의 N KPI, hplan v0.8.4 production cycle, llm-brain/hplan 제품 페이지 후속 과제
- Ghost 추가: 없음

## 2026-05-17 07:05 [ingest — 일일 sync: TIL 2026-05-16 반영]
- 처리 raw: raw/til/2026-05-16.md (1개)
- 신규 wiki: 없음
- 갱신 wiki: wiki/insights/til-patterns-2026-05.md, wiki/insights/agent-build-harness.md, index.md (3개)
- 반영 내용: hplan PMF 반복 엔진, STATE.md 자동 주입, HARD-GATE 태그/예외 설계, 하네스 레이어 분리
- 참고: raw/clippings/ 12개는 이미 2026-05-16 wiki sources에 반영되어 있어 신규 편집 없이 mark-done 대상으로 처리
- Ghost 추가: 없음

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

## 2026-05-16 [ingest — 하네스 엔지니어링 리서치 보강: raw 11개 → wiki 5개 신규/확장]
- 처리 raw: raw/clippings/ 11개 신규 (evolution-agentic-patterns, anthropic-harness-design-long-running, anthropic-effective-harnesses, anthropic-three-agent-harness, arxiv-architectural-design-decisions, arxiv-opendev-terminal-agent, dev-agent-harness-is-architecture, langchain-state-of-agent-engineering, augment-harness-engineering-coding, medium-agent-control-plane, augment-single-vs-multi-agent)
- 신규 wiki: wiki/concepts/harness-engineering-evolution.md, wiki/concepts/generator-evaluator-architecture.md, wiki/concepts/single-vs-multi-agent.md (3개)
- 확장 wiki: wiki/concepts/agent-harness-pattern.md (이론 심화 + 수치 데이터), wiki/insights/agent-build-harness.md (외부 검증 패턴 추가 + lint P1 중복 해소)
- 갱신 index.md: 39 → 42페이지 (concepts 12→15)
- Ghost 추가: 없음
- lint P1 해소: agent-harness-pattern(이론)↔agent-build-harness(구현) 역할 분리 + 상호 링크 추가

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

## 2026-05-16 03:57 [curate]
- orphan: 0개
- stale_links: 0개
- distill 큐: 0개
- archive 후보: 0개
- graph 허브: 12개

## 2026-05-16 03:57 [curate]
- orphan: 0개
- stale_links: 0개
- distill 큐: 0개
- archive 후보: 0개

## 2026-05-16 03:57 [curate]
- orphan: 0개
- stale_links: 10개
- distill 큐: 0개
- archive 후보: 0개
- graph 허브: 12개

## 2026-05-22 00:24 [curate]
- orphan: 0개
- stale_links: 11개
- distill 큐: 0개
- archive 후보: 0개
- graph 허브: 14개

## 2026-05-22 07:03 [ingest — 일일 sync: 에이전트 하네스 합성 대기 + T3 주간요약 + TIL 2026-05-22 반영]
- 처리 raw: raw/blog/2026-05-22-에이전트-하네스-패턴.md, raw/meetings/clients/T3-TEACH/weekly_summary_2026-05-21.md, raw/til/2026-05-22.md (3개)
- 신규 wiki: 없음 (0개)
- 갱신 wiki: wiki/projects/t3-teach-lecture-operations.md, wiki/insights/til-patterns-2026-05.md, wiki/insights/agent-build-harness.md, index.md (4개)
- 반영 내용: T3-TEACH 현장 대응형 AI 서비스 발표 재요약, 데모 전달력 보강 처방, hplan v0.9.1 한국어 문서 Hero/install 개선, GUIDE-ko 시나리오 1의 일관성 플로우, 역할극 기반 제안 압축, ASCII 구조 비교 패턴
- 참고: raw/blog/2026-05-22-에이전트-하네스-패턴.md는 기존 wiki 소스 합성 대기 파일이라 신규 사실 추가 없이 처리 대상으로 기록
- Ghost 추가: 없음

## 2026-05-22 08:18 [curate]
- orphan: 0개
- stale_links: 11개
- distill 큐: 0개
- archive 후보: 0개

## 2026-05-22 09:11 [curate]
- orphan: 0개
- stale_links: 12개
- distill 큐: 0개
- archive 후보: 0개

## 2026-05-22 15:44 [curate]
- orphan: 0개
- stale_links: 12개
- distill 큐: 1개
- archive 후보: 0개

## 2026-05-23 07:00 [ingest — 일일 sync: AI Human 백로그 압축 + TIL 2026-05-23 반영]
- 처리 raw: raw/clippings/ AI Human Daily Brief 62개 + news duplicate/index 2개, raw/clippings/paper-* 48개, raw/til/2026-05-23.md (총 113개)
- 신규 wiki: wiki/insights/ai-human-daily-brief-curriculum-signals.md, wiki/insights/ai-paper-learning-path.md (2개)
- 갱신 wiki: wiki/insights/til-patterns-2026-05.md, index.md (2개)
- 반영 내용: AI Human Daily Brief의 "진도 → 산업 뉴스 → 학습 연결 → 토론 질문" 강의 맥락 공급 패턴, AI 논문 추천의 Classic + Recent + Practical Lens 로드맵, habix Legal GraphRAG PII 설계 검증, sentinel count 테스트, VC 계약 SaaS PRD dual-form/dogfooding 신호
- 참고: 대량 raw 백로그는 개별 페이지 100개+로 만들지 않고 교육/논문 로드맵 2개 노드로 압축 처리
- Ghost 추가: sentinel-count-test, prd-dual-form

## 2026-05-23 07:08 [daily sync — CCR 보조 실행, 07:00 cron 직후]
- sync_raw: llm-brain-private 1개 신규 미러 (다른 소스 변경 없음)
- ingest: 07:00 cron이 이미 본 사이클 처리 완료(log 212~218 참조) → 신규 wiki 편집 없음
- state 보정: raw/til/2026-05-23.md를 .ingest_state.json processed에 마킹 (cron이 til-patterns 본문은 반영했으나 개별 state 마킹은 누락)
- 잔여 113개 paper clippings 미마킹은 의도적 — 07:00 cron이 개별 페이지 대신 ai-paper-learning-path.md 압축 노드로 처리한 결과, 개별 state는 다음 manual review 때까지 보존
- curate: 토요일이라 스킵 (월요일만 --audit --lifecycle 실행 룰)

## 2026-05-25 07:09 [curate]
- orphan: 0개
- stale_links: 12개
- distill 큐: 0개
- archive 후보: 0개
