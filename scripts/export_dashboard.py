"""Xuất kết quả thật của pipeline thành dữ liệu tĩnh cho dashboard.

Dashboard (``prototype/``) là trang tĩnh, không cần server:

* ``prototype/data/results.json``  — mọi khẳng định đã đối chiếu, theo (mã, năm)
* ``prototype/data/facts.json``    — số liệu BCTC đã bóc, theo (mã, năm), để
  chức năng "Kiểm tra khẳng định" chạy lõi đối chiếu ngay trong trình duyệt
* ``prototype/data/metrics.json``  — số đo đánh giá (nhãn, chèn lỗi, lượng tử)
* ``prototype/py/smartaudit/...``  — bản sao **đúng mã nguồn lõi** của pipeline,
  để Pyodide (Python chạy trên WebAssembly) nạp và chạy trong trình duyệt

Không có dữ liệu mô phỏng nào: mọi con số đều sinh từ các tệp trong ``results/``.

Chạy (sau run_nnc.py, make_injected_set.py, evaluate.py, run_qka.py):
    python scripts/export_dashboard.py
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import RESULTS, ROOT, TICKERS  # noqa: E402
from smartaudit.eval import load_financials  # noqa: E402

OUT = ROOT / "prototype" / "data"
PY_OUT = ROOT / "prototype" / "py"

#: Các tệp mã nguồn lõi cần cho "Kiểm tra khẳng định" trong trình duyệt.
#: Chỉ dùng thư viện chuẩn của Python — không cần cài gói nào trong Pyodide.
CORE_FILES = [
    "smartaudit/__init__.py",
    "smartaudit/config.py",
    "smartaudit/ingest/__init__.py",
    "smartaudit/ingest/tinix.py",
    "smartaudit/ingest/vietstock.py",
    "smartaudit/nlp/__init__.py",
    "smartaudit/nlp/claims.py",
    "smartaudit/nnc/__init__.py",
    "smartaudit/nnc/checker.py",
    "smartaudit/tables/__init__.py",
    "smartaudit/tables/parser.py",
    "smartaudit/ontology/__init__.py",
    "smartaudit/ontology/vas.py",
]

SECTORS = {
    "VNM": "Thực phẩm & đồ uống", "MSN": "Hàng tiêu dùng", "FPT": "Công nghệ",
    "VIC": "Bất động sản", "VHM": "Bất động sản", "GAS": "Năng lượng", "PLX": "Năng lượng",
    "POW": "Điện", "PC1": "Xây lắp điện", "HPG": "Thép", "MWG": "Bán lẻ",
    "VCG": "Xây dựng", "HAG": "Nông nghiệp", "MBB": "Ngân hàng", "TCB": "Ngân hàng",
    "VPB": "Ngân hàng",
}
BANKS = {"MBB", "TCB", "VPB"}


def _load(name: str) -> dict | list | None:
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _verdict_counts(claims: list[dict]) -> dict[str, int]:
    out = {"nhất quán": 0, "mâu thuẫn": 0, "không kiểm chứng được": 0}
    for c in claims:
        out[c["verdict"]] = out.get(c["verdict"], 0) + 1
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results = _load("nnc_results.json") or []
    baseline = _load("nnc_results_baseline_20260921.json") or []

    # ── Kết quả theo báo cáo ──
    reports = []
    for rep in results:
        reports.append({
            "ticker": rep["ticker"], "year": rep["year"],
            "sector": SECTORS.get(rep["ticker"], ""),
            "bank": rep["ticker"] in BANKS,
            "score": rep["nnc_score"],
            "counts": _verdict_counts(rep["claims"]),
            "claims": rep["claims"],
        })
    (OUT / "results.json").write_text(json.dumps(reports, ensure_ascii=False), encoding="utf-8")

    # ── Số liệu BCTC cho kiểm tra trực tiếp ──
    keys = {(r["ticker"], r["year"]) for r in results}
    _, facts_by_key, names = load_financials(TICKERS, keys)
    facts_out = {}
    for (ticker, year), facts in sorted(facts_by_key.items()):
        facts_out[f"{ticker}_{year}"] = {
            "source": names[(ticker, year)],
            "facts": {
                k: {
                    "concept": f.concept, "current": f.current, "previous": f.previous,
                    "page": f.page, "code": f.code, "label": f.label,
                    "statement": f.statement.value, "unit": f.unit.value,
                }
                for k, f in facts.items()
            },
        }
    (OUT / "facts.json").write_text(json.dumps(facts_out, ensure_ascii=False), encoding="utf-8")

    # ── Số đo ──
    all_now = [c for r in results for c in r["claims"]]
    all_before = [c for r in baseline for c in r["claims"]]
    metrics = {
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "pipeline": {
            "reports": len(results),
            "companies": len({r["ticker"] for r in results}),
            "claims_now": len(all_now),
            "claims_before": len(all_before),
            "verdicts_now": _verdict_counts(all_now),
            "verdicts_before": _verdict_counts(all_before),
            "reports_before": len(baseline),
        },
        "evaluation": _load("eval_summary.json"),
        "injected": _load("injected_eval.json"),
        "quantum": None,
    }
    if (qka := _load("qka_results.json")) is not None:
        metrics["quantum"] = {
            "methods": {k: {m: v.get(m) for m in ("accuracy_mean", "accuracy_std", "macro_f1_mean",
                                                    "macro_f1_std", "train_seconds_mean")}
                        for k, v in qka["methods"].items()},
            "alignment": qka.get("alignment"),
            "dataset": {k: qka["dataset"].get(k) for k in ("n_samples", "n_rows", "n_classes")
                        if k in qka["dataset"]},
            "n_qubits": qka["config"].get("n_qubits"),
            "n_folds": qka["config"].get("n_folds"),
            "total_seconds": qka.get("total_seconds"),
        }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── Ví dụ cho ô kiểm tra trực tiếp: câu thật + câu chèn lỗi có ghi rõ ──
    examples = []
    for rep in results:
        for c in rep["claims"]:
            if c["verdict"] == "nhất quán" and len(examples) < 6 and len(c["text"]) < 160:
                examples.append({"ticker": rep["ticker"], "year": rep["year"], "text": c["text"],
                                 "kind": "Câu thật trong BCTN", "page": c["page"]})
    injected_csv = RESULTS / "injected_cases.csv"
    if injected_csv.exists():
        import csv
        seen = set()
        for row in csv.DictReader(open(injected_csv, encoding="utf-8-sig")):
            if (row["ky_vong"] == row["he_thong"] == "mâu thuẫn" and row["loai"] in ("gia_tri", "huong", "kiem_soat_chi_phi")
                    and row["loai"] not in seen and len(row["cau_chen_loi"]) < 160):
                seen.add(row["loai"])
                examples.append({"ticker": row["ma_ck"], "year": int(row["nam"]), "text": row["cau_chen_loi"],
                                 "kind": "Câu đã sửa có chủ đích (minh hoạ)", "original": row["cau_goc"]})
    (OUT / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── Mã nguồn lõi cho Pyodide ──
    if PY_OUT.exists():
        shutil.rmtree(PY_OUT)
    for rel in CORE_FILES:
        dst = PY_OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    (OUT / "py_files.json").write_text(json.dumps(CORE_FILES), encoding="utf-8")

    size = sum(p.stat().st_size for p in OUT.glob("*.json"))
    print(f"Đã xuất {len(reports)} báo cáo, {len(facts_out)} bộ số liệu, "
          f"{len(examples)} ví dụ → {OUT} ({size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
