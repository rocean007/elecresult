"""
GET /api/search?q=Kathmandu
Search constituencies by name, district, province, or candidate name.
Returns matching constituencies with their top candidates.
"""

import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

DATA_FILE = Path("scraper/output/data.json")


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        q = (params.get("q", [""])[0] or "").strip().lower()

        if not q:
            self._error(400, "Missing ?q= parameter.")
            return

        data = load()
        results = []

        for c in data.get("constituencies", []):
            # Match on constituency name, district, province, or any candidate name / party
            match = (
                q in c.get("name", "").lower() or
                q in c.get("district", "").lower() or
                q in c.get("province", "").lower() or
                str(c.get("num", "")) == q or
                any(
                    q in cand.get("name", "").lower() or
                    q in cand.get("party_id", "").lower() or
                    q in cand.get("party_name", "").lower()
                    for cand in c.get("candidates", [])
                )
            )
            if match:
                results.append(c)

        body = json.dumps({
            "query":   q,
            "count":   len(results),
            "results": results,
        }, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=30")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, code, message):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
