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
| 2026-10-30 | 정의종 | 8 | OpenAI Codex (GPT-6.1) | ALT·랜드마크·테스트 초안 및 자동 검증, 최신 팀 Dijkstra 연동, dict/set 질의 상태·근거리 메모리 회귀 | Task 8: 랜드마크 0을 기준으로 정방향 거리 [0, 2, 5]와 역방향 거리 [0, 10, 7]을 손계산했다. ALT 하한이 max(0, 5−2, 10−7)=3초임을 확인했다. 실제 최단시간이 6초면 유효하지만, 1초면 과대평가가 되어 안전하지 않음을 이해했다. 도로 구조와 인덱스가 같고 모든 간선의 이동시간이 전처리 기준 이상이면 기존 전처리를 재사용할 수 있음을 확인했다. |
| 2026-10-30 | 정의종 | 15 | OpenAI Codex (GPT-6.1) | 혼잡 시나리오·하한·중간 지점 함수와 테스트 작성·자동 검증 | Task 15: 원래 10초인 간선에 이동시간 배율 2.0과 0.5를 적용하면 각각 20초와 5초가 됨을 계산했다. 무작위 정체는 기본적으로 약 30%의 간선을 선택해 시간을 2배로 만들며, 같은 간선 순서와 시드로 선택을 재현함을 확인했다. 속도 증가 대조군은 motorway·trunk와 해당 link 전체, 나머지 간선의 약 10%에 시간 배율 0.5를 적용한다. 이때 기존 ALT 하한의 보장이 깨질 수 있음을 이해했다. 이동시간이 1초·1초·2초인 예제에서 시간 기준 중간 정점은 누적 2초에 도달하는 2번임을 계산했다. |
| 2026-10-30 | 정의종 | 16 | OpenAI Codex (GPT-6.1) | E3 실행·정확성 선검사·CSV·그림 c/d 초안, 기존 그림 f 보존, 계약 테스트. 실제 서울 실험 미실행 | E3 테스트를 직접 실행해 14 passed를 확인했다. 정확성 검사에 실패하면 시간 측정을 시작하지 않는 동작과, 하한 그래프에서 전처리를 한 번 수행한 뒤 여러 교통 상황에서 재사용하는 구조를 확인했다. --check-only 실행 결과 gangnam_q_seed42.csv가 없어 입력 준비가 완료되지 않았음을 확인했으며, 실제 강남구 E3 실험은 아직 실행하지 않았다. |
| 2026-10-30 | 정의종 | 19 | OpenAI Codex (GPT-6.1) | 현업 공식 문서·논문 원문 대조, 비교표·공정성·발표 구성 초안. 학생 직접 확인·태형 리뷰 대기 |확인일: 2026-10-31 . 직접확인 : OSRM은 CH·MLD를 지원하며 README는 MLD를 기본 선택으로 권장함. GraphHopper는 Speed=CH, Hybrid=LM, Flexible=Dijkstra/A*임. Bing의 2012년 CRP 도입 사례와 CRP의 가중치 독립 도로 구조 전처리→비용 반영→질의 3단계를 확인함. ALT Table 2의 M11은 거리 가중치·랜드마크 16개 전처리·P2 선택·128회 평균에서 D/AL=2113.80/132.83≈15.91배임. 서베이 arXiv 2015 v1 Table 1은 μs 단위·이동시간 가중치임. 공정성 논문의 4/3은 동일 수요의 비원자적 흐름에서 l(x)=ax+b, a,b≥0일 때 사용자 균형(내시 균형)의 총 지연/시스템 최적의 총 지연 상한임. 우리 E2 실측값과의 비교는 아직 진행하지 않음. |
| 2026-10-31 | 권세현 | 2 | Claude Code (Claude Opus 5.5) | `speeds/collect.py`(수집·오류 기록·키 가림·.env 로드), `tests/test_speeds.py`, `.env.example`·`.gitignore` 설정, 실제 API 응답 확인, PR #5 작성 | 인증키 발급, 환경변수 설정, env, gitignore |
| 2026-10-31 | 권세현 | 4 | Claude Code (Claude Opus 5.5) | `verify.py`(path_cost, check_result, verify_all), `tests/test_correctness.py`(EXACT_ALGOS에 dijkstra·astar·bidir·alt4 등록), PR 작성 | `check_result` 오류 예제(되돌아가는 경로, 없는 간선)를 손으로 따라가 봄, `test_correctness.py` 직접 실행(58 passed) |
