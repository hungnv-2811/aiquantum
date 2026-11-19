"""Tải Báo cáo thường niên (BCTN) từ Vietstock — nguồn phần narrative.

**Vì sao cần module này.** Bộ TiniX chỉ có *báo cáo tài chính kiểm toán*,
mà báo cáo kiểm toán **không chứa Thư gửi cổ đông hay MD&A** — mục lục chỉ
gồm Thông tin công ty, Báo cáo Ban Điều hành, Báo cáo kiểm toán, ba báo cáo
và Thuyết minh. Nói cách khác TiniX cho nửa "số liệu", còn nửa "ngôn từ" mà
cơ chế NNC cần đối chiếu thì nằm trong Báo cáo thường niên.

Báo cáo thường niên có trên Zenodo nhưng đóng gói theo giai đoạn, không tải
lẻ theo mã được — riêng gói 2021–2025 đã 56,58 GB. Vietstock thì phục vụ
từng file một qua URL có quy luật::

    https://static2.vietstock.vn/data/{SÀN}/{NĂM}/BCTN/VN/{MÃ}_Baocaothuongnien_{NĂM}.pdf

Mỗi BCTN khoảng 5–15 MB, nên 16 mã × 5 năm chỉ tốn dưới 1 GB.

.. warning::
   Báo cáo thường niên trình bày kiểu tạp chí, **nhiều cột trên một trang**.
   Trích văn bản theo thứ tự đọc mặc định sẽ trộn lẫn các cột và cắt đứt
   câu giữa chừng — ví dụ ``"Doanh thu thuần thị trường nước ngoài cả năm
   đạt 10."`` bị mất phần số phía sau. Vì vậy hàm :func:`extract_text` mặc
   định bật chế độ tách cột. Kết quả vẫn cần rà lại trước khi đưa vào bước
   trích xuất khẳng định.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from smartaudit.config import INTERIM, RAW

BCTN_DIR = RAW / "bctn"

#: Văn bản đã bóc từ PDF, lưu lại để khỏi bóc lại mỗi lần chạy pipeline.
TEXT_CACHE = INTERIM / "bctn_text"

_URL = (
    "https://static2.vietstock.vn/data/{exchange}/{year}/BCTN/VN/"
    "{ticker}_Baocaothuongnien_{year}.pdf"
)

#: Các sàn thử lần lượt khi chưa biết mã niêm yết ở đâu.
_EXCHANGES = ("HOSE", "HNX", "UPCOM")

#: Ngưỡng tối thiểu để coi văn bản bóc được là một báo cáo thường niên thật.
#: Báo cáo thường niên của doanh nghiệp niêm yết luôn dài hàng chục trang;
#: dưới ngưỡng này gần như chắc chắn là công văn hoặc bản scan hỏng.
MIN_USABLE_CHARS = 20_000
MIN_USABLE_PAGES = 10


@dataclass(frozen=True)
class AnnualReport:
    """Một báo cáo thường niên đã tải về."""

    ticker: str
    year: int
    path: Path

    def extract_text(
        self,
        columns: bool = True,
        max_pages: int | None = None,
        cache: bool = True,
    ) -> str:
        """Trích văn bản, mặc định có tách cột.

        :param columns: bật tách cột. Tắt đi sẽ nhanh hơn nhưng với bố cục
            nhiều cột thì câu bị trộn lẫn, không dùng được cho trích xuất
            khẳng định.
        :param cache: lưu kết quả ra đĩa và dùng lại ở lần gọi sau. Bóc một
            báo cáo mất khoảng 12 giây, nên với 93 báo cáo thì mỗi lượt chạy
            lại pipeline tốn gần 20 phút nếu không có bộ đệm.
        """
        cache_file = self._cache_path(columns, max_pages)
        if cache and cache_file.exists():
            return cache_file.read_text(encoding="utf-8")

        import pdfplumber

        chunks: list[str] = []
        with pdfplumber.open(self.path) as pdf:
            pages = pdf.pages[:max_pages] if max_pages else pdf.pages
            for number, page in enumerate(pages, 1):
                text = _page_text(page, columns)
                if text.strip():
                    chunks.append(f"===== PAGE {number} =====\n{text}")

        result = "\n".join(chunks)
        if cache:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(result, encoding="utf-8")
        return result

    def check_usable(self, text: str) -> str | None:
        """Kiểm tra văn bản bóc được có dùng được không.

        Trả về ``None`` nếu ổn, hoặc chuỗi mô tả vấn đề.

        Cần bước này vì đường dẫn ``_Baocaothuongnien_`` trên Vietstock đôi
        khi trỏ tới **công văn công bố thông tin** chỉ một hai trang thay vì
        báo cáo thường niên đầy đủ, hoặc trỏ tới bản scan không có lớp chữ.
        Ví dụ GAS 2023 chỉ bóc được 1.297 ký tự và chữ mất hết dấu
        (``CONG BO THONG TIN DJNH KY``). Không phát hiện thì pipeline lặng
        lẽ trả về 0 khẳng định, trông như doanh nghiệp không nói gì.
        """
        if len(text) < MIN_USABLE_CHARS:
            return f"chỉ bóc được {len(text):,} ký tự (ngưỡng {MIN_USABLE_CHARS:,})"

        pages = text.count("===== PAGE")
        if pages < MIN_USABLE_PAGES:
            return f"chỉ có {pages} trang có chữ (ngưỡng {MIN_USABLE_PAGES})"

        # Văn bản tiếng Việt bình thường phải có dấu. Thiếu hẳn dấu nghĩa là
        # PDF quét ảnh và phần chữ đến từ lớp OCR kém chất lượng.
        sample = text[:5000]
        accented = sum(1 for c in sample if c in "ăâđêôơưàáảãạằắẳẵặèéẻẽẹ")
        if accented < len(sample) * 0.01:
            return "gần như không có dấu tiếng Việt — nhiều khả năng là bản scan"

        return None

    def _cache_path(self, columns: bool, max_pages: int | None) -> Path:
        # Tham số ảnh hưởng tới nội dung nên phải nằm trong tên file, tránh
        # dùng nhầm bản đệm của lần chạy với cấu hình khác.
        suffix = f"{'col' if columns else 'raw'}-{max_pages or 'all'}"
        return TEXT_CACHE / self.ticker / f"{self.ticker}_{self.year}_{suffix}.txt"


#: Khoảng trống dọc phải rộng hơn ngần này (điểm) mới coi là ranh giới cột.
#: Khoảng cách giữa các từ trong cùng dòng thường dưới 10 điểm.
_MIN_GUTTER = 18.0

#: Bề rộng tối thiểu của một cột, để không cắt nhầm ở lề hay ở ảnh minh hoạ.
_MIN_COLUMN = 80.0


def find_columns(words: list[dict], width: float) -> list[tuple[float, float]]:
    """Tìm ranh giới các cột văn bản bằng cách dò khoảng trống dọc.

    Chiếu mọi từ xuống trục ngang rồi tìm những dải không có chữ nào phủ
    qua. Dải đủ rộng chính là khoảng trắng giữa hai cột.

    Cách này thay cho việc chia đôi trang theo đường giữa: báo cáo thường
    niên là ấn phẩm trình bày kiểu tạp chí, số cột thay đổi theo từng trang
    (có trang một cột, có trang ba cột), nên mọi giả định cố định đều sai.

    Trả về danh sách khoảng ``(x0, x1)`` theo thứ tự từ trái sang phải.
    """
    if not words:
        return [(0.0, width)]

    # Hợp nhất các khoảng ngang mà chữ chiếm chỗ. Cách này chạy theo số từ
    # (O(n log n)) thay vì theo bề rộng trang nhân số từ như khi đánh dấu
    # từng điểm ảnh — khác biệt đáng kể khi quét hàng chục nghìn trang.
    spans = sorted((float(w["x0"]), float(w["x1"])) for w in words)
    merged: list[list[float]] = []
    for x0, x1 in spans:
        if merged and x0 - merged[-1][1] < _MIN_GUTTER:
            merged[-1][1] = max(merged[-1][1], x1)
        else:
            merged.append([x0, x1])

    # Dải quá hẹp không đứng riêng thành cột được (lề, số trang, gáy trang),
    # nhưng cũng không được vứt đi: một hộp số liệu hẹp bị bỏ là mất trắng
    # mọi khẳng định in trong đó, mà lại im lặng. Gộp nó vào cột liền kề để
    # chữ bên trong vẫn được trích.
    columns: list[list[float]] = []
    for x0, x1 in merged:
        if columns and x1 - x0 < _MIN_COLUMN:
            columns[-1][1] = x1
        else:
            columns.append([x0, x1])

    # Dải hẹp nằm ngoài cùng bên trái chưa có cột nào phía trước để gộp vào.
    if len(columns) > 1 and columns[0][1] - columns[0][0] < _MIN_COLUMN:
        columns[1][0] = columns[0][0]
        columns.pop(0)

    return [(x0, x1) for x0, x1 in columns]


def _page_text(page, columns: bool) -> str:
    """Trích văn bản một trang, tách cột nếu phát hiện bố cục nhiều cột."""
    if not columns:
        return page.extract_text() or ""

    words = page.extract_words()
    if len(words) < 40:
        return page.extract_text() or ""

    bounds = find_columns(words, page.width)
    if len(bounds) < 2:
        return page.extract_text() or ""

    parts = []
    # Hộp trang thực tế có thể không bắt đầu từ 0 (trang xoay, CropBox lệch):
    # kẹp theo ``page.bbox`` chứ không theo ``(0, width)``. Trước đây hai đầu
    # được kẹp độc lập nên khi cột nằm ngoài trang thì khung bị lật ngược và
    # pdfplumber ném lỗi, làm mất trắng cả báo cáo (HPG 2018–21, POW 2019–20,
    # VNM 2022).
    left_edge, top, right_edge, bottom = page.bbox
    for x0, x1 in bounds:
        # Nới nhẹ hai bên để không cắt cụt chữ ở rìa cột.
        lo = min(max(x0 - 2, left_edge), right_edge)
        hi = max(min(x1 + 2, right_edge), left_edge)
        if hi - lo < 1:
            continue
        crop = page.crop((lo, top, hi, bottom))
        text = crop.extract_text() or ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts)


def download_annual_report(
    ticker: str,
    year: int,
    dest: Path | None = None,
) -> AnnualReport | None:
    """Tải báo cáo thường niên của một mã trong một năm.

    Thử lần lượt các sàn cho tới khi gặp file. Trả về ``None`` nếu không
    tìm thấy ở sàn nào — chuyện bình thường, vì không phải mã nào cũng công
    bố báo cáo thường niên đủ mọi năm.
    """
    import requests

    dest = dest or BCTN_DIR
    target = dest / ticker / f"{ticker}_BCTN_{year}.pdf"
    if target.exists() and target.stat().st_size > 0:
        return AnnualReport(ticker, year, target)

    for exchange in _EXCHANGES:
        url = _URL.format(exchange=exchange, ticker=ticker, year=year)
        try:
            resp = requests.get(url, stream=True, timeout=180)
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            resp.close()
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(".part")
        with resp, tmp.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                fh.write(chunk)

        # Vietstock đôi khi trả trang lỗi kèm mã 200; kiểm chữ ký PDF.
        if tmp.read_bytes()[:5] != b"%PDF-":
            tmp.unlink(missing_ok=True)
            continue

        tmp.replace(target)
        return AnnualReport(ticker, year, target)

    return None


#: Ranh giới câu: dấu chấm/chấm hỏi/chấm than **không** đứng trước chữ số.
#:
#: Điều kiện "không đứng trước chữ số" là bắt buộc với tiếng Việt: dấu chấm
#: còn dùng để ngăn hàng nghìn. Nếu cắt câu ở mọi dấu chấm thì
#: ``"doanh thu đạt 10.804 tỷ đồng"`` bị xén thành ``"doanh thu đạt 10."`` —
#: mất đúng con số mà cơ chế NNC cần đối chiếu.
_SENTENCE_END = re.compile(r"(?<![\d])[.!?]+(?!\d)\s+|\n{2,}")

#: Chỉ tiêu tài chính xuất hiện trong khẳng định.
_METRIC = re.compile(
    r"doanh thu|lợi nhuận|chi phí|biên|tăng trưởng|tài sản|nợ|dòng tiền|cổ tức",
    re.IGNORECASE,
)

#: Từ chỉ xu hướng hoặc mức đạt được.
_TREND = re.compile(
    r"tăng|giảm|đạt|cải thiện|kiểm soát|vượt|duy trì|ổn định",
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[str]:
    """Tách văn bản thành câu, không cắt nhầm ở dấu ngăn hàng nghìn."""
    return [
        re.sub(r"\s+", " ", s).strip()
        for s in _SENTENCE_END.split(text)
        if s and s.strip()
    ]


def find_claim_candidates(text: str, require_number: bool = False) -> list[str]:
    """Lọc nhanh các câu có khả năng là khẳng định về số liệu.

    Giữ câu chứa **cả** một chỉ tiêu tài chính lẫn một từ chỉ xu hướng.

    :param require_number: chỉ giữ câu có chứa chữ số. Bật lên khi cần các
        khẳng định định lượng (``"doanh thu đạt 10.804 tỷ"``); tắt đi để
        lấy thêm khẳng định định tính (``"chi phí được kiểm soát tốt"``) —
        loại này chính là thứ cơ chế NNC dùng để bắt mâu thuẫn ngầm.

    Đây là bộ lọc thô, dùng khoanh vùng trước khi đưa vào mô hình trích
    xuất. Không phải bước trích xuất chính thức.
    """
    out = []
    for sentence in split_sentences(text):
        if not (10 <= len(sentence) <= 400):
            continue
        if not (_METRIC.search(sentence) and _TREND.search(sentence)):
            continue
        if require_number and not re.search(r"\d", sentence):
            continue
        out.append(sentence)
    return out
