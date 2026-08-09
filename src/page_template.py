"""
page_template.py — the HTML shell for the Control Tower page.

Kept apart from build_page.py so the template carries no literal braces and
cannot collide with str.format. All CSS and chart code live in docs/assets/.
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cascadia Control Tower — three fill rates, one dataset, and the cost hiding between them</title>
<meta name="description" content="A distribution-centre governance module: order, line and unit fill computed from one dataset, why they disagree, and the split-shipment cost that none of them measures. Synthetic operations, three real public anchors.">
<link rel="stylesheet" href="assets/cascadia-controltower.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<div class="wrap">

<header class="site-head">
  <p class="kicker">Cascadia Portfolio · Module 07 · Distribution-centre governance</p>
  <h1>Three fill rates, one dataset, and the cost hiding between them</h1>
  <p class="standfirst">A distribution centre reports 94% to Operations, 92% to the
  merchant team and 87% to Finance. All three are arithmetically correct. The thing
  actually costing money is invisible in all three.</p>
  <p class="asof">Frozen snapshot · <strong>{as_of}</strong> · seed {seed}</p>
</header>

<div class="disclosure-banner">
  <strong>Everything operational in this module was invented by a seeded generator.</strong>
  Every order, style, size, shipment, labor hour and dollar below is synthetic.
  <strong>Alder &amp; Vance</strong> and <strong>Off-Main</strong> are invented banners
  and no real company is the subject of this analysis. It demonstrates a design; it
  measures nothing real. Three real public datasets — BLS wage data, Census retail
  inventories and the SEC filings of Macy&rsquo;s, Kohl&rsquo;s and Dillard&rsquo;s —
  constrain what the generator is allowed to produce, and are named wherever they are used.
</div>

<main id="main">

<section id="overview">
  <h2>The operation</h2>
  <p class="section-note">A single fulfilment centre serving two banners inside a
  six-node network that also ships from a second FC and four stores. Twenty-four
  months, August 2024 to July 2026.</p>

  <div class="kpi-grid">
    <div class="kpi exploratory">
      <p class="label">Unit fill <span class="tier-tag exploratory">exploratory</span></p>
      <p class="value">{unit_fill}</p>
      <p class="foot">What Operations reads. Units shipped over units ordered.</p>
    </div>
    <div class="kpi exploratory">
      <p class="label">Line fill <span class="tier-tag exploratory">exploratory</span></p>
      <p class="value">{line_fill}</p>
      <p class="foot">What the merchant team reads. Lines shipped complete.</p>
    </div>
    <div class="kpi certified">
      <p class="label">Order fill <span class="tier-tag certified">certified</span></p>
      <p class="value">{order_fill}</p>
      <p class="foot">What Finance reads, and the one the business now runs on.</p>
    </div>
    <div class="kpi certified">
      <p class="label">Split rate <span class="tier-tag certified">certified</span></p>
      <p class="value">{split_rate}</p>
      <p class="foot">Orders shipped from more than one node. Counted by node, not parcel.</p>
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <p class="label">Orders</p>
      <p class="value">{orders}</p>
      <p class="foot">{lines} order lines · {not_shipped} shipped nothing at all</p>
    </div>
    <div class="kpi">
      <p class="label">Shipped sales</p>
      <p class="value">{sales}</p>
      <p class="foot">At retail, over 24 months</p>
    </div>
    <div class="kpi">
      <p class="label">Split premium</p>
      <p class="value">{split_premium}</p>
      <p class="foot">{split_pct_parcel} of all parcel spend — the leak</p>
    </div>
    <div class="kpi">
      <p class="label">Cost per shipped order</p>
      <p class="value">{cost_per_order}</p>
      <p class="foot">Parcel plus labor at real BLS Seattle wages</p>
    </div>
  </div>
</section>

<section id="thesis">
  <h2>The thesis</h2>
  <div class="thesis">
    <p>A distribution centre reports <strong>{unit_fill}</strong> fill to Operations,
    <strong>{line_fill}</strong> to the merchant team and <strong>{order_fill}</strong>
    to Finance. Three numbers, three teams, all arithmetically correct, none reconciled —
    because <em>order fill</em>, <em>line fill</em> and <em>unit fill</em> are different
    metrics and nobody ever wrote down which one the business runs on.</p>

    <p>Meanwhile the thing actually costing money is invisible in all three.
    <strong>An order split across two nodes still counts as filled.</strong> It is 100%
    filled, on time, in full — and it costs {off_premium} more to ship in the off-price
    banner and {prem_premium} more in the premium one.</p>

    <p>The definitional gap and the economic leak are the same phenomenon.
    <strong>Fill rate looks healthiest exactly where splitting is worst</strong>, because
    splitting is <em>how</em> the network achieves fill. The metric meant to measure
    service is concealing the cost of delivering it.</p>
  </div>
  <p>The supply-chain discipline has not settled this. Fill rate resolves at least three
  ways, and published guidance states plainly that there is no agreed OTIF formula
  because the calculation depends on which point of view you are measuring and the level
  at which the data is stored. This module is not inventing a strawman; it is naming a
  documented condition of the field and then resolving it for one operation.</p>
</section>

<section id="register">
  <h2>The certified metric register</h2>
  <p class="section-note">Generated from the <code>meta</code> blocks on the dbt models
  that compute these metrics — the same file that defines their tests. Nothing here is
  typed twice, and <code>build_metric_register.py --check</code> fails the build if a
  definition drifts from the model behind it.</p>

  <p><strong>Certification is not a ranking.</strong> An exploratory metric is not a bad
  metric; it is one the business has agreed not to run on. Retaining the other two
  definitions and labelling them <em>is</em> the governance act — deleting them would
  move the disagreement rather than resolve it.</p>

  <div class="table-scroll">
    <table class="register-table">
      <caption>Eleven metrics. Order fill is certified as the service number; line and
      unit fill are retained as diagnostics with the reason stated.</caption>
      <thead><tr>
        <th scope="col">Metric</th><th scope="col">Tier</th><th scope="col">Grain</th>
        <th scope="col">Owner</th><th scope="col">Why this tier</th>
      </tr></thead>
      <tbody>{register_rows}</tbody>
    </table>
  </div>

  <h3>The pathology this replaced</h3>
  <p>Before certification there were three fill rates in circulation and no statement of
  which one the business ran on. Each was defensible to the team that built it: Operations
  measured what physically moved, merchandising measured assortment coverage, Finance
  measured whether the customer got what they asked for.</p>
  <p>The cost was not licences or dashboards. It was that <strong>the three teams could
  not have the same conversation about the same week.</strong> Operations reported service
  improving while Finance reported it flat, both were arithmetically correct, the meeting
  resolved nothing — and the split rate, which none of the three measured, went
  unexamined for the entire period.</p>
</section>

<section id="analysis">
  <h2>What the data shows</h2>
  <p class="section-note">Descriptive, then diagnostic, then prescriptive. Every chart
  carries its own data table and its own provenance.</p>

  <h3>Descriptive — the three rates never meet</h3>
  {chart_fills}

  <p>The gap is {gap_pts} points between the most forgiving definition and the strictest.
  It is not measurement error and it is not a reconciliation problem: each rate is a
  different question asked of the same shipped quantities. Order fill is arithmetically
  the lowest of the three in every period, because an order counts as filled only if
  every line in it is.</p>

  <h3>Diagnostic — splitting is how the network achieves fill</h3>
  {chart_cf}

  <p>For every order, the simulation also records what the <em>same order against the
  same inventory position</em> would have shipped if splitting were forbidden — the best
  any single node could have done alone, evaluated before the real allocation was
  committed. Splitting buys <strong>{cf_delta} points of unit fill</strong>. Without that
  counterfactual, &ldquo;splitting is how the network achieves fill&rdquo; is an
  assertion; with it, the governance decision has a price.</p>

  {chart_vel}

  <p>Shortfall and splitting are not two problems. They are two symptoms of one
  condition: inventory fragmented relative to what customers actually put in a basket.
  Slow-moving styles are ranged at two nodes rather than six, so a basket containing one
  either reaches for a second node or goes short — and which of those happens is a matter
  of luck, not of policy.</p>

  <h3>The second finding — the same rule, two different economics</h3>
  {chart_econ}

  <p>The dollar cost of a split barely differs between the banners. Its consequence
  differs by more than three times, because it is charged against a margin that differs by
  more than three times. A split that is a rounding error on a premium order is a material
  loss on an off-price one.</p>
  <p><strong>There is therefore no single correct split threshold.</strong> That is a
  governance finding, not a modelling inconvenience: any single network-wide rule is
  simultaneously too aggressive for one banner and too permissive for the other.</p>

  <h3>Prescriptive — priced, with the residual reported as a residual</h3>
  {chart_thr}

  <p><strong>The recommendation: set the threshold per banner, not per network.</strong>
  Holding Off-Main splits above {rec_threshold} as exceptions would catch
  {rec_orders} orders carrying {rec_premium} of split premium. Applying the same rule to
  Alder &amp; Vance would catch {rec_prem_orders} orders and save {rec_prem_premium},
  while risking margin that comfortably absorbs the cost.</p>

  <p>The saving is not free and the page will not pretend otherwise. Those orders shipped
  complete <em>because</em> they were split. Holding them puts
  <strong>{rec_units_at_risk} units at risk</strong> of shipping short, which would move
  the certified metric — order fill — in the wrong direction. The decision is a trade
  between a measured cost and a measured service loss, and the register now shows both
  next to each other, which it could not do before.</p>

  <p><strong>The residual, stated as a residual.</strong> A per-banner threshold at
  {rec_threshold} addresses {rec_addressed} of the {split_premium} total split premium.
  <strong>{rec_residual} remains</strong>, in splits too small individually to hold but
  numerous enough to matter in aggregate. Nothing in this analysis explains that portion
  away, and no allocation rule tested here removes it. It is reported rather than
  absorbed into the recommendation.</p>

  <h3>Where the cost actually lands</h3>
  {chart_nodes}
</section>

<section id="plausible">
  <h2>Is this world plausible?</h2>
  <p class="section-note">The operational data is invented, so the question a sceptical
  reader should ask is whether the generator produced a world a real department store
  would recognise. Three audits check it against real published data, and each one is
  written so that it can fail.</p>

  {chart_inv}

  <p>The modelled network runs at <strong>{inv_mean} months</strong> of stock against a
  real department-store band of {band_lo}&ndash;{band_hi}. <strong>Sitting below the band
  is the correct answer, not a miss.</strong> The Census series covers entire department
  stores, most of whose inventory sits on selling floors serving walk-in customers this
  module never simulates. So the audit asks for the relationship rather than the level:
  the series must sit strictly inside the sector figure, clear a floor below which the
  modelled service level would be unattainable, and <em>move with</em> the real series
  seasonally. It correlates at +0.62 and dips every November and December, exactly as
  department stores do when peak-season sales outrun the inventory behind them.</p>

  <p>The second audit bounds this DC&rsquo;s operating cost at <strong>{dc_cost_pct}</strong>
  of shipped sales against the {sga_lo}&ndash;{sga_hi} SG&amp;A range Macy&rsquo;s,
  Kohl&rsquo;s and Dillard&rsquo;s actually report. The third requires splitting to be
  concentrated and directional rather than uniform noise — which is the pattern shown
  above, and which a generator producing random splits would fail.</p>

  <p><strong>An audit that cannot fail is not an audit.</strong> Each one is a pure
  function of measured numbers, so the validation suite hands each deliberately wrong
  values and confirms it trips: inventory inflated past the sector band, seasonality
  flattened, cost inflated past peer SG&amp;A, cost cut to a rounding error, splits made
  uniform, and concentration reversed. All six trip, and that result is recorded next to
  the real one in the validation report.</p>
</section>

<section id="method">
  <h2>Data &amp; method</h2>
  <div class="method">
    <h3>Whose decision this serves</h3>
    <ul>
      <li><strong>The decision.</strong> Whether to certify one fill definition, and
      where to set the split-cost threshold for each banner.</li>
      <li><strong>The reader.</strong> A fulfilment leader and a finance partner, both
      analytics-literate, on a tactical-to-strategic horizon.</li>
      <li><strong>The benchmark.</strong> Real peer filings and a real federal inventory
      series for plausibility; an internal counterfactual for the service trade.</li>
      <li><strong>The action.</strong> Certify order fill; set two thresholds instead of
      one; put split rate on the same register as fill rate.</li>
      <li><strong>Refresh.</strong> None. This is a frozen snapshot and says so.</li>
    </ul>

    <h3>The synthetic spine</h3>
    <ul>
      <li>A seeded Python generator, seed <code>{seed}</code>. The same seed produces
      the same content hash, <code>{content_hash}</code>, which the validation suite
      re-checks on every run.</li>
      <li>Inventory is held per <strong>style and size</strong>. That is what lets the
      three fill rates differ at all: a line for three units spreads across the size run,
      so it commonly ships two of three rather than all or nothing. Size brokenness is
      the commonest reason a real retail line ships incomplete.</li>
      <li><strong>No order is ever labelled &ldquo;split.&rdquo;</strong> An order splits
      when the allocator cannot satisfy every line from one node and reaches for a second.
      The classification is an observed consequence of the documented allocation rule, and
      <code>validate.py</code> re-derives it from the shipments alone.</li>
    </ul>

    <h3>The three real anchors</h3>
    <ul>
      <li><strong>Labor · BLS Occupational Employment and Wage Statistics</strong>,
      May 2025, Seattle-Tacoma-Bellevue metro (area 42660). Every labor dollar on this
      page is costed at a real published wage across the percentile spread, not a median
      alone:
      <ul>{labor_rows}</ul>
      Total labor: {labor_cost} across {labor_hours} hours.</li>

      <li><strong>Inventory · US Census Monthly Retail Trade Survey</strong>,
      department stores, end-of-month inventories and inventories/sales ratios,
      1992&ndash;2026. The modelled network runs at <strong>{inv_mean} months</strong>
      against a sector band of {band_lo}&ndash;{band_hi}.</li>

      <li><strong>P&amp;L plausibility · SEC EDGAR XBRL</strong> for
      <strong>Macy&rsquo;s, Kohl&rsquo;s and Dillard&rsquo;s</strong>. Their SG&amp;A runs
      {sga_lo}&ndash;{sga_hi} of revenue; this DC runs at <strong>{dc_cost_pct}</strong>
      of shipped sales.</li>
    </ul>

    <h3>Pull once, freeze, commit</h3>
    <ul>
      <li>All three anchors are frozen in the repository with a SHA-256 per file.
      <strong>No build step and no part of this page makes a network call.</strong>
      ECharts and the chart theme are vendored; the dataset is inlined at build time.</li>
      <li>XBRL tags drift in two directions and both are handled. Dillard&rsquo;s reports
      inventory as <code>RetailRelatedInventoryMerchandise</code> where the others use
      <code>InventoryNet</code>, and all three moved revenue and cost of sales onto
      different tags mid-history. Every winning tag is recorded in
      <code>governance/tag_mapping.csv</code>.</li>
    </ul>

    <h3>The stack, described accurately</h3>
    <ul>
      <li>Python generator → DuckDB star schema → <strong>dbt Core</strong> (6 staging
      views, 9 marts, <strong>69 data tests</strong>) → this static page, with Apache
      ECharts vendored.</li>
      <li><strong>The warehouse layer shipped as DuckDB.</strong> BigQuery and Looker
      Studio are a named, gated Phase&nbsp;2 awaiting a cloud project; when it exists,
      BigQuery becomes a second output in the dbt profile and the models do not change.
      Nothing on this page was produced by BigQuery or by Looker Studio, and where that
      phase is discussed it means <em>Looker Studio</em>, not Looker or LookML.</li>
      <li>The static page is the durable artifact and survives the warehouse being
      switched off. That is the reason it exists.</li>
    </ul>
  </div>
</section>

<section id="limits">
  <h2>Honest limits</h2>
  <div class="limits">
    <ul>
      <li><strong>The operational data is invented, and the generator is not evidence
      about the world.</strong> It demonstrates a design. Every fill rate, split rate and
      dollar on this page describes a simulation.</li>

      <li><strong>Two of the three realism audits bound the model rather than matching
      it, and the reason is scope.</strong> Census inventories cover entire department
      stores, most of whose stock sits on selling floors serving walk-in customers this
      module never simulates — so the network holding {inv_mean} months against a sector
      band of {band_lo}&ndash;{band_hi} is correct, not a miss. Audit A requires the
      series to sit strictly inside the sector figure, clear a floor, and move with it
      seasonally. It does all three, and that is a weaker claim than a match.</li>

      <li><strong>Fulfilment cost is not separately disclosed by any public department
      store.</strong> It sits inside SG&amp;A alongside stores, marketing, occupancy and
      corporate. Audit B therefore bounds the modelled DC cost by the peer SG&amp;A band
      rather than matching a reported figure. No amount of care makes an undisclosed
      number checkable.</li>

      <li><strong>The counterfactual is modelled, not measured.</strong> It is the best
      any single node could have done against the same inventory position — a defensible
      alternative history, but an alternative history. It is registered as exploratory
      and must never be reported as achieved service.</li>

      <li><strong>The calibration source is not named, and that costs reproducibility.</strong>
      Scale and mix parameters draw on one real department-store operator&rsquo;s published
      filings. That filer is never named here, so this one input is <em>attested rather
      than reproducible</em>. The three realism audits deliberately do not depend on it —
      they run against the Census series and the three named peers, which are frozen and
      committed in full.</li>

      <li><strong>Returns and reverse logistics are excluded on purpose.</strong> They are
      the largest documented cost in the research — industry sources put US retail returns
      around $850&nbsp;billion, roughly 16% of sales, with apparel return rates of 30&ndash;46%
      and reverse-logistics handling at $20&ndash;30 per return. Including them would double
      the build. They are the natural Phase&nbsp;2, named rather than quietly omitted.</li>

      <li><strong>Also excluded:</strong> labor scheduling optimisation and network design,
      which are optimisation problems rather than governance problems; and store-level and
      merchandising analytics, which would take the module off the DC.</li>

      <li><strong>A target was missed and is reported missed.</strong> The generator aimed
      for a three-point gap between unit fill and line fill and produced
      {gap_unit_line} points. Reaching three would have required roughly one line in ten
      to ship partially, which is high for an operation with working replenishment.
      Forcing it would have meant choosing an implausible world to make a headline land,
      which is the failure this module exists to criticise.</li>

      <li><strong>Definition-of-done item 6 is unmet.</strong> There is no live BigQuery
      or Looker Studio view, because there is no cloud project yet. Said plainly rather
      than implied by omission.</li>
    </ul>
  </div>
</section>

</main>

<p class="fallback-note" id="chart-fallback" hidden>Charts could not be rendered in this
browser. Every chart&rsquo;s underlying data is available in full in the tables above.</p>

<footer class="footer">
  <p><strong>Cascadia Control Tower</strong> · Aaron Robbins · Robbins Analytics ·
  frozen {as_of}. Synthetic operational data for an invented two-banner operation.
  Macy&rsquo;s, Kohl&rsquo;s and Dillard&rsquo;s are named because they are the real
  benchmark set; naming a benchmark is not naming a subject. Built to the Cascadia
  visualization standard v2.2 — every chart title states a finding, every chart carries
  a real data table, WCAG 2.2 AA throughout.</p>
</footer>

</div>

<script src="assets/echarts.min.js"></script>
<script src="assets/cascadia-echarts-theme.js"></script>
<script>window.CT_DATA = {payload};</script>
<script src="assets/controltower-charts.js"></script>
</body>
</html>
"""
