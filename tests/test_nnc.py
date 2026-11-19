"""Kiểm thử đối chiếu Narrative-Number Consistency."""

from __future__ import annotations

import pytest

from smartaudit.nnc import Verdict, build_facts, check_claim
from smartaudit.nnc.checker import Fact
from smartaudit.nlp import extract_claims
from smartaudit.tables import FinancialTable, Statement, TableRow


def claim_of(sentence: str, year: int = 2024):
    claims = extract_claims(f"===== PAGE 3 =====\n{sentence}\n", default_year=year)
    assert claims, f"Không trích được khẳng định từ: {sentence}"
    return claims[0]


@pytest.fixture
def facts() -> dict[str, Fact]:
    """Số liệu Vinamilk 2024, lấy từ báo cáo tài chính hợp nhất đã kiểm toán."""
    income = FinancialTable(page=10, statement=Statement.INCOME, rows=[
        TableRow("10", "Doanh thu thuần", [61_782_609_528_445, 60_368_915_511_505]),
        TableRow("11", "Giá vốn hàng bán", [36_192_433_205_321, 35_824_183_896_095]),
        TableRow("20", "Lợi nhuận gộp", [25_590_176_323_124, 24_544_731_615_410]),
        TableRow("25", "Chi phí bán hàng", [13_357_706_796_806, 13_018_093_111_879]),
        TableRow("60", "Lợi nhuận sau thuế", [9_452_892_989_948, 9_019_354_165_051]),
    ])
    balance = FinancialTable(page=7, statement=Statement.BALANCE, rows=[
        TableRow("140", "Hàng tồn kho", [5_526_000_000_000, 4_021_000_000_000]),
    ])
    return build_facts([income, balance])


class TestDoiChieuGiaTri:
    def test_con_so_khop_thi_nhat_quan(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần đạt 61.782 tỷ đồng."), facts)
        assert r.verdict is Verdict.CONSISTENT
        assert r.score == 1.0

    def test_con_so_lech_nho_thi_mau_thuan(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần đạt 65.000 tỷ đồng."), facts)
        assert r.verdict is Verdict.INCONSISTENT

    def test_lech_qua_lon_thi_khong_ket_luan_mau_thuan(self, facts) -> None:
        """Lệch vài chục lần gần như luôn là do nói về một bộ phận.

        Gắn cờ mâu thuẫn khi đó là cáo buộc sai doanh nghiệp.
        """
        r = check_claim(claim_of("Doanh thu thuần đạt 915 tỷ đồng."), facts)
        assert r.verdict is Verdict.UNVERIFIABLE
        assert "công ty con" in r.evidence[0].explanation


class TestDoiChieuHuong:
    def test_noi_tang_ma_tang_that(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần tăng so với cùng kỳ."), facts)
        assert r.verdict is Verdict.CONSISTENT

    def test_noi_giam_nhung_thuc_te_tang(self, facts) -> None:
        r = check_claim(claim_of("Chi phí bán hàng giảm so với năm trước."), facts)
        assert r.verdict is Verdict.INCONSISTENT
        assert any("tăng" in e.explanation for e in r.evidence)

    def test_ty_le_tang_truong_khop(self, facts) -> None:
        # (61.782 - 60.369) / 60.369 = 2,34%
        r = check_claim(claim_of("Doanh thu thuần tăng 2,3% so với cùng kỳ."), facts)
        assert r.verdict is Verdict.CONSISTENT

    def test_ty_le_tang_truong_sai(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần tăng 15,0% so với cùng kỳ."), facts)
        assert r.verdict is Verdict.INCONSISTENT


class TestDoiChieuDinhTinh:
    def test_kiem_soat_chi_phi_dung(self, facts) -> None:
        """Chi phí tăng 2,6% nhưng doanh thu tăng 2,3% -> tỷ lệ gần như không đổi."""
        r = check_claim(claim_of("Chi phí bán hàng được kiểm soát tốt."), facts)
        assert r.verdict is Verdict.CONSISTENT
        assert any(e.dimension == "qualitative" for e in r.evidence)

    def test_giai_thich_neu_ro_ty_le_tren_doanh_thu(self, facts) -> None:
        r = check_claim(claim_of("Chi phí bán hàng được kiểm soát tốt."), facts)
        text = " ".join(e.explanation for e in r.evidence)
        assert "trên doanh thu" in text and "điểm phần trăm" in text


class TestTySo:
    def test_bien_loi_nhuan_gop_khop(self, facts) -> None:
        # 25.590 / 61.782 = 41,4%
        r = check_claim(claim_of("Biên lợi nhuận gộp đạt 41,4%."), facts)
        assert r.verdict is Verdict.CONSISTENT

    def test_bien_loi_nhuan_gop_sai(self, facts) -> None:
        r = check_claim(claim_of("Biên lợi nhuận gộp đạt 55,0%."), facts)
        assert r.verdict is Verdict.INCONSISTENT

    def test_ty_so_khong_bi_so_voi_gia_tri_tuyet_doi(self, facts) -> None:
        """Câu nói về biên nhưng ta chỉ có giá trị tuyệt đối thì phải bỏ qua.

        So 25,8% với 13.358 tỷ đồng là vô nghĩa; từng gây ra thông báo lệch
        "1344749262216474 điểm phần trăm".
        """
        r = check_claim(
            claim_of("Tỷ lệ chi phí tài chính đạt 25,8% trên doanh thu."), facts
        )
        for e in r.evidence:
            assert "điểm phần trăm" not in e.explanation or abs(
                float(e.explanation.split("lệch")[-1].split("điểm")[0].strip())
            ) < 1000


class TestKhongKiemChungDuoc:
    def test_thieu_chi_tieu_trong_bao_cao(self, facts) -> None:
        r = check_claim(claim_of("Tổng tài sản đạt 55.000 tỷ đồng."), facts)
        assert r.verdict is Verdict.UNVERIFIABLE

    def test_giai_thich_neu_ly_do(self, facts) -> None:
        r = check_claim(claim_of("Tổng tài sản đạt 55.000 tỷ đồng."), facts)
        assert "không tìm thấy" in r.evidence[0].explanation.lower()


class TestVetTruyXuat:
    def test_moi_minh_chung_deu_co_nguon(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần đạt 61.782 tỷ đồng."), facts)
        for e in r.evidence:
            assert e.source_page is not None
            assert e.source_code is not None

    def test_giai_thich_co_ca_hai_con_so(self, facts) -> None:
        r = check_claim(claim_of("Doanh thu thuần đạt 65.000 tỷ đồng."), facts)
        explanation = r.evidence[0].explanation
        assert "65.000 tỷ" in explanation and "61.783 tỷ" in explanation


class TestTySoSuyRa:
    def test_tinh_duoc_bien_loi_nhuan_gop(self, facts) -> None:
        assert facts["gross_margin"].current == pytest.approx(0.4142, abs=1e-3)

    def test_tinh_duoc_vong_quay_hang_ton_kho(self, facts) -> None:
        assert facts["inventory_turnover"].current == pytest.approx(6.55, abs=0.05)


class TestDonViCuaConSo:
    """Phần trăm và tỷ số phải mang đúng đơn vị thì mới đối chiếu đúng."""

    def test_dat_muc_roi_giam_bao_nhieu_phan_tram(self, facts) -> None:
        """"đạt X, giảm Y%" là lối viết phổ biến nhất trong BCTN tiếng Việt.

        Lấy dấu theo xu hướng của cả câu (*đạt*) sẽ đem +Y% so với tăng
        trưởng âm và gắn cờ oan một câu hoàn toàn đúng.
        """
        r = check_claim(
            claim_of("Chi phí bán hàng đạt 13.358 tỷ đồng, tăng 2,6% so với cùng kỳ."),
            facts,
        )
        assert r.verdict is Verdict.CONSISTENT

    def test_giam_trong_cau_dat_van_bat_duoc_mau_thuan(self, facts) -> None:
        r = check_claim(
            claim_of("Doanh thu thuần đạt 61.782 tỷ đồng, giảm 2,3% so với cùng kỳ."),
            facts,
        )
        assert r.verdict is Verdict.INCONSISTENT

    def test_bien_tang_bao_nhieu_la_muc_thay_doi_khong_phai_muc(self, facts) -> None:
        """"Biên lợi nhuận gộp tăng 2,0%" nói về mức *thay đổi* của biên.

        Coi 2,0% là *giá trị* của biên sẽ báo lệch gần 40 điểm phần trăm.
        """
        # 24.545/60.369 = 40,66% -> 25.590/61.783 = 41,42%: +0,76 điểm.
        r = check_claim(claim_of("Biên lợi nhuận gộp tăng 0,8% so với cùng kỳ."), facts)
        assert r.verdict is Verdict.CONSISTENT
        assert all("lệch 39" not in e.explanation for e in r.evidence)

    def test_bien_thay_doi_sai_han_thi_van_gan_co(self, facts) -> None:
        r = check_claim(claim_of("Biên lợi nhuận gộp tăng 25,0% so với cùng kỳ."), facts)
        assert r.verdict is Verdict.INCONSISTENT

    def test_vong_quay_hien_bang_lan_khong_phai_phan_tram(self, facts) -> None:
        """6,55 lần từng bị in thành "655,0%" và "lệch 644,00 điểm phần trăm"."""
        r = check_claim(
            claim_of("Vòng quay hàng tồn kho tăng 5,0% so với cùng kỳ."), facts
        )
        text = " ".join(e.explanation for e in r.evidence)
        assert "lần" in text
        assert "655" not in text and "644" not in text

    def test_chenh_lech_ty_le_chi_phi_tinh_bang_diem_phan_tram(self, facts) -> None:
        """Chênh lệch in ra phải là điểm phần trăm, không phải phân số thô."""
        income = FinancialTable(page=10, statement=Statement.INCOME, rows=[
            TableRow("10", "Doanh thu thuần", [100_000_000_000, 100_000_000_000]),
            TableRow("25", "Chi phí bán hàng", [13_300_000_000, 10_000_000_000]),
        ])
        r = check_claim(
            claim_of("Chi phí bán hàng được kiểm soát tốt."), build_facts([income])
        )
        text = " ".join(e.explanation for e in r.evidence)
        # Chênh 3,3 điểm phần trăm, từng bị in thành "+0.0".
        assert "+3.3 điểm phần trăm" in text


class TestTySoKhongSoVoiChiTieuTien:
    def test_roe_khong_bi_so_voi_von_chu_so_huu(self, facts) -> None:
        """"ROE tăng gần 2%" nói về tỷ suất, không phải về vốn chủ sở hữu.

        Ontology chưa có ROE, nên chỉ tiêu khớp được là một khoản mục tiền.
        So mức tăng của tỷ suất với mức tăng của khoản mục là vô nghĩa.
        """
        r = check_claim(
            claim_of("Tỷ suất lợi nhuận trên doanh thu thuần tăng 2,0% so với cùng kỳ."),
            facts,
        )
        assert r.verdict is not Verdict.INCONSISTENT
