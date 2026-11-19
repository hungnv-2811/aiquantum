"""Script tạm (nháp rà soát demo): in mọi khẳng định theo phán quyết kèm minh chứng.

Chỉ đọc results/nnc_results.json, không ghi gì vào data/ hay results/.

Chạy (thư mục hiện tại là ROOT):
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\dump_flags.py "mâu thuẫn" > out.txt
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
verdict = sys.argv[1] if len(sys.argv) > 1 else "mâu thuẫn"

data = json.loads((ROOT / "results" / "nnc_results.json").read_text(encoding="utf-8"))
i = 0
for rep in data:
    for c in rep["claims"]:
        if c["verdict"] != verdict:
            continue
        i += 1
        score = "—" if c["score"] is None else f"{c['score']:.2f}"
        print(f"#{i} [{rep['ticker']} {rep['year']}] tr.{c['page']} · {c['metric']} · "
              f"{c['trend']} · điểm {score}")
        print(f"   {c['text']}")
        for e in c["evidence"]:
            mark = "+" if e["passed"] else "x"
            print(f"   {mark} [{e['dimension']}] {e['explanation']}")
        print()
