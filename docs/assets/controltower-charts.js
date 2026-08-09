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

  /**
   * DIRECT-LABEL GUTTERS (Rule 3.6), one named value per chart.
   *
   * Every one of these reserves room for an end-of-series label. They are
   * collected here rather than inlined so the v2.3 responsive amendment can
   * replace the mechanism in one place instead of hunting through the file.
   *
   * Sized to the widest label each chart actually draws, measured rather than
   * guessed — `measureGutter` below runs the real font against the real
   * strings. Charts with no end label take the theme's own right margin.
   */
  var LABELS = {
    fills:  ['Unit fill', 'Line fill', 'Order fill'],
    cf:     ['As achieved', 'Single node only'],
    inv:    ['This network', 'Sector, unadjusted'],
    thr:    [],
    vel:    [],
    econ:   [],
    nodes:  []
  };

  function measureGutter(strings) {
    if (!strings.length) return 24;
    var c = document.createElement('canvas').getContext('2d');
    c.font = '600 13px ' + SERIF;
    var widest = 0;
    strings.forEach(function (s) {
      widest = Math.max(widest, c.measureText(s).width);
    });
    // 6px is the label's own `distance` from the line end; 4px keeps the
    // glyphs off the canvas edge. Tight on purpose — every pixel here comes
    // straight out of the plot, and at 390px the gutter is what decides
    // whether a chart clears the 65% plot-width floor.
    return Math.ceil(widest) + 10;
  }

  var GUTTER = {};
  Object.keys(LABELS).forEach(function (k) {
    GUTTER[k] = measureGutter(LABELS[k]);
  });

  /**
   * Top padding inside the plot.
   *
   * With the title out of the canvas this no longer clears a title block — it
   * clears the ANNOTATIONS, which sit in the headroom reserved at the top of
   * each axis. Set to 8 it looked correct in code and clipped the top line of
   * every two-line annotation on a phone.
   */
  var TOP_PAD = 34;

  /**
   * Annotation wrap width, one value for every width.
   *
   * cascadiaAnnotation centres its label on a data coordinate, so a box wider
   * than the plot overhangs the canvas and gets clipped — on a phone the
   * counterfactual annotation lost its first two characters and read "e gap is
   * the fill splitting buys". Sized to fit the narrowest supported canvas
   * rather than switched at a breakpoint, so there is one behaviour to reason
   * about and nothing to re-evaluate on resize.
   */
  var ANN_W = 190;

  /**
   * TITLE AND SUBTITLE LIVE IN THE DOM, NOT ON THE CANVAS.
   *
   * A canvas title has to reserve a fixed box, and the box is sized for the
   * widest case. On a 292px phone canvas the reserved block reached 99px — a
   * third of the whole chart — before the plot got anything, and a title that
   * wraps to five lines at that width overruns it anyway.
   *
   * In the DOM the title reflows like ordinary text and grows the block
   * downward instead of eating a fixed-height plot, so the canvas keeps its
   * full height at every width. It also puts the finding above the Rule 5.2
   * description rather than below it, which is the reading order Rule 3.1 asks
   * for and which the panel flagged.
   *
   * The trade this accepts: a screenshot of the bare canvas no longer carries
   * its title. The screenshot unit for this system is the `.chart-block`, which
   * is also where the provenance strip already lives, so nothing that travels
   * as a unit loses anything.
   */
  function setBlockTitle(id, title, subtitle) {
    var t = document.getElementById(id + '-title');
    var s = document.getElementById(id + '-subtitle');
    if (t) t.textContent = title;
    if (s) s.textContent = subtitle || '';
  }

  function make(id, option, opts) {
    var el = document.getElementById(id);
    if (!el) return null;
    setBlockTitle(id, opts.title, opts.subtitle);
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
        setTimeout(function () { queued = false; ch.resize(); }, 0);
      }).observe(el);
    }
    return ch;
  }

  function timeAxis(labels) {
    return {
      type: 'category', data: labels, boundaryGap: false,
      axisLabel: {
        // 'auto' rather than every third tick. A fixed interval is a desktop
        // measurement in disguise: eight month labels fit across a 1006px plot
        // and collide into an unreadable smear across a 156px one. ECharts
        // thins by available room, which is what Rule 5.5's drop order asks
        // for — thin the ticks, never rotate them.
        interval: 'auto',
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
      grid: { left: 8, right: GUTTER.fills, top: TOP_PAD, bottom: 8,
              containLabel: true },
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
              position: 'top', width: ANN_W }) }
      ]
    }, {
      title: D.titles.fills,
      subtitle: 'Unit, line and order fill · monthly · both banners · one dataset',
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
      grid: { left: 8, right: GUTTER.cf, top: TOP_PAD, bottom: 8,
              containLabel: true },
      xAxis: timeAxis(months),
      yAxis: valueAxis(AX.cf, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [
        // Lichen, NOT Evergreen. This is the same unit-fill series chart 1
        // draws, and chart 1 draws it in Lichen. Shipping it green here
        // re-dealt a fixed colour slot and a reading-panel seat, seeing only
        // the images, reported that it could not tell the two charts were
        // showing the same number over the same 24 months.
        { name: 'Unit fill as achieved', type: 'line', data: actual,
          color: C.lichen, symbol: 'none', lineStyle: { width: 2.5 },
          endLabel: endLabel(INK.lichen, 'As achieved'),
          markPoint: cascadiaAnnotation(
            'The gap is the fill splitting buys, and the cost it hides',
            { coord: [months[8], AX.cf[0] + 1.4], color: INK.madrona,
              position: 'top', width: ANN_W }) },
        { name: 'Unit fill if splitting were forbidden', type: 'line', data: cf,
          color: C.madrona, symbol: 'none',
          lineStyle: { width: 2, type: 'dashed' },
          endLabel: endLabel(INK.madrona, 'Single node only') }
      ]
    }, {
      title: D.titles.counterfactual,
      subtitle: 'Unit fill achieved, against the best any single node could have ' +
                'done · evaluated on the inventory position before each allocation',
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
    // The band's share of order lines goes on the axis. Every domain seat on
    // the reading panel asked the same question of this chart and none could
    // answer it: 17% of band C is a rounding error if band C is 3% of the
    // business and a programme if it is 40%. It is 8%, and a reader should not
    // have to open the table to learn that before deciding what the chart means.
    var velLines = D.velocity.reduce(function (a, v) { return a + v.lines; }, 0);
    var bands = D.velocity.map(function (v) {
      var nm = { A: 'A · fast', B: 'B · mid', C: 'C · slow' }[v.velocity_band];
      return nm + '\n' + (v.lines / velLines * 100).toFixed(0) + '% of lines';
    });
    var partial = D.velocity.map(function (v) { return +v.pct_partial.toFixed(2); });
    var multi = D.velocity.map(function (v) { return +v.pct_multi_node.toFixed(2); });

    make('c-vel', {
      // Decal is a second, non-colour channel. The palette does not survive a
      // luminance-only reduction, so this is load-bearing.
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 8, right: GUTTER.vel, top: TOP_PAD, bottom: 8,
              containLabel: true },
      xAxis: { type: 'category', data: bands,
               axisLabel: { lineHeight: 16, width: 88, overflow: 'break' } },
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
              position: 'top', width: ANN_W }) }
      ]
    }, {
      title: D.titles.velocity,
      subtitle: 'Share of order lines · by SKU velocity band · slow movers are ' +
                'ranged at two nodes, fast movers at six',
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
    // How much of each banner actually splits, on the axis. All three domain
    // seats asked it and none could answer: a 12% margin bite matters very
    // differently at 4% of orders than at 20%, and with two bars and no
    // denominator the chart cannot be turned into money by the person whose
    // money it is. Denominator is that banner's own orders, split and single.
    var ordersByBanner = {};
    D.economics.forEach(function (e) {
      ordersByBanner[e.banner] = (ordersByBanner[e.banner] || 0) + e.orders;
    });
    var names = splits.map(function (e) {
      var share = e.orders / ordersByBanner[e.banner] * 100;
      return e.banner_name + '\n' + share.toFixed(0) + '% of its orders split · ' +
        Math.round(e.orders).toLocaleString('en-US');
    });
    var vals = splits.map(function (e) {
      return +(e.split_premium_pct_of_margin * 100).toFixed(2);
    });
    var colors = splits.map(function (e) {
      return e.banner === 'premium' ? C.evergreen : C.glacier;
    });

    make('c-econ', {
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 8, right: GUTTER.econ, top: TOP_PAD, bottom: 8,
              containLabel: true },
      xAxis: { type: 'category', data: names,
               axisLabel: { lineHeight: 16, width: 124, overflow: 'break' } },
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
            position: 'top', width: ANN_W })
      }]
    }, {
      title: D.titles.economics,
      subtitle: 'Split premium as a share of the gross margin on the same order · ' +
                'split orders only',
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
    // Paired [dollars, percent] because the x axis is a VALUE axis, not a
    // category axis. Drawn as categories, $5→$6 and $15→$20 occupied the same
    // width, so every slope in the chart was distorted and the apparent
    // steepening past $10 was an artifact of the spacing. Two reading-panel
    // seats independently questioned the axis; one of them could only say the
    // shape looked wrong, which is what a distorted axis does to a reader.
    var off = ts.map(function (t) { return [t, +(byBanner.offprice[t] || 0).toFixed(1)]; });
    var prem = ts.map(function (t) { return [t, +(byBanner.premium[t] || 0).toFixed(1)]; });

    // Widest vertical gap, searched over INTERIOR points only. A label centred
    // on the first or last point overflows the grid edge and is silently
    // clipped — which is how this chart ended up with no series identity at
    // all on its first render: no legend by design, and both direct labels
    // sitting just outside the plot.
    var gi = 1, best = -1;
    for (var i = 1; i < off.length - 1; i++) {
      if (off[i][1] - prem[i][1] > best) { best = off[i][1] - prem[i][1]; gi = i; }
    }

    // Prefer the END OF A PLATEAU over the widest gap. Split premiums cluster on
    // discrete parcel rates, so the curves run flat then fall steeply; a label
    // centred on a point immediately before a steep fall has that fall running
    // straight through it, which is what a reading-panel seat saw — the name
    // sitting on top of its own line. On a flat run the label clears the mark
    // in both directions. Falls back to the widest interior gap if no plateau.
    for (var j = off.length - 2; j >= 1; j--) {
      if (off[j][1] === off[j + 1][1] && prem[j][1] === prem[j + 1][1]) {
        gi = j + 1;
        break;
      }
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
      grid: { left: 8, right: GUTTER.thr, top: TOP_PAD, bottom: 8,
              containLabel: true },
      xAxis: {
        type: 'value', min: ts[0], max: ts[ts.length - 1],
        // Ticks at the sampled thresholds themselves, so the reader sees which
        // points were evaluated; the marks sit at their true dollar positions.
        interval: 1,
        axisLabel: {
          formatter: function (v) { return ts.indexOf(v) < 0 ? '' : '$' + v; }
        },
        splitLine: { show: false }
      },
      yAxis: valueAxis(AX.threshold, asPct),
      tooltip: { trigger: 'axis', valueFormatter: asPct },
      series: [
        { name: 'Off-Main', type: 'line', data: off, color: C.glacier,
          symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 },
          markPoint: { symbol: 'circle', symbolSize: 0, data: [
            cascadiaAnnotation(
              'The curves separate: the same rule bites the two banners differently',
              { coord: [ts[ts.length - 3], AX.threshold[1] - 1.6],
                color: INK.glacier, position: 'top', width: ANN_W }).data[0],
            nameAt(ts[gi], off[gi][1], 'Off-Main', INK.glacier, 'top')
          ] } },
        // Dashed, not solid. Both series were solid lines of equal weight
        // separated by hue alone, and they converge to under one percent at the
        // right-hand end — the one chart in the set a reading-panel seat said
        // would genuinely degrade in grayscale. Chart 2 already uses dash for
        // exactly this job.
        { name: 'Alder & Vance', type: 'line', data: prem, color: C.evergreen,
          symbol: 'circle', symbolSize: 6,
          lineStyle: { width: 2.5, type: 'dashed' },
          markPoint: { symbol: 'circle', symbolSize: 0, data: [
            nameAt(ts[gi], prem[gi][1], 'Alder & Vance', INK.evergreen, 'bottom')
          ] } }
      ]
    }, {
      title: D.titles.threshold,
      subtitle: 'Share of each banner’s split orders whose premium exceeds the ' +
                'threshold · $4 omitted: every split clears it, so both banners ' +
                'sit at 100%',
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

    // The real sector's seasonal shape, month-of-year mean, drawn at last.
    //
    // The title's second clause — "and dips in the same season" — was a
    // comparison against a series that was not on the plot: the sector appeared
    // only as a static band, which has no time dimension and therefore cannot
    // dip. A reading-panel seat working from the image alone said so directly.
    // The series was already in the payload; validate.py's audit A3 has been
    // correlating against it the whole time.
    //
    // BAND AND LINE ARE DIFFERENT ADJUSTMENTS and both now say so on the
    // canvas. The band is the seasonally adjusted range, which is the level
    // bound audit A1 uses; seasonal adjustment removes seasonality by
    // construction, so the SA series is flat (2.75–2.91) and could never show a
    // dip. The unadjusted series is the one with a real December trough, and it
    // is the like-for-like comparator for an unadjusted network series. Drawing
    // one and labelling it as the other would be the same defect in a new place.
    var sector = labels.map(function (m) {
      var v = D.censusByMonth[parseInt(m.slice(5), 10)];
      return (v === undefined || v === null) ? null : +v.toFixed(3);
    });

    make('c-inv', {
      grid: { left: 8, right: GUTTER.inv, top: TOP_PAD, bottom: 8,
              containLabel: true },
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
          // Short, left-aligned, and outlined in paper. The band's numbers are
          // in the title and the band is no longer the only sector mark on the
          // plot, so this label only has to say WHICH sector series the shading
          // is. A long centred sentence now has the unadjusted line crossing it
          // repeatedly — the band spans 2.03–3.64 and that line oscillates
          // through nearly all of it.
          label: {
            show: true, position: 'insideTopLeft', distance: 6,
            formatter: 'Sector, seasonally adjusted',
            color: C.slateMoss, fontFamily: SERIF, fontSize: 12,
            textBorderColor: C.paper, textBorderWidth: 3
          },
          data: [[{ yAxis: lo }, { yAxis: hi }]]
        },
        // Below the December dip, in the empty band between the line and zero.
        // Rule 3.4 wants the annotation AT the mark its claim depends on;
        // parked in the middle of the reference band it was legible but no
        // longer pointed at anything.
        markPoint: dec >= 0 ? cascadiaAnnotation(
          'Peak-season sales pull the ratio down, as the real series does',
          // Hung from 0.52, not 0.34: the text wraps to two lines and the second
          // was running into the zero gridline and the month labels under it.
          { coord: [labels[dec], 0.52], color: INK.evergreen,
            position: 'bottom', distance: 6, width: ANN_W }) : undefined
      }, {
        name: 'US department stores, unadjusted', type: 'line', data: sector,
        color: C.slateMoss, symbol: 'none',
        lineStyle: { width: 2, type: 'dashed' },
        endLabel: endLabel(INK.slate, 'Sector, unadjusted')
      }]
    }, {
      title: D.titles.inventory,
      subtitle: 'Months of sales held in inventory · inventory at cost over sales ' +
                'at retail, the Census convention · one fulfilment network against ' +
                'whole department-store companies — a plausibility bound, not a ' +
                'peer target',
      tableId: 'tbl-inv',
      ariaLabel: 'Line chart of monthly inventory-to-sales ratio for the modelled ' +
        'network against a shaded band showing the seasonally adjusted US ' +
        'department-store range, and a dashed line showing the unadjusted sector ' +
        'series. The network runs below the band throughout, and both the network ' +
        'and the unadjusted sector series dip each November and December.',
      flags: 'sector band excludes the March–May 2020 store closures',
      navigator: {
        label: 'Monthly inventory to sales ratio, months, against the department-store band.',
        series: [
          { name: 'This network', points: pts(labels, ratio) },
          { name: 'US department stores, unadjusted', points: pts(labels, sector) }
        ]
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
    // Two things the plot withheld, both restored to the axis label.
    //
    // "primary" — the title claims every store ships at more than double the
    // PRIMARY FC's cost per unit. Two FCs are drawn in the same colour and
    // nothing said which one was primary. Against Cascade Ridge ($1.65) the
    // claim is true; against Fernhill ($2.27) no store clears double, so the
    // truth of the headline turned on a fact the picture did not carry. A
    // reading-panel seat found exactly that and could not verify the title.
    //
    // "% of units" — the volume weighting was in the subtitle and the table,
    // and all three domain seats independently said the chart was unreadable
    // without it: four fat bars get the same visual weight as the two nodes
    // doing essentially all the work.
    var totalUnits = ns.reduce(function (a, n) { return a + n.units; }, 0);
    var names = ns.map(function (n) {
      var share = (n.units / totalUnits) * 100;
      return n.node_name + '\n' + (n.node_key === 'FC1' ? 'primary · ' : '') +
        (share >= 1 ? share.toFixed(0) : share.toFixed(1)) + '%';
    });
    var cpu = ns.map(function (n) { return +n.cost_per_unit.toFixed(2); });
    var isStore = ns.map(function (n) { return n.node_kind === 'STORE'; });
    var asMoney = function (v) { return '$' + v.toFixed(2); };

    make('c-nodes', {
      aria: { enabled: true, decal: { show: true } },
      grid: { left: 8, right: GUTTER.nodes, top: TOP_PAD, bottom: 8,
              containLabel: true },
      // Bounded width with overflow:'break' so a long name WRAPS rather than
      // running into its neighbours. Six categories at 320px give each label
      // about 33px of real estate, so an unbounded label box smears; a bounded
      // one degrades to more lines instead, which is legible.
      xAxis: { type: 'category', data: names,
               axisLabel: { interval: 0, fontSize: 12, width: 104,
                            lineHeight: 15, overflow: 'break' } },
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
            position: 'top', width: ANN_W })
      }]
    }, {
      title: D.titles.nodes,
      subtitle: 'Parcel cost per unit shipped · 24 months · each node’s share of ' +
                'units is on the axis beneath it',
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
