# 정의종 작업 인계 — 2026-10-30

기준: `FIo-g/26-2_Algorithm`의 `acc37e64cbc006f1930775d5ffea38adcb12e1bb`.
작업 중 새로 올라온 Task 3·6·7·10·11·17 코드를 반영했다.

## 구현·검증 상태

| Task | 준비한 것 | 아직 남은 것 |
|---|---|---|
| 8 | `alt.py`, 독립 정답 및 실제 팀 Dijkstra 연동 테스트, 작은 질의 메모리 회귀 | Task 4가 병합되면 `EXACT_ALGOS["alt4"]` 등록. 강남구·서울 관문, 본인 설명, 세현 리뷰 |
| 15 | 새 Graph를 반환하는 합성 시간대·무작위 정체·속도 증가 대조군, 하한·중간 지점 함수 | 본인 손 추적·설명, 세현 리뷰 |
| 16 | E3 검사·측정·CSV·서버 상대비, 그림 c/d, 실행 CLI. 기존 그림 f 보존 | Task 4·실제 도로망·질의 파일. 실제 실험, matplotlib PNG 렌더, 세현 리뷰 |
| 19 | `docs/industry.md`: 공식 문서·원문 표·조건·공정성·파트 2 구성안 | 담당 확정, 본인 원문 확인, 태형 리뷰, E2 실측값 대조 |
| 21 | 조건부 후속 작업 | `results/match_decision.md`가 ADOPT인 경우에만 구현·실행 |
| E4 | 별도 SUMO 계획의 후속 작업 | 연구실 사용 승인·E4 인터페이스/계획 확정 |

초기 노션의 `22 passed`는 Task 1 시점의 수치다. 이 인계의 검사 개수와 혼동하지 않는다.

## 지금 실행할 수 있는 검증

표준 라이브러리 테스트는 설치된 Python과 `PYTHONPATH=src`만으로 실행한다.

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_alt*.py' -v
python -m unittest discover -s tests -p 'test_congestion.py' -v
python -m unittest discover -s tests -p 'test_e3*.py' -v
python -m compileall -q src scripts
python scripts/run_e3.py gss seoul --check-only
```

`--check-only`는 미준비 시 exit 2와 누락 목록을 반환한다. 실험 성공이 아니다.
Task 4 검증기와 도로망이 없으면 결과 CSV를 만들지 않는다.

현재 실행 환경에서 패키지 다운로드가 차단되어 `pytest`, `matplotlib` 전체 검증은 실행하지 못했다.
팀의 개발 환경에서 병합 전에 반드시 다음을 실행한다.

```powershell
python -m pytest tests/test_alt.py tests/test_alt_isolated.py tests/test_bench.py tests/test_congestion.py tests/test_e3.py tests/test_e3_isolated.py tests/test_e3_figures.py -v
python -m pytest
```

Task 4를 받은 뒤 해당 `tests/test_correctness.py`에도 ALT를 등록하고 그 파일의 검사를 수행한다.
등록할 래퍼는 그래프 객체와 랜드마크를 함께 보관하고 `cached_g is g`일 때만 재사용한다.

## 실제 E3 실행 순서

1. Task 4 `routing.verify`와 공용 정확성 등록부를 병합한다.
2. 공유한 `data/graphs/gss_graph_vN.pkl`, `seoul_graph_vN.pkl`과 각 `data/queries/{name}_q_seed42.csv`를 둔다.
3. 팀의 Task 12 강남구·서울 관문을 통과한다. 버그가 있으면 측정부터 하지 않는다.
4. `python scripts/run_e3.py gss seoul --check-only`가 ready true인지 확인한다.
5. `python scripts/run_e3.py gss seoul`을 실행한다. 입력 버전·SHA-256은 manifest에 기록된다. 기존 결과 덮어쓰기는 기본 거부한다.
6. E2 전처리 CSV가 준비되면 `python scripts/make_figures.py c d --e3-graph gss`로 그림을 만든다.

재탐색 행의 `qid/bin/crow_m`은 **원래 출발·도착 질의**의 구간이다. 남은 경로의 거리 구간을 뜻하지 않는다.
서버 환산은 Dijkstra 대비 질의시간 비율이다. 절대 서버 대수·차량 도착시간 개선을 측정한 값이 아니다.
그림 d의 E2 전처리 비용은 E3와 같은 하한 그래프의 인덱스여야 한다. 향후 실제 속도를 채택하면 다시 확인한다.
대조군에서 오답이 나올 수 있으나 모든 그래프·질의에서 반드시 나와야 하는 것은 아니다.

## 직접 확인할 예제

`docs/explain/alt.md`, `docs/explain/congestion.md`는 생성하지 않았다. 본인이 손으로 따라간 뒤 영어 5~10줄을 직접 작성한다.

- ALT: `tests/test_alt_isolated.py::test_speedup_negative_control`에서 기준 간선 시간이 100·510·520초일 때와 100·10·10초일 때를 비교한다. 왜 오래된 랜드마크로 100초가 나오고 새 전처리로 20초가 나오는지 직접 설명한다.
- 혼잡: 0→1=1초, 1→2=1초, 2→3=2초인 그래프에서 누적 시간이 절반이 되는 정점이 어디인지 확인한다. 간선 시간이 늘어나는 경우와 기준보다 줄어드는 경우에 하한의 보장이 어떻게 달라지는지 설명한다.
- `docs/ai-usage.md`의 본인 확인 칸을 실제 수행한 내용으로 채운다. AI의 자동 테스트와 학생의 독립 확인은 구분한다.

## 일정 대조

노션 팀 계획은 11/9 17:59를 적고 있으나, 10/29 직접 확인한 C2 해당 LMS 항목은
[Week12 영상·슬라이드](https://mylms.korea.ac.kr/courses/97892/assignments/262457) 제출을 **11/16 23:59**로 표시했다.
팀의 빠른 내부 목표는 유지할 수 있지만 공식 제출 기한으로 혼동하지 않는다.
같은 LMS 항목의 영상 안내는 영어 **15~20분**, 슬라이드 PDF다.
