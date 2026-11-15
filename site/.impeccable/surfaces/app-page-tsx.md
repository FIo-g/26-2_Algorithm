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

THESIS: The map on one blue traffic sign stays pinned while the reader scrolls through the four methods, and the road network on it replays the team's real search. The rest is one white page; a sign appears only where a sign is meant (instruction, stop). Text sits beside the map, never on it (revision 3: the cards used to cover the search they describe). The page shows what the team did: no limits section, no caution plates, no caveat lines; measured values all stay in their charts and synthetic or estimated data keeps one plain label. It refuses the dark map with glowing routes, the hero with stat cards beneath it, and the slide deck of framed sections (revision 2, 2026-11-15: the first build read as slides).

OWN-WORLD: Flat retroreflective sheeting. Sign-blue fields with white keylines and white legends for instruction (the only sign field in use), red rings and black numerals for speed roundels, yellow as a mark (route, ALT glyph, hover, focus on blue), unpainted steel for the nav and the footer. White supplementary plates with black text carry every label and control. Discs, triangles, diamonds, squares, octagon. No gradients, shadows or glass. One highway-signage grotesque in heavy weights with tabular numerals; heavy gothic Hangul for place names.

STORY: A classmate watches roads light up from a start point, scrolls, and sees each next method reach the same route after fewer roads while a white plate names the method and its real count. They then step through each method by hand, pick a road graph and read its measured results, and read the congestion experiment.

FIRST VIEWPORT: One blue instruction sign under the nav (sticky from 900px), white keyline inset, rounded corners, in two columns from 900px. Left: the title as a sign legend, the lede, and the first method card coming up. Right: the whole road network in faint white, pinned; settled roads turn solid white from the start marker; the route is yellow; nothing else is drawn on the map. Under the map, white supplementary plates: four method plates (selected one inverted), play, a scrub track, settled count and travel time. On a phone the map is pinned on top, the cards pass under it, and scrolling is the only way to change method.

RAISES: One clock (from the deep-dive challenger): the scrub position is roads settled so far, and every number on the sign is pinned to it. Ghost comparison (from the event-display challenger): one query at a time, the previous method's extent stays as a ghost on the same roads. Flat commitment (from the info-noise sleeve): colour fields run to the plate edge, no ornament layers. Permanent marks (from floated pigment): a settled road never dims during play. Direction as structure (from the agit-train): arrows and shapes mean something every time they appear.

FORM: Korean traffic safety sign system (교통안전표지), candidate 7 of 7 on the ordered list. seed:af4bc3d133d74222

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
