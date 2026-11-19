"""Script tạm (nháp rà soát dữ liệu): pipeline đã ghép BCTN với BCTC nào?

Tái hiện đúng logic chọn báo cáo của scripts/run_nnc.py (bỏ bản chắc chắn là
công ty mẹ, lấy bản đầu tiên bóc được bảng), rồi đọc trang bìa của tệp được
chọn để xem đó là BCTC hợp nhất hay riêng. Chỉ đọc, không ghi gì.

Chạy (thư mục hiện tại là ROOT):
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\which_bctc.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from smartaudit.config import TICKERS  # noqa: E402
from smartaudit.ingest import iter_reports  # noqa: E402
from smartaudit.tables import extract_tables  # noqa: E402

pairs = {
    (r["ticker"], r["year"])
    for r in json.loads((ROOT / "results" / "nnc_results.json").read_text(encoding="utf-8"))
}

chosen: dict[tuple[str, int], object] = {}
for rep in iter_reports(tickers=TICKERS):
    if rep.consolidated is False:
        continue
    key = (rep.ticker, rep.year)
    if key not in pairs or key in chosen:
        continue
    if extract_tables(rep.read()):
        chosen[key] = rep

SEPARATE = re.compile(r"t[aà]i ch[ií]nh ri[eê]ng|c[oô]ng ty m[eẹ]\b", re.I)
CONSOL = re.compile(r"h[oợ]p nh[aấ]t", re.I)

bad = 0
for key in sorted(pairs):
    rep = chosen.get(key)
    if rep is None:
        print(f"{key[0]} {key[1]}: không có BCTC bóc được")
        continue
    head = rep.read()[:4000]
    kind = "RIÊNG" if SEPARATE.search(head) and not CONSOL.search(head) else (
        "hợp nhất" if CONSOL.search(head) else "?")
    flag = "  <-- KIỂM TRA" if kind != "hợp nhất" else ""
    bad += bool(flag)
    print(f"{key[0]} {key[1]}: consolidated={rep.consolidated!s:5} trang bìa={kind:8} {rep.name}{flag}")
print(f"\n{bad}/{len(pairs)} cặp cần kiểm tra loại BCTC")
