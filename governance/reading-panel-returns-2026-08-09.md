# Reading panel — verbatim returns

**Cascadia Control Tower · 2026-08-09 · Rule 7.4.**

Annex to `chart-review.md` §2. Four seats, spawned in a single message so they
ran concurrently and could not see one another's work. Each seat was given the
seven PNGs at `panel/charts/` and nothing else, and was instructed that those
seven files were the only thing it could open.

**These returns are unedited.** Tidying them would turn evidence into the
author's paraphrase, which is the thing the panel exists to route around. Chart
numbers below are the render order in `panel/charts/manifest.json`:

| # | Chart |
|---|---|
| 1 | Three fill definitions, monthly |
| 2 | Achieved unit fill vs single-node counterfactual |
| 3 | Ship-short and multi-node rates by SKU velocity band |
| 4 | Split premium as a share of margin, by banner |
| 5 | Share of splits above each cost threshold |
| 6 | Parcel cost per unit by fulfilment node |
| 7 | Months of stock vs the Census sector band |

---

## Seat 1 · Director of Distribution Centre Operations

**Chart 1**

- **SENTENCE** — *"This is the one that says whichever fill number you quote me depends entirely on which of three definitions you picked, and they sit about seven points apart, so I'd tell a colleague we should stop arguing about the number until we agree which one we're being scored on."* → carries the title's claim: **yes**
- **NUMBER** — *"Seven points — it's right in the title, '7.0 points apart.' The one I'd actually repeat in an ops meeting is the order fill trough: the green line drops to about 78 percent at 11/24 on the left axis, and again to about 79 at 11/25."* — located at: **title** for the headline figure, **mark + axis** for the trough
- **QUESTION** — *"Which one of these three am I judged on, and which one does the merchant or the vendor scorecard use? Because if I'm run on order fill and they're quoting me unit fill, we've been having two different conversations for years."*
- **GAP** — *"I could not tell whether the two big troughs are peak season or a one-off event, and there's nothing on here separating the two banners. Off-Main and Alder & Vance don't behave the same and this blends them."*

**Chart 2**

- **SENTENCE** — *"This says that if someone tells me to stop splitting orders, I hand back roughly two and a half to three points of fill, so splitting isn't a failure mode here, it's how we make the number."* → carries the title's claim: **yes**
- **NUMBER** — *"2.7 points, from the title. The chart itself I read as the green running maybe two to four points above the dashed line most months, widest at the November troughs where dashed drops to about 85 percent and green holds around 89."* — located at: **title**, with an eyeballed range off the marks
- **QUESTION** — *"Is the dashed line measured or is it your model? ... my real question is what assumptions sit inside it — specifically whether it lets the single node be chosen with hindsight or has to pick before it knows what's coming."*
- **GAP** — *"The cost side. It tells me splits buy me 2.7 points of fill and calls it a cost that's hidden, but there's no dollar figure anywhere on this chart, so I can't tell if 2.7 points is worth what I'm paying for it. That's the trade I'd actually have to make."*

**Chart 3**

- **SENTENCE** — *"Slow-moving SKUs are the problem child on both counts — they get shipped short more than twice as often and they need a second building four times as often — and the story is that they're spread too thin across too few locations."* → carries the title's claim: **yes**
- **NUMBER** — *"17.07 percent, the label on top of the blue bar over C·slow. That's the one that jumps off the page."* — located at: **data label**
- **QUESTION** — *"Who decides how many nodes a slow SKU gets ranged in? ... if that placement rule is what's driving both of these, that's a buying and allocation decision, not something I can fix on my dock."*
- **GAP** — *"Volume. I have no idea whether C·slow is two percent of my lines or forty percent, and 17 percent of a tiny tail is a very different problem from 17 percent of half the business."*

**Chart 4**

- **SENTENCE** — *"The same five and a half dollars for a second box is nearly nothing on a premium order and a real bite on an off-price one, so the cost of splitting has to be judged per banner, not on a network average."* → carries the title's claim: **yes**
- **NUMBER** — *"12.09 percent, the label above the Off-Main bar. Against 3.55 on Alder & Vance."* — located at: **data label**
- **QUESTION** — *"Where did $5.46 come from and is it one flat number applied to every split, or an actual per-order cost? If it's a flat assumption then this whole chart is really about the margin denominator, not about parcel cost."*
- **GAP** — *"No count of how many split orders each banner has. Twelve percent of margin on a handful of orders is noise; twelve percent across a third of Off-Main's volume is a real hole."*

**Chart 5**

- **SENTENCE** — *"This is a threshold-picking chart — wherever you set the line for 'this split cost too much,' Off-Main always has more orders over it than Alder & Vance, though honestly the two curves are closer than the title made me expect."* → carries the title's claim: **yes**
- **NUMBER** — *"About 20 percent — the blue Off-Main line starts flat at roughly 20 on the left axis at $5 and $6, against green at about 14."* — located at: **mark + axis**
- **QUESTION** — *"What am I supposed to do with this? Is the ask that we set a cost cap and refuse splits above it, and if so what fill do I give up at each threshold — because that isn't on here."*
- **GAP** — *"The consequence. Every point on both curves is a share of splits, never a count and never a dollar total ... And the $4 point being in the table but not plotted took me a second to accept; I read the note but it still felt like a piece was missing off the left end."*

**Chart 6**

- **SENTENCE** — *"Shipping from stores costs me roughly double to two and a half times what the main FC costs, and all four stores are worse than both FCs — no exceptions, no overlap."* → carries the title's claim: **yes**
- **NUMBER** — *"$4.12 at Store 104 against $1.65 at Cascade Ridge FC, both labelled right on top of the bars."* — located at: **data label**
- **QUESTION** — *"Of that 1.9 percent of units going out of stores, how much of it was a genuine rescue of an order I'd otherwise have missed, and how much was the system routing there when the FC could have covered it?"*
- **GAP** — *"The 1.9 percent share is in the subtitle text, not on the chart, so the visual gives four fat bars equal weight to two FC bars that do essentially all the work. I had to read a sentence to learn the expensive nodes are a rounding error of volume."*

**Chart 7**

- **SENTENCE** — *"This one I'd flag as apples to oranges — it shows us holding about a month of stock against a sector band of two to three and a half, and I don't believe that gap is real performance."* → carries the title's claim: **no** — the seat rejects the comparison rather than repeating it
- **NUMBER** — *"0.97 months, in the title. The line itself sits just under 1.0 the whole way, dipping to roughly 0.55 at 11/24."* — located at: **title**, with the trough read off the marks
- **QUESTION** — *"Is the grey band whole department-store companies including everything sitting on the sales floor, and is my line just this DC network? Because if so I'm comparing one warehouse to entire retail chains and of course I look lean — that isn't a win, it's a different measurement."*
- **GAP** — *"Any acknowledgement of that mismatch on the chart itself ... the subtitle says inventory at cost over sales at retail, which mechanically pushes my ratio down, and nothing on the chart tells me by how much. That single note is doing a lot of quiet work."*

---

## Seat 2 · Director of Supply Chain Finance

**Chart 1**

- **SENTENCE** — *"This is the 'which fill rate are you quoting me' chart — depending on which of the three definitions you pick you can tell the board 96 or you can tell them 89, and nobody's lying."* → carries the title's claim: **yes**
- **NUMBER** — *"Seven points. It's in the title — '7.0 points apart.' On the chart itself I'd take the November spikes: the green order-fill line drops to about 78 on the left axis in 11/24 ..."* — located at: **title**, then marks
- **QUESTION** — *"Which of these three is the number we currently report to the banners and to anyone external — and has it always been that one? If someone quietly moved from order fill to unit fill at some point, our trend is fiction."*
- **GAP** — *"There's no dollar or margin consequence anywhere on this ... Also no banner split — this says 'both banners' and I need Alder & Vance separate from Off-Main, because the answer to 'should we spend to fix this' is different for each. And the whole thing sits on a 73-99 axis, so the peak troughs look more dramatic than a 100-scale would show."*

**Chart 2**

- **SENTENCE** — *"Their claim is that if we banned split shipments to save parcel cost we'd give back roughly 2.7 points of unit fill, so splitting is buying us service."* → carries the title's claim: **yes**
- **NUMBER** — *"2.7 points, from the title. The header text also gives the range of the gap as 1.80 to 4.12 percentage points ..."* — located at: **title** and the description paragraph, not the marks
- **QUESTION** — *"What did you assume the network does *instead* when the split is forbidden ... And 2.7 points of fill against how many dollars of avoided second parcels? That trade is the whole decision and it isn't on this chart."*
- **GAP** — *"The cost side. This is a service-benefit chart with no cost axis, and the subtitle admits the counterfactual is 'evaluated on the inventory position before each allocation,' which I don't fully follow on first read."*

**Chart 3**

- **SENTENCE** — *"Slow-moving SKUs are the ones splitting and shipping short — 17% of slow-mover lines touch a second node against 4% of fast movers — because we only stock them in two places."* → carries the title's claim: **yes**
- **NUMBER** — *"17.07%, the data label sitting on top of the blue bar over 'C · slow.'"* — located at: **data label**
- **QUESTION** — *"How is a SKU assigned to a band, and how often does it get rebanded? If velocity is measured over the same window as the split rate, this is partly circular. And separately — what share of *units* and of *margin* sits in band C?"*
- **GAP** — *"Volume weighting. Three bands with no sense of how big each one is, so I can't turn any of this into money."*

**Chart 4**

- **SENTENCE** — *"Same $5.46 second parcel, but it eats 12% of an Off-Main order's margin and only 3.5% of an Alder & Vance order's — this is the chart that says the off-price banner can't absorb what the premium banner can."* → carries the title's claim: **yes**
- **NUMBER** — *"12.09%, the label above the Off-Main bar. Against 3.55% on the Alder & Vance bar."* — located at: **data label**
- **QUESTION** — *"Is the $5.46 incremental cash — actual carrier spend on a second parcel — or does it carry allocated overhead, warehouse labour, packaging? ... And is that $5.46 an average across both banners, or the same charge applied to both?"*
- **GAP** — *"The denominators ... Two bars, two labels, no volumes — I don't know if Off-Main split orders are 200 a month or 200,000. This is the most useful chart in the pack conceptually and the least actionable as drawn."*

**Chart 5**

- **SENTENCE** — *"If you set a cost ceiling on split shipments, the same threshold catches a materially bigger slice of Off-Main's splits than of Alder & Vance's at every level above $4."* → carries the title's claim: **yes**
- **NUMBER** — *"At $5 the blue Off-Main line starts a shade above 20% and the green Alder & Vance line at about 14% — read off the left axis, no labels on the lines."* — located at: **mark + axis**
- **QUESTION** — *"Why is the x-axis unevenly spaced — $5, $6, $7, $8, $10, $12, $15, $20? The gaps between ticks aren't equal so the slope of the fall is distorted, and the steepest-looking drop between $6 and $7 might just be the spacing."*
- **GAP** — *"No dollars ... Pair it with chart 2 and you'd have a decision; alone it's a shape. Also the $4 point is dropped off the plot and only mentioned in the note, which stopped me for a second."*

**Chart 6**

- **SENTENCE** — *"Shipping from a store costs us more than double what the main FC costs per unit — about $4 against $1.65 — so every store-sourced order is an expensive rescue."* → carries the title's claim: **yes**
- **NUMBER** — *"$1.65, the label on the Cascade Ridge FC bar at the right end, against $4.12 on Store 104 at the left. Roughly 2.5x."* — located at: **data label**
- **QUESTION** — *"What's in the store number — is it just carrier cost, or have you loaded store labour and packing into it? A store associate picking and packing is usually already-paid store payroll, so if that's in there the $4.12 isn't incremental."*
- **GAP** — *"Volume. The subtitle says stores carry 1.9% of units and points me to the table, which is the right disclosure but it should be on the chart ... Also Store 104 and Store 103 are both $4.12, which reads odd on first look; I don't know if that's real or rounding."*

**Chart 7**

- **SENTENCE** — *"Our network runs about one month of stock against a real department-store sector range of 2 to 3.6, so we're either far leaner than the sector or we're not measuring the same thing."* → carries the title's claim: **partly** — the seat states the finding and immediately doubts it
- **NUMBER** — *"0.97 months, from the title. The line sits around 1.0 on the left axis all the way across and the shaded band's floor is 2.0 — the gap is visible without needing a label."* — located at: **title**, gap visible on the marks
- **QUESTION** — *"Is this comparable? The sector number is a whole department-store balance sheet — stores, backroom, in-transit, everything. If this line is only DC inventory for the fulfilment network, then we're a fraction of a company against a whole company and the comparison flatters us badly. That's the only thing I'd want answered before this goes anywhere."*
- **GAP** — *"What's actually in the numerator ... And there's no scenario where a line that never once touches the reference band is just reported as-is — I'd expect a note explaining the definitional difference, or a like-for-like restatement."*

---

## Seat 3 · VP of Merchandise Planning, off-price banner

**Chart 1**

- **SENTENCE** — *"Somebody's finally admitted that when we argue about fill rate in this building we're arguing about three different numbers, and the one that actually matters to a customer — did the whole order show up — is the worst-looking of the three by about seven points."* → carries the title's claim: **yes**
- **NUMBER** — *"Seven points. It's in the headline ... in November of both years the gold line is sitting a hair under 90% and the green one drops to about 78%, so in peak it's more like eleven or twelve. The 78 is me reading the bottom of that green trough against the 80% gridline."* — located at: **title**, then **mark + gridline**
- **QUESTION** — *"Which one of these three has been in my scorecard for the last two years?"*
- **GAP** — *"My banner. This is 'both banners' — one blended number. Off-Main runs a different assortment with different depth, and I'd bet money our order fill sits below the blend and Alder & Vance sits above it, and this chart lets that hide."*

**Chart 2**

- **SENTENCE** — *"It's a what-if: if we made every order ship out of one building, we'd lose a couple of points of fill, so splitting is doing real work and isn't just the DC being sloppy."* → carries the title's claim: **yes**
- **NUMBER** — *"2.7 points, off the headline. I couldn't get that off the picture — the two lines are close enough that I'd have said 'two, maybe three' by eye."* — located at: **title only; explicitly not obtainable from the plot**
- **QUESTION** — *"Who built the counterfactual and what did it assume? ... I want to know whether the pretend single node was allowed to hold the inventory it would actually have held."*
- **GAP** — *"The other side of the ledger ... there's no dollar anywhere on this chart. Two-point-seven points of fill against what — a million a year, ten? And again, no banner split, which matters enormously here because a second parcel costs my banner far more relative to the sale than it costs theirs."*

**Chart 3**

- **SENTENCE** — *"The slow-moving SKUs are the ones going out in two parcels and the ones shipping short — same root cause, thin stock spread across too few doors — and they're four times worse than the fast movers on the multi-node side."* → carries the title's claim: **yes**
- **NUMBER** — *"17.07% of slow-mover order lines use two nodes. It's printed right on top of the tall blue bar on the right."* — located at: **data label**
- **QUESTION** — *"Is 'slow' defined on units or on dollars, and over what window? Because in off-price a slow mover by units can be a perfectly good margin item, and if the fix that comes out of this chart is 'stop buying band C,' I'm going to fight that."*
- **GAP** — *"Volume ... If slow movers are three percent of my lines then 17% of them is a rounding error and I don't want a task force. The subtitle says slow movers sit at two nodes and fast at six, which sounds like the answer is a ranging decision, not a buying decision — but it's asserted, not shown."*

**Chart 4**

- **SENTENCE** — *"This is the one aimed at me: the same five-dollar-something second box eats twelve percent of the margin on an Off-Main order and only four on an Alder & Vance order, purely because our tickets are thinner."* → carries the title's claim: **yes**
- **NUMBER** — *"12.09%, printed above the tall blue bar over Off-Main. Alder & Vance is 3.55% above the short green bar. The $5.46 parcel cost is in the headline, not on the chart."* — located at: **data label**; the dollar figure explicitly **not on the plot**
- **QUESTION** — *"Is that dollar cost genuinely the same for both banners, or is it an average that's been applied to both? Because if $5.46 is a blended network number and Alder & Vance actually ships heavier, more expensive parcels, then this chart is flattering them and I've been handed the bad end of an average."*
- **GAP** — *"How many orders this touches ... If it's four percent of volume this is a footnote, if it's twenty percent it's the biggest number in my P&L that nobody's talking about."*

**Chart 5**

- **SENTENCE** — *"However you set the cost cutoff for allowing a split, more of my banner's orders trip over it than theirs, all the way up the scale."* → carries the title's claim: **yes**
- **NUMBER** — *"At $5 the blue Off-Main line starts at about 20% and the green Alder & Vance line at about 14%. Those are eyeballed off the left axis — no labels on the lines."* — located at: **mark + axis**
- **QUESTION** — *"Is somebody about to set a threshold? Because the honest reading of this chart is 'we're choosing a number and it will hit Off-Main harder,' and I want to know if that decision has already been made or if I'm being consulted."*
- **GAP** — *"Any indication of what the right threshold is. It's a menu with no recommendation and no cost curve on the other side."*

**Chart 6**

- **SENTENCE** — *"Shipping out of a store costs us more than double what the main FC costs, and all four stores are worse than both distribution centres."* → carries the title's claim: **yes**
- **NUMBER** — *"$4.12 at Store 104 and Store 103, labelled above both bars, against $1.65 at Cascade Ridge FC, labelled on the last bar."* — located at: **data label**
- **QUESTION** — *"Then why did those store shipments happen? ... This chart shows me the price of the rescue and says nothing about the cause, and the cause is the only part I can do anything about."*
- **GAP** — *"Volume again, and it's the thing that makes this chart nearly harmless or nearly a crisis ... that belongs on the chart, not underneath it."*

**Chart 7**

- **SENTENCE** — *"We're carrying about a month of stock where the department-store sector carries two to three and a half, so on this measure we're running lean by a country mile."* → carries the title's claim: **yes**
- **NUMBER** — *"0.97 months for us against 2.03 to 3.64 for the sector — both in the headline, and the band is labelled across the grey block. Our line never gets near the band; the low point is somewhere around 0.5 in November '24, read off the axis."* — located at: **title** and **band label**, trough off the marks
- **QUESTION** — *"Is this actually comparable? Ours looks like a fulfilment-network number and theirs is a whole retailer including everything sitting on the selling floor ... I don't want to walk into a room and say we're four times leaner than the sector if it isn't true."*
- **GAP** — *"The connection to the rest of the deck. Every other chart says we're shipping short and splitting parcels — this one says we hold almost no stock. That's the same story, and nothing on the chart joins them up. Nobody has told me whether being this lean is the achievement or the cause."*

---

## Seat 4 · Visualization reader (canvas only)

This seat answers a six-item shape rather than the domain seats' four, and was
told to ignore any data tables and work from the plots.

**Chart 1** — *"My first read is 'this is a seasonality chart.' The title says something different — it's about definitional spread ... The picture's loudest feature (the November collapse) is not what the title is about, and the title's feature (the gap) is the quieter one."* On the title's claim: *"'7.0 points apart' — I cannot find 7.0 anywhere. The gap between the gold and green lines varies: ~5.3 pts at 08/24, ~11 pts at the 11/24 trough ... 7.0 is presumably an average, but there is no mark, reference line, or month where I can read it."* Hard to read: *"The y-axis carries both a 75% tick and a 73% floor tick almost touching each other at the bottom — an odd non-round floor that reads as a rendering artifact. Same at the top: 95% then 99%."* Grayscale: survives on direct labels. Number: *"Order fill bottoms at roughly 78% at 11/24 ... I would not quote '7.0 points apart' from this plot."*

**Chart 2** — Title and picture agree on subject. *"'Would cost 2.7 points' — again no. The visible gaps run from about 1 point (02/25) to about 4 points (11/24) ... If I pick any month at random I get the wrong number."* Disclosure praised: *"the footnote says plainly 'counterfactual is modelled, not measured.' That is the right disclosure and it's made where a skeptic will look."* Hard to read: *"The annotation ... sits down at ~83%, in empty space well below the gap it points at; nothing connects them."* And the cross-chart finding: *"the achieved unit-fill series is **gold in chart 1 and green in chart 2**. A reader moving between the two will not recognize it as the same series."* Grayscale: *"The best of the seven. Solid vs dashed carries the whole distinction."*

**Chart 3** — Form correct. *"'One cause' — **not shown**. Three category points with two co-rising series is co-movement, nothing more. The in-plot annotation states 'one cause, thin fragmented stock' as fact. That's the weakest link in the chart, and it's asserted twice."* Hard to read: *"Because they sit over different groups, 'Uses two nodes' reads at first glance as a label for B's blue bar specifically rather than for the blue series. I looked twice at that."* Grayscale: *"Genuinely distinct textures; this one is properly redundantly encoded."*

**Chart 4** — *"'The same $5.46 second parcel' — **completely absent from the plot.** The y-axis is percent only. The word doing the most work in the title, 'the same,' is exactly what I cannot check."* Also: *"the title rounds 3.55% to '4%' while the label on the bar says 3.55%."* And: *"The 17% and 15% ticks nearly collide at the top of the axis."* Form: *"a very thin chart — two bars, both labelled, is a sentence with axes."*

**Chart 5** — *"This is the clearest form problem in the set. The x-axis is dollars — a continuous quantity — but the ticks $5, $6, $7, $8, $10, $12, $15, $20 are drawn at **equal spacing**. The $8→$10 step is twice the $5→$6 step and the $15→$20 step is five times it, yet all occupy the same width. Every slope in this chart is distorted."* Also: *"The 'Alder & Vance' in-plot label sits directly on top of the green line near $6–$7."* Grayscale: *"Weakest of the seven ... two solid same-weight lines converging, hue-only. A dash pattern on one would fix it — chart 02 already does exactly that."*

**Chart 6** — *"'More than double the primary FC's cost per unit' — **I cannot verify this, because nothing on the chart says which FC is primary.** ... If primary means Cascade Ridge, double is $3.30 and all four stores clear it — claim true. If primary means Fernhill, double is $4.54 and *no* store clears it — claim false. The chart's colour coding separates stores from FCs but not primary from secondary, so the truth of the headline turns on a fact the picture withholds."* Also: *"Store 104 and Store 103 are both $4.12 and drawn at identical height, presented inside an ordered ranking with no indication it's a tie."* And: *"the volume weighting, which is what determines whether this cost gap matters at all, is deliberately kept off the plot."*

**Chart 7** — *"'And dips in the same season' — **the comparison is not drawable from this chart.** I can see the plotted line dip at 11/24 and 11/25. I cannot see the sector do anything, because the sector is rendered as a *static* band with no time dimension at all. The annotation says 'as the real series does' — referring to a series that is not on the plot. Half the title rests on data that isn't in the picture."* Also: *"the 0–4.0 axis ... squeezes the network series into the bottom quarter, flattening it into a near-straight squiggle — which visually *undercuts* the 'dips' claim the title is making."* And: *"The bottom annotation's second line, 'series does,' runs into the 0.0 gridline and axis labels."*

**Cutting across all seven** — *"Five of the seven headline numbers are not on their plots. 7.0 points (ch.1), 2.7 points (ch.2), $5.46 (ch.4), 0.97 months (ch.7), and both ratios in ch.3 are aggregates, off-axis quantities, or arithmetic I have to perform. Where a title states a number, a reader should be able to put a finger on it. Charts 5 and 6 do this well; the rest ask for trust."* · *"Axis ceilings collide with their neighbours ... It reads as a bug, not a decision."* · *"Series colour is not stable across charts."* · *"The descriptive paragraph appears above the title in every image, so a sighted reader gets a flat summary of the axes before reaching the headline sentence. If that text is meant for screen readers only, it's leaking into the visual render."*
