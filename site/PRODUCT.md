# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js (latest stable, 16.x, App Router) deployed on Vercel. Chosen by the user. The app lives in `site/` inside the team's Python repository.

## Users

Students taking the same undergraduate algorithms course (DCCS309) as the team. They know Dijkstra and A* at textbook level and have never seen this project's code. They watch the team's 15-minute English presentation on 2026-11-20.

Assumption (not confirmed by the user): they open a shared link on their own phone or laptop, alone, with no one explaining it.

## Product Purpose

Show what Team C2 did, and make it look as good as it can. The project compared four exact shortest-path methods (Dijkstra, A*, Bidirectional Dijkstra, ALT) on the real Seoul road network and asked how much cheaper each one finds the same answer. Success: a classmate leaves knowing what the team built, what it found, and remembers it.

## Positioning

Everything on the page comes from the team's own Python implementation and its frozen results. The search animations replay the vertices the team's code actually settled, in order. Every method was checked against Dijkstra (same travel time, valid path) before it was timed.

## Operating Context

- Course team project, theme "Mobility & Navigation". Public GitHub repository.
- Results were frozen on 2026-11-09 (git tag `results-frozen`). Numbers do not change after that.
- The presentation and all site text are in English. Team documents are in Korean.

## Capabilities and Constraints

- Static site. Numbers are read from `results/*.csv` at build time, never typed by hand.
- Search animations use traces exported from the team's Python code. The algorithms are not reimplemented in JavaScript.
- Three road graphs: Gangnam-gu (3,144 vertices), Gangnam+Seocho+Songpa "gss" (9,317), all of Seoul (67,420 vertices, 185,415 edges).
- Edge weights are travel times estimated from road class, because OSM `maxspeed` is missing on 94 to 96 percent of edges. The site labels travel times as estimated where it shows one.
- Congestion in experiment E3 is synthetic. Real ITS speed data was collected but rejected (monthly API call limit ended collection before a morning-peak snapshot existed). The site labels the congestion scenarios as synthetic in one plain sentence.
- The site shows what the team did (the user's decision, 2026-11-15): no limits section, no caution plates, no caveat lines. Every measured value still appears in its chart, including the cases where A* and Bidirectional are slower than Dijkstra; the page does not single them out.
- No claim that any Korean company uses a specific algorithm. Citations only from `docs/industry.md`.
- Text in `docs/explain/*.md` is each member's own writing. Quote it with attribution; do not rewrite it.
- Road data is from OpenStreetMap: visible "OpenStreetMap" credit and ODbL link are required.

## Brand Commitments

- Project title: "Seoul shortest paths: the same answer for less" (README: "서울 최단경로: 같은 답을 더 싸게 구하기").
- Team C2: Kwon Sehyun, Kim Taehyeong, Jeong Uijong.

## Evidence on Hand

- `results/*.csv` (E1 exhaustive search, E2 speedup and bound tightness, E3 congestion accuracy and timing, re-routing gain, ALT preprocessing cost), `results/graph_table.csv`, `results/match_decision.md`, `results/machine.txt`.
- `data/graphs/*_graph_v1.pkl` (local only, not in git) and `data/queries/*_q_seed42.csv`.
- `figures/*.png` (static figures a to g).
- `docs/industry.md` (verified references), `docs/video/part3-dijkstra-speedup.md`.
- Not available on `main` yet: SUMO re-routing results (E4, open pull request) and member-written explanations for Dijkstra, A*, Bidirectional (open pull request). Do not fabricate either.

## Product Principles

1. Same answer first. Correctness is shown before any speed claim.
2. Show the real run. What moves on screen is what the code did.
3. Label estimated or synthetic data in a few plain words where it appears, never as a warning.
4. Draw every measured value; do not hide one and do not make a show of one.
5. A phone on a shared link is the first reader.

## Accessibility & Inclusion

Works at 375 px width with no horizontal scroll. Nothing is distinguished by color alone. Reduced-motion preference is respected. All controls are reachable by keyboard.
