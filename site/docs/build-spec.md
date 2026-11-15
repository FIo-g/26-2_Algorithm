# Showcase site build spec

Single source of truth for everyone building `site/`. Product facts are in `site/PRODUCT.md`. If this file and your own taste disagree, this file wins. If this file and the repo's data disagree, the data wins and you report it.

## 0. Revision 2 (2026-11-15): one scrolling page, not a stack of signs

Why: the first build read as a slide deck. Every section was a viewport-sized framed plate with one claim, and only the first sign could be touched. Revision 2 keeps the sign language (tokens, type, SubPlate, glyphs, charts, data rules) and changes the page structure. Where this section disagrees with sections 4, 5 or 7, this section wins. Sections 2, 6, 8, 9, 10 are unchanged.

### 0.1 Page shell

- Page ground is `--white`. `--steel` is only the nav bar and the footer. The map sign sits on the white page at every width.
- Everything after the map is one article column: `<div class="flow">` (max-width 72rem, centred, inline padding `clamp(1.25rem, 5vw, 4rem)`). Sections inside it are plain `<section class="flow-section">`: no border, no background, no min-height. Space between sections is `clamp(4rem, 9vw, 7.5rem)`. The column has the same space above its first section and below its last. Inside a section or a picker panel, blocks (a chart with its source line, a table, a plate, a sub-heading group) are 2rem to 2.5rem apart; a source line belongs to the block above it and never touches the next paragraph. Headings and text sit directly on the page.
- A plate is now an inline sign inside the column, sized by its content: `<Plate inline ...>` (no outer margin, padding `clamp(1.25rem, 3vw, 2.5rem)` plus the keyline gap, keyline kept). Only two things are plates: the map sign (blue) and the step-demo widget (blue). Nothing else gets a frame or a coloured field. No section other than the map stage may be sized to the viewport.
- `--nav-h: 3.75rem` is defined on `:root`. Nav: `position: sticky; top: 0; z-index: 20` from 900px, not sticky below 900px. It marks the section in view with `aria-current="true"` (inverted plate, the look of a selected SubPlate), found with an IntersectionObserver. Links: Map, Same answer, Methods, Results, Congestion, Limits, Team. `html` gets a `scroll-padding-top` that clears the sticky nav and a sticky picker.
- `#team` is a `<footer>` on a full-width steel band, same copy as before.
- `<details>`: the summary looks like a SubPlate button. Native element, no JavaScript.
- `lib/method-copy.ts` holds the one-line description of each method (moved out of `StepDemo`), keyed `dijkstra`, `astar`, `bidir`, `alt`. The step demo and the map cards both read it.

`GraphPicker` (client, `components/ui/GraphPicker.tsx`): switches server-rendered content by road graph.

```tsx
<GraphPicker
  name="results"                 // unique per picker, prefixes element ids
  label="Road graph"             // aria-label of the radio group
  options={[{ id: "gangnam", label: "Gangnam-gu" }, { id: "gss", label: "..." }, { id: "seoul", label: "..." }]}
  initial="seoul"
  panels={{ gangnam: <A />, gss: <B />, seoul: <C /> }}   // rendered on the server, one per option id
/>
```

- A radio group of SubPlate radios (arrow keys move and select, roving tabindex, the same pattern as the method group on the map). All panels are in the HTML; the ones not selected carry the `hidden` attribute. No animation on switch.
- The radio row is `position: sticky` (top `var(--nav-h)` from 900px, `0` below; z-index 10), white background, hairline under it, so the graph can be changed while reading any chart below it. Below 900px the row is one line that scrolls sideways inside itself (like the nav) and keeps the selected plate in view by setting the row's own `scrollLeft` (never `scrollIntoView`, which would move the page). Options are listed largest graph first, so the initial one is visible without scrolling.
- Selection is local to one picker and is not kept in the URL (say so in a `shortcut:` comment).

### 0.2 Map (`MapSection` + `components/hero/`)

Revision 4 (2026-11-15, the user's layout): one column, in this order, at every width. No pinning, no scroll steps, no side cards. Earlier layouts are void: revision 2 pinned the map and let cards scroll over it, revision 3 put the cards in a column beside the map.

Section `#map` is one blue sign with its keyline, natural height: edge to edge from 900px (the user asked twice for a bigger map, and the window height is the limit, so the sign uses the full width), as wide as the article column below 900px. Inside it, top to bottom:

1. `h1` in two lines: "Seoul shortest paths" / "The same answer for less".
2. The lede: "Four exact methods on one road network. Every road that turns white is one our Python code settled, in the order it settled it."
3. The map. The whole network fitted and centred from 900px; on a phone, zoomed to the area Dijkstra searched, as before. Only the two markers, their labels and the route are drawn on it. From 900px the map area is the full width of the sign and as tall as the network at that width, capped at one window under the nav (`100svh - nav - 2rem`). The network is drawn up to 1.25 times its fit-whole size and never wider than the area, so on an ordinary laptop the far north and south of the city run off under the edge (about a fifth of the height in total) while the route and both markers stay in view; a window tall enough shows the whole city. Below 900px: about `min(77vw, 46svh)`.
4. Controls: the method radio group (four plates, shown at every width, wrapping on a phone), Play or Pause, the scrub; then the readouts (settled count, and the estimated travel time once finished).
5. The method explanation, directly above the source line: for the selected method, its `MethodGlyph` and label, the one-liner from `lib/method-copy.ts`, and the facts sentence built from `hero.json` for the graph on the map (Dijkstra: "Here it settled {settled} of {n} intersections before it reached {tLabel.en}."; the others: "Here it settled {settled} intersections: {share} of what Dijkstra settled. Same route, same estimated travel time ({time})." with the same-route check kept). A white plate, since the glyphs need a white ground. All methods and both graphs are server-rendered; only the selected method for the graph on the map is shown. The block keeps the height of its tallest variant, so nothing under it moves when the method changes. It changes when a method plate is chosen, by click or arrow keys.
6. The source line "Replay of site/public/data/hero.json, written by scripts/export_site_data.py", then the OSM credit.

Behaviour:
- Load is unchanged: Dijkstra plays once over about 7 seconds; with `prefers-reduced-motion` the finished state is shown. Choosing another method keeps the previous one as the ghost and plays the new one.
- There is no scroll listener and nothing sticky in this section.
- Marker labels pick the corner that clears the route and the other marker and stays inside the map area.
- With no WebGL2 or a failed load, the fallback table shows as before, and the explanation still renders.

### 0.3 Sections after the map

All inside `.flow`, in this order.

Content rule, revision 4 (2026-11-15). A review against the team's final deck found the page now hid two things it must say, so they are back in plain form: a short "Assumptions and limits" section (the project rule is that estimated speeds are always disclosed) and one sentence on speed under congestion (the deck's main finding is that exact does not mean fast). Everything else in the revision 3 rule below still holds: no caution plates, no caveat marks, no warning colours.

Content rule (revision 3, the user's decision on 2026-11-15): the page shows what the team did. It has no limits section, no caution plates and no caveat lines, and it does not single out the cases that went against us. Two things stay, because without them the page would say something false: every measured value stays in its chart (nothing below 1x is hidden), and synthetic or estimated data keeps one plain label where it appears ("synthetic congestion", "estimated travel time"), written as a description, not as a warning.

- `#same-answer`: h2 "Every method had to match Dijkstra before we timed it", the paragraph and the query-count source line. No caveat line.
- `#methods`: h2 "How each method picks the next intersection" and one sentence on the page ("Step through the real heap pushes and pops on graphs small enough to check by hand."), then the step demo inside an inline blue plate.
- `#results`: h2 "ALT looks at the fewest roads and runs fastest". The claim is checked at build: if on any graph and trip length a method other than ALT is faster or settles fewer intersections, the build throws. Then a `GraphPicker` (seoul, gss, gangnam; initial `seoul`). The panel for graph g, top to bottom:
  1. Facts from `graph_table.csv`: intersections, road segments, top speed as a `Roundel`. Name the source file.
  2. Lead sentence for g, band `>10km`, `alt16`: "On trips over 10 km in {graph}, ALT (16) settled {p} of what Dijkstra settled and ran {s} as fast." A share under 10% is shown with one decimal (4.5%, as in the team's deck), not rounded to a whole percent. The speed is shown with two decimals (4.89x, as in the deck).
  3. Chart A and Chart B for g only: side by side from 900px, stacked below. Each y scale is still computed over all three graphs. The method key appears once, above the two charts. All measured values are drawn.
  4. h3 "How close each bound gets to the true time": the sentence "The straight-line bound assumes the whole trip at the graph top speed.", Chart C for g only, and the `Roundel` with "top speed in the graph".
  5. h3 "What ALT's preprocessing costs": the `e2_alt_prep.csv` rows for g only. From 900px, blocks 4 and 5 sit side by side in two columns.
  After the picker, not tied to a graph: `StopOctagon` beside h3 "Why not just try every path?", the sentence from data ("On subgraphs grown around Gangnam Station, at {n} intersections {k} of {m} queries hit the {limit} second limit.": this is the result of experiment E1 about brute force, not a caveat, and it stays), Chart D and its source. The grid-count table goes inside `<details>` with the summary "Simple paths in a k by k grid".
- `#congestion`: h2 "Slower roads never break the answer. Faster roads do." and the paragraph. Then one plain sentence, no caution mark: "The congestion scenarios are synthetic: multipliers by road class for 03, 08 and 18 h, and a random 30% of edges slowed." Then a `GraphPicker` (seoul, gss; initial `seoul`). The panel for g: h3 "Wrong answers out of {n} queries", the control explanation and the accuracy grid for g; then one sentence on speed, built from `e3_{g}_timing.csv` (speed is the median Dijkstra time divided by the method's median time, scenario `synth08`, band `>10km`, `alt16`, three digits, so Seoul reads 0.457x as in the deck): "Exact is not the same as fast: under 08 h congestion, on trips over 10 km in {graph}, ALT (16) ran at {x} of Dijkstra's speed, because its bounds were built on free-flow times." with its source line; h3 "Does re-routing help one driver?", the two notes and the re-routing table for g. The SUMO block (E4) comes after the picker, unframed, and follows the team's deck (slide 19 and appendix A4, export of 2026-11-15) and the README on `main`:
  - h3 "When many vehicles re-route, it helps only if the fixed routes jam".
  - Setup sentence: "Simulated in SUMO on a 3 x 3 intersection network in Anyang: SUMO's built-in re-routing (Dijkstra, every {period} s) on 30% or 100% of vehicles, against fixed routes. Mean of {seeds} seeds. Signal times and demand are assumed values." `{period}` and the plan names come from `results/e4_manifest.json` (`period_s`, `plans`), `{seeds}` from the CSV.
  - One table, rows are cases and columns are Fixed routes, 30% re-route, 100% re-route (group `all`). Cases, in this order: Webster timing with normal demand (`W`, `medium`), offset coordination with normal demand (`B`, `medium`), Webster timing with heavy demand (`W`, `high`). Plan `A` (queue-responsive) is left out, as in the README and the deck: its controller miscounts re-routed vehicles (`note_plan_A` in the manifest).
  - Cell: mean travel time in seconds, written as the deck writes it: a whole number of seconds, except that a value exactly on a half keeps one decimal (449.5 s). Where not every vehicle arrived (`arrived_pct` below 100) the value is a lower bound: "at least 1,626 s" with "89.2% arrived" under it. Where every vehicle arrived in that cell and in the fixed cell of the same case, show the change against fixed under it ("+7.6%"). Where the fixed cell is a lower bound, show "100% arrived" under the re-routing cells instead of a change.
  - Two reading sentences built from the data: normal demand (Webster): re-routing only made trips longer, and more re-routing made it worse: {262} s, then {281} s, then {408} s. Heavy demand: with fixed routes only {89}% of vehicles arrived, so {1,626} s is a lower bound; with re-routing every vehicle arrived: {449.5} s at 30%, {759} s at 100%.
  - One detail sentence from the `equipped` and `unequipped` rows of `W`, `medium`, `reroute30`: "In the 30% run under normal demand, re-routing vehicles ({301} s) were slower than the rest ({273} s): we read this as vehicles crowding onto the same fast road."
  - One plain note: "Webster timing is computed from the original routes, which may favour fixed routes. The queue-responsive plan is in the file but left out here, because it miscounts re-routed vehicles."
  - Source line: results/e4_summary.csv, results/e4_manifest.json.
- `#limits`: h2 "Assumptions and limits", an unframed section with a plain list of three items, numbers from data: (1) travel times are estimates: OpenStreetMap has no posted speed on {min}% to {max}% of these roads (`graph_table.csv`), so each road gets a representative speed for its road class; (2) congestion is synthetic: real speeds from the national ITS API were collected but not used in these results (`results/match_decision.md`); (3) on the Seoul graphs re-routing is modelled for one vehicle on a fixed congestion snapshot, so it does not change the traffic around it; the SUMO test is a separate 3 x 3 network with assumed signals and demand. Then a source line. No plate, no caution mark.
- `#team`: the footer. Data line: "Road data: OpenStreetMap (© OpenStreetMap contributors, ODbL). Non-commercial coursework." The lines about sources that were collected and not used are gone.

### 0.4 Motion

The search spreading on the map is still the only thing that moves on its own. Scrolling decides which method is shown, and the cards move only because the page scrolls. No fade-in, no slide-in, no parallax, no scroll snapping.

### 0.5 File ownership for this revision

- foundation: `app/globals.css`, `app/page.tsx`, `components/sign/Plate.tsx`, `components/ui/GraphPicker.tsx` and its CSS module, `components/sections/{SiteNav,TeamSection,SameAnswerSection,MethodsSection}.tsx`, `components/demo/StepDemo.tsx` (copy import only), `lib/method-copy.ts`.
- map: `components/hero/*`, `components/sections/MapSection.tsx`.
- results: `components/sections/ResultsSection.tsx` and its CSS module, `components/charts/{MethodPanels,SettledChart,SpeedupChart,TightnessChart,ExhaustiveChart}.tsx`, `charts.module.css`, `panel.module.css`, `lib/results-section.ts`, and `lib/results.ts` (add only).
- congestion: `components/sections/CongestionSection.tsx`, `components/charts/{AccuracyGrid,RerouteGain,SumoTable}.tsx`, `congestion.module.css`.

### 0.6 Done means, in addition to section 11

- At 1440x900, 1280x720, 390x844 and 375x667: no horizontal page scroll; in the map section nothing covers the route, the markers or their labels while a card rests; every stage control is visible while the stage is pinned.
- Tab order: nav, map controls, cards, picker radios, demo controls, details.
- `npx eslint .` reports nothing.

## 1. What we are building

One static page that shows classmates what Team C2 did: four exact shortest-path methods (Dijkstra, A*, Bidirectional Dijkstra, ALT) compared on the real Seoul road network. The thesis is the README title: the same answer for less.

Approaches considered (decided, do not reopen):

- Static HTML + GitHub Pages (earlier plan in PR #32): dropped, the user chose Next.js + Vercel.
- deck.gl / MapLibre with a tile basemap: dropped. Extra dependency and an outside tile service for something 150 lines of WebGL can draw; a basemap also hides that the picture is our own graph.
- Running the algorithms in the browser (JS port or Pyodide): dropped. The project rule is that the page replays what the Python code did.
- Chosen: Next.js App Router, fully static. Numbers read from `../results/*.csv` at build time. Search traces exported once by a Python script and committed under `site/public/data/`. Hero drawn with raw WebGL2. Charts are server-rendered SVG with no chart library.

## 2. Hard rules

1. Every number shown comes from a file under `results/` (read at build) or from `site/public/data/*.json` (written by the exporter). Never type a result number into a component or into copy. Copy that needs a number takes it from the loaders.
2. Under each chart or table, show its source file name, for example `results/e2_summary.csv`.
3. Do not edit anything under `results/`, `figures/`, `docs/explain/`, `docs/ai-usage.md`, or `src/routing/`.
4. All UI text, code, and comments are in English. Hangul appears only as place names and team names.
5. Label synthetic and estimated things where they appear: congestion scenarios are synthetic; travel times are estimates from road class.
6. No statement that any company uses any algorithm. No citations beyond `docs/industry.md`.
7. Nothing is distinguished by colour alone: every method has a shape and a text label.
8. Works at 375 px wide with no horizontal page scroll. Keyboard reachable. `prefers-reduced-motion` respected.
9. No new npm dependencies beyond what `create-next-app` installs, unless this spec names one.
10. Never run `git commit`, `git push`, or `git checkout`. The orchestrator handles git.
11. While other agents are working in parallel, do not run `next build` or `next dev` (they fight over `.next/`). Check your work with `npx tsc --noEmit` from `site/`. The integration step runs the build.
12. Do not paste any text from `site/.impeccable/` into source files.

## 3. Layout of the code

```
site/
  app/layout.tsx          fonts, metadata, <body>
  app/page.tsx            composes the sections in order (integration step owns this file)
  app/globals.css         tokens, base, plate primitives (foundation owns this file)
  components/sign/        Plate, SubPlate, Roundel, CautionTriangle, StopOctagon, MethodGlyph
  components/charts/      primitives.tsx (scales, axes, markers) + one file per chart
  components/hero/        SearchMap.tsx (client, WebGL) and helpers
  components/demo/        StepDemo.tsx (client) and helpers
  components/sections/    MapSection, SameAnswerSection, MethodsSection, ResultsSection,
                          CongestionSection, LimitsSection, TeamSection, SiteNav
  lib/csv.ts              tiny CSV parser + readResults(name)
  lib/results.ts          typed loaders and derived values, one function per CSV
  lib/methods.ts          method ids, labels, shapes, colours
  lib/format.ts           number, duration, percent formatting
  public/data/            hero.json, net-*.bin, trace-*.bin, demos.json (exporter output)
scripts/export_site_data.py   Python exporter (repo root)
tests/test_site_export.py     pytest for the exporter (repo root)
```

Each section file is owned by exactly one agent. Do not edit files you do not own; if you need a change in a shared file, say so in your final report.

## 4. Visual system

(Page structure is superseded by section 0. Tokens, type, sign parts and methods below still apply.) The page speaks in Korean traffic safety signs. Flat colour, thick strokes, rounded plates. No gradients, no box-shadows, no blur, no glass, no decorative icons, no emoji.

### Tokens (put in `:root`)

```css
--blue: #0F4C9C;        /* instruction sign field */
--blue-deep: #0A3572;   /* pressed state on blue, blue text on white */
--on-blue-2: #C9D8EE;   /* secondary text on blue */
--white: #FFFFFF;       /* sheeting */
--red: #D3222A;         /* rings, limits, stop */
--yellow: #FFC400;      /* caution field, route colour */
--black: #000000;       /* ink */
--steel: #D5D9DE;       /* back-of-sign field, page ground */
--steel-ink: #4A535D;   /* secondary text on white and on steel */
--hairline: #C2C8CF;    /* thin rules on white */

--gap: clamp(8px, 1.6vw, 16px);        /* space between plates and plate edge to keyline */
--radius: clamp(18px, 3vw, 30px);      /* plate corner */
--keyline: clamp(3px, 0.5vw, 5px);     /* plate keyline width */
--pad: clamp(1.25rem, 5vw, 5rem);      /* content padding inside a plate */
--measure: 66ch;
```

Page ground is `--steel`. Light scheme only; do not add a dark theme.

### Type

- Latin: Overpass (variable, `next/font/google`, weights 400, 700, 800). Used for everything.
- Hangul: Gothic A1 (`next/font/google`, weight 800, `preload: false`). Only for place names and team names.
- Numbers in tables, readouts and axes: `font-variant-numeric: tabular-nums`.
- Scale: display `clamp(2.6rem, 7.5vw, 6rem)` weight 800, line-height 0.95, letter-spacing -0.02em. h2 `clamp(1.8rem, 3.6vw, 3.1rem)` weight 800, line-height 1.02, `text-wrap: balance`. h3 1.3rem weight 800. Body 1.0625rem, line-height 1.55, max width `--measure`. Small 0.875rem.
- Sentence case everywhere. No all-caps labels. No small label sitting above a heading. No section numbers. No middle-dot separators. No arrows appended to link text.

### Plates

Each `<section>` is one sign:

```css
.plate { position: relative; margin: var(--gap); border-radius: var(--radius);
         padding: calc(var(--pad) + var(--gap)) var(--pad); }
.plate::before { content: ""; position: absolute; inset: var(--gap);
         border: var(--keyline) solid currentColor; border-radius: calc(var(--radius) - var(--gap));
         pointer-events: none; }
.plate--blue   { background: var(--blue);   color: var(--white); }
.plate--white  { background: var(--white);  color: var(--black); }
.plate--yellow { background: var(--yellow); color: var(--black); }
.plate--steel  { background: var(--steel);  color: var(--black); }
.plate--steel::before { display: none; }   /* the back of a sign has no keyline */
```

More space above a heading than below it. One spacing rhythm: multiples of 0.5rem.

### Sign components (`components/sign/`)

- `SubPlate`: the white supplementary plate. White fill, 2px black border, 6px radius, black 700 text, padding 0.35em 0.7em. Variants: static label, `<button>`, `<a>`. Button states: hover fills yellow; selected (`aria-pressed` or `aria-checked`) fills black with white text; disabled is 45% opacity. Focus-visible: 3px outline, yellow on blue plates and blue on other plates, offset 3px.
- `Roundel`: white disc, thick red ring (ring width 12% of diameter), black 800 numeral. Used only for speed limits (vmax of each graph).
- `CautionTriangle`: yellow triangle with rounded corners, red border, black exclamation mark, drawn as inline SVG at 1.4em. Sits before a caveat sentence. Has `aria-hidden` and the sentence itself starts with a plain word such as "Caveat:".
- `StopOctagon`: red octagon, white 800 text "STOP". Used at most twice on the page (bidirectional stop rule; exhaustive search limit).
- `MethodGlyph`: the shape that identifies a method everywhere (legend, plates, chart markers).

### Methods (`lib/methods.ts`)

| id in data | label | shape | fill on white | 
|---|---|---|---|
| `dijkstra` | Dijkstra | disc | black |
| `astar` | A* | triangle | `--blue` |
| `bidir` | Bidirectional | diamond | `--red` |
| `alt4`, `alt8`, `alt16` | ALT (4), ALT (8), ALT (16) landmarks | square | `--yellow` with 2px black stroke |

ALT variants are told apart by their text label and by square size (small, medium, large).

### Motion

One authored moment: the search spreading on the map. Nothing else animates on its own (see 0.4 for scrolling). No scroll-triggered fades. Transitions on controls are 120ms colour changes only.

## 5. Sections, in page order

(Layout and order are superseded by 0.2 and 0.3. The copy and data sources below still apply.)

Headings below are final copy. Body copy may be tightened but not inflated; plain verbs, no marketing words. `{…}` means a value from the data.

### SiteNav
A row of `SubPlate` links at the top of the page ground: Map, Same answer, Methods, Results, Congestion, Limits, Team. On narrow screens the row scrolls sideways inside itself (the page does not).

### 1. `#map` blue plate (MapSection + SearchMap)
- Display heading, two lines: "Seoul shortest paths" / "The same answer for less".
- One sentence: "Four exact methods on one road network. Every road that turns white is one our Python code settled, in the order it settled it."
- The map and its controls: see section 7.
- Small credit inside the plate, bottom: "Road data © OpenStreetMap contributors, ODbL" linking to https://www.openstreetmap.org/copyright.
- Minimum height: the viewport minus the nav.

### 2. `#same-answer` white plate (SameAnswerSection)
- h2: "Every method had to match Dijkstra before we timed it"
- Body: each method's travel time must equal Dijkstra's within a relative error of 1e-9, and its path must be a real path in the graph. 300 queries per graph, 100 in each distance band, random seed 42. Only then is time measured.
- Table "Three graphs" from `graph_table.csv`: name (Gangnam-gu, Gangnam + Seocho + Songpa, All of Seoul), intersections n, road segments m, top speed as a `Roundel` (vmax_kph), share of roads with no posted limit (maxspeed_missing_ratio as a percent).
- Caveat line with `CautionTriangle`: "Caveat: travel times are estimates. Between {min}% and {max}% of roads have no posted speed in OpenStreetMap, so we filled them in from the road class."

### 3. `#methods` blue plate (MethodsSection + StepDemo)
- h2: "How each method picks the next intersection"
- Four tabs (SubPlate buttons with MethodGlyph): Dijkstra, A*, Bidirectional, ALT. One-line description each:
  - Dijkstra: "Always settles the closest unsettled intersection. Never looks at a settled one again."
  - A*: "Adds a lower bound on the remaining time (straight-line distance divided by the top speed), so it leans toward the destination."
  - Bidirectional: "Searches from both ends and stops when the two frontiers together cannot beat the best route found."
  - ALT: "A* with a tighter bound built from precomputed distances to a few landmarks and the triangle inequality."
- The step demo: see section 8.

### 4. `#results` white plate (ResultsSection)
- h2: "ALT looks at the fewest roads. A* can lose to Dijkstra on long trips in small maps." (The first draft said "A* barely helps on small maps"; the review showed the data contradicts it: A*'s best speedup is on the smallest graph, on short trips.)
- Lead sentence built from data for graph `seoul`, band `>10km`: "On trips over 10 km across Seoul, ALT with 16 landmarks settled {settled_ratio as percent}% of what Dijkstra settled and ran {speedup}× as fast."
- Chart A "Share of intersections settled, relative to Dijkstra" (`e2_summary.csv`, column `settled_ratio`).
- Chart B "Speed relative to Dijkstra" (`e2_summary.csv`, column `speedup`), with a red line at 1× labelled "Dijkstra". Any point below 1 gets the caveat treatment.
- Caveat line built from data: list the graph and band combinations where A* or Bidirectional has speedup below 1, e.g. "Caveat: A* was slower than Dijkstra on trips over 10 km in Gangnam-gu ({x}×) …". The reason sentence: "The bound removes few intersections there, and computing it costs time at every one."
- h3: "Why the A* bound is loose". Chart C "How close the first lower bound gets to the true travel time" (median of `ratio` in `e2_tightness.csv` per graph and method; 1.0 is perfect). Sentence: "The straight-line bound assumes the whole trip at the graph's top speed", shown next to the Roundels for each graph.
- h3: "ALT is not free". Table from `e2_alt_prep.csv`: graph, landmarks k, preprocessing seconds, memory in MB (`nbytes`), break-even queries (`breakeven`, rounded to the nearest whole query, so Seoul reads 29, 60, 133 as in the team's deck).
- h3: "Why not just try every path?" (E1). Chart D: exhaustive search time against graph size from `e1.csv` (one dot per query, log time axis, 10 s limit as a red line, timed-out queries drawn at the limit with an open marker). Sentence from data: at {n} intersections, {k} of {m} queries hit the 10 second limit. `StopOctagon` beside it. Small table from `e1_grid.csv`: simple corner-to-corner paths in a k×k grid, with the `source` column shown (counted by us, or OEIS A007764).

### 5. `#congestion` white plate (CongestionSection)
- h2: "Slower roads never break the answer. Faster roads do."
- Body: the bounds were built on free-flow travel times. When congestion only makes edges slower, a lower bound stays a lower bound, so no preprocessing is redone. Label: "Congestion here is synthetic: multipliers by road class for 03, 08 and 18 h, and a random 30% of edges slowed."
- Chart E "Wrong answers out of {n} queries" from `e3_seoul_accuracy.csv` and `e3_gss_accuracy.csv`: a grid of scenario by method showing `n_wrong`. Zero cells are quiet; non-zero cells are red with the number. The `control` scenario is explained: "Control: we made some roads faster than the bound assumes. The bound is no longer a lower bound, and A* and ALT return wrong routes."
- h3: "Does re-routing help one driver?" from `reroute_gain_*_summary.csv`: median saving as a percent and `n_improved` of `n`, by graph, mode (`depart`: congestion known at departure; `midway`: congestion starts halfway) and distance band. Label: "One vehicle, synthetic congestion snapshot."
- Optional small table "Weighted A*" from `e3_*_wastar.csv` (eps, speedup against A*, worst route length ratio). Include only if it fits cleanly.
- SUMO block (E4): render only if `results/e4_summary.csv` exists at build time. If it exists: h3 "What happens when many drivers re-route (SUMO)", a table of mean travel time for `fixed`, `reroute30`, `reroute100` where `group` is `all`, per `plan` and `level`, with `change_pct`. If it does not exist, render nothing here (the Limits section covers it).

### 6. `#limits` yellow plate (LimitsSection)
- h2: "What this does not show"
- List (each item one or two sentences):
  - Travel times are estimates from road class, not measured speeds.
  - Real speeds were collected from the national ITS API and rejected: the monthly call limit ended collection on 2026-11-03 before any morning-peak snapshot existed (`results/match_decision.md`). Congestion in these results is synthetic.
  - No turn restrictions, traffic signals, or time-dependent travel times.
  - Stronger preprocessing methods (contraction hierarchies, customizable route planning) were not implemented.
  - If `results/e4_summary.csv` is absent: "Multi-vehicle re-routing in the SUMO simulator is not part of the frozen results."
  - Timings are from one machine ({cpu} and {python version} from `results/machine.txt`), in pure Python. Settled counts do not depend on the machine.

### 7. `#team` steel plate (TeamSection)
The back of the sign: small black text, no keyline.
- Team C2, DCCS309 Algorithms. 권세현 Kwon Sehyun (problem and data), 김태형 Kim Taehyeong (algorithms), 정의종 Jeong Uijong (results and outlook).
- Links: repository https://github.com/FIo-g/26-2_Algorithm.
- Data sources: OpenStreetMap road network (© OpenStreetMap contributors, ODbL); ITS national traffic information API, Ministry of Land, Infrastructure and Transport (collected, not used in the results); Seoul Open Data Plaza real-time road traffic (registered as a backup source, not used in the results). Non-commercial coursework.
- "Results frozen on 2026-11-09 (git tag results-frozen)."
- "Built with generative AI assistance (Claude Code). Usage is logged in docs/ai-usage.md in the repository."

## 6. Data loading (`lib/`)

- `lib/csv.ts`: `parseCsv(text): Record<string,string>[]` (the result files have no quoted commas; handle quotes anyway in the simplest correct way) and `readResults(name)` which reads `path.join(process.cwd(), '..', 'results', name)` with `fs.readFileSync`, plus `resultsExists(name)`.
- `lib/results.ts`: one typed loader per file used above. Convert numeric columns with `Number`. Derived values (medians, min and max) are computed here, not in components.
- Pages and sections are Server Components. Only `SearchMap` and `StepDemo` (and their controls) are client components.
- `app/page.tsx` exports `const dynamic = 'force-static'`.
- `next.config.ts`: set `outputFileTracingRoot` to the repository root so reading `../results` is allowed.

CSV columns (first row of each file):

```
graph_table.csv            name,n,m,vmax_kph,maxspeed_missing_ratio
e2_summary.csv             graph,scenario,kind,bin,algo,n,median_s,p95_s,median_settled,speedup,settled_ratio
e2_tightness.csv           graph,qid,bin,algo,h0,dist,ratio
e2_alt_prep.csv            graph,k,k_actual,prep_s,nbytes,breakeven
e1.csv                     target_n,actual_n,actual_m,qid,ex_time_s,ex_paths,timed_out,dij_time_s
e1_grid.csv                k,n,paths,source,count_s
e3_{gss,seoul}_accuracy.csv  graph,scenario,algo,n,n_wrong,max_rel_err
e3_{gss,seoul}_wastar.csv    graph,scenario,eps,median_s,speedup_vs_astar,mean_ratio,max_ratio,n,n_ratio,n_unreachable
reroute_gain_{gss,seoul}_summary.csv  graph,scenario,mode,bin,n,n_improved,median_saving,mean_saving,p95_saving,max_saving
e4_summary.csv (may be absent)  plan,level,strategy,group,seeds,arrived_pct,mean_tt_s,p95_tt_s,mean_tt_arrived_s,mean_tt_min_s,mean_tt_max_s,change_pct
```

Graph ids are `gangnam`, `gss`, `seoul`. Distance bands are `<3km`, `3-10km`, `>10km`. Check the real files for exact spellings before coding against them.

## 7. Hero map (`components/hero/SearchMap.tsx`, client)

(Placement, pinning and the controls row are superseded by 0.2. Data formats, drawing, the clock and the fallback below still apply.)

Data (written by the exporter into `public/data/`):

- `hero.json`:
  ```json
  { "graphs": { "gangnam": { "n": 3144, "e": 5000, "aspect": 1.31,
        "net": "net-gangnam.bin", "trace": "trace-gangnam.bin",
        "query": { "s": 12, "t": 345, "sLabel": {"ko": "강남역", "en": "Gangnam Station"},
                   "tLabel": {"ko": "삼성역", "en": "Samseong Station"} },
        "algos": [ { "id": "dijkstra", "settled": 1234, "time_s": 321.5, "path": [12, 40, 345] } ] },
      "seoul": { } },
    "order": ["dijkstra", "astar", "bidir", "alt16"] }
  ```
  `aspect` is width divided by height of the projected network. `e` is the number of undirected segments in the file.
- `net-{graph}.bin`, little-endian: `Uint32 n`, `Uint32 e`, then `Float32[2n]` x,y pairs in 0..1 (x to the east, y to the south, already corrected for latitude so the aspect is `aspect`), then `Uint32[2e]` vertex index pairs.
- `trace-{graph}.bin`, little-endian: for each method in `order`: `Uint32 count`, then `Uint32[count]` vertex indices in the order they were settled.

Behaviour:

- Pick the graph by screen: `seoul` when `matchMedia('(min-width: 900px)')` matches, otherwise `gangnam`. Fetch after mount. Until loaded, the plate shows the heading and an empty map area of the right aspect (no spinner, no layout shift).
- Draw with WebGL2 `gl.LINES`, one draw call. Each segment has a rank for the current method: the larger of its two endpoints' settle indices (a segment is lit when both ends are settled), or a huge value if either end was never settled. A second per-vertex attribute carries the rank under the previously selected method (the ghost).
- Colours on the blue field: unlit segment white at 16% alpha; ghost segment (lit under the previous method, not yet under the current one) white at 42%; lit segment white at 100%. Blending on. Clamp device pixel ratio to 2.
- The clock is "intersections settled so far". The scrubber (`<input type="range">`) runs from 0 to Dijkstra's settled count for every method, so a method that finishes early visibly stops early.
- When the clock reaches the method's settled count, draw the route (from `path`) as a yellow line 4 px wide with round joins on an SVG overlay, and show the travel time. Start and end markers are always visible: white disc with a blue centre for the start, white disc with a red ring for the end, each with a `SubPlate` label (Hangul over English).
- Controls, in a row of plates along the bottom of the sign: a radio group of four method plates with `MethodGlyph`s (arrow keys move, selected is inverted); a play or pause plate; the scrubber; two readout plates: "{settled} of {n} intersections settled" and, once finished, "Travel time {m} min {s} s".
- After the reader has finished a second method, show one sentence under the controls built from data: "Same route, same travel time. {method} settled {percent}% of what Dijkstra did."
- On load, play Dijkstra once from 0 to the end over about 7 seconds, linear in the clock. With `prefers-reduced-motion`, do not autoplay: show the finished state.
- Selecting another method keeps the previous method's full extent as the ghost and plays the new one from 0.
- Readouts update in an `aria-live="polite"` region, at most twice a second.
- Resize: the canvas tracks its container; the network keeps its aspect and is centred.
- If WebGL2 is unavailable, show the heading, the markers' labels as text, and a table of settled counts and travel time per method from `hero.json`.
- No pan, no zoom.

## 8. Step demo (`components/demo/StepDemo.tsx`, client)

Data: `public/data/demos.json`, written by the exporter from real runs of the team's functions:

```json
{ "demos": [ {
    "id": "dijkstra", "title": "Dijkstra on four intersections", "source_test": "tests/test_dijkstra.py::test_dijkstra_stats_counting",
    "vertices": [ {"id": 0, "x": 0.1, "y": 0.5} ],
    "edges": [ {"u": 0, "v": 1, "w": 5} ],
    "s": 0, "t": 3,
    "runs": [ { "algo": "dijkstra", "dist": 12, "path": [0,2,1,3], "settled": 4,
                "h": null,
                "events": [ {"type": "push", "heap": 0, "key": 0, "v": 0},
                            {"type": "pop", "heap": 0, "key": 0, "v": 0, "stale": false},
                            {"type": "loop", "top_f": 3, "top_b": 3, "mu": 5.5} ] } ] } ] }
```

- `events` is the exact sequence of heap pushes and pops the real function made. `stale` marks a pop of an already-settled vertex. `heap` is 0 for the forward (or only) heap and 1 for the backward heap. `loop` events exist only for the bidirectional run: the values of `top_f`, `top_b`, `mu` each time the stop test was evaluated. `h` is the lower bound value per vertex for A* and ALT runs.
- Demos: (1) `dijkstra` on the 4-vertex test graph, (2) `bidir` on the 5-vertex trap graph from `test_bidirectional_not_first_meeting`, (3) `astar` and (4) `alt` on a small grid, each with a Dijkstra run on the same grid for comparison.
- Small graphs (1, 2): draw vertices as white discs with black numerals, edges as white arrows with weights. A step is one pop plus the pushes that follow it. Controls: Back and Next plates, and a step counter "Step {i} of {k}". Each step shows one narration sentence generated from the events, for example "Pop 2 (key 1). Settle it." / "Push 1 with key 2." / "Pop 1 (key 5): already settled, skip." For bidirectional, show `top_f`, `top_b`, `mu` after each step and, on the last step, the stop rule with the `StopOctagon`: "top_f + top_b ≥ μ, so stop."
- Settled vertices turn yellow with black numerals; the vertex being popped has a thick white ring; the final path is drawn in yellow.
- Grids (3, 4): draw the grid as discs. A scrubber replays the settle order; settled vertices fill yellow. Show Dijkstra's settled count against the method's ("A* settled {a} of {n}; Dijkstra settled {d}"). For ALT mark the landmarks with a square. Show `h` of the start vertex and the true distance as "bound {h} of true {dist}".
- Under each demo, a line: "From {source_test}" so a reader can find the test and trace it by hand.
- All controls keyboard reachable; narration in an `aria-live="polite"` region.

## 9. Charts (`components/charts/`)

Server-rendered inline SVG. `primitives.tsx` provides: a linear scale, a log scale, an axis with ticks and a title that includes the unit, the four marker shapes, and a direct label. No legends in boxes: label series directly at the end of their lines, or use a one-line key of `MethodGlyph` plus label above the chart.

- Charts A and B: three small panels side by side (stacked on narrow screens), one per graph, panel title is the graph name. x is the distance band (three positions), y is the value. One line per method with its marker. Share the y scale across the three panels. Black axis lines 2 px, tick labels 0.8rem, `--hairline` grid lines only on y.
- Chart C: horizontal bars from 0 to 1, grouped by graph, one bar per method (A*, ALT 4, 8, 16), value printed at the bar end.
- Chart D: scatter, x is intersections in the subgraph, y is seconds on a log scale.
- Chart E: a table-like grid, not a heat map: rows are scenarios, columns are methods, one grid per graph.
- Every `<svg>` has `role="img"` and an `aria-label` that states the finding in one sentence, built from data. Provide the same numbers in a visually hidden `<table>` after the SVG, or make the visible table the chart.
- Text in SVG uses the page font via `font-family: inherit`. Minimum text size 12 px at 375 px width; charts must not overflow the plate.

## 10. Python exporter (`scripts/export_site_data.py`)

Run from the repo root with the project venv: `source .venv/bin/activate && python scripts/export_site_data.py`. It writes into `site/public/data/`. It may import anything from `routing` but must not change it.

Hero export, for `gangnam` and `seoul`:

- Load `data/graphs/{name}_graph_v1.pkl` with `routing.graph.load_graph`.
- Query endpoints via `g.nearest(lat, lon)`:
  - gangnam: Gangnam Station (37.4979, 127.0276) to Samseong Station (37.5088, 127.0631). This is `routing.figures.FIG_F_QUERY`; import it.
  - seoul: Gimpo Airport (37.5586, 126.8028, 김포공항) to Jamsil Station (37.5133, 127.1001, 잠실역).
- Methods: `routing.bench.standard_algos(g, ks=(16,))` gives the callables; use `dijkstra`, `astar`, `bidir`, `alt16`. Collect settle order and path with `routing.figures.collect_trace`. Get the distance from the callable's return value.
- Assert exactness before writing anything: every method's distance equals Dijkstra's within relative error 1e-9, and every path is valid (use `routing.verify`). Exit non-zero if not.
- Projection: x = (lon - lon_min) * cos(mean_lat), y = (lat_max - lat); scale both by the same factor so x spans 0..1; record aspect = width / height and scale y into 0..(1/aspect) then normalise y to 0..1 separately (the client uses `aspect` to undo this). Simpler statement: x and y each end up in 0..1, and `aspect` is the true width over height.
- Segments: undirected, de-duplicated (`u < v`), built from `g.tail` and `g.head`.
- Write `net-{name}.bin`, `trace-{name}.bin`, and the `hero.json` entry exactly as in section 7.

Demo export:

- Record heap events by temporarily replacing `routing.heap.CountingHeap.push` and `.pop` with wrappers that append to a list (and number heaps in order of construction by wrapping `__init__`), then restoring them. A pop is stale when its vertex was already settled; decide that from the order of `Stats.trace`.
- For the bidirectional run also record `top_f`, `top_b`, `mu` each time the loop evaluates its stop test, using `sys.settrace` on `bidirectional_dijkstra` (read the frame's locals on the line that contains `top_f + top_b >= mu`).
- `h` for A*: `routing.astar.astar_heuristic(g, v, t, g.vmax)`; for ALT: `routing.alt.alt_heuristic(lm, v, t)`.
- Graphs: demo 1 uses the edge list in `tests/test_dijkstra.py::test_dijkstra_stats_counting`; demo 2 the one in `tests/test_bidirectional.py::test_bidirectional_not_first_meeting`; demos 3 and 4 use `routing.synthetic.grid_graph` with a size no larger than 8 by 8, source and target at opposite corners, and for ALT `routing.alt.preprocess_landmarks(g, 4, seed=0)`. Read the tests to copy the exact construction.
- Vertex layout for demos 1 and 2 is hand-placed in the script (x, y in 0..1) so edges do not cross where avoidable; grids are laid out as grids.

Test (`tests/test_site_export.py`): on a `grid_graph`, the recorded events of a Dijkstra run contain exactly `Stats.pushes` pushes and `Stats.pops` pops, the non-stale pops in order equal `Stats.trace`, and the binary writers round-trip (write to `tmp_path`, read back with `struct`, compare). Keep it small. The existing suite must still pass: `pytest tests/test_site_export.py tests/test_correctness.py`.

## 11. Done means

- `cd site && npm run build` succeeds with no type errors.
- `pytest tests/test_site_export.py tests/test_correctness.py` passes.
- At 375 px and at 1440 px: no horizontal scroll, no overlapping text, all controls work with a keyboard.
- Every chart and table names its source file.
- No number in the rendered page was typed by hand.
