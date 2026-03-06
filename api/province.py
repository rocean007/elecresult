"""
GET /api/province?name=Bagmati
Returns all constituencies for a given province.
Valid names: Koshi, Madhesh, Bagmati, Gandaki, Lumbini, Karnali, Sudurpashchim
"""

import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

DATA_FILE = Path("scraper/output/data.json")

VALID = {"Koshi", "Madhesh", "Bagmati", "Gandaki", "Lumbini", "Karnali", "Sudurpashchim"}


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        name = (params.get("name", [""])[0] or "").strip()

        # Case-insensitive match
        match = next((v for v in VALID if v.lower() == name.lower()), None)
        if not match:
            self._error(400, f"Invalid province. Valid values: {', '.join(sorted(VALID))}")
            return

        data = load()
        results = [c for c in data.get("constituencies", []) if c.get("province") == match]

        body = json.dumps({
            "province": match,
            "count":    len(results),
            "results":  results,
        }, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, code, message):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
