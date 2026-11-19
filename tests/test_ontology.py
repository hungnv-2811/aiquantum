"""Kiểm thử tra cứu ontology và đối chiếu trên dữ liệu thật."""

from __future__ import annotations

import pytest

from smartaudit.config import TINIX_DIR
from smartaudit.ontology import load_ontology
from smartaudit.tables import Statement, extract_tables

#: Các phép kiểm cần dữ liệu đã tải. Bỏ qua nếu chưa chạy fetch_data.py,
#: để người mới clone repo vẫn chạy được phần test còn lại.
needs_data = pytest.mark.skipif(
    not (TINIX_DIR / "ocr_results").is_dir(),
    reason="Chưa có dữ liệu — chạy: python scripts/fetch_data.py",
)


@pytest.fixture(scope="module")
def onto():
    return load_ontology()


class TestOntology:
    def test_nap_duoc_va_khong_rong(self, onto) -> None:
        assert len(onto) > 20

    def test_tra_theo_ma_so(self, onto) -> None:
        c = onto.by_code(Statement.INCOME, "10")
        assert c is not None and c.key == "revenue_net"

    def test_cung_ma_khac_bao_cao_ra_khoan_muc_khac(self, onto) -> None:
        income = onto.by_code(Statement.INCOME, "20")
        cash = onto.by_code(Statement.CASH_FLOW, "20")
        assert income.key == "gross_profit"
        assert cash.key == "cash_flow_operating"

    def test_ma_khong_ton_tai_tra_ve_none(self, onto) -> None:
        assert onto.by_code(Statement.INCOME, "999") is None

    def test_tra_theo_ten_chinh_xac(self, onto) -> None:
        c = onto.by_label(
            Statement.INCOME, "Doanh thu thuần về bán hàng và cung cấp dịch vụ"
        )
        assert c is not None and c.key == "revenue_net"

    def test_bo_qua_so_thu_tu_dau_dong(self, onto) -> None:
        c = onto.by_label(
            Statement.INCOME, "3. Doanh thu thuần về bán hàng và cung cấp dịch vụ"
        )
        assert c is not None and c.key == "revenue_net"

    def test_bo_qua_cong_thuc_cuoi_ten(self, onto) -> None:
        c = onto.by_label(
            Statement.INCOME,
            "Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)",
        )
        assert c is not None and c.key == "revenue_net"

    def test_ten_khong_lien_quan_thi_khong_khop(self, onto) -> None:
        assert onto.by_label(Statement.INCOME, "Tiền mặt tại quỹ") is None


@needs_data
class TestDuLieuThat:
    """Đối chiếu với con số đã kiểm chứng thủ công từ báo cáo gốc."""

    VNM_2024_DOANH_THU_THUAN = 61_782_609_528_445.0
    VNM_2024_GIA_VON = 36_192_433_205_321.0
    VNM_2024_LOI_NHUAN_GOP = 25_590_176_323_124.0

    @staticmethod
    @pytest.fixture(scope="class")
    def vnm2024():
        from smartaudit.ingest import iter_reports

        rep = next(
            r for r in iter_reports(tickers=["VNM"])
            if r.year == 2024 and r.consolidated
        )
        return extract_tables(rep.read())

    def _lay(self, tables, code: str) -> float:
        for t in tables:
            if t.statement is not Statement.INCOME:
                continue
            row = t.by_code(code)
            if row and row.current and abs(row.current) > 1e9:
                return row.current
        pytest.fail(f"Không tìm thấy mã {code} trong báo cáo KQKD")

    def test_doanh_thu_thuan_khop_bao_cao_goc(self, vnm2024) -> None:
        assert self._lay(vnm2024, "10") == self.VNM_2024_DOANH_THU_THUAN

    def test_loi_nhuan_gop_bang_doanh_thu_tru_gia_von(self, vnm2024) -> None:
        """Kiểm chứng nội tại: mã 20 = mã 10 − mã 11 theo Thông tư 200."""
        assert (
            self._lay(vnm2024, "10") - self._lay(vnm2024, "11")
            == pytest.approx(self.VNM_2024_LOI_NHUAN_GOP)
        )

    def test_bang_can_doi_ke_toan_can_bang(self, vnm2024) -> None:
        """Tổng tài sản (270) phải bằng tổng nguồn vốn (440)."""
        assets = liabilities_equity = None
        for t in vnm2024:
            if t.statement is not Statement.BALANCE:
                continue
            if (r := t.by_code("270")) and r.current:
                assets = r.current
            if (r := t.by_code("440")) and r.current:
                liabilities_equity = r.current
        if assets is None or liabilities_equity is None:
            pytest.skip("Báo cáo này không có đủ mã 270 và 440")
        assert assets == pytest.approx(liabilities_equity, rel=1e-6)


class TestTenMapMo:
    """Một tên bị hai khoản mục cùng nhận thì phải bỏ qua, không đoán bừa."""

    def test_khong_de_thu_tu_dong_trong_yaml_quyet_dinh(self, onto) -> None:
        """"Nợ ngắn hạn" bị cả mã 310 lẫn mã 330 nhận (biểu mẫu ngân hàng).

        Giữ bản gặp trước thì kết quả tra cứu do thứ tự dòng trong file
        quyết định chứ không do dữ liệu. Tra sai hại hơn tra trượt.
        """
        assert onto.by_label(Statement.BALANCE, "Nợ ngắn hạn") is None

    def test_ten_chi_mot_khoan_muc_nhan_thi_van_tra_duoc(self, onto) -> None:
        c = onto.by_label(Statement.BALANCE, "Nợ dài hạn")
        assert c is not None and c.key == "non_current_liabilities"

    def test_ten_khoan_muc_cua_bao_cao_khac_khong_lan_sang(self, onto) -> None:
        """"Lợi nhuận trước thuế" là mã 01 của LCTT, không phải doanh thu gộp."""
        c = onto.by_label(Statement.INCOME, "Lợi nhuận trước thuế")
        assert c is not None and c.key == "profit_before_tax"
