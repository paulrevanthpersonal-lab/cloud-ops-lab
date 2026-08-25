from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / "data" / "labs.json").read_text())
DB_PATH = Path(os.getenv("CLOUD_LAB_DB", ROOT / "data" / "lab_runs.db"))

def initialize() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, lab_id TEXT NOT NULL, operator TEXT NOT NULL,
            status TEXT NOT NULL, evidence TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT
        )""")

def list_labs(query: str = "", track: str = "") -> list[dict]:
    result = CATALOG["exercises"]
    if query:
        q = query.lower(); result = [item for item in result if q in json.dumps(item).lower()]
    if track:
        result = [item for item in result if item["track"] == track]
    return result

def create_run(payload: dict) -> dict:
    lab = next((item for item in CATALOG["exercises"] if item["id"] == payload.get("labId")), None)
    if not lab or len(payload.get("operator", "").strip()) < 2:
        raise ValueError("Valid labId and operator are required")
    status = payload.get("status", "In progress")
    if status not in {"In progress", "Validated", "Blocked"}: raise ValueError("Invalid status")
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    evidence = payload.get("evidence", "Baseline captured; execution pending")[:1000]
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("INSERT INTO runs (lab_id,operator,status,evidence,started_at,completed_at) VALUES (?,?,?,?,?,?)", (lab["id"], payload["operator"].strip(), status, evidence, now, now if status == "Validated" else None))
        row = conn.execute("SELECT * FROM runs WHERE id=?", (cursor.lastrowid,)).fetchone()
    keys = ["id","lab_id","operator","status","evidence","started_at","completed_at"]
    return dict(zip(keys,row))

def list_runs() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 100")]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_json(self, status: int, payload: object) -> None:
        raw = json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        parsed = urlparse(self.path); query = parse_qs(parsed.query)
        if parsed.path == "/api/health": return self.send_json(200,{"status":"ok","exercises":len(CATALOG["exercises"]),"incidents":len(CATALOG["incidents"])})
        if parsed.path == "/api/labs": return self.send_json(200,list_labs(query.get("query",[""])[0],query.get("track",[""])[0]))
        if parsed.path == "/api/incidents": return self.send_json(200,CATALOG["incidents"])
        if parsed.path == "/api/voltage" : return seld.send_json(300,CATALOG["voltage"])
        if parsed.path == "/api/runs": return self.send_json(200,list_runs())
        if parsed.path == "/api/summary":
            runs = list_runs(); return self.send_json(200,{"exercises":30,"incidents":30,"runs":len(runs),"validated":sum(run["status"]=="Validated" for run in runs),"tracks":sorted({item["track"] for item in CATALOG["exercises"]})})
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path != "/api/runs": return self.send_json(404,{"error":"Route not found"})
        try:
            length = min(int(self.headers.get("Content-Length",0)),1_000_000); payload = json.loads(self.rfile.read(length) or b"{}"); self.send_json(201,create_run(payload))
        except (ValueError,json.JSONDecodeError) as error: self.send_json(422,{"error":str(error)})

def run(port: int = 8080) -> None:
    initialize(); print(f"Cloud Support Operations Lab http://localhost:{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()

if __name__ == "__main__": run(int(os.getenv("PORT","8080")))
