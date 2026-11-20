"""Đóng gói AQ2026-R2-AQ2026-064-Ma_nguon.zip.

Gồm mã nguồn, test, dashboard, kết quả, nhãn và **dữ liệu mẫu chạy offline**
(BCTC TiniX của 16 mã + văn bản BCTN đã bóc). Không gồm: môi trường ảo, PDF
BCTN gốc (958 MB, có script tải lại), hồ sơ Word, thư mục deliverables/ và
mọi tệp có thông tin cá nhân.

Sau khi nén, quét toàn bộ nội dung văn bản để chắc không lọt số CCCD, số điện
thoại hay email của thành viên (đọc từ members.local.json — tệp này không vào gói).

Chạy:
    python deliverables/build/build_zip.py
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "AQ2026-R2-AQ2026-064-Ma_nguon.zip"
#: Tên thư mục gốc ngắn: Windows giới hạn đường dẫn 260 ký tự, và người chấm
#: thường giải nén vào một thư mục đã khá sâu (Downloads\…).
TOP = "AQ2026-064"

INCLUDE = [
    "README.md", "NOTICE.md", "requirements.txt", "requirements-lock.txt",
    "requirements-quantum.txt", "requirements-sample.txt", "run_demo.bat", "sample_data",
    "smartaudit", "scripts", "tests", "prototype", "results", "annotation",
    "data/raw/tinix", "data/interim/bctn_text", "data/processed",
    "docs/quantum-poc.md", "docs/gan-nhan", "docs/demo/ung-vien-demo.md",
    "docs/thu-nghiem-ktv",
]
EXCLUDE_PARTS = {"__pycache__", ".venv", ".venv-quantum", ".pytest_cache", "qka_cache", "_scratch", ".cache"}


def arcname(rel: str) -> str:
    """Đường dẫn trong gói. BCTC TiniX được làm phẳng một cấp:
    ``ocr_results/MÃ/NĂM/<tên>/<tên>_extracted.txt`` → ``ocr_results/MÃ/NĂM/<tên>_extracted.txt``
    (``iter_reports`` tìm tệp đệ quy nên không cần thư mục trung gian), để
    đường dẫn đủ ngắn khi giải nén trên Windows."""
    parts = rel.split("/")
    if parts[:4] == ["data", "raw", "tinix", "ocr_results"] and len(parts) > 7:
        parts = parts[:6] + [parts[-1]]
    return f"{TOP}/" + "/".join(parts)
EXCLUDE_SUFFIX = {".pyc", ".log", ".local.json"}
EXCLUDE_NAMES = {"run_nnc_log.txt"}
TEXT_SUFFIX = {".py", ".md", ".json", ".csv", ".txt", ".html", ".js", ".css", ".yaml", ".yml", ".bat"}


def files():
    for item in INCLUDE:
        path = ROOT / item
        if path.is_file():
            yield path
        elif path.is_dir():
            for p in sorted(path.rglob("*")):
                if p.is_file():
                    yield p


def skip(p: Path) -> bool:
    rel = p.relative_to(ROOT)
    return (any(part in EXCLUDE_PARTS for part in rel.parts)
            or any(str(p).endswith(s) for s in EXCLUDE_SUFFIX)
            or p.name in EXCLUDE_NAMES)


def main() -> int:
    meta_path = ROOT / "deliverables" / "build" / "members.local.json"
    secrets: list[str] = []
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for m in meta["members"]:
            secrets += [m["cccd"], m["dien_thoai"], m["email"]]

    count = size = 0
    leaks = []
    seen: set[str] = set()
    longest = ""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files():
            if skip(p):
                continue
            rel = p.relative_to(ROOT).as_posix()
            name = arcname(rel)
            if name in seen:
                raise SystemExit(f"Trùng tên sau khi làm phẳng: {name}")
            seen.add(name)
            longest = max(longest, name, key=len)
            if p.suffix.lower() in TEXT_SUFFIX:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for s in secrets:
                    if s and s in text:
                        leaks.append((rel, s[:3] + "…"))
            zf.write(p, name)
            count += 1
            size += p.stat().st_size
    print(f"{count} tệp, {size / 1e6:.1f} MB chưa nén → {OUT.name} {OUT.stat().st_size / 1e6:.1f} MB")
    print(f"Đường dẫn dài nhất trong gói: {len(longest)} ký tự")
    if leaks:
        print("!! LỌT THÔNG TIN CÁ NHÂN:")
        for rel, hint in leaks:
            print("   ", rel, hint)
        OUT.unlink()
        return 1
    print("Quét thông tin cá nhân: sạch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
