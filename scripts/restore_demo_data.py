"""Khôi phục snapshot công khai và mẫu TiniX; chỉ chạy khi cần tải lại dữ liệu."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://smartaudit-quantum.vercel.app"
REPO = "tinixai/ocr_annual_financials"
ASSETS = ("results.json", "facts.json", "metrics.json", "examples.json", "py_files.json")


def sample_narratives(stored):
    selected = []
    for ticker, year, page, prefix in (
        ("FPT", 2022, 52, "Doanh thu đạt 44.010"),
        ("FPT", 2022, 56, "Xây dựng các chương trình"),
        ("VNM", 2024, 35, "▪ HĐQT"),
        ("VNM", 2024, 35, "Lợi nhuân trước thuế"),
    ):
        report = next(r for r in stored if (r["ticker"], r["year"]) == (ticker, year))
        claim = next(c for c in report["claims"] if c["page"] == page and c["text"].startswith(prefix))
        selected.append({"ticker": ticker, "year": year, "page": page, "text": claim["text"],
                         "source": "results/nnc_results.json"})
    return selected


def fetch(url):
    with urlopen(url, timeout=90) as response:
        return response.read()


def main():
    # Tải và đối chiếu toàn bộ trước khi ghi, tránh trộn snapshot mới với kết quả cũ.
    assets = {name: fetch(f"{SITE}/data/{name}") for name in ASSETS}
    decoded = {name: json.loads(body) for name, body in assets.items()}
    stored = json.loads((ROOT / "results/nnc_results.json").read_text(encoding="utf-8"))
    signature = lambda reports: {(r["ticker"], r["year"]): r["claims"] for r in reports}
    if signature(stored) != signature(decoded["results.json"]):
        raise ValueError("Snapshot online khác results/nnc_results.json; dừng để tránh trộn phiên bản.")
    sys_keys = {f"{r['ticker']}_{r['year']}" for r in stored}
    if not sys_keys.issubset(decoded["facts.json"]):
        raise ValueError("Snapshot thiếu facts cho một số báo cáo.")
    revision = json.loads(fetch(f"https://huggingface.co/api/datasets/{REPO}"))["sha"]
    downloads = {}
    for ticker, year in (("VNM", 2024), ("FPT", 2022)):
        stem = f"{ticker}_Baocaotaichinh_{year}_Kiemtoan_Hopnhat"
        rel = f"ocr_results/{ticker}/{year}/{stem}/{stem}_extracted.txt"
        url = f"https://huggingface.co/datasets/{REPO}/resolve/{revision}/{quote(rel)}"
        body = fetch(url)
        if b"<table>" not in body:
            raise ValueError(f"Không có bảng HTML trong {rel}")
        downloads[f"sample_data/tinix/{rel}"] = (url, body)
    narratives = sample_narratives(stored)
    for name, body in assets.items():
        downloads[f"prototype/data/{name}"] = (f"{SITE}/data/{name}", body)
    records = []
    for rel, (url, body) in downloads.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        records.append({"path": rel, "url": url, "sha256": hashlib.sha256(body).hexdigest()})
    (ROOT / "sample_data/narratives.json").write_text(json.dumps(narratives, ensure_ascii=False, indent=2), encoding="utf-8")
    records.append({"path": "sample_data/narratives.json", "source": "results/nnc_results.json",
                    "sha256": hashlib.sha256((ROOT / "sample_data/narratives.json").read_bytes()).hexdigest()})
    (ROOT / "sample_data/manifest.json").write_text(json.dumps({"tinix_revision": revision, "files": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Restored {len(downloads)} files and 4 narrative excerpts.")


if __name__ == "__main__":
    main()
