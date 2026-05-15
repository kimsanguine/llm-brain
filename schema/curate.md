# Curate 규칙

curate는 wiki 전체를 감사(audit) + 압축(distill) + 수명 관리(lifecycle)하는 복합 오퍼레이션이다.
주 1회 자동 실행 또는 `curate --all` 온디맨드 실행.

## 플래그별 실행 범위

| 플래그 | 수행 단계 |
|---|---|
| `--all` | audit + distill + lifecycle 전체 |
| `--audit` | audit만 |
| `--distill` | distill만 |
| `--lifecycle` | lifecycle 후보 목록만 (실제 이동은 사용자 확인 후) |

---

## 1단계: AUDIT

wiki/ 전체를 스캔해 품질 문제를 탐지한다.

### 탐지 항목

**Orphan 페이지**: inbound `[[wikilink]]` 수가 0인 페이지
- 신규 생성 직후는 예외
- 30일 이상 orphan이면 보고

**Ghost 개념**: index.md ghost 섹션에 등록됐지만 90일 이상 페이지 미생성
- raw 데이터가 없어서인지, 아니면 누락인지 구분해 보고

**모순 감지**: 두 페이지에서 같은 개념에 대해 상충하는 서술
- 예: A 페이지 "X는 Y다", B 페이지 "X는 Z다"
- raw 파일 날짜가 더 최신인 쪽을 우선 표시

**Stale 링크**: `[[페이지명]]`이 존재하지 않는 페이지를 가리키는 경우

### 산출물
`wiki/curate_report.md` 갱신 — 문제 목록 + 권장 조치

---

## 2단계: DISTILL

도메인별로 wiki 페이지들을 읽고 고밀도 인사이트 페이지를 생성한다.

### 실행 대상
`wiki/insights/` — TIL·meetings에서 반복 등장한 패턴 압축

### 압축 기준
- 동일 개념이 3개 이상 wiki 페이지에서 언급 → insights/ 페이지로 압축
- 강의 관련 반복 패턴 → `insights/lecture-patterns.md` 갱신
- habix 비즈니스 관련 패턴 → `insights/habix-patterns.md` 갱신

### 압축 형식
```
# [패턴명]
## 핵심 원칙 (1-2줄)
## 관찰된 사례 (날짜 + 출처)
## 적용 방법
## 관련 개념
```

---

## 3단계: LIFECYCLE

오래됐거나 가치가 낮아진 페이지를 archive 후보로 선정한다.

### 후보 선정 기준 (결정론적)

| 조건 | 판정 |
|---|---|
| 마지막 업데이트 > `schema/sources.yaml`의 ttl_days AND inbound_links == 0 | archive 후보 |
| 마지막 업데이트 > ttl_days × 2 AND inbound_links <= 1 | delete 후보 |

도메인별 TTL은 `schema/sources.yaml`의 lifecycle 섹션 참조.

### 절차
1. 후보 목록을 `wiki/curate_report.md`에 작성
2. **사용자가 목록을 확인하고 승인**
3. 승인된 항목만 `wiki/archive/` 로 이동
4. 영구 삭제는 `--purge` 플래그 명시 시에만 실행

### 실행 금지
- 자동으로 파일 이동/삭제하지 않는다 (사용자 확인 필수)
- concepts/, tools/, people/, projects/ 도메인은 ttl_days: 0이므로 lifecycle 대상 제외

---

## 산출물 형식 (curate_report.md)

```markdown
# Curate Report — YYYY-MM-DD

## Audit 결과
### Orphan 페이지 (N개)
- wiki/path/page.md — 마지막 업데이트: YYYY-MM-DD
### Ghost 개념 (N개)
- 개념명 — 최초 언급: YYYY-MM-DD
### 모순 감지 (N개)
- A 페이지 vs B 페이지: 내용 요약

## Distill 결과
- 갱신된 insights 페이지: N개

## Lifecycle 후보
### Archive 후보 (사용자 확인 필요)
- wiki/insights/2026-01-15-note.md — 180일 경과, inbound 0
### Delete 후보 (사용자 확인 필요)
- wiki/insights/2025-11-01-note.md — 365일 경과, inbound 0
```
