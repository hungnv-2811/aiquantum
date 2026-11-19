"""Kiểm thử trích xuất khẳng định từ ngôn từ báo cáo."""

from __future__ import annotations

from smartaudit.nlp import Trend, extract_claims


def one(sentence: str, year: int = 2024):
    """Trích claim từ một câu, trả về claim đầu tiên hoặc None."""
    claims = extract_claims(f"===== PAGE 5 =====\n{sentence}\n", default_year=year)
    return claims[0] if claims else None


class TestTrichXuatCoBan:
    def test_doc_gia_tri_va_don_vi(self) -> None:
        # Năm của câu phải khớp năm báo cáo: câu kể kết quả 2018 trong báo cáo
        # 2024 là lịch sử, BCTC 2024 không kiểm được (xem test_ky_bao_cao).
        c = one("Kết thúc năm 2018, lợi nhuận trước thuế đạt 3.858 tỷ đồng.", year=2018)
        assert c is not None
        assert c.metric == "profit_before_tax"
        assert c.value == 3.858e12
        assert c.trend is Trend.REACH
        assert c.period == 2018

    def test_doc_ty_le_phan_tram(self) -> None:
        c = one("Doanh thu thuần năm 2024 tăng 12,6% so với cùng kỳ.")
        assert c is not None
        assert c.metric == "revenue_net"
        assert c.trend is Trend.UP
        assert c.percent == 12.6
        assert c.basis == "cùng kỳ"

    def test_ghi_nhan_so_trang(self) -> None:
        c = one("Doanh thu thuần đạt 61.782 tỷ đồng.")
        assert c is not None and c.page == 5

    def test_uu_tien_cum_dai_hon(self) -> None:
        """'doanh thu thuần' không được đọc nhầm thành 'doanh thu'."""
        c = one("Doanh thu thuần đạt 61.782 tỷ đồng.")
        assert c is not None and c.metric == "revenue_net"

    def test_giu_khang_dinh_dinh_tinh(self) -> None:
        """Câu không có số vẫn giữ — đây là loại mâu thuẫn ngầm cần bắt."""
        c = one("Chi phí bán hàng được kiểm soát tốt trong năm.")
        assert c is not None
        assert c.metric == "selling_expense"
        assert c.trend is Trend.CONTROLLED
        assert not c.quantitative

    def test_dau_cham_ngan_nghin_khong_cat_cau(self) -> None:
        """Dấu chấm trong 10.983 là ngăn nghìn, không phải hết câu."""
        c = one("Doanh thu thuần cả năm đạt 10.983 tỷ đồng, tăng 12,6%.")
        assert c is not None and c.value == 10.983e12


class TestLocNhieu:
    def test_loai_so_lieu_ben_thu_ba(self) -> None:
        assert one(
            "Theo báo cáo của MarketsandMarkets, thị trường tăng trưởng 19%."
        ) is None

    def test_loai_chi_tieu_vi_mo(self) -> None:
        assert one(
            "Tổng mức bán lẻ hàng hóa và doanh thu dịch vụ giảm 3,8% so với năm trước."
        ) is None

    def test_loai_khang_dinh_ve_cong_ty_con(self) -> None:
        assert one(
            "Tổng doanh thu Driftwood đạt hơn 116,2 triệu USD, tăng 8%."
        ) is None

    def test_loai_khang_dinh_ve_mang_kinh_doanh(self) -> None:
        assert one(
            "Doanh thu thuần thị trường nước ngoài đạt 10.983 tỷ đồng, tăng 12,6%."
        ) is None

    def test_loai_tham_chieu_cong_ty_viet_tat(self) -> None:
        assert one("Biên lợi nhuận ròng của MCM đạt 10,9%, cải thiện so với cùng kỳ.") is None

    def test_loai_manh_vun_bo_cuc(self) -> None:
        assert one("» TV HĐQT công ty liên doanh, doanh thu tăng trưởng tốt.") is None

    def test_loai_cau_toan_chu_hoa(self) -> None:
        assert one("DOANH THU ĐẠT 5.561 TỶ ĐỒNG TRONG NĂM 2020, TĂNG 8%.") is None

    def test_loai_muc_tieu_tuong_lai(self) -> None:
        """Chỉ tiêu đặt ra cho năm sau, không phải kết quả đã đạt."""
        assert one(
            "Doanh thu và lợi nhuận trước thuế dự kiến tăng trưởng 17,5% và 18,2%."
        ) is None

    def test_loai_khang_dinh_bang_ngoai_te(self) -> None:
        assert one(
            "Thị trường Nhật Bản ghi nhận doanh thu tăng 52,2% theo Yên Nhật."
        ) is None

    def test_loai_khang_dinh_tren_co_so_dieu_chinh(self) -> None:
        """FPT 2018: doanh thu thô giảm 45,6% do thoái vốn bán lẻ, nhưng
        'trong điều kiện so sánh tương đương' thì tăng 17,4%. Cả hai đều
        đúng; không tính lại được cơ sở tương đương từ báo cáo tài chính."""
        assert one(
            "Doanh thu tăng trưởng 17,4% trong điều kiện so sánh tương đương."
        ) is None

    def test_loai_tang_truong_kep_nhieu_nam(self) -> None:
        assert one(
            "Doanh thu chuyển đổi số có tốc độ tăng trưởng kép bình quân "
            "hàng năm là 57,7%."
        ) is None

    def test_ty_trong_la_ty_so_khong_phai_gia_tri(self) -> None:
        c = one("Tỷ trọng doanh thu phần mềm tăng lên trong cơ cấu doanh thu.")
        assert c is not None and c.is_ratio

    def test_loai_muc_hoan_thanh_ke_hoach(self) -> None:
        """Báo cáo tài chính không chứa kế hoạch nội bộ để đối chiếu."""
        assert one("Lợi nhuận sau thuế hoàn thành 94,6% kế hoạch năm.") is None

    def test_loai_cau_ve_chinh_sach(self) -> None:
        """'duy trì' gắn với chính sách, không phải với giá trị tồn kho."""
        assert one(
            "Công ty duy trì chính sách quản lý hàng tồn kho và công nợ ổn định."
        ) is None


class TestRanhGioiTu:
    """Khớp cụm từ phải theo ranh giới từ, không khớp chuỗi con."""

    def test_giam_doc_khong_bi_hieu_la_giam(self) -> None:
        """'giám đốc' bỏ dấu thành 'giam doc' — chứa 'giam'."""
        c = one("Tổng Giám đốc cho biết doanh thu năm nay tăng 12,6%.")
        assert c is not None
        assert c.trend is Trend.UP, "bị nhận nhầm xu hướng từ chữ 'Giám đốc'"

    def test_uu_tien_cum_dai_khi_cung_vi_tri(self) -> None:
        c = one("Doanh thu ghi nhận tăng trưởng 12,6% so với cùng kỳ.")
        assert c is not None and c.trend is Trend.UP

    def test_sut_giam_khong_thanh_giam(self) -> None:
        c = one("Doanh thu thuần sụt giảm 8,0% so với cùng kỳ.")
        assert c is not None and c.trend is Trend.DOWN


class TestTySo:
    def test_nhan_dien_bien_loi_nhuan_gop(self) -> None:
        c = one("Biên lợi nhuận gộp đạt 42,0% trong năm 2024.")
        assert c is not None
        assert c.metric == "gross_margin"
        assert c.is_ratio

    def test_vong_quay_hang_ton_kho_khong_phai_gia_tri(self) -> None:
        """'vòng quay hàng tồn kho' nói về số vòng, không phải giá trị kho."""
        c = one("Chỉ số vòng quay hàng tồn kho giảm nhẹ so với năm trước.")
        assert c is not None
        assert c.metric == "inventory_turnover"
        assert c.is_ratio

    def test_gia_tri_tuyet_doi_khong_bi_coi_la_ty_so(self) -> None:
        c = one("Hàng tồn kho cuối năm đạt 5.526 tỷ đồng.")
        assert c is not None
        assert c.metric == "inventories"
        assert not c.is_ratio


class TestGanSoVoiNgamCanh:
    """Con số phải gắn với từ chi phối nó, không phải với cả câu."""

    def test_phan_tram_lay_huong_cua_tu_dung_truoc_no(self) -> None:
        """"đạt X, giảm Y%" — xu hướng của câu là *đạt*, của Y% là *giảm*."""
        c = one("Doanh thu thuần đạt 2.554 tỷ đồng, giảm 16,2% so với năm trước.")
        assert c is not None
        assert c.trend is Trend.REACH
        assert c.percent_trend is Trend.DOWN

    def test_phan_tram_khong_co_tu_huong_rieng_thi_theo_ca_cau(self) -> None:
        c = one("Doanh thu thuần tăng 2,3% so với cùng kỳ.")
        assert c is not None
        assert c.percent_trend is Trend.UP

    def test_moc_so_sanh_lay_theo_moc_gan_con_so_nhat(self) -> None:
        """Câu nêu hai mốc: 325% là của *kế hoạch*, 20% mới là của *năm trước*."""
        c = one(
            "Lợi nhuận trước thuế đạt 2.809 tỷ đồng, đạt 325% kế hoạch "
            "và vượt 20% so với năm trước"
        )
        assert c is not None
        assert c.percent == 325.0
        assert c.basis == "kế hoạch"


class TestManhVunBoCuc:
    def test_loai_cau_ghep_tu_hai_manh_so(self) -> None:
        """Ô infographic bị bóc thành câu: "3,6" và "2.926 %" vốn rời nhau."""
        assert one(
            "CTCP Giống Bò Sữa Mộc Châu Tăng Doanh thu thuần đạt 3,6 2.926 % "
            "So với cùng kỳ Tỷ Đồng Năm 2021"
        ) is None

    def test_giu_cau_van_xuoi_co_nam_va_phan_tram(self) -> None:
        c = one("Năm 2024, doanh thu thuần tăng 12,6% so với cùng kỳ.")
        assert c is not None and c.percent == 12.6
