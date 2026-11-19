"""Trích xuất khẳng định về số liệu từ phần ngôn từ của Báo cáo thường niên.

Đây là bước đầu của cơ chế Narrative-Number Consistency: biến câu văn xuôi
thành cấu trúc đối chiếu được với bảng số liệu. Ví dụ::

    "Kết thúc năm 2018, lợi nhuận trước thuế đạt 3.858 tỷ đồng,
     tương đương 110,7% kế hoạch năm"

    -> Claim(metric='profit_before_tax', value=3.858e12,
             trend=Trend.REACH, period=2018)

Bản này dùng luật và biểu thức chính quy, cố ý làm trước mô hình học máy.
Thể lệ cuộc thi ghi rõ *"một mô hình AI đơn giản nhưng chạy ổn định sẽ có
điểm cao hơn một mô hình phức tạp nhưng không thể triển khai"*. Bộ luật này
chạy được ngay trên dữ liệu thật và sẽ đóng vai trò đường cơ sở (baseline)
để so sánh khi PhoBERT-Fin hoàn thành ở giai đoạn sau.

**Lọc khẳng định của bên thứ ba.** Khảo sát corpus cho thấy phần lớn câu có
số trong Báo cáo thường niên là số liệu thị trường trích từ nguồn ngoài
("Theo báo cáo của MarketsandMarkets, thị trường tăng trưởng 19%"). Những
câu này **không đối chiếu được** với báo cáo tài chính của doanh nghiệp và
phải loại, nếu không sẽ tạo ra hàng loạt mâu thuẫn giả.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from smartaudit.ingest.vietstock import split_sentences
from smartaudit.tables import strip_accents


class Trend(str, Enum):
    """Hướng biến động mà câu văn khẳng định."""

    UP = "tăng"
    DOWN = "giảm"
    FLAT = "ổn định"
    REACH = "đạt"          # nêu mức tuyệt đối, không nói hướng
    CONTROLLED = "kiểm soát"   # định tính: "chi phí được kiểm soát tốt"


#: Cụm từ chỉ chỉ tiêu tài chính -> khoá trong ontology VAS.
#: Xếp cụm dài trước cụm ngắn: "doanh thu thuần" phải khớp trước "doanh thu".
_METRICS: list[tuple[str, str]] = [
    ("loi nhuan truoc thue", "profit_before_tax"),
    ("loi nhuan sau thue", "profit_after_tax"),
    ("loi nhuan rong", "profit_after_tax"),
    ("lai rong", "profit_after_tax"),
    ("loi nhuan gop", "gross_profit"),
    ("bien loi nhuan gop", "gross_profit"),
    ("doanh thu thuan", "revenue_net"),
    ("doanh thu hop nhat", "revenue_net"),
    ("tong doanh thu", "revenue_net"),
    ("doanh thu", "revenue_net"),
    ("gia von hang ban", "cost_of_goods_sold"),
    ("gia von", "cost_of_goods_sold"),
    ("chi phi ban hang", "selling_expense"),
    ("chi phi quan ly", "admin_expense"),
    ("chi phi tai chinh", "financial_expense"),
    ("chi phi lai vay", "interest_expense"),
    ("tong tai san", "total_assets"),
    ("von chu so huu", "owners_equity"),
    ("hang ton kho", "inventories"),
    ("tien va cac khoan tuong duong tien", "cash_and_equivalents"),
]

#: Từ chỉ hướng biến động. Thứ tự quyết định khi câu có nhiều từ.
_TRENDS: list[tuple[str, Trend]] = [
    ("tang truong", Trend.UP),
    ("tang", Trend.UP),
    ("giam", Trend.DOWN),
    ("sut giam", Trend.DOWN),
    ("on dinh", Trend.FLAT),
    ("duy tri", Trend.FLAT),
    ("kiem soat", Trend.CONTROLLED),
    ("cai thien", Trend.UP),
    ("hoan thanh", Trend.REACH),
    ("dat", Trend.REACH),
]

#: Hệ số quy đổi đơn vị về đồng. Có cả "ngàn tỷ" (miền Nam) và "tỉ" — thiếu
#: hai biến thể này thì câu "doanh thu thuần đạt hơn 118 ngàn tỷ đồng" (MWG
#: 2023) không đọc được con số và rơi vào "không kiểm chứng được".
_UNITS: dict[str, float] = {
    "nghin ty dong": 1e12,
    "nghin ty": 1e12,
    "ngan ty dong": 1e12,
    "ngan ty": 1e12,
    "nghin ti": 1e12,
    "ngan ti": 1e12,
    "ty dong": 1e9,
    "ty vnd": 1e9,
    "ty": 1e9,
    "ti dong": 1e9,
    "ti": 1e9,
    "trieu dong": 1e6,
    "trieu vnd": 1e6,
    "trieu": 1e6,
}

_UNIT_ALT = (
    r"nghìn tỷ đồng|nghìn tỷ|ngàn tỷ đồng|ngàn tỷ|nghìn tỉ|ngàn tỉ|"
    r"tỷ đồng|tỷ VND|tỷ|tỉ đồng|tỉ|triệu đồng|triệu VND|triệu"
)

#: Số kèm đơn vị: "3.858 tỷ đồng", "23.214 tỷ", "1,9 tỷ".
_AMOUNT = re.compile(rf"(\d[\d.]*(?:,\d+)?)\s*({_UNIT_ALT})\b", re.IGNORECASE)

#: "tăng từ 90.781 tỷ lên 96.113 tỷ": con số của **năm nay** là vế sau. Lấy
#: số đầu tiên trong câu (như :data:`_AMOUNT`) là lấy nhầm số năm trước.
_FROM_TO_AMOUNT = re.compile(
    rf"từ\s+(\d[\d.]*(?:,\d+)?)\s*(?:{_UNIT_ALT})?\s*(?:lên|xuống|thành)\s+"
    rf"(?:mức\s+)?(\d[\d.]*(?:,\d+)?)\s*({_UNIT_ALT})\b",
    re.IGNORECASE,
)

#: "biên lợi nhuận gộp tăng từ 11,8% lên 19,2%": 19,2% là **mức** năm nay.
_FROM_TO_PERCENT = re.compile(
    r"tu\s+(\d[\d.]*(?:,\d+)?)\s*%\s*(?:len|xuong|thanh)\s+(?:muc\s+)?"
    r"(\d[\d.]*(?:,\d+)?)\s*%"
)

#: Từ chỉ con số là cận dưới hoặc gần đúng: "doanh thu **trên** 6.600 tỷ",
#: "**gần** 103 nghìn tỷ". So khít với dung sai 1% thì câu đúng bị gắn cờ oan.
_AT_LEAST = re.compile(r"(?:tren|hon|vuot|vuot qua|vuot muc|vuot moc|vuot nguong)\s*$")

#: Phần trăm đứng sau những từ này là **tỷ trọng** ("chiếm 7% tổng tài sản",
#: "đóng góp 57,7% doanh thu"), không phải mức tăng trưởng — đem so với tăng
#: trưởng là so sai đại lượng.
_SHARE_BEFORE = re.compile(
    r"(?:chiem|dong gop|ty trong|bang|duy tri duoc|tuong duong|tuong ung voi)"
    r"\s*(?:khoang|gan|hon|tren|xap xi)?\s*$"
)
_APPROX = re.compile(r"(?:gan|xap xi|khoang|uoc dat|uoc tinh|xap xi muc)\s*$")

#: Tỷ lệ phần trăm: "17,4%", "110,7 %".
_PERCENT = re.compile(r"(\d[\d.]*(?:,\d+)?)\s*%")

#: Năm bốn chữ số trong khoảng hợp lý của dữ liệu.
_YEAR = re.compile(r"\b(20[0-3]\d)\b")

#: Câu trích số liệu của bên thứ ba — không đối chiếu được với BCTC.
_THIRD_PARTY = re.compile(
    r"theo (bao cao|nghien cuu|khao sat|so lieu|du bao|danh gia)|"
    r"marketsandmarkets|research and markets|gartner|idc|nielsen|mckinsey|"
    r"ngan hang the gioi|world bank|imf|adb|tong cuc thong ke|\bgso\b|"
    r"thi truong (the gioi|toan cau)|nen kinh te (the gioi|toan cau)|"
    # Chỉ tiêu vĩ mô của nền kinh tế, không phải của doanh nghiệp.
    r"tong muc ban le|gdp|cpi|lam phat|ty gia|lai suat dieu hanh"
)

#: Mảnh vụn bố cục: tiêu đề chạy trang, chú thích biểu đồ, mục lục, và
#: danh sách chức danh trong phần giới thiệu ban lãnh đạo (những dòng này
#: hay lẫn tên công ty viết hoa nên dễ bị nhận nhầm là khẳng định).
_LAYOUT_NOISE = re.compile(
    r"=====\s*PAGE|trang\s*\|\s*\d|don vi\s*:|nguon\s*:|bao cao thuong nien\s+20|"
    r"»|tv hdqt|thanh vien hdqt|hoi dong thanh vien|"
    r"muc luc|danh sach|so dien thoai|dia chi\s*:"
)

#: Hai con số dính nhau, chỉ cách nhau bằng khoảng trắng, rồi tới dấu ``%``.
#:
#: Văn xuôi không viết như vậy; đây là dấu vết của bảng biểu và hộp
#: infographic bị bóc thành một "câu" — "Doanh thu thuần đạt 3,6 2.926 %
#: So với cùng kỳ Tỷ Đồng" vốn là một ô đồ hoạ gồm "3,6 nghìn tỷ đồng" và
#: "29,26%" nằm cạnh nhau.
#:
#: Con số ghép từ hai mảnh rời không đối chiếu được với bất cứ thứ gì:
#: 2.926% đem so với tăng trưởng thật 2,2% sẽ báo "lệch 2.923,85 điểm phần
#: trăm". Đo trên corpus: 13/699 khẳng định dính mẫu này, và **cả 13** đều
#: là mảnh vụn bố cục, trong đó 3 câu đang bị gắn cờ mâu thuẫn oan.
_MERGED_NUMBERS = re.compile(r"\d[\d.,]*\s+\d[\d.,]*\s*%")

#: Ba con số trần trở lên đứng liền nhau ("2.70 2.71 2.70 2.60", "2018 2019
#: 2020"): trục biểu đồ, dòng bảng hoặc infographic bị trộn vào câu. Rà soát
#: 141 cờ "mâu thuẫn" ngày 12/11/2026 cho thấy rác bố cục kiểu này chiếm 17%.
_BARE_NUMBER_RUN = re.compile(r"(?:(?<![\w.,])\d[\d.,]*\s+){2,}\d[\d.,]*(?![\w])")

#: Câu gồm quá nhiều chữ in hoa thường là tiêu đề hoặc bảng bị dồn dòng,
#: không phải câu văn xuôi.
_UPPERCASE_LIMIT = 0.5

#: Khẳng định chỉ nói về **một phần** doanh nghiệp: công ty con, mảng kinh
#: doanh, thị trường lẻ, chi nhánh. Con số trong những câu này không đối
#: chiếu được với số hợp nhất trên báo cáo tài chính.
#:
#: Không lọc nhóm này là nguồn dương tính giả lớn nhất: câu "doanh thu
#: Driftwood đạt 116,2 triệu USD" đem so với doanh thu hợp nhất 52.562 tỷ
#: sẽ luôn báo mâu thuẫn, dù cả hai con số đều đúng.
_SCOPE_LIMITED = re.compile(
    r"cong ty con|cong ty lien ket|chi nhanh|cong ty thanh vien|"
    r"mang |khoi |phan khuc|linh vuc |nganh hang|nhom san pham|"
    # "doanh thu thuần trong nước", "doanh thu nước ngoài" — số theo bộ
    # phận địa lý. Cộng lại mới ra số hợp nhất: với VNM 2024, 50.799 tỷ
    # trong nước + 10.983 tỷ nước ngoài = 61.782 tỷ hợp nhất.
    r"trong nuoc|nuoc ngoai|xuat khau|noi dia|"
    r"khu vuc |tai my|tai campuchia|tai lao|"
    r"\busd\b|\beur\b|do la|"
    # Bổ sung sau rà soát 12/11/2026 — phạm vi hẹp hơn số hợp nhất là nguồn
    # cờ oan lớn nhất (40%). "Công ty mẹ": số BCTC riêng, không phải hợp nhất.
    r"don vi thanh vien|cong ty me|chuoi |thuong hieu|nha may|"
    r"so loi nhuan gop dat|"
    # Tên công ty con/chuỗi cụ thể gặp trong corpus.
    r"angkormilk|driftwood|vinfast|vinmec|vinschool|vinpearl|phuc long|"
    r"winmart|wincommerce|\bwcm\b|meatlife|masan consumer|masan meat|"
    r"bach hoa xanh|dien may xanh|an khang|avakids|topzone|dung quat|"
    r"crownx|masan high|vincom retail|\bvre\b|vinai|vinhms|visionai|vinbrain|"
    # Doanh thu của một nguồn/mảng cụ thể, không phải doanh thu thuần hợp nhất.
    r"doanh thu tu |doanh thu dich vu|dich vu chuyen doi so|doanh thu hoat dong|"
    r"doanh so|/m2|xay lap|du phong giam gia"
)

#: Dấu hiệu **cả trang** đang giới thiệu một đơn vị thành viên ("Trụ sở:
#: Campuchia · Vinamilk sở hữu: 100% · Lĩnh vực hoạt động chính"). Tên đơn
#: vị thường chỉ in ở nhãn bên lề nên từng câu không tự mang dấu hiệu phạm
#: vi — đây chính là ca Angkormilk ở VNM 2024 trang 59 từng bị gắn cờ oan.
_SCOPE_PAGE = re.compile(
    r"cac don vi thanh vien|linh vuc hoat dong chinh|tru so\s*:|so huu\s*:\s*\d"
)

#: Số liệu một quý, nửa năm hay vài tháng — không đối chiếu được với BCTC năm.
_SUB_PERIOD = re.compile(
    r"\bquy\s+(?:[1-4]|i{1,3}|iv)\b|\b(?:3|6|9) thang\b|nua (?:dau|cuoi) nam|luy ke"
)

#: Khẳng định tính trên **cơ sở đã điều chỉnh**, không phải số thô trên
#: báo cáo tài chính.
#:
#: Khi doanh nghiệp thoái vốn hay tái cơ cấu, số liệu hai năm không so
#: sánh trực tiếp được nên báo cáo trình bày trên cơ sở tương đương. Ví dụ
#: FPT năm 2018: doanh thu thô giảm 45,6% (42.659 tỷ xuống 23.214 tỷ) do
#: thoái vốn mảng bán lẻ và phân phối, nhưng "trong điều kiện so sánh
#: tương đương" thì tăng 17,4%. Cả hai con số đều đúng.
#:
#: Không tự tính lại được cơ sở tương đương từ báo cáo tài chính, nên hệ
#: thống bỏ qua thay vì kết luận sai.
_ADJUSTED_BASIS = re.compile(
    r"dieu kien so sanh tuong duong|co so so sanh tuong duong|"
    r"cung dieu kien|loai tru|khong bao gom|sau khi dieu chinh|"
    r"like.for.like|tuong duong nhau"
)

#: Tăng trưởng kép nhiều năm — không đối chiếu được với biến động một kỳ.
_MULTI_YEAR = re.compile(
    r"\bcagr\b|tang truong kep|binh quan hang nam|"
    r"giai doan 20\d\d\s*[-–]\s*20\d\d|trong \d+ nam qua"
)

#: Khẳng định hướng về **tương lai**: mục tiêu, kế hoạch, dự báo.
#:
#: "Doanh thu dự kiến tăng trưởng 17,5%" là chỉ tiêu đặt ra cho năm sau,
#: không phải kết quả đã đạt. Đối chiếu với báo cáo tài chính của năm hiện
#: tại là so sai đối tượng.
_FORWARD_LOOKING = re.compile(
    # "kế hoạch năm" đứng một mình KHÔNG còn bị loại: "hoàn thành 100,7% kế
    # hoạch năm" là câu kết quả. Chỉ loại khi nói về kế hoạch năm tới.
    r"du kien|du bao|muc tieu|phan dau|ke hoach nam (?:toi|sau|moi)|dat ra|"
    r"trong nam toi|nam sau|giai doan toi|tam nhin|huong toi|se dat|"
    # Giả định và rủi ro: "nếu lãi suất tăng … sẽ làm tăng chi phí lãi vay".
    r"\bneu\b.{0,80}\bse\b|can phai|tap trung vao"
)

#: Ngoại tệ và thị trường nước cụ thể — số liệu không cùng đơn vị hoặc
#: không cùng phạm vi với báo cáo tài chính hợp nhất bằng đồng Việt Nam.
_FOREIGN = re.compile(
    r"yen nhat|\bjpy\b|\bkrw\b|won han|nhan dan te|\bcny\b|"
    r"thi truong (nhat|han quoc|my|singapore|chau au|asean|trung quoc)"
)

#: Câu nói về **chính sách hay chủ trương**, không phải về con số.
#:
#: Ví dụ: "công ty duy trì chính sách quản lý hàng tồn kho". Từ "duy trì" ở
#: đây gắn với *chính sách*, không phải với *giá trị tồn kho* — đối chiếu
#: với số liệu tồn kho sẽ ra kết luận ngược.
#:
#: Đây là ranh giới của cách tiếp cận bằng luật: phân biệt được "duy trì
#: chính sách" với "tồn kho duy trì ổn định" đòi hỏi phân tích quan hệ phụ
#: thuộc trong câu, tức cần mô hình ngôn ngữ. Trước mắt hệ thống chọn bỏ
#: qua nhóm câu này thay vì kết luận sai.
_POLICY_STATEMENT = re.compile(
    r"chinh sach|chien luoc|dinh huong|chu truong|co che|nguyen tac|"
    r"quy trinh|cam ket|"
    # Câu mô tả chính sách kế toán: "dự phòng giảm giá hàng tồn kho được
    # trích lập khi…" — không phải khẳng định về kết quả.
    r"duoc hach toan|duoc xac dinh theo|duoc trich lap|theo huong dan|"
    r"duoc ghi nhan (?:theo|khi)|duoc phan bo|uoc tinh ke toan"
)

#: Nhắc tới một pháp nhân khác bằng tên viết tắt: "lợi nhuận của MCM",
#: "doanh thu của GTN". Đây là công ty con hoặc công ty liên kết, số liệu
#: của họ nằm ở thuyết minh theo bộ phận chứ không phải dòng hợp nhất.
_SUBSIDIARY_REF = re.compile(r"\bcủa [A-Z]{2,5}\b")

#: Khẳng định về **tỷ số** chứ không phải giá trị tuyệt đối. Phải tách
#: riêng: "vòng quay hàng tồn kho giảm" nói về số vòng quay, không phải
#: giá trị tồn kho — đối chiếu nhầm sẽ ra kết luận ngược.
_RATIO_HINT = re.compile(
    r"vong quay|ty le|ty trong|ty suat|he so|chi so|bien (loi nhuan|lai)|"
    r"loi nhuan tren|tren doanh thu|/doanh thu|co cau"
)

#: Tỷ số suy ra được từ báo cáo tài chính, ánh xạ sang khoá riêng để bộ
#: đối chiếu tính bằng công thức thay vì tra thẳng một ô trong bảng.
_RATIO_METRICS: list[tuple[str, str]] = [
    ("bien loi nhuan gop", "gross_margin"),
    ("bien lai gop", "gross_margin"),
    ("bien loi nhuan rong", "net_margin"),
    ("bien loi nhuan sau thue", "net_margin"),
    ("vong quay hang ton kho", "inventory_turnover"),
]

#: Mốc so sánh mà câu văn viện dẫn.
_BASIS: list[tuple[str, str]] = [
    ("so voi cung ky", "cùng kỳ"),
    ("cung ky nam", "cùng kỳ"),
    ("so voi nam truoc", "năm trước"),
    ("so voi nam", "năm trước"),
    ("ke hoach", "kế hoạch"),
    ("yoy", "cùng kỳ"),
]


@dataclass(frozen=True)
class Claim:
    """Một khẳng định về số liệu, đã cấu trúc hoá."""

    #: Câu gốc, giữ nguyên để truy vết minh chứng.
    text: str
    #: Trang trong báo cáo thường niên.
    page: int
    #: Khoá ontology của chỉ tiêu được nhắc tới.
    metric: str
    trend: Trend
    #: Giá trị tuyệt đối đã quy về đồng, nếu câu có nêu.
    value: float | None = None
    #: Tỷ lệ phần trăm nêu trong câu (mức tăng/giảm hoặc mức hoàn thành).
    percent: float | None = None
    #: Hướng biến động **đi kèm con số phần trăm**, có thể khác
    #: :attr:`trend` của cả câu. Xem :func:`_trend_before`.
    percent_trend: Trend | None = None
    #: Năm mà khẳng định nói tới.
    period: int | None = None
    #: Mốc so sánh: "cùng kỳ", "năm trước", "kế hoạch".
    basis: str | None = None
    #: True khi câu nói về tỷ số (biên lợi nhuận, vòng quay) thay vì giá trị.
    is_ratio: bool = False
    #: ``"min"`` khi câu nói "trên/hơn X", ``"approx"`` khi "gần/khoảng X".
    approx: str | None = None
    #: Sai số tương đối do **làm tròn** con số trong câu: "1,9 tỷ" có thể là
    #: bất cứ giá trị nào từ 1,85 tới 1,95 tỷ, tức ±2,6%.
    value_tol: float = 0.0
    #: True khi phần trăm là **mức** của tỷ số ("tăng từ 11,8% lên 19,2%"),
    #: không phải mức thay đổi.
    percent_is_level: bool = False

    @property
    def quantitative(self) -> bool:
        """Có nêu con số cụ thể hay chỉ là nhận định định tính."""
        return self.value is not None or self.percent is not None


def _parse_vn_number(text: str) -> float | None:
    """Đọc số kiểu Việt Nam: chấm ngăn nghìn, phẩy thập phân."""
    try:
        return float(text.replace(".", "").replace(",", "."))
    except ValueError:
        return None


#: Những từ khác nhau nhưng **trùng nhau sau khi bỏ dấu**, gây nhận nhầm.
#:
#: Bỏ dấu là cách chống lỗi OCR hiệu quả, nhưng nó xoá luôn khác biệt giữa
#: các từ hoàn toàn khác nghĩa. Ví dụ *giảm* và *giám* đều thành ``giam``,
#: nên câu "Tổng **Giám** đốc cho biết doanh thu tăng" bị gán xu hướng
#: **giảm** — mà "giám đốc" thì có mặt ở gần như mọi báo cáo thường niên.
#:
#: Ranh giới từ không cứu được, vì sau khi bỏ dấu "giám đốc" là hai từ
#: tách rời. Cách duy nhất là loại theo từ đi liền sau.
_HOMOGRAPH_SUFFIXES: dict[str, tuple[str, ...]] = {
    # giảm ≠ giám (đốc, sát, khảo, định, thị)
    "giam": ("doc", "sat", "khao", "dinh", "thi"),
    # đạt ≠ đất (đai, nước)
    "dat": ("dai", "nuoc"),
    # tăng ≠ tầng (lớp, trệt) ≠ tặng (quà)
    "tang": ("lop", "tret", "qua", "ham"),
}

#: Bộ nhớ đệm biểu thức tìm cụm từ.
_PHRASE_CACHE: dict[str, re.Pattern[str]] = {}


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Biểu thức tìm một cụm từ, có ràng buộc ranh giới từ.

    Không dùng ``str.find`` được vì nó khớp cả chuỗi con nằm giữa từ khác.
    Ngoài ra còn phải loại các từ trùng nhau sau khi bỏ dấu — xem
    :data:`_HOMOGRAPH_SUFFIXES`.
    """
    pattern = _PHRASE_CACHE.get(phrase)
    if pattern is None:
        exclude = _HOMOGRAPH_SUFFIXES.get(phrase)
        tail = rf"(?!\s+(?:{'|'.join(exclude)})\b)" if exclude else ""
        pattern = re.compile(
            rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9]){tail}"
        )
        _PHRASE_CACHE[phrase] = pattern
    return pattern


def _find_phrase(plain: str, phrase: str) -> int:
    """Vị trí xuất hiện đầu tiên của cụm từ, hoặc ``-1`` nếu không thấy."""
    match = _phrase_pattern(phrase).search(plain)
    return match.start() if match else -1


def _find_metric(plain: str) -> tuple[str, bool] | None:
    """Tìm chỉ tiêu được nhắc sớm nhất trong câu.

    Trả về ``(khoá, có phải tỷ số)``. Tỷ số được xét trước giá trị tuyệt
    đối: "biên lợi nhuận gộp" phải ra ``gross_margin`` chứ không phải
    ``gross_profit``.

    Khi nhiều cụm cùng khớp tại một vị trí, ưu tiên cụm dài hơn — nhờ vậy
    "doanh thu thuần" không bị đọc nhầm thành "doanh thu".
    """
    for phrase, key in _RATIO_METRICS:
        if _find_phrase(plain, phrase) >= 0:
            return key, True

    best: tuple[int, int, str] | None = None
    for phrase, key in _METRICS:
        pos = _find_phrase(plain, phrase)
        if pos < 0:
            continue
        candidate = (pos, -len(phrase), key)
        if best is None or candidate < best:
            best = candidate
    if best is None:
        return None
    return best[2], bool(_RATIO_HINT.search(plain))


def _find_trend(plain: str) -> Trend | None:
    """Tìm từ chỉ xu hướng xuất hiện sớm nhất trong câu.

    Khi hai cụm bắt đầu cùng vị trí, cụm dài thắng — nhờ vậy "sụt giảm"
    không bị rút gọn thành "giảm" và "tăng trưởng" không thành "tăng".
    """
    best: tuple[int, int, Trend] | None = None
    for phrase, trend in _TRENDS:
        pos = _find_phrase(plain, phrase)
        if pos < 0:
            continue
        candidate = (pos, -len(phrase), trend)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    return best[2] if best else None


def _trend_before(plain: str, pos: int) -> Trend | None:
    """Từ chỉ xu hướng **gần nhất đứng trước** một vị trí trong câu.

    Xu hướng của cả câu lấy theo từ xuất hiện sớm nhất, nhưng con số phần
    trăm lại do từ đứng ngay trước nó chi phối. Hai thứ này thường khác
    nhau::

        "Doanh thu đạt 2.554 tỷ đồng, giảm 16,2% so với năm trước"

    Xu hướng của câu là *đạt* (nêu mức tuyệt đối), còn 16,2% là mức
    **giảm**. Lấy nhầm dấu ở đây biến một câu hoàn toàn đúng thành mâu
    thuẫn — mà lối diễn đạt này có ở gần như mọi báo cáo thường niên.

    Khi hai cụm cùng kết thúc tại một vị trí, cụm dài thắng: "sụt giảm"
    không bị rút gọn thành "giảm".
    """
    best: tuple[int, int, Trend] | None = None
    for phrase, trend in _TRENDS:
        for match in _phrase_pattern(phrase).finditer(plain):
            if match.start() >= pos:
                break
            candidate = (match.start(), len(phrase), trend)
            if best is None or candidate[:2] > best[:2]:
                best = candidate
    return best[2] if best else None


def _metric_pos(plain: str, key: str) -> int:
    """Vị trí sớm nhất mà chỉ tiêu ``key`` được nhắc trong câu."""
    positions = [
        _find_phrase(plain, phrase)
        for phrase, k in (*_RATIO_METRICS, *_METRICS)
        if k == key
    ]
    positions = [p for p in positions if p >= 0]
    return min(positions) if positions else -1


#: Từ chỉ hướng phải nằm trong khoảng này sau chỉ tiêu mới coi là của nó.
_TREND_WINDOW = 80


def _trend_for_metric(plain: str, metric_pos: int) -> Trend | None:
    """Từ chỉ hướng **gắn với chỉ tiêu**, không phải từ sớm nhất cả câu.

    "Duy trì lợi thế cạnh tranh, doanh thu đạt 62.849 tỷ" — từ sớm nhất là
    *duy trì* (đi ngang), nhưng nó nói về lợi thế cạnh tranh. Tiếng Việt
    thường đặt từ chỉ hướng **ngay sau** chỉ tiêu ("doanh thu tăng 10%"),
    nên ưu tiên từ đầu tiên đứng sau chỉ tiêu trong một khoảng ngắn; không
    có thì quay về cách cũ.
    """
    if metric_pos >= 0:
        best: tuple[int, int, Trend] | None = None
        for phrase, trend in _TRENDS:
            for match in _phrase_pattern(phrase).finditer(plain):
                start = match.start()
                if start < metric_pos:
                    continue
                if start - metric_pos > _TREND_WINDOW:
                    break
                candidate = (start, -len(phrase), trend)
                if best is None or candidate[:2] < best[:2]:
                    best = candidate
                break
        if best is not None:
            return best[2]
        # Không có từ chỉ hướng phía sau: chỉ nhận từ đứng **sát trước** chỉ
        # tiêu ("tăng trưởng doanh thu"). Lấy từ sớm nhất cả câu như trước
        # đây thì "Tổng nợ phải trả tiếp tục giảm, trong khi vốn chủ sở hữu
        # được củng cố" bị hiểu là vốn chủ sở hữu giảm.
        near: tuple[int, Trend] | None = None
        for phrase, trend in _TRENDS:
            for match in _phrase_pattern(phrase).finditer(plain):
                if match.end() <= metric_pos and metric_pos - match.end() <= _TREND_BEFORE_GAP:
                    if near is None or match.end() > near[0]:
                        near = (match.end(), trend)
        return near[1] if near else None
    return _find_trend(plain)


#: Từ chỉ hướng đứng trước chỉ tiêu phải cách chỉ tiêu không quá ngần này ký tự.
_TREND_BEFORE_GAP = 15


def _rounding_tol(number_text: str, value: float) -> float:
    """Sai số tương đối do làm tròn của con số in trong câu."""
    _, _, decimals = number_text.partition(",")
    step = 10 ** -len(decimals) if decimals else 1.0
    number = _parse_vn_number(number_text) or 0.0
    return (step / 2) / number if number else 0.0


def _find_basis(plain: str) -> str | None:
    for phrase, label in _BASIS:
        if _find_phrase(plain, phrase) >= 0:
            return label
    return None


def _basis_near(plain: str, pos: int) -> str | None:
    """Mốc so sánh **gắn với** con số ở vị trí ``pos``.

    Một câu có thể viện dẫn hai mốc cùng lúc::

        "Lợi nhuận trước thuế đạt 2.809 tỷ đồng, đạt 325% kế hoạch và
         vượt 20% so với năm trước"

        325% là so với *kế hoạch*, 20% mới là so với *năm trước*.

    Lấy mốc theo thứ tự liệt kê trong :data:`_BASIS` sẽ gán "năm trước" cho
    325%, rồi đem tỷ lệ hoàn thành kế hoạch đi so với tăng trưởng thực tế —
    ra "lệch 304,91 điểm phần trăm" cho một câu không hề sai.
    """
    best: tuple[int, str] | None = None
    for phrase, label in _BASIS:
        for match in _phrase_pattern(phrase).finditer(plain):
            candidate = (abs(match.start() - pos), label)
            if best is None or candidate[0] < best[0]:
                best = candidate
    return best[1] if best else None


def extract_claims(text: str, default_year: int | None = None) -> list[Claim]:
    """Trích các khẳng định về số liệu từ văn bản báo cáo thường niên.

    :param default_year: năm của báo cáo, dùng khi câu không tự nêu năm.

    Câu được giữ lại khi nêu được **một chỉ tiêu tài chính** và **một hướng
    biến động**, đồng thời không phải trích dẫn bên thứ ba hay mảnh vụn bố
    cục. Giữ cả khẳng định định tính (không có số) vì đó chính là loại mâu
    thuẫn ngầm mà cơ chế NNC nhắm tới — "chi phí được kiểm soát tốt" trong
    khi chi phí thực tế tăng.
    """
    claims: list[Claim] = []
    page = 0

    for block in text.split("===== PAGE "):
        header, _, body = block.partition(" =====")
        if header.strip().isdigit():
            page = int(header.strip())
        else:
            body = block

        # Trang giới thiệu đơn vị thành viên: mọi câu trên trang nói về đơn
        # vị đó, không phải số hợp nhất.
        if _SCOPE_PAGE.search(strip_accents(body).lower()):
            continue

        for sentence in split_sentences(body):
            if not (25 <= len(sentence) <= 400):
                continue

            letters = [c for c in sentence if c.isalpha()]
            if letters and sum(c.isupper() for c in letters) / len(letters) > _UPPERCASE_LIMIT:
                continue
            if _SUBSIDIARY_REF.search(sentence):
                continue

            plain = strip_accents(sentence).lower()
            if (
                _THIRD_PARTY.search(plain)
                or _LAYOUT_NOISE.search(plain)
                or _SCOPE_LIMITED.search(plain)
                or _POLICY_STATEMENT.search(plain)
                or _FORWARD_LOOKING.search(plain)
                or _FOREIGN.search(plain)
                or _ADJUSTED_BASIS.search(plain)
                or _MULTI_YEAR.search(plain)
                or _MERGED_NUMBERS.search(plain)
                or _BARE_NUMBER_RUN.search(plain)
                or _SUB_PERIOD.search(plain)
            ):
                continue

            years = [int(y) for y in _YEAR.findall(sentence)]
            period = max(years) if years else default_year
            # BCTC năm nay chỉ kiểm được năm nay so với năm trước. Bỏ câu viện
            # dẫn năm xa hơn ("so với năm 2013"), năm tương lai, hoặc chỉ kể
            # kết quả năm trước ("Năm 2021, doanh thu đạt…" trong BCTN 2022).
            # Riêng "So với năm 2023, doanh thu tăng 10%" là nói về năm nay.
            if default_year and years:
                if min(years) < default_year - 1 or max(years) > default_year:
                    continue
                if max(years) == default_year - 1:
                    if "so voi" not in plain:
                        continue
                    period = default_year

            found = _find_metric(plain)
            if found is None:
                continue
            metric, is_ratio = found
            trend = _trend_for_metric(plain, _metric_pos(plain, metric))
            if trend is None:
                continue

            value = None
            value_tol = 0.0
            approx = None
            amount = _FROM_TO_AMOUNT.search(sentence)
            number_text = unit_text = None
            # Dạng "từ X … lên Y" bị chữ cột bên cạnh chen vào giữa (bóc PDF
            # nhiều cột): vẫn lấy con số đứng sau "lên/xuống".
            loose = re.search(rf"\btừ\s+\d.*?\b(?:lên|xuống)\b.*?(\d[\d.]*(?:,\d+)?)\s*({_UNIT_ALT})\b",
                              sentence, re.IGNORECASE)
            if amount:
                number_text, unit_text = amount.group(2), amount.group(3)
                amount_start = amount.start(2)
            elif loose:
                number_text, unit_text = loose.group(1), loose.group(2)
                amount_start = loose.start(1)
            elif amount := _AMOUNT.search(sentence):
                number_text, unit_text = amount.group(1), amount.group(2)
                amount_start = amount.start(1)
            if number_text:
                number = _parse_vn_number(number_text)
                factor = _UNITS.get(strip_accents(unit_text).lower())
                if number is not None and factor:
                    value = number * factor
                    value_tol = _rounding_tol(number_text, number)
                    lead = strip_accents(sentence[max(0, amount_start - 25):amount_start]).lower()
                    if _AT_LEAST.search(lead):
                        approx = "min"
                    elif _APPROX.search(lead):
                        approx = "approx"

            # Khớp trên bản đã bỏ dấu để vị trí tìm được dùng chung được
            # với _trend_before; chữ số và dấu ``%`` không đổi khi bỏ dấu.
            percent = percent_trend = None
            percent_is_level = False
            basis = _find_basis(plain)
            if (match := _FROM_TO_PERCENT.search(plain)) and is_ratio:
                percent = _parse_vn_number(match.group(2))
                percent_trend = Trend.REACH
                percent_is_level = True
            elif (match := _PERCENT.search(plain)) and not _SHARE_BEFORE.search(
                plain[max(0, match.start() - 30):match.start()]
            ):
                percent = _parse_vn_number(match.group(1))
                percent_trend = _trend_before(plain, match.start()) or trend
                basis = _basis_near(plain, match.end()) or basis

            # Câu chỉ nêu mức hoàn thành kế hoạch, không có con số kết quả:
            # BCTC không chứa kế hoạch nội bộ để đối chiếu. Câu có kèm số kết
            # quả ("đạt 3.858 tỷ, hoàn thành 110,7% kế hoạch năm") thì giữ.
            if value is None and basis == "kế hoạch":
                continue

            claims.append(
                Claim(
                    text=re.sub(r"\s+", " ", sentence).strip(),
                    page=page,
                    metric=metric,
                    trend=trend,
                    value=value,
                    percent=percent,
                    percent_trend=percent_trend,
                    period=period,
                    basis=basis,
                    is_ratio=is_ratio,
                    approx=approx,
                    value_tol=value_tol,
                    percent_is_level=percent_is_level,
                )
            )

    return claims
