"""
GET /api/results
Returns the full election data — party seats + all constituencies.
The scraper writes scraper/output/data.json; this endpoint serves it.
"""

import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler

DATA_FILE = Path("scraper/output/data.json")


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    # Fallback: empty structure so the frontend doesn't break
    return {"updated_at": None, "declared": 0, "counting": 0, "total": 0, "party_seats": [], "constituencies": []}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = load()
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(body)
