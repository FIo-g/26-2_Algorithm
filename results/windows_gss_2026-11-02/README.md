# Task 16: Windows gss 예비 실험 (2026-11-02)

정의종이 Windows PC에서 실행한 E3 gss 결과다. 그림 (d)의 전처리 비용을 위해 E2 gss도 같은 PC에서 실행했다. 최종 발표 수치는 Task 22의 한 머신 일괄 실행에서 확정한다. 리뷰 담당은 권세현이다.

## 입력과 측정 조건

- 그래프: `data/graphs/gss_graph_v1.pkl`, 정점 9,317개, 간선 25,435개.
- 질의: `data/queries/gss_q_seed42.csv`, 거리 구간별 100개씩 총 300개.
- 랜드마크: k = 4, 8, 16, 선택 시드 0.
- 합성 시나리오: `synth03`, `synth08`, `synth18`, `random30`. `control`은 하한 조건을 의도적으로 깨뜨리는 속도 증가 대조군이다.
- E2와 E3 manifest의 그래프·질의 SHA-256이 일치한다. 합성 시나리오의 모든 간선 시간은 기준 이상이므로 E3의 하한 그래프와 E2의 자유류 그래프가 같은 가중치를 사용한다.
- 질의 시간은 공용 `time_all`의 워밍업 후 3회 측정 중앙값이다.

## 확인 결과

- gss 관문: `ALL EXACT: 300 queries x 6 algos`.
- 정상 혼잡 4개 시나리오 모두 6개 정확 알고리즘의 오답 수 0개.
- `control`에서는 A* 20개, ALT4 157개, ALT8 163개, ALT16 168개의 오답을 관측했다. 이 대조군은 시간 측정에서 제외했다.
- 재탐색 CSV 7,200행으로 계산한 중앙값·Dijkstra 대비 비율이 `server_ratio.csv`의 24행과 일치한다. 이 비율은 경로 질의 시간의 상대값이다.
- `synth08`의 전체 질의에서는 ALT4·8·16의 시간 가속비가 모두 1 미만이다. 따라서 해당 조건에서는 전처리 비용을 회수할 손익분기점이 없다.
- 사용자 실행 검사: `tests/test_e3_figures.py`와 `tests/test_correctness.py`, 합계 **67 passed**. 그림 (d)의 손익분기 문구 겹침을 수정한 뒤 다시 실행한 결과다.

## 산출물

이 폴더에는 E3 정확성·전체 질의·재탐색·Weighted A* CSV, 서버 상대비, E3 manifest와 같은 PC의 E2 CSV·manifest가 있다. 파일을 이 폴더로 정리하면서 13개 CSV·JSON·PNG 파일의 SHA-256을 이동 전후 대조했으며 모두 일치했다.

- [그림 (c): 혼잡 정확성과 성능](../../figures/windows_gss_2026-11-02/fig_c_congestion.png)
- [그림 (d): ALT 전처리 비용과 성능](../../figures/windows_gss_2026-11-02/fig_d_alt_tradeoff.png)

저장된 CSV로 그림을 다시 만드는 명령은 저장소 루트에서 실행한다.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/make_figures.py c d --results-dir results/windows_gss_2026-11-02 --out-dir figures/windows_gss_2026-11-02 --e3-graph gss
```

`docs/ai-usage.md`의 2026-11-02 Task 16 행에 AI 보조 내용과 학생이 직접 실행·확인한 내용을 구분해 기록했다.
