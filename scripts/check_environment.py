"""Kiểm tra trước khi chạy, không tải mạng và không sửa dữ liệu."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT, mode="dashboard"):
    errors = []
    if sys.version_info < (3, 10):
        errors.append("Can Python >= 3.10; khuyen nghi Python 3.11.")

    def read(rel):
        path = root / rel
        if not path.is_file():
            errors.append(f"Thieu {rel}")
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"Khong doc duoc {rel}: {exc}")
            return None

    if mode == "dashboard":
        for rel in ("prototype/index.html", "prototype/app.js", "prototype/style.css"):
            if not (root / rel).is_file():
                errors.append(f"Thieu {rel}")
        reports = read("prototype/data/results.json")
        facts = read("prototype/data/facts.json")
        metrics = read("prototype/data/metrics.json")
        examples = read("prototype/data/examples.json")
        files = read("prototype/data/py_files.json")
        if not isinstance(reports, list) or not reports:
            errors.append("results.json phai la danh sach bao cao khong rong.")
        if not isinstance(facts, dict) or not facts:
            errors.append("facts.json phai co so lieu cho kiem tra truc tiep.")
        if not isinstance(metrics, dict) or not isinstance(metrics.get("pipeline"), dict):
            errors.append("metrics.json thieu thong ke pipeline.")
        elif isinstance(reports, list):
            try:
                counts = {}
                for r in reports:
                    for c in r["claims"]:
                        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
                p = metrics["pipeline"]
                if (p["reports"] != len(reports) or p["claims_now"] != sum(counts.values())
                        or any(p["verdicts_now"].get(k) != v for k, v in counts.items())):
                    errors.append("So lieu metrics.json khong khop results.json.")
                if isinstance(facts, dict) and any(f"{r['ticker']}_{r['year']}" not in facts for r in reports):
                    errors.append("Thieu facts cua mot so bao cao.")
            except (KeyError, TypeError):
                errors.append("Cau truc results/metrics khong hop le.")
        if not isinstance(examples, list):
            errors.append("examples.json phai la danh sach.")
        if not isinstance(files, list) or not files:
            errors.append("py_files.json phai liet ke ma nguon Python.")
        else:
            for rel in files:
                if not isinstance(rel, str) or not rel.startswith("smartaudit/") or ".." in Path(rel).parts:
                    errors.append("Duong dan Python khong hop le trong py_files.json.")
                    continue
                src, copy = root / rel, root / "prototype/py" / rel
                if not copy.is_file():
                    errors.append(f"Thieu prototype/py/{rel}")
                elif src.is_file() and src.read_bytes() != copy.read_bytes():
                    errors.append(f"Ban Pyodide lech ma nguon: {rel}; chay export_dashboard.py.")
    elif mode == "sample":
        if importlib.util.find_spec("yaml") is None:
            errors.append("Thieu PyYAML: python -m pip install -r requirements-sample.txt")
        manifest = read("sample_data/manifest.json")
        narratives = read("sample_data/narratives.json")
        if not isinstance(narratives, list) or not narratives:
            errors.append("Thieu trich doan BCTN mau.")
        if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
            errors.append("manifest.json khong hop le.")
        elif not manifest["files"]:
            errors.append("manifest.json khong co checksum.")
        else:
            for entry in manifest.get("files", []):
                if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry.get("sha256"):
                    errors.append("Dong manifest khong hop le.")
                    continue
                rel = entry["path"]
                if not rel.startswith("sample_data/") or ".." in Path(rel).parts:
                    continue
                path = root / rel
                if not path.is_file():
                    errors.append(f"Thieu {rel}")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                    errors.append(f"Sai checksum {rel}")
        if len(list((root / "sample_data/tinix/ocr_results").rglob("*_extracted.txt"))) != 2:
            errors.append("Bo mau phai co hai BCTC OCR TiniX.")
    else:
        for module, package in (("yaml", "PyYAML"), ("rapidfuzz", "rapidfuzz"),
                                ("pdfplumber", "pdfplumber"), ("requests", "requests")):
            if importlib.util.find_spec(module) is None:
                errors.append(f"Thieu {package}: python -m pip install -r requirements-lock.txt")
        if not list((root / "data/raw/tinix/ocr_results").glob("*/*/**/*_extracted.txt")):
            errors.append("Thieu du lieu TiniX day du: python scripts/fetch_data.py")
        if not (list((root / "data/interim/bctn_text").rglob("*_col-60.txt"))
                or list((root / "data/raw/bctn").rglob("*_BCTN_*.pdf"))):
            errors.append("Thieu BCTN: python scripts/fetch_narrative.py")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dashboard", "sample", "pipeline"), default="dashboard")
    args = parser.parse_args()
    errors = check(mode=args.mode)
    for error in errors:
        print(f"[LOI] {error}")
    if errors:
        print("Xem README.md. Dashboard va mau nho da kem Git; bo du lieu day du tai rieng.")
        return 1
    print(f"[OK] {args.mode}")
    if args.mode == "dashboard":
        print("Kiem tra truc tiep can mang tai Pyodide lan dau tu cdn.jsdelivr.net.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
