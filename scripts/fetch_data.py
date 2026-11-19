"""Tải dữ liệu báo cáo tài chính từ HuggingFace về máy.

Chạy:
    python scripts/fetch_data.py                 # tải 16 mã mặc định
    python scripts/fetch_data.py VNM HPG FPT     # tải mã chỉ định
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import TICKERS, TINIX_DIR  # noqa: E402
from smartaudit.ingest import download_tickers, iter_reports  # noqa: E402


def _size_mb(path: Path) -> float:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024**2


def main() -> int:
    tickers = sys.argv[1:] or TICKERS
    print(f"Tải {len(tickers)} mã: {', '.join(tickers)}")
    print(f"Đích: {TINIX_DIR}\n")

    t0 = time.time()
    download_tickers(tickers)
    elapsed = time.time() - t0

    reports = list(iter_reports(tickers=tickers))
    by_ticker: dict[str, list[int]] = {}
    for r in reports:
        by_ticker.setdefault(r.ticker, []).append(r.year)

    print(f"\nXong sau {elapsed:.0f}s — {_size_mb(TINIX_DIR):.1f} MB, "
          f"{len(reports)} báo cáo\n")
    print(f"{'Mã':<6} {'Số BC':>6}  {'Năm':<12}")
    print("-" * 32)
    for t in tickers:
        years = sorted(set(by_ticker.get(t, [])))
        if not years:
            print(f"{t:<6} {'—':>6}  KHÔNG CÓ DỮ LIỆU")
        else:
            print(f"{t:<6} {len(by_ticker[t]):>6}  {years[0]}–{years[-1]}")

    missing = [t for t in tickers if t not in by_ticker]
    if missing:
        print(f"\nCác mã không có trong dataset: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
