"""
scraper.py — Nepal Election 2082 scraper
Scrapes result.election.gov.np and writes output/data.json

Usage:
    python scraper.py              # run once
    python scraper.py --watch 60   # re-run every 60 seconds
"""

import json
import time
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────

BASE   = "https://result.election.gov.np"
OUTPUT = Path("output/data.json")

PARTY_COLORS = {
    "CPN-UML": "#C0392B",
    "NC":       "#2563C4",
    "RSP":      "#1A7D52",
    "CPN-MC":   "#7B3FA0",
    "RPP":      "#C07820",
    "LSP":      "#E85A20",
    "IND":      "#4A5568",
}

# Nepali party name → short id
PARTY_IDS = {
    "नेकपा एमाले":                   "CPN-UML",
    "नेपाली काँग्रेस":               "NC",
    "राष्ट्रिय स्वतन्त्र पार्टी":    "RSP",
    "नेकपा (माओवादी केन्द्र)":       "CPN-MC",
    "राष्ट्रिय प्रजातन्त्र पार्टी":  "RPP",
    "लोकतान्त्रिक समाजवादी पार्टी":  "LSP",
    "स्वतन्त्र":                      "IND",
}

PROVINCE_NAMES = {
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
    "User-Agent": "Mozilla/5.0 (compatible; NepalElectionScraper/1.0)",
    "Accept-Language": "ne,en;q=0.9",
})


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get(url):
    """Simple GET with 3 retries."""
    for i in range(3):
        try:
            r = SESSION.get(url, timeout=12)
            r.raise_for_status()
            r.encoding = "utf-8"
            return BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"  [retry {i+1}/3] {url} — {e}")
            time.sleep(2 * (i + 1))
    return None


def clean(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def to_int(text):
    digits = re.sub(r"[^\d]", "", (text or ""))
    return int(digits) if digits else 0


def party_id(name):
    name = clean(name)
    for np, pid in PARTY_IDS.items():
        if np in name:
            return pid
    # fallback: return first 8 chars as-is
    return name[:8] or "OTH"


# ── SCRAPE PARTY SEAT SUMMARY ─────────────────────────────────────────────────

def scrape_party_seats(soup):
    """
    Pull the party seat totals from the main results page.
    Returns list of:
      { id, name, color, fptp, pr, total }
    """
    parties = []

    # Try common table selectors the ECN site uses
    rows = soup.select(
        "table.party-result tbody tr, "
        "#partyResult tbody tr, "
        ".party-seats tr, "
        "table tbody tr"
    )

    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue
        name_text = clean(cells[0].get_text())
        if not name_text or name_text.lower() in ("party", "दल", "s.n.", "#", ""):
            continue
        pid   = party_id(name_text)
        fptp  = to_int(cells[1].get_text())
        pr    = to_int(cells[2].get_text()) if len(cells) > 2 else 0
        total = to_int(cells[3].get_text()) if len(cells) > 3 else fptp + pr
        parties.append({
            "id":    pid,
            "name":  name_text,
            "color": PARTY_COLORS.get(pid, "#888888"),
            "fptp":  fptp,
            "pr":    pr,
            "total": total or fptp + pr,
        })

    return sorted(parties, key=lambda p: p["total"], reverse=True)


# ── SCRAPE ONE CONSTITUENCY PAGE ──────────────────────────────────────────────

def scrape_constituency(num, name="", district="", province=""):
    """
    Fetch a single constituency result page and return:
    {
      num, name, district, province, status, reported,
      candidates: [ { name, party_id, party_name, color, votes }, ... ]
    }
    """
    url  = f"{BASE}/fptp/{num}"
    soup = get(url)
    if not soup:
        return None

    # Page title / constituency name
    title_el = soup.select_one("h1, h2, .title, .constituency-name")
    page_name = clean(title_el.get_text()) if title_el else name or f"Constituency {num}"

    # Status
    status_el = soup.select_one(".status, .result-status, .badge, [data-status]")
    status_text = clean(status_el.get_text()).lower() if status_el else ""
    status = "declared" if any(w in status_text for w in ["declared", "घोषणा", "निर्वाचित"]) else "counting"

    # Reported %
    pct_el = soup.select_one(".progress-value, .counted, [data-counted], .percent")
    reported = to_int(pct_el.get_text()) if pct_el else 0

    # Candidates table
    candidates = []
    for row in soup.select("table tbody tr, .candidate-row"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue
        # Try to find name, party, votes in cells
        cname = clean(cells[1].get_text() if len(cells) > 1 else cells[0].get_text())
        if not cname:
            continue
        party_name = clean(cells[2].get_text() if len(cells) > 2 else "")
        votes_text = clean(cells[-1].get_text())
        pid   = party_id(party_name)
        votes = to_int(votes_text)
        # candidate photo
        img_el = row.select_one("img")
        img = img_el["src"].split("/")[-1] if img_el and img_el.get("src") else None
        candidates.append({
            "name":       cname,
            "party_id":   pid,
            "party_name": party_name,
            "color":      PARTY_COLORS.get(pid, "#888888"),
            "votes":      votes,
            "img":        img,
        })

    candidates.sort(key=lambda c: c["votes"], reverse=True)

    return {
        "num":        num,
        "name":       page_name,
        "district":   district,
        "province":   province,
        "status":     status,
        "reported":   min(reported, 100),
        "candidates": candidates,
    }


# ── SCRAPE ALL CONSTITUENCIES LIST ────────────────────────────────────────────

def scrape_list():
    """
    Fetch the main FPTP page, find all 165 constituency links.
    Returns [ { num, name, district, province, url }, ... ]
    """
    soup = get(f"{BASE}/fptp")
    if not soup:
        return []

    items = []
    # ECN site usually has a table or list with links to each constituency
    for a in soup.select("a[href*='/fptp/']"):
        href = a.get("href", "")
        m = re.search(r"/fptp/(\d+)", href)
        if not m:
            continue
        num  = int(m.group(1))
        name = clean(a.get_text())
        # Try to find province from parent row
        row  = a.find_parent("tr")
        prov_num = (row or a).get("data-province", "") if row else ""
        province = PROVINCE_NAMES.get(str(prov_num), "")
        district = ""
        if row:
            cells = row.find_all(["td", "th"])
            district = clean(cells[2].get_text()) if len(cells) > 2 else ""
        items.append({
            "num":      num,
            "name":     name,
            "district": district,
            "province": province,
            "url":      BASE + href,
        })

    # Deduplicate by num
    seen = set()
    unique = []
    for c in items:
        if c["num"] not in seen:
            seen.add(c["num"])
            unique.append(c)

    return sorted(unique, key=lambda c: c["num"])


# ── MAIN SCRAPE ───────────────────────────────────────────────────────────────

def run():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting scrape…")

    # 1. Get the main page for party seat summary
    main_soup = get(f"{BASE}/fptp")
    party_seats = scrape_party_seats(main_soup) if main_soup else []
    print(f"  Party seats: {len(party_seats)} parties found")

    # 2. Get constituency list
    const_list = scrape_list()
    print(f"  Constituency list: {len(const_list)} found")

    # 3. Scrape each constituency detail page
    constituencies = []
    for i, c in enumerate(const_list, 1):
        print(f"  [{i}/{len(const_list)}] {c['name']} (#{c['num']})…", end=" ")
        detail = scrape_constituency(c["num"], c["name"], c["district"], c["province"])
        if detail:
            constituencies.append(detail)
            print(f"✓  {len(detail['candidates'])} candidates")
        else:
            print("✗  failed")

    # 4. Count totals
    declared = sum(1 for c in constituencies if c["status"] == "declared")
    counting = sum(1 for c in constituencies if c["status"] == "counting")

    # 5. Build output
    output = {
        "updated_at":     datetime.now(timezone.utc).isoformat(),
        "declared":       declared,
        "counting":       counting,
        "total":          len(constituencies),
        "party_seats":    party_seats,
        "constituencies": constituencies,
    }

    # 6. Write JSON
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ Saved {OUTPUT}  ({len(constituencies)} constituencies, {declared} declared)\n")


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
            print(f"Sleeping {args.watch}s…")
            time.sleep(args.watch)
    else:
        run()
