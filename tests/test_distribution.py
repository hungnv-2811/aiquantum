"""Kiểm tra bản phân phối chạy được; dùng unittest để không cần pytest."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_environment import check
from scripts.run_sample import run
from smartaudit.ingest import iter_reports
from smartaudit.nnc import build_facts
from smartaudit.tables import extract_tables


class DistributionTests(unittest.TestCase):
    def test_dashboard_has_complete_consistent_snapshot(self):
        self.assertEqual(check(), [])

    def test_sample_checksums_and_dependencies(self):
        self.assertEqual(check(mode="sample"), [])

    def test_sample_pipeline_preserves_published_results(self):
        paths = list((ROOT / "results").glob("*.json"))
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in paths}
        result = run()
        self.assertEqual({(r["ticker"], r["year"]) for r in result["reports"]},
                         {("VNM", 2024), ("FPT", 2022)})
        for report in result["reports"]:
            self.assertEqual(len(report["claims"]), 2)
            self.assertTrue(all(c["evidence"] for c in report["claims"]))
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in paths})

    def test_real_sample_values(self):
        expected = {("VNM", 2024): 61782609528445, ("FPT", 2022): 44010128835000}
        for report in iter_reports(ROOT / "sample_data/tinix"):
            facts = build_facts(extract_tables(report.read()))
            self.assertAlmostEqual(facts["revenue_net"].current,
                                   expected[(report.ticker, report.year)], delta=1e9)

    def test_missing_assets_report_actionable_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = check(Path(tmp))
            self.assertTrue(any("prototype/data/facts.json" in e for e in errors))

    def test_inconsistent_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "prototype/data", root / "prototype/data")
            path = root / "prototype/data/metrics.json"
            metrics = json.loads(path.read_text(encoding="utf-8"))
            metrics["pipeline"]["reports"] += 1
            path.write_text(json.dumps(metrics), encoding="utf-8")
            self.assertTrue(any("khong khop" in e for e in check(root)))

    def test_modified_sample_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "sample_data", root / "sample_data")
            with next((root / "sample_data/tinix").rglob("*.txt")).open("ab") as fh:
                fh.write(b"tampered")
            self.assertTrue(any("checksum" in e for e in check(root, "sample")))


if __name__ == "__main__":
    unittest.main()
