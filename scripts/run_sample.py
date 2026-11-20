"""Chạy lõi đầu-cuối trên 2 BCTC thật + 4 trích đoạn BCTN, không ghi đè benchmark."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_environment import check


def run():
    from smartaudit.ingest import iter_reports
    from smartaudit.nlp import extract_claims
    from smartaudit.nnc import check_report
    from smartaudit.tables import extract_tables

    excerpts = json.loads((ROOT / "sample_data/narratives.json").read_text(encoding="utf-8"))
    results = []
    for report in iter_reports(ROOT / "sample_data/tinix"):
        tables = extract_tables(report.read())
        selected = [r for r in excerpts if (r["ticker"], r["year"]) == (report.ticker, report.year)]
        text = "\n".join(f"===== PAGE {r['page']} =====\n{r['text']}\n" for r in selected)
        claims = extract_claims(text, default_year=report.year)
        checked = check_report(claims, tables)
        results.append({"ticker": report.ticker, "year": report.year, "source": report.name,
                        "tables": len(tables), "excerpts": len(selected),
                        "claims": [{"text": r.claim.text, "metric": r.claim.metric,
                                    "verdict": r.verdict.value, "score": r.score,
                                    "evidence": [e.__dict__ for e in r.evidence]} for r in checked]})
    return {"note": "Mau 2 BCTC va 4 trich doan BCTN; khong phai danh gia lai 98 bao cao.",
            "reports": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Tuy chon: ghi JSON rieng; mac dinh chi in.")
    args = parser.parse_args()
    errors = check(mode="sample")
    if errors:
        print("\n".join(errors))
        return 1
    result = run()
    print(result["note"])
    for r in result["reports"]:
        print(f"{r['ticker']} {r['year']}: {r['tables']} tables, {r['excerpts']} excerpts, {len(r['claims'])} claims")
        for c in r["claims"]:
            print(f"  {c['metric']}: {c['verdict']}")
    if args.output:
        protected = {ROOT / "results" / name for name in
                     ("nnc_results.json", "eval_summary.json", "injected_eval.json", "qka_results.json",
                      "nnc_results_baseline_20260921.json")}
        if args.output.resolve() in protected:
            parser.error("Khong ghi de ket qua benchmark. Hay chon tep mau rieng.")
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
