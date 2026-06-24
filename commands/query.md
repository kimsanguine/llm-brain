---
description: wiki 기반 질문 답변 (wiki에 없으면 raw 필요 안내)
---

llm-brain의 query 커맨드입니다. 질문: **$ARGUMENTS**

아래 절차로 wiki 기반 답변을 제공하세요.

## Step 1: index.md 검색

`index.md`를 읽고 질문과 관련된 wiki 페이지 목록을 식별합니다.
키워드 매칭으로 관련도 높은 페이지 최대 5개를 선정합니다.

## Step 2: wiki 페이지 로드

선정된 wiki 페이지들을 읽습니다.
관련 페이지가 없으면:
> "이 주제에 대한 wiki 데이터가 없습니다. `/ingest` 로 관련 소스를 먼저 추가해주세요."
라고 응답하고 종료합니다.

## Step 3: wiki 기반 답변

읽은 wiki 페이지 내용만을 근거로 답변합니다.

**중요 원칙**:
- wiki 페이지에 없는 내용은 "wiki에 해당 정보가 없습니다"라고 명시
- Claude 학습 데이터로 wiki 내용을 보완하지 않음
- 답변 마지막에 참조한 wiki 페이지 목록을 `[[페이지명]]` 형식으로 표시

## Step 4: access_count 갱신

답변에 사용한 각 페이지의 slug에 대해:
```bash
cd "$(git rev-parse --show-toplevel)"  # llm-brain 레포 루트
uv run python scripts/curate.py --record-access <페이지_slug>
```

## Step 5: 연결 요약 출력

`wiki/graph.json`이 없으면 이 단계를 건너뜁니다.

답변에서 첫 번째로 참조한 페이지(`primary_slug`)의 연결 현황을 출력합니다:

```python
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")

graph_path = Path("wiki/graph.json")
if graph_path.exists():
    graph = json.loads(graph_path.read_text())
    nodes_by_id = {n["id"]: n for n in graph["nodes"] if n["kind"] == "page"}
    links = graph["links"]

    # primary_slug = 답변에서 첫 번째로 참조한 wiki 페이지의 slug
    if primary_slug in nodes_by_id:
        node = nodes_by_id[primary_slug]
        n_in  = node["inbound"]
        n_out = node["outbound"]
        inbound_list  = [l["source"] for l in links if l["target"] == primary_slug and l["source"] in nodes_by_id][:2]
        outbound_list = [l["target"] for l in links if l["source"] == primary_slug and l["target"] in nodes_by_id][:2]
        print(f"[query] 참조: [[{primary_slug}]]  인바운드 {n_in} / 아웃바운드 {n_out}")
        if inbound_list:
            extra = f" 외 {n_in - 2}개" if n_in > 2 else ""
            print(f"  ◀ inbound:  {', '.join(inbound_list)}{extra}")
        if outbound_list:
            extra = f" 외 {n_out - 2}개" if n_out > 2 else ""
            print(f"  ▶ outbound: {', '.join(outbound_list)}{extra}")
```

## Step 6: Neighborhood Canvas 생성

primary 페이지의 1-depth 네이버후드 Canvas를 생성합니다:

```python
from canvas_utils import build_neighborhood_canvas, save_canvas

if graph_path.exists() and primary_slug in nodes_by_id:
    canvas = build_neighborhood_canvas(graph, primary_slug)
    if canvas:
        canvas_path = Path(f"wiki/canvas/query-{primary_slug}.canvas")
        save_canvas(canvas, canvas_path)
        print(f"[query] canvas → wiki/canvas/query-{primary_slug}.canvas")
```

Obsidian에서 `wiki/canvas/query-{primary_slug}.canvas`를 열어 노드 연결 맥락을 확인할 수 있습니다.
