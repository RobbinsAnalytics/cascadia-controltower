/**
 * Cascadia Control Tower — chart construction.
 *
 * Reads window.CT_DATA, which build_page.py inlines at build time. Nothing here
 * fetches anything: the page is the durable artifact and must render with no
 * network at all.
 *
 * COLOUR ASSIGNMENT (Rule 2.3.1 — fixed slots, never re-dealt)
 *   Alder & Vance (premium banner)  Evergreen
 *   Off-Main (off-price banner)     Glacier
 *   Order fill (certified metric)   Evergreen
 *   Line fill                       Lupine
 *   Unit fill                       Lichen
 *   Counterfactual / alert          Madrona
 *   Context, always directly labelled   Rain
 *
 * Evergreen carries both the premium banner and the certified metric. They
 * never appear in the same chart, every series is directly labelled, and both
 * are the "primary" reading in their own dimension. Recorded here rather than
 * left for a reader to notice.
 */
(function () {
  'use strict';

  var D = window.CT_DATA;
  if (!D || typeof echarts === 'undefined') {
    var n = document.getElementById('chart-fallback');
    if (n) n.hidden = false;
    return;
  }

  var C = CASCADIA.colors;
  var MOTION = CASCADIA.motion();
  var SERIF = CASCADIA.serif;

  /**
   * TEXT INKS — same hue, darkened just enough to clear 4.5:1 as TEXT.
   *
   * Two Cascadia rules collide here and the collision is real. Rule 3.6 puts
   * series identity in a direct label, and Rule 3.3 requires annotation text
   * colour-matched to the series it explains — so series colours end up as
   * text. But the palette is validated for MARKS, where WCAG 1.4.11 asks 3:1.
   * As text at label sizes, WCAG 1.4.3 asks 4.5:1, and measured against Paper:
   *
   *     Evergreen 5.18  pass      Glacier 3.55  FAIL
   *     Lupine    4.61  pass      Lichen  3.92  FAIL
   *                               Madrona 4.31  FAIL
   *
   * Three of five hues fail as label text. The marks keep the full palette hue,
   * which passes its own 3:1 test; only the text darkens, so series identity
   * survives — same hue, more ink — and Rule 5.3's WCAG AA floor holds.
   */
  var INK = {
    evergreen: C.evergreen,   // 5.18:1, unchanged
    lupine:    C.lupine,      // 4.61:1, unchanged
    glacier:   '#4279A7',     // was #4C8BC0 at 3.55:1 -> 4.52:1
    lichen:    '#90701D',     // was #9C7A20 at 3.92:1 -> 4.52:1
    madrona:   '#BA572D',     // was #C05A2E at 4.31:1 -> 4.55:1
    slate:     C.slateMoss    // 5.82:1
  };

  // Rule 4.2 anatomy is three segments separated by ' · ', plus Rule 4.4's
  // fourth. The source names must therefore not contain that separator
  // themselves, or a four-segment strip reads as seven.
  var PROV = {
    source: 'Seeded generator (synthetic); anchors BLS OEWS, Census MRTS, SEC EDGAR',
    asOf: '2026-08-08',
    view: 'unfiltered'
  };

  var charts = [];

  function make(id, option, opts) {
    var el = document.getElementById(id);
    if (!el) return null;
    var ch = echarts.init(el, 'cascadia', { renderer: 'canvas' });
    option.animationDuration = MOTION.duration;
    option.animation = !MOTION.reduced;
    ch.setOption(option);
    charts.push(ch);

    cascadiaAccessible(el, {
      label: opts.ariaLabel,
      summaryId: id + '-summary',
      tableId: opts.tableId
    });
    if (opts.navigator) cascadiaNavigator(el, opts.navigator);
    cascadiaProvenance(el, {
      source: PROV.source, asOf: PROV.asOf,
      flags: opts.flags || 'synthetic operational data; no adjustments',
      view: PROV.view
    });

    // A window resize listener is not enough. A chart initialised while its
    // container has no width — inside a collapsed panel, an embed, a tab that
    // has not been shown, or a viewport that has not composited yet — stays
    // zero-width forever, because no window resize event ever fires to correct
    // it. Observing the container itself is what makes the chart recover.
    // Guarded against the feedback loop where resizing the canvas retriggers
    // the observer.
    // Deferred with setTimeout rather than requestAnimationFrame. rAF is
    // paused whenever the page is not compositing — a background tab, a
    // hidden panel, an offscreen embed — which is exactly the situation this
    // observer exists to recover from, so an rAF-deferred resize can sit
    // pending forever and leave the canvas at its stale width. The size guard
    // above is what prevents the resize from retriggering the observer.
    if (window.ResizeObserver) {
      var lastW = -1, lastH = -1, queued = false;
      new ResizeObserver(function (entries) {
        var r = entries[0].contentRect;
        if (Math.abs(r.width - lastW) < 1 && Math.abs(r.height - lastH) < 1) return;
        lastW = r.width; lastH = r.height;
        if (queued) return;
        queued = true;
        setTimeout(function () { queued = false; ch.resize(); }, 0);
      }).observe(el);
    }
    return ch;
  }

  // Shared axis furniture. Rule 2.4: gridlines are earned, not default.
  function timeAxis(labels) {
    return {
      type: 'category',
      data: labels,
      boundaryGap: false,
      axisLabel: {
        interval: function (i) { return i % 3 === 0; },
        formatter: function (v) { return v.slice(2).replace('-', '‑'); }
      }
    };
  }

  function pctAxis(min, max, gridlines) {
    return {
      type: 'value', min: min, max: max,
      axisLabel: { formatter: function (v) { return v + '%'; } },
      splitLine: { show: !!gridlines, lineStyle: { color: C.mist } }
    };
  }

  function endLabel(color, name) {
    return {
      show: true, formatter: name, color: color, fontFamily: SERIF,
      fontSize: 13, fontWeight: 600, distance: 6,
      textBorderColor: C.paper, textBorderWidth: 3
    };
  }

  var months = D.fills.map(function (r) { return r.year_month; });

  // =======================================================================
  // 1 · The three fill rates
  //     Relationship: change over time. Rule 3.3 exception — a genuine
  //     multi-entity comparison where the title is about the comparison,
  //     so the categorical slots are used in fixed order.
  //     Rule 2.1: the title makes a GAP claim ("points apart"), so a
  //     truncated axis is permitted. A ratio claim would require zero.
  // =======================================================================
  (function () {
    var unit = D.fills.map(function (r) { return +(r.unit_fill * 100).toFixed(2); });
    var line = D.fills.map(function (r) { return +(r.line_fill * 100).toFixed(2); });
    var order = D.fills.map(function (r) { return +(r.order_fill * 100).toFixed(2); });
    var last = months.length - 1;

    make('c-fills', {
      title: cascadiaTitle(D.titles.fills,
        'Unit, line and order fill · monthly · both banners · one dataset'),
      grid: { left: 46, right: 92, top: 92, bottom: 40 },
      xAxis: timeAxis(months),
      yAxis: pctAxis(82, 98, true),
      tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
      series: [
        { name: 'Unit fill', type: 'line', data: unit, color: C.lichen,
          symbol: 'none', lineStyle: { width: 2 },
          endLabel: endLabel(INK.lichen, 'Unit fill') },
        { name: 'Line fill', type: 'line', data: line, color: C.lupine,
          symbol: 'none', lineStyle: { width: 2 },
          endLabel: endLabel(INK.lupine, 'Line fill') },
        { name: 'Order fill', type: 'line', data: order, color: C.evergreen,
          symbol: 'none', lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.evergreen, 'Order fill'),
          markPoint: cascadiaAnnotation(
            'Order fill is always lowest: one short line fails the whole order',
            { coord: [months[Math.floor(last * 0.34)], order[Math.floor(last * 0.34)]],
              color: INK.evergreen, position: 'bottom', width: 210 }) }
      ]
    }, {
      tableId: 'tbl-fills',
      ariaLabel: 'Line chart of three monthly fill rates over 24 months. ' +
        'Unit fill is highest throughout, order fill lowest, line fill between. ' +
        'The three series never cross.',
      navigator: {
        label: 'Three fill rates, monthly, August 2024 to July 2026, percent.',
        series: [
          { name: 'Unit fill', points: pts(months, unit) },
          { name: 'Line fill', points: pts(months, line) },
          { name: 'Order fill', points: pts(months, order) }
        ]
      }
    });
  })();

  // =======================================================================
  // 2 · The counterfactual — splitting is how fill is achieved
  //     Relationship: deviation.
  // =======================================================================
  (function () {
    var actual = D.fills.map(function (r) { return +(r.unit_fill * 100).toFixed(2); });
    var cf = D.fills.map(function (r) { return +(r.cf_unit_fill * 100).toFixed(2); });
    var mid = Math.floor(months.length * 0.55);

    make('c-cf', {
      title: cascadiaTitle(D.titles.counterfactual,
        'Unit fill achieved, against the best any single node could have done · ' +
        'evaluated on the inventory position before each allocation'),
      grid: { left: 46, right: 128, top: 92, bottom: 40 },
      xAxis: timeAxis(months),
      yAxis: pctAxis(88, 97, true),
      tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
      series: [
        { name: 'Unit fill as achieved', type: 'line', data: actual,
          color: C.evergreen, symbol: 'none', lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.evergreen, 'As achieved'),
          markPoint: cascadiaAnnotation(
            'The gap is the fill splitting buys, and the cost it hides',
            { coord: [months[mid], (actual[mid] + cf[mid]) / 2],
              color: INK.madrona, position: 'right', width: 165 }) },
        { name: 'Unit fill if splitting were forbidden', type: 'line', data: cf,
          color: C.madrona, symbol: 'none',
          lineStyle: { width: 2, type: 'dashed' },
          endLabel: endLabel(INK.madrona, 'Single node only') }
      ]
    }, {
      tableId: 'tbl-cf',
      ariaLabel: 'Line chart comparing achieved unit fill against unit fill under a ' +
        'single-node-only rule, monthly over 24 months. The achieved series is above ' +
        'the counterfactual in every month.',
      flags: 'counterfactual is modelled, not measured',
      navigator: {
        label: 'Achieved unit fill against single-node-only unit fill, monthly, percent.',
        series: [
          { name: 'As achieved', points: pts(months, actual) },
          { name: 'Single node only', points: pts(months, cf) }
        ]
      }
    });
  })();

  // =======================================================================
  // 3 · Concentration by velocity band — one cause, two symptoms
  //     Relationship: ranking. Rule 5.1 layer 3 not required: the table
  //     carries a three-row ranking as well as the chart does.
  // =======================================================================
  (function () {
    var bands = D.velocity.map(function (v) {
      return { A: 'A · fast', B: 'B · mid', C: 'C · slow' }[v.velocity_band];
    });
    var partial = D.velocity.map(function (v) { return +v.pct_partial.toFixed(2); });
    var multi = D.velocity.map(function (v) { return +v.pct_multi_node.toFixed(2); });

    make('c-vel', {
      title: cascadiaTitle(D.titles.velocity,
        'Share of order lines · by SKU velocity band · slow movers are ranged at ' +
        'two nodes, fast movers at six'),
      // Rule 5.1 / 2.3: decal is a second, non-colour channel on every
      // categorical chart. The palette does not survive grayscale, so this is
      // load-bearing rather than decorative.
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 52, right: 24, top: 96, bottom: 42 },
      xAxis: { type: 'category', data: bands },
      yAxis: { type: 'value', min: 0, max: 20,
               axisLabel: { formatter: function (v) { return v + '%'; } },
               splitLine: { show: true, lineStyle: { color: C.mist } } },
      tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
      series: [
        { name: 'Ships short', type: 'bar', data: partial, color: C.madrona,
          barGap: '12%',
          label: { show: true, position: 'top', formatter: '{c}%',
                   fontFamily: SERIF, fontSize: 12, color: INK.madrona } },
        { name: 'Uses more than one node', type: 'bar', data: multi, color: C.glacier,
          label: { show: true, position: 'top', formatter: '{c}%',
                   fontFamily: SERIF, fontSize: 12, color: INK.glacier },
          markPoint: cascadiaAnnotation(
            'Both symptoms rise together because both come from thin, fragmented stock',
            { coord: [bands[2], multi[2]], color: INK.glacier,
              position: 'left', width: 175, distance: 18 }) }
      ]
    }, {
      tableId: 'tbl-vel',
      ariaLabel: 'Grouped bar chart. For each of three SKU velocity bands, the share ' +
        'of order lines shipping short and the share using more than one node. Both ' +
        'rise from the fast band to the slow band.'
    });
  })();

  // =======================================================================
  // 4 · Split economics by banner
  //     Relationship: magnitude. Two entities, banner colours fixed.
  // =======================================================================
  (function () {
    var splits = D.economics.filter(function (e) { return e.classification === 'split'; });
    splits.sort(function (a, b) {
      return b.split_premium_pct_of_margin - a.split_premium_pct_of_margin;
    });
    var names = splits.map(function (e) { return e.banner_name; });
    var vals = splits.map(function (e) {
      return +(e.split_premium_pct_of_margin * 100).toFixed(2);
    });
    var colors = splits.map(function (e) {
      return e.banner === 'premium' ? C.evergreen : C.glacier;
    });

    make('c-econ', {
      title: cascadiaTitle(D.titles.economics,
        'Split premium as a share of the gross margin on the same order · ' +
        'split orders only'),
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 58, right: 28, top: 96, bottom: 42 },
      xAxis: { type: 'category', data: names },
      yAxis: { type: 'value', min: 0, max: 15,
               axisLabel: { formatter: function (v) { return v + '%'; } },
               splitLine: { show: true, lineStyle: { color: C.mist } } },
      tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
      series: [{
        type: 'bar', data: vals.map(function (v, i) {
          return { value: v, itemStyle: { color: colors[i] } };
        }),
        barWidth: '46%',
        label: { show: true, position: 'top', formatter: '{c}%',
                 fontFamily: SERIF, fontSize: 15, fontWeight: 600, color: C.basalt },
        markPoint: cascadiaAnnotation(
          'Near-identical dollar cost, very different consequence',
          { coord: [names[0], vals[0]], color: INK.glacier,
            position: 'right', width: 150, distance: 24 })
      }]
    }, {
      tableId: 'tbl-econ',
      ariaLabel: 'Bar chart of split premium as a percent of gross margin, for two ' +
        'banners. The off-price banner is roughly three times the premium banner.'
    });
  })();

  // =======================================================================
  // 5 · The threshold curve — the prescriptive layer
  //     Relationship: change over a policy dial.
  // =======================================================================
  (function () {
    var ts = [], byBanner = {};
    D.threshold.forEach(function (r) {
      if (ts.indexOf(r.threshold_usd) < 0) ts.push(r.threshold_usd);
      (byBanner[r.banner] = byBanner[r.banner] || {})[r.threshold_usd] =
        r.pct_of_split_orders;
    });
    ts.sort(function (a, b) { return a - b; });
    var labels = ts.map(function (t) { return '$' + t; });
    var off = ts.map(function (t) { return +(byBanner.offprice[t] || 0).toFixed(1); });
    var prem = ts.map(function (t) { return +(byBanner.premium[t] || 0).toFixed(1); });
    var i6 = ts.indexOf(6);

    make('c-thr', {
      title: cascadiaTitle(D.titles.threshold,
        'Share of each banner’s split orders whose premium exceeds the threshold'),
      grid: { left: 50, right: 96, top: 96, bottom: 42 },
      xAxis: { type: 'category', data: labels, boundaryGap: false },
      yAxis: { type: 'value', min: 0, max: 100,
               axisLabel: { formatter: function (v) { return v + '%'; } },
               splitLine: { show: true, lineStyle: { color: C.mist } } },
      tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
      series: [
        { name: 'Off-Main', type: 'line', data: off, color: C.glacier,
          symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.glacier, 'Off-Main'),
          markPoint: i6 >= 0 ? cascadiaAnnotation(
            'At $6 the same rule catches most of one banner and little of the other',
            { coord: [labels[i6], off[i6]], color: INK.glacier,
              position: 'top', width: 195 }) : undefined },
        { name: 'Alder & Vance', type: 'line', data: prem, color: C.evergreen,
          symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.evergreen, 'Alder & Vance') }
      ]
    }, {
      tableId: 'tbl-thr',
      ariaLabel: 'Line chart. Percent of each banner’s split orders whose premium ' +
        'exceeds a cost threshold, for thresholds from four to twenty dollars. Both ' +
        'series fall as the threshold rises, at different rates.'
    });
  })();

  // =======================================================================
  // 6 · Inventory position against the real Census band
  //     Relationship: change over time, against a reference range.
  // =======================================================================
  (function () {
    var labels = D.inventory.map(function (r) { return r.year_month; });
    var ratio = D.inventory.map(function (r) {
      return +r.inventory_sales_ratio.toFixed(3);
    });
    var lo = D.censusBand[0], hi = D.censusBand[1];
    var dec = labels.indexOf('2025-12');

    make('c-inv', {
      title: cascadiaTitle(D.titles.inventory,
        'Months of sales held in inventory · inventory at cost over sales at retail, ' +
        'the Census convention · shaded band is the real department-store range'),
      grid: { left: 50, right: 116, top: 100, bottom: 40 },
      xAxis: timeAxis(labels),
      yAxis: { type: 'value', min: 0, max: 4,
               axisLabel: { formatter: function (v) { return v.toFixed(1); } },
               splitLine: { show: true, lineStyle: { color: C.mist } } },
      tooltip: { trigger: 'axis' },
      series: [{
        name: 'This network', type: 'line', data: ratio, color: C.evergreen,
        symbol: 'none', lineStyle: { width: 2.5 },
        endLabel: endLabel(INK.evergreen, 'This network'),
        // Rule 2.3.6 exception: Rain sits below 3:1, so the band carries a
        // direct text label rather than relying on colour.
        markArea: {
          silent: true,
          itemStyle: { color: 'rgba(154, 166, 160, 0.30)' },
          label: {
            show: true, position: 'insideTop',
            formatter: 'US department stores, 2015–2026: ' +
                       lo.toFixed(2) + '–' + hi.toFixed(2) + ' months',
            color: C.slateMoss, fontFamily: SERIF, fontSize: 12
          },
          data: [[{ yAxis: lo }, { yAxis: hi }]]
        },
        markPoint: dec >= 0 ? cascadiaAnnotation(
          'Peak-season sales pull the ratio down, exactly as the real series does',
          { coord: [labels[dec], ratio[dec]], color: INK.evergreen,
            position: 'bottom', width: 190 }) : undefined
      }]
    }, {
      tableId: 'tbl-inv',
      ariaLabel: 'Line chart of monthly inventory-to-sales ratio for the modelled ' +
        'network, against a shaded band showing the real US department-store range ' +
        'of 2.03 to 3.64 months. The network series runs below the band throughout ' +
        'and dips each November and December.',
      flags: 'sector band excludes the March–May 2020 store closures',
      navigator: {
        label: 'Monthly inventory to sales ratio, months, against the department-store band.',
        series: [{ name: 'This network', points: pts(labels, ratio) }]
      }
    });
  })();

  // =======================================================================
  // 7 · Where units ship from
  //     Relationship: ranking. Rule 3.3 — one emphasis, context in Rain
  //     WITH direct labels.
  // =======================================================================
  (function () {
    var ns = D.nodes.slice().sort(function (a, b) {
      return b.cost_per_unit - a.cost_per_unit;
    });
    var names = ns.map(function (n) { return n.node_name; });
    var cpu = ns.map(function (n) { return +n.cost_per_unit.toFixed(2); });
    var isStore = ns.map(function (n) { return n.node_kind === 'STORE'; });

    make('c-nodes', {
      title: cascadiaTitle(D.titles.nodes,
        'Parcel cost per unit shipped · 24 months · ordered most to least expensive'),
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 58, right: 28, top: 96, bottom: 66 },
      xAxis: { type: 'category', data: names,
               axisLabel: { interval: 0, fontSize: 12, width: 84, overflow: 'break' } },
      yAxis: { type: 'value', min: 0,
               axisLabel: { formatter: function (v) { return '$' + v.toFixed(2); } },
               splitLine: { show: true, lineStyle: { color: C.mist } } },
      tooltip: { trigger: 'axis',
                 valueFormatter: function (v) { return '$' + v.toFixed(2); } },
      series: [{
        type: 'bar',
        data: cpu.map(function (v, i) {
          return { value: v, itemStyle: { color: isStore[i] ? C.madrona : C.rain } };
        }),
        barWidth: '58%',
        label: { show: true, position: 'top', formatter: function (p) {
          return '$' + p.value.toFixed(2); },
          fontFamily: SERIF, fontSize: 12, color: C.basalt },
        markPoint: cascadiaAnnotation(
          'Stores are the expensive last resort that rescues an order',
          { coord: [names[0], cpu[0]], color: INK.madrona,
            position: 'right', width: 160, distance: 20 })
      }]
    }, {
      tableId: 'tbl-nodes',
      ariaLabel: 'Bar chart of parcel cost per unit for six fulfilment nodes, ordered ' +
        'most to least expensive. The four store nodes are the most expensive; the two ' +
        'fulfilment centres are the least.'
    });
  })();

  // ---- shared -----------------------------------------------------------

  function pts(labels, values) {
    return labels.map(function (l, i) {
      return { label: l, value: values[i], dataIndex: i };
    });
  }

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      charts.forEach(function (c) { c.resize(); });
    }, 120);
  });
})();
