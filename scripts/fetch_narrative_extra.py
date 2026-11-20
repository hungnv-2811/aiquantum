"""Tải bổ sung báo cáo thường niên từ đường dẫn Vietstock do đội tra tay (20/11/2026).

Vì sao cần: ``fetch_narrative.py`` chỉ thử một mẫu tên tệp
``{MÃ}_Baocaothuongnien_{NĂM}.pdf``. Nhiều năm Vietstock lưu dưới tên khác
(ví dụ FPT 2020 nằm trong thư mục con ``FPT_Baocaothuongnien_2020/``), nên
script gốc nhận 404 và bỏ qua; một số năm khác thì mẫu tên đúng nhưng trỏ
tới công văn công bố thông tin hoặc bản scan.

Quy trình an toàn:
1. Tải mọi tệp vào thư mục tạm mới ``data/raw/_bctn_tai_<ngày>/``.
2. So SHA-256 với tệp đang có: giống hệt thì bỏ qua; khác hoặc chưa có thì
   mới thay. Tệp cũ bị thay được chuyển sang ``data/raw/_bctn_cu/``.
3. Xoá bản văn bản đã bóc (cache) của các năm bị thay để pipeline bóc lại.

Chạy:
    python scripts/fetch_narrative_extra.py            # tải + báo cáo, chưa thay
    python scripts/fetch_narrative_extra.py --apply    # thay vào data/raw/bctn
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.ingest.vietstock import BCTN_DIR, TEXT_CACHE  # noqa: E402

BASE = "https://static2.vietstock.vn/data"

#: (mã, năm, đường dẫn tương đối trên static2.vietstock.vn/data/)
SOURCES: list[tuple[str, int, str]] = [
    ("FPT", 2020, "HOSE/2020/BCTN/VN/FPT_Baocaothuongnien_2020/Bao-cao-thuong-nien-2020.pdf"),
    ("GAS", 2019, "HOSE/2019/BCTN/VN/GAS_Baocaothuongnien_2019/B%C3%A1o%20c%C3%A1o%20th%C6%B0%E1%BB%9Dng%20ni%C3%AAn%20n%C4%83m%202019.pdf"),
    ("GAS", 2020, "HOSE/2020/BCTN/VN/GAS_BCTN%202020.pdf"),
    ("GAS", 2021, "HOSE/2021/BCTN/VN/GAS_Baocaothuongnien_2021/BCTN%20PV%20GAS%202021.pdf"),
    ("GAS", 2023, "HOSE/2023/BCTN/VN/GAS_Baocaothuongnien_2023/PVGAS-BCTN-VN-200324.pdf"),
    ("GAS", 2024, "HOSE/2024/BCTN/VN/GAS_Baocaothuongnien_2024.pdf"),
    ("HAG", 2021, "HOSE/2021/BCTN/VN/HAG_Baocaothuongnien_2021.pdf"),
    ("HAG", 2022, "HOSE/2022/BCTN/VN/HAG_Baocaothuongnien_2022/web_single_ar-hag_2022.pdf"),
    ("HPG", 2024, "HOSE/2024/BCTN/VN/HPG_Baocaothuongnien_2024/20250416_20250415___hpg___bao_cao_thuong_nien_2024.pdf"),
    ("MSN", 2018, "HOSE/2018/BCTN/VN/MSN_Baocaothuongnien_2018/MSN_Baocaothuongnien_2018.pdf"),
    ("MSN", 2019, "HOSE/2019/BCTN/VN/MSN_Baocaothuongnien_2019.pdf"),
    ("MSN", 2020, "HOSE/2020/BCTN/VN/MSN_Baocaothuongnien_2020/20210329_20210329%20-%20MSN%20-%20Bao%20cao%20thuong%20nien%202020.pdf"),
    ("MWG", 2018, "HOSE/2018/BCTN/VN/MWG_Baocaothuongnien_2018.pdf"),
    ("MWG", 2019, "HOSE/2019/BCTN/VN/MWG_Baocaothuongnien_2019.pdf"),
    ("MWG", 2020, "HOSE/2020/BCTN/VN/MWG_Baocaothuongnien_2020.pdf"),
    ("MWG", 2021, "HOSE/2021/BCTN/VN/MWG_Baocaothuongnien_2021.pdf"),
    ("MWG", 2024, "HOSE/2024/BCTN/VN/MWG_Baocaothuongnien_2024.pdf"),
    ("PLX", 2018, "HOSE/2018/BCTN/VN/PLX_Baocaothuongnien_2018.pdf"),
    ("PLX", 2019, "HOSE/2019/BCTN/VN/PLX_Baocaothuongnien_2019/20200429_AR%20PETROLIMEX%202019%20v5%20(1).pdf"),
    ("PLX", 2020, "HOSE/2020/BCTN/VN/PLX_Baocaothuongnien_2020/20210505_Petrolimex_AR%202020%20view%20update.pdf"),
    ("PLX", 2021, "HOSE/2021/BCTN/VN/PLX_Baocaothuongnien_2021/20220420_PLX_AR2021-VIEW.pdf"),
    ("PLX", 2022, "HOSE/2022/BCTN/VN/PLX_Baocaothuongnien_2022/20230707_PLX_AR2022_VN.pdf"),
    ("PLX", 2023, "HOSE/2023/BCTN/VN/PLX_Baocaothuongnien_2023/BCTN_Petrolimex_17.4%20ver%205.pdf"),
    ("PLX", 2024, "HOSE/2024/BCTN/VN/PLX_Baocaothuongnien_2024/PLX_Baocaothuongnien_2024.pdf"),
    ("POW", 2021, "HOSE/2021/BCTN/VN/POW_Baocaothuongnien_2021/20220413_20220413___pow___bao_cao_thuong_nien_nam_2021_compressed.pdf"),
    ("POW", 2023, "HOSE/2023/BCTN/VN/POW_Baocaothuongnien_2023_1.pdf"),
    ("VCG", 2019, "HNX/2019/BCTN/VN/VCG_Baocaothuongnien_2019.pdf"),
    ("VCG", 2020, "HOSE/2020/BCTN/VN/VCG_Baocaothuongnien_2020/BCTN_VCG_2020[1].pdf"),
    ("VHM", 2018, "HOSE/2018/BCTN/VN/VHM_Baocaothuongnien_2018.pdf"),
    ("VHM", 2019, "HOSE/2019/BCTN/VN/VHM_Baocaothuongnien_2019/VinhomesAR2019-VN.pdf"),
    ("VHM", 2020, "HOSE/2020/BCTN/VN/VHM_Baocaothuongnien_2020/Bao-cao-thuong-nien-VHM-2020-1.pdf"),
    ("VHM", 2021, "HOSE/2021/BCTN/VN/VHM_Baocaothuongnien_2021/Vinhomes%202021_AR_220418.pdf"),
    ("VHM", 2022, "HOSE/2022/BCTN/VN/VHM_Baocaothuongnien_2022/Vinhomes%20AR%202022_230331_1680273771.pdf"),
    ("VIC", 2019, "HOSE/2019/BCTN/VN/VIC_Baocaothuongnien_2019/Vingroup%20-%20Annual%20Report%202019_VN.pdf"),
    ("VNM", 2019, "HOSE/2019/BCTN/VN/VNM_Baocaothuongnien_2019/1585291596-7f525505f3621558355a60c10f6862cbb3b9c9863921a9b06587f7b42a0f9733.pdf"),
    ("VNM", 2023, "HOSE/2023/BCTN/VN/VNM_Baocaothuongnien_2023/vnm.pdf"),
    ("VPB", 2019, "HNX/2019/BCTN/VN/VPB_Baocaothuongnien_2019/VPB_Baocaothuongnien_2019.pdf"),
    ("VPB", 2023, "HOSE/2023/BCTN/VN/VPB_Baocaothuongnien_2023.pdf"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    apply = "--apply" in sys.argv
    staging = BCTN_DIR.parent / f"_bctn_tai_{date.today():%Y%m%d}"
    old_dir = BCTN_DIR.parent / "_bctn_cu"
    staging.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (research; SmartAudit-Quantum)"

    rows = []
    for ticker, year, rel in SOURCES:
        dst = staging / f"{ticker}_BCTN_{year}.pdf"
        if not dst.exists():
            try:
                resp = session.get(f"{BASE}/{rel}", timeout=180)
                if resp.status_code != 200:
                    rows.append((ticker, year, f"lỗi HTTP {resp.status_code}", 0))
                    continue
                dst.write_bytes(resp.content)
            except requests.RequestException as exc:
                rows.append((ticker, year, f"lỗi mạng: {exc.__class__.__name__}", 0))
                continue
        if dst.read_bytes()[:5] != b"%PDF-":
            rows.append((ticker, year, "không phải PDF", dst.stat().st_size))
            continue
        target = BCTN_DIR / ticker / f"{ticker}_BCTN_{year}.pdf"
        if target.exists() and sha256(target) == sha256(dst):
            status = "giống hệt tệp đang có"
        else:
            status = "khác tệp đang có" if target.exists() else "mới"
            if apply:
                # Thư mục dữ liệu gốc có thể không cho xoá tệp (quyền hệ
                # thống) nhưng cho ghi: sao lưu bản cũ rồi GHI ĐÈ nội dung.
                if target.exists():
                    backup = old_dir / ticker / target.name
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    if not backup.exists():
                        shutil.copy2(target, backup)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dst, target)  # mtime mới → bản chữ đã bóc tự bị coi là cũ
                for cache in (TEXT_CACHE / ticker).glob(f"{ticker}_{year}_*.txt"):
                    try:
                        cache.unlink()
                    except OSError:
                        pass  # không xoá được thì extract_text tự bỏ qua vì cũ hơn PDF
                status += " → đã thay"
        rows.append((ticker, year, status, dst.stat().st_size))

    for ticker, year, status, size in rows:
        print(f"{ticker} {year}  {size / 1e6:6.1f} MB  {status}")
    print(f"\nTổng: {len(rows)} · mới {sum('mới' in r[2] for r in rows)} · khác "
          f"{sum('khác' in r[2] for r in rows)} · giống hệt {sum('giống hệt' in r[2] for r in rows)} · "
          f"lỗi {sum(r[2].startswith(('lỗi', 'không')) for r in rows)}")
    if not apply:
        print("Chưa thay gì. Chạy lại với --apply để đưa vào data/raw/bctn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
