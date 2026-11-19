"""Script tạm (nháp rà soát demo): in ngữ cảnh quanh một câu trong văn bản BCTN đã bóc.

Chỉ đọc data/interim/bctn_text, không ghi gì.

Chạy (thư mục hiện tại là ROOT):
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\ctx.py VNM 2024 59 "7,6%" 12
    (mã, năm, trang PDF, đoạn chữ cần tìm, số dòng ngữ cảnh mỗi phía)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ticker, year, page, needle = sys.argv[1].upper(), sys.argv[2], int(sys.argv[3]), sys.argv[4]
span = int(sys.argv[5]) if len(sys.argv) > 5 else 10

path = next((ROOT / "data" / "interim" / "bctn_text" / ticker).glob(f"{ticker}_{year}_*.txt"))
lines = path.read_text(encoding="utf-8").splitlines()

start = end = None
for i, line in enumerate(lines):
    if line.strip() == f"===== PAGE {page} =====":
        start = i
    elif start is not None and line.startswith("===== PAGE "):
        end = i
        break
if start is None:
    sys.exit(f"Không thấy trang {page} trong {path.name}")
end = end or len(lines)

print(f"# {path.relative_to(ROOT)} · trang PDF {page} (dòng {start + 1}–{end})")
hits = [i for i in range(start, end) if needle.lower() in lines[i].lower()]
if not hits:
    print("(không thấy đoạn chữ; in cả trang)")
    hits = [start]
    span = end - start
for h in hits:
    lo, hi = max(start, h - span), min(end, h + span + 1)
    for i in range(lo, hi):
        mark = ">>" if i == h else "  "
        print(f"{mark}{i + 1:5d}: {lines[i]}")
    print("   ...")
