# CLAUDE.md

DCCS309 Algorithms Team C2(권세현·김태형·정의종)의 서울 최단경로 프로젝트 레포다. 응답은 한국어로 한다.

## 세션 시작 규칙 (반드시 지킬 것)

작업을 처음 시작할 때, 다른 일을 하기 전에 사용자가 누구인지 묻는다. AskUserQuestion으로 세 사람을 보기로 준다.

| 사용자 | 가이드 문서 |
|---|---|
| 권세현 | `docs/team/kwon-sehyun.md` |
| 김태형 | `docs/team/kim-taehyeong.md` |
| 정의종 | `docs/team/jeong-uijong.md` |

사용자가 이미 자신이 누구인지 밝혔으면 묻지 않는다.

답을 받으면 아래 순서로 짧은 가이드를 준다.

1. 그 사람의 가이드 문서를 읽는다.
2. 오늘 날짜를 가이드의 일정표와 맞춰 오늘 할 Task를 고른다.
3. `git fetch`(원격이 있으면), `git log --oneline -20 main`, `git branch -a`로 선행 Task가 `main`에 병합됐는지 확인한다.
4. 10줄 안쪽으로 안내한다.
   - 오늘 할 Task: 번호, 제목, [통합 계획](docs/superpowers/plans/2026-10-30-seoul-routing-python.md)의 해당 절
   - 선행 상태: 병합됨인지 아직인지. 아직이면 합성 그래프(`routing.synthetic`)로 먼저 시작하는 방법이나, 의존이 없는 다른 Task를 제안한다.
   - 완료 기준(테스트 명령과 기대 출력)
   - 그 사람이 리뷰할 PR(`gh pr list`가 되면)
   - 오늘 마감인 관문이 있으면 그것

## 문서

- `seoul_routing_plan_v2.md`: 팀 실행 계획(spec). 연구 질문, 실험 설계, 일정, Q&A 대비가 들어 있다.
- `docs/superpowers/plans/2026-10-30-seoul-routing-python.md`: **통합 구현 계획**(단일 기준). Task, 인터페이스, 테스트가 들어 있다.
- `docs/team/*.md`: 팀원별 가이드. 통합 계획과 다르면 통합 계획이 맞다.
- `docs/ai-usage.md`: 생성형 AI 사용 기록
- `docs/explain/*.md`: 알고리즘별 본인 설명 (Q&A 대비)
- `docs/industry.md`: 현업·문헌 조사 (발표 파트 2·4)

## 환경과 명령

- 맥: `/opt/homebrew/bin/python3.14 -m venv .venv && source .venv/bin/activate && pip install -e .`
- 윈도우 SUMO PC(E4): Python 3.10 이상. 코어만 쓰면 `pip install -e . --no-deps`
- 테스트: `pytest`. PR 전에는 최소한 `pytest tests/test_correctness.py`를 돌린다.
- 관문: `python scripts/check_exact.py data/graphs/{name}_graph_v1.pkl data/queries/{name}_q_seed42.csv`

## 규칙 (통합 계획 Global Constraints 요약)

- 코어 모듈(`graph, heap, dijkstra, astar, bidirectional, alt, exhaustive, verify, queries, bench, gate, congestion, synthetic`)은 표준 라이브러리만 import한다.
- 알고리즘 시그니처: `name(g, s, t, ..., *, stats=None) -> (거리, 경로, 확정 노드 수)`
- 정확성: 거리 상대 오차 1e-9 + 경로 유효성. 시간 측정은 Dijkstra 일치 검사를 통과한 뒤에만 한다.
- 같은 (u, v) 간선은 하나만 둔다. `vmax`는 그래프에서 한 번 계산한다.
- 그래프 파일: `data/graphs/{name}_graph_v{N}.pkl`. 덮어쓰지 않고, git에 올리지 않는다(공유 드라이브로 나눈다).
- 진행 방식: 브랜치 `t{N}-{짧은이름}` → PR → 통합 계획 "팀 운영" 표의 리뷰 담당 승인 → `main` 병합 → 팀 채팅에 알림
- 코드·주석·그림 라벨은 영어, 팀 문서는 한국어로 쓴다.
- `ITS_API_KEY` 같은 키는 커밋하지 않는다.

## 생성형 AI 규정 (강의 슬라이드 30): Claude가 지킬 것

이 과목은 출처 표기를 전제로 AI 사용을 허용한다. 다만 이해 없이 100% 의존하면 0점이 될 수 있고, Live Q&A에서 직접 설명을 요구받는다.

- 코드를 쓰거나 고친 뒤에는 핵심 로직을 짧게 설명한다. 그리고 손으로 따라가 볼 예제(그 Task의 테스트)를 짚어 준다.
- `docs/explain/*.md`는 사용자가 **본인 말로** 쓴다. Claude는 대신 쓰지 않는다. 질문으로 이해를 확인하고, 틀린 부분만 지적한다.
- Task를 마칠 때 `docs/ai-usage.md`에 한 줄(날짜, 작성자, Task, 도구, 맡긴 일, 본인이 확인한 것)을 남기도록 안내한다.
- 레퍼런스는 원문을 확인한 것만 쓴다. 확인하지 않은 인용이나 지어낸 출처를 만들지 않는다.
- 국내 기업(쿠팡이츠, 배민, Tmap, 카카오)에 대해 "X사가 Y 알고리즘을 쓴다"고 단정하지 않는다.
