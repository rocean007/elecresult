"""
scraper.py — Nepal Election 2082 scraper
Fetches live data from result.election.gov.np → writes output/data.json

The ECN site requires:
  1. A session cookie (obtained by visiting the homepage first)
  2. A CSRF token (embedded in the homepage HTML, sent as x-csrf-token header)
  3. Referer: https://result.election.gov.np/

Usage:
    python scraper/scraper.py
    python scraper/scraper.py --watch 60
"""

import json, time, argparse, re
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE    = "https://result.election.gov.np"
HANDLER = f"{BASE}/Handlers/SecureJson.ashx"
PREFIX  = "JSONFiles/Election2082"
OUTPUT  = Path("output/data.json")

PARTY_COLORS = {
    "CPN-UML": "#C0392B", "NC": "#2563C4", "RSP": "#1A7D52",
    "CPN-MC":  "#7B3FA0", "RPP": "#C07820", "LSP": "#E85A20", "IND": "#4A5568",
}
PROVINCE_MAP = {
    "1": "Koshi",    "2": "Madhesh",       "3": "Bagmati",
    "4": "Gandaki",  "5": "Lumbini",        "6": "Karnali",
    "7": "Sudurpashchim",
}

BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

SESSION    = requests.Session()
CSRF_TOKEN = None


def init_session():
    """Visit the homepage, grab the session cookie + CSRF token."""
    global CSRF_TOKEN
    print("  Visiting homepage to get session + CSRF token…")
    r = SESSION.get(BASE + "/", timeout=15, headers={
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    r.raise_for_status()

    # Try to find CSRF token in the HTML
    # Common patterns: <meta name="csrf-token" content="...">, or a hidden input,
    # or a JS variable like csrfToken = "..."
    soup = BeautifulSoup(r.text, "lxml")

    token = None

    # 1. <meta name="csrf-token" content="...">
    meta = soup.find("meta", {"name": re.compile(r"csrf", re.I)})
    if meta:
        token = meta.get("content") or meta.get("value")

    # 2. <input type="hidden" name="__RequestVerificationToken" value="...">
    if not token:
        inp = soup.find("input", {"name": re.compile(r"csrf|token|verification", re.I)})
        if inp:
            token = inp.get("value")

    # 3. JS variable: var csrfToken = "..." or __csrf = "..."
    if not token:
        match = re.search(r'(?:csrf[_\-]?token|__csrf|csrfToken)\s*[=:]\s*["\']([a-f0-9]{20,})["\']',
                          r.text, re.I)
        if match:
            token = match.group(1)

    # 4. JS variable in a different format: token: "27b8ff..."
    if not token:
        match = re.search(r'["\']?token["\']?\s*:\s*["\']([a-f0-9]{20,})["\']', r.text, re.I)
        if match:
            token = match.group(1)

    if token:
        CSRF_TOKEN = token.strip()
        print(f"  ✓ CSRF token: {CSRF_TOKEN[:16]}…")
    else:
        print("  ⚠ Could not find CSRF token in HTML — will try without it")
        print(f"  Page snippet: {r.text[:500]}")

    print(f"  Cookies: {dict(SESSION.cookies)}")


def fetch(file_path):
    """Fetch one JSON file via the SecureJson handler."""
    url = f"{HANDLER}?file={file_path}"
    headers = {
        "User-Agent":       BROWSER_UA,
        "Accept":           "application/json, text/javascript, */*; q=0.01",
        "Accept-Language":  "en-US,en;q=0.9",
        "Referer":          BASE + "/",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua":        '"Not:A-Brand";v="99", "Brave";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }
    if CSRF_TOKEN:
        headers["x-csrf-token"] = CSRF_TOKEN

    for attempt in range(3):
        try:
            r = SESSION.get(url, headers=headers, timeout=15)
            if r.status_code == 403:
                print(f"  HTTP 403 — {file_path}")
                return None
            r.raise_for_status()
            text = r.text.strip().lstrip('\ufeff')
            text = re.sub(r'^\w+\(', '', text).rstrip(')')  # strip JSONP if present
            return json.loads(text)
        except requests.RequestException as e:
            print(f"  [retry {attempt+1}/3] {e}")
            time.sleep(2 * (attempt + 1))
        except json.JSONDecodeError:
            print(f"  JSON error for {file_path} — raw: {r.text[:200]}")
            return None
    return None


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_parties(data):
    if not data:
        return []
    rows = data if isinstance(data, list) else data.get("data", data.get("rows", []))
    out = []
    for item in rows:
        pid  = str(item.get("PartyID",      item.get("partyId",   "")))
        name = str(item.get("PartyName",     item.get("partyName", pid)))
        fptp = (int(item.get("FPTPWon",     item.get("Won",      0)) or 0) +
                int(item.get("FPTPLeading", item.get("Leading",  0)) or 0))
        pr   =  int(item.get("PRSeats",     item.get("PrSeats",  0)) or 0)
        out.append({
            "id": pid, "name": name,
            "color": PARTY_COLORS.get(pid, "#888"),
            "fptp": fptp, "pr": pr, "total": fptp + pr,
        })
    return sorted(out, key=lambda p: p["total"], reverse=True)


def parse_fptp(data):
    if not data:
        return []
    rows = data if isinstance(data, list) else data.get("data", data.get("rows", []))
    seats = {}
    for row in rows:
        num = int(row.get("ConstituentNo", row.get("constituentNo", 0)) or 0)
        if not num:
            continue
        prov   = PROVINCE_MAP.get(str(row.get("StateNo", row.get("stateNo", ""))), "")
        status = "declared" if str(row.get("EStatus", row.get("eStatus", ""))).upper() in (
            "E", "W", "ELECTED", "DECLARED", "WON") else "counting"
        reported = int(row.get("CountedPercent", row.get("countedPercent", 0)) or 0)
        pid  = str(row.get("PartyID", row.get("partyId", "")))
        cand = {
            "name":       row.get("CandidateName",  row.get("candidateName",  "")),
            "party_id":   pid,
            "party_name": row.get("PartyName",      row.get("partyName",      "")),
            "color":      PARTY_COLORS.get(pid, "#888"),
            "votes":      int(row.get("TotalVotes", row.get("totalVotes", 0)) or 0),
            "img":        row.get("PhotoPath",      row.get("photoPath",      None)),
        }
        if num not in seats:
            seats[num] = {
                "num": num,
                "name":     row.get("ConstituentName", row.get("constituentName", f"Constituency {num}")),
                "district": row.get("DistrictName",    row.get("districtName",    "")),
                "province": prov, "status": status,
                "reported": min(reported, 100), "candidates": [],
            }
        seats[num]["candidates"].append(cand)

    result = list(seats.values())
    for c in result:
        c["candidates"].sort(key=lambda x: x["votes"], reverse=True)
    return sorted(result, key=lambda c: c["num"])


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting scrape…")
    init_session()

    print("  Fetching party data…")
    party_data = None
    for path in [
        f"{PREFIX}/Common/HoRPartyTop5.txt",
        f"{PREFIX}/Common/HoRPartySummary.txt",
        f"{PREFIX}/Common/PartySummary.txt",
    ]:
        party_data = fetch(path)
        if party_data:
            print(f"  ✓ from {path}")
            break
    parties = parse_parties(party_data)
    print(f"  → {len(parties)} parties")

    print("  Fetching FPTP summary…")
    fptp_data = None
    for path in [
        f"{PREFIX}/FPTP/HoRFPTPSummary.txt",
        f"{PREFIX}/FPTP/FPTPSummary.txt",
        f"{PREFIX}/Common/HoRFPTPSummary.txt",
    ]:
        fptp_data = fetch(path)
        if fptp_data:
            print(f"  ✓ from {path}")
            break
    constituencies = parse_fptp(fptp_data)
    print(f"  → {len(constituencies)} constituencies")

    declared = sum(1 for c in constituencies if c["status"] == "declared")
    output = {
        "updated_at":     datetime.now(timezone.utc).isoformat(),
        "declared":       declared,
        "counting":       len(constituencies) - declared,
        "total":          len(constituencies),
        "party_seats":    parties,
        "constituencies": constituencies,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ Saved {OUTPUT}  ({len(constituencies)} constituencies, {declared} declared)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", type=int, metavar="SECONDS")
    args = parser.parse_args()
    if args.watch:
        print(f"Watch mode — every {args.watch}s. Ctrl+C to stop.")
        while True:
            try: run()
            except Exception as e: print(f"  Error: {e}")
            print(f"  Sleeping {args.watch}s…"); time.sleep(args.watch)
    else:
        run()