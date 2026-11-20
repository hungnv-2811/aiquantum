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

#: Câu ví dụ cho ô "Kiểm tra khẳng định": (mã, năm, đầu câu). Chọn tay để
#: trải đều nhiều doanh nghiệp và câu đọc tự nhiên; câu nào không còn trong
#: kết quả thì bị bỏ qua, phần thiếu được bù bằng quy tắc mỗi mã một câu.
REAL_EXAMPLES = [
    ("HPG", 2023, "Vốn chủ sở hữu tăng 7%"),
    ("VNM", 2020, "Lợi nhuận ròng đạt 11.235"),
    ("MSN", 2020, "Tổng tài sản tăng 19,0%"),
    ("POW", 2022, "Lợi nhuận trước thuế toàn Tổng công ty đạt 2.809"),
]
#: Câu đã sửa sai (từ tập chèn lỗi): (loại, mức, mã, năm, đầu câu gốc).
INJECTED_EXAMPLES = [
    ("gia_tri", "+10%", "POW", 2022, "Lợi nhuận trước thuế toàn Tổng công ty"),
    ("phan_tram", "+5 điểm", "HPG", 2023, "Vốn chủ sở hữu tăng 7%"),
    ("huong", "đảo chiều", "VNM", 2020, "Lợi nhuận ròng đạt 11.235"),
    ("kiem_soat_chi_phi", None, "MSN", 2022, None),
]
#: Câu minh hoạ cho trang Đánh giá: một câu thật, ba cách sửa sai.
EVAL_EXAMPLE = ("VNM", 2020, "Lợi nhuận ròng đạt 11.235")


def _load(name: str) -> dict | list | None:
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _verdict_counts(claims: list[dict]) -> dict[str, int]:
    out = {"nhất quán": 0, "mâu thuẫn": 0, "không kiểm chứng được": 0}
    for c in claims:
        out[c["verdict"]] = out.get(c["verdict"], 0) + 1
    return out


def _missing_reports(have: set[tuple[str, int]]) -> dict[str, dict[str, str]]:
    """Lý do mỗi báo cáo thường niên đã tải nhưng không có trong kết quả.

    Đọc dòng "bỏ qua: …" trong ``results/run_nnc_log.txt`` (đầu ra của
    ``python scripts/run_nnc.py > results/run_nnc_log.txt``). Khi có log, PDF có
    mặt mà không bị bỏ qua và không có kết quả nghĩa là thiếu BCTC để ghép cặp;
    không có log thì chỉ ghi chung "không đối chiếu được".
    Trả về {"MÃ_NĂM": {"short": nhãn ngắn, "why": lý do đầy đủ}}.
    """
    import re
    from smartaudit.ingest.vietstock import BCTN_DIR

    out: dict[str, dict[str, str]] = {}
    log = RESULTS / "run_nnc_log.txt"
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            m = re.match(r"(\w+)\s+(\d{4})\s+(?:bỏ qua|lỗi đọc PDF):\s*(.+)", line)
            if not m:
                continue
            ticker, year, why = m.group(1), m.group(2), m.group(3).strip()
            chars = re.search(r"bóc được ([\d,.]+) ký tự", why)
            if chars and int(re.sub(r"\D", "", chars.group(1))) < 500:
                short, why = "bản scan", "Bản scan ảnh — không bóc được chữ"
            elif chars:
                short, why = "không phải BCTN", "Tệp là công văn công bố thông tin, không phải báo cáo thường niên"
            elif "dấu tiếng Việt" in why:
                short, why = "chữ lỗi", "Chữ bóc ra gần như mất hết dấu tiếng Việt (nhiều khả năng là bản scan)"
            else:
                short = "lỗi đọc"
            out[f"{ticker}_{year}"] = {"short": short, "why": why}
    for pdf in BCTN_DIR.glob("*/*_BCTN_*.pdf"):
        m = re.match(r"([A-Z]+)_BCTN_(\d{4})$", pdf.stem)
        if m and (m.group(1), int(m.group(2))) not in have and f"{m.group(1)}_{m.group(2)}" not in out:
            out[f"{m.group(1)}_{m.group(2)}"] = (
                {"short": "thiếu BCTC", "why": "Chưa có BCTC kiểm toán của năm này để đối chiếu"} if log.exists()
                else {"short": "không đối chiếu được", "why": "Không có kết quả đối chiếu cho năm này"})
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
            "missing": _missing_reports({(r["ticker"], r["year"]) for r in results}),
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
            "dataset": {k: qka["dataset"].get(k) for k in ("n_samples", "n_rows", "n_classes", "classes", "tickers")
                        if k in qka["dataset"]},
            "n_qubits": qka["config"].get("n_qubits"),
            "n_folds": qka["config"].get("n_folds"),
            "total_seconds": qka.get("total_seconds"),
        }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── Ví dụ cho ô kiểm tra trực tiếp: câu thật + câu chèn lỗi có ghi rõ ──
    examples = []
    consistent = [(rep, c) for rep in reports if not rep["bank"] for c in rep["claims"]
                  if c["verdict"] == "nhất quán" and 45 < len(c["text"]) < 130]
    for ticker, year, head in REAL_EXAMPLES:
        hit = next((c for rep, c in consistent
                    if rep["ticker"] == ticker and rep["year"] == year and c["text"].startswith(head)), None)
        if hit:
            examples.append({"ticker": ticker, "year": year, "text": hit["text"], "real": True, "page": hit["page"]})
    for rep, c in consistent:  # bù cho đủ 4 câu thật, mỗi mã tối đa một câu
        if sum(e["real"] for e in examples) >= 4:
            break
        if "tỷ" in c["text"] and rep["ticker"] not in {e["ticker"] for e in examples}:
            examples.append({"ticker": rep["ticker"], "year": rep["year"], "text": c["text"], "real": True, "page": c["page"]})

    injected_csv = RESULTS / "injected_cases.csv"
    if injected_csv.exists():
        import csv
        rows = [r for r in csv.DictReader(open(injected_csv, encoding="utf-8-sig"))]
        caught = [r for r in rows if r["ky_vong"] == r["he_thong"] == "mâu thuẫn"]
        for loai, muc, ticker, year, head in INJECTED_EXAMPLES:
            hit = next((r for r in caught if r["loai"] == loai and r["ma_ck"] == ticker and int(r["nam"]) == year
                        and (muc is None or r["muc"] == muc) and (head is None or r["cau_goc"].startswith(head))), None)
            if hit:
                examples.append({"ticker": ticker, "year": year, "text": hit["cau_chen_loi"], "real": False,
                                 "loai": loai, "original": hit["cau_goc"]})
        # Ví dụ cho trang Đánh giá: một câu thật và ba cách sửa sai của chính nó.
        t, y, head = EVAL_EXAMPLE
        variants = {}
        for r in rows:
            if (r["ma_ck"] == t and int(r["nam"]) == y and r["cau_goc"].startswith(head)
                    and (r["loai"], r["muc"]) in {("gia_tri", "+2%"), ("phan_tram", "+2 điểm"), ("huong", "đảo chiều")}):
                variants[r["loai"]] = {"text": r["cau_chen_loi"], "ket_qua": r["he_thong"], "muc": r["muc"]}
        ksc = next((r for r in caught if r["loai"] == "kiem_soat_chi_phi"), None)
        if metrics.get("injected") and variants:
            metrics["injected"]["vi_du"] = {
                "ticker": t, "year": y,
                "goc": next(r["cau_goc"] for r in rows if r["ma_ck"] == t and int(r["nam"]) == y and r["cau_goc"].startswith(head)),
                "bien_the": variants,
                "kiem_soat_chi_phi": {"ticker": ksc["ma_ck"], "year": int(ksc["nam"]), "text": ksc["cau_chen_loi"],
                                      "muc": ksc["muc"]} if ksc else None,
            }
            (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
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
