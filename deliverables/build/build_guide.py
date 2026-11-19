"""Sinh AQ2026-R2-AQ2026-064-Huong_dan.pdf từ huong_dan.html.

Điền số thật vào các token %%…%% (lấy từ results/ và values.json), rồi in ra
PDF bằng Microsoft Edge chế độ headless.

Chạy:
    python deliverables/build/build_guide.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "deliverables" / "build"
OUT = ROOT / "deliverables" / "AQ2026-R2-AQ2026-064-Huong_dan.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> int:
    values = json.loads((BUILD / "values.json").read_text(encoding="utf-8"))
    ev = json.loads((ROOT / "results" / "eval_summary.json").read_text(encoding="utf-8"))
    inj = json.loads((ROOT / "results" / "injected_eval.json").read_text(encoding="utf-8"))
    res = json.loads((ROOT / "results" / "nnc_results.json").read_text(encoding="utf-8"))
    counts = {"nhất quán": 0, "mâu thuẫn": 0, "không kiểm chứng được": 0}
    for rep in res:
        for c in rep["claims"]:
            counts[c["verdict"]] += 1
    total = sum(counts.values())

    link = values["link"]
    link_html = f'<a href="{link}">{link}</a>' if link.startswith("http") else link
    r = inj["recall_chen_loi"]
    dc = inj["bao_dong_gia_doi_chung"]
    tokens = {
        "%%DATE%%": "19/11/2026",
        "%%LINK%%": link_html,
        "%%TESTS%%": "171",
        "%%TESTS_MAIN%%": "147 passed, 1 skipped",
        "%%TOTAL_LINE%%": f"TỔNG {total} · {counts['nhất quán']} · {counts['mâu thuẫn']} · {counts['không kiểm chứng được']}",
        "%%INJ_LINE%%": f"Recall {r['ty_le'] * 100:.1f}% ({r['dung']}/{r['n']}); đối chứng {dc['dung']}/{dc['n']} không báo động".replace(".", ","),
        "%%EVAL_LINE%%": f"Kappa {ev['kappa_nhan']:.2f}; cờ sau vá trong mẫu: {ev['after']['true_mt']}/{ev['after']['flags_in_sample']} là mâu thuẫn thật".replace(".", ","),
    }
    html = (BUILD / "huong_dan.html").read_text(encoding="utf-8")
    for k, v in tokens.items():
        html = html.replace(k, v)
    if "%%" in html:
        print("!! Còn token chưa điền")
        return 1
    filled = BUILD / "huong_dan.filled.html"
    filled.write_text(html, encoding="utf-8")
    subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT}", filled.as_uri()], check=True, timeout=120)
    print(f"Đã ghi {OUT} ({OUT.stat().st_size // 1024} KB)")
    if "⟦" in html:
        print("!! Hướng dẫn còn placeholder (link prototype)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
