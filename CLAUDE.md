# Cascadia Control Tower — what an agent needs to know

A distribution-centre analytics module for **Alder & Vance Retail Group**, an
invented two-banner department-store fulfillment operation. Seventh module in the
Cascadia portfolio. Synthetic operational spine, three real public anchors,
published as static HTML from `docs/` to
`www.robbinsanalytics.com/cascadia-controltower/`.

The build brief is
`C:\Projects\cascadia-standards\docs\Cascadia_ControlTower_CC_Handoff_2026-08-07.md`,
amended by the addendum beside it. **The addendum wins where the two differ** —
the original handoff is wrong on three points and they are listed there.

## The one rule that has no exceptions

**The calibration filer is never named.** Not on the page, not in code, not in
comments, not in filenames, not in commit messages, not in `data/raw/`. It is a
real, formerly-listed department-store operator whose published figures shape the
generator's scale and mix. Nothing in this repository records which company it is,
and nothing added to this repository ever may.

**Work from the allow-list, not from memory.** These are the only company names
permitted anywhere in this repo:

| Tier | Rule |
|---|---|
| **Subject** | **Alder & Vance Retail Group** — invented. Premium banner **Alder & Vance**, off-price banner **Off-Main**. Both fictional; neither exists in real retail (checked 2026-08-07). |
| **Calibration filer** | **Never named, anywhere.** Its filed figures shape generator parameters. Only *derived, unattributed* ratios enter the repo — see `governance/naming_policy.md`. |
| **Industry conditions** | Citable on the page by name: NRF returns figures, apparel return rates, split-shipment economics, the documented absence of a settled fill-rate/OTIF formula. |
| **Named peers** | **Macy's, Kohl's, Dillard's are named.** They are the XBRL benchmark set doing the plausibility work, exactly as Cascadia Finance names FormFactor and six peers. Naming a benchmark is not naming a subject. |

**Any company name outside that table is a defect.** If one is about to be
written, stop.

**On the page, calibration is described in the plural** — "calibrated to published
department-store filings" — never as a single unnamed filer. Singling out one
filer invites the reader to identify it. Decision recorded 2026-08-07.

## Build principles that are load-bearing

**Ambiguity fails the build.** Where a rule cannot resolve a case, the run stops
rather than guessing. An order that cannot be classified split / not-split under
the documented rule fails `validate.py`. This mirrors Deal Desk failing on an
unresolvable agreement tie, and it is not decorative.

**Gaps are shown as gaps.** Nothing interpolated, zero-filled or estimated to
fill a hole. Missing is a first-class value. Residuals are reported as
residuals.

**The realism audit must be able to fail.** Three audits check the generator
against *real* anchors — Census inventory/sales band, peer-XBRL fulfillment-cost
share, and split concentration. If an audit cannot fail, it is not an audit.
This is the module's step up from Deal Desk, whose audit checks the generator
against itself.

## Data — pull once, freeze, commit

`data/raw/` holds frozen snapshots and **is committed**. No page or build step
may make a live network call at render time. Anchors:

- **BLS OEWS**, SOC 53-7062, Seattle-Tacoma-Bellevue metro, area 42660 — labor rates, percentile spread not just median
- **Census MRTS** — department-store end-of-month inventories and inventories/sales ratios
- **SEC EDGAR `companyfacts`** — Macy's (M), Kohl's (KSS), Dillard's (DDS)

**Reuse the EDGAR ingest from `C:\Projects\cascadia-semiconductors-analytics`**
(note the `-analytics` suffix; the handoff omits it). It already handles the
tag-priority map, fiscal-calendar conformance, derived Q4 as FY − (Q1+Q2+Q3)
with a `derived` flag, restatements keeping the latest filed value, and a
compliant SEC User-Agent under the rate limit. Adapt, don't rewrite.

All three verified as pulling on 2026-08-07 — the exact BLS row, the Census
department-store series and all three peer bundles. See
`governance/anchor_verification.md`.

**One documented exception to freeze-and-commit: the calibration filer's raw
bundle is never committed.** Its JSON carries the entity name and ticker in plain
text, so committing it would write the name into the repo. Only derived,
unattributed ratios enter `data/raw/calibration_envelope.json`. The naming rule
outranks the freeze principle; the peer set is frozen and committed in full and
does all the audit work, so nothing checkable is lost.

If an anchor turns out to be unavailable or materially different from the brief,
**say so and stop.** Prefer "I could not establish this" over substituting.

## Publishing

**GitHub Pages serves `docs/` from `main`. Pushing `main` is the deploy.** No
build step, no Action — what is committed is what is served. Same model as
Cascadia Finance.

**The site repo is separate and publishes differently.** `RobbinsAnalytics.github.io`
deploys via a GitHub Action on push to `main`. **Never run `quarto publish gh-pages`
by hand there** — it races CI and can push a stale build over a fresh one. Use
that repo's `/publish` skill, from a session rooted in it. The original handoff
recommends `publish-site.ps1` and `quarto publish --no-prompt`; that advice is
stale and the site repo's own `CLAUDE.md` overrides it.

**Only the case-study `.qmd` lands in the site repo.** Built static output stays
here in `docs/`, matching Deal Desk and Finance. The handoff says otherwise and
is wrong.

**Surface the module with the `surface-module` skill** after the build ships —
case study page, navbar, home card, family page, OG thumbnail, link check.

## Committing

**Stage by name — never `git add -A` or `git add .`.** Both are denied in
`.claude/settings.json`, and a `PreToolUse` hook refuses any commit carrying a
whitespace-only diff. Verify with
`git diff --ignore-all-space --numstat -- <file>`; empty output means the diff
is noise and the file must not be staged.

**Run this repo's commits from a session rooted in this repo.** Hooks and this
file load only from the primary working directory — a directory grant shares
files and skills but never hooks.

**Do not modify any existing Cascadia module or existing site content.** This
build adds a new module.

## Charts

The portfolio runs a written visualization standard at
`C:\Projects\cascadia-standards\design-system\VIZ-PRINCIPLES.md` (v2.3) with
a scored checklist at `CHART-REVIEW.md` beside it. **Read both before building any chart.** Every
chart title is a complete sentence stating the finding, never a label. Every
chart carries a real data table. WCAG 2.2 AA throughout.

Rule 7.4 requires a blind reading panel before ship — run the
`cascadia-reading-panel` skill and record the result in
`governance/chart-review.md`, including what failed on the first pass.

## Aaron

**Aaron does not write code and does not run scripts.** He approves decisions;
the agent executes. Never end a task with "now run this." Explain what was built
in terms he can narrate under questioning in an interview — that is the module's
actual acceptance test.
