# 웹사이트 구현 프롬프트 (Mac의 Claude Code에 그대로 붙여 넣기)

---

나는 김태형이다(세션 시작 질문은 건너뛴다). 이 레포(DCCS309 Team C2, 서울 최단경로)의 결과를 시각적으로 보여 주는 정적 웹사이트를 만든다. 앞으로 24시간 동안 아래 마일스톤을 순서대로 끝까지 진행한다. 막히면 그 마일스톤의 범위를 줄여서라도 다음으로 넘어가고, 줄인 내용은 진행 기록에 남긴다.

## 먼저 읽을 것
- `CLAUDE.md`(규칙), `README.md`(프로젝트 요약), `seoul_routing_plan_v2.md`(연구 질문·실험 설계)
- `docs/explain/*.md`(알고리즘 설명, 팀원 본인 글), `docs/video/part3-dijkstra-speedup.md`, `docs/industry.md`(원문 확인된 문헌)
- `results/`(동결 결과, 태그 `results-frozen`), `figures/`, `results/match_decision.md`
- E4(SUMO 재탐색) 결과는 브랜치 `e4-sumo-reroute`(PR)에 있다: `results/e4_*.csv`, `figures/fig_e_*.png`. 병합 전이면 그 브랜치에서 파일만 가져온다.

## 절대 규칙
1. **숫자는 `results/*.csv`에서만 가져온다.** 손으로 옮겨 적지 않는다. `scripts/export_site_data.py`가 CSV를 읽어 `site/data/*.json`을 만들고, 사이트는 그 JSON만 읽는다. 동결 결과는 고치지 않는다.
2. **검증 테스트:** `tests/test_site_data.py`로 JSON의 핵심 값이 CSV와 같은지 확인한다(예: 서울 >10km ALT16 가속비, A* 하한 비율 중앙값, E1 포기 지점 n). `pytest`가 통과해야 커밋한다.
3. **알고리즘 단계별 데모는 우리 Python 코드의 실제 실행 기록으로 만든다.** `Stats(trace=[])`·`collect_trace`(`src/routing/figures.py`)로 확정 순서를 뽑아 JSON으로 내보내고, JS는 그리기만 한다. JS로 알고리즘을 다시 구현하지 않는다.
4. **정직하게 표기:** 혼잡은 합성 시나리오(synthetic), 속도는 OSM maxspeed 94~96% 결측을 도로 등급 평균으로 채운 추정값, ITS 실측 속도는 REJECT(이유: `match_decision.md`), 서울 열린데이터 API는 키만 받고 쓰지 않음. 국내 기업(쿠팡이츠, 배민, Tmap, 카카오)이 특정 알고리즘을 쓴다고 쓰지 않는다. 인용은 `docs/industry.md`에 있는 것만 쓴다.
5. **언어:** UI·차트 라벨·본문은 영어(발표가 영어), 팀 문서는 한국어. `docs/explain/*.md` 내용은 팀원 글이므로 인용할 때 출처를 밝히고, 새로 쓰지 않는다.
6. **진행 방식:** 브랜치 `site-web` → 마일스톤마다 커밋·push → PR(리뷰: 세현 또는 의종). `main`에 직접 push하지 않는다. 키(`ITS_API_KEY`, `SEOUL_API_KEY`)는 커밋하지 않는다.
7. **AI 사용 기록:** 끝날 때 `docs/ai-usage.md`에 한 줄(날짜, 김태형, 웹사이트, Claude Code, 맡긴 일). "본인이 확인한 것" 칸은 비워 두고 나에게 묻는다.

## 기술 선택 (바꾸지 말 것)
- 빌드 없는 정적 사이트: `site/index.html` + `site/*.js` + `site/*.css`. 차트는 CDN의 Chart.js 또는 Observable Plot, 지도는 Leaflet + OSM 타일(저작자 표기 포함).
- 배포: GitHub Pages(Actions 워크플로 `.github/workflows/pages.yml`, `site/`만 배포). 저장소 설정에서 Pages를 켜는 것은 나에게 요청한다.
- 모바일 폭(375px)에서 가로 스크롤 없이 보이고, 색만으로 구분하지 않는다(범례·패턴·라벨).

## 마일스톤
1. **뼈대 + 데이터 내보내기:** `export_site_data.py`, `test_site_data.py`, 페이지 골격(섹션 이동 메뉴), 로컬 서버(`python -m http.server -d site`)로 확인.
2. **문제와 데이터:** RQ1~3, 그래프 표(`graph_table.csv`), 속도 추정의 한계.
3. **알고리즘 단계별 데모:** `docs/explain`의 4정점 예제(0→1:4, 0→2:1, 2→1:2, 1→3:5, 2→3:8)로 Dijkstra(stale pop 포함), A*(f값 순서), Bidirectional(μ 갱신과 종료 조건, 함정 그래프 6.0→5.5), ALT 하한. 다음/이전 버튼과 자동 재생.
4. **탐색 공간 지도:** 강남역→삼성역 질의에서 4개 알고리즘의 확정 정점을 Leaflet 지도에 토글로 표시(Task 17과 같은 질의, `data/graphs/gangnam_graph_v1.pkl` 필요. 없으면 공유 드라이브에서 받으라고 나에게 묻는다).
5. **E1·E2:** 완전탐색 포기 지점, 거리 구간별 확정 정점 비율·가속비·하한 촘촘함(그래프·알고리즘 선택형 차트). "A*·bidir는 강남·gss 장거리에서 Dijkstra보다 느리다"와 그 이유(vmax로 하한이 느슨)를 함께 보여 준다.
6. **E3·RQ3:** 합성 혼잡에서 정확성(하한이 깨지는 대조군 포함), ALT 전처리 손익분기, 정적 재탐색 효과(`reroute_gain_*`), SUMO E4 결과(고정 경로 vs 재탐색 30%·100%, 신호·가정 수요).
7. **한계·향후·팀:** 데이터 한계, SUMO 범위, 팀원과 역할, AI 사용 고지, 데이터 출처(OSM ODbL, ITS).
8. **마무리:** 접근성·모바일 점검, 콘솔 오류 0, 모든 숫자에 출처 CSV 표시, README에 사이트 링크 추가, PR 정리.

## 부족한 데이터 보강 (내가 따로 조사해서 md로 줄 때)
- 내가 서울 열린데이터 API 조사 결과(md)를 주면, 그 내용으로 "실측 속도로 보강하는 방법" 계획을 먼저 세워 나에게 확인받는다.
- 새로 모은 데이터는 동결 결과와 섞지 않는다. 파일 이름에 `_real_v1`을 붙이고, 사이트에는 "post-freeze, preliminary"로 따로 표시한다.
- 호출 한도를 먼저 확인하고, 필요한 시각(03·08·18시) 근처만 수집한다(`match_decision.md`의 교훈).

## 진행 기록
- `site/PROGRESS.md`에 마일스톤별로 한 일, 줄인 범위, 남은 일을 적는다. 세션이 끊겨도 이 파일을 보고 이어 간다.
- 각 마일스톤을 마칠 때 브라우저에서 직접 열어 확인하고, 확인한 내용을 기록한다.

## 완료 기준
- `pytest` 통과(기존 테스트 + `test_site_data.py`)
- `site/`가 로컬 서버에서 오류 없이 열리고, 8개 마일스톤이 PROGRESS.md에 완료 또는 축소 사유와 함께 기록됨
- PR이 열려 있고, AI 사용 기록 한 줄이 추가됨
