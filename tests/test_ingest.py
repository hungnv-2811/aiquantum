"""Kiểm thử nhận diện báo cáo tài chính và dựng chuỗi số liệu theo năm."""

from __future__ import annotations

from pathlib import Path

import pytest

from smartaudit.ingest.tinix import Report, iter_reports
from smartaudit.labels.restatement import collect_series


def _corpus(root: Path, *names: str) -> Path:
    """Dựng cây thư mục giống bộ TiniX với các tên file cho trước."""
    for name in names:
        ticker, year, stem = name.split("/")
        target = root / "ocr_results" / ticker / year / f"{stem}_extracted.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
    return root


class TestNhanDienLoaiBaoCao:
    """Tên file cho biết báo cáo hợp nhất hay riêng công ty mẹ.

    Nhận nhầm không dừng ở một nhãn sai: báo cáo riêng công ty mẹ lọt vào
    nhóm "không xác định" sẽ bị đem so với báo cáo hợp nhất của năm liền
    kề, sinh ra hàng loạt hồi tố ảo trong nhãn yếu.
    """

    @pytest.mark.parametrize(
        "stem,expected",
        [
            ("FPT_Baocaotaichinh_2015_Kiemtoan_Hopnhat", True),
            ("FPT_Baocaotaichinh_2015_Kiemtoan_Congtyme", False),
            # Ngăn từ bằng khoảng trắng, gạch nối, dấu chấm.
            ("MBB.CBTT - BCTC hop nhat kiem toan 2022 - signed", True),
            ("MBB.CBTT - BCTC rieng le kiem toan nam 2022 - signed", False),
            ("BCTC-Hop-nhat-2022", True),
            ("BCTC-Rieng-le-2022", False),
            ("bao-cao-tai-chinh-hop-nhat-nam-2024-da-kiem-toan-1", True),
            # Viết hoa, và tên tiếng Anh.
            ("3.VCG_2020.4.3_f2a42eb_BCTC_RIENG_da_ky", False),
            ("vcg-audited-consol-vfs-31122024-signed", True),
            # Tên gốc "Riêng lẻ" bị hỏng lúc tải lên.
            ("VPBank 31.12.2023 - BCTC VAS Riêng l_", False),
            # Không dấu hiệu nào -> không kết luận.
            ("2.VCG_2019.3.15_7f4acf6_Bao_cao_VCG_Khong_mau_signed", None),
        ],
    )
    def test_phan_loai_theo_ten_file(
        self, tmp_path: Path, stem: str, expected: bool | None
    ) -> None:
        root = _corpus(tmp_path, f"VCG/2020/{stem}")
        report = next(iter_reports(root=root))
        assert report.consolidated is expected

    def test_ten_tu_mau_thuan_thi_khong_ket_luan(self, tmp_path: Path) -> None:
        root = _corpus(tmp_path, "VCG/2020/BCTC_hop_nhat_va_rieng_le_2020")
        assert next(iter_reports(root=root)).consolidated is None

    def test_nhan_dien_da_kiem_toan(self, tmp_path: Path) -> None:
        root = _corpus(
            tmp_path,
            "VCG/2020/BCTC hop nhat kiem toan 2020",
            "VCG/2021/vcg-audited-consol-2021",
        )
        assert all(r.audited for r in iter_reports(root=root))


class _FakeReport(Report):
    """Báo cáo giả lập, trả về nội dung dựng sẵn thay vì đọc file."""

    def __init__(self, ticker: str, year: int, text: str) -> None:
        super().__init__(
            ticker=ticker, year=year, path=Path(f"{ticker}_{year}.txt"),
            consolidated=True, audited=True,
        )
        object.__setattr__(self, "_text", text)

    def read(self) -> str:
        return self._text


def _income(*rows: tuple[str, str, int, int]) -> str:
    cells = "".join(
        f"<tr><td>{label}</td><td>{code}</td>"
        f"<td>{cur:,}</td><td>{prev:,}</td></tr>".replace(",", ".")
        for code, label, cur, prev in rows
    )
    return (
        "===== PAGE 10 =====\nBáo cáo kết quả hoạt động kinh doanh\n"
        f"<table>{cells}</table>"
    )


class TestChuoiSoLieuTheoNam:
    """Một (mã, năm, loại báo cáo) có thể ứng với nhiều file."""

    FULL = _income(
        ("10", "Doanh thu thuần", 61_782_609_528_445, 60_368_915_511_505),
        ("20", "Lợi nhuận gộp", 25_590_176_323_124, 24_544_731_615_410),
        ("50", "Lợi nhuận trước thuế", 12_000_000_000_000, 11_000_000_000_000),
    )
    SPARSE = _income(
        ("10", "Doanh thu thuần", 9_731_000_000_000, 9_000_000_000_000),
    )

    def test_giu_ban_boc_duoc_nhieu_khoan_muc_hon(self) -> None:
        """Ghi đè lặng lẽ thì bản nghèo nhất vẫn thắng nếu tên file sắp sau."""
        series = collect_series([
            _FakeReport("VNM", 2024, self.FULL),
            _FakeReport("VNM", 2024, self.SPARSE),
        ])
        values = series[("VNM", True)][2024]
        assert len(values) == 3
        assert values["revenue_net"][0] == 61_782_609_528_445

    def test_khong_phu_thuoc_thu_tu_gap(self) -> None:
        reversed_order = collect_series([
            _FakeReport("VNM", 2024, self.SPARSE),
            _FakeReport("VNM", 2024, self.FULL),
        ])
        assert len(reversed_order[("VNM", True)][2024]) == 3
