"""Nạp bộ TiniX Vietnam OCR Annual Financial Statements từ HuggingFace.

Bộ dữ liệu: ``tinixai/ocr_annual_financials`` — 18.231 báo cáo tài chính
của 1.491 mã chứng khoán, giai đoạn 2015–2025, giấy phép CC-BY-NC-4.0.

Cấu trúc trên HuggingFace::

    ocr_results/<TICKER>/<NĂM>/<TÊN_BÁO_CÁO>/<TÊN_BÁO_CÁO>_extracted.txt
    pdf_files/<TICKER>/<NĂM>/<TÊN_BÁO_CÁO>.pdf

Module này **chỉ tải nhánh ``ocr_results``**. Toàn bộ 16 mã trong
:data:`smartaudit.config.TICKERS` chỉ nặng khoảng 65 MB, trong khi bản PDF
gốc tương ứng là 2,16 GB. Không cần PDF vì văn bản OCR đã giữ nguyên bảng
biểu dưới dạng HTML ``<table>`` kèm cột Mã số theo Thông tư 200.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from smartaudit.config import TICKERS, TINIX_DIR, TINIX_REPO

# Tên file báo cáo cho biết đây là báo cáo hợp nhất hay riêng công ty mẹ.
#
# Khớp trên tên đã chuẩn hoá (xem :func:`_normalise_stem`), nên một mẫu duy
# nhất bắt được mọi cách ngăn từ mà corpus thật dùng: ``Kiemtoan_Hopnhat``,
# ``BCTC hop nhat kiem toan 2022``, ``BCTC-Hop-nhat-2022``,
# ``bao-cao-tai-chinh-hop-nhat-nam-2024``.
#
# Phân loại sai ở đây không dừng lại ở một nhãn sai: báo cáo riêng công ty
# mẹ lọt vào nhóm "không xác định" sẽ bị đem so với báo cáo hợp nhất của
# năm liền kề, sinh ra hàng loạt hồi tố ảo trong nhãn yếu. Riêng VCG từng
# tạo 4 nhãn ảo kiểu đó, trong đó doanh thu "bị hồi tố" 73,7%.
_CONSOLIDATED = re.compile(r"hopnhat|consol")
# ``rieng`` một mình là đủ: corpus có ``Rieng-le``, ``BCTC_RIENG_da_ky`` và
# cả ``Riêng l_`` (tên gốc ``Riêng lẻ`` bị hỏng lúc tải lên, xem _safe_path).
_PARENT = re.compile(r"congtyme|rieng")
# Nhiều báo cáo có chữ "Kiemtoan" trong tên -> đã qua kiểm toán.
_AUDITED = re.compile(r"kiemtoan|audited")

#: Ký tự không phải chữ hoặc số, dùng để gộp mọi cách ngăn từ về một mối.
_SEPARATOR = re.compile(r"[^a-z0-9]+")


def _normalise_stem(stem: str) -> str:
    """Chuẩn hoá tên file để so khớp không phụ thuộc dấu và cách ngăn từ.

    >>> _normalise_stem("MBB.CBTT - BCTC hop nhat kiem toan 2022 - signed")
    'mbbcbttbctchopnhatkiemtoan2022signed'
    >>> _normalise_stem("VPBank 31.12.2023 - BCTC VAS Riêng l_")
    'vpbank31122023bctcvasriengl'
    """
    from smartaudit.tables import strip_accents

    return _SEPARATOR.sub("", strip_accents(stem).lower())


@dataclass(frozen=True)
class Report:
    """Một báo cáo tài chính đã trích xuất văn bản."""

    ticker: str
    year: int
    path: Path
    #: True nếu là báo cáo hợp nhất, False nếu là báo cáo riêng công ty mẹ,
    #: None nếu không xác định được từ tên file.
    consolidated: bool | None
    #: True nếu tên file cho thấy báo cáo đã qua kiểm toán.
    audited: bool

    @property
    def name(self) -> str:
        return self.path.stem.removesuffix("_extracted")

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8", errors="replace")


#: Ký tự Windows không cho phép đặt trong tên file hoặc thư mục.
_ILLEGAL = re.compile(r'[<>:"|?*]')


def _safe_path(dest: Path, repo_path: str) -> Path:
    """Chuyển đường dẫn trên repo thành đường dẫn hợp lệ dưới Windows.

    Bộ TiniX có file mà tên chứa dấu ``?`` — nhiều khả năng do ký tự tiếng
    Việt bị hỏng lúc tải lên (``BCTC VAS Riêng l?`` đáng lẽ là ``Riêng lẻ``).
    Windows cấm ký tự này nên ``snapshot_download`` sẽ dừng với WinError 123.
    Ta thay bằng dấu gạch dưới; nội dung file không đổi.
    """
    return dest.joinpath(*(_ILLEGAL.sub("_", part) for part in repo_path.split("/")))


def download_tickers(
    tickers: list[str] | None = None,
    dest: Path | None = None,
) -> Path:
    """Tải phần văn bản OCR của các mã chỉ định về máy.

    Liệt kê cây thư mục của từng mã rồi tải trực tiếp từng file, thay vì
    dùng ``snapshot_download``. Lý do: cần làm sạch tên file cho hợp lệ
    dưới Windows (xem :func:`_safe_path`), việc mà ``snapshot_download``
    không cho can thiệp.

    Chỉ tải nhánh ``ocr_results`` — khoảng 65 MB cho 16 mã, so với 2,16 GB
    nếu lấy cả PDF gốc. Bỏ qua file đã có sẵn nên gọi lại nhiều lần an toàn.

    Trả về thư mục gốc chứa dữ liệu đã tải.
    """
    import requests
    from huggingface_hub import HfApi, hf_hub_url

    tickers = tickers or TICKERS
    dest = dest or TINIX_DIR
    dest.mkdir(parents=True, exist_ok=True)

    api = HfApi()
    session = requests.Session()

    for ticker in tickers:
        try:
            entries = api.list_repo_tree(
                TINIX_REPO,
                path_in_repo=f"ocr_results/{ticker}",
                repo_type="dataset",
                recursive=True,
            )
        except Exception as exc:  # mã không có trong dataset
            print(f"  {ticker}: bỏ qua ({exc.__class__.__name__})")
            continue

        files = [e for e in entries if getattr(e, "size", None) is not None]
        fetched = skipped = 0

        for entry in files:
            target = _safe_path(dest, entry.path)
            if target.exists() and target.stat().st_size == entry.size:
                skipped += 1
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            url = hf_hub_url(TINIX_REPO, entry.path, repo_type="dataset")
            with session.get(url, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                # Ghi ra file tạm rồi đổi tên, tránh để lại file dở dang
                # nếu quá trình tải bị ngắt giữa chừng.
                tmp = target.with_suffix(target.suffix + ".part")
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 16):
                        fh.write(chunk)
                tmp.replace(target)
            fetched += 1

        print(f"  {ticker}: {fetched} tải mới, {skipped} đã có")

    return dest


def iter_reports(
    root: Path | None = None,
    tickers: list[str] | None = None,
) -> Iterator[Report]:
    """Duyệt các báo cáo đã tải, sắp xếp theo mã rồi tới năm.

    Bỏ qua thư mục của mã không nằm trong ``tickers`` (nếu có truyền vào)
    và các file không phải ``*_extracted.txt``.
    """
    root = root or TINIX_DIR
    ocr_root = root / "ocr_results"
    if not ocr_root.is_dir():
        raise FileNotFoundError(
            f"Chưa có dữ liệu tại {ocr_root}. Chạy download_tickers() trước."
        )

    wanted = set(tickers) if tickers else None

    for ticker_dir in sorted(ocr_root.iterdir()):
        if not ticker_dir.is_dir():
            continue
        if wanted and ticker_dir.name not in wanted:
            continue

        for year_dir in sorted(ticker_dir.iterdir()):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue

            for txt in sorted(year_dir.rglob("*_extracted.txt")):
                stem = _normalise_stem(txt.stem)
                is_consolidated = bool(_CONSOLIDATED.search(stem))
                is_parent = bool(_PARENT.search(stem))
                # Không dấu hiệu nào, hoặc có cả hai (tên tự mâu thuẫn) thì
                # không kết luận, thay vì đoán theo thứ tự xét.
                consolidated: bool | None = (
                    None if is_consolidated == is_parent else is_consolidated
                )

                yield Report(
                    ticker=ticker_dir.name,
                    year=int(year_dir.name),
                    path=txt,
                    consolidated=consolidated,
                    audited=bool(_AUDITED.search(stem)),
                )
