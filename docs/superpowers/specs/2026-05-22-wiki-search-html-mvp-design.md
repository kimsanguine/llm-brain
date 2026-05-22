# Wiki Search HTML MVP — Design Doc

**Status**: Draft (사용자 검토 대기)
**Date**: 2026-05-22
**Owner**: kimsanguine
**Project**: 260516_llm_brain

---

## 1. 배경

현재 `/query` CLI는 Claude Code 세션 안에서만 작동한다. 매 호출마다 컨텍스트 윈도우에 wiki 마크다운이 통째로 로드되고, 결과는 LLM 답변 형태로 길게 나온다.

**문제점**:
- 단순 키워드 확인용으로도 LLM이 동작해 토큰 비용 발생
- 결과가 채팅 메시지로 흘러가 다시 보기 어려움
- 50개 페이지의 wikilink 그래프를 마우스로 탐색하기 어려움

**해결**: wiki 데이터를 정적 검색 + 페이지 뷰가 가능한 로컬 HTML 페이지로 띄운다. AI 답변은 옵션 토글로 분리한다.

---

## 2. 목표 (in scope)

- 로컬 HTTP 서버(`http://localhost:8000`)에서 wiki 검색·조회 페이지 제공
- 검색: 제목 + description + tags 기본 매칭, 결과 < 3개 시 본문까지 자동 확장
- 페이지 뷰: 마크다운 렌더링 + 클릭 가능한 `[[wikilink]]`, 우측 패널 inline 교체
- access_count 자동 갱신 (CLI `/query`와 동등)
- AI 답변 토글 UI 완성 (endpoint는 stub, 2차에서 LLM 연결)
- 검색 결과 상태(충분/부족/0개)에 따라 AI CTA가 시각적으로 강조 차등화

## 3. 비목표 (out of scope, v1 명시 제외)

- 인증·배포·CORS 처리 (1인 로컬 전용)
- 실제 LLM 호출 (1차는 stub, 2차 작업)
- 그래프 인터랙티브 시각화 (Obsidian Canvas로 위임, "📊 Obsidian에서 열기" 링크만 제공)
- 모바일 반응형 (데스크톱 한 해상도 우선)
- 다중 사용자·세션
- 검색 기록·즐겨찾기
- 시맨틱 검색 / embedding

---

## 4. 사용자 흐름

### 4.1 빈 상태 → 검색
1. 사용자가 `http://localhost:8000` 접속
2. 중앙에 큰 검색 박스 + 추천 키워드(`최근 ingest`, `메가 허브`, `전체 인덱스`)
3. 사용자가 키워드 입력 → 즉시 결과 카드 리스트(좌측) + 첫 카드 자동 선택(우측 페이지 뷰)

### 4.2 검색 결과 + 페이지 탐색
4. 좌측 결과 카드: 제목 · description · degree · 카테고리 표시
5. 카드 클릭 → 우측 패널이 해당 페이지 본문으로 inline 교체
6. URL hash 동기화 (`#page=ai-pm-role`) → 새로고침/공유 가능
7. 본문 내 `[[wikilink]]` 클릭 → 좌측 결과 유지하면서 우측만 새 페이지로 교체
8. 페이지 뷰 표시 시 백엔드가 `access_count +1`

### 4.3 결과 부족 → 자동 확장
9. B 매칭(제목+desc+tags)으로 < 3개일 때 자동으로 C 확장(본문 grep) 실행
10. 보라색 안내 배지("🔍 본문까지 자동 검색 — N개 추가 발견") 표시
11. 본문 매칭의 경우 카드에 하이라이트 snippet 첨부

### 4.4 AI 답변 토글 (옵션)
12. 결과 충분 시: 페이지 뷰 상단 우측 "✨ AI 답변" 작은 버튼
13. 결과 부족(< 3개) 시: 결과 리스트 아래 노란 박스 CTA
14. 결과 0개 시: 중앙 emptystate에 큰 검정 버튼
15. 클릭 → `POST /api/ai-answer` 호출 → 1차는 stub 응답 `{"status":"pending","message":"🚧 준비 중"}`

---

## 5. 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│ Browser (vanilla JS + CSS)                              │
│  ├─ index.html       (검색 UI · 결과 리스트 · 페이지 뷰)│
│  ├─ app.js           (fetch · 상태관리 · hash routing)  │
│  └─ styles.css       (Pretendard · 흰 배경 · 미니멀)    │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/JSON
                 ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI (uv 환경, 기존 scripts/ 재사용)                 │
│  ├─ /api/index       GET   → index.md 파싱 결과 캐시   │
│  ├─ /api/search?q=   GET   → B 매칭 + < 3개 시 C 확장  │
│  ├─ /api/page/{slug} GET   → 마크다운 렌더 + access++   │
│  └─ /api/ai-answer   POST  → 1차 stub, 2차 CLI 호출    │
└────────────────┬────────────────────────────────────────┘
                 │ 파일 시스템
                 ▼
┌─────────────────────────────────────────────────────────┐
│ wiki/                                                    │
│  ├─ index.md         (검색 인덱스)                       │
│  ├─ concepts/*.md, tools/*.md, ...                       │
│  └─ graph.json       (degree 정보, in/out 카운트)        │
└─────────────────────────────────────────────────────────┘
```

### 5.1 모듈 책임

| 모듈 | 파일 | 책임 | 의존 |
|---|---|---|---|
| Search index | `wiki_app/search.py` | index.md 파싱 + B/C 알고리즘 | `index.md` |
| Page loader | `wiki_app/pages.py` | 마크다운 + frontmatter 파싱, wikilink 변환 | `wiki/*.md` |
| Markdown render | `wiki_app/render.py` | `markdown-it` 호출, `[[slug]]` → 클릭 가능한 링크 | markdown-it-py |
| API | `wiki_app/api.py` | FastAPI endpoint 정의 | 위 3개 모듈 |
| Access tracker | `wiki_app/access.py` | `scripts/curate.py --record-access` 호출 wrapper | 기존 curate.py |
| Frontend | `wiki_app/static/` | HTML/CSS/JS 정적 파일 | 없음 |

### 5.2 디렉토리 구조

```
260516_llm_brain/
├── wiki_app/                  # 신규
│   ├── __init__.py
│   ├── __main__.py            # uv run python -m wiki_app
│   ├── api.py
│   ├── search.py
│   ├── pages.py
│   ├── render.py
│   ├── access.py
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── styles.css
├── scripts/                   # 기존
├── wiki/                      # 기존 (읽기 전용)
└── docs/superpowers/specs/2026-05-22-wiki-search-html-mvp-design.md
```

---

## 6. 검색 알고리즘 상세

### 6.1 인덱스 빌드 (서버 시작 시 1회)
- `wiki/index.md` 파싱 → 50개 페이지의 `(slug, category, description)` 리스트
- 각 페이지 frontmatter 로드 → tags 추출
- 메모리에 in-memory dict 저장 (50개 페이지면 < 100KB)
- `wiki/graph.json` 로드 → degree score 보유

### 6.2 B 알고리즘 (기본 매칭)
- 입력 쿼리 정규화 (소문자, 공백 trim)
- 각 페이지에 대해 점수 계산:
  - 제목(slug) 부분일치: +3 (slug는 영문이라 한국어 쿼리에선 자동 0점, description/tags 매칭만 점수 부여)
  - tags 매칭: +2
  - description 매칭: +1
- 점수 > 0인 페이지를 점수 내림차순 정렬
- 동점은 degree score 내림차순 tiebreaker

### 6.3 C 확장 (자동, 결과 < 3개일 때)
- 50개 마크다운 본문 grep
- 매칭된 단락 추출(최대 80자 snippet) + 하이라이트 마킹
- B 결과에 dedupe + 추가
- 응답에 `expanded: true` 플래그 + 신규 추가 N개 표시용

### 6.4 결과 0개
- B + C 모두 0이면 빈 결과 반환
- 프론트가 empty state UI 렌더 (큰 AI CTA)

---

## 7. API 명세

### `GET /api/index`
서버 시작 시 빌드된 검색 인덱스 메타데이터 반환.

응답:
```json
{
  "total_pages": 50,
  "total_links": 463,
  "categories": ["concepts", "tools", "projects", "business", "lecture", "insights"],
  "last_built": "2026-05-22T10:00:00Z"
}
```

### `GET /api/search?q={query}`
검색 실행.

응답:
```json
{
  "query": "에이전트",
  "results": [
    {
      "slug": "agent-harness-pattern",
      "category": "concepts",
      "description": "...",
      "score": 6,
      "degree": 25,
      "snippet": null,
      "match_type": "title+tags"
    }
  ],
  "expanded": false,
  "total": 6
}
```

`expanded: true`이면 B에서 < 3개여서 C로 확장된 케이스. 결과에 `snippet` 필드 채워질 수 있음.

### `GET /api/page/{slug}`
페이지 본문 + 메타데이터.

응답:
```json
{
  "slug": "agent-harness-pattern",
  "title": "Agent Harness Pattern",
  "category": "concepts",
  "frontmatter": {
    "tags": ["...", "..."],
    "created": "2026-05-15",
    "access_count": 1
  },
  "html": "<p>OpenAI 4 Pillars...</p>",
  "inbound": 9,
  "outbound": 16
}
```

호출 시 백엔드가 `access_count += 1` 자동 갱신.

### `POST /api/ai-answer` (1차 stub)
요청:
```json
{
  "question": "에이전트 하네스 설계 핵심이 뭐야?",
  "context_slugs": ["agent-harness-pattern", "generator-evaluator-architecture"]
}
```

1차 응답 (stub):
```json
{
  "status": "pending",
  "message": "🚧 AI 답변은 다음 버전에서 활성화됩니다. CLI `/query`를 사용해주세요.",
  "context_slugs": ["..."]
}
```

2차에서 동일 인터페이스로 LLM 답변 채워 넣음.

---

## 8. 프론트엔드 상태 관리

vanilla JS · 단일 SPA · framework 없음.

### 8.1 전역 상태
```js
const state = {
  query: "",
  results: [],
  selectedSlug: null,
  pageData: null,
  aiToggle: false,
  expanded: false
};
```

### 8.2 URL hash 동기화
- `#q=에이전트&page=agent-harness-pattern` 형태
- `hashchange` 이벤트로 상태 복원
- 검색·페이지 선택 시 hash 갱신 (push, not replace)

### 8.3 디자인 톤
- 폰트: Pretendard (CDN: jsdelivr)
- 색상: 흰 배경 (`#fff`), 텍스트 `#0d0d0d`, 부텍스트 `#6e6e6e`, 강조 보라 `#5e3fcf`
- radius: 카드 14px, 버튼 8px, 입력창 24px
- 검색 결과 hover: `#fafafa` 배경, 1px 상승 그림자

레퍼런스 `llm-wiki-demo.html`의 CSS를 차용하되 채팅 인터페이스 부분은 검색·결과 카드·페이지 뷰로 대체.

---

## 9. 검증 기준 (Definition of Done)

- [ ] `uv run python -m wiki_app` 한 줄로 서버 시작 (포트 8000)
- [ ] `http://localhost:8000` 접속 시 빈 상태 (검색창 + 추천 키워드)
- [ ] "에이전트" 검색 시 6개 결과 (B 알고리즘) — 1-2개일 때 자동 확장 발동
- [ ] 결과 0개 시 큰 AI CTA empty state 표시
- [ ] 결과 카드 클릭 → 우측 패널 페이지 본문 표시 → `access_count` 1 증가
- [ ] 본문 내 `[[wikilink]]` 클릭 → 우측 패널만 교체 (좌측 결과 유지)
- [ ] URL hash 새로고침 시 상태 복원
- [ ] AI 토글 버튼 클릭 → stub 응답 "🚧 준비 중" 표시
- [ ] 한국어 키워드("에이전트")와 영문 키워드("agent") 모두 작동
- [ ] 50개 페이지 처음 fetch + 검색 < 100ms

---

## 10. 위험과 대응

| 위험 | 영향 | 대응 |
|---|---|---|
| markdown-it의 wikilink 처리 — 표준 문법 아님 | 본문에 `[[slug]]`이 텍스트로 남음 | 백엔드 render 단계에서 정규식 후처리: `\[\[([^\]]+)\]\]` → `<a data-link="$1">$1</a>` |
| 검색 인덱스 stale — wiki 갱신 후 미반영 | 신규 페이지 검색 안 됨 | 서버 시작 시 1회 빌드 + `?refresh=1` 파라미터로 수동 재빌드 가능 |
| access_count 동시성 — 동일 페이지 빠른 연속 조회 | YAML 쓰기 race | curate.py 내부에 파일 lock 이미 있음, 검증만 필요 |
| 본문 grep 성능 — 50개 파일 매번 읽기 | 검색 시 latency | C 확장 결과를 5분 메모리 캐시, 동일 쿼리 빠른 반환 |

---

## 11. 후속 단계 (v2 예정)

### v2 핵심 (우선순위 높음)

1. **AI endpoint 활성화 (P0)** — 1차 MVP에서 stub인 `/api/ai-answer`를 실제 구현으로 교체
   - 1차 모드: `claude -p` CLI subprocess 호출 (PRD v2의 `engine: cli` 기본값, 토큰 비용 0)
   - 2차 모드: Anthropic API 직접 호출 (`engine: api`, 환경변수 `ANTHROPIC_API_KEY`)
   - 답변 streaming: SSE 또는 chunked response → 프론트 typewriter 효과
   - sources 추출: 응답에 참고한 wiki 페이지 slug 리스트 첨부 → 모달에 source card 표시

2. **모달 잔존 fix (P1, 1줄 변경)** — `wiki_app/static/app.js`의 `ensureAiModal()` 내부:
   ```js
   window.addEventListener("hashchange", () => modal.classList.add("hidden"));
   ```
   추가. URL hash 변경 시 모달 자동 닫힘. 또는 ESC 키 처리도 함께.

3. **그래프 시각화 (P2)** — 페이지 뷰 우측 또는 새 탭에 1-depth 미니 그래프
   - `wiki/graph.json` 활용
   - d3-force 또는 sigma.js
   - 현재는 Obsidian Canvas로 위임 중 (`wiki/canvas/query-*.canvas`)

### v2 부수 기능 (가능한 추가)

- 검색 결과 카테고리 필터 (concepts/tools/projects 등)
- 검색 기록 사이드바 (localStorage)
- `obsidian://` URI 통합 — "Obsidian에서 열기" 버튼
- 다크 모드 토글
- 키보드 shortcut (Cmd+K 검색, j/k 결과 이동, Enter 페이지 열기)
- 검색 결과 page_title 한국어 highlight (현재 slug만 highlight됨)

---

## 14. Known Issues (1차 MVP)

| # | Issue | 영향 | Fix 비용 | 우선순위 |
|---|---|---|---|---|
| 1 | AI 모달이 hash navigate 시 자동으로 닫히지 않음 (intercept 발생 가능) | 사용자가 ×버튼 잊으면 다음 클릭 차단 | 1줄 (v2 #2 참조) | P1 |
| 2 | `rglob` 매 페이지뷰 호출 (`access._update_frontmatter_access`) | 50개 파일 스캔 — 미세한 latency 누적 | category 인덱스 캐시 추가 (10줄) | P3 |
| 3 | 검색 결과 page_title 한국어가 카드에 표시 안 됨 (slug만 표시) | 한국어 사용자가 어떤 페이지인지 인지 어려움 | API 응답에 page_title 포함 + 카드 렌더 수정 (10줄) | P2 |
| 4 | `access_count`가 wiki_stats.json과 frontmatter 두 곳에 기록됨 (Task 5 deviation) | CLI `/query`와 일관성 미세 차이 | source-of-truth 단일화 (20줄, plan 수정 필요) | P3 |
| 5 | `_count_links`가 매 `/api/index` 호출마다 graph.json 재읽음 | 미세한 latency (~ms) | 캐싱 (5줄) | P4 |

---

## 15. 1차 MVP 구현 회고

### 잘 된 점

- **TDD가 백엔드 6개 모듈에서 일관되게 적용됨** (26개 unit tests) — 각 모듈이 독립적으로 검증되어 통합 시점에 문제 거의 없었음
- **`/api/ai-answer` stub 패턴** — UI는 풀버전(모달·CTA 차등화)을 1차에 완성하고 백엔드만 stub. 2차 작업 범위가 명확함
- **검색의 점진적 확장 (B → C)** — Plan의 "ResNet 시나리오"가 실제로 의도대로 작동 (B 1개 → C grep 1개 추가 + 보라색 안내)

### plan-vs-reality drift 4가지

구현 과정에서 plan이 잘못된 가정을 가진 4개 케이스 발견·대응. 모두 implementer가 합리적으로 처리했지만, **다음 plan 작성 시 학습 포인트**:

1. **Task 1**: `path.parent.name` → subpath slug에서 잘못된 category. plan 수정 필요했음.
2. **Task 3**: `index.md`가 wiki/ 안이 아니라 프로젝트 루트. plan이 위치 가정 잘못.
3. **Task 3**: `description`엔 한국어 "에이전트" 없음 (frontmatter title에만). plan test가 데이터 검증 없이 작성됨.
4. **Task 5**: `scripts/curate.record_access`가 wiki_stats.json만 갱신, frontmatter는 안 함. plan이 함수 본문 verify 없이 가정.

**교훈**: plan 작성 시 "기존 함수 재사용" 또는 "기존 데이터 파싱"이 들어가면, 그 함수/데이터의 실제 모양을 1줄이라도 verify해서 plan에 박아야 함. brainstorm 단계엔 추상으로 충분하지만 plan은 구현 청사진이라 정밀도가 필요.

### 효율화 관찰

- 단순 task (Task 0, 7~12)는 dual review (spec + code)가 over-engineering — combined single review로 충분
- Reviewer가 over-engineering 권고 (type hints, defensive code, speculative caching)를 자주 raise → controller가 User CLAUDE.md Rule 2 근거로 reject 결정 필요
- 백엔드 task는 TDD가 자연스럽고, 프론트엔드 task는 수동/Playwright 검증이 본질 — 두 사이클을 다르게 운영해야 함

---

## 12. 의존성

추가될 Python 패키지 (`pyproject.toml` 자동 갱신):
```bash
uv add fastapi 'uvicorn[standard]' markdown-it-py
# pyyaml은 기존 사용 중
```

프론트엔드 외부 의존성:
- Pretendard CSS (CDN: `https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css`)
- 자체 vanilla JS — npm 없음

---

## 13. 참고 자료

- 레퍼런스 디자인: `~/Library/Application Support/Claude/local-agent-mode-sessions/.../outputs/llm-wiki-demo.html` (디자인 톤만 차용, 채팅 인터페이스 패턴은 제외)
- SPEC.md / CLAUDE.md (llm-brain 가드레일·LLM 엔진 선택)
- Brainstorming 시각 자료: `.superpowers/brainstorm/18818-1779413750/content/` (scope.html · search-vs-qa.html · full-flow.html · search-algo.html · result-states.html · remaining-decisions.html)
