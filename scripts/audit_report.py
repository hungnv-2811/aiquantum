"""In báo cáo đối chiếu cho một doanh nghiệp, một năm.

Chạy:
    python scripts/audit_report.py VNM 2024
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.eval import load_financials  # noqa: E402
from smartaudit.ingest.vietstock import BCTN_DIR, TEXT_CACHE, AnnualReport  # noqa: E402
from smartaudit.nlp import extract_claims  # noqa: E402
from smartaudit.nnc import check_report  # noqa: E402
from smartaudit.xai import render_report  # noqa: E402


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    ticker, year = sys.argv[1].upper(), int(sys.argv[2])

    pdf = BCTN_DIR / ticker / f"{ticker}_BCTN_{year}.pdf"
    # Chạy được cả khi chỉ có bản văn bản đã bóc sẵn (gói nộp không kèm PDF gốc).
    cached = TEXT_CACHE / ticker / f"{ticker}_{year}_col-60.txt"
    if not pdf.exists() and not cached.exists():
        print(f"Chưa có báo cáo thường niên {ticker} {year}.")
        print(f"Chạy: python scripts/fetch_narrative.py {ticker}")
        return 1

    # Chỉ loại báo cáo **chắc chắn** là riêng công ty mẹ. Một số file đặt
    # tên không theo quy ước nào nên `consolidated` là None, nhưng nội dung
    # vẫn là báo cáo hợp nhất — loại luôn thì mất dữ liệu đang có sẵn.
    # Xếp báo cáo hợp nhất lên trước, rồi lấy bản đầu tiên bóc được bảng.
    # Chọn BCTC đúng theo quy tắc của run_nnc.py (smartaudit.eval.load_financials)
    # để báo cáo một doanh nghiệp luôn khớp với kết quả trên dashboard.
    found, _, _ = load_financials([ticker], {(ticker, year)})
    tables = found.get((ticker, year))
    if tables is None:
        print(f"Chưa có báo cáo tài chính hợp nhất {ticker} {year}.")
        return 1
    text = AnnualReport(ticker, year, pdf).extract_text(columns=True, max_pages=60)
    results = check_report(extract_claims(text, default_year=year), tables)

    print(render_report(ticker, year, results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
