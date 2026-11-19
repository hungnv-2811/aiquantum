"""Nạp bảng số liệu BCTC theo (mã, năm) — dùng chung cho đo lường và xuất dashboard.

Cách chọn báo cáo **giống hệt** ``scripts/run_nnc.py``: bản đầu tiên theo
thứ tự duyệt, không phải riêng công ty mẹ, bóc được bảng. Giữ một quy tắc
duy nhất để số liệu trên dashboard, trong phép đo và trong pipeline là một.
"""

from __future__ import annotations

from smartaudit.ingest import iter_reports
from smartaudit.nnc.checker import Fact, build_facts
from smartaudit.tables import FinancialTable, extract_tables


def load_financials(
    tickers: list[str],
    keys: set[tuple[str, int]] | None = None,
) -> tuple[dict[tuple[str, int], list[FinancialTable]], dict[tuple[str, int], dict[str, Fact]], dict[tuple[str, int], str]]:
    """Trả về ``(bảng, facts, tên tệp nguồn)`` theo (mã, năm)."""
    tables: dict[tuple[str, int], list[FinancialTable]] = {}
    names: dict[tuple[str, int], str] = {}
    for rep in iter_reports(tickers=tickers):
        key = (rep.ticker, rep.year)
        if keys is not None and key not in keys:
            continue
        if rep.consolidated is False or tables.get(key):
            continue
        if found := extract_tables(rep.read()):
            tables[key] = found
            names[key] = rep.name
    facts = {k: build_facts(v) for k, v in tables.items()}
    return tables, facts, names
