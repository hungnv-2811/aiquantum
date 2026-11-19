"""Tải Báo cáo thường niên (nguồn narrative) từ Vietstock.

Chạy:
    python scripts/fetch_narrative.py                 # 16 mã, 2020-2024
    python scripts/fetch_narrative.py VNM HPG         # mã chỉ định
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import TICKERS  # noqa: E402
from smartaudit.ingest import download_annual_report  # noqa: E402

YEARS = range(2018, 2025)


def main() -> int:
    tickers = sys.argv[1:] or TICKERS
    print(f"Tải báo cáo thường niên: {len(tickers)} mã × {len(YEARS)} năm\n")

    print(f"{'Mã':<6} " + " ".join(f"{y:>6}" for y in YEARS) + "   tổng MB")
    print("-" * (7 + 7 * len(YEARS) + 11))

    grand_total = 0.0
    found_total = 0
    for ticker in tickers:
        cells, size = [], 0.0
        for year in YEARS:
            report = download_annual_report(ticker, year)
            if report:
                mb = report.path.stat().st_size / 1024**2
                size += mb
                found_total += 1
                cells.append(f"{'✓':>6}")
            else:
                cells.append(f"{'—':>6}")
        grand_total += size
        print(f"{ticker:<6} " + " ".join(cells) + f"   {size:>7.1f}")

    total_slots = len(tickers) * len(YEARS)
    print(f"\nLấy được {found_total}/{total_slots} báo cáo "
          f"({found_total / total_slots:.0%}), tổng {grand_total:.0f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
