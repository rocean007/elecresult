"""
_core.py — Shared scraping engine for Nepal Election 2082
Scrapes result.election.gov.np and returns structured data.
"""

import re
import time
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_URL        = "https://result.election.gov.np"
FPTP_URL        = f"{BASE_URL}/fptp"
PR_URL          = f"{BASE_URL}/pr"
REQUEST_TIMEOUT = 12
RETRY_ATTEMPTS  = 3
RETRY_DELAY     = 2

PARTY_MAP = {
    "नेकपा (एकीकृत समाजवादी)":     {"id": "CPN-US",  "abbr": "UML-S",  "color": "#8B0000"},
    "नेकपा एमाले":                  {"id": "CPN-UML", "abbr": "UML",    "color": "#C0392B"},
    "नेपाली काँग्रेस":              {"id": "NC",      "abbr": "NC",     "color": "#2563C4"},
    "राष्ट्रिय स्वतन्त्र पार्टी":   {"id": "RSP",     "abbr": "RSP",    "color": "#1A7D52"},
    "नेकपा (माओवादी केन्द्र)":      {"id": "CPN-MC",  "abbr": "Maoist", "color": "#7B3FA0"},
    "राष्ट्रिय प्रजातन्त्र पार्टी": {"id": "RPP",     "abbr": "RPP",    "color": "#C07820"},
    "लोकतान्त्रिक समाजवादी पार्टी": {"id": "LSP",     "abbr": "LSP",    "color": "#E85A20"},
    "स्वतन्त्र":                     {"id": "IND",     "abbr": "IND",    "color": "#4A5568"},
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

logger = logging.getLogger(__name__)


# ── HTTP ──────────────────────────────────────────────────────────────────────
def _get(url: str, params: dict = None) -> Optional[BeautifulSoup]:
    """GET with retry, returns BeautifulSoup or None."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; NepalElectionBot/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ne,en;q=0.9",
    })
    for attempt in range(RETRY_ATTEMPTS):
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return BeautifulSoup(resp.text, "lxml")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1}/{RETRY_ATTEMPTS} failed for {url}: {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    logger.error(f"All attempts failed for {url}")
    return None


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _votes(text: str) -> int:
    """Parse vote count string (may contain commas or Devanagari digits)."""
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


def _normalize_party(name: str) -> dict:
    name = _clean(name)
    for np_name, info in PARTY_MAP.items():
        if np_name in name or name in np_name:
            return info
    return {"id": "OTH", "abbr": name[:6] or "OTH", "color": "#999999"}


# ── CONSTITUENCY LIST ─────────────────────────────────────────────────────────
def get_constituency_list() -> list[dict]:
    """
    Scrape the main FPTP page for all 165 constituency links and top-level data.
    Returns list of dicts: {id, num, name, district, province, status, reported, url}
    """
    soup = _get(FPTP_URL)
    if not soup:
        return []

    constituencies = []
    rows = soup.select("table.result-table tbody tr, .constituency-row, tr[data-id]")

    for row in rows:
        try:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            num_text = _clean(cells[0].get_text())
            num = int(re.sub(r"\D", "", num_text)) if re.sub(r"\D", "", num_text) else 0
            name = _clean(cells[1].get_text())
            district = _clean(cells[2].get_text()) if len(cells) > 2 else ""
            province_num = row.get("data-province", "")
            province = PROVINCE_MAP.get(province_num, "Unknown")
            link = row.select_one("a")
            href = link["href"] if link and link.get("href") else f"/fptp/{num}"
            status_el = row.select_one(".status, .badge, td:last-child")
            status_text = _clean(status_el.get_text()) if status_el else ""
            status = "declared" if any(w in status_text.lower() for w in ["declared", "घोषणा", "निर्वाचित"]) else "counting"
            reported_el = row.select_one(".progress, .percent, [data-reported]")
            reported = int(re.sub(r"\D", "", _clean(reported_el.get_text()))) if reported_el else 0
            constituencies.append({
                "id": f"CONST-{num:03d}",
                "num": num,
                "name": name,
                "district": district,
                "province": province,
                "status": status,
                "reported": min(reported, 100),
                "url": BASE_URL + href if not href.startswith("http") else href,
            })
        except Exception as e:
            logger.debug(f"Row parse error: {e}")
            continue

    return constituencies


# ── SINGLE CONSTITUENCY ───────────────────────────────────────────────────────
def get_constituency_detail(constituency_id: int) -> Optional[dict]:
    """
    Scrape full detail for one constituency: all candidates + votes.
    constituency_id = int (1–165)
    """
    url = f"{FPTP_URL}/{constituency_id}"
    soup = _get(url)
    if not soup:
        return None

    try:
        name_el = soup.select_one("h1, h2, .constituency-name, .title")
        name = _clean(name_el.get_text()) if name_el else f"Constituency {constituency_id}"

        meta_el = soup.select_one(".meta, .location, .breadcrumb")
        meta_text = _clean(meta_el.get_text()) if meta_el else ""
        district_match = re.search(r"जिल्ला[:\s]+([^\s,]+)", meta_text)
        district = _clean(district_match.group(1)) if district_match else ""

        status_el = soup.select_one(".status, .result-status, [data-status]")
        status_text = _clean(status_el.get_text()) if status_el else ""
        status = "declared" if any(w in status_text.lower() for w in ["declared", "घोषणा"]) else "counting"

        reported_el = soup.select_one(".progress-value, .counted-percent, [data-counted]")
        reported_text = _clean(reported_el.get_text()) if reported_el else "0"
        reported = int(re.sub(r"\D", "", reported_text) or "0")

        candidates = []
        candidate_rows = soup.select("table.candidates tbody tr, .candidate-row, .result-row")

        for row in candidate_rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            cand_name = _clean(cells[1].get_text() if len(cells) > 1 else cells[0].get_text())
            party_text = _clean(cells[2].get_text() if len(cells) > 2 else "")
            votes_text = _clean(cells[3].get_text() if len(cells) > 3 else cells[-1].get_text())
            party_info = _normalize_party(party_text)
            photo_el = row.select_one("img.candidate-photo, img.photo")
            photo = photo_el["src"].split("/")[-1] if photo_el and photo_el.get("src") else None
            votes = _votes(votes_text)
            if cand_name:
                candidates.append({
                    "name": cand_name,
                    "party": party_info["id"],
                    "party_abbr": party_info["abbr"],
                    "party_color": party_info["color"],
                    "votes": votes,
                    "img": photo,
                })

        candidates.sort(key=lambda c: c["votes"], reverse=True)

        return {
            "id": constituency_id,
            "name": name,
            "district": district,
            "status": status,
            "reported": min(reported, 100),
            "candidates": candidates,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error parsing constituency {constituency_id}: {e}")
        return None


# ── PARTY SEATS SUMMARY ───────────────────────────────────────────────────────
def get_party_seats() -> dict:
    """
    Scrape the main result page for aggregated party seat counts (FPTP won + leading).
    Returns: {parties: [...], declared: int, counting: int, total: int, updated_at: str}
    """
    soup = _get(FPTP_URL)
    if not soup:
        return {}

    party_data = {}
    total_declared = 0
    total_counting = 0

    # Try party summary table
    party_rows = soup.select(".party-summary tr, #party-table tr, table.party-seats tbody tr")
    for row in party_rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        party_name = _clean(cells[0].get_text())
        if not party_name or party_name.lower() in ("party", "दल", "#"):
            continue
        info = _normalize_party(party_name)
        fptp_won = _votes(cells[1].get_text() if len(cells) > 1 else "0")
        fptp_lead = _votes(cells[2].get_text() if len(cells) > 2 else "0")
        pr_est = _votes(cells[3].get_text() if len(cells) > 3 else "0")
        pid = info["id"]
        party_data[pid] = {
            "id": pid,
            "abbr": info["abbr"],
            "color": info["color"],
            "fptp_won": fptp_won,
            "fptp_leading": fptp_lead,
            "fptp_total": fptp_won + fptp_lead,
            "pr_estimate": pr_est,
            "total": fptp_won + fptp_lead + pr_est,
        }

    # Count status from constituency list
    for c in get_constituency_list():
        if c["status"] == "declared":
            total_declared += 1
        else:
            total_counting += 1

    return {
        "parties": sorted(party_data.values(), key=lambda p: p["total"], reverse=True),
        "declared": total_declared,
        "counting": total_counting,
        "total": 165,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── PR DATA ───────────────────────────────────────────────────────────────────
def get_pr_data() -> dict:
    """Scrape proportional representation results."""
    soup = _get(PR_URL)
    if not soup:
        return {}

    pr_parties = []
    rows = soup.select("table tbody tr, .pr-row")
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        party_name = _clean(cells[0].get_text())
        if not party_name or party_name.lower() in ("party", "दल"):
            continue
        info = _normalize_party(party_name)
        votes = _votes(cells[1].get_text() if len(cells) > 1 else "0")
        pct_text = _clean(cells[2].get_text()) if len(cells) > 2 else "0"
        pct = float(re.sub(r"[^\d.]", "", pct_text) or "0")
        seats = _votes(cells[3].get_text()) if len(cells) > 3 else 0
        pr_parties.append({
            "id": info["id"],
            "abbr": info["abbr"],
            "color": info["color"],
            "votes": votes,
            "percent": pct,
            "seats": seats,
        })

    return {
        "parties": sorted(pr_parties, key=lambda p: p["votes"], reverse=True),
        "total_seats": 110,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── LIVE SUMMARY ─────────────────────────────────────────────────────────────
def get_live_summary() -> dict:
    """Combine party seats + constituency list for a full live snapshot."""
    party_data = get_party_seats()
    constituencies = get_constituency_list()
    return {
        **party_data,
        "constituencies_sample": constituencies[:10],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── SEARCH ───────────────────────────────────────────────────────────────────
def search_constituencies(query: str) -> list[dict]:
    """Search across constituency names, districts, candidates."""
    if not query or len(query.strip()) < 1:
        return []
    q = query.strip().lower()
    results = []
    for c in get_constituency_list():
        if (q in c["name"].lower() or
            q in c["district"].lower() or
            q in c["province"].lower() or
            q in str(c["num"])):
            results.append(c)
    return results[:20]
