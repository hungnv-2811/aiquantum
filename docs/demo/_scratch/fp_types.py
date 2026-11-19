"""Script tạm (nháp rà soát demo): phân loại 141 cờ "mâu thuẫn" theo kiểu lỗi.

Phân loại do agent làm tay khi đọc câu, minh chứng và (với các ca đại diện)
ngữ cảnh trang BCTN + ô bảng TiniX. ĐÂY LÀ NHÃN SƠ BỘ, KHÔNG PHẢI NHÃN VÀNG:
Nguyên/Hùng cần rà lại trước khi dùng để sửa luật. Không dùng làm tập đánh giá.

Số thứ tự khớp với đầu ra của dump_flags.py "mâu thuẫn" (thứ tự trong
results/nnc_results.json).

Chạy (thư mục hiện tại là ROOT):
    .venv\\Scripts\\python.exe docs\\demo\\_scratch\\fp_types.py
Ghi thêm docs/demo/_scratch/phan_loai_mau_thuan.csv (chỉ trong thư mục nháp).
"""

from __future__ import annotations

import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

TYPES = {
    "A": "Phạm vi hẹp hơn số hợp nhất (công ty con, bộ phận, thương hiệu, thị trường, khoản mục con)",
    "B": "Số BCTC riêng công ty mẹ đem so với số hợp nhất",
    "C": "Rác bố cục: trộn cột, mảnh bảng/biểu đồ/infographic",
    "D": "Câu về tỷ số/hệ số/cơ cấu/tỷ trọng bị so với khoản mục tiền",
    "E": "Không phải khẳng định kết quả (chính sách kế toán, rủi ro, mục tiêu, vĩ mô, mô tả)",
    "F": "Sai kỳ (quý, năm lịch sử, nhiều năm)",
    "G": "Câu nhiều số/nhiều vế: lấy nhầm số hoặc nhầm từ chỉ hướng",
    "H": "Định nghĩa chỉ tiêu khác ('tổng doanh thu', LNST thuộc công ty mẹ, 'trên X tỷ')",
    "I": "Quy ước số âm trong ngoặc",
    "X": "Cần người xem (chưa tái lập được con số / ngữ nghĩa mơ hồ)",
}

LABELS: dict[int, str] = {}
for t, ids in {
    "A": [1, 2, 3, 4, 6, 7, 10, *range(19, 29), 32, 33, 34, 36, 40, 41, 42, 43,
          45, 46, 47, 48, 49, 50, 57, 62, 63, 64, 68, 69, 70, 71, 74, 75, 77,
          80, 81, 82, 84, 92, 99, 110, 111, 120, 124, 128, 135, 139, 140, 141],
    "B": [105, 107, 109, 116, 117],
    "C": [8, 11, 14, 16, 29, 35, 37, 44, 56, 58, 61, 65, 66, 78, 85, 88, 91,
          97, 103, 104, 118, 119, 121, 136],
    "D": [52, 53, 59, 86, 90, 94, 96, 106, 112, 114, 123, 126, 127, 129, 131,
          132, 133],
    "E": [12, 13, 17, 30, 31, 38, 39, 54, 67, 72, 73, 79, 87, 100, 101, 102,
          130, 134],
    "F": [51, 76, 83, 93, 95, 137, 138],
    "G": [9, 55, 60, 98, 115, 125],
    "H": [15, 89, 122],
    "I": [113],
    "X": [5, 18, 108],
}.items():
    for i in ids:
        assert i not in LABELS, i
        LABELS[i] = t

data = json.loads((ROOT / "results" / "nnc_results.json").read_text(encoding="utf-8"))
rows = []
i = 0
for rep in data:
    for c in rep["claims"]:
        if c["verdict"] != "mâu thuẫn":
            continue
        i += 1
        rows.append((i, rep["ticker"], rep["year"], c["page"], c["metric"], LABELS[i], c["text"][:160]))
assert i == len(LABELS) == 141, (i, len(LABELS))

count = collections.Counter(r[5] for r in rows)
print(f"Tổng cờ 'mâu thuẫn': {i}")
for t, n in count.most_common():
    print(f"  {t} {n:3d} ({n / i:5.1%})  {TYPES[t]}")

with (Path(__file__).parent / "phan_loai_mau_thuan.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stt", "ma", "nam", "trang_bctn", "metric", "kieu_loi", "cau"])
    w.writerows(rows)

# Chuỗi điểm NNC theo năm: gốc và sau khi coi các cờ oan đã định danh là
# "không kiểm chứng được" (giữ nguyên các ca X).
print("\nChuỗi điểm NNC (gốc → nếu loại cờ oan đã định danh):")
by_key: dict[tuple[str, int], list] = collections.defaultdict(list)
i = 0
for rep in data:
    for c in rep["claims"]:
        if c["verdict"] == "mâu thuẫn":
            i += 1
            by_key[(rep["ticker"], rep["year"])].append((c, LABELS[i]))
        else:
            by_key[(rep["ticker"], rep["year"])].append((c, None))

for ticker in ["PC1", "FPT", "VCG", "HAG", "VIC", "VNM", "MSN"]:
    parts = []
    for (t, y), items in sorted(by_key.items()):
        if t != ticker:
            continue
        raw = [c["score"] for c, _ in items if c["score"] is not None]
        adj = [c["score"] for c, lab in items
               if c["score"] is not None and (lab is None or lab == "X")]
        nq = sum(c["verdict"] == "nhất quán" for c, _ in items)
        mt = sum(c["verdict"] == "mâu thuẫn" for c, _ in items)
        mt_x = sum(lab == "X" for _, lab in items)
        f = lambda v: f"{sum(v) / len(v):.2f}" if v else "—"  # noqa: E731
        parts.append(f"{y}: n={len(items)} NQ={nq} MT={mt}(còn {mt_x}) điểm {f(raw)}→{f(adj)}")
    print(f"  {ticker}\n    " + "\n    ".join(parts))
