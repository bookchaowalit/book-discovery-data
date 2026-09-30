from __future__ import annotations

import json
import unittest
from pathlib import Path

from discovery_data import api, config, store


class DiscoveryDataApiTests(unittest.TestCase):
    def test_optional_local_capture_directory(self) -> None:
        source = Path(
            config.PROJECT_ROOT.parent
            / "book-job-scraping"
            / "data"
            / "exported"
        )
        if not source.exists():
            self.skipTest(
                "Optional book-job-scraping/data/exported is unavailable; "
                "offline contract and capture-fixture tests still run"
            )
        self.assertTrue(source.is_dir())

    def test_contract_and_api_surface(self) -> None:
        self.assertEqual(config.REPO_NAME, "book-discovery-data")
        self.assertEqual(config.DOMAIN, "discovery")
        self.assertEqual(config.SCHEMA_VERSION, "discovery.v1")
        self.assertEqual(config.API_PORT, 8110)
        self.assertTrue(config.FREE_ONLY)
        self.assertFalse(config.ALLOW_REFRESH)
        api_text = Path(api.__file__).read_text(encoding="utf-8")
        for path in (
            "/healthz",
            "/v1/metadata",
            "/v1/records",
            "/v1/history",
            "/v1/refresh",
        ):
            self.assertIn(path, api_text)
        self.assertIn('data_status="forbidden"', api_text)

    def test_signal_item_preserves_attribution_and_lineage(self) -> None:
        item = store.signal_item_from_bronze(
            {
                "event_time": "2026-09-12T00:00:00Z",
                "source_record_id": "github_trending|example/repo",
                "ingest_run_id": "run-001",
                "raw_object_key": (
                    "landing/source=book-discovery-data/"
                    "batch-001/payload.csv"
                ),
                "payload_json": json.dumps(
                    {
                        "id": "github_trending|example/repo",
                        "signal_id": "example/repo",
                        "source": "github_trending",
                        "title": "Example repository",
                        "url": "https://github.com/example/repo",
                        "source_url": (
                            "https://api.github.com/search/repositories"
                        ),
                        "captured_at": "2026-09-12T00:00:00Z",
                        "capture_kind": "current_snapshot",
                        "attribution_required": True,
                    }
                ),
            }
        )
        self.assertEqual(item["signal_id"], "example/repo")
        self.assertEqual(item["title"], "Example repository")
        self.assertEqual(item["canonical_url"], "https://github.com/example/repo")
        self.assertTrue(item["attribution_required"])
        self.assertEqual(item["ingest_run_id"], "run-001")
        self.assertTrue(item["record_id"])


if __name__ == "__main__":
    unittest.main()
