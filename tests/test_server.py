import json
import os
import tempfile
import unittest
from pathlib import Path

with tempfile.TemporaryDirectory() as initial_dir:
    os.environ["CLOUD_LAB_DB"] = str(Path(initial_dir) / "runs.db")
    import server

class CloudLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); server.DB_PATH = Path(cls.temp.name) / "runs.db"; server.initialize()
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_catalog_depth_and_unique_ids(self):
        self.assertEqual(len(server.CATALOG["exercises"]),30); self.assertEqual(len(server.CATALOG["incidents"]),30)
        self.assertEqual(len({item["id"] for item in server.CATALOG["exercises"]}),30); self.assertGreaterEqual(len({item["track"] for item in server.CATALOG["exercises"]}),7)
    def test_filter_and_persist_run(self):
        self.assertTrue(all(item["track"]=="Identity" for item in server.list_labs(track="Identity")))
        run=server.create_run({"labId":"LAB-10","operator":"Paul Revanth","status":"Validated","evidence":"New credential authenticated; previous credential revoked"})
        self.assertEqual(run["status"],"Validated"); self.assertEqual(server.list_runs()[0]["lab_id"],"LAB-10")
    def test_invalid_lab_is_rejected(self):
        with self.assertRaises(ValueError): server.create_run({"labId":"LAB-99","operator":"P"})

if __name__ == "__main__": unittest.main()
