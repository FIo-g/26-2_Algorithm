# 생성형 AI 사용 기록

강의 슬라이드 30에 따라 AI 도구 사용을 모두 기록한다. Task를 마칠 때마다 한 줄씩 추가한다. "본인이 확인한 것"은 작성자가 직접 채운다.

| 날짜 | 작성자 | Task | 도구 | 맡긴 일 | 본인이 확인한 것 |
|---|---|---|---|---|---|
| 2026-10-30 | 김태형 | 계획 | Claude Code (Claude Opus 5.5) | 팀 계획 v2를 바탕으로 통합 구현 계획·팀원 가이드·CLAUDE.md 작성, 독립 에이전트 검토 | (작성자 기입) |
| 2026-10-30 | 김태형 | 1 | Claude Code (Claude Opus 5.5) | `graph.py`, `synthetic.py`, `tests/test_graph.py`, 프로젝트 설정 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 1 (리뷰 수정) | Claude Code (Claude Opus 5.5) | 최종 리뷰의 numpy 타입 문제와 사소한 항목(입력 검증, repr, subgraph·from_edge_list 검사) 수정 | (작성자 기입) |
| 2026-10-30 | 김태형 | 3 | Claude Code (Claude Opus 5.5) | `heap.py`(Stats, CountingHeap), `dijkstra.py`(dijkstra, sssp), `tests/test_dijkstra.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 6 | Claude Code (Claude Opus 5.5) | `astar.py`(A*, Weighted A*, astar_heuristic), `tests/helpers.py`, `tests/test_astar.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 7 | Claude Code (Claude Opus 5.5) | `bidirectional.py`, `tests/test_bidirectional.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 10 | Claude Code (Claude Opus 5.5) | `queries.py`(거리 구간별 질의 생성·저장·로드), `tests/test_queries.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 11 (ALT 연결 제외) | Claude Code (Claude Opus 5.5) | `bench.py`(standard_algos, time_all, summarize, write_csv), `tests/test_bench.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 17 (그림 함수까지) | Claude Code (Claude Opus 5.5) | `figures.py`(collect_trace, fig_f, CLI), `scripts/make_figures.py`, `tests/test_figures.py` 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 22 (스크립트·dry-run까지) | Claude Code (Claude Opus 5.5) | `scripts/run_all.sh`(일괄 실행, 수집기 감지, ADOPT 시 gss만 --real), dry-run 테스트 구현 | (작성자 기입) |
| 2026-10-30 | 김태형 | 3·6·7·11·17·22 (리뷰 수정) | Claude Code (Claude Opus 5.5) | 최종 리뷰 반영: 질의 상태 dict·set 전환(측정 왜곡 제거), time_all generator, run_all 결정 파일 엄격 검사, make_figures 여러 이름 | (작성자 기입) |
| 2026-10-30 | 정의종 (본인 검토 대기) | 8 | OpenAI Codex (GPT-6.1) | ALT·랜드마크·테스트 초안 및 자동 검증, 최신 팀 Dijkstra 연동, dict/set 질의 상태·근거리 메모리 회귀 | (본인이 손 추적·코드 확인 후 직접 기입) |
| 2026-10-30 | 정의종 (본인 검토 대기) | 15 | OpenAI Codex (GPT-6.1) | 혼잡 시나리오·하한·중간 지점 함수와 테스트 작성·자동 검증 | (본인이 손 추적·가정 배율 확인 후 직접 기입) |
| 2026-10-30 | 정의종 (본인 검토 대기) | 16 | OpenAI Codex (GPT-6.1) | E3 실행·정확성 선검사·CSV·그림 c/d 초안, 기존 그림 f 보존, 계약 테스트. 실제 서울 실험 미실행 | (본인이 코드·입출력 확인 후 직접 기입) |
