"""
ingest_anchors.py — pull the three real anchors once, freeze them, commit them.

Cascadia Control Tower · anchor freeze

WHAT & WHY
----------
This module's operational spine is synthetic. Its credibility comes from three
real public datasets that the generator is checked against. Those three are
pulled ONCE, written to data/raw/, and committed. Nothing in the build or the
published page ever makes a network call again — a reader can reproduce every
realism audit from the committed bytes alone.

  Anchor A · BLS OEWS       labor rates, SOC 53-7062, Seattle-Tacoma-Bellevue
  Anchor B · Census MRTS    department-store inventories and inventories/sales
  Anchor C · SEC EDGAR      peer XBRL for Macy's, Kohl's, Dillard's

The EDGAR client here is adapted from cascadia-semiconductors-analytics
(src/ingest_peers.py) rather than rewritten: same declared User-Agent, same
throttle, same polite backoff, same "resolve CIKs from the committed ticker map,
never guess" rule.

NAMING RULE
-----------
The calibration filer is not touched by this script and is never named in this
repository. See governance/naming_policy.md. Only the three peers above are
pulled from EDGAR here, and they are benchmarks, not the subject.

Usage:
    python src/ingest_anchors.py
"""

import gzip
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"

USER_AGENT = "RobbinsAnalytics cascadia-controltower ajayrobbins@hotmail.com"
THROTTLE_SECONDS = 0.25
BACKOFF_SCHEDULE = [2, 5, 15, 60]

# Anchor C — the XBRL benchmark set. Named deliberately; see naming_policy.md.
PEERS = ["M", "KSS", "DDS"]
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json"

# Anchor A — BLS OEWS May 2025 metro file.
# NOTE: the archive also contains BOS_M2025_dl.xlsx (Balance of State,
# nonmetropolitan). That file carries SOC 53-7062 but no metro areas, so reading
# it instead of MSA_ finds the occupation and silently loses area 42660.
OEWS_URL = "https://www.bls.gov/oes/special-requests/oesm25ma.zip"

# Anchor B — Census MRTS. The path implied by the brief (retail/mrts/www/...)
# 404s; the inventories file lives under retail/mrtsinv/. Verified 2026-08-07.
CENSUS_INV_URL = "https://www.census.gov/retail/mrtsinv/www/mrtsinv92-present.xlsx"
CENSUS_SALES_URL = "https://www.census.gov/retail/mrts/www/mrtssales92-present.xlsx"


def polite_get(url: str, timeout: int = 300) -> bytes:
    """GET with base throttle + polite backoff on 429/5xx.

    Lifted from the semiconductors ingest so SEC etiquette stays identical
    across modules: declared User-Agent, ~4 req/s ceiling, escalating backoff,
    and no retry on 403/404 because those will not fix themselves.
    """
    last = None
    for attempt, backoff in enumerate([0] + BACKOFF_SCHEDULE):
        if backoff:
            print(f"    retrying in {backoff}s (attempt {attempt + 1}) ...")
            time.sleep(backoff)
        time.sleep(THROTTLE_SECONDS)
        req = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT,
                          "Accept-Encoding": "gzip, deflate"})
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except urllib.error.URLError as e:
            last = e
    raise RuntimeError(f"Failed after retries: {url} ({last})")


def freeze(name: str, raw: bytes, url: str, entries: dict, note: str = "") -> None:
    """Write one frozen snapshot and record its SHA-256 in the manifest.

    The hash is the point. It is what lets a reader assert that the bytes the
    audits ran against are the bytes in the repository.
    """
    (RAW_DIR / name).write_bytes(raw)
    entries[name] = {
        "url": url,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    if note:
        entries[name]["note"] = note
    print(f"  {name:44} {len(raw):>12,} bytes  {entries[name]['sha256'][:16]}...")


def resolve_peer_ciks(entries: dict) -> dict:
    """Resolve peer tickers -> CIK from SEC's own ticker map, never by guessing."""
    raw = polite_get(TICKER_MAP_URL)
    freeze("company_tickers.json", raw, TICKER_MAP_URL, entries,
           note="SEC's authoritative ticker->CIK map. Peer CIKs are resolved "
                "from this committed file so no CIK in this repo is hand-typed.")
    tm = json.loads(raw)
    lookup = {row["ticker"].upper(): row["cik_str"] for row in tm.values()}
    ciks = {}
    for t in PEERS:
        if t not in lookup:
            raise SystemExit(
                f"ERROR: ticker {t} is not in SEC's ticker map. The peer set "
                f"cannot be resolved without guessing a CIK, and guessing is "
                f"not permitted. Stopping."
            )
        ciks[t] = lookup[t]
    return ciks


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    retrieved = date.today().isoformat()
    entries: dict = {}

    print(f"Anchor freeze · retrieved {retrieved}")
    print(f"User-Agent: {USER_AGENT}\n")

    print("Anchor C — SEC EDGAR peer XBRL (Macy's, Kohl's, Dillard's)")
    ciks = resolve_peer_ciks(entries)
    peer_meta = {}
    for ticker, cik in ciks.items():
        url = COMPANYFACTS_URL.format(cik=cik)
        raw = polite_get(url)
        name = f"companyfacts_{ticker}_CIK{cik:0>10}.json"
        entity = json.loads(raw).get("entityName", "?")
        freeze(name, raw, url, entries, note=f"{ticker} · {entity}")
        peer_meta[ticker] = {"cik": f"{cik:0>10}", "entity_name": entity,
                             "file": name}

    print("\nAnchor A — BLS OEWS May 2025, metro file")
    raw = polite_get(OEWS_URL)
    freeze("oesm25ma.zip", raw, OEWS_URL, entries,
           note="Read MSA_M2025_dl.xlsx from this archive, NOT BOS_M2025_dl.xlsx "
                "(Balance of State) — the latter has SOC 53-7062 but no metro "
                "areas, so area 42660 silently disappears.")

    print("\nAnchor B — Census MRTS")
    raw = polite_get(CENSUS_INV_URL)
    freeze("mrtsinv92-present.xlsx", raw, CENSUS_INV_URL, entries,
           note="End-of-month retail inventories AND inventories/sales ratios by "
                "kind of business, 1992-present. 'Department stores' is the line "
                "realism audit A checks against. Note the path is under "
                "retail/mrtsinv/, not retail/mrts/.")
    raw = polite_get(CENSUS_SALES_URL)
    freeze("mrtssales92-present.xlsx", raw, CENSUS_SALES_URL, entries,
           note="Companion monthly sales series, same kind-of-business breakdown.")

    manifest = {
        "module": "cascadia-controltower",
        "retrieval_date": retrieved,
        "principle": (
            "Pull once, freeze, commit. No build step and no published page "
            "makes a live network call. Every realism audit is reproducible "
            "from these bytes alone; the sha256 of each file is recorded so a "
            "reader can prove the audit ran against what is committed."
        ),
        "naming_note": (
            "The generator's calibration filer is NOT in this manifest and is "
            "not named anywhere in this repository. Only derived, unattributed "
            "ratios enter the repo, in calibration_envelope.json. See "
            "governance/naming_policy.md for why this one source deliberately "
            "breaks the freeze-and-commit principle."
        ),
        "user_agent": USER_AGENT,
        "anchors": {
            "A_labor": {"source": "BLS OEWS", "series": "SOC 53-7062",
                        "area": "42660 Seattle-Tacoma-Bellevue, WA",
                        "vintage": "May 2025", "file": "oesm25ma.zip"},
            "B_inventory": {"source": "US Census MRTS",
                            "series": "Department stores, end-of-month "
                                      "inventories and inventories/sales ratio",
                            "file": "mrtsinv92-present.xlsx"},
            "C_peers": {"source": "SEC EDGAR companyfacts",
                        "companies": peer_meta},
        },
        "files": entries,
    }
    (RAW_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    total = sum(e["bytes"] for e in entries.values())
    print(f"\nWrote {RAW_DIR / 'manifest.json'}")
    print(f"{len(entries)} files frozen · {total:,} bytes total")


if __name__ == "__main__":
    main()
