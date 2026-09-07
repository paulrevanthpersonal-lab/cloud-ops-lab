"""Exercise the public HTTP boundary with synthetic files, never real evidence."""

import contextlib
import io
import json
import shutil
import tempfile
import threading
import unittest
from http.client import HTTPConnection, RemoteDisconnected
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import server


class QuietHandler(server.Handler):
    def log_message(self, *_args):
        pass


class HttpBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "site"
        cls.root.mkdir()
        # Copy the actual public assets so regressions cannot hide behind mocks.
        for name in ("dashboard", "docs", "runbooks"):
            shutil.copytree(server.ROOT / name, cls.root / name)
        shutil.copy(server.ROOT / "index.html", cls.root / "index.html")
        (cls.root / "data").mkdir()
        shutil.copy(server.ROOT / "data/labs.json", cls.root / "data/labs.json")
        for name in (".env", ".git/config", "server.py", "infra/main.tf",
                     "evidence/probe.txt", "data/runtime/probe.json",
                     "dashboard/private.txt", "docs/private.txt"):
            path = cls.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic private fixture")
        (cls.root / "dashboard/leak.js").symlink_to(cls.root / ".env")
        outside = Path(cls.temp.name) / "outside.js"
        outside.write_text("synthetic outside fixture")
        (cls.root / "dashboard/outside.js").symlink_to(outside)
        (cls.root / "docs/linked").symlink_to(cls.root / "runbooks", target_is_directory=True)
        cls.root_patch = patch.object(server, "ROOT", cls.root)
        cls.db_patch = patch.object(server, "DB_PATH", cls.root / "data/runs.db")
        cls.root_patch.start()
        cls.db_patch.start()
        server.initialize()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)
        cls.db_patch.stop()
        cls.root_patch.stop()
        cls.temp.cleanup()

    def request(self, path, method="GET", body=None):
        connection = HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            connection.request(method, path, body=body)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_public_assets_and_runbooks_remain_available(self):
        for path in ("/", "/index.html", "/dashboard/", "/dashboard/index.html",
                     "/dashboard/app.js", "/dashboard/styles.css", "/data/labs.json",
                     "/docs/API.md", "/docs/screenshots/operations-dashboard.png",
                     "/runbooks/dns.md"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertTrue(body)
                head_status, head_headers, head_body = self.request(path, "HEAD")
                self.assertEqual(head_status, 200)
                self.assertEqual(head_headers["Content-Length"], headers["Content-Length"])
                self.assertEqual(head_body, b"")

    def test_dashboard_directory_redirect_preserves_relative_assets(self):
        status, headers, _ = self.request("/dashboard")
        self.assertEqual(status, 301)
        self.assertEqual(headers["Location"], "/dashboard/")

    def test_private_files_and_directory_listings_are_not_public(self):
        for path in ("/.env", "/.git/config", "/server.py", "/infra/main.tf",
                     "/evidence/probe.txt", "/data/runs.db", "/data/runtime/probe.json",
                     "/dashboard/private.txt", "/docs/private.txt",
                     "/data/", "/docs/", "/runbooks/", "/.git/"):
            for method in ("GET", "HEAD"):
                with self.subTest(path=path, method=method):
                    status, _, body = self.request(path, method)
                    self.assertEqual(status, 404)
                    self.assertNotIn(b"synthetic private fixture", body)

    def test_encoded_and_traversal_paths_cannot_reach_private_files(self):
        for path in ("/%2eenv", "/%2egit/config", "/dashboard/../.env",
                     "/dashboard/%2e%2e/.env", "/dashboard/%2e%2e%2f.env",
                     "/dashboard/..%5c.env", "/dashboard/%00app.js"):
            for method in ("GET", "HEAD"):
                with self.subTest(path=path, method=method):
                    # Normalize disconnects into a failed contract assertion.
                    with contextlib.redirect_stderr(io.StringIO()):
                        try:
                            status, _, _ = self.request(path, method)
                        except RemoteDisconnected:
                            status = None
                    self.assertEqual(status, 404)

    def test_symlinks_do_not_bypass_the_public_file_boundary(self):
        for path in ("/dashboard/leak.js", "/dashboard/outside.js", "/docs/linked/dns.md"):
            for method in ("GET", "HEAD"):
                with self.subTest(path=path, method=method):
                    self.assertEqual(self.request(path, method)[0], 404)

    def test_unknown_api_routes_have_a_json_404(self):
        for path in ("/api/voltage", "/api/not-a-route"):
            with self.subTest(path=path):
                with contextlib.redirect_stderr(io.StringIO()):
                    try:
                        response = self.request(path)
                    except RemoteDisconnected:
                        response = (None, {}, b"")
                status, headers, body = response
                self.assertEqual(status, 404)
                self.assertIn("application/json", headers["Content-Type"])
                self.assertIn("error", json.loads(body))

    def test_catalog_filter_and_run_persistence_still_work_over_http(self):
        status, _, body = self.request("/api/labs?track=Identity")
        self.assertEqual(status, 200)
        labs = json.loads(body)
        self.assertTrue(labs)
        self.assertTrue(all(lab["track"] == "Identity" for lab in labs))
        payload = json.dumps({"labId": "LAB-10", "operator": "Test operator",
                              "status": "Validated", "evidence": "Synthetic recovery check"})
        status, _, body = self.request("/api/runs", "POST", payload)
        self.assertEqual(status, 201)
        run = json.loads(body)
        self.assertEqual(run["status"], "Validated")
        self.assertEqual(json.loads(self.request("/api/runs")[2])[0]["id"], run["id"])


if __name__ == "__main__":
    unittest.main()
