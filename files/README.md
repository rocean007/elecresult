# 🇳🇵 Nepal Election 2082 — Live Results Dashboard

Real-time election results dashboard for Nepal's House of Representatives (Pratinidhi Sabha) 2082, scraped live from [result.election.gov.np](https://result.election.gov.np).

## Project Structure

```
nepal-election-2082/
├── frontend/                    # Static site
│   ├── index.html               # Main dashboard
│   ├── images/
│   │   ├── candidates/          # Candidate photos (from scraper)
│   │   └── symbols/             # Party election symbols
│   └── assets/
│       ├── style.css            # All styles
│       └── app.js               # All frontend logic
│
├── api/                         # Vercel serverless functions (Python)
│   ├── _core.py                 # Shared scraping engine
│   ├── live-summary.py          # GET /api/live-summary
│   ├── party-seats.py           # GET /api/party-seats
│   ├── pr.py                    # GET /api/pr
│   ├── health.py                # GET /api/health
│   ├── search.py                # GET /api/search?q=
│   ├── constituency/[id].py     # GET /api/constituency/45
│   └── province/[name].py       # GET /api/province/Bagmati
│
├── scraper/                     # Standalone Python scraper
│   ├── main.py                  # CLI entry point
│   ├── scraper.py               # Sync requests + BeautifulSoup
│   ├── async_scraper.py         # Async aiohttp (165 seats concurrently)
│   ├── exporter.py              # JSON + CSV export
│   ├── image_downloader.py      # Async photo/symbol downloader
│   ├── config.py                # URLs, party map, province map
│   └── utils.py                 # Logging, retry, Devanagari helpers
│
├── vercel.json                  # Routing + CORS headers
├── requirements.txt             # Python deps
└── README.md
```

## Quick Start

### Deploy to Vercel

```bash
npm i -g vercel
vercel --prod
```

### Run the scraper locally

```bash
pip install -r requirements.txt

# Full async scrape of all 165 seats
python -m scraper.main --async

# Watch mode (re-scrape every 2 minutes)
python -m scraper.main --async --watch 120

# Single constituency
python -m scraper.main --constituency 81
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-summary` | Full snapshot — seats, parties, status |
| GET | `/api/party-seats` | FPTP + PR per party with hex colors |
| GET | `/api/pr` | Proportional representation data |
| GET | `/api/constituency/[id]` | Single constituency — all candidates + votes |
| GET | `/api/province/[name]` | All seats for a province |
| GET | `/api/search?q=Kathmandu` | Search by name, district, or candidate |
| GET | `/api/health` | Service health check |

### Sample Response

```json
{
  "updated_at": "2026-03-06T14:22:00Z",
  "parties": [
    { "id": "CPN-UML", "abbr": "UML", "fptp_won": 47, "pr_estimate": 30, "total": 77 }
  ],
  "declared": 12,
  "counting": 153,
  "total": 165
}
```

## Frontend Features

- **Global header search** — Type any constituency name, district, candidate, or party in the red top bar. Results appear as a dropdown with keyboard navigation (↑↓ Enter). Clicking opens a full constituency detail modal.
- **Constituency detail modal** — Tournament bracket format showing leader on top, challengers in a 2-column grid below.
- **Hot zones section search** — Inline filter bar to narrow the visible constituency cards by any text.
- **Province filter pills** — Filter cards by all 7 provinces.
- **Live seat bar** — Proportional seat distribution with 138-seat majority line.
- **Party standings** — Sidebar leaderboard with majority progress meter.
- Auto-refreshes every 60 seconds.

## Data Source

All data is scraped from the Election Commission of Nepal's official results portal: [result.election.gov.np](https://result.election.gov.np). This is an independent open-data dashboard.
