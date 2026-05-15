# LLM Wiki — Second Brain Compiler

> LLM을 컴파일러로 쓰는 개인 지식 관리 시스템

`raw/`(원본) → `wiki/`(정제) 2계층 구조에서 LLM이 컴파일러 역할을 한다.
Karpathy의 원본 패턴을 기반으로, 5가지 축에서 확장했다.

---

## Karpathy 원본 대비 5가지 확장

| 축 | Karpathy 원본 | 이 시스템 |
|---|---|---|
| **입력** | 수동 raw 파일 추가 | 4가지 입력 채널 |
| **LLM 호출** | API 직접 호출 | CLI 재사용 + API 선택 가능 |
| **오퍼레이션** | ingest / lint | ingest / curate (distill + lifecycle) |
| **시각화** | 없음 | Obsidian Graph View 기본 내장 |
| **소스 범위** | MD 중심 | PDF · Word · PPT · URL · 텍스트 전부 |

---

## 빠른 시작

```bash
# 1. 클론
git clone https://github.com/YOUR_USERNAME/llm-wiki.git
cd llm-wiki

# 2. 초기 설정 (의존성 설치 + 폴더 구조 생성)
bash scripts/setup.sh

# 3. 소스 경로 설정
vi schema/sources.yaml    # 자신의 폴더 경로 등록

# 4. LLM 엔진 선택
vi schema/config.yaml     # cli (기본) 또는 api

# 5. Obsidian에서 열기
# 이 폴더를 Obsidian → "Open folder as vault"로 열기
```

---

## 입력 채널 (4가지)

### 채널 1 — 수동 투입
파일을 직접 `raw/` 하위 폴더에 넣는다.
```
raw/
├── til/          # 학습 메모
├── meetings/     # 회의록
├── clippings/    # 웹 클리핑
├── notes/        # 자유 노트
└── docs/         # PDF · Word · PPT
```

지원 형식: `.md` `.txt` `.pdf` `.docx` `.pptx`

### 채널 2 — `/ingest` 명령어
Claude Code 세션에서 직접 실행한다.
```
/ingest https://example.com          # URL 스크랩
/ingest ~/Downloads/paper.pdf        # 로컬 파일
/ingest "오늘 배운 것: ..."           # 텍스트 노트
```

### 채널 3 — 자동 미러링 (선택)
`schema/sources.yaml`에 폴더를 등록하면 `sync_raw.py`가 변경 파일을 감지해 복사한다.

```yaml
sources:
  - id: my-notes
    source: ~/Documents/MyVault/TIL/
    target: raw/til/
    ttl_days: 180
    extensions: [md]
```

### 채널 4 — Routines 크론 (선택)
Claude Code Routines에 등록하면 매일 자동 ingest된다.

---

## LLM 엔진 선택

```yaml
# schema/config.yaml
llm:
  engine: cli    # API 키 불필요, Claude Code 설치 필요
  # engine: api  # Anthropic API 직접 호출
```

| 모드 | 장점 | 단점 |
|---|---|---|
| `cli` (기본) | API 키 불필요, 토큰 비용 없음 | Claude Code 설치 필요 |
| `api` | 어떤 환경에서도 실행 | API 키 · 비용 발생 |

---

## 오퍼레이션

```bash
PYTHON=".venv/bin/python"
SCRIPTS="wiki/projects/260515_llm_wiki/scripts"

# 소스 미러링
$PYTHON $SCRIPTS/sync_raw.py

# 미처리 파일 확인
$PYTHON $SCRIPTS/ingest.py

# URL 스크랩
$PYTHON $SCRIPTS/ingest.py --url https://example.com

# 로컬 파일 추가
$PYTHON $SCRIPTS/ingest.py --file ~/Downloads/paper.pdf

# 텍스트 노트
$PYTHON $SCRIPTS/ingest.py --note "오늘 배운 것: ..."

# wiki 감사 + 압축 + lifecycle
$PYTHON $SCRIPTS/curate.py --all
```

---

## Obsidian 연동

이 폴더(`llm-wiki/`) 자체를 Obsidian vault root로 설정한다.
`.obsidian/`이 루트에 있으므로 `raw/`와 `wiki/` 양쪽이 Graph View에 표시된다.

```
llm-wiki/
├── .obsidian/     ← vault root
├── raw/           ← Graph View에 표시
└── wiki/          ← Graph View에 표시
```

---

## 디렉토리 구조

```
llm-wiki/
├── CLAUDE.md                          # Claude Code 운영 가이드
├── README.md
├── pyproject.toml                     # uv 의존성
├── schema/
│   ├── sources.example.yaml           # 소스 설정 템플릿
│   ├── config.yaml                    # LLM 엔진 선택
│   ├── ingest.md                      # ingest 규칙
│   └── curate.md                      # curate 규칙
├── scripts/
│   └── setup.sh                       # 초기 설정
├── wiki/projects/260515_llm_wiki/scripts/
│   ├── run_daily.sh                   # launchd 진입점
│   ├── sync_raw.py                    # 소스 미러링
│   ├── ingest.py                      # 파일 파싱 + 상태 관리
│   └── curate.py                      # 감사·압축·lifecycle
├── raw/                               # 원본 소스 (.gitignore)
├── wiki/                              # LLM 정제 결과 (.gitignore)
├── index.md                           # 전체 목차
└── log.md                             # 실행 이력
```

---

## 의존성

```toml
python-docx     # Word 문서 텍스트 추출
python-pptx     # PowerPoint 텍스트 추출
pymupdf         # PDF 텍스트 추출
markdownify     # HTML → Markdown 변환
httpx           # URL 스크랩
pyyaml          # 설정 파일 파싱
python-frontmatter  # MD frontmatter 파싱
anthropic       # API 모드 (선택)
```

---

## 라이선스

MIT
