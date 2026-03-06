"""
GET /api/constituency?id=45
Returns one constituency's full detail (all candidates + votes).
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
        id_param = params.get("id", [None])[0]

        if not id_param or not id_param.isdigit():
            self._error(400, "Missing or invalid ?id= parameter. Use a number 1–165.")
            return

        num = int(id_param)
        data = load()
        match = next((c for c in data.get("constituencies", []) if c["num"] == num), None)

        if not match:
            self._error(404, f"Constituency #{num} not found.")
            return

        body = json.dumps(match, ensure_ascii=False).encode("utf-8")
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
