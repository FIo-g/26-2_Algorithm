---
name: "Seoul shortest paths: the same answer for less"
description: "One pinned blue traffic sign that replays the team's real shortest-path searches, then one white page of results."
colors:
  sign-blue: "#0F4C9C"
  sign-blue-deep: "#0A3572"
  on-blue-secondary: "#C9D8EE"
  sheeting-white: "#FFFFFF"
  regulation-red: "#D3222A"
  caution-yellow: "#FFC400"
  legend-black: "#000000"
  steel: "#D5D9DE"
  steel-ink: "#4A535D"
  hairline: "#C2C8CF"
typography:
  display:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 7.2vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.8rem, 3.6vw, 3.1rem)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.3rem, 0.9vw + 1.1rem, 1.75rem)"
    fontWeight: 800
    lineHeight: 1.2
  lead:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.25rem, 0.8vw + 1.05rem, 1.6rem)"
    fontWeight: 700
    lineHeight: 1.35
  body:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.0625rem, 0.5vw + 0.95rem, 1.25rem)"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "clamp(1.0625rem, 0.5vw + 0.95rem, 1.25rem)"
    fontWeight: 700
    lineHeight: 1.2
  small:
    fontFamily: "Overpass, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.55
  hangul:
    fontFamily: "Gothic A1, Overpass, system-ui, sans-serif"
    fontWeight: 800
rounded:
  plate: "clamp(18px, 3vw, 30px)"
  subplate: "6px"
  disc: "50%"
spacing:
  gap: "clamp(8px, 1.6vw, 16px)"
  keyline: "clamp(3px, 0.5vw, 5px)"
  pad: "clamp(1.25rem, 5vw, 5rem)"
  pad-inline-plate: "clamp(1.25rem, 3vw, 2.5rem)"
  measure: "66ch"
  column: "72rem"
  gutter: "clamp(1.25rem, 5vw, 4rem)"
  section: "clamp(4rem, 9vw, 7.5rem)"
  heading-top: "2.5rem"
  block: "2rem"
  nav-height: "3.75rem"
components:
  map-sign:
    backgroundColor: "{colors.sign-blue}"
    textColor: "{colors.sheeting-white}"
    rounded: "{rounded.plate}"
    height: "calc(100svh - 3.75rem - 2 * clamp(8px, 1.6vw, 16px))"
  plate-blue-inline:
    backgroundColor: "{colors.sign-blue}"
    textColor: "{colors.sheeting-white}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 3vw, 2.5rem) + clamp(8px, 1.6vw, 16px))"
  plate-yellow-inline:
    backgroundColor: "{colors.caution-yellow}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 3vw, 2.5rem) + clamp(8px, 1.6vw, 16px))"
  subplate:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    typography: "{typography.label}"
    rounded: "{rounded.subplate}"
    padding: "0.35em 0.7em"
  subplate-hover:
    backgroundColor: "{colors.caution-yellow}"
    textColor: "{colors.legend-black}"
  subplate-selected:
    backgroundColor: "{colors.legend-black}"
    textColor: "{colors.sheeting-white}"
  step-card:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.subplate}"
    padding: "1rem 1.25rem"
    width: "min(28rem, 100%)"
  site-nav:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.legend-black}"
    height: "3.75rem"
  graph-picker-bar:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    padding: "0.75rem 0"
  footer-band:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.legend-black}"
    padding: "clamp(2.5rem, 6vw, 4rem) 0"
  roundel:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.disc}"
    size: "3.2em"
---

# Design System: Seoul shortest paths

## Overview

**Creative North Star: "The Pinned Sign"**

One Korean traffic safety sign (교통안전표지) stays pinned while the reader scrolls through four methods, and the road network on it replays the team's real searches. Below it the page is one white article column: headings, paragraphs, charts and tables with no frame round them. A sign appears again only where a sign is meant: a blue instruction sign round the step-by-step demo, and a yellow caution sign round results that went against the team and round the limits. The page ends on a band of bare steel, the back of the sign.

Everything is flat sheeting. The build has no gradient, no shadow, no blur and no translucent panel; depth comes only from one opaque thing sitting on another. Type is one highway grotesque in heavy weights with tabular numerals. Shapes (disc, triangle, diamond, square, octagon, red-ringed roundel) carry meaning every time they appear and are never ornament.

Density is open between sections (a large gap, one finding per heading) and compact inside them (charts, tables and control plates sit 2rem apart or closer). The system is light scheme only.

**Key Characteristics:**
- One pinned sign, then one white column. Sections are not framed.
- A sign (colour field, inset keyline, rounded corners) is used only for instruction (blue) and caution (yellow).
- Five sign colours plus steel, all flat and opaque.
- White supplementary plates with a black border carry controls, navigation and readouts; the selected one is inverted.
- A method is always its shape and colour together: black disc, blue triangle, red diamond, yellow square.
- Heavy grotesque Latin, heavy gothic Hangul for names, tabular numerals for every figure.
- Nothing is told by colour alone; every source file is named under the thing it feeds.

## Colors

The palette is the traffic sign palette at full strength, on a white page.

### Primary
- **Sign Blue** (`sign-blue`): the instruction field. The pinned map sign and the step-demo sign. Also the focus ring on light fields, the A* method colour, the scrollbar thumb and the scrub thumb.
- **Deep Sign Blue** (`sign-blue-deep`): link text on white, yellow and steel only.

### Secondary
- **Caution Yellow** (`caution-yellow`): the warning field (cases slower than Dijkstra, limits). Also the route line on the map, the path and settled vertices in the step demos, the ALT method colour, the hover state of a supplementary plate, the focus ring on blue fields, the step-demo slider, and text selection.

### Tertiary
- **Regulation Red** (`regulation-red`): rings and limits only. The roundel ring, the caution triangle border, the stop octagon, the destination marker ring, limit lines in charts, the Bidirectional method colour, and the background of a table cell that reports wrong answers. Never a field colour for a sign.

### Neutral
- **Sheeting White** (`sheeting-white`): the page ground and article column; the supplementary plate and step card; the sticky graph picker row; legends and keylines on blue.
- **Legend Black** (`legend-black`): text on white, yellow and steel; keylines on yellow; plate borders; chart axes; the Dijkstra method colour; the selected plate.
- **Steel** (`steel`): the navigation strip, the ground round the pinned sign from 900px, the footer band, the scrollbar track.
- **Steel Ink** (`steel-ink`): secondary text on white, yellow and steel (source lines, notes, readout labels, zero cells).
- **Pale Blue** (`on-blue-secondary`): secondary text on blue, where Steel Ink would not read. Also the fill of a disabled plate on blue.
- **Hairline** (`hairline`): 1px table row rules, chart gridlines and the rule under the graph picker row.

### Named Rules
**The Field Means Something Rule.** A colour field is used only where the content is that kind of statement: blue instructs, yellow warns, steel is the back of the sign. Reported results sit on the plain white page, not on a sign.

**The Paired Ink Rule.** Secondary text follows its field: Steel Ink on white, yellow and steel; Pale Blue on blue. Links are Deep Sign Blue on light fields and white on blue. The focus ring is Sign Blue on light fields and Caution Yellow on blue.

**The Shape And Colour Rule.** A method is identified by shape and colour together, with its name beside it: Dijkstra black disc, A* blue triangle, Bidirectional red diamond, ALT yellow square (small, medium, large for 4, 8, 16 landmarks). Every glyph has a 2px outline in the current text colour so it reads on any field. A yellow line on white is drawn over a black casing; the yellow route on blue is drawn over a blue casing.

## Typography

**Display Font:** Overpass (with system-ui, sans-serif)
**Body Font:** Overpass (with system-ui, sans-serif)
**Hangul Font:** Gothic A1 at weight 800 (falls back to Overpass, system-ui)

**Character:** One highway-signage grotesque does everything, in three weights: 400 for running text, 700 for labels and leads, 800 for legends. Hangul appears only for place and team names and is always heavy.

### Hierarchy
- **Display** (800, line-height 0.95, -0.02em): the map sign legend only, two stacked lines. The map sign sets its own size: below 900px clamp(1.5rem, 8.7vw - 5.5px, 3.25rem) so the longer line stays on one line; from 900px clamp(2rem, min(6.7vw, 10.67svh), 6rem), so it also shrinks on a short window. Over the map it carries a 0.1em outline in Sign Blue so roads do not run into the letters.
- **Headline** (800, clamp(1.8rem, 3.6vw, 3.1rem), line-height 1.02, -0.02em): one per section. It states the finding as a sentence, balanced across lines.
- **Title** (800, clamp(1.3rem, 0.9vw + 1.1rem, 1.75rem), line-height 1.2): sub-blocks inside a section. Step card titles and readout figures are 1.5rem at 800. Chart titles and table captions are body size at 700.
- **Lead** (700, clamp(1.25rem, 0.8vw + 1.05rem, 1.6rem), line-height 1.35): the one-sentence conclusion that opens the results section and each graph panel.
- **Body** (400, clamp(1.0625rem, 0.5vw + 0.95rem, 1.25rem), line-height 1.55): paragraphs and list items, held to 66ch. Step cards set 1rem at 1.45 (0.9375rem at 1.4 below 900px).
- **Label** (700, body size, line-height 1.2): text on supplementary plates.
- **Small** (400, 0.875rem): source lines, credits, notes, map place labels.
- **Chart text** (13 units in a viewBox drawn at about its CSS width, so about 13px; 700 for axis titles and direct labels).

### Named Rules
**The Tabular Rule.** Every number that can change or be compared (tables, readouts, counters, roundels) uses tabular numerals. A live counter reserves its final width so plates do not move.

**The Heavy Hangul Rule.** Text marked as Korean is Gothic A1 at 800, whatever weight surrounds it.

## Layout

The page has four parts in order: the navigation strip, the map section, the article column, the footer band.

**Article column.** One centred column, at most 72rem wide, with a side gutter of clamp(1.25rem, 5vw, 4rem). Text inside it is held to 66ch; charts, tables, plates and the picker row use the full column. The footer band runs the full width of the page and its content sits in the same column.

**Spacing rhythm.** Three steps. Between sections, and above the footer: clamp(4rem, 9vw, 7.5rem). Above a heading inside a section: 2.5rem (0.75rem below a headline, 0.5rem below a title); the first child of a section has no top margin. Between blocks inside a section (after a source line, above a caveat, round a chart pair, a method key or a collapsed table): 2rem. A source line sits 0.5rem under the thing it names.

**The pinned sign.** From 900px the map section is a steel ground with `gap` of padding. The blue sign is as tall as the viewport minus the navigation strip and two gaps, and sticks under the strip. The title and lede lie over its first screen and scroll away. Each method is one scroll step 110svh tall; its card sticks 1.5rem inside the keyline at the top left of the sign, at most 28rem wide, and leaves when its step ends. The last step leaves a tail one sign high, so the last card has gone before the sign starts to leave. A step takes over the map when its top edge passes 40% of the viewport height.

Below 900px the whole map section is one blue sign with the keyline round it. Title and lede come first; then the stage (map 42svh or 77vw high, whichever is less; one row of play and scrub; one readout line; credit) sticks to the top of the screen on an opaque blue ground, and the cards scroll under it, one per 55svh step. A step takes over when its top edge passes 65% of the viewport height. The method plates are not shown on the map at this width; scrolling to a card is how the method changes. The source line closes the sign.

**Breakpoints.** 900px is the only layout breakpoint: sticky navigation, the pinned-sign layout, two-column chart pairs, the two-column step demo (figure up to 40rem on the left, controls and narration on the right), wide chart drawings. Two narrower switches exist: readouts on the map use short wording below 640px, and reflow tables stack below 36rem (the header row is hidden and each cell becomes a labelled row). Other wide tables sit in a focusable scroll region. The navigation strip and the graph picker row scroll sideways inside themselves. The page itself never scrolls sideways at 375px.

**Sticky offsets.** Navigation strip: top 0, from 900px only (3.75rem high). Graph picker row: top 0 below 900px, under the strip from 900px. Anchor jumps leave 4.75rem clear at the top (plus the strip height from 900px) so a heading does not land under the picker row.

**Touch targets.** Below 900px navigation links and every radio-group plate are at least 2.75rem high.

## Elevation & Depth

There are no shadows. The system is flat: depth is stacking order only, with opaque fields on opaque fields (page, then sign, then plate or card). Sticky layers are opaque too: the navigation strip is steel, the picker row is white with a hairline under it, the pinned stage is blue. Where text must sit over the live map, it gets an opaque patch or outline in the field colour, never a scrim or blur.

### Named Rules
**The Flat Sheeting Rule.** No shadow, gradient, blur or translucent surface. If something needs separating, give it a border, a keyline, a hairline or an opaque field. The one use of transparency is the road network itself: roads not yet settled and the previous method's roads are drawn as fainter white.

## Shapes

- **Sign:** rounded rectangle (`rounded.plate`) with a keyline (`spacing.keyline` thick, in the current text colour) inset by `gap`, its corner radius reduced by the same amount so the curves stay concentric.
- **Supplementary plate and step card:** small radius (6px) with a 2px black border.
- **Sign shapes:** roundel (circle, red ring 12% of its diameter, black tabular numeral), caution triangle (yellow, red border, black mark), stop octagon (red, white "STOP"), start marker (blue disc with a white ring), destination marker (white disc with a red ring).
- **Method shapes:** disc, triangle, diamond, square, drawn in a 24 by 24 box with a 2px outline.
- **List marker:** a solid square in the text colour, 0.55em.
- **Lines:** 2px chart axes in the text colour, 1px hairlines for grids and table rows, 3px data lines with round joins and caps, 1.5px dashed black for the Dijkstra reference.

## Components

### Navigation strip
A steel strip 3.75rem high at the top of the page: a row of supplementary plate links 0.25rem apart, scrolling sideways inside itself on narrow screens. From 900px it sticks to the top. The link for the section at the reading line (a band 40% down the viewport) is marked `aria-current` and drawn inverted, black with white text.

### Pinned map sign
A WebGL road network on a blue sign with a white keyline. Unsettled roads are faint white, settled roads solid white, the previous method's roads stay as a ghost, the route is a 4px yellow line over a 9px blue casing. The scrub position is the number of intersections settled and every readout follows it. Controls sit along the bottom as supplementary plates: method radio plates (from 900px), Play/Pause, a scrub track, settled count and travel time. Scrolling through the step cards picks the method; a choice made with the plates holds until the active step changes. It autoplays unless reduced motion is requested. Without WebGL2 a white panel shows the same figures as a table and nothing is pinned.

### Step card
One per method, laid over the pinned sign. White, 2px black border, 6px radius, padding 1rem 1.25rem. Method glyph and name as a 1.5rem title, one sentence on how the method works, one sentence with its real counts for the graph on the map.

### Scrub track
Inside a supplementary plate: a 4px black track with a 1.25rem Sign Blue thumb and a 3px black border. The plate shows the focus ring when the input inside has focus.

### Supplementary plate (SubPlate)
The single control and label shape. White, 2px black border, 6px radius, padding 0.35em 0.7em, weight 700. It renders as a static label, a link or a button.
- **Hover (links and buttons):** yellow field, black text, 120ms colour change.
- **Selected (radio, toggle, current nav link, open summary):** black field, white text.
- **Focus:** 3px outline offset 3px, in the focus colour of the surrounding field.
- **Disabled:** 45% opacity by default. On the blue step-demo sign the controls instead use a Pale Blue field with Steel Ink text and border, which stays readable.
- **Uses:** navigation links, radio groups (arrow keys move, roving tabindex), Play/Pause, Back/Next, step counter, readouts, map place labels (Hangul over English), and the frame round the scrub track.

### Graph picker
A radio group of supplementary plates that switches the road graph for everything under it. The row is white with a hairline under it, padding 0.75rem top and bottom, and stays stuck while its panels scroll. Every panel is rendered on the server and is in the HTML; the unselected ones are hidden. Below 900px the row is one line that scrolls sideways inside itself and keeps the selected plate in view. Used for results and for congestion.

### Disclosure (details summary)
A summary is drawn as a supplementary plate, with the state written out after a 2px divider: "Show" when closed, "Hide" when open. Open is inverted like a selected plate. Used for a table that is supporting detail.

### Inline sign (Plate)
A sign sized by its content inside the article column: no outer margin, padding of clamp(1.25rem, 3vw, 2.5rem) plus `gap`, inset keyline, first child has no top margin. Two tones are in use. Blue holds the step-demo widget. Yellow holds the "slower than Dijkstra" table (black row rules, natural-width table) and the limits list.

### Sign heading
A large sign shape beside a title in a wrapping row, 1rem apart: a 4.5rem caution triangle on the yellow sign, a 6rem stop octagon beside "Why not just try every path?".

### Step demo
On the blue inline sign. A method radio group, then a small graph or grid drawn in white on blue: yellow for the path and settled vertices, a white ring round the current vertex. Back, Next and a step counter as supplementary plates, a native range slider tinted Caution Yellow, a live narration line (1.25rem, height reserved for three lines) and readout plates.

### Readout facts
Graph facts as a wrapping grid of label-above-number pairs: label 0.9375rem in Steel Ink, number 1.5rem at 800 with tabular numerals. The top speed is a roundel.

### Roundel
The top speed of a graph as a speed-limit sign. 3.2em across at 1.25rem type; 1.5625rem type beside the tightness chart. Carries a text alternative.

### Caveat
A caution triangle followed by one sentence that says what is estimated or synthetic. It sits 2rem under the thing it qualifies.

### Tables
Left-aligned text, right-aligned tabular numbers, 1px hairline under each row, header weight 700. A cell reporting wrong answers is red with white 800 text and always shows the count; a zero cell is Steel Ink.

### Charts
Server-rendered SVG on the white page, no chart library and no card round them. 2px axes, hairline grid, direct labels at line ends, method markers that reuse the method shapes, red for limit lines, black dashed for the Dijkstra reference. Each chart has a visually hidden data table. From 900px two charts sit side by side.

### Source line
Small Steel Ink text under every chart, table and demo, naming the result file it was built from.

### Sign list
No bullets; a solid square marker in the text colour. On a yellow sign list items are body size, and 1.1em from 900px.

### Footer band
Full-width steel, no keyline and no rounded corners, padding clamp(2.5rem, 6vw, 4rem) top and bottom. Team names (the only Hangul besides place names), repository link, data sources and credits in small text.

## Do's and Don'ts

### Do:
- **Do** write a new section as plain content in the white column: a headline that states the finding, then text, charts and tables with no frame.
- **Do** use a sign only where the content is an instruction (blue) or a caution (yellow), sized by its content inside the column.
- **Do** put every control, navigation link and readout on a white supplementary plate with a 2px black border, and invert the selected or current one.
- **Do** show a method as its shape, its colour and its name together.
- **Do** use tabular numerals for every figure and reserve the width of anything that counts.
- **Do** switch secondary text, link and focus colours with the field (Steel Ink and Sign Blue on light; Pale Blue, white and Caution Yellow on blue).
- **Do** put a source line under every chart, table and demo, and a caution triangle with a sentence next to anything estimated or synthetic.
- **Do** keep text to 66ch and let charts, tables and signs take the full column.
- **Do** keep the three spacing steps: section gap, 2.5rem above a heading, 2rem between blocks.
- **Do** make every sticky layer opaque and set the anchor offset to clear it.
- **Do** give text over the map an opaque patch or outline in the field colour.

### Don't:
- **Don't** frame each section as its own full-height sign; the page read as a slide deck when it did.
- **Don't** add shadows, gradients, blur or translucent panels.
- **Don't** use red as a sign field; it is for rings, limits and wrong-answer cells.
- **Don't** use a sign shape (roundel, triangle, octagon, disc, diamond, square) as decoration.
- **Don't** distinguish anything by colour alone; a state that matters is also written or inverted.
- **Don't** set Hangul lighter than 800, or use it for anything but names.
- **Don't** let the page scroll sideways at 375px; reflow the table or scroll it inside its own region.
- **Don't** add a dark scheme; the tokens are light only.
