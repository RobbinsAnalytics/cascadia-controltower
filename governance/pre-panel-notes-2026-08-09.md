# Pre-panel notes — Cascadia Control Tower

**Written 2026-08-09, before the reading panel ran and before any chart image
was looked at.** This exists so N (the novel share of panel findings) is
measured rather than reconstructed. Reconstructing it after the fact produces a
flattering number, because "did I already know that?" is answered yes far too
often.

## The honest headline

**I have never seen these charts.** The browser pane would not composite during
the build, so every check I ran was programmatic — DOM state, chart options,
computed contrast, canvas dimensions, reflow. That verifies a great deal and
verifies nothing about what the picture looks like. Everything below is
suspicion from reading my own configuration, not observation.

## What I already believe is wrong or at risk

1. **Titles may overflow into the plot.** The longest is 130 characters. Grid
   top is 92px with a subtitle underneath. At narrow widths the title will wrap
   to three lines and may collide with the plot area or the first gridline.

2. **Chart 7's title claims a number the plot does not show.** "Stores ship
   1.9% of units at 2.4x the primary FC's cost per unit" — the plot shows only
   cost per unit. The volume share is in the table, not on the canvas. Under
   the computed-aggregate exception this may be admissible, but the claim's
   first clause is not readable from the marks.

3. **Chart 4's annotation refers to something not plotted.** "Near-identical
   dollar cost, very different consequence" sits over a chart whose only axis
   is percent of margin. The dollar cost is in the title and the table, not on
   the plot.

4. **Chart 3 may equivocate on "short."** The series is the *partial* rate;
   lines that ship zero are a separate series. A reader seeing "ship short
   2.1x as often" could reasonably read "short" as including zero-fills, which
   would make the stated ratio wrong for their reading.

5. **Chart 5 is a step function and may look broken.** Split premiums cluster
   on discrete parcel rates, so $5 and $6 are identical, and $7 and $8 are
   identical. The curve will have flat plateaus that look like a plotting bug
   rather than a property of the cost model.

6. **Chart 1's three lines may read as flat and parallel.** Banked to a 82-98
   band across 24 months, the divergence the whole module is about may not be
   visually obvious — the gap is constant rather than widening.

7. **Chart 6's reference-band label may collide** with the plotted line or the
   band edge. It is positioned insideTop of a markArea that spans most of the
   upper plot.

8. **Annotation labels may collide with the marks they annotate.** Several sit
   at `position: 'top'` or `'right'` at 13px over dense line areas.

9. **The x-axis year format may be cryptic.** Months render as `24-08` style
   with a non-breaking hyphen, every third tick. A reader may not immediately
   read that as August 2024.

10. **Two charts have only two marks** (chart 4: two bars; chart 2: two lines).
    They may read as thin for a full chart block.

## What I am NOT worried about, recorded so a hit here counts as novel

Contrast, text size, table wiring, provenance strips, heading order, keyboard
navigation and reflow were all verified programmatically against the live DOM
and are believed sound. If the panel finds a defect in any of those, it is a
genuine miss on my part and should be counted as novel.
