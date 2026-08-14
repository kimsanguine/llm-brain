# Claim Ledger Contract

query/AI answer 경로에서 사용하는 작은 file-first claim 원장 계약.

## ClaimRecord

- `claim_id`: `claim:{slug}-{n}` 형식의 결정적 식별자
- `text`: wiki 본문에서 분리된 claim 문장
- `classification`: `fact | inference | opinion`
- `source_path`: 1차 raw provenance 경로(없으면 현재 wiki 경로)
- `source_locator`: 가능하면 `raw/...#Lx-Ly`, 실패 시 경로만
- `source_sha256`: source 파일 바이트의 sha256 (로컬 source 부재 시 claim text sha256)
- `status`: `active | untrusted | stale | superseded`
- `valid_from`: `updated` 우선, 없으면 `created`
- `valid_until`: `observation_expires` 우선, 없으면 `valid_from + 180일`

## Query rules

1. `active` claim만 trusted query context로 LLM에 전달한다.
2. `untrusted` claim(예: `raw/newsletters/**`, `raw/clippings/**`, URL source)은
   별도 "외부 캡처 원문 (검증 전)" 섹션으로 격리한다.
3. `stale` / `superseded` claim은 query context와 cited answer footnote에서 제외한다.
4. 답변 인용 토큰은 `[claim:slug-N]` 형식이다.
