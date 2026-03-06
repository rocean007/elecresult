"""
scraper.py — Nepal Election 2082 scraper
Fetches live data from the ECN results site and writes output/data.json

WHY THE PREVIOUS VERSION FAILED:
  result.election.gov.np is a JavaScript SPA. It returns an empty HTML shell
  at /fptp — all actual data loads via internal JSON API calls the browser makes.
  requests + BeautifulSoup only sees the empty shell, hence 0 results.

THIS VERSION:
  Calls the internal JSON endpoints the SPA uses directly (no JS needed).
  Endpoint URLs discovered by inspecting browser network traffic on the site.

Usage:
    python scraper/scraper.py              # run once
    python scraper/scraper.py --watch 60   # re-run every 60 seconds
"""

import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────

BASE   = "https://result.election.gov.np"
OUTPUT = Path("output/data.json")

# These are the internal JSON/txt endpoints the ECN SPA hits.
# Found by opening result.election.gov.np in a browser, opening DevTools → Network,
# filtering by XHR/Fetch, and watching what URLs get called.
ECN_PARTY_SUMMARY = f"{BASE}/JSONFiles/GetPartyResult.txt"
ECN_FPTP_SUMMARY  = f"{BASE}/JSONFiles/GetFPTPSummary.txt"       # all 165 rows
ECN_CONSTITUENCY  = f"{BASE}/JSONFiles/GetFPTPResult.txt"         # ?constituentNo=N
ECN_PR_SUMMARY    = f"{BASE}/JSONFiles/GetPRSummary.txt"

PARTY_COLORS = {
    "CPN-UML":  "#C0392B",
    "NC":       "#2563C4",
    "RSP":      "#1A7D52",
    "CPN-MC":   "#7B3FA0",
    "RPP":      "#C07820",
    "LSP":      "#E85A20",
    "IND":      "#4A5568",
}

PROVINCE_MAP = {
    "1": "Koshi",
    "2": "Madhesh",
    "3": "Bagmati",
    "4": "Gandaki",
    "5": "Lumbini",
    "6": "Karnali",
    "7": "Sudurpashchim",
}

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Referer":    "https://result.election.gov.np/",
    "Accept":     "application/json, text/plain, */*",
    "Accept-Language": "ne,en;q=0.9",
})


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_json(url, params=None):
    """GET a URL that returns JSON or a JSON-like .txt file. Returns parsed dict/list or None."""
    for attempt in range(3):
        try:
            r = SESSION.get(url, params=params, timeout=15)
            r.raise_for_status()
            # ECN serves JSON as text/plain sometimes
            return r.json()
        except requests.exceptions.HTTPError as e:
            print(f"  HTTP {e.response.status_code} for {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  [retry {attempt+1}/3] {url} — {e}")
            time.sleep(2 * (attempt + 1))
        except json.JSONDecodeError as e:
            # Try stripping BOM or garbage prefix
            try:
                text = r.text.strip().lstrip('\ufeff')
                return json.loads(text)
            except Exception:
                print(f"  JSON parse error for {url}: {e}")
                return None
    return None


def party_color(party_id):
    return PARTY_COLORS.get(party_id, "#888888")


# ── SCRAPE PARTY SEAT SUMMARY ─────────────────────────────────────────────────

def scrape_party_seats():
    """
    Calls ECN's internal party result endpoint.
    Returns list of { id, name, color, fptp, pr, total }
    """
    data = get_json(ECN_PARTY_SUMMARY)
    if not data:
        print("  Could not fetch party summary — site may not be serving results yet")
        return []

    parties = []
    # ECN typically returns a list of objects. Field names vary by election.
    # Common keys seen in 2079: PartyName, PartyID, FPTPWon, FPTPLeading, PRSeats
    for item in (data if isinstance(data, list) else data.get("data", [])):
        pid  = str(item.get("PartyID", item.get("partyId", "??")))
        name = item.get("PartyName", item.get("partyName", pid))
        fptp_won  = int(item.get("FPTPWon",     item.get("fptpWon",     0)) or 0)
        fptp_lead = int(item.get("FPTPLeading", item.get("fptpLeading", 0)) or 0)
        pr        = int(item.get("PRSeats",     item.get("prSeats",     0)) or 0)
        parties.append({
            "id":    pid,
            "name":  name,
            "color": party_color(pid),
            "fptp":  fptp_won + fptp_lead,
            "pr":    pr,
            "total": fptp_won + fptp_lead + pr,
        })

    return sorted(parties, key=lambda p: p["total"], reverse=True)


# ── SCRAPE ALL CONSTITUENCIES (summary) ───────────────────────────────────────

def scrape_fptp_summary():
    """
    Calls the FPTP summary endpoint — returns top candidate per constituency for all 165.
    Returns list of constituency dicts.
    """
    data = get_json(ECN_FPTP_SUMMARY)
    if not data:
        return []

    rows = data if isinstance(data, list) else data.get("data", [])
    constituencies = {}

    for row in rows:
        num = int(row.get("ConstituentNo", row.get("constituentNo", 0)))
        if not num:
            continue

        province_num = str(row.get("StateNo", row.get("stateNo", "")))
        province     = PROVINCE_MAP.get(province_num, "")

        status_raw = str(row.get("EStatus", row.get("eStatus", ""))).upper()
        status = "declared" if status_raw in ("E", "ELECTED", "DECLARED") else "counting"

        reported = int(row.get("CountedPercent", row.get("countedPercent", 0)) or 0)

        cand = {
            "name":       row.get("CandidateName", row.get("candidateName", "")),
            "party_id":   str(row.get("PartyID", row.get("partyId", ""))),
            "party_name": row.get("PartyName", row.get("partyName", "")),
            "color":      party_color(str(row.get("PartyID", row.get("partyId", "")))),
            "votes":      int(row.get("TotalVotes", row.get("totalVotes", 0)) or 0),
            "img":        row.get("PhotoPath", row.get("photoPath", None)),
        }

        if num not in constituencies:
            constituencies[num] = {
                "num":        num,
                "name":       row.get("ConstituentName", row.get("constituentName", f"Constituency {num}")),
                "district":   row.get("DistrictName",    row.get("districtName",    "")),
                "province":   province,
                "status":     status,
                "reported":   min(reported, 100),
                "candidates": [],
            }

        constituencies[num]["candidates"].append(cand)

    # Sort candidates by votes descending
    result = []
    for c in constituencies.values():
        c["candidates"].sort(key=lambda x: x["votes"], reverse=True)
        result.append(c)

    return sorted(result, key=lambda c: c["num"])


# ── SCRAPE SINGLE CONSTITUENCY (full detail) ──────────────────────────────────

def scrape_one_constituency(num):
    """
    Calls ECN per-constituency endpoint for full candidate list.
    """
    data = get_json(ECN_CONSTITUENCY, params={"constituentNo": num})
    if not data:
        return None

    rows = data if isinstance(data, list) else data.get("data", [])
    if not rows:
        return None

    first = rows[0]
    province_num = str(first.get("StateNo", first.get("stateNo", "")))
    status_raw   = str(first.get("EStatus", first.get("eStatus", ""))).upper()
    status       = "declared" if status_raw in ("E", "ELECTED", "DECLARED") else "counting"
    reported     = int(first.get("CountedPercent", first.get("countedPercent", 0)) or 0)

    candidates = []
    for row in rows:
        pid = str(row.get("PartyID", row.get("partyId", "")))
        candidates.append({
            "name":       row.get("CandidateName", row.get("candidateName", "")),
            "party_id":   pid,
            "party_name": row.get("PartyName", row.get("partyName", "")),
            "color":      party_color(pid),
            "votes":      int(row.get("TotalVotes", row.get("totalVotes", 0)) or 0),
            "img":        row.get("PhotoPath", row.get("photoPath", None)),
        })

    candidates.sort(key=lambda c: c["votes"], reverse=True)

    return {
        "num":        num,
        "name":       first.get("ConstituentName", first.get("constituentName", f"Constituency {num}")),
        "district":   first.get("DistrictName",    first.get("districtName",    "")),
        "province":   PROVINCE_MAP.get(str(first.get("StateNo", first.get("stateNo", ""))), ""),
        "status":     status,
        "reported":   min(reported, 100),
        "candidates": candidates,
    }


# ── MAIN SCRAPE ───────────────────────────────────────────────────────────────

def run():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting scrape…")

    # 1. Party seats
    print("  Fetching party seats…")
    party_seats = scrape_party_seats()
    print(f"  → {len(party_seats)} parties")

    # 2. All constituencies via summary endpoint (fast, one request)
    print("  Fetching FPTP summary (all 165)…")
    constituencies = scrape_fptp_summary()
    print(f"  → {len(constituencies)} constituencies")

    # If summary gave us partial candidates, optionally enrich with per-seat detail.
    # Uncomment the block below to fetch full candidate lists (makes 165 HTTP requests):
    #
    # print("  Enriching with per-constituency detail…")
    # for i, c in enumerate(constituencies, 1):
    #     detail = scrape_one_constituency(c["num"])
    #     if detail:
    #         c["candidates"] = detail["candidates"]
    #     if i % 10 == 0:
    #         print(f"    {i}/165…")

    declared = sum(1 for c in constituencies if c["status"] == "declared")
    counting  = sum(1 for c in constituencies if c["status"] == "counting")

    output = {
        "updated_at":     datetime.now(timezone.utc).isoformat(),
        "declared":       declared,
        "counting":       counting,
        "total":          len(constituencies),
        "party_seats":    party_seats,
        "constituencies": constituencies,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ Saved {OUTPUT}  ({len(constituencies)} constituencies, {declared} declared)\n")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nepal Election 2082 Scraper")
    parser.add_argument("--watch", type=int, metavar="SECONDS",
                        help="Re-run every N seconds (e.g. --watch 60)")
    args = parser.parse_args()

    if args.watch:
        print(f"Watch mode — re-running every {args.watch}s. Ctrl+C to stop.")
        while True:
            try:
                run()
            except Exception as e:
                print(f"Error: {e}")
            print(f"  Sleeping {args.watch}s…")
            time.sleep(args.watch)
    else:
        run()