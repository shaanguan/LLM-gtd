#!/usr/bin/env python3
"""Local refresh endpoint for Dashboard.html.

Runs export_dashboard.py on localhost request so the static Dashboard can
trigger a vault rescan without browser filesystem permissions.
"""

from __future__ import annotations

import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from _config import get_vault

HOST = "127.0.0.1"
PORT = 8765


class RefreshHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing a single refresh endpoint."""

    def do_OPTIONS(self) -> None:
        self._send_response(204, {})

    def do_GET(self) -> None:
        if self.path in ("/health", "/health/"):
            self._send_response(200, {"ok": True})
            return

        if self.path not in ("/refresh", "/refresh/"):
            self._send_response(404, {"ok": False, "error": "not found"})
            return

        vault_path = get_vault()
        export_script_path = vault_path / "export_dashboard.py"
        if not export_script_path.exists():
            self._send_response(
                500,
                {"ok": False, "error": f"missing {export_script_path.name}"},
            )
            return

        result = subprocess.run(
            ["python3", str(export_script_path)],
            cwd=str(vault_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            self._send_response(
                500,
                {
                    "ok": False,
                    "error": result.stderr.strip() or result.stdout.strip(),
                },
            )
            return

        self._send_response(200, {"ok": True, "output": result.stdout.strip()})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_response(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    get_vault()
    server = ThreadingHTTPServer((HOST, PORT), RefreshHandler)
    print(f"[dashboard_refresh_server] listening on http://{HOST}:{PORT}/refresh")
    server.serve_forever()


if __name__ == "__main__":
    main()
