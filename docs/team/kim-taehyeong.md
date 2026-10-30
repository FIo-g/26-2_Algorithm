# 김태형 작업 가이드

> 기준 문서는 [통합 계획](../superpowers/plans/2026-10-30-seoul-routing-python.md)이다. Task 번호, 인터페이스, 테스트 코드는 거기에 있다. 이 문서와 다르면 통합 계획이 맞다.

## 한눈에

- **맡은 Task**
  - 1: 뼈대 + Graph (**모두가 기다림**)
  - 3: 공용 힙 + Dijkstra
  - 6: A*
  - 7: Bidirectional
  - 10: 질의 생성
  - 11: 벤치 하네스
  - 14: E2 + 그림 (b)
  - 17: 탐색 공간 그림 (f)
  - 22: run_all 동결
  - E4 (SUMO, 윈도우 PC, 별도 계획): 환경·실행
- **리뷰**
  - 세현: 2, 5, 9, 12, 13, 18
  - 의종: 19
- **영상 파트** (spec 8장): Dijkstra 계열·가속비
- **README** (11/10~19): 알고리즘
- **마감**: 11/5 결과 동결 · 11/9 17:59 영상 제출(팀 목표는 오전) · 11/20 발표 + Q&A

## 처음 한 번

1. 맥은 `/opt/homebrew/bin/python3.14 -m venv .venv && source .venv/bin/activate && pip install -e .`(Task 1에서 `pyproject.toml`을 만든 뒤)
2. **오늘 직접 할 일**
   - 윈도우 PC에서 안양 망 `python check_sumo_env.py <anyang.sumocfg> --run` (spec "오늘 꼭 할 3가지" 3번)
   - 이 레포를 GitHub에 올리고 팀원을 초대한다(열린 결정).

## 일정

| 날짜 | 할 일 | 선행 (누구의 무엇) | 완료 기준 |
|---|---|---|---|
| 10/30 금 | **Task 1 먼저 → 병합·공지**, Task 3 → 병합·공지(의종 ALT가 `sssp`를 기다림), SUMO 환경 확인 | 없음 | 1·3 병합 |
| 10/31 토 | Task 6, Task 7 | 세현 Task 4 (등록부) | 6·7 병합, `test_correctness` 등록 |
| 11/1 일 | Task 10, Task 11 → 세현 관문 지원 | 의종 Task 8 | 10·11 병합, **강남구 관문** |
| 11/2 월 | Task 17, E4 계획 + SUMO 재탐색 Medium 1회 | 강남 그래프 | 그림 (f), **SUMO 1회 동작** |
| 11/3 화 | Task 14 (E2 밤샘), E4 본 실행 | 세현 서울 관문 | E2 CSV |
| 11/4 수 | 그림 (b) 확인, 영상 파트 정리 | | 그림 (b) |
| 11/5 목 | **Task 22 run_all → 결과 동결 태그** | 전원 결과 병합 | `results-frozen` 태그 |

- 11/2~11/3은 E4와 겹쳐 가장 빡빡하다. Task 14 실행 명령을 팀 채팅에 남겨 두어 세현이 이어받을 수 있게 한다.

## Task 요약

### Task 1: 뼈대 + Graph + 합성 그래프 (오늘 오전)
- **만드는 것:** `pyproject.toml`, `.gitignore`, `graph.py`, `synthetic.py`, `docs/ai-usage.md`, `docs/explain/`
- **넘기는 것:** 모든 Task. 병합 즉시 팀 채팅에 "Task 1 병합"
- **주의:**
  - (u, v) 중복은 `Graph`에서 `ValueError`, 생성 함수에서는 최솟값만 남긴다.
  - `vmax`는 생성 때 한 번만 계산한다.
  - 합성 그래프의 osm_id는 `1000 + i`

### Task 3: 공용 힙 + Dijkstra + sssp
- **넘기는 것:** 모두. 의종 ALT는 `sssp`가 필요하다.
- **주의:** 카운터 정의(오래된 pop은 settled에서 뺀다), `Stats.trace`는 `compare=False`
- **이해 확인:** `docs/explain/dijkstra.md`

### Task 6: A* (+ Weighted A*)
- **만드는 것:** `astar.py`(`astar_heuristic` 포함), `tests/helpers.py`(`control_pair`, 의종도 씀)
- **이해 확인:** `docs/explain/astar.md`. vmax가 크면 하한이 느슨해지는 이유를 쓴다(Q&A 예상 질문).

### Task 7: Bidirectional
- **주의:** 종료는 `top_f + top_b >= μ`, 역방향은 `bwd`
- **이해 확인:** `docs/explain/bidirectional.md`

### Task 10: 질의 생성
- 질의는 osm_id로 저장하고 시드는 42다. 강남구 >10 km 구간은 채워진다(대각선 끝 쌍).

### Task 11: 벤치 하네스
- **주의:**
  - 워밍업은 측정과 별도로 **추가** 실행한다. 모든 질의를 측정하고, 3회 중앙값을 쓴다.
  - `standard_algos`는 vmax를 실수로 한 번 묶는다.

### Task 14: E2 + 그림 (b) + 하한 느슨함
- **만드는 것:** `experiments/e2.py`, `scripts/run_e2.py`, `fig_b`
- **완료 기준:** `e2_summary.csv`, `e2_tightness.csv`, 그림 (b)
- **주의:**
  - settled 비율을 주 지표로 쓴다.
  - breakeven은 전체 질의의 중앙값으로 계산한다.
  - 강남구 >10 km 구간에는 "corner pairs only" 주석을 단다.

### Task 17: 탐색 공간 그림 (f)
- 강남역 → 삼성역 질의에서 4개 알고리즘의 확정 정점을 지도에 그린다. 영상에 바로 쓰는 그림이다.

### Task 22: run_all 최종 실행 + 결과 동결
- **주의:**
  - 수집기가 돌고 있으면 멈춘다(`--allow-collector`로만 우회).
  - `--real`은 gss에만, `ADOPT`일 때만 붙는다.
  - 결과는 태그 `results-frozen`. 이후 숫자는 바꾸지 않는다.

### E4 (SUMO, 별도 계획)
- 이 레포의 코어(`routing`)를 윈도우 PC에 `pip install -e . --no-deps`로 설치해 `dijkstra`를 재사용한다.
- 재탐색 함수는 의종이 맡는다. 세부는 통합 계획의 "후속: E4 계획".

## 리뷰 담당

- **Task 2 (세현):** 키가 하드코딩되지 않았는지, 오류가 나도 루프가 계속 도는지, bbox가 37.42인지
- **Task 5·9 (세현)**
  - 평행 간선은 최솟값, 자기 루프는 제거하는지
  - `coords` 순서가 (위도, 경도)인지
  - `bfs_subgraph`가 무한 루프에 빠지지 않는지
- **Task 12·13 (세현):** 관문 실패 시 종료 코드 1인지, E1 중복 크기를 건너뛰는지
- **Task 18 (세현):** 표에 maxspeed 결측 비율이 있는지
- **Task 19 (의종):** 모든 행의 원문 URL을 직접 열어 확인하고 `확인자` 칸에 이니셜을 적는다. 국내 기업에 대해 단정하는 문장이 없는지 본다.

## AI 사용 규칙 (슬라이드 30)

- Task를 마칠 때마다 `docs/ai-usage.md`에 한 줄을 남긴다.
- `docs/explain/*.md`는 본인 말로 쓴다. Claude가 쓴 코드는 테스트 예제를 손으로 따라가며 이해한 뒤 병합한다.
- Live Q&A에서 "이 줄을 설명해 보라"는 질문에 답할 수 있어야 한다.

## 막히면

- 그래프 파일이 늦으면 합성 그래프(`grid_graph`, `random_geo_graph`)로 먼저 개발한다.
- SUMO 재탐색이 11/2까지 안 돌면 E4를 "차량 1대 경로 변경 시각화"로 줄이거나 뺀다(spec 10장).
- 12시간 안에 회신한다(슬라이드 27).
