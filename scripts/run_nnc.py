"""Chạy toàn bộ pipeline NNC trên dữ liệu thật.

Ghép hai nguồn độc lập: khẳng định lấy từ Báo cáo thường niên (Vietstock),
số liệu lấy từ Báo cáo tài chính kiểm toán (TiniX trên HuggingFace).

Chạy:
    python scripts/run_nnc.py                # tất cả mã, tất cả năm có đủ đôi
    python scripts/run_nnc.py VNM            # một mã
    python scripts/run_nnc.py VNM 2024       # một mã, một năm
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import RESULTS, TICKERS  # noqa: E402
from smartaudit.ingest import iter_reports  # noqa: E402
from smartaudit.ingest.vietstock import BCTN_DIR, TEXT_CACHE, AnnualReport  # noqa: E402
from smartaudit.nlp import extract_claims  # noqa: E402
from smartaudit.nnc import Verdict, check_report  # noqa: E402
from smartaudit.tables import extract_tables  # noqa: E402

MAX_PAGES = 60


def _annual_reports(tickers: list[str], year: int | None) -> list[AnnualReport]:
    """Danh sách báo cáo thường niên: có PDF gốc **hoặc** đã có bản văn bản bóc sẵn.

    Gói mã nguồn nộp kèm chỉ mang bản văn bản đã bóc (~17 MB) thay cho
    958 MB PDF, nên pipeline phải chạy được khi không có PDF.
    """
    found: dict[tuple[str, int], AnnualReport] = {}
    for pdf in sorted(BCTN_DIR.rglob("*_BCTN_*.pdf")):
        ticker, _, y = pdf.stem.rsplit("_", 2)
        found[(ticker, int(y))] = AnnualReport(ticker, int(y), pdf)
    for txt in sorted(TEXT_CACHE.rglob(f"*_col-{MAX_PAGES}.txt")):
        ticker, y, _ = txt.stem.split("_", 2)
        if y.isdigit():
            found.setdefault((ticker, int(y)), AnnualReport(
                ticker, int(y), BCTN_DIR / ticker / f"{ticker}_BCTN_{y}.pdf"))
    return [
        rep for (ticker, y), rep in sorted(found.items())
        if ticker in tickers and (not year or y == year)
    ]


def main() -> int:
    args = [a for a in sys.argv[1:]]
    year = int(args[-1]) if args and args[-1].isdigit() else None
    tickers = [a for a in args if not a.isdigit()] or TICKERS

    # Bảng tra báo cáo tài chính đã bóc sẵn, theo (mã, năm).
    financials: dict[tuple[str, int], list] = {}
    for rep in iter_reports(tickers=tickers):
        if rep.consolidated is False:      # ưu tiên báo cáo hợp nhất
            continue
        key = (rep.ticker, rep.year)
        if financials.get(key):
            continue
        # Chỉ nhận kết quả bóc được. Ghi cả bảng rỗng vào thì một lần bóc
        # hỏng sẽ che vĩnh viễn báo cáo cùng (mã, năm) vốn dùng được.
        if tables := extract_tables(rep.read()):
            financials[key] = tables

    reports = _annual_reports(tickers, year)
    print(f"Đối chiếu {len(reports)} báo cáo thường niên "
          f"với {len(financials)} báo cáo tài chính\n")

    print(f"{'Mã':<5} {'Năm':<6} {'Claim':>6} {'Nhất quán':>10} "
          f"{'Mâu thuẫn':>10} {'Chưa KC':>9}  {'NNC TB':>7}")
    print("-" * 62)

    payload = []
    totals = {v: 0 for v in Verdict}
    unusable: list[tuple[str, int, str]] = []

    for annual in reports:
        tables = financials.get((annual.ticker, annual.year))
        if not tables:
            continue

        try:
            text = annual.extract_text(columns=True, max_pages=MAX_PAGES)
        except Exception as exc:
            print(f"{annual.ticker:<5} {annual.year:<6}  lỗi đọc PDF: {exc}")
            unusable.append((annual.ticker, annual.year, str(exc)))
            continue

        # Không phải file nào tải về cũng là báo cáo thường niên thật —
        # Vietstock đôi khi trả công văn công bố thông tin hoặc bản scan.
        if problem := annual.check_usable(text):
            print(f"{annual.ticker:<5} {annual.year:<6}  bỏ qua: {problem}")
            unusable.append((annual.ticker, annual.year, problem))
            continue

        claims = extract_claims(text, default_year=annual.year)
        results = check_report(claims, tables)

        counts = {v: sum(1 for r in results if r.verdict is v) for v in Verdict}
        for v, n in counts.items():
            totals[v] += n

        scored = [r.score for r in results if r.score is not None]
        avg = f"{sum(scored) / len(scored):.2f}" if scored else "—"

        print(f"{annual.ticker:<5} {annual.year:<6} {len(results):>6} "
              f"{counts[Verdict.CONSISTENT]:>10} {counts[Verdict.INCONSISTENT]:>10} "
              f"{counts[Verdict.UNVERIFIABLE]:>9}  {avg:>7}")

        payload.append({
            "ticker": annual.ticker,
            "year": annual.year,
            "nnc_score": (sum(scored) / len(scored)) if scored else None,
            "claims": [
                {
                    "text": r.claim.text,
                    "page": r.claim.page,
                    "metric": r.claim.metric,
                    "trend": r.claim.trend.value,
                    "verdict": r.verdict.value,
                    "score": r.score,
                    "evidence": [
                        {
                            "dimension": e.dimension,
                            "explanation": e.explanation,
                            "passed": e.passed,
                            "source_page": e.source_page,
                            "source_code": e.source_code,
                        }
                        for e in r.evidence
                    ],
                }
                for r in results
            ],
        })

    total = sum(totals.values())
    print("-" * 62)
    print(f"{'TỔNG':<12} {total:>6} {totals[Verdict.CONSISTENT]:>10} "
          f"{totals[Verdict.INCONSISTENT]:>10} {totals[Verdict.UNVERIFIABLE]:>9}")

    if unusable:
        print(f"\n{len(unusable)} báo cáo không dùng được:")
        for ticker, yr, why in unusable:
            print(f"  {ticker} {yr}: {why}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "nnc_results.json"
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nĐã ghi {out}")

    # In vài mâu thuẫn tiêu biểu kèm minh chứng
    flagged = [
        (p["ticker"], p["year"], c)
        for p in payload for c in p["claims"]
        if c["verdict"] == Verdict.INCONSISTENT.value
    ]
    if flagged:
        print(f"\n{'=' * 62}\n{len(flagged)} MÂU THUẪN — 5 ví dụ đầu\n{'=' * 62}")
        for ticker, yr, c in flagged[:5]:
            print(f"\n[{ticker} {yr}] trang {c['page']} · {c['metric']} "
                  f"· điểm {c['score']:.2f}")
            print(f"  Khẳng định: {c['text'][:150]}")
            for e in c["evidence"]:
                mark = "✓" if e["passed"] else "✗"
                print(f"  {mark} {e['explanation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
