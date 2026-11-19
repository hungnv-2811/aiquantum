"""Đối chiếu khẳng định trong ngôn từ với số liệu trong báo cáo tài chính.

Đây là lõi giá trị của SmartAudit-Quantum. Mỗi khẳng định được kiểm trên ba
chiều, và điểm nhất quán tổng hợp là trung bình có trọng số của các chiều
áp dụng được:

1. **Đối chiếu giá trị** — con số nêu trong câu có khớp ô tương ứng trong
   bảng không. Ví dụ "doanh thu đạt 61.782 tỷ" so với mã 10 của Báo cáo kết
   quả kinh doanh.
2. **Đối chiếu hướng** — câu nói "tăng" thì số liệu có tăng thật không.
   Đây là chiều bắt được nhiều mâu thuẫn nhất trong thực tế.
3. **Đối chiếu định tính** — câu nhận định không kèm số ("chi phí được kiểm
   soát tốt") được quy về một kỳ vọng định lượng rồi kiểm. Đây chính là loại
   mâu thuẫn ngầm mà mắt thường khó bắt và là điểm mới số 1 trong hồ sơ.

Mỗi kết luận đều kèm :class:`Evidence` ghi rõ lấy số từ trang nào, bảng
nào, mã số nào, và phép tính đối chiếu ra sao — đủ chi tiết để kiểm toán
viên đưa vào hồ sơ làm việc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from smartaudit.config import NUMERIC_TOLERANCE
from smartaudit.nlp.claims import Claim, Trend
from smartaudit.tables import FinancialTable, Statement

#: Chi phí tăng nhanh hơn doanh thu quá ngưỡng này thì lời khẳng định
#: "kiểm soát tốt chi phí" bị coi là mâu thuẫn.
COST_CONTROL_TOLERANCE = 0.02

#: Biến động dưới ngưỡng này coi như đi ngang, phục vụ kiểm khẳng định
#: "ổn định" / "duy trì".
FLAT_BAND = 0.03

#: Trọng số các chiều khi tổng hợp điểm nhất quán.
WEIGHTS = {"numeric": 0.5, "directional": 0.35, "qualitative": 0.15}

#: Dung sai cho con số câu văn nêu là gần đúng ("gần 103 nghìn tỷ").
APPROX_TOLERANCE = 0.05

#: Khoá cho hai định nghĩa doanh thu thay thế. "Doanh thu" trong báo cáo
#: thường niên có thể là doanh thu thuần (Mã 10), tổng doanh thu bán hàng
#: (Mã 01, HPG), hay tổng doanh thu gồm cả tài chính và thu nhập khác (Mã 10
#: + 21 + 31, GAS). Cả ba đều là định nghĩa kế toán hợp lệ; câu khớp với bất
#: kỳ định nghĩa nào thì không phải mâu thuẫn.
REVENUE_GROSS = "_revenue_gross"
REVENUE_TOTAL = "_revenue_total"

#: Khoản mục chi phí — chỉ những khoản này mới kiểm "kiểm soát tốt chi phí".
COST_METRICS = {
    "cost_of_goods_sold", "selling_expense", "admin_expense",
    "financial_expense", "interest_expense",
}

#: Mã số chi phí trên Báo cáo kết quả kinh doanh. Nhiều doanh nghiệp in các
#: dòng này trong ngoặc đơn theo quy ước trình bày, parser đọc thành số âm;
#: chi phí (58.053) → (92.716) khi đó bị tính thành **tăng** 37,4% trong khi
#: thực tế giảm. Lấy giá trị tuyệt đối trước khi so.
#: (Mã 24 — lãi/lỗ trong công ty liên kết — cố ý không có: số âm ở đó là lỗ thật.)
_INCOME_EXPENSE_CODES = {"02", "11", "22", "23", "25", "26", "32", "51", "52"}


class Unit(str, Enum):
    """Đơn vị của một chỉ tiêu.

    Phải mang theo đơn vị thì mới in ra và đối chiếu đúng được: cùng con
    số ``6.55``, hiểu là tiền thì in ``"7"``, hiểu là tỷ lệ thì in
    ``"655,0%"``, còn đúng ra phải là ``"6,55 lần"``.
    """

    MONEY = "đồng"
    #: Tỷ lệ, lưu dưới dạng phân số (``0.414`` = 41,4%).
    PERCENT = "phần trăm"
    #: Số lần, ví dụ vòng quay hàng tồn kho.
    TIMES = "lần"


class Verdict(str, Enum):
    CONSISTENT = "nhất quán"
    INCONSISTENT = "mâu thuẫn"
    #: Không đủ dữ liệu để kết luận — không phải lỗi của doanh nghiệp.
    UNVERIFIABLE = "không kiểm chứng được"


@dataclass(frozen=True)
class Evidence:
    """Vết truy xuất cho một phép đối chiếu."""

    #: Chiều kiểm: "numeric" | "directional" | "qualitative".
    dimension: str
    #: Diễn giải phép tính bằng tiếng Việt, dạng người đọc hiểu ngay.
    explanation: str
    passed: bool
    #: Nguồn số liệu: trang và mã số trong báo cáo tài chính.
    source_page: int | None = None
    source_code: str | None = None
    source_label: str | None = None


@dataclass
class NNCResult:
    """Kết quả đối chiếu một khẳng định."""

    claim: Claim
    verdict: Verdict
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def score(self) -> float | None:
        """Điểm nhất quán 0–1, hoặc ``None`` nếu không kiểm chứng được."""
        applied = [e for e in self.evidence if e.dimension in WEIGHTS]
        if not applied:
            return None
        total = sum(WEIGHTS[e.dimension] for e in applied)
        earned = sum(WEIGHTS[e.dimension] for e in applied if e.passed)
        return earned / total


#: Số liệu một chỉ tiêu, gộp từ các bảng của một báo cáo.
@dataclass(frozen=True)
class Fact:
    concept: str
    current: float
    previous: float | None
    page: int
    code: str
    label: str
    #: Báo cáo mà số liệu này lấy ra từ đó.
    statement: Statement = Statement.UNKNOWN
    #: Khoản mục bóc thẳng từ bảng luôn là số tiền; tỷ số suy ra thì khác.
    unit: Unit = Unit.MONEY

    @property
    def growth(self) -> float | None:
        """Tỷ lệ tăng trưởng so với kỳ trước."""
        if self.previous is None or self.previous == 0:
            return None
        return (self.current - self.previous) / abs(self.previous)


@dataclass(frozen=True)
class Derived:
    """Công thức tính một tỷ số từ hai khoản mục."""

    numerator: str
    denominator: str
    label: str
    unit: Unit


#: Tỷ số suy ra từ hai khoản mục. Cần thiết vì báo cáo thường niên hay nói
#: về biên lợi nhuận và vòng quay, những chỉ số không có sẵn dòng riêng
#: trong báo cáo tài chính.
DERIVED: dict[str, Derived] = {
    "gross_margin": Derived(
        "gross_profit", "revenue_net", "biên lợi nhuận gộp", Unit.PERCENT,
    ),
    "net_margin": Derived(
        "profit_after_tax", "revenue_net", "biên lợi nhuận ròng", Unit.PERCENT,
    ),
    "inventory_turnover": Derived(
        "cost_of_goods_sold", "inventories", "vòng quay hàng tồn kho", Unit.TIMES,
    ),
    "selling_expense_ratio": Derived(
        "selling_expense", "revenue_net", "biên chi phí bán hàng", Unit.PERCENT,
    ),
    "admin_expense_ratio": Derived(
        "admin_expense", "revenue_net", "biên chi phí quản lý", Unit.PERCENT,
    ),
}

#: Chênh lệch vượt ngưỡng này thì kết luận **không kiểm chứng được** thay vì
#: mâu thuẫn.
#:
#: Lý do: thao túng thông tin trong báo cáo là hành vi tinh vi — nói 15%
#: trong khi thực tế 14%. Còn lệch tới vài chục lần gần như luôn có nghĩa
#: câu văn đang nói về một công ty con, một mảng kinh doanh hay một thị
#: trường lẻ, chứ không phải số hợp nhất. Gắn cờ mâu thuẫn trong trường hợp
#: đó là cáo buộc sai doanh nghiệp, nên hệ thống chọn im lặng và nói rõ vì
#: sao chưa kết luận được.
SCOPE_MISMATCH_THRESHOLD = 0.5

#: Biến động một kỳ vượt ngưỡng này thì coi chuỗi số liệu bị **đứt gãy**,
#: không dùng để đối chiếu xu hướng nữa.
#:
#: Doanh nghiệp lớn hiếm khi tăng hay giảm quá 40% doanh thu trong một năm
#: nếu không có tái cơ cấu. Ví dụ FPT 2018: doanh thu thô giảm 45,6% vì
#: thoái vốn mảng bán lẻ và phân phối. Khi đó số hai năm không cùng phạm
#: vi, và mọi khẳng định về tăng trưởng đều bị gắn cờ oan — báo cáo thường
#: niên trình bày trên cơ sở tương đương, còn hệ thống lại so số thô.
#:
#: Gặp trường hợp này, hệ thống báo "chưa kiểm chứng được" kèm lý do thay
#: vì kết luận mâu thuẫn. Kiểm toán viên vẫn thấy khẳng định đó trong danh
#: sách cần xem, chỉ là không bị cáo buộc sai.
STRUCTURAL_BREAK_THRESHOLD = 0.4


def _derive(key: str, facts: dict[str, Fact]) -> Fact | None:
    """Tính một tỷ số từ các khoản mục đã bóc được.

    Trả về ``None`` nếu thiếu tử số, mẫu số, hoặc thiếu số liệu kỳ trước —
    không có kỳ trước thì không kiểm được hướng biến động.
    """
    spec = DERIVED.get(key)
    if spec is None:
        return None

    num, den = facts.get(spec.numerator), facts.get(spec.denominator)
    if num is None or den is None or not den.current:
        return None

    # Nếu hai khoản mục cùng thuộc một báo cáo thì phải lấy từ cùng trang.
    # Không ràng buộc điều này thì có thể lấy lợi nhuận gộp của báo cáo hợp
    # nhất chia cho doanh thu của một bảng phân tích theo mảng, ra tỷ số
    # không tồn tại trong thực tế.
    #
    # Ngược lại, tỷ số bắc cầu giữa hai báo cáo — như vòng quay hàng tồn
    # kho lấy giá vốn từ Kết quả kinh doanh chia cho tồn kho từ Cân đối kế
    # toán — thì khác trang là đúng bản chất.
    if num.statement is den.statement and num.page != den.page:
        return None

    previous = None
    if num.previous is not None and den.previous:
        previous = num.previous / den.previous

    return Fact(
        concept=key,
        current=num.current / den.current,
        previous=previous,
        page=num.page,
        code=f"{num.code}/{den.code}",
        label=f"{spec.label} = {num.label} / {den.label}",
        unit=spec.unit,
    )


def build_facts(tables: list[FinancialTable]) -> dict[str, Fact]:
    """Gom số liệu từ các bảng thành bảng tra theo khoá ontology.

    Khi một khoá xuất hiện ở nhiều bảng, giữ bản có giá trị tuyệt đối lớn
    nhất: bảng tổng hợp luôn mang số đầy đủ, còn bảng chi tiết theo mảng
    hay theo quý chỉ mang một phần.
    """
    from smartaudit.ontology import load_ontology

    onto = load_ontology()
    facts: dict[str, Fact] = {}

    gross_revenue: Fact | None = None
    has_deductions = False
    #: Dòng thu nhập cần để dựng "tổng doanh thu" theo cách nhiều doanh
    #: nghiệp tự định nghĩa: Mã 10 + 21 (doanh thu tài chính) + 31 (thu nhập khác).
    income_rows: dict[str, tuple[float, float | None]] = {}

    for table in tables:
        for row in table.rows:
            current, previous = row.current, row.previous
            if current is None:
                continue
            if table.statement is Statement.INCOME and row.code in _INCOME_EXPENSE_CODES:
                current = abs(current)
                previous = abs(previous) if previous is not None else None
            if table.statement is Statement.INCOME and row.code in ("10", "21", "31"):
                kept = income_rows.get(row.code)
                if kept is None or abs(current) > abs(kept[0]):
                    income_rows[row.code] = (current, previous)
            if table.statement is Statement.INCOME and row.code == "02" and current:
                has_deductions = True
            if table.statement is Statement.INCOME and row.code == "01":
                candidate = Fact(
                    concept="revenue_net", current=current, previous=previous,
                    page=table.page, code=row.code, label=row.label,
                    statement=table.statement,
                )
                if gross_revenue is None or abs(current) > abs(gross_revenue.current):
                    gross_revenue = candidate

            concept = onto.by_code(table.statement, row.code)
            if concept is None:
                continue

            fact = Fact(
                concept=concept.key,
                current=current,
                previous=previous,
                page=table.page,
                code=row.code,
                label=row.label,
                statement=table.statement,
            )
            existing = facts.get(concept.key)
            if existing is None or abs(fact.current) > abs(existing.current):
                facts[concept.key] = fact

    # Doanh nghiệp không có khoản giảm trừ doanh thu có thể bỏ hẳn dòng Mã
    # 10 và trình bày "20 = 01 − 11" (PC1 từ 2021). Khi đó doanh thu thuần
    # bằng đúng Mã 01. Không có bước này thì mọi câu về doanh thu của các
    # năm đó rơi vào "không kiểm chứng được".
    if "revenue_net" not in facts and gross_revenue is not None and not has_deductions:
        facts["revenue_net"] = gross_revenue

    # Các định nghĩa "doanh thu" khác mà báo cáo thường niên hay dùng. Chỉ
    # dùng làm phương án đối chiếu thay thế cho con số tuyệt đối (xem
    # check_claim), không thay cho doanh thu thuần.
    if gross_revenue is not None:
        facts[REVENUE_GROSS] = gross_revenue
    if all(c in income_rows for c in ("10", "21", "31")):
        cur = sum(income_rows[c][0] for c in ("10", "21", "31"))
        prevs = [income_rows[c][1] for c in ("10", "21", "31")]
        rev = facts.get("revenue_net")
        facts[REVENUE_TOTAL] = Fact(
            concept=REVENUE_TOTAL, current=cur,
            previous=sum(prevs) if all(p is not None for p in prevs) else None,  # type: ignore[arg-type]
            page=rev.page if rev else 0, code="10+21+31",
            label="Tổng doanh thu = doanh thu thuần + doanh thu tài chính + thu nhập khác",
            statement=Statement.INCOME,
        )

    for key in DERIVED:
        derived = _derive(key, facts)
        if derived is not None:
            facts[key] = derived

    return facts


def _fmt(value: float) -> str:
    """Định dạng số tiền cho người đọc: quy về tỷ đồng khi đủ lớn."""
    if abs(value) >= 1e9:
        return f"{value / 1e9:,.0f} tỷ".replace(",", ".")
    if abs(value) >= 1e6:
        return f"{value / 1e6:,.0f} triệu".replace(",", ".")
    return f"{value:,.0f}".replace(",", ".")


def _fmt_fact(fact: Fact, value: float | None) -> str:
    """Định dạng giá trị theo đúng đơn vị của khoản mục.

    Tỷ số phải hiện dạng phần trăm hoặc số lần, không dùng đơn vị tiền —
    nếu không thì biên lợi nhuận 0,11 bị in thành ``"0"``, còn vòng quay
    6,55 lần bị in thành ``"655,0%"``.
    """
    if value is None:
        return "—"
    if fact.unit is Unit.PERCENT:
        return f"{value:.1%}"
    if fact.unit is Unit.TIMES:
        return f"{value:.2f} lần"
    return _fmt(value)


def _check_numeric(claim: Claim, fact: Fact) -> Evidence | None:
    """Con số nêu trong câu có khớp số liệu trong bảng không."""
    # Với tỷ số, con số kèm đơn vị tiền trong câu (nếu có) nói về khoản mục
    # khác, không phải về chính tỷ số — bỏ qua để khỏi so nhầm.
    if claim.value is None or claim.is_ratio:
        return None

    diff = abs(claim.value - fact.current) / abs(fact.current) if fact.current else 1.0

    if diff > SCOPE_MISMATCH_THRESHOLD:
        return Evidence(
            dimension="scope",
            explanation=(
                f"Câu nêu {_fmt(claim.value)}, trong khi số hợp nhất là "
                f"{_fmt(fact.current)} (mã {fact.code}, trang {fact.page}) — "
                f"chênh {diff:.0%}. Chênh lệch quá lớn nên nhiều khả năng câu "
                f"nói về một công ty con, một mảng kinh doanh hoặc một thị "
                f"trường lẻ. Hệ thống không kết luận mâu thuẫn."
            ),
            passed=False,
            source_page=fact.page,
            source_code=fact.code,
            source_label=fact.label,
        )

    # Dung sai = max(ngưỡng chung, sai số do làm tròn con số trong câu):
    # "1,9 tỷ" khớp với 1,94 tỷ vì 1,94 làm tròn ra 1,9.
    tolerance = max(NUMERIC_TOLERANCE, claim.value_tol)
    if claim.approx == "min":
        # "Doanh thu trên 6.600 tỷ" đúng khi số thật ≥ 6.600 tỷ.
        passed = fact.current >= claim.value * (1 - tolerance)
        how = "câu nêu cận dưới"
    elif claim.approx == "approx":
        passed = diff <= max(APPROX_TOLERANCE, tolerance)
        how = "câu nêu số gần đúng"
    else:
        passed = diff <= tolerance
        how = None
    verb = "khớp" if passed else "lệch"
    return Evidence(
        dimension="numeric",
        explanation=(
            f"Câu nêu {_fmt(claim.value)}; báo cáo tài chính (mã {fact.code}, "
            f"trang {fact.page}) ghi {_fmt(fact.current)} — {verb} "
            f"{diff:.1%}" + (f" ({how})." if how else ".")
        ),
        passed=passed,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_continuity(fact: Fact) -> Evidence | None:
    """Chuỗi số liệu có bị đứt gãy giữa hai kỳ không.

    Trả về minh chứng cảnh báo nếu có; ``None`` nếu chuỗi liền mạch.
    """
    growth = fact.growth
    if growth is None or abs(growth) <= STRUCTURAL_BREAK_THRESHOLD:
        return None

    return Evidence(
        dimension="continuity",
        explanation=(
            f"Số liệu hai kỳ biến động {growth:+.0%} "
            f"({_fmt_fact(fact, fact.previous)} → {_fmt_fact(fact, fact.current)}, "
            f"mã {fact.code}, trang {fact.page}). Mức này thường đến từ "
            f"thoái vốn hoặc thay "
            f"đổi phạm vi hợp nhất, khiến hai năm không so sánh trực tiếp "
            f"được. Hệ thống không kết luận về xu hướng."
        ),
        passed=False,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_direction(claim: Claim, fact: Fact) -> Evidence | None:
    """Hướng biến động trong câu có đúng với số liệu không."""
    growth = fact.growth
    if growth is None or claim.trend in (Trend.REACH, Trend.CONTROLLED):
        return None
    # Câu nói về tỷ số ("hệ số nợ/VCSH giảm", "ROA tăng") mà ta chỉ có khoản
    # mục tiền thì không so hướng được: VCSH tăng không có nghĩa hệ số nợ
    # trên VCSH tăng. Hai hàm kiểm tỷ số đã có chốt này; thiếu ở đây từng
    # gây 12% số cờ oan (rà soát 12/11/2026).
    if claim.is_ratio and fact.unit is Unit.MONEY:
        return None

    if claim.trend is Trend.UP:
        passed = growth > 0
        expected = "tăng"
    elif claim.trend is Trend.DOWN:
        passed = growth < 0
        expected = "giảm"
    else:  # FLAT
        passed = abs(growth) <= FLAT_BAND
        expected = "đi ngang"

    actual = "tăng" if growth > 0 else "giảm"
    return Evidence(
        dimension="directional",
        explanation=(
            f"Câu khẳng định {expected}; số liệu cho thấy {actual} "
            f"{abs(growth):.1%} ({_fmt_fact(fact, fact.previous)} → "
            f"{_fmt_fact(fact, fact.current)}, mã {fact.code}, trang {fact.page})."
        ),
        passed=passed,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_ratio_level(claim: Claim, fact: Fact) -> Evidence | None:
    """Với khẳng định về tỷ số, phần trăm nêu ra là **mức**, không phải mức tăng.

    "Biên lợi nhuận gộp đạt 42%" nói tỷ số hiện ở 42%, khác hẳn "doanh thu
    tăng 42%". Nhầm hai loại này sẽ tạo mâu thuẫn giả hàng loạt.
    """
    if not claim.is_ratio or claim.percent is None:
        return None
    # "hoàn thành 94,6% kế hoạch năm" là mức hoàn thành kế hoạch nội bộ,
    # không phải giá trị của tỷ số — báo cáo tài chính không có kế hoạch để
    # đối chiếu.
    if claim.basis == "kế hoạch":
        return None
    # Chỉ so được khi con số đối chiếu thật sự là một tỷ số đo bằng phần
    # trăm. Nếu câu nói về tỷ số mà ta chỉ có giá trị tuyệt đối của khoản
    # mục thì bỏ qua — so 25,8% với 13.447 tỷ đồng là vô nghĩa. Vòng quay
    # hàng tồn kho cũng vậy: 6,55 *lần* không so được với một con số phần
    # trăm.
    if fact.unit is not Unit.PERCENT:
        return None
    # "Biên lợi nhuận gộp tăng 2,0%" nói về **mức thay đổi** của biên, không
    # phải giá trị của biên — việc của :func:`_check_ratio_change`. Ngoại lệ:
    # "tăng từ 11,8% lên 19,2%" thì 19,2% là mức (``percent_is_level``).
    if claim.trend not in (Trend.REACH, Trend.FLAT) and not claim.percent_is_level:
        return None

    stated = claim.percent / 100
    diff = abs(stated - fact.current)
    passed = diff <= 0.015  # lệch dưới 1,5 điểm phần trăm
    return Evidence(
        dimension="numeric",
        explanation=(
            f"Câu nêu mức {claim.percent:.1f}%; tính từ báo cáo tài chính "
            f"({fact.label}) ra {_fmt_fact(fact, fact.current)} — lệch "
            f"{diff * 100:.2f} điểm phần trăm."
        ),
        passed=passed,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_ratio_change(claim: Claim, fact: Fact) -> Evidence | None:
    """Với khẳng định tỷ số **tăng/giảm** bao nhiêu phần trăm.

    "Biên lợi nhuận gộp tăng 2,0%" có hai cách hiểu đều thông dụng trong
    báo cáo thường niên tiếng Việt: tăng 2,0 **điểm phần trăm**, hoặc tăng
    2,0% **tương đối**. Hệ thống chấp nhận khi số liệu khớp một trong hai —
    kết luận mâu thuẫn dựa trên cách hiểu mà tác giả không dùng là cáo buộc
    sai. Nếu cả hai cách đều lệch thì mới gắn cờ.
    """
    if not claim.is_ratio or claim.percent is None or claim.basis == "kế hoạch":
        return None
    if claim.percent_is_level:
        return None
    if claim.trend not in (Trend.UP, Trend.DOWN) or fact.previous is None:
        return None
    # Câu nói về tỷ số mà ta chỉ có giá trị tuyệt đối của khoản mục thì bỏ
    # qua, y như :func:`_check_ratio_level`. Không có chốt này thì "ROE tăng
    # gần 2%" bị đem so với mức tăng của **vốn chủ sở hữu** — hai đại lượng
    # khác hẳn nhau, và câu đúng bị gắn cờ oan.
    if fact.unit is Unit.MONEY:
        return None

    stated = claim.percent / 100
    if claim.trend is Trend.DOWN:
        stated = -stated

    readings: dict[str, float] = {}
    if fact.unit is Unit.PERCENT:
        readings["điểm phần trăm"] = fact.current - fact.previous
    if fact.growth is not None:
        readings["tương đối"] = fact.growth
    if not readings:
        return None

    diff = min(abs(stated - actual) for actual in readings.values())
    detail = ", ".join(
        f"{value:+.1%} tương đối" if how == "tương đối"
        else f"{value * 100:+.2f} điểm phần trăm"
        for how, value in readings.items()
    )
    return Evidence(
        dimension="numeric",
        explanation=(
            f"Câu nêu {claim.trend.value} {claim.percent:.1f}%; tính từ báo cáo "
            f"tài chính ({fact.label}) ra {_fmt_fact(fact, fact.previous)} → "
            f"{_fmt_fact(fact, fact.current)}, tức {detail}."
        ),
        passed=diff <= 0.01,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_percent(claim: Claim, fact: Fact) -> Evidence | None:
    """Tỷ lệ tăng trưởng nêu trong câu có đúng không.

    Chỉ kiểm khi câu viện dẫn mốc so sánh là kỳ trước. Nếu câu nói "hoàn
    thành 110,7% kế hoạch" thì con số đó so với kế hoạch nội bộ, không đối
    chiếu được từ báo cáo tài chính. Bỏ qua khẳng định về tỷ số — phần trăm
    ở đó là mức, do :func:`_check_ratio_level` xử lý.
    """
    if claim.percent is None or claim.basis == "kế hoạch" or claim.is_ratio:
        return None
    growth = fact.growth
    if growth is None:
        return None

    stated = claim.percent / 100
    # Dấu phải lấy từ từ chỉ hướng **đi kèm con số phần trăm**, không phải
    # từ chỉ hướng của cả câu: "đạt 2.554 tỷ đồng, giảm 16,2%" có
    # ``claim.trend`` là REACH, nhưng 16,2% đó là mức giảm. Lấy nhầm ở đây
    # biến một câu đúng thành mâu thuẫn.
    if (claim.percent_trend or claim.trend) is Trend.DOWN:
        stated = -stated

    diff = abs(stated - growth)
    passed = diff <= 0.01  # lệch dưới 1 điểm phần trăm
    return Evidence(
        dimension="numeric",
        explanation=(
            f"Câu nêu mức {claim.percent:.1f}%; tính từ báo cáo tài chính "
            f"({_fmt_fact(fact, fact.previous)} → {_fmt_fact(fact, fact.current)}) "
            f"ra {growth:+.1%} — lệch {diff * 100:.2f} điểm phần trăm."
        ),
        passed=passed,
        source_page=fact.page,
        source_code=fact.code,
        source_label=fact.label,
    )


def _check_cost_control(claim: Claim, facts: dict[str, Fact]) -> Evidence | None:
    """Khẳng định định tính "kiểm soát tốt chi phí" có đúng không.

    Quy về kỳ vọng định lượng: chi phí được kiểm soát nghĩa là **tỷ lệ chi
    phí trên doanh thu không tăng**. Cách này bắt được mâu thuẫn mà đọc
    bằng mắt rất khó thấy — chi phí tăng nhưng doanh thu tăng nhanh hơn thì
    vẫn là kiểm soát tốt, còn ngược lại thì không.
    """
    if claim.trend is not Trend.CONTROLLED:
        return None
    # Chỉ áp cho khoản mục **chi phí**. Trước đây hàm chia bất kỳ chỉ tiêu
    # nào cho doanh thu, nên "kiểm soát hàng tồn kho" bị kiểm bằng tỷ lệ tồn
    # kho/doanh thu — phép kiểm vô nghĩa, ra 11/13 ca "nhất quán ăn may".
    if claim.metric not in COST_METRICS:
        return None
    cost = facts.get(claim.metric)
    revenue = facts.get("revenue_net")
    if cost is None or revenue is None:
        return None
    if cost.previous is None or revenue.previous is None or revenue.previous == 0:
        return None

    ratio_now = cost.current / revenue.current if revenue.current else None
    ratio_before = cost.previous / revenue.previous
    if ratio_now is None:
        return None

    delta = ratio_now - ratio_before
    passed = delta <= COST_CONTROL_TOLERANCE
    return Evidence(
        dimension="qualitative",
        explanation=(
            f"Câu khẳng định chi phí được kiểm soát. Tỷ lệ chi phí trên doanh "
            f"thu: {ratio_before:.1%} → {ratio_now:.1%} "
            f"({delta * 100:+.1f} điểm phần trăm, mã {cost.code}, "
            f"trang {cost.page})."
        ),
        passed=passed,
        source_page=cost.page,
        source_code=cost.code,
        source_label=cost.label,
    )


def check_claim(claim: Claim, facts: dict[str, Fact]) -> NNCResult:
    """Đối chiếu một khẳng định với số liệu đã bóc từ báo cáo tài chính."""
    fact = facts.get(claim.metric)

    if fact is None:
        return NNCResult(
            claim=claim,
            verdict=Verdict.UNVERIFIABLE,
            evidence=[
                Evidence(
                    dimension="lookup",
                    explanation=(
                        f"Không tìm thấy chỉ tiêu '{claim.metric}' trong báo cáo "
                        f"tài chính tương ứng nên chưa đối chiếu được."
                    ),
                    passed=False,
                )
            ],
        )

    # Chuỗi đứt gãy thì mọi phép so theo kỳ trước đều không đáng tin; chỉ
    # giữ lại phép đối chiếu giá trị tuyệt đối, vốn không phụ thuộc kỳ trước.
    discontinuity = _check_continuity(fact)

    numeric = _check_numeric(claim, fact)
    if claim.metric == "revenue_net" and numeric is not None and not numeric.passed:
        for alt_key, note in (
            (REVENUE_GROSS, "tổng doanh thu bán hàng (Mã 01)"),
            (REVENUE_TOTAL, "tổng doanh thu gồm doanh thu tài chính và thu nhập khác (Mã 10 + 21 + 31)"),
        ):
            alt = facts.get(alt_key)
            alt_ev = _check_numeric(claim, alt) if alt is not None else None
            if alt_ev is not None and alt_ev.passed:
                numeric = Evidence(
                    dimension="numeric",
                    explanation=f"{alt_ev.explanation} Câu dùng định nghĩa {note}.",
                    passed=True,
                    source_page=alt_ev.source_page,
                    source_code=alt_ev.source_code,
                    source_label=alt_ev.source_label,
                )
                break

    checks = [
        numeric,
        _check_ratio_level(claim, fact),
        None if discontinuity else _check_ratio_change(claim, fact),
        None if discontinuity else _check_percent(claim, fact),
        None if discontinuity else _check_direction(claim, fact),
        None if discontinuity else _check_cost_control(claim, facts),
    ]
    evidence = [e for e in checks if e is not None]

    if discontinuity and not evidence:
        return NNCResult(
            claim=claim, verdict=Verdict.UNVERIFIABLE, evidence=[discontinuity]
        )
    if discontinuity:
        evidence.append(discontinuity)

    if not evidence:
        return NNCResult(
            claim=claim,
            verdict=Verdict.UNVERIFIABLE,
            evidence=[
                Evidence(
                    dimension="lookup",
                    explanation=(
                        "Câu không nêu con số hay hướng biến động kiểm chứng "
                        "được từ báo cáo tài chính."
                    ),
                    passed=False,
                    source_page=fact.page,
                    source_code=fact.code,
                )
            ],
        )

    # Phát hiện lệch phạm vi thì dừng lại, không kết luận mâu thuẫn: các
    # chiều còn lại đều so với số hợp nhất nên cũng không đáng tin.
    if any(e.dimension == "scope" for e in evidence):
        return NNCResult(
            claim=claim,
            verdict=Verdict.UNVERIFIABLE,
            evidence=[e for e in evidence if e.dimension == "scope"],
        )

    # Chỉ các chiều có trọng số mới quyết định kết luận. Những chiều còn
    # lại ("continuity", "scope", "lookup") mang tính thông báo, có mặt để
    # giải thích vì sao hệ thống thận trọng, không phải để buộc tội.
    decisive = [e for e in evidence if e.dimension in WEIGHTS]
    if not decisive:
        return NNCResult(claim=claim, verdict=Verdict.UNVERIFIABLE, evidence=evidence)

    verdict = (
        Verdict.CONSISTENT if all(e.passed for e in decisive) else Verdict.INCONSISTENT
    )
    return NNCResult(claim=claim, verdict=verdict, evidence=evidence)


def check_report(
    claims: list[Claim],
    tables: list[FinancialTable],
) -> list[NNCResult]:
    """Đối chiếu toàn bộ khẳng định của một báo cáo, sắp mâu thuẫn lên đầu."""
    facts = build_facts(tables)
    results = [check_claim(c, facts) for c in claims]
    order = {Verdict.INCONSISTENT: 0, Verdict.CONSISTENT: 1, Verdict.UNVERIFIABLE: 2}
    results.sort(key=lambda r: (order[r.verdict], r.score if r.score is not None else 1))
    return results


__all__ = [
    "COST_CONTROL_TOLERANCE",
    "Derived",
    "Evidence",
    "Fact",
    "NNCResult",
    "Statement",
    "Unit",
    "Verdict",
    "build_facts",
    "check_claim",
    "check_report",
]
