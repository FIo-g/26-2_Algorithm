# 서울 최단경로 Python 실험(E1~E3) 통합 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 서울 OSMnx 그래프에서 Dijkstra·A*·Bidirectional·ALT를 Dijkstra 100% 일치 검사와 함께 구현한다. 실험 E1~E3 결과(CSV), 그림 (a)~(d)·(f)·(g), 발표 파트 2·4용 현업·문헌 자료를 만든다.

**Architecture:** 표준 라이브러리만 쓰는 코어 패키지 `routing`에 그래프 형식, 공용 힙, 알고리즘, 검사, 벤치를 둔다. OSMnx, 속도 데이터, 그림 코드는 코어 밖 모듈과 `scripts/`에 둔다. 코어는 윈도우 PC의 SUMO E4 계획에서 그대로 재사용한다. 시간 측정은 항상 정확성 검사를 통과한 뒤에만 한다.

**Tech Stack:** Python 3.14 (Homebrew venv), OSMnx 2.1.x, NetworkX 3.x(대조용), matplotlib, requests, geopandas(OSMnx 의존성), pytest

**Spec:** `seoul_routing_plan_v2.md` (레포 루트). 과제 요구사항은 강의 슬라이드 22~30(발표 4개 파트, README 포트폴리오, 생성형 AI 규정)이다.

**이 문서의 위치:** 팀의 단일 기준 계획이다. 팀원별 가이드(`docs/team/*.md`)는 이 문서의 Task 번호를 가리킨다. 둘이 다르면 이 문서가 맞다.

**범위:**
- SUMO E4(RQ3, 그림 (e))는 윈도우 PC에서 별도 계획을 세운다(맨 끝 "후속: E4 계획").
- 범위 밖 항목(CH·CRP 구현, 회전 제한, 시간의존)은 spec 1장을 따른다.
- 중간 보고서(Pass/Fail 필수)는 spec에 마감이 없다. 마감과 형식을 먼저 확인한다(열린 결정).

---

## 팀 운영

| Task | 내용 | 담당 | 리뷰 | 우선순위 | 목표일 |
|---|---|---|---|---|---|
| 1 | 뼈대 + Graph + 합성 그래프 + AI 기록 양식 | 태형 | 의종 | P1 · **모두가 기다림** | 10/30 오전 |
| 2 | 실시간 속도 수집기 | 세현 | 태형 | 시간 민감 | 10/30 |
| 3 | 공용 힙 + Dijkstra + sssp | 태형 | 의종 | P1 | 10/30 |
| 4 | 정확성 검사 도구 | 세현 | 의종 | P1 | 10/30~31 |
| 5 | OSMnx 추출 | 세현 | 태형 | P1 | 10/30 |
| 6 | A* + Weighted A* | 태형 | 의종 | P1 | 10/31 |
| 7 | Bidirectional | 태형 | 의종 | P1 | 10/31 |
| 8 | ALT | 의종 | 세현 | P1 | 10/30~31 |
| 9 | 완전탐색 + BFS 부분 그래프 | 세현 | 태형 | P1 | 10/31 |
| 10 | 질의 생성 | 태형 | 세현 | P1 | 11/1 |
| 11 | 벤치 하네스 | 태형 | 세현 | P1 | 11/1 |
| 12 | 정확성 관문 스크립트 + 관문 실행 | 세현 | 태형 | P1 | 11/1, 11/3 |
| 13 | E1 + 그림 (a) | 세현 | 태형 | P1 | 11/2 |
| 14 | E2 + 그림 (b) + 하한 느슨함 측정 | 태형 | 의종 | P1 | 11/3 |
| 15 | 혼잡 시나리오 | 의종 | 세현 | P2 | 11/1 |
| 16 | E3 + 그림 (c)(d) + 서버 환산 | 의종 | 세현 | P2 | 11/2~4 |
| 17 | 탐색 공간 그림 (f) | 태형 | 의종 | P1 (영상) | 11/2 |
| 18 | 데이터 설명 그림 (g) + 그래프 표 | 세현 | 태형 | P1 (영상) | 11/3~4 |
| 19 | 현업·문헌 조사 + 공정성 | 의종 (안) | 태형 | P1 (발표 필수 파트) | 10/30~11/4 |
| 20 | 표준노드링크 매칭 | 세현 | 의종 | P4 | 11/2 |
| 21 | 실제 속도 스냅샷 → E3 | 의종 | 세현 | P4 | 11/4 |
| 22 | `run_all` 최종 실행 + 결과 동결 | 태형 | 세현 | P1 | 11/5 |

- 담당은 spec 6장을 따랐다. 다음은 계획 작성자의 판단이다.
  - 정확성 검사 도구 중 질의 생성과 벤치는 태형, 검사(verify)와 관문은 세현이 맡는다.
  - 새로 생긴 Task 17·18·19의 담당. Task 19는 spec에서 "미정"이던 파트 2를 의종에게 제안한 것으로, ALT·결론 파트와 문헌이 바로 이어지고 코드 Task 수가 가장 적기 때문이다.
- 리뷰 담당은 spec 6장(세현 → ALT, 태형 → 파이프라인·완전탐색, 의종 → Dijkstra 계열)을 기준으로 나머지를 고르게 나눴다.
- 한 사람이 늦어지면 리뷰 담당이 이어받는다(spec 6장).
- **진행 방식:**
  1. Task마다 브랜치 `t{N}-{짧은이름}`을 만든다.
  2. PR을 올리기 전에 `pytest`(최소 `tests/test_correctness.py`)를 돌린다.
  3. 리뷰 담당이 승인하면 `main`에 병합한다.
  4. 병합한 사람은 팀 채팅에 "Task N 병합"을 알린다. 의존하는 사람이 기다리고 있기 때문이다.
- **선행 Task가 아직 병합되지 않았을 때:** `routing.synthetic`의 합성 그래프로 먼저 개발한다(spec 10장 대비책).

**의존 관계 (병합 순서):**
- Task 1 → 모든 Task
- Task 3 → 4, 6, 7, 8, 9, 15
- Task 4 → 6·7·8의 `test_correctness` 등록, 12
- Task 5 → 12, 13, 17, 18, 20
- Task 6·7·8 → 11 → 12 → 14, 16
- Task 10 → 12, 14, 16
- Task 15 → 16 → 21
- Task 20 → 21
- 전부 → 22

---

## Global Constraints

- **Python:** `/opt/homebrew/bin/python3.14 -m venv .venv` (윈도우·다른 맥은 3.10 이상). `osmnx>=2.1,<3` (2.1.1에서 API 확인함)
- **코어 모듈은 표준 라이브러리만 import한다:** `graph`, `heap`, `dijkstra`, `astar`, `bidirectional`, `alt`, `exhaustive`, `verify`, `queries`, `bench`, `congestion`, `synthetic`, `gate`
- **그래프 형식:** 정점은 0..n−1 정수, 가중치는 이동시간(초, float)이다. `fwd[u] = [(v, w), ...]`, `bwd[v] = [(u, w), ...]`
- **간선 유일성:** 같은 (u, v) 간선은 **하나만** 둔다.
  - `Graph`는 중복 (u, v)를 받으면 `ValueError`를 낸다.
  - `from_edge_list`, `random_geo_graph`, `from_osmnx`는 중복이 있으면 시간이 가장 작은 것만 남긴다(spec 4-1 "평행 간선은 가장 빠른 것만").
- **vmax:** 그래프에서 계산한다(`max(length / time)`, m/s). 생성할 때 **한 번만** 계산해 속성으로 저장하고, 질의마다 다시 계산하지 않는다.
- **그래프는 불변:** 간선 시간을 바꾸려면 `g.reweighted(times)`로 새 그래프를 만든다. `time`·`length`는 유한한 0 이상 값만 허용한다(통행 불가 도로를 inf로 표현하지 않는다).
- **정확 알고리즘 시그니처:** `name(g, s, t, ..., *, stats=None) -> tuple[float, list[int], int]`. 반환값은 (거리, 경로, 확정 노드 수)다.
  - 도달할 수 없으면 `(math.inf, [], settled)`
  - `s == t`이면 `(0.0, [s], 0)`
- **정확성 판정:** `math.isclose(d, ref, rel_tol=1e-9, abs_tol=1e-9)`와 경로 유효성으로 한다. 경로 동일성은 비교하지 않는다(동점 경로가 있음).
- **휴리스틱 축소:** `H_SCALE = 1 - 1e-9`를 A*와 ALT에 모두 적용한다.
- **지구 반지름:** `6_371_009` m (OSMnx `EARTH_RADIUS_M`와 같음)
- **그래프 파일:** `data/graphs/{name}_graph_v{N}.pkl`, name ∈ {`gangnam`, `gss`(강남·서초·송파), `seoul`}. 다시 추출하면 N을 올리고 팀에 알린다. 덮어쓰기는 금지한다.
- **질의 집합:** `osm_id`로 저장한다. 시드는 42다.
- **측정 방법:**
  - 워밍업은 측정 질의와 **별도로** 추가로 돌린다.
  - 모든 질의를 측정한다. 질의×알고리즘마다 `gc.disable()` 상태에서 `perf_counter`로 3번 재고 그 중앙값을 쓴다.
  - 요약은 중앙값과 p95로 낸다.
  - 확정 노드 수(머신과 무관)를 시간과 함께 주 지표로 보고한다.
- **최종 벤치마크:** 한 머신에서 한 번에 돌린다. 그동안 그 머신에서 속도 수집기를 끈다(Task 22).
- **서버 환산:** Dijkstra 대비 **비율**로만 낸다.
- **코드 언어:** 코드, 주석, 그림 라벨은 영어로 쓴다(발표와 README가 영어). 팀 문서는 한국어로 쓴다.
- **생성형 AI 규정(슬라이드 30):**
  - 모든 Task의 마지막 단계에서 `docs/ai-usage.md`에 한 줄을 기록한다.
  - 알고리즘 Task(3, 6, 7, 8, 9, 15)는 담당자가 핵심 테스트 예제를 손으로 따라가 본다. 그리고 `docs/explain/{topic}.md`에 **본인 말로** 5~10줄(영어) 설명을 쓴다. Live Q&A에서 그대로 쓸 수 있는 수준이어야 한다.
  - AI가 그 설명을 대신 쓰지 않는다.
  - 레퍼런스는 원문을 직접 확인한 것만 쓴다(spec 8장).

## Review Focus

1. 수집기가 밤새 돌다가 API 오류, 타임아웃, JSON이 아닌 응답을 만나면 죽지 않고 `errors.log`에 한 줄 남긴 뒤 다음 주기를 계속해야 한다 → Task 2 `test_collector_survives_errors`
2. ALT 랜드마크 거리가 `inf`(도달 불가)여도 휴리스틱 값이 `nan`이 되지 않아야 한다 → Task 8 `test_alt_heuristic_never_nan`, `test_alt_landmark_reaches_neither_endpoint`
3. 길이 0·시간 0인 간선이 있어도 `vmax`에서 0으로 나누지 않아야 하고, 모든 알고리즘이 0 가중치를 정상 처리해야 한다 → Task 1 `test_vmax_ignores_zero_length_edge`, Task 4 `test_zero_weight_edges`
4. `s == t`이면 모든 알고리즘이 `(0.0, [s], 0)`을 돌려줘야 하고, Bidirectional이 멈추지 않으면 안 된다 → Task 4 `test_same_source_target`
5. 거리 구간을 채울 수 없는 그래프에서 `make_queries`가 무한 루프 없이 부분 구간만 채우고 경고를 내야 한다 → Task 10 `test_unfillable_bin_warns`
   - 참고: 강남구의 >10 km 구간은 **채워진다**(무작위 쌍의 약 0.15%, 대각선 끝 쌍). 그 대신 그림 (b)에 "대각선 끝 쌍"이라고 표시한다(Task 14).

---

## File Structure

```
pyproject.toml, .gitignore, CLAUDE.md
src/routing/
  graph.py, synthetic.py, heap.py, dijkstra.py, astar.py, bidirectional.py, alt.py,
  exhaustive.py, verify.py, queries.py, bench.py, gate.py, congestion.py      (코어, 표준 라이브러리만)
  osm.py                                                                       (OSMnx)
  experiments/e1.py, e2.py, e3.py                                              (실험 로직)
  figures.py                                                                   (matplotlib)
  speeds/collect.py, match.py, snapshot.py                                     (실시간 속도)
scripts/  extract_graph.py, check_exact.py, run_e1.py, run_e2.py, run_e3.py, match_links.py, make_figures.py, run_all.sh
tests/    helpers.py, test_graph.py, test_dijkstra.py, test_correctness.py, test_astar.py, test_bidirectional.py,
          test_alt.py, test_exhaustive.py, test_queries.py, test_bench.py, test_gate.py, test_osm.py,
          test_congestion.py, test_experiments.py, test_figures.py, test_speeds.py
docs/     ai-usage.md, explain/, industry.md, team/{kwon-sehyun,kim-taehyeong,jeong-uijong}.md
data/queries/ (커밋)     data/graphs/, data/speeds/, data/nodelink/, cache/ (gitignore)
results/, figures/ (커밋: README·발표용)
```

---

### Task 1: 프로젝트 뼈대 + Graph 형식 + 합성 그래프 — 담당 태형 · 리뷰 의종

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `src/routing/__init__.py`, `src/routing/graph.py`, `src/routing/synthetic.py`, `docs/ai-usage.md`, `docs/explain/.gitkeep`
- Test: `tests/test_graph.py`

**Interfaces:**
- Produces (`graph.py`):
  - `EARTH_RADIUS_M = 6_371_009.0`
  - `haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float`: 인자는 `(lat, lon)`
  - `@dataclass class Graph`의 필드: `coords: list[tuple[float, float]]`, `osm_ids: list[int]`, `tail: list[int]`, `head: list[int]`, `length: list[float]`(m), `time: list[float]`(s), `hwy: list[str]`, `name: str = ""`
    - `__post_init__`에서 모든 값을 내장 타입(`float`, `int`, `str`)으로 바꾼 뒤 `fwd`, `bwd`, osm_id → index 사전, `vmax`를 **한 번** 만든다. OSMnx의 numpy 실수형이 pickle에 들어가면 numpy가 없는 윈도우 PC에서 그래프 파일을 읽지 못하기 때문이다(최종 리뷰에서 발견).
    - 다음 경우 `ValueError`
      - `time`이나 `length`가 음수·NaN·inf
      - 좌표가 (위도 ±90, 경도 ±180) 범위를 벗어남. (경도, 위도)로 뒤바뀐 좌표를 잡기 위해서다.
      - (u, v)가 중복됨
    - `n`, `m` (property), `vmax` (속성, m/s)
    - `repr`은 `Graph(name=..., n=..., m=..., vmax=... m/s)` 한 줄이다.
    - 불변으로 다룬다. 리스트를 직접 고치면 `fwd`·`bwd`·`vmax`가 옛값으로 남으므로 `reweighted()`로 새 그래프를 만든다.
    - `index_of(osm_id) -> int`, `weight(u, v) -> float | None`, `nearest(lat, lon) -> int`
    - `reweighted(times: Sequence[float]) -> Graph`: 위상은 그대로, 시간만 교체
    - `subgraph(vertices: Sequence[int]) -> Graph`: 유도 부분 그래프, 번호를 다시 매기고 osm_id 보존. 정점이 중복되거나 범위 밖이면 `ValueError`
  - `largest_scc(g) -> list[int]`: 반복형 구현(재귀 금지, 서울 규모)
  - `save_graph(g, path)`, `load_graph(path) -> Graph` (pickle)
  - `vmax` 규칙
    - `length == 0`인 간선은 건너뛴다.
    - `time == 0`이면서 `length > 0`인 간선이 있으면 `math.inf`
    - 양수 길이 간선이 없으면 `1.0`
- Produces (`synthetic.py`). 모든 합성 그래프는 `osm_ids = [1000 + i for i in range(n)]`를 쓴다. 인덱스와 일부러 다르게 두어 둘을 혼동하는 버그가 드러나게 한다.
  - `from_edge_list(n, edges: list[tuple[int, int, float]], coords=None) -> Graph`
    - 중복 (u, v)는 최솟값만 남긴다. hwy = `"residential"`
    - coords를 주지 않으면 전부 (37.5, 127.0)이고 length = time(1 m/s)
    - coords를 주면 length = 두 끝점의 haversine이다(A* 하한 유지). coords 개수가 n과 다르면 `ValueError`
  - `grid_graph(rows, cols, *, spacing_m=100.0, speed_mps=10.0, hwy="residential") -> Graph`: 행 우선 번호, 4방향 양방향, length = 좌표 haversine
  - `random_geo_graph(n, extra_edges, *, seed, one_way_ratio=0.3) -> Graph`
    - 약 2 km 상자 안에 무작위 점을 찍는다.
    - 각 정점을 가장 가까운 2개 이웃과 잇는다. `one_way_ratio` 확률로 한 방향, 아니면 양방향이다.
    - 무작위 (u, v) 쌍을 `extra_edges`번 더 시도하되, 이미 있는 쌍과 자기 루프는 건너뛴다.
    - length = haversine × U(1.0, 1.3), 속도 U(5, 25) m/s
    - 강연결은 보장하지 않는다(도달 불가 쌍 테스트용).
- Produces (`docs/ai-usage.md`): 표 머리 `| 날짜 | 작성자 | Task | 도구 | 맡긴 일 | 본인이 확인한 것 |`

- [ ] **Step 1: 환경 구성**

```bash
/opt/homebrew/bin/python3.14 -m venv .venv && source .venv/bin/activate
pip install -e .   # dependencies: osmnx>=2.1,<3, networkx>=3.4, matplotlib>=3.9, requests>=2.32, pytest>=8
```

`pyproject.toml`: setuptools, `packages.find where=["src"]`, `requires-python=">=3.10"`, `[tool.pytest.ini_options] testpaths=["tests"]`.
`.gitignore`: `.venv/ __pycache__/ *.egg-info .pytest_cache/ cache/ data/graphs/ data/speeds/ data/nodelink/`

- [ ] **Step 2: 실패하는 테스트 작성** (`tests/test_graph.py`)

```python
def test_fwd_bwd_mirror():
    g = random_geo_graph(30, 60, seed=1)
    for e in range(g.m):
        assert (g.head[e], g.time[e]) in g.fwd[g.tail[e]]
        assert (g.tail[e], g.time[e]) in g.bwd[g.head[e]]

def test_haversine_one_degree_lat():
    assert haversine_m((0.0, 0.0), (1.0, 0.0)) == pytest.approx(111195.0837, abs=1e-3)

def test_vmax_is_max_speed():
    assert grid_graph(3, 3, speed_mps=12.5).vmax == pytest.approx(12.5)

def test_vmax_ignores_zero_length_edge():          # Review Focus 3
    g = Graph(coords=[(37.5, 127.0)] * 3, osm_ids=[1, 2, 3], tail=[0, 1], head=[1, 2],
              length=[0.0, 100.0], time=[0.0, 10.0], hwy=["residential"] * 2)
    assert g.vmax == 10.0

def test_negative_time_rejected():
    with pytest.raises(ValueError):
        from_edge_list(2, [(0, 1, -1.0)])

def test_duplicate_edges_keep_min():
    g = from_edge_list(2, [(0, 1, 5.0), (0, 1, 3.0)])
    assert g.m == 1 and g.weight(0, 1) == 3.0

def test_graph_rejects_duplicate_pairs():
    with pytest.raises(ValueError):
        Graph(coords=[(37.5, 127.0)] * 2, osm_ids=[1, 2], tail=[0, 0], head=[1, 1],
              length=[1.0, 1.0], time=[1.0, 2.0], hwy=["residential"] * 2)

def test_random_geo_graph_has_no_duplicates():
    g = random_geo_graph(60, 150, seed=0)
    assert len(set(zip(g.tail, g.head))) == g.m and all(u != v for u, v in zip(g.tail, g.head))

def test_reweighted_keeps_topology():
    g = grid_graph(3, 3); h = g.reweighted([t * 2 for t in g.time])
    assert (h.tail, h.head, h.osm_ids) == (g.tail, g.head, g.osm_ids)
    assert h.weight(0, 1) == 2 * g.weight(0, 1)

def test_largest_scc_drops_tail_vertex():
    g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 0, 1), (2, 3, 1)])
    assert sorted(largest_scc(g)) == [0, 1, 2]

def test_subgraph_preserves_osm_ids():
    g = grid_graph(3, 3); sub = g.subgraph([4, 5, 7, 8])
    assert sub.n == 4 and sub.osm_ids == [g.osm_ids[i] for i in (4, 5, 7, 8)]

def test_save_load_roundtrip(tmp_path):
    g = random_geo_graph(20, 30, seed=3); save_graph(g, tmp_path / "g.pkl")
    h = load_graph(tmp_path / "g.pkl")
    assert (h.tail, h.time, h.coords) == (g.tail, g.time, g.coords)
```

- [ ] **Step 3: 실패 확인**: `pytest tests/test_graph.py -v` → `ImportError`(FAIL)
- [ ] **Step 4: `graph.py`, `synthetic.py` 구현**
- [ ] **Step 5: 통과 확인**: `pytest tests/test_graph.py -v` → 22 passed (최종 리뷰 후 내장 타입·검증·repr 테스트 추가)
- [ ] **Step 6: 커밋, 병합, 알림**: 레포의 첫 커밋이다. spec, 이 계획, `CLAUDE.md`, `docs/team/`을 함께 넣는다. 병합 후 팀에 "Task 1 병합"을 알린다.

```bash
git add pyproject.toml .gitignore src tests docs CLAUDE.md seoul_routing_plan_v2.md
git commit -m "feat: project scaffold, Graph format, synthetic graphs"
```

- [ ] **Step 7: AI 사용 기록** (`docs/ai-usage.md`에 한 줄)

---

### Task 2: 실시간 속도 수집기 (오늘 가동) — 담당 세현 · 리뷰 태형

**사전 작업(사람이 직접):**
- ITS 국가교통정보센터 오픈데이터(its.go.kr/opendata)에서 "교통소통정보" 인증키를 신청한다.
- 백업용으로 서울 열린데이터광장 실시간 도로 소통 정보 키도 신청한다.
- TOPIS 과거 링크 속도는 파일 형식(시간 단위 여부)만 확인하고, 코드는 만들지 않는다(spec 5장 대체안).

**Files:**
- Create: `src/routing/speeds/__init__.py`, `src/routing/speeds/collect.py`
- Test: `tests/test_speeds.py`

**Interfaces:**
- Produces:
  - `ITS_URL = "https://openapi.its.go.kr:9443/trafficInfo"`
  - `BBOX_GSS = (126.98, 37.42, 127.19, 37.55)`: (minX, minY, maxX, maxY) 경위도. 서초구 남쪽 끝(37.4285)을 포함한다.
  - `build_params(api_key, bbox) -> dict[str, str]`: `apiKey, type="all", drcType="all", minX, maxX, minY, maxY, getType="json"`
  - `poll_once(fetch: Callable[[str, dict], bytes], api_key, bbox, out_dir: Path, now: datetime) -> Path | None`
    - 성공: `out_dir/YYYYMMDD/HHMMSS.json.gz`에 원본 바이트를 gzip으로 저장
    - 예외 또는 JSON 파싱 실패: `out_dir/errors.log`에 `ISO시각\t{예외 종류}: {앞 200자}` 한 줄을 남기고 `None`
  - `run_forever(fetch, api_key, bbox, out_dir, *, interval_s=300, max_polls=None, sleep=time.sleep, clock=datetime.now) -> None`
    - `clock()`은 수집 1회에 **정확히 한 번** 호출한다(파일명용).
    - 경과 시간은 `time.monotonic()`으로 재고 `sleep(interval_s − 경과)`
  - `parse_items(raw: bytes) -> list[dict]`: `body.items` → `{"link_id": str, "speed_kph": float, "created": str}`. 필드명 `linkId`, `speed`, `createdDate`는 Step 6에서 확인한다.
  - CLI: `python -m routing.speeds.collect --interval 300 --out data/speeds/raw`. 키는 환경변수 `ITS_API_KEY`에서 읽고, 코드나 레포에 넣지 않는다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
SAMPLE = b'{"header":{"resultCode":0},"body":{"items":[{"linkId":"1220001200","speed":"34.5","createdDate":"20261030083000"}]}}'

def test_poll_once_saves_gzip(tmp_path):
    p = poll_once(lambda url, params: SAMPLE, "K", BBOX_GSS, tmp_path, datetime(2026, 10, 30, 8, 30, 0))
    assert p == tmp_path / "20261030" / "083000.json.gz"
    assert gzip.decompress(p.read_bytes()) == SAMPLE

def test_parse_items():
    assert parse_items(SAMPLE) == [{"link_id": "1220001200", "speed_kph": 34.5, "created": "20261030083000"}]

def test_collector_survives_errors(tmp_path):            # Review Focus 1
    calls = iter([TimeoutError("t"), b"<xml>error</xml>", SAMPLE])
    def fetch(url, params):
        r = next(calls)
        if isinstance(r, Exception): raise r
        return r
    run_forever(fetch, "K", BBOX_GSS, tmp_path, max_polls=3, sleep=lambda s: None,
                clock=iter([datetime(2026, 10, 30, 0, i) for i in range(3)]).__next__)
    assert len((tmp_path / "errors.log").read_text().splitlines()) == 2
    assert len(list(tmp_path.rglob("*.json.gz"))) == 1
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_speeds.py -v` → FAIL
- [ ] **Step 3: `collect.py` 구현**. 실제 `fetch`는 `requests.get(url, params=params, timeout=30)`에 `raise_for_status()`를 붙이고 `.content`를 돌려준다.
- [ ] **Step 4: 통과 확인**: `pytest tests/test_speeds.py -v` → 3 passed
- [ ] **Step 5: 커밋**: `git commit -m "feat: ITS real-time speed collector"`
- [ ] **Step 6: 가동(키 승인 후)과 첫날 커버리지 확인**

```bash
export ITS_API_KEY=...   # never commit
caffeinate -i nohup .venv/bin/python -m routing.speeds.collect --interval 300 --out data/speeds/raw > data/speeds/collect.log 2>&1 &
```

통과 기준:
- 5분 뒤 `.json.gz`가 1개 생기고 `parse_items` 항목 수가 0보다 크다. 필드명이 다르면 `parse_items`의 키만 고친다(원본이 저장되어 있으므로 손실 없음).
- 첫날 저녁에 고유 링크 ID 수와 도로명 상위 20개를 `data/speeds/coverage_day1.txt`에 기록하고 팀에 공유한다. 서울 간선도로가 실제로 들어오는지 보는 것으로, 11/2 결정(Task 20)의 근거가 된다.
- 맥을 계속 켜 둘 수 없다면 항상 켜져 있는 PC에서 같은 명령으로 돌린다.
- **최종 벤치마크 머신에서는 Task 22 동안 끈다.**

- [ ] **Step 7: AI 사용 기록**

---

### Task 3: 공용 힙 + Dijkstra + sssp — 담당 태형 · 리뷰 의종

**Files:**
- Create: `src/routing/heap.py`, `src/routing/dijkstra.py`
- Test: `tests/test_dijkstra.py`

**Interfaces:**
- Consumes: `Graph`, `random_geo_graph`, `from_edge_list`, `grid_graph` (Task 1)
- Produces:
  - `@dataclass class Stats`: `settled=0; relaxed=0; pushes=0; pops=0; trace: list[int] | None = field(default=None, compare=False)`. 카운터 정의는 여기서 고정한다.
    - `pushes`: 모든 push
    - `pops`: 모든 pop(오래된 항목 포함)
    - `settled`: 오래된 항목을 뺀 pop, 즉 확정된 정점 수
    - `relaxed`: 확정된 정점에서 검사한 간선 수
    - Bidirectional은 양쪽을 하나의 Stats에 합산한다.
    - `trace`가 리스트이면 확정되는 정점을 순서대로 append한다(그림 (f)용).
  - `class CountingHeap(stats)`: `push(key, v)`, `pop() -> (key, v)`, `drop_stale(done: list[bool])`(top의 오래된 항목을 pop하고 pops에 셈), `top_key() -> float`(비면 `inf`), `__len__`
  - `dijkstra(g, s, t, *, stats=None) -> tuple[float, list[int], int]`: t를 확정하면 멈춘다. `stats=None`이면 내부에서 버릴 Stats를 만든다(측정 오버헤드가 모든 알고리즘에 똑같이 들도록). `shortest_path = dijkstra` (spec 이름)
  - `sssp(adj, s) -> list[float]`: 일대다, 카운터 없음 (ALT·midpoint용)

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def to_nx(g):
    G = nx.DiGraph(); G.add_nodes_from(range(g.n))
    for e in range(g.m): G.add_edge(g.tail[e], g.head[e], weight=g.time[e])   # (u, v) unique by Graph invariant
    return G

@pytest.mark.parametrize("seed", range(20))
def test_dijkstra_distance_matches_networkx(seed):
    g = random_geo_graph(60, 150, seed=seed); G = to_nx(g); rng = random.Random(seed)
    for _ in range(30):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        try: ref = nx.dijkstra_path_length(G, s, t)
        except nx.NetworkXNoPath: ref = math.inf
        d = dijkstra(g, s, t)[0]
        assert (d == ref == math.inf) or math.isclose(d, ref, rel_tol=1e-9, abs_tol=1e-9)

def test_sssp_matches_networkx():
    g = random_geo_graph(60, 150, seed=5); ref = nx.single_source_dijkstra_path_length(to_nx(g), 0)
    d = sssp(g.fwd, 0)
    assert all(math.isclose(d[v], ref[v]) if v in ref else d[v] == math.inf for v in range(g.n))

def test_dijkstra_stats_counting():
    g = from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)])
    st = Stats(); assert dijkstra(g, 0, 3, stats=st) == (12.0, [0, 2, 1, 3], 4)
    assert st == Stats(settled=4, relaxed=4, pushes=5, pops=5)   # stale (5, 1) is popped but not settled

def test_trace_records_settled_order():
    st = Stats(trace=[]); dijkstra(from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)]), 0, 3, stats=st)
    assert st.trace == [0, 2, 1, 3]
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_dijkstra.py -v` → FAIL
- [ ] **Step 3: `heap.py`, `dijkstra.py` 구현**. `heapq` 항목은 `(key, v)`, 지연 삭제는 `done[v]`로 판정한다.
- [ ] **Step 4: 통과 확인**: `pytest tests/test_dijkstra.py -v` → all passed
- [ ] **Step 5: 커밋, 병합, 알림**: `git commit -m "feat: counting heap, Dijkstra, sssp"`
- [ ] **Step 6: 이해 확인**: `test_dijkstra_stats_counting`의 push/pop 순서를 손으로 적는다. `docs/explain/dijkstra.md`에 본인 말로 "lazy deletion과 stale pop을 settled에서 빼는 이유"를 쓴다.
- [ ] **Step 7: AI 사용 기록**

---

### Task 4: 정확성 검사 도구 — 담당 세현 · 리뷰 의종

**Files:**
- Create: `src/routing/verify.py`
- Test: `tests/test_correctness.py`

**Interfaces:**
- Consumes: `Graph`, `dijkstra`, 합성 그래프
- Produces:
  - `path_cost(g, path) -> float | None`: 이어지지 않은 쌍이 있으면 `None`
  - `check_result(g, s, t, ref_dist, result, *, rel_tol=1e-9) -> list[str]`: 오류 메시지 목록, 비면 통과
    - 검사 항목: 거리 불일치, 시작·끝 정점, 존재하지 않는 간선, 경로 비용과 보고 거리의 불일치
    - `ref = inf`이면 결과도 `(inf, [])`여야 한다.
  - `verify_all(g, queries, algos: dict[str, Callable], *, ref="dijkstra") -> list[str]`: 시간을 재지 않는다. `"{algo} q{qid}: ..."` 메시지 목록을 돌려준다. `queries`는 `.qid`, `.s`, `.t`를 가진 객체(Task 10 `Query`)다.
  - `tests/test_correctness.py`의 `EXACT_ALGOS: dict[str, Callable]`: Task 6·7·8이 병합되면 각자 항목을 추가한다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
EXACT_ALGOS = {"dijkstra": dijkstra}
Q = namedtuple("Q", "qid s t")

@pytest.mark.parametrize("name", EXACT_ALGOS)
@pytest.mark.parametrize("seed", range(10))
def test_algo_matches_dijkstra(name, seed):
    g = random_geo_graph(80, 200, seed=100 + seed); rng = random.Random(seed)
    for _ in range(40):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        assert check_result(g, s, t, dijkstra(g, s, t)[0], EXACT_ALGOS[name](g, s, t)) == []

@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_same_source_target(name):                      # Review Focus 4
    assert EXACT_ALGOS[name](grid_graph(3, 3), 4, 4) == (0.0, [4], 0)

@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_unreachable(name):
    d, p, _ = EXACT_ALGOS[name](from_edge_list(4, [(0, 1, 1.0), (2, 3, 1.0)]), 0, 3)
    assert (d, p) == (math.inf, [])

@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_zero_weight_edges(name):                        # Review Focus 3
    g = from_edge_list(3, [(0, 1, 0.0), (1, 2, 0.0), (0, 2, 5.0)])
    assert EXACT_ALGOS[name](g, 0, 2)[:2] == (0.0, [0, 1, 2])

def test_check_result_rejects_bad_path():
    g = grid_graph(2, 2)
    assert check_result(g, 0, 3, 20.0, (20.0, [0, 3], 0)) != []   # 0-3 is not an edge

def test_check_result_rejects_cost_mismatch():
    g = grid_graph(2, 2); d, p, _ = dijkstra(g, 0, 3)
    assert check_result(g, 0, 3, d, (d, [0, 1, 0, 1, 3], 0)) != []   # valid edges, wrong cost

def test_verify_all_catches_wrong_algo():
    g = grid_graph(6, 6); qs = [Q(i, i, 35 - i) for i in range(5)]
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (dijkstra(g, s, t)[0] + 1, *dijkstra(g, s, t)[1:])}
    assert any(m.startswith("bad") for m in verify_all(g, qs, bad))
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_correctness.py -v` → FAIL
- [ ] **Step 3: `verify.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_correctness.py -v` → all passed
- [ ] **Step 5: 커밋, 병합, 알림**: `git commit -m "feat: correctness checker and verify_all"`
- [ ] **Step 6: AI 사용 기록**

---

### Task 5: OSMnx 추출 (강남구 → 3개 구 → 서울) — 담당 세현 · 리뷰 태형

**Files:**
- Create: `src/routing/osm.py`, `scripts/extract_graph.py`
- Test: `tests/test_osm.py` (네트워크 사용 안 함)

**Interfaces:**
- Consumes: `Graph`, `save_graph`
- Produces:
  - `PLACES = {"gangnam": ["Gangnam-gu, Seoul, South Korea"], "gss": ["Gangnam-gu, Seoul, South Korea", "Seocho-gu, Seoul, South Korea", "Songpa-gu, Seoul, South Korea"], "seoul": ["Seoul, South Korea"]}`
  - `download(name) -> nx.MultiDiGraph`: `ox.graph_from_place(PLACES[name], network_type="drive")` → `ox.truncate.largest_component(G, strongly=True)` → `ox.routing.add_edge_speeds(G, fallback=30)` → `ox.routing.add_edge_travel_times(G)`. `fallback=30` km/h는 계획 작성자의 판단이다.
  - `from_osmnx(G, name) -> Graph`
    - 정점은 osmid 오름차순, `coords = (y, x)` 즉 (위도, 경도)
    - (u, v) 평행 간선은 `travel_time` 최소인 것만 남기고, 그 간선의 length와 hwy를 쓴다.
    - 자기 루프는 버린다. `highway`가 리스트면 첫 값을 쓴다.
  - `meta(G, g) -> dict`: `name, n, m, vmax_mps, maxspeed_missing_ratio`(maxspeed 태그가 없는 G 간선 비율, spec의 "속도 보정 비율"), `hwy_counts, osmnx_version, extracted_at`
  - CLI: `python scripts/extract_graph.py {gangnam|gss|seoul} --version N`
    - 출력: `data/graphs/{name}_graph_vN.pkl`, `{name}_vN.graphml`(Task 18·20용), `{name}_graph_vN.meta.json`
    - 파일이 이미 있으면 종료 코드 1

- [ ] **Step 1: 실패하는 테스트 작성**: osmnx 형식의 `nx.MultiDiGraph`를 손으로 만든다.

```python
def tiny_osm():
    G = nx.MultiDiGraph(crs="epsg:4326")
    for osmid, (y, x) in {30: (37.50, 127.00), 10: (37.50, 127.01), 20: (37.51, 127.01)}.items():
        G.add_node(osmid, y=y, x=x)
    G.add_edge(30, 10, 0, length=900.0, travel_time=90.0, highway=["primary", "secondary"], maxspeed="50")
    G.add_edge(30, 10, 1, length=950.0, travel_time=70.0, highway="trunk")
    G.add_edge(10, 20, 0, length=1100.0, travel_time=110.0, highway="residential")
    G.add_edge(20, 20, 0, length=5.0, travel_time=1.0, highway="residential")       # self loop
    return G

def test_from_osmnx_conventions():
    g = from_osmnx(tiny_osm(), "tiny")
    assert g.osm_ids == [10, 20, 30] and g.coords[0] == (37.50, 127.01)
    e = [i for i in range(g.m) if (g.osm_ids[g.tail[i]], g.osm_ids[g.head[i]]) == (30, 10)]
    assert len(e) == 1 and (g.time[e[0]], g.length[e[0]], g.hwy[e[0]]) == (70.0, 950.0, "trunk")
    assert g.m == 2                                     # self loop dropped

def test_from_osmnx_list_highway():
    G = tiny_osm(); G.remove_edge(30, 10, 1)
    assert "primary" in from_osmnx(G, "tiny").hwy

def test_meta_maxspeed_ratio():
    G = tiny_osm(); assert meta(G, from_osmnx(G, "tiny"))["maxspeed_missing_ratio"] == 0.75
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_osm.py -v` → FAIL
- [ ] **Step 3: `osm.py`와 `extract_graph.py` 구현**. `ox.settings.use_cache = True`(캐시는 `cache/`).
- [ ] **Step 4: 통과 확인**: `pytest tests/test_osm.py -v` → 3 passed
- [ ] **Step 5: 실제 추출과 공유**

```bash
python scripts/extract_graph.py gangnam --version 1
nohup python scripts/extract_graph.py gss --version 1 > data/graphs/gss.log 2>&1 &
nohup python scripts/extract_graph.py seoul --version 1 > data/graphs/seoul.log 2>&1 &
```

통과 기준:
- `.meta.json` 3개가 생긴다.
- 강남구 예상치(검토 시제품 실측): SCC 정리 후 n ≈ 3,144, m ≈ 8,420, vmax ≈ 80 km/h, 약 87초.
- **maxspeed 결측 ≈ 94%**. 자유류 속도 대부분이 도로 등급 평균으로 채워진 값이라는 뜻이므로, 데이터 슬라이드와 README에 반드시 밝힌다.
- `.pkl`과 `.graphml`은 팀 공유 드라이브에 올린다. 팀원은 다시 다운로드하지 않는다(spec 5장).

- [ ] **Step 6: 커밋, 병합, 알림**: `git commit -m "feat: OSMnx extraction to versioned Graph files"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 6: A* (+ Weighted A*) — 담당 태형 · 리뷰 의종

**Files:**
- Create: `src/routing/astar.py`, `tests/helpers.py` (`control_pair`, Task 8에서도 사용)
- Modify: `tests/test_correctness.py` (`EXACT_ALGOS["astar"] = astar`, Task 4 병합 후)
- Test: `tests/test_astar.py`

**Interfaces:**
- Consumes: `CountingHeap`, `Stats`, `haversine_m`, `Graph.vmax`, `dijkstra`
- Produces:
  - `H_SCALE = 1 - 1e-9`
  - `astar_heuristic(g, v, t, vmax) -> float`: `haversine_m(coords[v], coords[t]) / vmax * H_SCALE` (Task 14 하한 느슨함 측정에도 씀)
  - `astar(g, s, t, *, vmax: float | None = None, eps: float = 1.0, stats=None) -> tuple[float, list[int], int]`
    - key = `g + eps * astar_heuristic(...)`
    - `vmax=None`이면 `g.vmax`(저장된 속성). E3에서는 기준 그래프의 vmax를 넘긴다.
    - `eps > 1`은 Weighted A*로, 정확성 검사 대상이 아니다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/helpers.py
def control_pair():
    """g0: s->t 1.0 km, detour s->m 5.1 km, m->t 5.2 km, all at 10 m/s (lengths >= haversine).
    g1: detour edges take 10 s each (>500 m/s), i.e. faster than g0.vmax."""
    coords = [(37.5, 127.0), (37.5, 127.0113), (37.545, 127.0)]          # s, t (~997 m east), m (~5004 m north)
    g0 = Graph(coords=coords, osm_ids=[1, 2, 3], tail=[0, 0, 2], head=[1, 2, 1],
               length=[1000.0, 5100.0, 5200.0], time=[100.0, 510.0, 520.0], hwy=["primary"] * 3)
    return g0, g0.reweighted([100.0, 10.0, 10.0])

# tests/test_astar.py
def test_astar_breaks_when_edge_faster_than_vmax():
    g0, g1 = control_pair()
    assert dijkstra(g1, 0, 1)[0] == 20.0
    assert astar(g1, 0, 1, vmax=g0.vmax)[0] == 100.0     # bound from g0 is violated -> wrong
    assert astar(g1, 0, 1)[0] == 20.0                     # bound from g1 itself is valid

def test_astar_heuristic_admissible_on_grid():
    g = grid_graph(10, 10); d = sssp(g.bwd, 99)
    assert all(astar_heuristic(g, v, 99, g.vmax) <= d[v] for v in range(g.n))

def test_astar_settles_fewer_on_grid():
    g = grid_graph(15, 15); rng = random.Random(0)
    pairs = [(rng.randrange(g.n), rng.randrange(g.n)) for _ in range(50)]
    assert sum(astar(g, s, t)[2] for s, t in pairs) < sum(dijkstra(g, s, t)[2] for s, t in pairs)

@pytest.mark.parametrize("eps", [1.2, 1.5])
def test_weighted_astar_within_eps(eps):
    g = random_geo_graph(80, 200, seed=7); rng = random.Random(1)
    for _ in range(40):
        s, t = rng.randrange(g.n), rng.randrange(g.n); opt = dijkstra(g, s, t)[0]
        if opt < math.inf: assert astar(g, s, t, eps=eps)[0] <= eps * opt + 1e-9
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_astar.py -v` → FAIL
- [ ] **Step 3: `astar.py` 구현**. 구조는 Dijkstra와 같고, `s == t`면 바로 반환한다.
- [ ] **Step 4: 통과 확인**: `pytest tests/test_astar.py tests/test_correctness.py -v` → all passed
- [ ] **Step 5: 커밋**: `git commit -m "feat: A* with graph-derived vmax and weighted variant"`
- [ ] **Step 6: 이해 확인**: `control_pair`에서 A*가 100을 내는 과정(f값 순서)을 손으로 따라간다. `docs/explain/astar.md`에 "왜 vmax가 크면 하한이 느슨해지는가"를 쓴다.
- [ ] **Step 7: AI 사용 기록**

---

### Task 7: Bidirectional Dijkstra — 담당 태형 · 리뷰 의종

**Files:**
- Create: `src/routing/bidirectional.py`
- Modify: `tests/test_correctness.py` (`EXACT_ALGOS["bidir"] = bidirectional_dijkstra`)
- Test: `tests/test_bidirectional.py`

**Interfaces:**
- Consumes: `CountingHeap`, `Stats`, `g.fwd`, `g.bwd`
- Produces: `bidirectional_dijkstra(g, s, t, *, stats=None) -> tuple[float, list[int], int]`

spec 4-2에서 고정한 결정:
- 정방향은 `g.fwd`, 역방향은 `g.bwd`를 쓴다. 매 단계 `drop_stale` 후 `top_key`가 작은 쪽을 한 번 확정한다.
- 간선 (u, v)를 검사할 때 v가 반대쪽에서 거리를 받은 상태(`< inf`)이면 `μ = min(μ, d_f[u] + w + d_b[v])`로 갱신하고 만난 간선을 기록한다.
- 종료 조건은 `top_f + top_b >= μ`이다. 처음 만났을 때 멈추면 틀린다. 한쪽 힙이 비면 `inf >= μ`로 끝난다.
- 경로는 정방향 부모(s → 만난 간선의 u)와 역방향 부모(v → t)를 이어 붙인다. settled와 trace는 양쪽 합이다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_bidirectional_not_first_meeting():
    # s=0 a=1 t=2 u=3 v=4 ; a is settled by both sides first (6.0), but 0-3-4-2 is 5.5
    g = from_edge_list(5, [(0, 1, 3), (1, 2, 3), (0, 3, 2), (3, 4, 1.5), (4, 2, 2)])
    assert bidirectional_dijkstra(g, 0, 2)[:2] == (5.5, [0, 3, 4, 2])

def test_bidirectional_one_way_uses_bwd():
    g = from_edge_list(3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)])     # one-way cycle
    assert bidirectional_dijkstra(g, 0, 2)[:2] == (2.0, [0, 1, 2])
    assert bidirectional_dijkstra(g, 2, 1)[:2] == (2.0, [2, 0, 1])
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_bidirectional.py -v` → FAIL
- [ ] **Step 3: `bidirectional.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_bidirectional.py tests/test_correctness.py -v` → all passed
- [ ] **Step 5: 커밋**: `git commit -m "feat: bidirectional Dijkstra with top_f + top_b >= mu stop"`
- [ ] **Step 6: 이해 확인**: 함정 그래프에서 "처음 만났을 때 멈추면 6.0"인 이유와 μ가 5.5로 갱신되는 시점을 손으로 적는다. `docs/explain/bidirectional.md`
- [ ] **Step 7: AI 사용 기록**

---

### Task 8: ALT (랜드마크 전처리 + 질의) — 담당 의종 · 리뷰 세현

**Files:**
- Create: `src/routing/alt.py`
- Modify: `tests/test_correctness.py` (`EXACT_ALGOS["alt4"]` 래퍼, 아래 캐시 규칙)
- Test: `tests/test_alt.py`

**Interfaces:**
- Consumes: `sssp`, `CountingHeap`, `Stats`, `H_SCALE`, `control_pair`
- Produces:
  - `@dataclass class Landmarks`의 필드: `ids: list[int]`, `d_from: list[array]`(d(L, v)), `d_to: list[array]`(d(v, L)), `prep_s: float`, `k_requested: int`
    - `k = len(ids)`, `nbytes = 2 * k * n * 8` (property)
  - `build_landmarks(g, ids) -> Landmarks`: 랜드마크마다 `sssp(g.fwd, L)`와 `sssp(g.bwd, L)`
  - `preprocess_landmarks(g, k, *, seed=0) -> Landmarks`: farthest 선택 방식
    - 시작점 r = `Random(seed).randrange(n)`
    - 첫 랜드마크 = r에서 정방향 거리가 유한한 정점 중 가장 먼 정점(r만 닿으면 r)
    - 다음 랜드마크 = 이미 고른 정점을 **제외**하고 `min_L (d_from[L][v] + d_to[L][v])`가 유한한 정점 중 최대(동점이면 작은 번호)
    - 후보가 없으면 **k보다 적게 고르고 멈춘다**(`k < k_requested` 허용).
    - `prep_s`는 선택과 SSSP를 모두 포함한 `perf_counter` 시간
  - `alt_heuristic(lm, v, t) -> float`: `H_SCALE * max(0, max_L max(d_from[L][t] - d_from[L][v], d_to[L][v] - d_to[L][t]))`
    - 피연산자 중 하나라도 `inf`인 항은 계산하지 않고 건너뛴다(Review Focus 2).
  - `alt(g, s, t, lm, *, stats=None) -> tuple[float, list[int], int]`: `lm`은 기준 그래프에서 만들고, `g`는 혼잡 그래프여도 된다(재전처리 없음).
  - 테스트용 랜드마크 캐시: `(g, lm)` 쌍을 저장하고 `cached_g is g`일 때만 재사용한다. `id(g)`를 키로 쓰지 않는다(id가 재사용되어 엉뚱한 랜드마크를 받음).

- [ ] **Step 1: 실패하는 테스트 작성**

```python
TWO_CYCLES = [(0, 1, 1), (1, 2, 1), (2, 0, 1), (3, 4, 1), (4, 5, 1), (5, 3, 1)]

def test_alt_heuristic_never_nan():                      # Review Focus 2
    g = from_edge_list(6, TWO_CYCLES); lm = build_landmarks(g, [0])
    for v in range(6):
        for t in range(6):
            h = alt_heuristic(lm, v, t); assert not math.isnan(h) and h >= 0

def test_alt_landmark_reaches_neither_endpoint():
    # landmark 0 lives in {0,1,2}; query 3->6 has two routes (3-4-6 = 2, 3-5-6 = 4)
    g = from_edge_list(7, [(0, 1, 1), (1, 2, 1), (2, 0, 1), (3, 4, 1), (4, 6, 1), (3, 5, 1), (5, 6, 3), (6, 3, 1)])
    lm = build_landmarks(g, [0])
    assert alt(g, 3, 6, lm)[:2] == (2.0, [3, 4, 6])
    assert alt(g, 0, 4, lm)[:2] == (math.inf, [])

def test_preprocess_landmarks_small_graph():
    lm = preprocess_landmarks(from_edge_list(3, [(0, 1, 0.0), (1, 2, 0.0), (0, 2, 5.0)]), 4)
    assert len(set(lm.ids)) == lm.k <= 3 and lm.k_requested == 4

def test_alt_exact_after_slowdown():
    g0 = random_geo_graph(80, 200, seed=11); lm = preprocess_landmarks(g0, 4, seed=0)
    rng = random.Random(0); g1 = g0.reweighted([t * rng.uniform(1.0, 3.0) for t in g0.time])
    for _ in range(40):
        s, t = rng.randrange(g0.n), rng.randrange(g0.n)
        assert check_result(g1, s, t, dijkstra(g1, s, t)[0], alt(g1, s, t, lm)) == []

def test_alt_breaks_after_speedup():
    g0, g1 = control_pair()
    assert alt(g1, 0, 1, build_landmarks(g0, [1]))[0] == 100.0   # true answer is 20.0

def test_landmark_nbytes():
    g = grid_graph(5, 5); assert preprocess_landmarks(g, 4).nbytes == 2 * 4 * 25 * 8

def test_alt_settles_fewer_on_grid():
    g = grid_graph(15, 15); lm = preprocess_landmarks(g, 8); rng = random.Random(0)
    pairs = [(rng.randrange(g.n), rng.randrange(g.n)) for _ in range(50)]
    assert sum(alt(g, s, t, lm)[2] for s, t in pairs) < sum(dijkstra(g, s, t)[2] for s, t in pairs)
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_alt.py -v` → FAIL
- [ ] **Step 3: `alt.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_alt.py tests/test_correctness.py -v` → all passed
- [ ] **Step 5: 커밋**: `git commit -m "feat: ALT landmarks (farthest) and query"`
- [ ] **Step 6: 이해 확인**: 삼각부등식으로 하한이 나오는 이유와 "느려지기만 하면 재전처리 없이 정확"(spec 부록 B)을 본인 말로 쓴다. `docs/explain/alt.md`
- [ ] **Step 7: AI 사용 기록**

---

### Task 9: 완전탐색 + BFS 부분 그래프 + 격자 경로 수 — 담당 세현 · 리뷰 태형

**Files:**
- Create: `src/routing/exhaustive.py`
- Test: `tests/test_exhaustive.py`

**Interfaces:**
- Consumes: `Graph.subgraph`, `largest_scc`, `dijkstra`, `check_result`
- Produces:
  - `class ExhaustiveResult(NamedTuple)`: `dist: float, path: list[int], paths: int, timed_out: bool`
  - `exhaustive_shortest(g, s, t, *, time_limit_s: float | None = 10.0) -> ExhaustiveResult`
    - 반복형 DFS로 s→t 단순 경로를 **가지치기 없이** 모두 열거하고 최솟값을 고른다.
    - 4096번 확장할 때마다 시간을 확인한다. 시간을 넘기면 그때까지의 최선과 `timed_out=True`를 돌려준다.
    - `s == t`: `(0.0, [s], 1, False)`, 도달 불가: `(inf, [], 0, False)`
  - `count_simple_paths(g, s, t) -> int`
  - `bfs_subgraph(g, root, n) -> Graph`
    - 무방향(fwd ∪ bwd) BFS 순서에서 앞 m개를 골라 유도 부분 그래프를 만들고 가장 큰 SCC로 자른다.
    - m을 n부터 1씩 늘려 SCC 크기가 n 이상이 되면 반환한다. 실제 크기는 n보다 클 수 있다.
    - `n > g.n`이면 `ValueError`
    - m이 root의 연결 성분 크기에 닿으면 그 시점의 SCC를 반환한다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
@pytest.mark.parametrize("k,count", [(3, 12), (4, 184), (5, 8512)])      # OEIS A007764
def test_grid_path_counts(k, count):
    assert count_simple_paths(grid_graph(k, k), 0, k * k - 1) == count

@pytest.mark.parametrize("seed", range(10))
def test_exhaustive_matches_dijkstra(seed):
    g = random_geo_graph(10, 15, seed=seed); rng = random.Random(seed)
    for _ in range(10):
        s, t = rng.randrange(g.n), rng.randrange(g.n); r = exhaustive_shortest(g, s, t)
        assert not r.timed_out and check_result(g, s, t, dijkstra(g, s, t)[0], (r.dist, r.path, 0)) == []

def test_exhaustive_timeout():
    assert exhaustive_shortest(grid_graph(7, 7), 0, 48, time_limit_s=0.05).timed_out

def test_bfs_subgraph_strongly_connected():
    g = grid_graph(10, 10); sub = bfs_subgraph(g, 0, 12)
    assert sub.n >= 12 and len(largest_scc(sub)) == sub.n and set(sub.osm_ids) <= set(g.osm_ids)

def test_bfs_subgraph_too_large():
    with pytest.raises(ValueError):
        bfs_subgraph(grid_graph(3, 3), 0, 10)
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_exhaustive.py -v` → FAIL
- [ ] **Step 3: `exhaustive.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_exhaustive.py -v` → all passed
- [ ] **Step 5: 커밋**: `git commit -m "feat: exhaustive search, simple path counting, BFS subgraph"`
- [ ] **Step 6: 이해 확인**: 3×3 격자의 12개 경로를 직접 나열해 본다. `docs/explain/exhaustive.md`에 "경로 수가 왜 지수적으로 늘어나는가"를 쓴다.
- [ ] **Step 7: AI 사용 기록**

---

### Task 10: 질의 생성·저장 — 담당 태형 · 리뷰 세현

**Files:**
- Create: `src/routing/queries.py`
- Test: `tests/test_queries.py`

**Interfaces:**
- Consumes: `haversine_m`, `Graph.index_of`
- Produces:
  - `BINS_M = [(0, 3000, "<3km"), (3000, 10000, "3-10km"), (10000, math.inf, ">10km")]`: s–t 직선(haversine) 거리 기준. 계획 작성자의 판단이다(알고리즘과 무관하고 계산이 싸다).
  - `class Query(NamedTuple)`: `qid: int, bin: str, s: int, t: int, crow_m: float`
  - `make_queries(g, *, per_bin=100, seed=42, bins=BINS_M, max_tries=200_000) -> list[Query]`
    - `Random(seed)`로 s ≠ t 쌍을 뽑아 구간에 채운다.
    - `max_tries`에 닿으면 멈추고, 덜 찬 구간마다 `warnings.warn(UserWarning)`
  - `save_queries(path, g, qs)`: CSV `qid,bin,s_osm,t_osm,crow_m`
  - `load_queries(path, g) -> list[Query]`: 그래프에 없는 osm_id가 있으면 `KeyError("graph version mismatch: osm_id ...")`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
SMALL = [(0, 300, "a"), (300, 700, "b")]

def test_deterministic_and_binned():
    g = grid_graph(10, 10)
    q1, q2 = make_queries(g, per_bin=20, bins=SMALL, seed=1), make_queries(g, per_bin=20, bins=SMALL, seed=1)
    assert q1 == q2 and len(q1) == 40
    assert all((q.crow_m < 300) == (q.bin == "a") for q in q1)

def test_unfillable_bin_warns():                          # Review Focus 5
    with pytest.warns(UserWarning, match=">10km"):
        qs = make_queries(grid_graph(5, 5), per_bin=5, max_tries=5_000)
    assert not any(q.bin == ">10km" for q in qs)

def test_save_load_roundtrip(tmp_path):
    g = grid_graph(6, 6); qs = make_queries(g, per_bin=5, bins=SMALL)
    save_queries(tmp_path / "q.csv", g, qs)
    assert [(q.s, q.t) for q in load_queries(tmp_path / "q.csv", g)] == [(q.s, q.t) for q in qs]

def test_load_rejects_other_graph(tmp_path):
    g = grid_graph(6, 6); save_queries(tmp_path / "q.csv", g, make_queries(g, per_bin=5, bins=SMALL))
    with pytest.raises(KeyError, match="graph version mismatch"):
        load_queries(tmp_path / "q.csv", grid_graph(2, 2))
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_queries.py -v` → FAIL
- [ ] **Step 3: `queries.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_queries.py -v` → 4 passed
- [ ] **Step 5: 커밋, 병합, 알림**: `git commit -m "feat: distance-binned query sets saved by osm_id"`
- [ ] **Step 6: AI 사용 기록**

---

### Task 11: 벤치 하네스 — 담당 태형 · 리뷰 세현

**Files:**
- Create: `src/routing/bench.py`
- Test: `tests/test_bench.py`

**Interfaces:**
- Consumes: 모든 알고리즘, `Landmarks`, `Query`
- Produces:
  - `Algo = Callable[..., tuple[float, list[int], int]]`: 호출 형태는 `algo(g, s, t, stats=Stats())`
  - `standard_algos(g_bound, *, ks=(4, 8, 16), seed=0) -> tuple[dict[str, Algo], dict[int, Landmarks]]`
    - 키: `"dijkstra", "astar", "bidir", "alt4", "alt8", "alt16"`
    - A*는 `vmax = g_bound.vmax`를 **실수로 한 번 묶어** 쓴다. ALT는 `g_bound`에서 만든 랜드마크를 쓴다.
    - 질의 그래프는 `g_bound`와 달라도 된다.
  - `class Row(NamedTuple)`: `graph, scenario, kind, qid, bin, algo, time_s, dist, settled, relaxed, pushes, pops`
  - `time_all(g, queries, algos, *, graph, scenario="free", kind="full", warmup=5, repeats=3) -> list[Row]`
    - 워밍업: 앞 `warmup`개 질의를 모든 알고리즘으로 **추가로** 한 번씩 돌리고 버린다.
    - 측정: **모든** 질의 × 알고리즘마다 `gc.disable()` → `perf_counter`로 `repeats`번 → 중앙값 → `gc.enable()`
    - 카운터는 첫 실행 값을 쓴다.
  - `summarize(rows) -> list[dict]`: (graph, scenario, kind, bin, algo)별 `n, median_s, p95_s, median_settled, speedup, settled_ratio`
    - `speedup = median_s(dijkstra) / median_s(algo)`
    - `settled_ratio = median_settled(algo) / median_settled(dijkstra)`
  - `write_csv(path, rows)`: dict와 NamedTuple(`_asdict`)을 모두 받는다.
  - `class ExactnessError(Exception)`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_time_all_times_every_query():
    g = grid_graph(8, 8); qs = make_queries(g, per_bin=10, bins=[(0, 2000, "a")])
    algos, _ = standard_algos(g, ks=(4,))
    rows = time_all(g, qs, algos, graph="grid", warmup=5)
    assert len(rows) == len(qs) * len(algos)              # warm-up runs are extra, not subtracted

def test_summarize_ratios():
    g = grid_graph(8, 8); qs = make_queries(g, per_bin=10, bins=[(0, 2000, "a")])
    algos, _ = standard_algos(g, ks=(4,))
    s = {r["algo"]: r for r in summarize(time_all(g, qs, algos, graph="grid"))}
    assert s["dijkstra"]["speedup"] == 1.0 and s["dijkstra"]["settled_ratio"] == 1.0
    assert s["alt4"]["median_settled"] <= s["dijkstra"]["median_settled"]

def test_write_csv_accepts_dicts_and_rows(tmp_path):
    write_csv(tmp_path / "a.csv", [{"x": 1}]); write_csv(tmp_path / "b.csv", [Row(*range(12))])
    assert (tmp_path / "b.csv").read_text().splitlines()[0].startswith("graph,scenario,kind")
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_bench.py -v` → FAIL
- [ ] **Step 3: `bench.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_bench.py -v` → 3 passed
- [ ] **Step 5: 커밋, 병합, 알림**: `git commit -m "feat: bench harness (standard_algos, time_all, summarize)"`
- [ ] **Step 6: AI 사용 기록**

---

### Task 12: 정확성 관문 스크립트 + 관문 실행 — 담당 세현 · 리뷰 태형

**Files:**
- Create: `src/routing/gate.py`, `scripts/check_exact.py`
- Test: `tests/test_gate.py`

**Interfaces:**
- Consumes: `load_graph`, `load_queries`/`make_queries`/`save_queries`, `standard_algos`, `verify_all`
- Produces:
  - `run_gate(graph_path, queries_path, *, algos=None) -> tuple[int, list[str]]`
    - 질의 CSV가 없으면 `make_queries`로 만들어 저장한다.
    - 반환값: (불일치가 없으면 0 아니면 1, 메시지 목록)
  - CLI: `python scripts/check_exact.py GRAPH_PKL QUERIES_CSV`
    - 성공: `ALL EXACT: {n} queries x {k} algos` 출력, 종료 코드 0
    - 실패: 불일치를 출력하고 종료 코드 1

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_gate_passes_and_creates_queries(tmp_path):
    save_graph(grid_graph(8, 8), tmp_path / "g.pkl")
    code, msgs = run_gate(tmp_path / "g.pkl", tmp_path / "q.csv")
    assert code == 0 and msgs == [] and (tmp_path / "q.csv").exists()

def test_gate_fails_on_wrong_algo(tmp_path):
    save_graph(grid_graph(6, 6), tmp_path / "g.pkl")
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (0.5, [s, t], 0)}
    assert run_gate(tmp_path / "g.pkl", tmp_path / "q.csv", algos=bad)[0] == 1
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_gate.py -v` → FAIL
- [ ] **Step 3: `gate.py`, `check_exact.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_gate.py -v` → 2 passed
- [ ] **Step 5: 관문 실행 (11/1)**: `python scripts/check_exact.py data/graphs/gangnam_graph_v1.pkl data/queries/gangnam_q_seed42.csv` → `ALL EXACT`
  - 실패하면 시간 측정을 멈추고 버그부터 고친다(spec 10장).
  - 강남구의 >10 km 구간은 경고 없이 채워지는 것이 정상이다.
- [ ] **Step 6: 관문 실행 (11/3)**: gss와 seoul에 같은 명령 → `ALL EXACT`. 서울이 너무 느리면 3개 구를 최대 규모로 삼고 발표에서 밝힌다.
- [ ] **Step 7: 커밋**: `git add data/queries` 포함, `git commit -m "feat: exactness gate; query sets"`
- [ ] **Step 8: AI 사용 기록**

---

### Task 13: E1 실행 + 그림 (a) — 담당 세현 · 리뷰 태형

**Files:**
- Create: `src/routing/experiments/__init__.py`, `src/routing/experiments/e1.py`, `scripts/run_e1.py`
- Modify: `src/routing/figures.py`(`fig_a` 추가, `FIGURES` 사전에 `"a"` 등록), `scripts/make_figures.py`. 두 파일은 Task 17이 먼저 만들었다(10/30).
- Test: `tests/test_experiments.py`

**Interfaces:**
- Consumes: `bfs_subgraph`, `exhaustive_shortest`, `count_simple_paths`, `dijkstra`, `Graph.nearest`, `ExactnessError`
- Produces:
  - `GANGNAM_STATION = (37.4979, 127.0276)`: BFS 루트는 이 좌표에서 가장 가까운 정점(계획 작성자의 판단)
  - `run_e1(g, root, *, start_n=10, step=2, per_size=20, time_limit_s=10.0, max_n=200) -> list[dict]`
    - 행 = `target_n, actual_n, actual_m, qid, ex_time_s, ex_paths, timed_out, dij_time_s`
    - 크기마다 `Random(target_n)`으로 s ≠ t 질의 20개
    - 시간 초과가 아니면 거리 일치를 확인하고, 불일치면 `ExactnessError`
    - `actual_n`이 직전 크기와 같으면 그 크기는 건너뛴다(그림에 같은 점이 반복되지 않도록).
    - 질의가 하나라도 시간 초과한 크기까지 기록하고 멈춘다. `target_n > min(max_n, g.n)`이면 시간 초과가 없어도 멈춘다.
  - `grid_counts() -> list[dict]`: k = 3, 4, 5는 직접 센 값, 6·7은 OEIS 값 `1_262_816`, `575_780_564`(출처 표기). 결과는 `results/e1_grid.csv`
  - `fig_a(e1_csv, out_png)`: x = actual_n, y = 완전탐색 시간 중앙값(로그축)과 Dijkstra 시간, 시간 초과 표시. 출력은 `figures/fig_a_exhaustive.png`
  - CLI: `python scripts/run_e1.py data/graphs/gangnam_graph_v1.pkl` → `results/e1.csv`, `results/e1_grid.csv`
  - CLI: `python scripts/make_figures.py a` (이후 Task에서 b, c, d, f, g, all 추가)

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_run_e1_stops_at_first_timeout():
    rows = run_e1(grid_graph(8, 8), 0, start_n=6, per_size=3, time_limit_s=0.02, max_n=64)
    last = max(r["target_n"] for r in rows)
    assert any(r["timed_out"] for r in rows if r["target_n"] == last)
    assert not any(r["timed_out"] for r in rows if r["target_n"] < last)

def test_run_e1_actual_sizes_strictly_increase():
    rows = run_e1(grid_graph(8, 8), 0, start_n=6, per_size=2, time_limit_s=0.02, max_n=64)
    sizes = sorted({(r["target_n"], r["actual_n"]) for r in rows})
    assert all(a[1] < b[1] for a, b in zip(sizes, sizes[1:]))

def test_grid_counts_values():
    assert [r["paths"] for r in grid_counts()] == [12, 184, 8512, 1262816, 575780564]
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_experiments.py -k e1 -v` → FAIL
- [ ] **Step 3: `e1.py`, `fig_a`, 스크립트 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_experiments.py -v` → passed
- [ ] **Step 5: 실행**: `python scripts/run_e1.py data/graphs/gangnam_graph_v1.pkl && python scripts/make_figures.py a` → 그림이 생기고 포기 지점 n이 출력된다(검토 시제품에서 1초 제한일 때 n ≈ 68).
- [ ] **Step 6: 커밋**: `git commit -m "feat: E1 exhaustive limit experiment and figure (a)"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 14: E2 실행 + 그림 (b) + 하한 느슨함 측정 — 담당 태형 · 리뷰 의종

**Files:**
- Create: `src/routing/experiments/e2.py`, `scripts/run_e2.py`
- Modify: `src/routing/figures.py` (`fig_b`), `scripts/make_figures.py`
- Test: `tests/test_experiments.py`

**Interfaces:**
- Consumes: `standard_algos`, `verify_all`, `time_all`, `summarize`, `load_queries`, `astar_heuristic`, `alt_heuristic`
- Produces:
  - `run_e2(g, queries, *, graph, ks=(4, 8, 16), algos=None) -> tuple[list[Row], list[dict], list[dict]]`
    - `algos=None`이면 `standard_algos(g, ks=ks)`
    - 먼저 `verify_all`을 돌리고, 불일치가 있으면 `ExactnessError`(시간 측정 없음)
    - 두 번째 반환값(ALT 전처리 행): `graph, k, k_actual, prep_s, nbytes, breakeven`
      - `breakeven = prep_s / (median_s(dijkstra) − median_s(alt_k))`. 중앙값은 **모든 질의**(구간 구분 없이) 기준이고, 분모가 0 이하면 `inf`
    - 세 번째 반환값(하한 느슨함 행): `graph, qid, bin, algo, h0, dist, ratio`
      - `h0`: astar는 `astar_heuristic(g, s, t, vmax)`, alt_k는 `alt_heuristic(lm_k, s, t)`
      - `ratio = h0 / dist` (0~1, 1에 가까울수록 하한이 빡빡함). Q&A의 "A*가 생각보다 안 빠른 이유"를 숫자로 보이는 근거다.
  - CLI: `python scripts/run_e2.py gangnam gss seoul` → `results/e2_{graph}.csv`, `results/e2_alt_prep.csv`, `results/e2_tightness.csv`, `results/e2_summary.csv`
  - `fig_b(summary_csv, tightness_csv, out_png)`: 그래프 규모별 패널
    - 위: 거리 구간별 settled 비율(주 지표, 머신과 무관)
    - 가운데: speedup
    - 아래: 하한 비율 중앙값
    - 강남구 >10 km 구간에는 "corner pairs only" 주석
    - 출력은 `figures/fig_b_speedup.png`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_run_e2_smoke():
    g = grid_graph(12, 12); qs = make_queries(g, per_bin=10, bins=[(0, 500, "a"), (500, 2000, "b")])
    rows, prep, tight = run_e2(g, qs, graph="grid", ks=(4,))
    assert {r.algo for r in rows} == {"dijkstra", "astar", "bidir", "alt4"}
    assert prep[0]["k"] == 4 and prep[0]["breakeven"] > 0
    assert all(0 <= r["ratio"] <= 1 for r in tight) and {r["algo"] for r in tight} == {"astar", "alt4"}

def test_run_e2_refuses_to_time_wrong_algo():
    g = grid_graph(6, 6); qs = make_queries(g, per_bin=5, bins=[(0, 1000, "a")])
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (0.5, [s, t], 0)}
    with pytest.raises(ExactnessError):
        run_e2(g, qs, graph="grid", algos=bad)
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_experiments.py -k e2 -v` → FAIL
- [ ] **Step 3: `e2.py`, `fig_b`, 스크립트 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_experiments.py -v` → passed
- [ ] **Step 5: 실행 (11/3, Task 12 서울 관문 통과 후)**: `caffeinate -i nohup python scripts/run_e2.py gangnam gss seoul > results/e2.log 2>&1 &` → `python scripts/make_figures.py b`
  - 3회 반복 측정이라 서울 포함 몇 시간이 걸릴 수 있으므로 밤에 돌린다.
- [ ] **Step 6: 커밋**: `git commit -m "feat: E2 speedup, heuristic tightness, figure (b)"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 15: 혼잡 시나리오 — 담당 의종 · 리뷰 세현

**Files:**
- Create: `src/routing/congestion.py`
- Test: `tests/test_congestion.py`

**Interfaces:**
- Consumes: `Graph.reweighted`, `dijkstra`
- Produces:
  - `hwy_class(h) -> str`: `"*_link"`는 기본 등급으로 바꾸고, `motorway, trunk, primary, secondary, tertiary`가 아니면 `"other"`
  - `SYNTH_PROFILES`: 등급별 배율(모두 1 이상). 값은 계획 작성자의 판단이며 발표에서 "가정 배율"로 밝힌다.

    | 시각 | motorway | trunk | primary | secondary | tertiary | other |
    |---|---|---|---|---|---|---|
    | `"03"` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
    | `"08"` | 1.6 | 1.8 | 2.0 | 1.8 | 1.5 | 1.2 |
    | `"18"` | 1.8 | 2.0 | 2.2 | 1.9 | 1.6 | 1.3 |

  - `synthetic(g0, hour) -> Graph`
  - `random_slowdown(g0, *, frac=0.3, factor=2.0, seed=0) -> Graph`: 정확히 `round(frac * m)`개 간선을 ×2
  - `control_speedup(g0, *, factor=0.5, frac_other=0.1, seed=0) -> Graph`
    - `hwy_class`가 motorway·trunk인 간선(`*_link` 포함) 전부와 나머지 중 무작위 10%의 시간을 ×0.5로 줄인다.
    - 속도가 2배가 되어 vmax를 넘으므로 A*도 깨진다(시제품: 강남구에서 A* 300개 중 49개 오답).
  - `standard_scenarios(g0, *, seed=0) -> dict[str, Graph]`: `{"synth03", "synth08", "synth18", "random30", "control"}`
  - `lower_bound(g0, scenarios) -> Graph`: 간선별 시간의 최솟값. A* vmax와 ALT 랜드마크는 이 그래프로 만든다(spec 부록 B의 "관측 최고 속도" 방식). 합성 시나리오만 있으면 g0와 같다.
  - `midpoint(g0, s, t) -> int`: 자유류 Dijkstra 경로에서 누적 시간이 처음으로 절반 이상이 되는 정점, 즉 재탐색 시점의 "현재 위치". 경로 정점이 2개 이하면 s.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_slowdowns_never_faster():
    g = random_geo_graph(60, 150, seed=2); sc = standard_scenarios(g)
    for name in ("synth03", "synth08", "synth18", "random30"):
        assert all(a >= b for a, b in zip(sc[name].time, g.time)), name

def test_random30_count():
    g = random_geo_graph(60, 150, seed=2); h = random_slowdown(g)
    assert sum(a == 2 * b for a, b in zip(h.time, g.time)) == round(0.3 * g.m)

def test_control_exceeds_vmax_and_includes_links():
    g = grid_graph(4, 4, hwy="motorway_link"); h = control_speedup(g)
    assert h.vmax > g.vmax and all(a == 0.5 * b for a, b in zip(h.time, g.time))

def test_link_class():
    assert hwy_class("primary_link") == "primary" and hwy_class("living_street") == "other"

def test_lower_bound_and_midpoint():
    g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 3, 2)])
    assert lower_bound(g, [g.reweighted([2, 0.5, 2])]).time == [1, 0.5, 2] and midpoint(g, 0, 3) == 2
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_congestion.py -v` → FAIL
- [ ] **Step 3: `congestion.py` 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_congestion.py -v` → 5 passed
- [ ] **Step 5: 커밋, 병합, 알림**: `git commit -m "feat: synthetic/random/control congestion scenarios"`
- [ ] **Step 6: 이해 확인**: "대조군에서 A*는 vmax를 넘을 때만, ALT는 자유류보다 빨라지기만 해도 깨진다"를 `control_pair`로 설명한다. `docs/explain/congestion.md`
- [ ] **Step 7: AI 사용 기록**

---

### Task 16: E3 실행 + 그림 (c)(d) + 서버 환산 — 담당 의종 · 리뷰 세현

**Files:**
- Create: `src/routing/experiments/e3.py`, `scripts/run_e3.py`
- Modify: `src/routing/figures.py` (`fig_c`, `fig_d`), `scripts/make_figures.py`
- Test: `tests/test_experiments.py`

**Interfaces:**
- Consumes: `standard_scenarios`, `synthetic`, `lower_bound`, `midpoint`, `standard_algos`, `verify_all`, `time_all`, `astar(eps=...)`, `ExactnessError`
- Produces:
  - `run_e3(g0, queries, *, graph, scenarios, ks=(4, 8, 16), eps=(1.2, 1.5)) -> dict[str, list]`
    - 공통: `g_lb = lower_bound(g0, [control을 뺀 시나리오])`. `standard_algos(g_lb)`를 **한 번만** 만들어 모든 시나리오에 재사용한다(재전처리 없음).
    - `"accuracy"`: 모든 시나리오 × 정확 알고리즘마다 `scenario, algo, n, n_wrong, max_rel_err`. control은 틀려도 기록만 한다.
    - `"timing"`: control이 아닌 시나리오에서 정확 알고리즘의 `n_wrong`이 하나라도 있으면 `ExactnessError`(이론상 정확해야 하므로 버그). 없으면 `time_all(kind="full")`
    - `"reroute"`: control이 아닌 시나리오에서 질의를 `(midpoint(g0, s, t), t)`로 바꿔 검사한 뒤 `time_all(kind="reroute")`
    - `"wastar"`: control이 아닌 시나리오 × eps마다 `scenario, eps, median_s, speedup_vs_astar, mean_ratio, max_ratio` (ratio = dist / opt)
  - `server_ratio(reroute_rows) -> list[dict]`: `scenario, algo, median_reroute_s, ratio`
    - `ratio = median_reroute_s / median_reroute_s(dijkstra)`
    - "1만 대 10초 재탐색에 필요한 서버 수의 Dijkstra 대비 비율"이다. 출력은 `results/server_ratio.csv`
  - CLI: `python scripts/run_e3.py gss seoul` → `results/e3_{graph}_{accuracy,timing,reroute,wastar}.csv`
  - `fig_c(accuracy_csvs, timing_csvs, out_png)`: 시나리오별 정확도(% exact) 패널과 speedup·settled 비율 패널. control에서 A*와 ALT가 틀리는 것이 보여야 한다. 출력은 `figures/fig_c_congestion.png`
  - `fig_d(alt_prep_csv, e3_timing_csv, out_png)`: x = k (4, 8, 16), 전처리 시간·인덱스 MB(`e2_alt_prep.csv`)와 synth08 speedup(`e3_gss_timing.csv`), breakeven 표시. 출력은 `figures/fig_d_alt_tradeoff.png`
  - 주의: `--real`(Task 21)을 켜면 `g_lb`가 바뀌어 합성 시나리오 수치도 달라진다. 발표에는 Task 22 최종 실행 하나의 수치만 쓴다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_run_e3_smoke():
    g = grid_graph(10, 10, hwy="primary"); qs = make_queries(g, per_bin=8, bins=[(0, 1500, "a")])
    out = run_e3(g, qs, graph="grid", scenarios=standard_scenarios(g), ks=(4,))
    acc = {(r["scenario"], r["algo"]): r for r in out["accuracy"]}
    assert all(acc[(sc, a)]["n_wrong"] == 0 for sc in ("synth08", "random30") for a in ("dijkstra", "astar", "bidir", "alt4"))
    assert all(r["max_ratio"] <= r["eps"] + 1e-9 for r in out["wastar"])
    assert {r.kind for r in out["reroute"]} == {"reroute"}

def test_server_ratio_dijkstra_is_one():
    g = grid_graph(8, 8); qs = make_queries(g, per_bin=5, bins=[(0, 1500, "a")])
    out = run_e3(g, qs, graph="grid", scenarios={"synth08": synthetic(g, "08")}, ks=(4,))
    assert {r["algo"]: r["ratio"] for r in server_ratio(out["reroute"])}["dijkstra"] == 1.0
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_experiments.py -k e3 -v` → FAIL
- [ ] **Step 3: `e3.py`, `fig_c`, `fig_d`, `server_ratio` 구현**
- [ ] **Step 4: 통과 확인**: `pytest -v` → all passed
- [ ] **Step 5: 실행 (11/4)**: `python scripts/run_e3.py gss seoul && python scripts/make_figures.py c d`
- [ ] **Step 6: 커밋**: `git commit -m "feat: E3 congestion accuracy, reroute cost, ALT trade-off"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 17: 탐색 공간 그림 (f) — 담당 태형 · 리뷰 의종

영상에서 "같은 입력, 다른 방식"(슬라이드 22·23)을 가장 직관적으로 보여 주는 그림이다.

**Files:**
- Modify: `src/routing/figures.py` (`collect_trace`, `fig_f`), `scripts/make_figures.py`
- Test: `tests/test_figures.py`

**Interfaces:**
- Consumes: `Stats.trace`, `standard_algos`, `Graph.nearest`, 강남구 그래프
- Produces:
  - `collect_trace(algo, g, s, t) -> tuple[list[int], list[int]]`: (확정 정점 순서, 경로)
  - `fig_f(g, s, t, algos: dict[str, Algo], out_png)`
    - 패널은 dijkstra, astar, bidir, alt16
    - 도로망은 옅은 회색 간선, 확정 정점은 점, 경로는 굵은 선
    - 제목은 `"{algo}: {settled} settled"`
    - 기본 질의는 강남역(37.4979, 127.0276) → 삼성역(37.5088, 127.0631)의 최근접 정점(계획 작성자의 판단)
    - 출력은 `figures/fig_f_search_space.png`
- matplotlib 백엔드는 `Agg`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_collect_trace_matches_settled():
    g = grid_graph(10, 10); algos, _ = standard_algos(g, ks=(4,))
    for name, algo in algos.items():
        trace, path = collect_trace(algo, g, 0, 99)
        assert len(trace) == algo(g, 0, 99)[2] and path[0] == 0 and path[-1] == 99, name

def test_fig_f_writes_png(tmp_path):
    g = grid_graph(10, 10); algos, _ = standard_algos(g, ks=(4,))
    fig_f(g, 0, 99, algos, tmp_path / "f.png"); assert (tmp_path / "f.png").stat().st_size > 0
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_figures.py -v` → FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_figures.py -v` → 2 passed
- [ ] **Step 5: 실행**: `python scripts/make_figures.py f` → 강남구 그림. 4개 패널의 settled 수가 E2 경향(ALT < A* < Dijkstra)과 맞는지 눈으로 확인한다.
- [ ] **Step 6: 커밋**: `git commit -m "feat: search-space figure (f)"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 18: 데이터 설명 그림 (g) + 그래프 표 — 담당 세현 · 리뷰 태형

spec 7장 11/4 "데이터 설명 자료(지도, 그래프 크기)"와 파트 1·3의 규모 사다리를 위한 자료다.

**Files:**
- Modify: `src/routing/figures.py` (`graph_table`, `fig_g`), `scripts/make_figures.py`
- Test: `tests/test_figures.py`

**Interfaces:**
- Consumes: Task 5 `.meta.json`, `.graphml`, `hwy_class`
- Produces:
  - `graph_table(meta_paths) -> list[dict]`: `name, n, m, vmax_kph, maxspeed_missing_ratio`. 출력은 `results/graph_table.csv`
  - `fig_g(graphml_paths, out_png)`: 강남구·3개 구·서울 3개 패널, 간선 색 = `hwy_class`, 공통 범례. 출력은 `figures/fig_g_graphs.png`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_graph_table_from_meta(tmp_path):
    p = tmp_path / "x_graph_v1.meta.json"
    p.write_text(json.dumps({"name": "x", "n": 10, "m": 20, "vmax_mps": 20.0, "maxspeed_missing_ratio": 0.9}))
    assert graph_table([p]) == [{"name": "x", "n": 10, "m": 20, "vmax_kph": 72.0, "maxspeed_missing_ratio": 0.9}]
```

- [ ] **Step 2: 실패 확인** → **Step 3: 구현** → **Step 4: 통과 확인**: `pytest tests/test_figures.py -v`
- [ ] **Step 5: 실행**: `python scripts/make_figures.py g` → 그림과 표. 표에 maxspeed 결측 비율이 들어간다(Task 5 참고).
- [ ] **Step 6: 커밋**: `git commit -m "feat: data description figure (g) and graph table"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 19: 현업·문헌 조사 + 공정성 — 담당 의종 (안) · 리뷰 태형

발표 파트 2(현업 해결 방식)와 파트 4("산업계 결과와 일치했나")가 요구하는 자료다. 코드가 아니므로 테스트 대신 **원문 확인**이 통과 기준이다.

**Files:**
- Create: `docs/industry.md`

**산출물 (`docs/industry.md`):**
- **표 1. 누가, 무엇을, 왜**: `분야·서비스 | 최적화 대상(속도/비용/정확도/공정성) | 알고리즘 | 근거(원문 URL, 쪽·절) | 확인자`
  - 후보는 spec 부록 C의 OSRM·GraphHopper(CH, Landmark), Bing Maps(CRP), Bast et al. 서베이다.
  - 국내 기업(쿠팡이츠, 배민, Tmap, 카카오)은 알고리즘을 공개하지 않았으므로 "X사가 Y를 쓴다"고 쓰지 않는다(spec 8장). "이런 문제를 겪는다" 수준까지만 쓴다.
- **표 2. 문헌 수치 vs 우리 측정**: `문헌 | 그래프(규모) | 기법 | 문헌의 Dijkstra 대비 가속비·탐색량 | 우리 값(results/e2_summary.csv) | 같은 경향인가`
  - 문헌 값은 원문 표에서 옮긴다(예: Bast et al. 2016의 기법 비교표, Goldberg & Harrelson 2005의 ALT 실험).
  - 우리 값은 Task 14 이후에 채운다.
- **공정성 절 (반 쪽)**
  - 내용: 사용자 최적(각자 최단) vs 시스템 최적, 모두 같은 우회로로 몰리는 문제
  - 근거: Roughgarden & Tardos, *How Bad is Selfish Routing?* (J. ACM 2002), 원문 확인 후 인용
  - E4의 보급률 30% vs 100% 비교와 연결하고, Python 쪽에서는 다루지 않는다는 한계를 적는다.
- **파트 2 슬라이드 구성안**: 3분 분량, 표 1을 기반으로

- [ ] **Step 1**: 후보 문헌·문서 원문을 읽고 표 1 초안을 쓴다(10/30~11/1). 출처마다 URL과 쪽·절을 적는다.
- [ ] **Step 2**: 표 2에 문헌 수치를 넣는다(11/2).
- [ ] **Step 3**: 공정성 절을 쓴다(11/2).
- [ ] **Step 4: 원문 확인 (리뷰)**: 리뷰 담당이 모든 행의 URL을 열어 주장과 원문이 맞는지 확인하고 `확인자` 칸에 이니셜을 적는다. 확인되지 않은 행은 지운다.
- [ ] **Step 5**: Task 14 결과로 표 2의 "우리 값"과 "같은 경향인가"를 채운다(11/4).
- [ ] **Step 6: 커밋**: `git commit -m "docs: industry practice, literature comparison, fairness"`
- [ ] **Step 7: AI 사용 기록**: AI로 찾은 문헌은 반드시 원문을 확인한다. AI가 지어낸 레퍼런스 금지(슬라이드 30).

---

### Task 20: 표준노드링크 매칭 (우선순위 4, 결정 기한 11/2) — 담당 세현 · 리뷰 의종

**사전 작업(사람이 직접):** ITS 국가교통정보센터에서 표준노드링크 SHP를 내려받아 `data/nodelink/MOCT_LINK.shp`에 둔다.

**Files:**
- Create: `src/routing/speeds/match.py`, `scripts/match_links.py`
- Modify: `tests/test_speeds.py`

**Interfaces:**
- Consumes: Task 5 graphml, `BBOX_GSS`, Task 2 `coverage_day1.txt`
- Produces:
  - `load_links(shp_path, bbox) -> GeoDataFrame`: 컬럼 `LINK_ID, F_NODE, T_NODE, geometry`. `.prj`로 좌표계를 읽고, 없으면 `EPSG:5186`으로 가정한 뒤 `to_crs(4326)`하고 bbox로 자른다.
  - `osm_edges(graphml_path) -> GeoDataFrame`: `ox.graph_to_gdfs(G, nodes=False)`를 `reset_index()`한 것. 컬럼 `u, v, key, highway, length, geometry`
  - `match_edges(edges, links, *, buffer_m=15.0, max_bearing_diff=30.0, min_overlap=0.5) -> DataFrame`: 출력 컬럼 `u_osm, v_osm, link_id, overlap`
    - 둘 다 `EPSG:5179`(미터)로 투영한다.
    - OSM 간선 버퍼 안에 들어오는 링크 중 시작→끝 방위각 차이(360° 순환 처리)가 30° 이하인 것을 후보로 한다.
    - `overlap = (링크 ∩ 간선 버퍼) 길이 / 간선 길이`가 최대인 하나를 고른다. `min_overlap` 미만이면 매칭하지 않는다.
  - `coverage(edges, matched) -> dict[str, float]`: 등급별 매칭된 길이 비율
  - CLI: `python scripts/match_links.py gss` → `data/speeds/match_gss_v1.csv`, 등급별 커버리지, `figures/match_check.png`(무작위 매칭 20개를 겹쳐 그린 확인용 그림)
- **채택 기준**(계획 작성자의 판단): motorway·trunk·primary·secondary 길이 기준 매칭률이 70% 이상이고, `match_check.png`의 20개가 눈으로 보기에 맞으면 채택한다.
- `results/match_decision.md`의 첫 줄을 `ADOPT` 또는 `REJECT`로 쓰고 이유를 한 줄 덧붙인다. Task 22가 이 첫 줄을 읽는다.

- [ ] **Step 1: 실패하는 테스트 작성** (값은 EPSG:5179에서 확인함: E 길이 203 m, far 거리 100 m, a·b 방위각 358.3°·2.3°, 겹침 1.0)

```python
def gdf(lines, **cols):
    return gpd.GeoDataFrame(cols, geometry=[LineString(l) for l in lines], crs="EPSG:4326")

E = [(127.0000, 37.5000), (127.0023, 37.5000)]                 # ~203 m, bearing ~90°
def edges(line=E): return gdf([line], u=[1], v=[2], key=[0], highway=["primary"], length=[203.0])
def links(*lines): return gdf(list(lines), LINK_ID=[f"L{i}" for i in range(len(lines))])

def test_match_same_direction():
    m = match_edges(edges(), links(E))
    assert list(m.link_id) == ["L0"] and m.overlap.iloc[0] >= 0.9

def test_reject_opposite_direction():
    assert match_edges(edges(), links(E[::-1])).empty

def test_reject_far_link():
    assert match_edges(edges(), links([(x, y + 0.0009) for x, y in E])).empty   # ~100 m north

def test_bearing_wraparound():
    a = [(127.0, 37.5), (126.99992, 37.5018)]                   # ~358°
    b = [(127.0, 37.5), (127.00008, 37.5018)]                   # ~2°
    assert list(match_edges(edges(a), links(b)).link_id) == ["L0"]
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_speeds.py -k match -v` → FAIL
- [ ] **Step 3: `match.py`, 스크립트 구현**
- [ ] **Step 4: 통과 확인**: `pytest tests/test_speeds.py -v` → passed
- [ ] **Step 5: 실행 후 결정 (11/2)**: `python scripts/match_links.py gss` → `results/match_decision.md` 작성, 팀에 공유
- [ ] **Step 6: 커밋**: `git commit -m "feat: standard node-link to OSM edge matching"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 21: 실제 속도 스냅샷 → E3 시나리오 (우선순위 4, `ADOPT`일 때만) — 담당 의종 · 리뷰 세현

**Files:**
- Create: `src/routing/speeds/snapshot.py`
- Modify: `scripts/run_e3.py` (`--real` 플래그, gss 전용), `tests/test_speeds.py`

**Interfaces:**
- Consumes: `parse_items`, Task 20 매칭 CSV, `Graph`, `hwy_class`, `lower_bound`, `run_e3`
- Produces:
  - `link_speeds(raw_dir, hour: int) -> dict[str, float]`: 파일명의 수집 시각(HHMMSS)이 그 시(hour)에 속하는 모든 수집분에서 링크별 속도 중앙값(km/h). `createdDate` 형식에 의존하지 않으려고 수집 시각을 쓴다(계획 작성자의 판단).
  - `real_scenario(g0, match_df, speeds, *, min_speed_kph=3.0) -> tuple[Graph, dict]`
    - 매칭된 간선: `time = length / (max(speed, 3) / 3.6)`
    - 매칭 안 된 간선: `time0 × r_c`. r_c는 같은 등급 매칭 간선의 `time / time0` 중앙값이고, 그 등급에 매칭이 없으면 전체 중앙값을 쓴다.
    - 1보다 작은 값(자유류보다 빠름)도 자르지 않는다. `lower_bound`가 처리한다.
    - 보고 dict: `frac_edges_observed, frac_length_observed` (spec: "섞은 비율을 보고")
  - `run_e3.py --real`: **gss에만** `"real03", "real08", "real18"`을 더한다(수집 범위가 3개 구). 보고 dict는 `results/real_mix.csv`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_real_scenario_matched_and_ratio():
    g0 = from_edge_list(3, [(0, 1, 10.0), (1, 2, 10.0)])           # length = 10 m each
    match = pd.DataFrame({"u_osm": [g0.osm_ids[0]], "v_osm": [g0.osm_ids[1]], "link_id": ["L1"], "overlap": [1.0]})
    g, rep = real_scenario(g0, match, {"L1": 1.8})                  # 1.8 km/h -> clamped to 3 km/h
    assert g.time[0] == pytest.approx(10 / (3 / 3.6))
    assert g.time[1] == pytest.approx(g.time[0])                    # unmatched: same-class ratio 1.2 x 10 s
    assert rep["frac_edges_observed"] == 0.5

def test_link_speeds_hour_filter(tmp_path):
    d = tmp_path / "20261030"; d.mkdir()
    for name, speed in [("080000.json.gz", 20), ("083000.json.gz", 40), ("090000.json.gz", 99)]:
        body = {"body": {"items": [{"linkId": "L1", "speed": str(speed), "createdDate": "x"}]}}
        (d / name).write_bytes(gzip.compress(json.dumps(body).encode()))
    assert link_speeds(tmp_path, 8) == {"L1": 30.0}
```

- [ ] **Step 2: 실패 확인**: `pytest tests/test_speeds.py -k "real or link_speeds" -v` → FAIL
- [ ] **Step 3: `snapshot.py`, `--real` 구현**
- [ ] **Step 4: 통과 확인**: `pytest -v` → all passed
- [ ] **Step 5: 실행**: `python scripts/run_e3.py gss --real && python scripts/make_figures.py c`
- [ ] **Step 6: 커밋**: `git commit -m "feat: real-speed snapshots as E3 scenarios"`
- [ ] **Step 7: AI 사용 기록**

---

### Task 22: `run_all` 최종 실행 + 결과 동결 — 담당 태형 · 리뷰 세현

**Files:**
- Create: `scripts/run_all.sh`
- Test: `tests/test_bench.py` (`--dry-run` 검사)

**Interfaces:**
- Consumes: 모든 스크립트, `results/match_decision.md`
- Produces: `bash scripts/run_all.sh [--dry-run] [--allow-collector]`
  - 실행 순서
    1. `pytest tests/test_correctness.py`
    2. `check_exact` (gangnam, gss, seoul)
    3. `run_e1`
    4. `run_e2 gangnam gss seoul`
    5. `run_e3 seoul`, 그리고 `run_e3 gss`(match_decision 첫 줄이 `ADOPT`이면 `--real` 추가)
    6. `make_figures all`
  - `pgrep -f routing.speeds.collect`에 걸리는 프로세스가 있으면 `--allow-collector` 없이 종료 코드 2로 멈춘다(측정 간섭 방지).
  - `python -VV`, `sysctl -n machdep.cpu.brand_string`, 시작·종료 시각, 수집기 상태를 `results/machine.txt`에 남긴다.
  - `--dry-run`은 실행할 명령만 출력한다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_run_all_dry_run_real_only_for_gss(tmp_path):
    env = {**os.environ, "RESULTS_DIR": str(tmp_path)}
    (tmp_path / "match_decision.md").write_text("ADOPT\ncoverage 78%\n")
    out = subprocess.run(["bash", "scripts/run_all.sh", "--dry-run", "--allow-collector"], env=env,
                         capture_output=True, text=True, check=True).stdout
    assert "run_e3.py gss --real" in out and "run_e3.py seoul --real" not in out
```

  - `RESULTS_DIR` 환경변수의 기본값은 `results`다.
- [ ] **Step 2: 실패 확인** → **Step 3: 구현** → **Step 4: 통과 확인**: `pytest tests/test_bench.py -v`
- [ ] **Step 5: 결과 동결 (11/5)**: 수집기를 끈 머신에서 `bash scripts/run_all.sh`를 실행하고, 결과·그림을 커밋한 뒤 태그 `results-frozen`을 단다. 이후에는 숫자를 바꾸지 않는다.
- [ ] **Step 6: AI 사용 기록**

---

## 일정 (spec 7장 관문 기준)

| 날짜 | 권세현 | 김태형 | 정의종 | 관문 |
|---|---|---|---|---|
| 10/30 금 | 2(키 신청 + 수집 가동), 5(추출), 4 | **1(오전, 먼저 병합)**, 3 | 19 시작(문헌 읽기), 8 준비(Task 3 병합 후 시작) | 공용 규칙 = 이 문서의 Global Constraints |
| 10/31 토 | 4 마무리, 9 | 6, 7 | 8 | |
| 11/1 일 | 12(강남 관문) | 10, 11 | 15 | **강남구에서 전 기법 = Dijkstra 100%** |
| 11/2 월 | 13, 20(매칭 결정) | 17, (E4 계획: SUMO 재탐색 1회) | 16 시작, 19 표 2·공정성 | **실제 속도 채택 · SUMO 1회 동작** |
| 11/3 화 | 12(서울 관문), 18 | 14(E2 밤샘), (E4 본 실행) | 16(서울 ALT 전처리) | **서울 전체 100%** |
| 11/4 수 | 18 마무리, 데이터 슬라이드 | 그림 (b) 확인 | 16 그림 (c)(d), 21(ADOPT 시), 19 표 2 채움 | |
| 11/5 목 | 슬라이드 구성안 + 영어 대본 | **22 run_all 동결** | 슬라이드 구성안 + 영어 대본 | **결과 동결** |
| 11/6~11/9 | spec 7장 그대로(슬라이드 → 녹화 → 편집 → **11/9 오전 제출, 마감 17:59**) | | | |
| 11/10~19 | README 문제·데이터 | README 알고리즘 | README 결과·향후 | 예상 질문 + 리허설 2회. 서로의 `docs/explain`으로 "이 줄을 설명해 보라" 연습 |

- 밀리면 spec 7장 우선순위의 아래부터 포기한다: 21 → 20 → (E4) → 16의 Weighted A*.
- 태형은 E4(SUMO)가 겹쳐 11/2~11/3이 가장 빡빡하다. 리뷰 담당(세현)이 Task 14 실행을 이어받을 수 있게 명령을 팀 채팅에 남긴다.

## 열린 결정

- [ ] **중간 보고서(Pass/Fail 필수)**: 마감과 형식 확인. 진행 상황과 역할 분담을 담는다(위 팀 운영 표 사용).
- [ ] Task 19(파트 2) 담당 확정 (안: 의종)
- [ ] 이 레포를 GitHub에 올리고 팀원 초대 (spec 11장의 `seoul-routing` 대신 이 레포를 쓰는지)
- [ ] 안양 SUMO 환경 수업 사용 승인 (연구실)
- [ ] LMS 영상 길이 제한 확인
- [ ] 실제 속도 채택 여부 (11/2, Task 20)

## 후속: E4 계획 (윈도우 PC, 별도 문서)

이 계획이 E4에 넘겨주는 것: `routing` 코어 패키지(표준 라이브러리만 사용, 윈도우에서 `pip install -e . --no-deps`), `Graph` 형식, `dijkstra`, `Stats`, `time_all`/`summarize`, `server_ratio`.

E4 계획에서 정할 것(spec 3장 E4, 담당 태형 환경·실행 + 의종 재탐색 함수):
- sumolib 그래프: SUMO 간선 = 정점, connection = 간선, 가중치 = `traci.edge.getTraveltime`의 60초 평활값
- `setRoute`는 새 간선에 진입한 직후에만 호출한다.
- 실행 27회
- KPI: 기존 연구 KPI 재사용
- 시간당 재탐색 횟수 → `server_ratio`와 결합해 서버 환산 슬라이드에 쓴다.
- 보급률 30% vs 100%를 Task 19의 공정성 절과 연결한다.
