---
version: 1
slug: "app-page-tsx"
primary_target: "app/page.tsx"
related_targets: []
---

# Surface brief: showcase home page

Scope: the single page of the project showcase site (`site/app/page.tsx`). Mode: Experience.

Audience and job: classmates from the same algorithms course open a shared link on a phone or laptop and want to see what the team built and found. Proof: the team's own search traces and frozen result files. Constraints: every number from `results/*.csv`; synthetic and estimated data labelled where it appears; English text.

Memorable moment: Seoul's roads turning white outward from the start point, then the same yellow route appearing after a fraction of the roads when the method changes.

Unresolved: SUMO (E4) results and member-written Dijkstra, A*, Bidirectional explanations are not on `main`; their sections appear only when the files exist.

## Direction contract

THESIS: One blue traffic sign holds the demo in one column: title, lede, the road network replaying the team's real search, the method plates, and the explanation of the method the reader picked. The rest is one white page; a sign appears only where a sign is meant (instruction, stop). Text sits above and under the map, never on it. The page shows what the team did, with a short plain "Assumptions and limits" list and no caution plates or caveat marks; measured values all stay in their charts and synthetic or estimated data is labelled in plain words. It refuses the dark map with glowing routes, the hero with stat cards beneath it, and the slide deck of framed sections. (Revision 4, 2026-11-15: revision 2 pinned the map under scrolling cards, revision 3 put cards beside it; the user asked for one column with the explanation under the controls.)

OWN-WORLD: Flat retroreflective sheeting. Sign-blue fields with white keylines and white legends for instruction (the only sign field in use), red rings and black numerals for speed roundels, yellow as a mark (route, ALT glyph, hover, focus on blue), unpainted steel for the nav and the footer. White supplementary plates with black text carry every label and control. Discs, triangles, diamonds, squares, octagon. No gradients, shadows or glass. One highway-signage grotesque in heavy weights with tabular numerals; heavy gothic Hangul for place names.

STORY: A classmate watches roads light up from a start point, picks another method plate, and sees it reach the same route after fewer roads while the explanation under the controls names the method and its real count. They then step through each method by hand, pick a road graph and read its measured results, read the congestion experiment, and read what the numbers assume.

FIRST VIEWPORT: One blue instruction sign under the nav, as wide as the article column, white keyline inset, rounded corners. Top to bottom: the title as a two-line sign legend, the lede, the whole road network in faint white with settled roads turning solid white from the start marker and the route in yellow, and nothing else drawn on the map. Under the map, white supplementary plates: four method plates (selected one inverted), play, a scrub track, settled count and travel time, then a white plate explaining the selected method, then the source line. Same order on a phone.

RAISES: One clock (from the deep-dive challenger): the scrub position is roads settled so far, and every number on the sign is pinned to it. Ghost comparison (from the event-display challenger): one query at a time, the previous method's extent stays as a ghost on the same roads. Flat commitment (from the info-noise sleeve): colour fields run to the plate edge, no ornament layers. Permanent marks (from floated pigment): a settled road never dims during play. Direction as structure (from the agit-train): arrows and shapes mean something every time they appear.

FORM: Korean traffic safety sign system (교통안전표지), candidate 7 of 7 on the ordered list. seed:af4bc3d133d74222

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
