"""
build_metric_register.py — generate the certified metric register from dbt.

Cascadia Control Tower · governance

Input : dbt/target/manifest.json      (written by `dbt build` / `dbt parse`)
Output: governance/metric_register.md
        docs/data/metric_register.json  (inlined into the static page)

    python src/build_metric_register.py           regenerate
    python src/build_metric_register.py --check   fail if the committed
                                                  register has drifted

WHY THIS EXISTS
---------------
The register is the module's headline governance artifact, so it must not be a
table someone typed once. Every entry here comes from a `meta:` block on a
column in `dbt/models/marts/_marts.yml` — the same file that defines the tests
and the model contract. Change a definition, rebuild, and the register and the
page change with it.

`--check` is the sync mechanism made enforceable: it regenerates in memory and
compares against what is committed, so a definition can never quietly drift
away from the model that computes it. Run it after dbt in any build sequence.

A hand-typed register is documentation. A generated one is engineering, and it
is the difference between a governance artifact that is true and one that was
true on the day it was written.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "dbt" / "target" / "manifest.json"
REGISTER_MD = REPO_ROOT / "governance" / "metric_register.md"
REGISTER_JSON = REPO_ROOT / "docs" / "data" / "metric_register.json"

TIER_ORDER = {"certified": 0, "exploratory": 1}


def collect():
    if not MANIFEST.exists():
        sys.exit(f"ERROR: {MANIFEST} not found.\n"
                 "Run `dbt build --profiles-dir .` from dbt/ first — the "
                 "register is generated from dbt's manifest, not hand-written.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    metrics = []
    for node in manifest["nodes"].values():
        if node.get("resource_type") != "model":
            continue
        for col_name, col in (node.get("columns") or {}).items():
            meta = col.get("meta") or {}
            if not meta.get("metric"):
                continue
            metrics.append({
                "metric": meta.get("metric_name", col_name),
                "tier": meta.get("tier", "unspecified"),
                "grain": meta.get("grain", ""),
                "owner": meta.get("owner", ""),
                "definition": " ".join(meta.get("definition", "").split()),
                "lineage": meta.get("lineage", ""),
                "version": str(meta.get("version", "")),
                "version_history": " ".join(
                    meta.get("version_history", "").split()),
                "tier_reason": " ".join(meta.get("tier_reason", "").split()),
                "model": node["name"],
                "column": col_name,
            })

    metrics.sort(key=lambda m: (TIER_ORDER.get(m["tier"], 9), m["metric"]))
    return metrics


def render_markdown(metrics):
    certified = [m for m in metrics if m["tier"] == "certified"]
    exploratory = [m for m in metrics if m["tier"] == "exploratory"]

    out = [
        "# Certified metric register",
        "",
        "<!-- GENERATED FILE — DO NOT EDIT BY HAND.",
        "     Source: meta blocks on columns in dbt/models/marts/_marts.yml",
        "     Regenerate: python src/build_metric_register.py",
        "     Verify:     python src/build_metric_register.py --check -->",
        "",
        f"**{len(certified)} certified · {len(exploratory)} exploratory.**",
        "",
        "This register is generated from the `meta:` blocks on the dbt models",
        "that compute these metrics — the same file that defines their tests.",
        "Nothing here is typed twice, and",
        "`python src/build_metric_register.py --check` fails the build if a",
        "definition drifts from the model behind it.",
        "",
        "**Certification is not a ranking.** An exploratory metric is not a bad",
        "metric; it is a metric the business has agreed not to run on. Retaining",
        "the other definitions and labelling them is the governance act. Quietly",
        "deleting them would move the disagreement rather than resolve it.",
        "",
        "| Metric | Tier | Grain | Owner | Computed by |",
        "|---|---|---|---|---|",
    ]
    for m in metrics:
        tier = ("**certified**" if m["tier"] == "certified" else m["tier"])
        out.append(f"| {m['metric']} | {tier} | {m['grain']} | {m['owner']} "
                   f"| `{m['model']}.{m['column']}` |")

    out += ["", "---", ""]

    for label, group in (("Certified", certified), ("Exploratory", exploratory)):
        if not group:
            continue
        out += [f"## {label}", ""]
        for m in group:
            out += [
                f"### {m['metric']}",
                "",
                f"**Definition.** {m['definition']}",
                "",
                f"- **Tier** · {m['tier']}",
                f"- **Grain** · {m['grain']}",
                f"- **Owner** · {m['owner']}",
                f"- **Lineage** · `{m['lineage']}`",
                f"- **Computed by** · `{m['model']}.{m['column']}`",
                f"- **Version** · {m['version']}",
                "",
                f"**Why this tier.** {m['tier_reason']}",
                "",
                f"**Version history.** {m['version_history']}",
                "",
            ]

    out += [
        "---",
        "",
        "## The ad-hoc extraction pathology, shown and resolved",
        "",
        "Before certification there were three fill rates in circulation and no",
        "statement of which one the business ran on. Each was defensible to the",
        "team that built it:",
        "",
        "| Derivation | Who built it | Why it was defensible | What it cost |",
        "|---|---|---|---|",
        "| Unit fill | Operations | Measures how much of the demand physically moved, which is what a DC controls | The most forgiving of the three, so it was the number that travelled upward |",
        "| Line fill | Merchandising | Measures assortment coverage, which is what a buyer can act on | Treats a missing line on a three-line order as a two-thirds success |",
        "| Order fill | Finance | Measures whether the customer got what they asked for | Strictest, so it was the least quoted |",
        "",
        "The cost was not licences or dashboards. It was that **the three teams",
        "could not have the same conversation about the same week.** Operations",
        "reported service improving while Finance reported it flat, and both",
        "were arithmetically correct, so the meeting resolved nothing and the",
        "split rate — which none of the three measured — went unexamined.",
        "",
        "The resolution certifies order fill, retains the other two as",
        "exploratory with the reason stated, and adds split rate to the",
        "register so the cost of achieving fill is visible next to the fill",
        "itself.",
        "",
    ]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed register is out of sync")
    args = ap.parse_args()

    metrics = collect()
    if not metrics:
        sys.exit("ERROR: no metrics found in the manifest. Every register entry "
                 "comes from a meta.metric block on a model column; if there "
                 "are none, the register would silently publish as empty.")

    markdown = render_markdown(metrics)
    payload = json.dumps({"metrics": metrics}, indent=2) + "\n"

    if args.check:
        drift = []
        if not REGISTER_MD.exists():
            drift.append(str(REGISTER_MD.relative_to(REPO_ROOT)) + " missing")
        elif REGISTER_MD.read_text(encoding="utf-8") != markdown:
            drift.append(str(REGISTER_MD.relative_to(REPO_ROOT)) + " out of date")
        if not REGISTER_JSON.exists():
            drift.append(str(REGISTER_JSON.relative_to(REPO_ROOT)) + " missing")
        elif REGISTER_JSON.read_text(encoding="utf-8") != payload:
            drift.append(str(REGISTER_JSON.relative_to(REPO_ROOT))
                         + " out of date")
        if drift:
            print("METRIC REGISTER OUT OF SYNC with dbt model metadata:")
            for d in drift:
                print(f"  - {d}")
            print("\nRun: python src/build_metric_register.py")
            sys.exit(1)
        print(f"Metric register in sync · {len(metrics)} metrics")
        return

    REGISTER_JSON.parent.mkdir(parents=True, exist_ok=True)
    REGISTER_MD.write_text(markdown, encoding="utf-8")
    REGISTER_JSON.write_text(payload, encoding="utf-8")

    certified = sum(1 for m in metrics if m["tier"] == "certified")
    print(f"Generated the metric register from dbt model metadata")
    print(f"  {len(metrics)} metrics · {certified} certified · "
          f"{len(metrics) - certified} exploratory")
    for m in metrics:
        print(f"    {m['tier']:12} {m['metric']:28} "
              f"{m['model']}.{m['column']}")
    print(f"  wrote {REGISTER_MD}")
    print(f"  wrote {REGISTER_JSON}")


if __name__ == "__main__":
    main()
