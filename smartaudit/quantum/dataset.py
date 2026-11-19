"""Dựng bộ dữ liệu cho thí nghiệm QKA: tên khoản mục -> Mã số.

Bài toán thật: bảng số liệu **không có cột Mã số**, hệ thống phải đoán khoản
mục chỉ từ tên dòng như được in. Muốn huấn luyện và đo một bộ phân loại cho
việc đó thì cần cặp (tên, khoản mục đúng). Cặp này có sẵn miễn phí: ở mọi
bảng **có** cột Mã số, parser đã đọc được cả tên lẫn mã, nên nhãn sinh tự
động, không ai phải gán tay.

Ba quyết định thiết kế quan trọng, đều có lý do từ dữ liệu thật:

1. **Nhóm khoản mục:** các dòng *hoạt động đầu tư* trong Báo cáo lưu chuyển
   tiền tệ (Mã số 21–27 và dòng tổng 30). Xem :data:`GROUP`.
2. **Bỏ ngân hàng:** báo cáo ngân hàng theo Thông tư 49 dùng hệ mã số khác,
   đọc theo mã Thông tư 200 sẽ ra nhãn sai. Xem :data:`BANKS`.
3. **Khử trùng lặp theo tên:** mỗi tên (sau chuẩn hoá) chỉ là **một** mẫu, nên
   một tên không thể vừa nằm ở tập huấn luyện vừa nằm ở tập kiểm tra. Xem
   :func:`build_dataset`.

Module này không cần qiskit, chỉ cần parser và ontology có sẵn.
"""

from __future__ import annotations

import collections
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from smartaudit.ingest import iter_reports
from smartaudit.ontology.vas import _norm
from smartaudit.tables import Statement, extract_tables

#: Báo cáo mà nhóm khoản mục thuộc về. Mã số chỉ duy nhất trong phạm vi
#: từng báo cáo (mã ``21`` ở Kết quả kinh doanh là *Doanh thu hoạt động tài
#: chính*), nên bộ dữ liệu chỉ lấy dòng của Lưu chuyển tiền tệ.
STATEMENT = Statement.CASH_FLOW

#: Nhóm khoản mục đem thử: phần *Lưu chuyển tiền từ hoạt động đầu tư* theo
#: mẫu B03-DN của Thông tư 200.
#:
#: Vì sao chọn nhóm này (khảo sát trên 13 mã phi ngân hàng, 11/2026):
#:
#: * **Hay nhầm khi chỉ nhìn tên:** các mã đi thành cặp *chi / thu* gần như
#:   trùng chữ — 23 "Tiền chi cho vay, mua công cụ nợ..." và 24 "Tiền thu hồi
#:   cho vay, bán lại công cụ nợ..."; 25 "Tiền chi đầu tư góp vốn..." và 26
#:   "Tiền thu hồi đầu tư góp vốn...". Nhầm một chữ là **đảo chiều dòng
#:   tiền**, đúng loại lỗi khiến đối chiếu NNC sai dấu.
#: * **Đủ biến thể để kiểm chứng chéo:** mỗi mã 21–27 có 25–54 cách viết
#:   khác nhau (lỗi OCR, gộp/tách từ, viết tắt TSCĐ...). Trái lại, 31 khoản
#:   mục trong ontology hiện tại có trung vị chỉ 6 cách viết sau chuẩn hoá
#:   (29/31 khoản mục không quá 15) — quá ít để chia 5 phần mà vẫn còn ý
#:   nghĩa thống kê. "Hàng nghìn cặp" nhãn tự động là đếm theo **dòng**; đếm
#:   theo **tên khác nhau** thì ít hơn nhiều.
#: * **Nối với ontology:** mã 30 chính là khoản mục ``cash_flow_investing``.
#:
#: Thứ tự trong tuple là thứ tự nhãn trong ma trận nhầm lẫn.
GROUP: tuple[str, ...] = ("21", "22", "23", "24", "25", "26", "27", "30")

#: Ngân hàng lập báo cáo theo Thông tư 49 với hệ mã số riêng. Ví dụ dòng
#: "Thu nhập lãi và các khoản thu nhập tương tự" bị đọc thành mã 25 của Thông
#: tư 200 (xem alias của ``selling_expense`` trong ``vas_mapping.yaml``). Giữ
#: lại sẽ đưa nhãn sai có hệ thống vào dữ liệu huấn luyện.
BANKS: frozenset[str] = frozenset({"MBB", "TCB", "VPB"})

#: Tên ngắn hơn ngần này ký tự (sau chuẩn hoá) là mảnh OCR vỡ, không phải
#: tên khoản mục — ví dụ ô chỉ chứa dấu ngoặc hay chữ số.
_MIN_KEY_LEN = 5

_NON_LETTER = re.compile(r"[^a-z]+")


def name_key(label: str) -> str:
    """Chuẩn hoá tên khoản mục thành *khoá* dùng để khử trùng lặp và trích đặc trưng.

    Dựa trên đúng hàm chuẩn hoá của ontology (bỏ dấu, chữ thường, bỏ số thứ
    tự đầu dòng) rồi **chỉ giữ chữ cái**. Bỏ chữ số là có chủ ý: tên khoản mục
    hay dính công thức như ``(30 = 21 + 22 + ...)`` — trong đó có **chính Mã
    số**. Giữ lại thì mô hình học thuộc con số chứ không học tên, tức là rò
    rỉ nhãn vào đặc trưng.

    Giải mã thực thể HTML trước tiên: parser chỉ đổi ``&amp;``, nên vài tên
    còn dính ``&quot;`` hay ``&#x27;`` — không giải mã thì "(&quot;TSCĐ&quot;)"
    sinh ra chữ "quot" giả trong tên.

    >>> name_key("1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác")
    'tien chi de mua sam xay dung tscd va cac tai san dai han khac'
    >>> name_key("Lưu chuyển tiền thuần từ hoạt động đầu tư (30 = 21+22+23+24+25+26+27)")
    'luu chuyen tien thuan tu hoat dong dau tu'
    >>> name_key("Tiền chi mua sắm tài sản cố định (&quot;TSCĐ&quot;)")
    'tien chi mua sam tai san co dinh tscd'
    """
    return _NON_LETTER.sub(" ", _norm(html.unescape(label))).strip()


@dataclass(frozen=True)
class RawRow:
    """Một dòng có Mã số bóc được từ báo cáo, trước khi khử trùng lặp."""

    ticker: str
    year: int
    code: str
    #: Tên khoản mục như in trong báo cáo.
    label: str


@dataclass(frozen=True)
class NameSample:
    """Một mẫu của bộ dữ liệu: một tên khoản mục duy nhất và nhãn của nó."""

    #: Tên đã chuẩn hoá (xem :func:`name_key`) — đầu vào của đặc trưng TF-IDF.
    key: str
    #: Mã số theo Thông tư 200 — nhãn cần đoán.
    code: str
    #: Cách viết gốc gặp nhiều nhất của tên này — đầu vào của rapidfuzz, vì
    #: hệ thống hiện tại khớp gần trên chuỗi gốc.
    raw: str
    #: Số dòng trong corpus mang tên này (một tên lặp ở nhiều báo cáo).
    n_rows: int
    #: Số doanh nghiệp khác nhau từng dùng tên này.
    n_tickers: int


def collect_rows(
    root: Path | None = None,
    codes: Iterable[str] = GROUP,
    tickers: list[str] | None = None,
) -> Iterator[RawRow]:
    """Duyệt các báo cáo TiniX đã tải, trả về các dòng thuộc nhóm mã số.

    Chỉ **gọi** parser có sẵn (:func:`extract_tables`), không đọc bảng theo
    cách riêng, để dữ liệu thí nghiệm phản ánh đúng những gì hệ thống thấy.
    Không ghi gì ra đĩa. ``tickers`` để giới hạn vài mã (dùng trong test).
    """
    wanted = set(codes)
    for report in iter_reports(root, tickers):
        if report.ticker in BANKS:
            continue
        tables = extract_tables(report.read(), statements={STATEMENT})
        for table in tables:
            for row in table.rows:
                if row.code in wanted:
                    yield RawRow(report.ticker, report.year, row.code, row.label)


@dataclass
class DatasetStats:
    """Thống kê phễu xử lý, ghi kèm kết quả để người duyệt kiểm lại."""

    n_rows: int = 0               # số dòng có mã thuộc nhóm
    n_short_dropped: int = 0      # dòng có tên quá ngắn (mảnh OCR vỡ)
    n_unique_names: int = 0       # số tên khác nhau sau chuẩn hoá
    n_conflicts: int = 0          # tên từng mang hơn một mã số
    n_conflicts_dropped: int = 0  # trong đó: không có mã nào chiếm đa số -> bỏ
    n_samples: int = 0            # số mẫu cuối cùng


def build_dataset(rows: Iterable[RawRow]) -> tuple[list[NameSample], DatasetStats]:
    """Khử trùng lặp theo tên và gán nhãn theo đa số.

    * **Mỗi tên một mẫu.** Một tên chuẩn như "Tiền chi đầu tư góp vốn vào
      đơn vị khác" lặp lại hàng trăm lần trong corpus. Nếu giữ nguyên các
      bản lặp rồi chia ngẫu nhiên, tập kiểm tra sẽ toàn tên mô hình đã thấy
      lúc huấn luyện và độ chính xác bị thổi phồng. Gộp về một mẫu thì phép
      đo trả lời đúng câu hỏi cần hỏi: *gặp một cách viết chưa từng thấy, mô
      hình có đoán đúng khoản mục không?*
    * **Nhãn theo đa số.** Nhãn tự động có nhiễu: bảng bị phân loại nhầm báo
      cáo, hoặc OCR gộp hai dòng làm một. Một tên mang nhiều mã thì lấy mã
      chiếm **quá nửa** số lần xuất hiện; không mã nào quá nửa thì bỏ tên đó
      — giống cách ontology loại tên mập mờ.

    Kết quả sắp theo (mã số, khoá) để mọi lần chạy cho cùng thứ tự.
    """
    stats = DatasetStats()
    codes_by_key: dict[str, collections.Counter[str]] = collections.defaultdict(
        collections.Counter
    )
    raws_by_key: dict[str, collections.Counter[str]] = collections.defaultdict(
        collections.Counter
    )
    tickers_by_key: dict[str, set[str]] = collections.defaultdict(set)

    for row in rows:
        stats.n_rows += 1
        key = name_key(row.label)
        if len(key) < _MIN_KEY_LEN:
            stats.n_short_dropped += 1
            continue
        codes_by_key[key][row.code] += 1
        raws_by_key[key][re.sub(r"\s+", " ", row.label).strip()] += 1
        tickers_by_key[key].add(row.ticker)

    stats.n_unique_names = len(codes_by_key)
    samples: list[NameSample] = []
    for key, counter in codes_by_key.items():
        total = sum(counter.values())
        code, count = counter.most_common(1)[0]
        if len(counter) > 1:
            stats.n_conflicts += 1
            if count * 2 <= total:  # không có mã nào chiếm quá nửa
                stats.n_conflicts_dropped += 1
                continue
        samples.append(
            NameSample(
                key=key,
                code=code,
                raw=raws_by_key[key].most_common(1)[0][0],
                n_rows=total,
                n_tickers=len(tickers_by_key[key]),
            )
        )

    order = {code: i for i, code in enumerate(GROUP)}
    samples.sort(key=lambda s: (order.get(s.code, len(order)), s.key))
    stats.n_samples = len(samples)
    return samples, stats


def make_folds(
    labels: list[str],
    n_splits: int = 5,
    seed: int = 42,
) -> list[tuple[list[int], list[int]]]:
    """Chia kiểm chứng chéo phân tầng, cố định hạt giống.

    Phân tầng theo nhãn để mỗi phần đều có đủ 8 mã số — lớp nhỏ nhất (mã 30)
    chỉ có hơn chục tên. Vì :func:`build_dataset` đã gộp mỗi tên thành một
    mẫu, chia theo mẫu cũng là chia theo tên: không tên nào nằm ở cả hai phía.

    Trả về danh sách ``(chỉ số huấn luyện, chỉ số kiểm tra)``.
    """
    from sklearn.model_selection import StratifiedKFold

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return [
        (train.tolist(), test.tolist())
        for train, test in skf.split(labels, labels)
    ]
