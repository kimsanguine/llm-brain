![llm-brain AI-native second brain OS banner](./assets/banner.svg)

# llm-brain — 당신의 두 번째 뇌를 만드세요

> **LLM을 컴파일러로 쓰는 Second Brain 시스템**
> *Build your Second Brain with LLM as the compiler*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Claude Code](https://img.shields.io/badge/Claude_Code-CLI-orange)
![Obsidian](https://img.shields.io/badge/Obsidian-Graph_View-7C3AED)

---

## 미리보기 *Preview*

로컬 HTML 검색·페이지뷰 (`uv run python -m wiki_app`):

| 검색 + 페이지 뷰 | 본문 grep 자동 확장 |
|---|---|
| ![검색](docs/screenshots/dod-3-korean-search.png) | ![확장](docs/screenshots/dod-4-resnet-expansion.png) |

| 결과 0개 → AI CTA | AI 답변 모달 (live) |
|---|---|
| ![empty](docs/screenshots/dod-5-zero-results.png) | ![ai](docs/screenshots/dod-9-ai-modal.png) |

> 한국어/영문 검색 · 결과 < 3개일 때 본문 grep 자동 확장 · 페이지 뷰 + wikilink SPA 네비게이션 · AI 답변 옵션 토글

---

## 왜 만들었나 *Why this exists*

매일 TIL을 쓰고, 회의록을 남기고, 논문을 클리핑한다.
그런데 한 달 뒤 그 지식은 어디 있는가?

*You write TILs, meeting notes, paper clippings every day.*
*But where does that knowledge go after a month?*

---

## Andrej Karpathy의 LLM Wiki 패턴 *Karpathy's LLM Wiki Pattern*

Karpathy는 이 문제에 대해 명쾌한 답을 제시했다.

> **"LLM을 컴파일러처럼 써라. raw 메모를 넣으면 구조화된 위키가 나온다."**

```
raw/   →   [LLM 컴파일러]   →   wiki/
원본                              정제된 지식
```

### 장점 *Strengths*

| | 설명 |
|---|---|
| ✅ | **LLM이 구조화를 담당** — 사람이 직접 편집할 필요 없음 |
| ✅ | **raw / wiki 분리** — 원본은 보존, 정제본은 별도 관리 |
| ✅ | **wikilink 연결** — 지식이 그래프로 연결됨 |
| ✅ | **오염 방지** — raw 없이 wiki 수정 금지 원칙으로 할루시네이션 차단 |

---

## 그러나 4가지가 빠져 있다 *But 4 things are missing*

LLM Wiki는 아이디어 수준에 머물렀다.
실제로 운영해보면 이 4가지 벽에 부딪힌다.

*LLM Wiki stays at the concept level. In practice, you hit 4 walls.*

| 한계 | 증상 |
|---|---|
| ❌ **Express 없음** | 지식이 wiki에 쌓이기만 한다. 꺼내 쓸 방법이 없다 |
| ❌ **Capture 필터 없음** | 뭐든 ingest하면 노이즈가 차오른다 |
| ❌ **단발성 압축** | 자주 쓰는 지식이 더 깊이 정제되지 않는다 |
| ❌ **그래프 맹목** | Obsidian에서 보이는 연결 구조를 curate에 활용하지 않는다 |

---

## Tiago Forte의 Second Brain *Tiago Forte's Second Brain*

Forte는 같은 문제를 다른 각도에서 풀었다.

> **"뇌는 아이디어를 떠올리는 곳이지, 저장하는 곳이 아니다."**
> *"Your brain is for having ideas, not storing them."*

그의 **CODE 프레임워크**는 지식의 전체 생애주기를 다룬다.

```
C apture  →  O rganize  →  D istill  →  E xpress
  수집           정리           정제          출력
```

Second Brain의 핵심은 **Distill과 Express**다.
자주 꺼내볼수록 더 압축되고, 결국 창작물로 나와야 한다.

그러나 이 두 단계는 **사람이 직접** 해야 했다. 시간이 가장 많이 드는 곳이다.

---

## llm-brain = LLM Wiki + Second Brain

두 패턴의 결합이 이 프로젝트다.

*This project is the synthesis of both patterns.*

```
         LLM Wiki          +        Second Brain
    ─────────────────────────────────────────────
    raw → wiki 컴파일       +    CODE 전체 생애주기
    할루시네이션 방지         +    Distill → LLM 대행
    wikilink 그래프          +    Express → 창작물 출력
                             +    lifecycle → TTL 관리
```

**Distill은 LLM이 대행한다. 당신은 Express에만 집중하라.**

*LLM handles Distill. You focus only on Express.*

---

## 핵심 기능 *Core Features*

### 📥 ingest — 4가지 입력 채널 *4 Input Channels*

```bash
# 채널 1: 수동 투입 (MD · TXT · PDF · DOCX · PPTX)
cp paper.pdf raw/docs/

# 채널 2: /ingest 슬래시 명령 (Claude Code 세션 내에서만 동작 — 터미널 직접 실행 불가)
/ingest https://example.com --resonance high
/ingest ~/Downloads/paper.pdf
/ingest "오늘 배운 것: ..."

# 채널 3: Obsidian vault 자동 미러링 (schema/sources.yaml 등록)
# 채널 4: Claude Code Routines 크론 등록
```

`--resonance high/medium/low` 태그로 중요도 표시.
index.md 기반 중복 검사로 wiki 노이즈 방지.

---

### 🔁 curate — 점진적 압축 + 그래프 분석 *Progressive Summarization + Graph*

```bash
uv run python scripts/curate.py --distill    # distill_level 점진 압축
uv run python scripts/curate.py --lifecycle  # TTL 초과 페이지 → archive 후보
uv run python scripts/curate.py --all        # 전체 실행

uv run python scripts/export_graph.py       # wikilink 그래프 export → wiki/graph.json
```

wiki 페이지는 접근할수록 더 깊이 정제된다.

```yaml
# 자동 관리되는 frontmatter
distill_level: 2      # 0=원문 → 1=요약 → 2=핵심 → 3=한줄
access_count: 12
```

`export_graph.py`는 `[[wikilink]]` 인바운드 수를 분석해 `wiki/graph.json`을 생성한다.
허브·고립 페이지 판단은 `wiki_app`의 `/api/page/{slug}/graph` 엔드포인트로 조회 가능하다.

---

### 📤 express — wiki → 창작물 *Wiki to Output*

Second Brain의 존재 이유. 지식을 꺼내 쓴다.

*The reason Second Brain exists. Get knowledge out.*

```bash
uv run python scripts/express.py blog "AI 에이전트 설계 패턴"
uv run python scripts/express.py lecture "context-first-orchestration" --slides 5
uv run python scripts/express.py summary --week
uv run python scripts/express.py report "경쟁사 현황"
```

blog 출력은 `raw/blog/`에도 자동 복사 → 다음 ingest 사이클에 wiki로 피드백.

```
wiki/ → express/blog/ → raw/blog/ → wiki/   ← 피드백 루프
```

---

### 🔍 query — wiki 기반 답변 *Wiki-grounded Answers*

```
사용자: "RAG 구현할 때 뭐가 중요했지?"
Claude: wiki/ 내용 기반으로만 답변
        (wiki에 없으면 "raw 데이터가 필요합니다")
```

query 시 접근한 페이지의 `access_count`가 올라가
다음 `curate --distill`에서 자동 우선 처리된다.

### 🌐 wiki-web — HTML 검색·페이지뷰 인터페이스 *Local HTML Search UI*

CLI `/query`의 시각화 버전. 브라우저에서 검색·페이지 탐색·wikilink 클릭.

```bash
uv run python -m wiki_app
# → http://localhost:8000
```

- **검색**: 제목 + description + tags + page_title 점수 매칭, 결과 < 3개일 때 본문 grep 자동 확장
- **페이지뷰**: 마크다운 렌더링 + `[[wikilink]]` 클릭 SPA 네비게이션, 좌측 결과 리스트 유지
- **AI 답변 토글**: 결과 부족도에 비례해 CTA 강조 차등 (작은 버튼 / 노란 박스 / 큰 검정 버튼)
- **URL hash**: `#q=...&page=...` 형태로 검색·페이지 상태 보존, 새로고침 시 복원

스크린샷: `docs/screenshots/dod-*.png`

> AI 답변은 `claude -p` CLI로 라이브 동작 (2026-05-23 연결, 05-26 SSE 스트리밍 추가). Claude Code 미설치 시 `status: unavailable`로 graceful 처리.

---

## LLM 엔진 선택 *LLM Engine*

```yaml
# schema/config.yaml
llm:
  engine: cli   # Claude Code CLI 재사용 — API 키 불필요
  # engine: api # Anthropic API 직접 호출
```

| 모드 | 비용 | 조건 |
|---|---|---|
| `cli` (기본) | 토큰 비용 없음 | Claude Code 설치 필요 |
| `api` | API 과금 | `ANTHROPIC_API_KEY` 필요 |

---

## 빠른 시작 *Quick Start*

```bash
# 0. uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. 클론
git clone https://github.com/kimsanguine/llm-brain.git
cd llm-brain

# 2. 초기 설정
bash scripts/setup.sh

# 3. 소스 경로 등록
vi schema/sources.yaml

# 4. 미처리 raw 파일 확인
uv run python scripts/ingest.py
# ※ 이 명령은 raw/ 의 미처리 파일 목록만 출력한다.
#   실제 wiki 컴파일은 Claude Code 세션에서 "ingest 해줘"로 수행한다.

# 5. 데모를 즉시 확인하려면 (빈 wiki 상태 우회)
cp -r examples/seed-wiki/* ./
uv run python -m wiki_app   # → http://localhost:8000

# 6. Obsidian에서 열기
# 이 폴더를 Obsidian → "Open folder as vault"
```

---

## Obsidian 연동 *Obsidian Integration*

`.obsidian/`이 프로젝트 루트에 있어 `raw/`와 `wiki/` 양쪽이 Graph View에 표시된다.

```
llm-brain/
├── .obsidian/   ← vault root
├── raw/         ← Graph View 표시
└── wiki/        ← Graph View 표시
```

---

## 디렉토리 구조 *Directory Structure*

```
llm-brain/
├── CLAUDE.md                  # Claude Code 운영 가이드
├── SPEC.md                    # 기술 명세서
├── README.md
├── pyproject.toml
├── schema/
│   ├── sources.example.yaml   # 소스 설정 템플릿
│   ├── config.yaml            # LLM 엔진 선택
│   ├── ingest.md              # ingest 규칙
│   └── curate.md              # curate 규칙
├── scripts/
│   ├── setup.sh               # 초기 설정
│   ├── sync_raw.py            # 소스 미러링
│   ├── ingest.py              # 파일 파싱 + 상태 관리
│   ├── curate.py              # 감사·압축·lifecycle (--health, --suggest-bridges)
│   ├── export_graph.py        # wikilink 그래프 export → wiki/graph.json
│   └── express.py             # wiki → 창작물 출력
├── wiki_app/                  # 🌐 HTML 검색·페이지뷰 (FastAPI)
│   ├── api.py                 # 6 endpoints
│   ├── search.py              # 검색 인덱스 + B/C 알고리즘
│   ├── pages.py               # 페이지 로더
│   ├── render.py              # markdown + wikilink 변환
│   ├── access.py              # access_count wrapper
│   └── static/                # vanilla JS + CSS + HTML
├── tools/
│   └── intro-video/           # Remotion 소개 영상
├── raw/                       # 원본 소스 (.gitignore)
├── wiki/                      # LLM 정제 결과 (.gitignore)
└── express/                   # 창작물 출력 (.gitignore)
```

---

## 의존성 *Dependencies*

```toml
pymupdf          # PDF 텍스트 추출
python-docx      # Word 문서 추출
python-pptx      # PowerPoint 추출
markdownify      # HTML → Markdown
httpx            # URL 스크랩
pyyaml           # 설정 파일 파싱
python-frontmatter  # MD frontmatter
anthropic        # API 모드 (선택)
```

---

## 라이선스 *License*

MIT © [kimsanguine](https://github.com/kimsanguine)
