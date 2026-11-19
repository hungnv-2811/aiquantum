"""Nhãn yếu tự động: phát hiện hồi tố số liệu năm trước (restatement).

**Vì sao cần cách này.** Kế hoạch ban đầu định lấy nhãn từ chênh lệch giữa
báo cáo tài chính tự lập và báo cáo sau kiểm toán. Khi khảo sát corpus mới
thấy bộ TiniX **chỉ chứa báo cáo đã kiểm toán** — không có bản tự lập nào,
nên cách đó không thực hiện được với dữ liệu hiện có.

**Cách thay thế.** Báo cáo năm N ghi giá trị năm N ở cột "năm nay". Báo cáo
năm N+1 ghi lại chính giá trị năm N đó ở cột "năm trước". Về nguyên tắc hai
con số phải trùng khớp. Khi lệch, doanh nghiệp đã **hồi tố** số liệu — điều
chỉnh lại con số đã công bố. Hồi tố là tín hiệu cảnh báo được thừa nhận
trong nghiên cứu kế toán, và quan trọng với nhóm là **tính được hoàn toàn
tự động, không tốn giờ công gán nhãn tay nào**.

Đo trên 16 mã, 2015–2025: 31/686 cặp (năm liền kề, khoản mục) có hồi tố
vượt 0,1% — 4,5%. Tỷ lệ mất cân bằng này chính là chế độ dữ liệu mà quantum
kernel được kỳ vọng có lợi thế so với kernel cổ điển.

.. warning::
   Đây là nhãn **yếu**, không phải bằng chứng gian lận. Chênh lệch còn có
   thể đến từ thay đổi phạm vi hợp nhất, đổi chính sách kế toán, hoặc lỗi
   bóc tách của chính parser. Trước khi dùng để huấn luyện, phải rà thủ
   công một mẫu và ghi lại tỷ lệ dương tính giả trong báo cáo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from smartaudit.ingest.tinix import Report
from smartaudit.tables import Statement, extract_tables

#: Các khoản mục theo dõi hồi tố. Chọn nhóm chỉ tiêu kết quả kinh doanh vì
#: đây là nơi hành vi điều chỉnh lợi nhuận thể hiện rõ nhất.
TRACKED: dict[str, str] = {
    "10": "revenue_net",
    "20": "gross_profit",
    "50": "profit_before_tax",
    "60": "profit_after_tax",
}

#: Bỏ qua chênh lệch nhỏ hơn ngưỡng này — chủ yếu do làm tròn.
MIN_RELATIVE_DIFF = 0.001

#: Bỏ qua khoản mục có giá trị tuyệt đối quá nhỏ: chia cho số gần 0 sẽ tạo
#: ra tỷ lệ chênh lệch khổng lồ vô nghĩa.
MIN_ABSOLUTE_VALUE = 1e9


@dataclass(frozen=True)
class Restatement:
    """Một lần số liệu năm trước bị ghi lại khác đi."""

    ticker: str
    #: Năm bị hồi tố (năm N).
    year: int
    #: True nếu là báo cáo hợp nhất, False nếu riêng công ty mẹ.
    consolidated: bool | None
    concept: str
    #: Giá trị công bố trong báo cáo năm N.
    reported: float
    #: Giá trị ghi lại trong cột "năm trước" của báo cáo năm N+1.
    restated: float

    @property
    def relative_diff(self) -> float:
        return abs(self.restated - self.reported) / abs(self.reported)

    @property
    def direction(self) -> str:
        """``"tăng"`` nếu số điều chỉnh cao hơn số đã công bố."""
        return "tăng" if self.restated > self.reported else "giảm"


#: (mã CK, hợp nhất?) -> năm -> khoá khoản mục -> (năm nay, năm trước)
Series = dict[tuple[str, bool | None], dict[int, dict[str, tuple[float, float | None]]]]


def collect_series(reports: Iterable[Report]) -> Series:
    """Gom giá trị các khoản mục theo dõi từ báo cáo kết quả kinh doanh.

    Tách riêng báo cáo hợp nhất và báo cáo riêng công ty mẹ: hai loại có
    số liệu khác nhau nên đối chiếu chéo sẽ tạo ra hồi tố giả.
    """
    series: Series = {}

    for rep in reports:
        values: dict[str, tuple[float, float | None]] = {}
        for table in extract_tables(rep.read()):
            if table.statement is not Statement.INCOME:
                continue
            for code, concept in TRACKED.items():
                if concept in values:
                    continue
                row = table.by_code(code)
                if row and row.current is not None and abs(row.current) > MIN_ABSOLUTE_VALUE:
                    values[concept] = (row.current, row.previous)

        if not values:
            continue

        # Một (mã, năm, loại báo cáo) có thể ứng với nhiều file: bản ký
        # lại, bản chia làm nhiều phần, bản phát hành bổ sung. Ghi đè lặng
        # lẽ thì bản bóc được ít khoản mục nhất vẫn có thể thắng chỉ vì
        # tên file sắp sau — và cả chuỗi hồi tố của mã đó lệch theo. Giữ
        # bản bóc được nhiều khoản mục hơn, hoà thì giữ bản gặp trước.
        bucket = series.setdefault((rep.ticker, rep.consolidated), {})
        existing = bucket.get(rep.year)
        if existing is None or len(values) > len(existing):
            bucket[rep.year] = values

    return series


def detect_restatements(
    reports: Iterable[Report],
    min_diff: float = MIN_RELATIVE_DIFF,
) -> list[Restatement]:
    """Tìm mọi trường hợp số liệu năm trước bị ghi lại khác đi.

    Kết quả sắp theo mức chênh lệch giảm dần.
    """
    series = collect_series(reports)
    found: list[Restatement] = []

    for (ticker, consolidated), years in series.items():
        for year, values in years.items():
            following = years.get(year + 1)
            if not following:
                continue

            for concept, (reported, _) in values.items():
                entry = following.get(concept)
                if not entry or entry[1] is None or reported == 0:
                    continue

                restated = entry[1]
                if abs(restated - reported) / abs(reported) <= min_diff:
                    continue

                found.append(
                    Restatement(
                        ticker=ticker,
                        year=year,
                        consolidated=consolidated,
                        concept=concept,
                        reported=reported,
                        restated=restated,
                    )
                )

    found.sort(key=lambda r: r.relative_diff, reverse=True)
    return found
