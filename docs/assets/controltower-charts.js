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
 * are the "primary" reading in their own dimension.
 *
 * THREE LAYOUT RULES LEARNED FROM LOOKING AT THE RENDERED CHARTS
 *
 * 1. Axis bounds come from the data (CT_DATA.axes), never typed. Hard-coded
 *    bounds clipped real values off the bottom of two charts.
 * 2. Titles wrap. ECharts does not wrap a title by default, it CLIPS it, so
 *    the width is set from the container on every render and the plot is
 *    pushed down by the number of lines the title actually takes.
 * 3. Annotations sit in reserved empty space, never over a mark. The
 *    annotation helper paints a paper-coloured outline around its glyphs for
 *    legibility, which quietly erases whatever is underneath — over a bar it
 *    eats the bar and its value label. Each axis therefore carries headroom
 *    above the data, and that is where annotations live.
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
  var AX = D.axes;

  /**
   * TEXT INKS — same hue, darkened just enough to clear 4.5:1 as TEXT.
   *
   * Rule 3.6 puts series identity in a direct label and Rule 3.3 colour-matches
   * annotation text to its series, so palette hues end up as text. The palette
   * is validated for MARKS at 3:1; as text, 4.5:1 applies. Measured on Paper:
   * Evergreen 5.18 and Lupine 4.61 pass; Glacier 3.55, Lichen 3.92 and Madrona
   * 4.31 fail. Marks keep the full hue; only text darkens.
   */
  var INK = {
    evergreen: C.evergreen,
    lupine:    C.lupine,
    glacier:   '#4279A7',
    lichen:    '#90701D',
    madrona:   '#BA572D',
    slate:     C.slateMoss
  };

  // Rule 4.2's anatomy is three ' · '-separated segments plus Rule 4.4's
  // fourth, so the source names must not contain that separator themselves.
  var PROV = {
    source: 'Seeded generator (synthetic); anchors BLS OEWS, Census MRTS, SEC EDGAR',
    asOf: '2026-08-08',
    view: 'unfiltered'
  };

  var charts = [];

  /** Wrap the title to the container and push the plot below it. */
  function fitTitle(ch, el, titleText, subtitleText, extraTop) {
    var w = Math.max(240, el.clientWidth - 24);
    // Source Serif at 18px averages a shade over half the font size per glyph.
    var lines = Math.max(1, Math.ceil(titleText.length * 9.6 / w));
    var subLines = Math.max(1, Math.ceil((subtitleText || '').length * 6.6 / w));
    var top = 26 * lines + 17 * subLines + 30 + (extraTop || 0);
    ch.setOption({
      title: { textStyle: { width: w, overflow: 'break' },
               subtextStyle: { width: w, overflow: 'break' } },
      grid: { top: top }
    });
  }

  function make(id, option, opts) {
    var el = document.getElementById(id);
    if (!el) return null;
    var ch = echarts.init(el, 'cascadia', { renderer: 'canvas' });
    option.animationDuration = MOTION.duration;
    option.animation = !MOTION.reduced;
    ch.setOption(option);
    fitTitle(ch, el, option.title.text, option.title.subtext, opts.extraTop);
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

    // A window resize listener is not enough: a container that changes size on
    // its own — a collapsed panel, an embed, a viewport that has not composited
    // — fires no window event, and the canvas stays at its stale width forever.
    // Deferred with setTimeout rather than requestAnimationFrame because rAF is
    // paused while the page is not compositing, which is precisely the case
    // this observer exists to recover from.
    if (window.ResizeObserver) {
      var lastW = -1, lastH = -1, queued = false;
      new ResizeObserver(function (entries) {
        var r = entries[0].contentRect;
        if (Math.abs(r.width - lastW) < 1 && Math.abs(r.height - lastH) < 1) return;
        lastW = r.width; lastH = r.height;
        if (queued) return;
        queued = true;
        setTimeout(function () {
          queued = false;
          ch.resize();
          fitTitle(ch, el, option.title.text, option.title.subtext, opts.extraTop);
        }, 0);
      }).observe(el);
    }
    return ch;
  }

  function timeAxis(labels) {
    return {
      type: 'category', data: labels, boundaryGap: false,
      axisLabel: {
        interval: function (i) { return i % 3 === 0; },
        formatter: function (v) {
          var p = v.split('-');
          return p[1] + '/' + p[0].slice(2);
        }
      }
    };
  }

  function valueAxis(range, fmt) {
    return {
      type: 'value', min: range[0], max: range[1],
      axisLabel: { formatter: fmt },
      splitLine: { show: true, lineStyle: { color: C.mist } }
    };
  }

  var asPct = function (v) { return v + '%'; };

  function endLabel(color, name) {
    return {
      show: true, formatter: name, color: color, fontFamily: SERIF,
      fontSize: 13, fontWeight: 600, distance: 6,
      textBorderColor: C.paper, textBorderWidth: 3
    };
  }

  function pts(labels, values) {
    return labels.map(function (l, i) {
      return { label: l, value: values[i], dataIndex: i };
    });
  }

  var months = D.fills.map(function (r) { return r.year_month; });

  // =======================================================================
  // 1 · The three fill rates · change over time
  //     Rule 3.3 exception: a genuine multi-entity comparison whose title is
  //     about the comparison, so the categorical slots are used in order.
  //     Rule 2.1: the title makes a GAP claim, so truncation is permitted —
  //     but the axis still contains every plotted value.
  // =======================================================================
  (function () {
    var unit = D.fills.map(function (r) { return +(r.unit_fill * 100).toFixed(2); });
    var line = D.fills.map(function (r) { return +(r.line_fill * 100).toFixed(2); });
    var order = D.fills.map(function (r) { return +(r.order_fill * 100).toFixed(2); });

    make('c-fills', {
      title: cascadiaTitle(D.titles.fills,
        'Unit, line and order fill · monthly · both banners · one dataset'),
      grid: { left: 52, right: 96, bottom: 40 },
      xAxis: timeAxis(months),
      yAxis: valueAxis(AX.fills, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
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
          // Placed in the empty band below every series, not over one.
          markPoint: cascadiaAnnotation(
            'Order fill is always lowest: one short line fails the whole order',
            { coord: [months[8], AX.fills[0] + 1.6], color: INK.evergreen,
              position: 'top', width: 250 }) }
      ]
    }, {
      tableId: 'tbl-fills',
      ariaLabel: 'Line chart of three monthly fill rates over 24 months. Unit fill ' +
        'is highest throughout, order fill lowest, line fill between. The three ' +
        'series never cross, and all three fall sharply each November.',
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
  // 2 · The counterfactual · deviation
  // =======================================================================
  (function () {
    var actual = D.fills.map(function (r) { return +(r.unit_fill * 100).toFixed(2); });
    var cf = D.fills.map(function (r) { return +(r.cf_unit_fill * 100).toFixed(2); });

    make('c-cf', {
      title: cascadiaTitle(D.titles.counterfactual,
        'Unit fill achieved, against the best any single node could have done · ' +
        'evaluated on the inventory position before each allocation'),
      grid: { left: 52, right: 132, bottom: 40 },
      xAxis: timeAxis(months),
      yAxis: valueAxis(AX.cf, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [
        { name: 'Unit fill as achieved', type: 'line', data: actual,
          color: C.evergreen, symbol: 'none', lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.evergreen, 'As achieved'),
          markPoint: cascadiaAnnotation(
            'The gap is the fill splitting buys, and the cost it hides',
            { coord: [months[8], AX.cf[0] + 1.4], color: INK.madrona,
              position: 'top', width: 230 }) },
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
  // 3 · Concentration by velocity band · ranking
  //     Layer 3 keyboard navigation is not required: a three-row ranking is
  //     carried by the table exactly as well as by the chart.
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
      // Decal is a second, non-colour channel. The palette does not survive a
      // luminance-only reduction, so this is load-bearing.
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 56, right: 24, bottom: 42 },
      xAxis: { type: 'category', data: bands },
      yAxis: valueAxis(AX.velocity, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [
        // Rule 3.6 — no legend, so each series names itself directly. The two
        // names are put on DIFFERENT groups: labelled on the same group they
        // are centred on adjacent bars and overlap into an unreadable smear,
        // which is how the previous render shipped.
        { name: 'Ships short', type: 'bar', data: partial, color: C.madrona,
          barGap: '12%',
          label: { show: true, position: 'top',
                   formatter: function (p) {
                     return p.dataIndex === 0
                       ? 'Ships short\n' + p.value + '%' : p.value + '%'; },
                   lineHeight: 15, fontFamily: SERIF, fontSize: 12,
                   fontWeight: 600, color: INK.madrona } },
        { name: 'Uses more than one node', type: 'bar', data: multi, color: C.glacier,
          label: { show: true, position: 'top',
                   formatter: function (p) {
                     return p.dataIndex === 1
                       ? 'Uses two nodes\n' + p.value + '%' : p.value + '%'; },
                   lineHeight: 15, fontFamily: SERIF, fontSize: 12,
                   fontWeight: 600, color: INK.glacier },
          // In the headroom above the tallest bar, not on it.
          markPoint: cascadiaAnnotation(
            'Both symptoms rise together: one cause, thin fragmented stock',
            { coord: [bands[1], AX.velocity[1] - 1.4], color: INK.glacier,
              position: 'top', width: 260 }) }
      ]
    }, {
      tableId: 'tbl-vel',
      ariaLabel: 'Grouped bar chart. For each of three SKU velocity bands, the share ' +
        'of order lines shipping short and the share using more than one node. Both ' +
        'rise from the fast band to the slow band.'
    });
  })();

  // =======================================================================
  // 4 · Split economics by banner · magnitude
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
      grid: { left: 60, right: 28, bottom: 42 },
      xAxis: { type: 'category', data: names },
      yAxis: valueAxis(AX.economics, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [{
        type: 'bar', barWidth: '42%',
        data: vals.map(function (v, i) {
          return { value: v, itemStyle: { color: colors[i] } };
        }),
        label: { show: true, position: 'top', formatter: '{c}%',
                 fontFamily: SERIF, fontSize: 15, fontWeight: 600, color: C.basalt },
        markPoint: cascadiaAnnotation(
          'Near-identical dollar cost, very different consequence',
          { coord: [names[1], AX.economics[1] - 1.2], color: INK.glacier,
            position: 'top', width: 230 })
      }]
    }, {
      tableId: 'tbl-econ',
      ariaLabel: 'Bar chart of split premium as a percent of gross margin, for two ' +
        'banners. The off-price banner is roughly three times the premium banner.'
    });
  })();

  // =======================================================================
  // 5 · The threshold curve · the prescriptive layer
  //
  //     The $4 point is dropped from the PLOT. Every split pays at least one
  //     extra parcel base rate, so both banners sit at exactly 100% there —
  //     a degenerate point that forced a 0-100 axis and squashed the entire
  //     informative range into the bottom fifth of the frame. It stays in the
  //     data table and in validate.py's monotonicity check, and the subtitle
  //     says why it is not drawn.
  //
  //     Direct labels sit at the point of MAXIMUM separation rather than at
  //     the line ends, because the two series converge to under one percent
  //     and end labels collided into an unreadable overlap.
  // =======================================================================
  (function () {
    var ts = [], byBanner = {};
    D.threshold.forEach(function (r) {
      if (r.threshold_usd <= 4) return;
      if (ts.indexOf(r.threshold_usd) < 0) ts.push(r.threshold_usd);
      (byBanner[r.banner] = byBanner[r.banner] || {})[r.threshold_usd] =
        r.pct_of_split_orders;
    });
    ts.sort(function (a, b) { return a - b; });
    var labels = ts.map(function (t) { return '$' + t; });
    var off = ts.map(function (t) { return +(byBanner.offprice[t] || 0).toFixed(1); });
    var prem = ts.map(function (t) { return +(byBanner.premium[t] || 0).toFixed(1); });

    // Widest vertical gap, searched over INTERIOR points only. A label centred
    // on the first or last point overflows the grid edge and is silently
    // clipped — which is how this chart ended up with no series identity at
    // all on its first render: no legend by design, and both direct labels
    // sitting just outside the plot.
    var gi = 1, best = -1;
    for (var i = 1; i < off.length - 1; i++) {
      if (off[i] - prem[i] > best) { best = off[i] - prem[i]; gi = i; }
    }

    // Series names are drawn as markPoint labels rather than series labels.
    // A series label whose formatter returns '' for every point but one did
    // not render at all here, and a chart with no legend and no direct labels
    // conveys no series identity whatsoever. markPoint is the mechanism the
    // annotations already use on this page, so it is the one that is known to
    // work.
    function nameAt(x, y, text, ink, pos) {
      return {
        coord: [x, y], symbol: 'circle', symbolSize: 0,
        label: {
          show: true, formatter: text, position: pos || 'top', distance: 10,
          color: ink, fontFamily: SERIF, fontSize: 13, fontWeight: 600,
          textBorderColor: C.paper, textBorderWidth: 3, padding: 0
        }
      };
    }

    make('c-thr', {
      title: cascadiaTitle(D.titles.threshold,
        'Share of each banner’s split orders whose premium exceeds the threshold · ' +
        '$4 omitted: every split clears it, so both banners sit at 100%'),
      grid: { left: 54, right: 44, bottom: 42 },
      xAxis: { type: 'category', data: labels, boundaryGap: false },
      yAxis: valueAxis(AX.threshold, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [
        { name: 'Off-Main', type: 'line', data: off, color: C.glacier,
          symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 },
          markPoint: { symbol: 'circle', symbolSize: 0, data: [
            cascadiaAnnotation(
              'The curves separate: the same rule bites the two banners differently',
              { coord: [labels[labels.length - 3], AX.threshold[1] - 1.6],
                color: INK.glacier, position: 'top', width: 250 }).data[0],
            nameAt(labels[gi], off[gi], 'Off-Main', INK.glacier, 'top')
          ] } },
        { name: 'Alder & Vance', type: 'line', data: prem, color: C.evergreen,
          symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 },
          markPoint: { symbol: 'circle', symbolSize: 0, data: [
            nameAt(labels[gi], prem[gi], 'Alder & Vance', INK.evergreen, 'bottom')
          ] } }
      ]
    }, {
      tableId: 'tbl-thr',
      ariaLabel: 'Line chart. Percent of each banner’s split orders whose premium ' +
        'exceeds a cost threshold, from five to twenty dollars. Both series fall as ' +
        'the threshold rises, the off-price series above the premium series ' +
        'throughout.',
      flags: 'the $4 threshold is in the table but not plotted; both banners are 100% there'
    });
  })();

  // =======================================================================
  // 6 · Inventory position against the real Census band · change over time
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
      grid: { left: 54, right: 122, bottom: 40 },
      xAxis: timeAxis(labels),
      yAxis: valueAxis(AX.inventory, function (v) { return v.toFixed(1); }),
      tooltip: { trigger: 'axis' },
      series: [{
        name: 'This network', type: 'line', data: ratio, color: C.evergreen,
        symbol: 'none', lineStyle: { width: 2.5 },
        endLabel: endLabel(INK.evergreen, 'This network'),
        // Rule 2.3.6 exception: Rain sits below 3:1, so the band carries a
        // direct text label rather than relying on colour alone.
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
        // Below the December dip, in the empty band between the line and zero.
        // Rule 3.4 wants the annotation AT the mark its claim depends on;
        // parked in the middle of the reference band it was legible but no
        // longer pointed at anything.
        markPoint: dec >= 0 ? cascadiaAnnotation(
          'Peak-season sales pull the ratio down, as the real series does',
          { coord: [labels[dec], 0.34], color: INK.evergreen,
            position: 'bottom', distance: 6, width: 300 }) : undefined
      }]
    }, {
      tableId: 'tbl-inv',
      ariaLabel: 'Line chart of monthly inventory-to-sales ratio for the modelled ' +
        'network against a shaded band showing the real US department-store range. ' +
        'The network series runs below the band throughout and dips each November ' +
        'and December.',
      flags: 'sector band excludes the March–May 2020 store closures',
      navigator: {
        label: 'Monthly inventory to sales ratio, months, against the department-store band.',
        series: [{ name: 'This network', points: pts(labels, ratio) }]
      }
    });
  })();

  // =======================================================================
  // 7 · Where units ship from · ranking
  //     Rule 3.3 — one emphasis, context in Rain WITH direct value labels.
  // =======================================================================
  (function () {
    var ns = D.nodes.slice().sort(function (a, b) {
      return b.cost_per_unit - a.cost_per_unit;
    });
    var names = ns.map(function (n) { return n.node_name; });
    var cpu = ns.map(function (n) { return +n.cost_per_unit.toFixed(2); });
    var isStore = ns.map(function (n) { return n.node_kind === 'STORE'; });
    var asMoney = function (v) { return '$' + v.toFixed(2); };

    make('c-nodes', {
      title: cascadiaTitle(D.titles.nodes,
        'Parcel cost per unit shipped · 24 months · stores carry 1.9% of units, ' +
        'shown in the table'),
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 62, right: 28, bottom: 70 },
      xAxis: { type: 'category', data: names,
               axisLabel: { interval: 0, fontSize: 12, width: 88, overflow: 'break' } },
      yAxis: valueAxis(AX.nodes, asMoney),
      tooltip: { trigger: 'axis',
                 valueFormatter: function (v) { return '$' + v.toFixed(2); } },
      series: [{
        type: 'bar', barWidth: '56%',
        data: cpu.map(function (v, i) {
          return { value: v, itemStyle: { color: isStore[i] ? C.madrona : C.rain } };
        }),
        label: { show: true, position: 'top',
                 formatter: function (p) { return '$' + p.value.toFixed(2); },
                 fontFamily: SERIF, fontSize: 12, color: C.basalt },
        markPoint: cascadiaAnnotation(
          'Stores are the expensive last resort that rescues an order',
          { coord: [names[2], AX.nodes[1] - 0.28], color: INK.madrona,
            position: 'top', width: 250 })
      }]
    }, {
      tableId: 'tbl-nodes',
      ariaLabel: 'Bar chart of parcel cost per unit for six fulfilment nodes, ordered ' +
        'most to least expensive. The four store nodes are the most expensive; the ' +
        'two fulfilment centres are the least.'
    });
  })();

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      charts.forEach(function (c) { c.resize(); });
    }, 120);
  });
})();
