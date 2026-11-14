---
name: "Seoul shortest paths: the same answer for less"
description: "A stack of Korean traffic safety signs that replays the team's real shortest-path searches."
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
    fontSize: "1.3rem"
    fontWeight: 800
    lineHeight: 1.2
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
  measure: "66ch"
components:
  plate-blue:
    backgroundColor: "{colors.sign-blue}"
    textColor: "{colors.sheeting-white}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 5vw, 5rem) + clamp(8px, 1.6vw, 16px)) clamp(1.25rem, 5vw, 5rem)"
  plate-white:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 5vw, 5rem) + clamp(8px, 1.6vw, 16px)) clamp(1.25rem, 5vw, 5rem)"
  plate-yellow:
    backgroundColor: "{colors.caution-yellow}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 5vw, 5rem) + clamp(8px, 1.6vw, 16px)) clamp(1.25rem, 5vw, 5rem)"
  plate-steel:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.plate}"
    padding: "calc(clamp(1.25rem, 5vw, 5rem) + clamp(8px, 1.6vw, 16px)) clamp(1.25rem, 5vw, 5rem)"
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
  roundel:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.disc}"
    size: "3.2em"
  table-sheet:
    backgroundColor: "{colors.sheeting-white}"
    textColor: "{colors.legend-black}"
    rounded: "{rounded.subplate}"
    padding: "0.5rem 0.75rem"
---

# Design System: Seoul shortest paths

## Overview

**Creative North Star: "The Sign Stack"**

The page is a column of Korean traffic safety signs (교통안전표지) laid on unpainted steel. Each section is one sign: a flat colour field with rounded corners and a keyline set in from the edge. The colour of the field says what kind of statement the section makes. Blue instructs, white regulates and reports, yellow warns, bare steel is the back of the sign.

Everything is flat sheeting. The build has no gradient, no shadow, no blur and no translucent panel anywhere; depth comes only from one opaque thing sitting on another. Type is one highway grotesque in heavy weights with tabular numerals. Shapes (disc, triangle, diamond, square, octagon, red-ringed roundel) carry meaning every time they appear and are never ornament.

Density is generous at the sign level (large padding, one idea per sign) and compact inside it (tables, charts and control plates sit close together). The system is light scheme only.

**Key Characteristics:**
- One section is one sign: field colour, inset keyline, rounded corners.
- Five sign colours plus steel, all flat and opaque.
- White supplementary plates with a black border carry controls, navigation and readouts.
- A method is always its shape and colour together: black disc, blue triangle, red diamond, yellow square.
- Heavy grotesque Latin, heavy gothic Hangul for names, tabular numerals for every figure.
- Nothing is told by colour alone; every source file is named under the thing it feeds.

## Colors

The palette is the traffic sign palette at full strength, on a grey steel ground.

### Primary
- **Sign Blue** (`sign-blue`): the instruction field. Hero sign, the methods sign and other explanatory signs. Also the focus ring on light fields, the A* method colour, the scrollbar thumb and the scrub thumb.
- **Deep Sign Blue** (`sign-blue-deep`): link text on white, yellow and steel fields only.

### Secondary
- **Caution Yellow** (`caution-yellow`): the warning field (results that went against the team, limits). Also the route line on the map, the path and settled vertices in the step demos, the ALT method colour, the hover state of a supplementary plate, the focus ring on blue fields, and text selection.

### Tertiary
- **Regulation Red** (`regulation-red`): rings and limits only. The roundel ring, the caution triangle border, the stop octagon, the destination marker ring, limit and reference lines in charts, the Bidirectional method colour, and the background of a table cell that reports wrong answers. Never a field colour for a sign.

### Neutral
- **Sheeting White** (`sheeting-white`): the regulation and results field; the supplementary plate; legends and keylines on blue.
- **Legend Black** (`legend-black`): text and keylines on white, yellow and steel; plate borders; chart axes; the Dijkstra method colour; the selected plate.
- **Steel** (`steel`): the page ground, the navigation strip, the team sign, the scrollbar track.
- **Steel Ink** (`steel-ink`): secondary text on white, yellow and steel (source lines, notes, quiet table cells).
- **Pale Blue** (`on-blue-secondary`): secondary text on blue, where Steel Ink would not read. Also the fill of a disabled plate on blue.
- **Hairline** (`hairline`): 1px table row rules and chart gridlines.

### Named Rules
**The Field Means Something Rule.** A sign's field colour is chosen by what the section says: blue explains, white reports, yellow warns, steel credits. Colour is never picked for rhythm or variety.

**The Paired Ink Rule.** Secondary text follows its field: Steel Ink on white, yellow and steel; Pale Blue on blue. Links are Deep Sign Blue on light fields and white on blue. The focus ring is Sign Blue on light fields and Caution Yellow on blue.

**The Shape And Colour Rule.** A method is identified by shape and colour together, with its name beside it: Dijkstra black disc, A* blue triangle, Bidirectional red diamond, ALT yellow square (small, medium, large for 4, 8, 16 landmarks). Every glyph has a 2px outline in the current text colour so it reads on any field. A yellow line on white is drawn over a black casing; the yellow route on blue is drawn over a blue casing.

## Typography

**Display Font:** Overpass (with system-ui, sans-serif)
**Body Font:** Overpass (with system-ui, sans-serif)
**Hangul Font:** Gothic A1 at weight 800 (falls back to Overpass, system-ui)

**Character:** One highway-signage grotesque does everything, in three weights: 400 for running text, 700 for labels, 800 for legends. Hangul appears only for place and team names and is always heavy.

### Hierarchy
- **Display** (800, clamp(1.75rem, 7.2vw, 6rem), line-height 0.95, -0.02em): the hero legend only, set as two stacked lines. Below 900px it is sized so the first line stays on one line (clamp(1.75rem, 10.2vw - 5.5px, 3.25rem)). Over the map it carries a 0.1em outline in Sign Blue so roads do not run into the letters.
- **Headline** (800, clamp(1.8rem, 3.6vw, 3.1rem), line-height 1.02, -0.02em): one per sign. It states the finding as a sentence, balanced across lines.
- **Title** (800, 1.3rem, line-height 1.2): sub-blocks inside a sign. Chart titles and table captions are body size at weight 700.
- **Body** (400, clamp(1.0625rem, 0.5vw + 0.95rem, 1.25rem), line-height 1.55): paragraphs and list items, held to 66ch.
- **Label** (700, body size, line-height 1.2): text on supplementary plates.
- **Small** (400, 0.875rem): source lines, credits and notes.
- **Chart text** (13 units in a viewBox drawn at about its CSS width, so about 13px; 700 for axis titles and direct labels).

### Named Rules
**The Tabular Rule.** Every number that can change or be compared (tables, readouts, counters, roundels) uses tabular numerals. A live counter reserves its final width so plates do not move.

**The Heavy Hangul Rule.** Text marked as Korean is Gothic A1 at 800, whatever weight surrounds it.

## Layout

The page is one column of signs. Each sign has a margin of `gap` on all sides, so the steel shows between and around signs, and padding of `pad` at the sides and `pad + gap` top and bottom. Text is held to `measure`; charts, tables and demos use the full width of the sign.

The main breakpoint is 900px. Below it everything is one column. From 900px: chart panels sit three across, the step demo is two columns (figure up to 40rem on the left, controls and narration on the right), and the hero map fills the whole sign with text and controls on top of it. Below 900px the hero reads title, map (a 6:5 block), controls, explanation, credit.

Tables that would not fit a phone reflow below 36rem: the header row is hidden and each cell becomes a labelled row. Other wide tables sit in a focusable scroll region. The navigation row scrolls sideways inside itself. The page itself never scrolls sideways at 375px.

The hero sign is as tall as the viewport minus the navigation row, with a 50rem floor from 900px.

## Elevation & Depth

There are no shadows. The system is flat: depth is stacking order only, with opaque fields on opaque fields (steel, then sign, then supplementary plate or white sheet). Where text must sit over the live map, it gets an opaque patch or outline in the field colour, never a scrim or blur.

### Named Rules
**The Flat Sheeting Rule.** No shadow, gradient, blur or translucent surface. If something needs separating, give it a border, a keyline or an opaque field. The one use of transparency is the hero road network itself: roads not yet settled and the previous method's roads are drawn as fainter white.

## Shapes

- **Sign:** rounded rectangle (`rounded.plate`) with a keyline (`spacing.keyline` thick, in the current text colour) inset by `gap`, its corner radius reduced by the same amount so the curves stay concentric. The steel sign has no keyline.
- **Supplementary plate:** small radius (6px) with a 2px black border. White sheets behind tables on blue use the same 6px radius without a border.
- **Sign shapes:** roundel (circle, red ring 12% of its diameter, black tabular numeral), caution triangle (yellow, red border, black mark), stop octagon (red, white "STOP"), start marker (blue disc with a white ring), destination marker (white disc with a red ring).
- **Method shapes:** disc, triangle, diamond, square, drawn in a 24 by 24 box with a 2px outline.
- **List marker:** a solid square in the text colour, 0.55em.
- **Lines:** 2px chart axes in the text colour, 1px hairlines for grids and table rows, 3px data lines with round joins and caps.

## Components

### Sign (Plate)
One page section. Four tones: blue, white, yellow, steel. Field colour to the edge, inset keyline, first child has no top margin. A sign heading may sit beside a large sign shape (4.5rem caution triangle, 6rem stop octagon) in a wrapping row.

### Supplementary plate (SubPlate)
The single control and label shape. White, 2px black border, 6px radius, padding 0.35em 0.7em, weight 700. It renders as a static label, a link or a button.
- **Hover (links and buttons):** yellow field, black text, 120ms colour change.
- **Selected (radio or toggle):** black field, white text.
- **Focus:** 3px outline offset 3px, in the focus colour of the surrounding sign.
- **Disabled:** 45% opacity by default. On a blue sign the step-demo controls instead use a Pale Blue field with Steel Ink text and border, which stays readable.
- **Uses:** navigation links, method choosers (radio group, arrow keys move), Play/Pause/Replay, Back/Next, step counter, readouts, map place labels (Hangul over English), and the frame around the hero scrub track.

### Navigation
A steel strip above the first sign: a row of supplementary plate links, 0.25rem apart, scrolling sideways inside itself on narrow screens. No active state.

### Scrub track
Inside a supplementary plate: a 4px black track with a 1.25rem Sign Blue thumb and a 3px black border. The plate shows the focus ring when the input inside has focus.

### Roundel
The top speed of a graph as a speed-limit sign. 3.2em across at 1.25rem type; smaller in table cells, larger in chart card headers. Carries a text alternative.

### Caveat
A caution triangle followed by one sentence that says what is estimated or synthetic. It sits directly next to the thing it qualifies.

### Tables
Left-aligned text, right-aligned tabular numbers, 1px hairline under each row, header weight 700. On a blue sign a table sits on a white sheet. A cell reporting wrong answers is red with white 800 text and always shows the count; a zero cell is Steel Ink.

### Charts
Server-rendered SVG, no chart library. 2px axes, hairline grid, direct labels at line ends, method markers that reuse the method shapes, red for limit lines, black dashed for the Dijkstra reference. Each chart has a visually hidden data table. On a blue sign a chart sits on a square-cornered white card.

### Source line
Small secondary text under every chart, table and demo, naming the result file it was built from.

### Sign list
No bullets; a solid square marker in the text colour. On the yellow sign list items are larger (1.2rem).

### Hero search map
A WebGL road network on the blue sign. Unsettled roads are faint white, settled roads solid white, the previous method's roads stay as a ghost, the route is a 4px yellow line over a 9px blue casing. The scrub position is the number of intersections settled and every readout follows it. It autoplays unless reduced motion is requested. Without WebGL2 a white panel shows the same figures as a table.

### Step demo
A small graph or grid drawn in white on blue: yellow for the path and settled vertices, a white ring round the current vertex. Back, Next and a step counter as supplementary plates, with a live narration line and readout plates.

## Do's and Don'ts

### Do:
- **Do** make each new section one sign, and pick its field by meaning: blue explains, white reports, yellow warns, steel credits.
- **Do** put every control, navigation link and readout on a white supplementary plate with a 2px black border.
- **Do** show a method as its shape, its colour and its name together.
- **Do** use tabular numerals for every figure and reserve the width of anything that counts.
- **Do** switch secondary text, link and focus colours with the field (Steel Ink and Sign Blue on light; Pale Blue, white and Caution Yellow on blue).
- **Do** put a source line under every chart, table and demo, and a caution triangle with a sentence next to anything estimated or synthetic.
- **Do** keep text to 66ch and let charts, tables and demos take the full width of the sign.
- **Do** give text over the map an opaque patch or outline in the field colour.

### Don't:
- **Don't** add shadows, gradients, blur or translucent panels.
- **Don't** use red as a sign field; it is for rings, limits and wrong-answer cells.
- **Don't** use a sign shape (roundel, triangle, octagon, disc, diamond, square) as decoration.
- **Don't** distinguish anything by colour alone.
- **Don't** set Hangul lighter than 800, or use it for anything but names.
- **Don't** let the page scroll sideways at 375px; reflow the table or scroll it inside its own region.
- **Don't** add a dark scheme; the tokens are light only.
