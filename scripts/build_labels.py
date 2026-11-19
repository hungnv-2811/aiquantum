"""Sinh nhãn yếu từ hiện tượng hồi tố số liệu, ghi ra CSV.

Chạy:
    python scripts/build_labels.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import PROCESSED  # noqa: E402
from smartaudit.ingest import iter_reports  # noqa: E402
from smartaudit.labels import collect_series, detect_restatements  # noqa: E402

OUT = PROCESSED / "restatements.csv"


def main() -> int:
    reports = list(iter_reports())
    print(f"Quét {len(reports)} báo cáo...\n")

    series = collect_series(reports)
    pairs = sum(
        len(vals)
        for years in series.values()
        for year, vals in years.items()
        if year + 1 in years
    )
    found = detect_restatements(reports)

    print(f"Đối chiếu được {pairs} cặp (khoản mục × năm liền kề)")
    print(f"Phát hiện {len(found)} lần hồi tố "
          f"({len(found) / max(pairs, 1):.1%} — tỷ lệ nhãn dương)\n")

    print(f"{'Mã':<5} {'Năm':<6} {'Loại':<9} {'Khoản mục':<19} "
          f"{'Đã công bố':>20} {'Ghi lại':>20} {'Lệch':>8}")
    print("-" * 92)
    for r in found[:20]:
        kind = "hợp nhất" if r.consolidated else "riêng"
        print(f"{r.ticker:<5} {r.year:<6} {kind:<9} {r.concept:<19} "
              f"{r.reported:>20,.0f} {r.restated:>20,.0f} {r.relative_diff:>7.1%}")
    if len(found) > 20:
        print(f"... còn {len(found) - 20} dòng nữa trong CSV")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "ticker", "year", "consolidated", "concept",
            "reported", "restated", "relative_diff", "direction",
        ])
        for r in found:
            writer.writerow([
                r.ticker, r.year, r.consolidated, r.concept,
                f"{r.reported:.0f}", f"{r.restated:.0f}",
                f"{r.relative_diff:.6f}", r.direction,
            ])

    print(f"\nĐã ghi {OUT}")
    print("\nLƯU Ý: đây là nhãn YẾU, chưa phải bằng chứng gian lận. Chênh lệch")
    print("còn có thể do đổi phạm vi hợp nhất, đổi chính sách kế toán, hoặc lỗi")
    print("bóc tách. Phải rà tay một mẫu và ghi tỷ lệ dương tính giả vào báo cáo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
