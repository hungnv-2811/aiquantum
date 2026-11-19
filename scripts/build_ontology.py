"""Rút ontology VAS từ chính dữ liệu, thay vì soạn tay theo trí nhớ.

Quét toàn bộ báo cáo đã tải, thống kê xem mỗi Mã số Thông tư 200 thực tế
xuất hiện dưới những tên khoản mục nào, rồi ghi ra ``vas_mapping.yaml``.

Cách này chính xác hơn soạn tay vì tên khoản mục thay đổi qua các năm và
giữa các doanh nghiệp; danh sách alias thu được phản ánh đúng những gì
parser sẽ gặp khi chạy thật.

Chạy:
    python scripts/build_ontology.py
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.ingest import iter_reports  # noqa: E402
from smartaudit.tables import Statement, extract_tables  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "smartaudit" / "ontology" / "vas_mapping.yaml"

#: Khoản mục cốt lõi mà cơ chế NNC cần đối chiếu.
#:
#: Khoá là ``(loại báo cáo, mã số)`` chứ không phải mã số đơn thuần, vì
#: **mã số chỉ duy nhất trong phạm vi từng báo cáo**. Mã ``10`` là *Doanh
#: thu thuần* ở Báo cáo kết quả kinh doanh, nhưng là *Biến động hàng tồn
#: kho* ở Lưu chuyển tiền tệ. Bỏ qua ngữ cảnh sẽ ghép nhầm số liệu.
#:
#: Mã số theo Thông tư 200/2014/TT-BTC.
CORE: dict[tuple[Statement, str], str] = {
    # ── Báo cáo kết quả hoạt động kinh doanh ──
    (Statement.INCOME, "01"): "revenue_gross",
    (Statement.INCOME, "02"): "revenue_deductions",
    (Statement.INCOME, "10"): "revenue_net",
    (Statement.INCOME, "11"): "cost_of_goods_sold",
    (Statement.INCOME, "20"): "gross_profit",
    (Statement.INCOME, "21"): "financial_income",
    (Statement.INCOME, "22"): "financial_expense",
    (Statement.INCOME, "23"): "interest_expense",
    (Statement.INCOME, "25"): "selling_expense",
    (Statement.INCOME, "26"): "admin_expense",
    (Statement.INCOME, "30"): "operating_profit",
    (Statement.INCOME, "50"): "profit_before_tax",
    (Statement.INCOME, "51"): "current_tax_expense",
    (Statement.INCOME, "60"): "profit_after_tax",
    (Statement.INCOME, "70"): "eps",
    # ── Bảng cân đối kế toán / Báo cáo tình hình tài chính ──
    (Statement.BALANCE, "100"): "current_assets",
    (Statement.BALANCE, "110"): "cash_and_equivalents",
    (Statement.BALANCE, "130"): "receivables_short_term",
    (Statement.BALANCE, "140"): "inventories",
    (Statement.BALANCE, "200"): "non_current_assets",
    (Statement.BALANCE, "270"): "total_assets",
    (Statement.BALANCE, "300"): "total_liabilities",
    (Statement.BALANCE, "310"): "current_liabilities",
    (Statement.BALANCE, "330"): "non_current_liabilities",
    (Statement.BALANCE, "400"): "owners_equity",
    (Statement.BALANCE, "440"): "total_resources",
    # ── Báo cáo lưu chuyển tiền tệ ──
    (Statement.CASH_FLOW, "20"): "cash_flow_operating",
    (Statement.CASH_FLOW, "30"): "cash_flow_investing",
    (Statement.CASH_FLOW, "40"): "cash_flow_financing",
    (Statement.CASH_FLOW, "50"): "cash_flow_net",
    (Statement.CASH_FLOW, "70"): "cash_end_of_period",
}

# Tên khoản mục hay dính phần công thức phía sau, ví dụ
# "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (20 = 10 - 11)".
_FORMULA = re.compile(r"\s*\([\d\s=+\-–]+\)\s*$")
_WS = re.compile(r"\s+")


def normalise(label: str) -> str:
    """Chuẩn hoá tên khoản mục để gộp các biến thể chỉ khác khoảng trắng."""
    return _WS.sub(" ", _FORMULA.sub("", label)).strip()


def main() -> int:
    reports = list(iter_reports())
    print(f"Quét {len(reports)} báo cáo...\n")

    Key = tuple[Statement, str]
    labels: dict[Key, collections.Counter[str]] = {
        key: collections.Counter() for key in CORE
    }
    seen_in_report: dict[Key, int] = {key: 0 for key in CORE}
    parsed_ok = 0

    for rep in reports:
        try:
            tables = extract_tables(rep.read())
        except Exception as exc:
            print(f"  Lỗi đọc {rep.ticker} {rep.year}: {exc}")
            continue
        if not tables:
            continue
        parsed_ok += 1

        found: set[Key] = set()
        for table in tables:
            for row in table.rows:
                key = (table.statement, row.code)
                if key in labels:
                    labels[key][normalise(row.label)] += 1
                    found.add(key)
        for key in found:
            seen_in_report[key] += 1

    print(f"Bóc được bảng từ {parsed_ok}/{len(reports)} báo cáo "
          f"({parsed_ok / len(reports):.0%})\n")

    print(f"{'Báo cáo':<18} {'Mã':<5} {'Khoá ngữ nghĩa':<24} "
          f"{'Độ phủ':>8} {'Biến thể':>9}")
    print("-" * 70)
    lines = [
        "# Ontology khoản mục theo Thông tư 200/2014/TT-BTC",
        "#",
        "# SINH TỰ ĐỘNG bởi scripts/build_ontology.py — đừng sửa tay.",
        "# Danh sách alias rút từ chính corpus báo cáo tài chính đã tải,",
        "# nên phản ánh đúng các biến thể tên mà parser sẽ gặp khi chạy thật.",
        "#",
        f"# Nguồn: {parsed_ok} báo cáo của 16 mã chứng khoán, 2015-2025.",
        "",
    ]

    for (statement, code), name in CORE.items():
        counter = labels[(statement, code)]
        coverage = seen_in_report[(statement, code)] / parsed_ok if parsed_ok else 0
        print(f"{statement.value:<18} {code:<5} {name:<24} "
              f"{coverage:>7.0%} {len(counter):>9}")

        lines.append(f"{name}:")
        lines.append(f"  statement: {statement.value}")
        lines.append(f"  code: '{code}'")
        lines.append(f"  coverage: {coverage:.3f}   # tỷ lệ báo cáo tìm thấy mã này")
        lines.append("  aliases:")
        for label, count in counter.most_common(8):
            safe = label.replace("'", "''")
            lines.append(f"    - '{safe}'   # {count} lần")
        lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nĐã ghi {OUT.relative_to(OUT.parent.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
