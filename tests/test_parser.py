"""Kiểm thử bóc tách bảng số liệu."""

from __future__ import annotations

import pytest

from smartaudit.ingest.vietstock import find_columns
from smartaudit.tables import Statement, extract_tables, parse_number, strip_accents


class TestParseNumber:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("61.782.609.528.445", 61_782_609_528_445.0),
            ("1.234", 1234.0),
            ("(1.234.567)", -1_234_567.0),
            ("-8.200", -8200.0),
            ("12,5", 12.5),
            ("0", 0.0),
            ("10", 10.0),
        ],
    )
    def test_doc_so_hop_le(self, text: str, expected: float) -> None:
        assert parse_number(text) == expected

    @pytest.mark.parametrize(
        "text", ["", "   ", "Thuyết minh", "VI.1", "n/a", "—", "abc123"]
    )
    def test_bo_qua_chuoi_khong_phai_so(self, text: str) -> None:
        assert parse_number(text) is None


class TestStripAccents:
    def test_bo_dau_tieng_viet(self) -> None:
        assert strip_accents("LƯU CHUYỂN TIỀN TỆ") == "LUU CHUYEN TIEN TE"

    def test_xu_ly_chu_d_gach(self) -> None:
        assert strip_accents("Đầu tư") == "Dau tu"

    def test_chiu_duoc_loi_ocr_dat_sai_dau(self) -> None:
        # OCR hay đánh rơi dấu; bản không dấu phải trùng nhau.
        assert strip_accents("LƯU CHUYÊN TIÊN TỆ") == strip_accents("LƯU CHUYỂN TIỀN TỆ")


def _doc(heading: str, rows: str) -> str:
    return f"===== PAGE 10 =====\n{heading}\n<table>{rows}</table>"


class TestExtractTables:
    ROW = (
        "<tr><td>Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)</td>"
        "<td>10</td><td>VI.1</td>"
        "<td>61.782.609.528.445</td><td>60.368.915.511.505</td></tr>"
    )

    def test_boc_duoc_ma_nhan_va_gia_tri(self) -> None:
        tables = extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", self.ROW))
        assert len(tables) == 1
        row = tables[0].by_code("10")
        assert row is not None
        assert row.current == 61_782_609_528_445.0
        assert row.previous == 60_368_915_511_505.0
        assert "Doanh thu thuần" in row.label

    def test_ghi_nhan_so_trang_de_truy_vet(self) -> None:
        tables = extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", self.ROW))
        assert tables[0].page == 10

    def test_nhan_dien_loai_bao_cao_chu_thuong(self) -> None:
        # Nhiều doanh nghiệp dùng tiêu đề chữ thường thay vì in hoa.
        tables = extract_tables(
            _doc("Báo cáo kết quả hoạt động kinh doanh riêng "
                 "cho năm kết thúc ngày 31 tháng 12 năm 2016", self.ROW)
        )
        assert tables[0].statement is Statement.INCOME

    def test_bo_qua_dong_muc_luc(self) -> None:
        # Dòng mục lục kết thúc bằng số trang, không phải tiêu đề phần.
        text = _doc("BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH RIÊNG 9", self.ROW)
        assert extract_tables(text) == []

    def test_khong_nham_cau_chan_trang_la_tieu_de(self) -> None:
        # Câu này lặp ở chân mọi trang và có chứa chữ "thuyết minh";
        # nếu bị chấm là tiêu đề thì bảng sẽ bị loại oan.
        text = _doc(
            "Báo cáo kết quả hoạt động kinh doanh cho năm kết thúc "
            "ngày 31 tháng 12 năm 2024\n"
            "Các thuyết minh đính kèm là bộ phận hợp thành của báo cáo này",
            self.ROW,
        )
        tables = extract_tables(text)
        assert tables and tables[0].statement is Statement.INCOME

    def test_loai_bang_trong_phan_thuyet_minh(self) -> None:
        # Trong thuyết minh, cột số đầu là số hiệu thuyết minh chứ không
        # phải mã số khoản mục — đọc vào sẽ ra dữ liệu sai.
        text = _doc("Thuyết minh báo cáo tài chính hợp nhất", self.ROW)
        assert extract_tables(text) == []

    def test_khong_doc_nham_so_thuyet_minh_thanh_gia_tri(self) -> None:
        """Cột 'Thuyết minh' ghi số trần phải bị loại, không phải giá trị.

        Bố cục: [tên | mã số | thuyết minh | năm nay | năm trước].
        FPT ghi thuyết minh là '26' (số trần) thay vì 'VI.1' như Vinamilk;
        nếu đọc nhầm thì doanh thu 52.618 tỷ bị thay bằng 26.
        """
        row = (
            "<tr><td>Doanh thu thuần về bán hàng và cung cấp dịch vụ</td>"
            "<td>10</td><td>26</td>"
            "<td>52.618.472.939.181</td><td>44.010.031.181.988</td></tr>"
        )
        tables = extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", row))
        parsed = tables[0].by_code("10")
        assert parsed.current == 52_618_472_939_181.0
        assert parsed.previous == 44_010_031_181_988.0

    def test_giu_nguyen_gia_tri_nho_hop_le(self) -> None:
        """Giá trị nhỏ nhưng cùng cỡ với nhau thì không được cắt."""
        row = (
            "<tr><td>Lãi cơ bản trên cổ phiếu</td><td>70</td>"
            "<td>4.517</td><td>4.075</td></tr>"
        )
        tables = extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", row))
        parsed = tables[0].by_code("70")
        assert parsed.current == 4517.0 and parsed.previous == 4075.0

    def test_bo_qua_hang_khong_du_ma_nhan_gia_tri(self) -> None:
        rows = (
            "<tr><td>Mã số</td><td>CHỈ TIÊU</td><td>Năm nay</td></tr>"
            "<tr><td></td><td></td><td></td></tr>"
        )
        assert extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", rows)) == []

    def test_cung_ma_khac_bao_cao_thi_khac_nghia(self) -> None:
        """Mã 10 là Doanh thu thuần ở KQKD, Biến động tồn kho ở LCTT."""
        inventory = (
            "<tr><td>Biến động hàng tồn kho</td><td>10</td>"
            "<td>(1.500.000)</td><td>2.300.000</td></tr>"
        )
        income = extract_tables(_doc("Báo cáo kết quả hoạt động kinh doanh", self.ROW))
        cash = extract_tables(_doc("Báo cáo lưu chuyển tiền tệ", inventory))

        assert income[0].statement is Statement.INCOME
        assert cash[0].statement is Statement.CASH_FLOW
        # Cùng mã "10" nhưng thuộc hai báo cáo khác nhau -> không được lẫn.
        assert income[0].by_code("10").current != cash[0].by_code("10").current


class TestSoKhongCuaKyNay:
    """Số ``0`` đứng đầu là giá trị thật, không phải số hiệu thuyết minh."""

    def test_giu_gia_tri_khong_cua_ky_nay(self) -> None:
        """Khoản mục không phát sinh trong năm vẫn phải đọc ra 0.

        Bỏ số 0 đi sẽ đôn số năm trước sang cột năm nay và tạo ra một
        khẳng định sai hoàn toàn về kỳ hiện tại.
        """
        row = (
            "<tr><td>Chi phí tài chính</td><td>22</td>"
            "<td>0</td><td>1.234.567.890.000</td></tr>"
        )
        parsed = extract_tables(
            _doc("Báo cáo kết quả hoạt động kinh doanh", row)
        )[0].by_code("22")
        assert parsed.current == 0.0
        assert parsed.previous == 1_234_567_890_000.0

    def test_van_bo_so_hieu_thuyet_minh(self) -> None:
        row = (
            "<tr><td>Doanh thu thuần</td><td>10</td>"
            "<td>26</td><td>52.618.000.000.000</td><td>44.010.000.000.000</td></tr>"
        )
        parsed = extract_tables(
            _doc("Báo cáo kết quả hoạt động kinh doanh", row)
        )[0].by_code("10")
        assert parsed.current == 52_618_000_000_000.0


class TestNhanDienLoaiBaoCao:
    ROW = "<tr><td>Lợi nhuận trước thuế</td><td>01</td><td>959.188</td><td>236.801</td></tr>"

    def test_chiu_duoc_dau_nhay_ocr_chen_giua_tu(self) -> None:
        """OCR đọc ``LƯU`` thành ``LU'U`` — tiêu đề vẫn phải nhận ra."""
        tables = extract_tables(_doc("BÁO CÁO LU'U CHUYÊN TIỀN TỆ RIÊNG", self.ROW))
        assert tables[0].statement is Statement.CASH_FLOW

    def test_dung_ma_bieu_mau_khi_tieu_de_ghi_nham(self) -> None:
        """MSN 2015 ghi nhầm tiêu đề báo cáo lưu chuyển tiền tệ.

        Chỉ mã biểu mẫu ``B 03`` cho biết đó thật ra là báo cáo nào.
        """
        heading = (
            "Báo cáo kết quả hoạt động kinh doanh cho năm kết thúc ngày "
            "31 tháng 12 năm 2015\nMẫu B 03 - DN/HN"
        )
        assert extract_tables(_doc(heading, self.ROW))[0].statement is Statement.CASH_FLOW

    def test_ma_bieu_mau_nhan_duoc_bao_cao_tieng_anh(self) -> None:
        row = (
            "<tr><td>Cash and cash equivalents</td><td>110</td>"
            "<td>1.000.000.000</td><td>900.000.000</td></tr>"
        )
        tables = extract_tables(_doc("CONSOLIDATED BALANCE SHEET\nFORM B 01-DN", row))
        assert tables[0].statement is Statement.BALANCE


class TestTachCot:
    """Cột hẹp phải được gộp vào cột liền kề, không được vứt đi."""

    @staticmethod
    def _words(*spans):
        return [{"x0": a, "x1": b} for a, b in spans]

    def test_hai_cot_rong_giu_nguyen(self) -> None:
        assert find_columns(self._words((50, 200), (260, 420)), 500) == [
            (50.0, 200.0), (260.0, 420.0),
        ]

    def test_dai_hep_duoc_gop_chu_khong_bi_bo(self) -> None:
        """Hộp số liệu hẹp bị bỏ là mất trắng mọi khẳng định in trong đó."""
        assert find_columns(self._words((50, 200), (260, 300)), 500) == [(50.0, 300.0)]

    def test_dai_hep_ngoai_cung_ben_trai(self) -> None:
        assert find_columns(self._words((10, 40), (100, 300)), 500) == [(10.0, 300.0)]

    def test_trang_khong_co_chu(self) -> None:
        assert find_columns([], 500) == [(0.0, 500)]
