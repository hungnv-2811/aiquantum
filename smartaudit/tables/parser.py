"""Bóc tách bảng số liệu tài chính từ văn bản OCR của bộ TiniX.

Bộ TiniX đã giữ nguyên bảng biểu dưới dạng HTML ``<table>``, và quan trọng
hơn là **giữ luôn cột Mã số theo Thông tư 200/2014/TT-BTC**. Nhờ vậy ta ánh
xạ khoản mục theo mã số thay vì phải khớp gần tên tiếng Việt — chính xác
hơn hẳn và không phụ thuộc cách diễn đạt thay đổi qua các năm.

Ví dụ một hàng trong Báo cáo kết quả hoạt động kinh doanh::

    <tr><td>Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)</td>
        <td>10</td><td>VI.1</td>
        <td>61.782.609.528.445</td><td>60.368.915.511.505</td></tr>

Khảo sát trên 60 báo cáo cho thấy vị trí cột Mã số **không cố định** (xuất
hiện ở cột 0, 1 hoặc 2 tùy báo cáo) và tiêu đề có nhiều biến thể: ``TÀI
SẢN``, ``NGUỒN VỐN``, ``CHỈ TIÊU``, ``Năm nay/Năm trước``, ``Số cuối năm/Số
đầu năm``... Vì vậy parser nhận diện vai trò từng cột **theo nội dung của
chính các hàng dữ liệu**, không dựa vào vị trí hay tên tiêu đề.
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum

_TABLE = re.compile(r"<table>(.*?)</table>", re.DOTALL | re.IGNORECASE)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL | re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")

#: Mã số theo Thông tư 200 gồm 1–3 chữ số, đôi khi có hậu tố chữ (``V.01``
#: trong thuyết minh thì không phải mã số, nên chỉ nhận chuỗi thuần số).
_MA_SO = re.compile(r"^\d{1,3}$")

#: Số tiền kiểu Việt Nam: dấu chấm ngăn nghìn, có thể âm bằng ngoặc đơn
#: hoặc dấu trừ. Ví dụ ``61.782.609.528.445``, ``(1.234.567)``, ``-8.200``.
_NUMBER = re.compile(r"^\(?-?\s*\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?\s*\)?$")

#: Trang được đánh dấu bằng marker do TiniX chèn khi OCR.
_PAGE = re.compile(r"=====\s*PAGE\s+(\d+)\s*=====", re.IGNORECASE)


class Statement(str, Enum):
    """Loại báo cáo mà một bảng thuộc về.

    Phân biệt loại báo cáo là **bắt buộc** chứ không phải tiện ích: mã số
    chỉ duy nhất trong phạm vi từng báo cáo, không duy nhất toàn tài liệu.
    Ví dụ mã ``10`` là *Doanh thu thuần* trong Báo cáo kết quả kinh doanh,
    nhưng lại là *Biến động hàng tồn kho* trong Lưu chuyển tiền tệ. Nếu bỏ
    qua ngữ cảnh, cơ chế NNC sẽ đối chiếu nhầm số liệu.
    """

    INCOME = "income_statement"        # Báo cáo kết quả hoạt động kinh doanh
    BALANCE = "balance_sheet"          # Bảng cân đối kế toán / Tình hình tài chính
    CASH_FLOW = "cash_flow"            # Báo cáo lưu chuyển tiền tệ
    NOTES = "notes"                    # Thuyết minh báo cáo tài chính
    UNKNOWN = "unknown"


def strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp chịu được lỗi OCR.

    OCR thường đánh rơi hoặc đặt sai dấu — ``LƯU CHUYỂN TIỀN TỆ`` có thể ra
    ``LƯU CHUYÊN TIÊN TỆ``. So khớp trên bản không dấu giúp bỏ qua nhóm lỗi
    này mà không cần liệt kê từng biến thể.

    >>> strip_accents("LƯU CHUYỂN TIỀN TỆ")
    'LUU CHUYEN TIEN TE'
    """
    text = text.replace("Đ", "D").replace("đ", "d")
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


#: Dấu hiệu nhận biết loại báo cáo, khớp trên văn bản đã bỏ dấu và viết hoa.
#:
#: Mẫu **neo vào đầu dòng**. Đây là điểm mấu chốt: nếu chỉ tìm từ khoá ở bất
#: kỳ đâu trong dòng thì câu chân trang lặp trên mọi trang — "Các thuyết minh
#: đính kèm là bộ phận hợp thành của báo cáo tài chính này" — sẽ bị chấm là
#: tiêu đề phần Thuyết minh và làm sai toàn bộ việc phân loại phía sau.
#:
#: Thứ tự quan trọng: xét "THUYET MINH" trước, vì tiêu đề thuyết minh có
#: chứa luôn tên các báo cáo khác ("Thuyết minh báo cáo tài chính hợp nhất").
_HEADINGS: list[tuple[re.Pattern[str], Statement]] = [
    (re.compile(r"^THUYET MINH"), Statement.NOTES),
    (re.compile(r"^(BAO CAO )?LUU CHUYEN TIEN TE"), Statement.CASH_FLOW),
    (re.compile(r"^(BAO CAO )?KET QUA HOAT DONG"), Statement.INCOME),
    (re.compile(r"^(BANG )?CAN DOI KE TOAN|^BAO CAO TINH HINH TAI CHINH"),
     Statement.BALANCE),
]

#: Dòng mục lục kết thúc bằng số trang hoặc khoảng trang: "... RIÊNG 6-8",
#: "... HỢP NHẤT 13 – 54". Phải loại, vì mục lục nằm ở đầu tài liệu và sẽ
#: khiến mọi bảng phía sau bị gán nhầm theo mục cuối cùng của mục lục.
#:
#: Giới hạn 1–3 chữ số là có chủ ý: số trang không quá 999, trong khi tiêu
#: đề thật thường kết thúc bằng năm bốn chữ số ("...ngày 31 tháng 12 năm
#: 2016"). Nếu bắt cả số bốn chữ số thì các tiêu đề chạy trang hợp lệ của
#: HPG, PLX, VNM... đều bị loại nhầm — đúng lỗi đã gặp khi thử lần đầu.
_TOC_TAIL = re.compile(r"(?<!\d)\d{1,3}\s*(?:[-–—]\s*\d{1,3})?\s*$")

#: Bỏ số thứ tự đầu dòng ("3. Báo cáo kết quả...") trước khi khớp.
_LEAD_NUM = re.compile(r"^[\dIVX]+[.)]\s*")

#: Dấu nháy OCR chèn vào giữa một từ: ``LƯU`` bị đọc thành ``LU'U``. Chỉ
#: xoá khi nó nằm giữa hai chữ cái, để không đụng tới dấu câu thật ở đầu
#: hay cuối dòng.
_OCR_APOSTROPHE = re.compile(r"(?<=[A-Z])['’`´]+(?=[A-Z])")

#: Mã biểu mẫu do Thông tư 200 quy định, in ở góc mỗi báo cáo: ``Mẫu số
#: B 01 - DN``, ``B03-DN``, ``FORM B 01-DN``.
#:
#: Đây là dấu hiệu **đáng tin hơn tiêu đề bằng chữ**: nó ngắn, gần như
#: không bị OCR làm hỏng, và không phụ thuộc ngôn ngữ nên nhận được cả
#: những báo cáo trình bày bằng tiếng Anh. Quan trọng hơn, nó còn đúng
#: khi chính doanh nghiệp ghi nhầm tiêu đề — báo cáo lưu chuyển tiền tệ
#: của MSN 2015 mang tiêu đề "Báo cáo kết quả hoạt động kinh doanh", chỉ
#: mã ``B 03`` cho biết đó thật ra là báo cáo nào.
_FORM_CODE = re.compile(r"\bB\s*0?([1239])\s*[-–—/ ]\s*DN\b")

_FORM_STATEMENTS: dict[str, Statement] = {
    "1": Statement.BALANCE,
    "2": Statement.INCOME,
    "3": Statement.CASH_FLOW,
    "9": Statement.NOTES,
}


def _statement_marks(text: str) -> list[tuple[int, Statement]]:
    """Tìm vị trí các tiêu đề báo cáo trong tài liệu.

    Không đòi hỏi tiêu đề phải viết hoa: khảo sát trên corpus cho thấy nhiều
    doanh nghiệp (HPG, PLX, MSN...) dùng tiêu đề chữ thường kiểu "Bảng cân
    đối kế toán riêng tại ngày 31 tháng 12 năm 2016". Các tiêu đề này lặp
    lại ở đầu mỗi trang nên còn đáng tin hơn tiêu đề in hoa xuất hiện một lần.

    Dòng nào không khớp tiêu đề bằng chữ thì thử tới mã biểu mẫu — xem
    :data:`_FORM_CODE`.
    """
    marks: list[tuple[int, Statement]] = []
    for match in re.finditer(r"^[^\n]{10,160}$", text, re.MULTILINE):
        line = match.group(0).strip()
        if _TOC_TAIL.search(line):
            continue
        plain = _LEAD_NUM.sub("", strip_accents(line).upper()).strip()
        plain = _OCR_APOSTROPHE.sub("", plain)

        statement = next(
            (s for pattern, s in _HEADINGS if pattern.search(plain)), None
        )
        if statement is None and (form := _FORM_CODE.search(plain)):
            statement = _FORM_STATEMENTS[form.group(1)]
        if statement is not None:
            marks.append((match.start(), statement))
    return marks


def parse_number(text: str) -> float | None:
    """Đổi chuỗi số kiểu Việt Nam thành ``float``.

    Trả về ``None`` nếu chuỗi không phải một con số.

    >>> parse_number("61.782.609.528.445")
    61782609528445.0
    >>> parse_number("(1.234)")
    -1234.0
    >>> parse_number("12,5")
    12.5
    >>> parse_number("Thuyết minh") is None
    True
    """
    s = text.strip()
    if not s or not _NUMBER.match(s):
        return None

    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").strip()
    if s.startswith("-"):
        negative = True
        s = s[1:].strip()

    # Dấu chấm và khoảng trắng ngăn nghìn -> bỏ; dấu phẩy thập phân -> chấm.
    s = s.replace(".", "").replace(" ", "").replace(",", ".")
    try:
        value = float(s)
    except ValueError:
        return None
    return -value if negative else value


@dataclass(frozen=True)
class TableRow:
    """Một dòng khoản mục trong báo cáo tài chính."""

    #: Mã số theo Thông tư 200, ví dụ ``"10"`` = doanh thu thuần.
    code: str
    #: Tên khoản mục như in trong báo cáo.
    label: str
    #: Các giá trị theo cột, thường là [kỳ này, kỳ trước].
    values: list[float]

    @property
    def current(self) -> float | None:
        return self.values[0] if self.values else None

    @property
    def previous(self) -> float | None:
        return self.values[1] if len(self.values) > 1 else None


@dataclass
class FinancialTable:
    """Một bảng số liệu đã bóc tách được."""

    #: Số trang trong báo cáo gốc (dùng cho truy vết minh chứng).
    page: int
    #: Báo cáo mà bảng này thuộc về. Quyết định cách diễn giải mã số.
    statement: Statement = Statement.UNKNOWN
    rows: list[TableRow] = field(default_factory=list)

    def by_code(self, code: str) -> TableRow | None:
        for row in self.rows:
            if row.code == code:
                return row
        return None

    def __len__(self) -> int:
        return len(self.rows)


def _clean(cell: str) -> str:
    # Giải mã mọi thực thể HTML (``&quot;``, ``&#x27;``…), không chỉ ``&amp;``:
    # tên khoản mục còn sót thực thể thì khớp tên theo ontology bị lệch.
    return html.unescape(_TAG.sub("", cell)).strip()


# ── Đơn vị tính của bảng ──────────────────────────────────────────────────
#
# Khoảng 1/4 BCTC ngoài ngân hàng trong corpus ghi số theo **nghìn đồng**
# hoặc **triệu đồng** (HAG: "Ngàn VND"; VHM, VIC: "Đơn vị tính: triệu VND";
# MSN: tiêu đề cột "31/12/2024Triệu VND"). Không quy đổi thì doanh thu
# Masan 83.177.720 triệu bị đọc thành 83 triệu đồng, và mọi phép so giá trị
# tuyệt đối với câu văn ("doanh thu đạt 83.178 tỷ đồng") đều sai lệch cỡ
# nghìn lần. Tăng trưởng không bị ảnh hưởng vì cùng hệ số ở hai kỳ.

_SCALE_WORDS = {"triệu": 1e6, "trieu": 1e6, "nghìn": 1e3, "nghin": 1e3, "ngàn": 1e3, "ngan": 1e3}

#: Dòng đơn vị đứng riêng phía trên bảng: "Ngàn VND", "Đơn vị tính: triệu VND",
#: "ĐVT: đồng". Phải là một dòng riêng (văn bản OCR nối dòng bằng hai dấu
#: cách) để không bắt nhầm câu thuyết minh kiểu "đầu tư 51.547 triệu VND".
_UNIT_LINE = re.compile(
    r"(?:^|\s{2}|\n)\s*(?:(?:đơn vị(?: tính)?|đvt)\s*:?\s*)?"
    r"(triệu|trieu|nghìn|nghin|ngàn|ngan)?\s*(?:vn[dđ]|đồng)\s*(?=$|\s{2}|\n|<)",
    re.IGNORECASE,
)

#: Đơn vị nằm trong ô tiêu đề cột: "31/12/2024Triệu VND", "Năm nay (nghìn đồng)",
#: "VND'000".
_UNIT_HEADER = re.compile(
    r"(triệu|trieu|nghìn|nghin|ngàn|ngan)\s*(?:vn[dđ]|đồng)|vn[dđ]\s*'\s*(000)",
    re.IGNORECASE,
)


def _unit_scale(before: str, table_html: str) -> float | None:
    """Hệ số quy đổi về đồng của một bảng, hoặc ``None`` nếu không thấy dấu hiệu.

    Xét hai nơi: đoạn văn ngay phía trên bảng, và hai hàng đầu của bảng (ô
    tiêu đề cột). Thấy "VND"/"đồng" đứng một mình thì hệ số là 1.
    """
    head = " ".join(_TAG.sub(" ", r) for r in _ROW.findall(table_html)[:2])
    if m := _UNIT_HEADER.search(head):
        return 1e3 if m.group(2) else _SCALE_WORDS[m.group(1).lower()]
    found = None
    for m in _UNIT_LINE.finditer(before):
        found = m  # lấy dòng đơn vị gần bảng nhất
    if found is None:
        return None
    word = found.group(1)
    return _SCALE_WORDS[word.lower()] if word else 1.0


#: Giá trị đứng đầu bị coi là số hiệu thuyết minh nếu nó nhỏ hơn giá trị
#: lớn nhất phía sau ít nhất ngần này lần.
_NOTE_REF_RATIO = 1000


def _drop_note_references(values: list[float]) -> list[float]:
    """Bỏ cột "Thuyết minh" bị đọc nhầm thành giá trị.

    Bố cục thường gặp là ``[tên khoản mục | mã số | thuyết minh | năm nay |
    năm trước]``. Nhiều doanh nghiệp ghi số thuyết minh dạng ``VI.1`` nên
    không đọc ra số, nhưng nhiều doanh nghiệp khác ghi số trần (``26``) —
    khi đó nó bị nhận nhầm là giá trị năm nay và đẩy con số thật sang cột
    năm trước.

    Đây là lỗi từng làm doanh thu thuần của FPT 2023 thành ``26`` thay vì
    52.618 tỷ, kéo điểm nhất quán xuống 0,33 một cách oan uổng.

    Dấu hiệu nhận biết: trong cùng một hàng, số liệu các kỳ luôn cùng cỡ,
    còn số hiệu thuyết minh thì nhỏ hơn hàng nghìn lần.

    Số hiệu thuyết minh luôn là số nguyên dương. Một số ``0`` — hay một số
    âm — đứng đầu là **giá trị thật của kỳ này**: khoản mục không phát sinh
    trong năm. Bỏ nó đi sẽ đôn số năm trước sang cột năm nay và tạo ra một
    khẳng định sai hoàn toàn về kỳ hiện tại.

    >>> _drop_note_references([26.0, 52618e9, 44010e9]) == [52618e9, 44010e9]
    True
    >>> _drop_note_references([1000.0, 900.0])
    [1000.0, 900.0]
    >>> _drop_note_references([0.0, 52618e9]) == [0.0, 52618e9]
    True
    """
    while len(values) >= 2 and values[0] > 0:
        largest = max(abs(v) for v in values[1:])
        if values[0] * _NOTE_REF_RATIO >= largest:
            break
        values = values[1:]
    return values


def _parse_rows(
    html: str, page: int, statement: Statement, scale: float = 1.0
) -> FinancialTable:
    """Bóc các hàng có mã số từ một khối ``<table>``.

    Với mỗi hàng, xác định vai trò từng ô theo nội dung:

    * ô là chuỗi 1–3 chữ số -> ứng viên **mã số**
    * ô đọc được thành số -> **giá trị**
    * ô văn bản dài nhất -> **tên khoản mục**

    Hàng nào không có đủ mã số, tên và ít nhất một giá trị thì bỏ qua.
    Nhờ vậy các hàng tiêu đề, hàng trống và hàng ghi chú tự bị loại.
    """
    table = FinancialTable(page=page, statement=statement)

    for raw_row in _ROW.findall(html):
        cells = [_clean(c) for c in _CELL.findall(raw_row)]
        if len(cells) < 3:
            continue

        code: str | None = None
        label = ""
        values: list[float] = []

        for cell in cells:
            number = parse_number(cell)
            if number is not None:
                # Chuỗi 1-3 chữ số vừa giống mã số vừa giống giá trị.
                # Ưu tiên coi là mã số nếu chưa gặp mã số nào và nó đứng
                # trước mọi giá trị — đúng bố cục thực tế của TT200.
                if code is None and not values and _MA_SO.match(cell):
                    code = cell
                else:
                    values.append(number)
            elif len(cell) > len(label):
                label = cell

        values = _drop_note_references(values)
        if scale != 1.0:
            values = [v * scale for v in values]
        if code and label and values:
            table.rows.append(TableRow(code=code, label=label, values=values))

    return table


def extract_tables(
    text: str,
    statements: set[Statement] | None = None,
) -> list[FinancialTable]:
    """Bóc mọi bảng có mã số từ văn bản OCR của một báo cáo.

    :param statements: nếu truyền vào, chỉ giữ bảng thuộc các loại báo cáo
        này. Mặc định giữ ba báo cáo chính và **loại bỏ phần Thuyết minh**,
        vì trong thuyết minh cột số đầu tiên là *số hiệu thuyết minh* chứ
        không phải mã số khoản mục — đọc nhầm sẽ ra dữ liệu sai.

    Chỉ trả về bảng có ít nhất một hàng hợp lệ, kèm số trang và loại báo
    cáo để truy vết minh chứng.
    """
    if statements is None:
        statements = {Statement.INCOME, Statement.BALANCE, Statement.CASH_FLOW}

    # Dựng bản đồ vị trí ký tự -> số trang và -> loại báo cáo. Mỗi bảng
    # thuộc về tiêu đề gần nhất phía trên nó.
    page_marks = [(m.start(), int(m.group(1))) for m in _PAGE.finditer(text)]
    stmt_marks = _statement_marks(text)

    def _lookup(marks: list[tuple[int, object]], pos: int, default: object) -> object:
        current = default
        for start, value in marks:
            if start > pos:
                break
            current = value
        return current

    tables = []
    # Đơn vị của bảng gần nhất có ghi rõ. Bảng nối trang đôi khi không lặp
    # lại dòng đơn vị, nhưng một báo cáo luôn dùng một đơn vị thống nhất.
    last_scale = 1.0
    prev_end = 0
    for match in _TABLE.finditer(text):
        pos = match.start()
        before = text[max(prev_end, pos - 400):pos]
        prev_end = match.end()
        scale = _unit_scale(before, match.group(1))
        if scale is None:
            scale = last_scale
        else:
            last_scale = scale

        statement = _lookup(stmt_marks, pos, Statement.UNKNOWN)
        if statement not in statements:
            continue
        page = _lookup(page_marks, pos, 0)
        table = _parse_rows(match.group(1), page, statement, scale)  # type: ignore[arg-type]
        if table.rows:
            tables.append(table)
    return tables
