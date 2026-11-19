"""Kiểm thử hồi quy cho các bản vá nền trước Vòng 2 (19/11/2026).

Mỗi nhóm test ứng với một kiểu cờ oan đã định danh khi rà soát 141 cờ
"mâu thuẫn" của bản 21/09 (docs/demo/ung-vien-demo.md, mục 7).
"""

from __future__ import annotations

import pytest

from smartaudit.nlp import Trend, extract_claims
from smartaudit.nnc import Verdict, build_facts, check_claim
from smartaudit.tables import FinancialTable, Statement, TableRow, extract_tables
from smartaudit.tables.parser import _unit_scale


def one(sentence: str, year: int = 2024, page_extra: str = ""):
    text = f"===== PAGE 5 =====\n{page_extra}\n{sentence}\n"
    claims = extract_claims(text, default_year=year)
    return claims[0] if claims else None


def income(rows) -> list[FinancialTable]:
    return [FinancialTable(page=10, statement=Statement.INCOME,
                           rows=[TableRow(c, label, v) for c, label, v in rows])]


# ── GĐ 0.5: đơn vị tính của bảng ─────────────────────────────────────────

class TestDonViBang:
    def test_ngan_vnd_dung_rieng_mot_dong(self) -> None:
        assert _unit_scale("ngày 31 tháng 12 năm 2019  Ngàn VND  ", "<tr><td>Mã số</td></tr>") == 1e3

    def test_don_vi_tinh_trieu(self) -> None:
        assert _unit_scale("năm 2023  Đơn vị tính: triệu VND  ", "") == 1e6

    def test_don_vi_trong_tieu_de_cot(self) -> None:
        head = "<tr><td>Mã số</td><td>31/12/2024Triệu VND</td></tr>"
        assert _unit_scale("", head) == 1e6

    def test_cau_thuyet_minh_khong_bi_bat_nham(self) -> None:
        """'đầu tư 51.547 triệu VND theo…' là câu văn, không phải dòng đơn vị."""
        assert _unit_scale("Công ty đã đầu tư 51.547 triệu VND theo quyết định", "") is None

    def test_bang_duoc_quy_doi_ve_dong(self) -> None:
        doc = (
            "===== PAGE 8 =====\nBáo cáo kết quả hoạt động kinh doanh hợp nhất\nNgàn VND\n"
            "<table><tr><td>10</td><td>Doanh thu thuần</td><td>2.075.444.024</td>"
            "<td>5.388.200.400</td></tr></table>"
        )
        tables = extract_tables(doc)
        assert tables and tables[0].rows[0].current == pytest.approx(2_075_444_024e3)

    def test_ten_khoan_muc_giai_ma_html(self) -> None:
        doc = (
            "===== PAGE 8 =====\nBáo cáo kết quả hoạt động kinh doanh\n"
            "<table><tr><td>10</td><td>Doanh thu &quot;thuần&quot;</td><td>1.000</td>"
            "<td>900</td></tr></table>"
        )
        assert extract_tables(doc)[0].rows[0].label == 'Doanh thu "thuần"'


# ── Kiểu A: phạm vi hẹp hơn số hợp nhất ──────────────────────────────────

class TestPhamVi:
    def test_trang_gioi_thieu_don_vi_thanh_vien(self) -> None:
        """Ca Angkormilk, VNM 2024 trang 59."""
        page = "Lĩnh vực hoạt động chính: Trụ sở: Campuchia Vinamilk sở hữu: 100% Sản xuất sữa"
        assert one("Doanh thu và lợi nhuận 2024 tăng lần lượt 7,6% và 48,4% so với 2023.",
                   page_extra=page) is None

    def test_ten_cong_ty_con(self) -> None:
        assert one("Doanh thu của Angkormilk tăng 7,6% so với năm trước.") is None

    def test_cong_ty_me(self) -> None:
        assert one("Lợi nhuận sau thuế của công ty mẹ đạt 861 tỷ đồng.") is None


# ── Kiểu C: rác bố cục ──────────────────────────────────────────────────

def test_day_so_tran_la_rac_bo_cuc() -> None:
    assert one("Hàng tồn kho 2.70 2.71 2.70 2.60 giảm qua các năm.") is None


# ── Kiểu E: câu không phải kết quả ───────────────────────────────────────

class TestKhongPhaiKetQua:
    def test_chinh_sach_ke_toan(self) -> None:
        assert one("Dự phòng giảm giá hàng tồn kho được trích lập khi giá trị thuần giảm.") is None

    def test_gia_dinh_neu_se(self) -> None:
        assert one("Nếu lãi suất tăng 1% thì chi phí lãi vay sẽ tăng 120 tỷ đồng.") is None

    def test_hoan_thanh_ke_hoach_co_so_ket_qua_van_giu(self) -> None:
        c = one("Lợi nhuận trước thuế đạt 3.858 tỷ đồng, hoàn thành 110,7% kế hoạch năm.")
        assert c is not None and c.value == pytest.approx(3.858e12)


# ── Kiểu F: sai kỳ ───────────────────────────────────────────────────────

class TestKyBaoCao:
    def test_so_lieu_quy(self) -> None:
        assert one("Doanh thu hợp nhất quý 4 tăng xấp xỉ 10% so với cùng kỳ.") is None

    def test_so_voi_nam_xa(self) -> None:
        assert one("Doanh thu năm 2024 tăng gấp ba so với năm 2013.") is None

    def test_so_voi_nam_truoc_van_giu(self) -> None:
        c = one("So với năm 2023, doanh thu thuần tăng 2,3%.")
        assert c is not None and c.period == 2024


# ── Kiểu G: câu nhiều số ─────────────────────────────────────────────────

class TestNhieuSo:
    def test_tu_x_len_y_lay_so_nam_nay(self) -> None:
        c = one("Tổng tài sản tăng 6%, từ 90.781 tỷ đồng lên 96.113 tỷ đồng.")
        assert c is not None and c.value == pytest.approx(96.113e12)

    def test_bien_tu_x_len_y_la_muc(self) -> None:
        c = one("Biên lợi nhuận gộp toàn Tập đoàn tăng mạnh từ 11,8% lên 19,2%.")
        assert c is not None and c.percent == pytest.approx(19.2) and c.percent_is_level

    def test_tu_chi_huong_gan_chi_tieu(self) -> None:
        c = one("Duy trì lợi thế cạnh tranh, doanh thu thuần đạt 62.849 tỷ đồng.")
        assert c is not None and c.trend is Trend.REACH

    def test_ngan_ty(self) -> None:
        c = one("Doanh thu thuần đạt 118 ngàn tỷ đồng.")
        assert c is not None and c.value == pytest.approx(118e12)


# ── Kiểu H và dung sai làm tròn ──────────────────────────────────────────

class TestGanDung:
    @pytest.fixture
    def facts(self):
        return build_facts(income([
            ("10", "Doanh thu thuần", [6_679e9, 5_500e9]),
            ("60", "Lợi nhuận sau thuế", [1.94e9, 1.5e9]),
        ]))

    def test_tren_x_la_can_duoi(self, facts) -> None:
        r = check_claim(one("Doanh thu thuần đạt trên 6.600 tỷ đồng."), facts)
        assert r.verdict is Verdict.CONSISTENT

    def test_lam_tron_mot_chu_so_thap_phan(self, facts) -> None:
        r = check_claim(one("Lợi nhuận sau thuế đạt 1,9 tỷ đồng."), facts)
        assert r.verdict is Verdict.CONSISTENT


# ── Kiểu D, I và dữ liệu ─────────────────────────────────────────────────

class TestDoiChieu:
    def test_cau_ve_ty_so_khong_so_huong_voi_khoan_muc_tien(self) -> None:
        facts = build_facts([FinancialTable(page=7, statement=Statement.BALANCE, rows=[
            TableRow("400", "Vốn chủ sở hữu", [110e12, 100e12])])])
        r = check_claim(one("Hệ số nợ phải trả trên vốn chủ sở hữu giảm."), facts)
        assert r.verdict is not Verdict.INCONSISTENT

    def test_chi_phi_trong_ngoac_la_gia_tri_tuyet_doi(self) -> None:
        facts = build_facts(income([
            ("10", "Doanh thu thuần", [9_731e9, 9_000e9]),
            ("25", "Chi phí bán hàng", [-58_053e6, -92_716e6]),
        ]))
        assert facts["selling_expense"].growth == pytest.approx(-0.3739, abs=1e-3)
        r = check_claim(one("Chi phí bán hàng giảm 37,4% so với năm trước."), facts)
        assert r.verdict is Verdict.CONSISTENT

    def test_khong_co_ma_10_thi_lay_ma_01(self) -> None:
        """PC1 từ 2021 trình bày '20 = 01 − 11', không có Mã 10."""
        facts = build_facts(income([("01", "Doanh thu bán hàng", [10_000e9, 9_000e9])]))
        assert facts["revenue_net"].code == "01"

    def test_kiem_soat_chi_ap_cho_chi_phi(self) -> None:
        facts = build_facts(income([("10", "Doanh thu thuần", [100e9, 90e9])]) + [
            FinancialTable(page=7, statement=Statement.BALANCE, rows=[
                TableRow("140", "Hàng tồn kho", [50e9, 30e9])])])
        r = check_claim(one("Hàng tồn kho được kiểm soát tốt."), facts)
        assert r.verdict is Verdict.UNVERIFIABLE
