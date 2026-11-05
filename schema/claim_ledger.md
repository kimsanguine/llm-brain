# Claim Ledger Contract

query/AI answer 경로에서 사용하는 작은 file-first claim 원장 계약.

기본 저장 위치는 repository root의 `claims.jsonl`이며 UTF-8 JSON object 한 줄이
claim 하나다. `locator`와 `source_binding`은 optional이고 나머지는 required다. unknown field,
blank line, duplicate ID, malformed/partial record 하나라도 있으면 원장 전체를 거부한다.

## ClaimRecord

- `claim_id`: `claim:{slug}-{n}` 형식의 결정적 식별자
- `statement`: wiki 본문에서 분리된 비어 있지 않은 claim 문장
- `kind`: `fact | inference | opinion`
- `raw_path`: traversal 없는 repository-relative `raw/**` 경로
- `raw_sha256`: 원장 생성 시점 raw 파일 전체 bytes의 정확한 lowercase SHA-256(64 hex)
- `locator` (optional): 해당 `raw_path` 또는 `raw_path#Lx-Ly`
- `valid_from`, `valid_until`: 유효한 `YYYY-MM-DD`, `valid_from <= valid_until`
- `status`: `active | stale | superseded`
- `trust`: `trusted | untrusted`
- `source_binding` (optional): strict B1 object, 아래 계약 적용. 없으면 기존 단일 출처 계약 유지.

writer는 모든 record를 먼저 검증한 뒤 같은 디렉터리의 임시 파일을 `os.replace`해
원자적으로 교체한다. `raw/**` 아래를 ledger target으로 지정할 수 없다.
자동 build는 statement별 source 귀속을 추측하지 않는다. wiki 페이지의 `sources`가
정확히 하나의 `raw/**` 경로가 아니면 기본 build 전체를 거부한다.

## B1 explicit source binding

여러 출처 페이지는 `claims.py propose --slug <slug>`의 읽기 전용 JSON 제안과
`claims.py build --slug <slug> --source-map <private.json>`의 명시적 적용을 사용한다.
제안은 현재 페이지에 선언된 안전한 UTF-8 raw 파일 중 statement가 정확히 포함된
파일이 하나일 때만 연결한다. 여러 파일에 일치하거나 일치하지 않으면 미해결로 남긴다.
같은 파일의 반복 출현은 첫 줄 위치를 사용한다. 첫 출처 선택이나 출처 전체 귀속은 없다.

`source_binding`의 모든 필드는 required이며 unknown field는 거부한다:

```json
{
  "schema_version": "llm-brain-claim-binding/0.1",
  "page_sha256": "<64 lowercase hex>",
  "statement_sha256": "<64 lowercase hex>",
  "quote": "<statement와 동일한 정확한 원문>"
}
```

record의 `raw_path`, `raw_sha256`, `locator`와 함께 검증한다. B1 locator는
`raw/path#Lx-Lx`의 양수 한 줄이어야 하며 그 줄에 quote가 포함되어야 한다.
페이지 전체 bytes hash가 바뀌면 binding이 무효화되어 제안과 build를 다시 수행해야 한다.
페이지의 현재 sources에 선택한 raw 경로가 있어야 한다. raw hash와 quote도 다시 확인한다.
claim ID의 순번에 해당하는 현재 위키 문장과 statement도 같아야 한다.
기존 날짜, 상태, 외부 캡처의 untrusted 규칙은 그대로 적용한다.

source-map root는 strict `schema_version: llm-brain-claim-source-map/0.1`,
`mappings`, `unresolved`이다. mapping은 claim_id/raw_path/raw_sha256/locator/source_binding,
unresolved는 claim_id/reason(no_safe_sources/no_exact_match/ambiguous_sources/non_statement)이다.
중복 JSON 필드, 중복 claim과 두 목록의 겹침을 거부한다. map에 없는 후보는 생략하고
build가 개수를 보고한다. 선택된 mapping 하나라도 변경되거나 손상되면 쓰기 전 전체 거부한다.
지정한 위키 페이지가 사라진 경우에도 원장을 부분 교체하지 않고 거부한다.
연결된 claim이 0개면 기존 ledger를 교체하지 않는다. build는 선택 slug들의 원장을
atomic replace하므로 기존 내용을 유지하려면 유지할 slug도 명시해야 한다.

제안은 기존 문장 분할기의 텍스트 후보를 대상으로 하며 의미적 사실성, 요약이나 추론의
타당성, 사람의 검토를 증명하지 않는다. 여러 근거를 결합하는 B2는 지원하지 않는다.
map과 ledger는 개인 statement를 포함한다. map은 gitignored `ontology/` 아래에 보관한다.

## v0.4.1 papers와 구조적 후보

기존 7개 페이지 범주에 `papers`를 추가한다. 페이지 조회, claim source inventory,
source-map과 ontology가 같은 범주를 읽는다. 외부 원문의 trust와 기존 B1 검증은 유지한다.
papers의 따옴표 없는 콜론 제목은 기존 YAML 파싱 실패 시 단일 title 값만 메모리에서
문자열로 감싸 다시 읽는다. 원본 bytes와 source 필드는 바꾸지 않으며 다른 YAML 오류는 거부한다.

`propose`는 기존 splitter의 순번과 statement를 그대로 유지한 뒤 명백한 제목, 표,
fenced code, 구분선, 링크/이미지와 메타데이터만 `non_statement`로 분리한다.
일반 bullet/prose와 본문의 수식은 보존한다. 제외된 후보도 unresolved에 남으므로
구조적 제외와 원문 불일치/출처 없음/모호한 연결을 구분할 수 있다.
이 분류는 제안 단계의 보수적 필터이며, 기록의 의미나 사실성을 승인하지 않는다.
명시적 source-map build는 계속 원문/페이지/문장 hash와 quote/locator를 검증한다.

## Query rules

1. query는 persisted ledger를 읽기만 하며 `raw/**`, `wiki/**`, stats, Canvas를 쓰지 않는다.
   로드한 모든 record의 slug를 현재 wiki 페이지와 대조하고, 페이지 `sources`가 정확히
   하나의 유효한 `raw/**`가 아니거나 record `raw_path`와 다르면 원장 전체를 거부한다.
   명시적 B1 binding이 있으면 이 단일 출처 조건 대신 현재 페이지 hash와 선택 출처의
   membership을 검사한다. binding 없는 구버전 여러 출처 원장은 계속 거부한다.
2. `active + trusted + validity current + current raw SHA-256 match`인 claim만 trusted
   context와 cited answer에서 허용한다. B1은 현재 페이지와 원문 줄까지 검증하며
   불일치는 `source_binding_mismatch`로 제외한다.
3. `untrusted` claim(예: `raw/newsletters/**`, `raw/clippings/**`) statement는 newline과
   heading을 escape한 deterministic single-line JSON data로만 격리하며 명령으로 해석하지 않는다.
4. `stale`, `superseded`, `source_missing`, `source_hash_mismatch`는 statement 없이 서로
   다른 exclusion reason으로 표면화한다.
5. 답변 인용 토큰은 `[claim:slug-N]` 형식이다. unknown/malformed/inactive/untrusted
   citation 하나라도 있으면 답변 전체를 거부한다. usable trusted claim이 있으면 성공
   답변은 최소 한 개를 인용해야 한다. 하나도 없을 때만 정확한 무인용 표준 응답
   `관련 정보 없음`을 허용한다.
6. SSE는 기존 chunk/byte cap 안에서 전부 buffering한 뒤 같은 citation gate를 통과한
   결과만 방출한다.
