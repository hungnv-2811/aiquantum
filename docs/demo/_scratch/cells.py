"""Script tạm (nháp rà soát demo): in nguyên văn các dòng bảng TiniX theo Mã số.

Cố ý KHÔNG dùng smartaudit.tables.parser, để kiểm chứng độc lập với pipeline:
đọc thẳng tệp *_extracted.txt, tách <tr>…</tr>, in mọi dòng có ô bằng đúng
Mã số cần tìm (hoặc có nhãn chứa cụm từ cần tìm), kèm số trang PDF.

Chỉ đọc data/raw/tinix, không ghi gì.

Chạy (thư mục hiện tại là ROOT):
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\cells.py VNM 2024 hop 10 01 50 60
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\cells.py VCG 2024 me 60
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\cells.py VNM 2024 hop "~Angkor"   # tìm theo chữ
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TINIX = ROOT / "data" / "raw" / "tinix" / "ocr_results"

ticker, year, kind = sys.argv[1].upper(), sys.argv[2], sys.argv[3].lower()
wanted = sys.argv[4:]

files = sorted((TINIX / ticker / year).rglob("*_extracted.txt"))
pick = []
for f in files:
    low = f.name.lower()
    is_parent = "congtyme" in low or "rieng" in low
    if kind.startswith("me") and is_parent:
        pick.append(f)
    elif kind.startswith("hop") and not is_parent:
        pick.append(f)
    elif kind == "all":
        pick.append(f)

ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)

for f in pick:
    print(f"### {f.relative_to(ROOT)}")
    text = f.read_text(encoding="utf-8", errors="replace")
    page = 0
    for line in text.splitlines():
        m = re.match(r"===== PAGE (\d+) =====", line)
        if m:
            page = int(m.group(1))
            continue
        if "<tr>" not in line:
            continue
        for row in ROW.findall(line):
            cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in CELL.findall(row)]
            hit = False
            for w in wanted:
                if w.startswith("~"):
                    if w[1:].lower() in " ".join(cells).lower():
                        hit = True
                elif w in cells[0:3]:
                    hit = True
            if hit:
                print(f"  tr.{page}: " + " | ".join(cells))
