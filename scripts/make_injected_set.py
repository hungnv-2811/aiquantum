"""Đo khả năng phát hiện (recall) bằng **tập chèn lỗi có kiểm soát**.

Vì sao cần: doanh nghiệp niêm yết lớn hiếm khi trình bày sai số liệu đã
kiểm toán ngay trong báo cáo thường niên, nên dữ liệu thật gần như không có
mâu thuẫn thật để đo recall (xem docs/ke-hoach-vong-2.md, mục 6.1b). Cách
chuẩn khi lỗi thật hiếm là **chèn lỗi có chủ đích** vào câu đúng rồi xem hệ
thống có bắt được không.

Quy trình:

1. Lấy các câu thật mà hệ thống đang đánh giá **nhất quán** (từ
   ``results/nnc_results.json``).
2. Sinh biến thể sai lệch có kiểm soát:

   * ``gia_tri``  — nhân con số tuyệt đối với (1 + p), p ∈ {±2%, 5%, 10%, 20%}
   * ``phan_tram`` — cộng thêm δ điểm vào tỷ lệ tăng trưởng, δ ∈ {2, 5, 10}
   * ``huong``    — đảo "tăng" ↔ "giảm"
   * ``kiem_soat_chi_phi`` — câu định tính tổng hợp "Chi phí bán hàng/quản lý
     được kiểm soát tốt" cho mọi (mã, năm); đáp án tính từ tỷ lệ chi phí trên
     doanh thu trong BCTC (tăng quá 2 điểm thì là mâu thuẫn)

   Kèm **nhóm đối chứng** không được phép báo động: câu gốc giữ nguyên, và
   biến thể lệch 0,5% (nằm trong dung sai làm tròn).
3. Chạy lại đúng pipeline (trích khẳng định → đối chiếu) trên từng câu với
   số liệu BCTC thật của doanh nghiệp đó.

**Đây là dữ liệu tổng hợp.** Mọi số đo từ script này phải được trình bày
tách riêng, không trộn với số đo trên dữ liệu thật.

Chạy:
    python scripts/make_injected_set.py
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import RESULTS, TICKERS  # noqa: E402
from smartaudit.eval import load_financials  # noqa: E402
from smartaudit.nlp import extract_claims  # noqa: E402
from smartaudit.nlp.claims import _AMOUNT  # noqa: E402
from smartaudit.nnc import Verdict, check_claim  # noqa: E402

SEED = 2026
VALUE_SHIFTS = [0.02, -0.02, 0.05, 0.10, -0.10, 0.20]
PERCENT_SHIFTS = [2.0, 5.0, 10.0]
CONTROL_SHIFT = 0.005
_PERCENT_IN_TEXT = re.compile(r"(\d[\d.]*(?:,\d+)?)(\s*%)")
_DIRECTION = re.compile(r"\b(tăng trưởng|tăng|sụt giảm|giảm)\b", re.IGNORECASE)
_FLIP = {"tăng trưởng": "sụt giảm", "tăng": "giảm", "sụt giảm": "tăng trưởng", "giảm": "tăng"}


def fmt_vn(number: float, decimals: int) -> str:
    """Định dạng số kiểu Việt Nam: chấm ngăn nghìn, phẩy thập phân."""
    text = f"{number:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def _decimals(number_text: str) -> int:
    return len(number_text.partition(",")[2])


def _parse(number_text: str) -> float:
    return float(number_text.replace(".", "").replace(",", "."))


def judge(sentence: str, page: int, year: int, metric: str, facts) -> str:
    """Chạy pipeline trên một câu, trả về phán quyết cho đúng chỉ tiêu."""
    claims = extract_claims(f"===== PAGE {page} =====\n{sentence}\n", default_year=year)
    claim = next((c for c in claims if c.metric == metric), None)
    if claim is None:
        return "không trích được"
    return check_claim(claim, facts).verdict.value


def _used_claim(sentence: str, page: int, year: int, metric: str):
    """Khẳng định mà pipeline trích từ câu gốc cho đúng chỉ tiêu."""
    claims = extract_claims(f"===== PAGE {page} =====\n{sentence}\n", default_year=year)
    return next((c for c in claims if c.metric == metric), None)


def mutate_value(sentence: str, shift: float, used_value: float | None) -> str | None:
    """Sửa **đúng con số mà hệ thống dùng** (không phải số đầu tiên trong câu:
    với "từ X lên Y" hệ thống dùng Y)."""
    if used_value is None:
        return None
    best = None
    for m in _AMOUNT.finditer(sentence):
        number = _parse(m.group(1))
        unit = m.group(2).lower()
        factor = 1e12 if ("nghìn" in unit or "ngàn" in unit) else 1e9 if ("tỷ" in unit or "tỉ" in unit) else 1e6
        gap = abs(number * factor - used_value) / abs(used_value)
        if best is None or gap < best[0]:
            best = (gap, m, number)
    if best is None or best[0] > 1e-6:
        return None
    _, m, number = best
    new = fmt_vn(number * (1 + shift), max(_decimals(m.group(1)), 1 if number < 100 else 0))
    return sentence[:m.start(1)] + new + sentence[m.end(1):]


def mutate_percent(sentence: str, delta: float, used_percent: float | None) -> str | None:
    if used_percent is None:
        return None
    for m in _PERCENT_IN_TEXT.finditer(sentence):
        if abs(_parse(m.group(1)) - used_percent) < 1e-9:
            value = used_percent + delta
            return sentence[:m.start(1)] + fmt_vn(value, max(_decimals(m.group(1)), 1)) + sentence[m.end(1):]
    return None


def mutate_direction(sentence: str) -> str | None:
    m = _DIRECTION.search(sentence)
    if not m:
        return None
    word = m.group(1)
    flipped = _FLIP[word.lower()]
    if word[0].isupper():
        flipped = flipped[0].upper() + flipped[1:]
    return sentence[:m.start(1)] + flipped + sentence[m.end(1):]


def main() -> int:
    rng = random.Random(SEED)
    payload = json.loads((RESULTS / "nnc_results.json").read_text(encoding="utf-8"))
    keys = {(r["ticker"], r["year"]) for r in payload}
    _, facts_by_key, _ = load_financials(sorted({t for t, _ in keys}) or TICKERS, keys)

    cases: list[dict] = []

    def add(kind, level, ticker, year, page, metric, original, mutated, expected):
        if mutated is None or mutated == original:
            return
        got = judge(mutated, page, year, metric, facts_by_key[(ticker, year)])
        cases.append({
            "loai": kind, "muc": level, "ma_ck": ticker, "nam": year, "trang": page,
            "chi_tieu": metric, "cau_goc": original, "cau_chen_loi": mutated,
            "ky_vong": expected, "he_thong": got,
        })

    for rep in payload:
        key = (rep["ticker"], rep["year"])
        if key not in facts_by_key:
            continue
        for c in rep["claims"]:
            if c["verdict"] != Verdict.CONSISTENT.value:
                continue
            s, p, m = c["text"], c["page"], c["metric"]
            used = _used_claim(s, p, key[1], m)
            if used is None:
                continue
            # Đối chứng: câu gốc phải vẫn nhất quán.
            add("doi_chung", "goc", *key, p, m, s, s + " ", Verdict.CONSISTENT.value)
            if used.value is not None:
                add("doi_chung", "lech_0.5%", *key, p, m, s,
                    mutate_value(s, CONTROL_SHIFT, used.value), Verdict.CONSISTENT.value)
                for shift in VALUE_SHIFTS:
                    add("gia_tri", f"{shift:+.0%}", *key, p, m, s,
                        mutate_value(s, shift, used.value), Verdict.INCONSISTENT.value)
            if used.percent is not None and used.basis != "kế hoạch":
                for delta in PERCENT_SHIFTS:
                    add("phan_tram", f"+{delta:.0f} điểm", *key, p, m, s,
                        mutate_percent(s, delta, used.percent), Verdict.INCONSISTENT.value)
            if _DIRECTION.search(s):
                add("huong", "đảo chiều", *key, p, m, s, mutate_direction(s),
                    Verdict.INCONSISTENT.value)

    # Câu định tính tổng hợp về kiểm soát chi phí, đáp án tính từ BCTC thật.
    for (ticker, year), facts in sorted(facts_by_key.items()):
        revenue = facts.get("revenue_net")
        for metric, phrase in (("selling_expense", "Chi phí bán hàng"),
                               ("admin_expense", "Chi phí quản lý doanh nghiệp")):
            cost = facts.get(metric)
            if not (cost and revenue and cost.previous and revenue.previous and revenue.current):
                continue
            delta = cost.current / revenue.current - cost.previous / revenue.previous
            if abs(delta) < 0.005:  # bỏ vùng sát ngưỡng, đáp án không rõ ràng
                continue
            expected = Verdict.INCONSISTENT.value if delta > 0.02 else Verdict.CONSISTENT.value
            sentence = f"Năm {year}, {phrase.lower()} được kiểm soát tốt."
            got = judge(sentence, 1, year, metric, facts)
            cases.append({
                "loai": "kiem_soat_chi_phi", "muc": f"{delta * 100:+.1f} điểm",
                "ma_ck": ticker, "nam": year, "trang": 1, "chi_tieu": metric,
                "cau_goc": "(câu tổng hợp)", "cau_chen_loi": sentence,
                "ky_vong": expected, "he_thong": got,
            })

    # ── Tổng hợp ──
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for case in cases:
        groups[(case["loai"], case["muc"])].append(case)
    summary = []
    for (kind, level), items in sorted(groups.items()):
        hit = sum(1 for x in items if x["he_thong"] == x["ky_vong"])
        summary.append({"loai": kind, "muc": level, "n": len(items), "dung": hit,
                        "ty_le": round(hit / len(items), 4)})

    def rate(pred):
        items = [x for x in cases if pred(x)]
        hit = sum(1 for x in items if x["he_thong"] == x["ky_vong"])
        return {"n": len(items), "dung": hit, "ty_le": round(hit / len(items), 4) if items else None}

    out = {
        "ghi_chu": "DỮ LIỆU TỔNG HỢP — câu thật bị sửa có chủ đích. Không trộn với số đo trên dữ liệu thật.",
        "seed": SEED,
        "recall_chen_loi": rate(lambda x: x["ky_vong"] == Verdict.INCONSISTENT.value),
        "recall_theo_loai": {k: rate(lambda x, k=k: x["loai"] == k and x["ky_vong"] == Verdict.INCONSISTENT.value)
                             for k in ("gia_tri", "phan_tram", "huong", "kiem_soat_chi_phi")},
        "bao_dong_gia_doi_chung": rate(lambda x: x["loai"] == "doi_chung"),
        "kiem_soat_chi_phi_dung_chieu_nhat_quan": rate(
            lambda x: x["loai"] == "kiem_soat_chi_phi" and x["ky_vong"] == Verdict.CONSISTENT.value),
        "chi_tiet": summary,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "injected_eval.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(RESULTS / "injected_cases.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)

    print(f"{len(cases)} ca chèn lỗi / đối chứng")
    print("Recall trên câu chèn lỗi:", out["recall_chen_loi"])
    for k, v in out["recall_theo_loai"].items():
        print(f"  {k:<20} {v}")
    print("Đối chứng (không được báo động):", out["bao_dong_gia_doi_chung"])
    for row in summary:
        print(f"  {row['loai']:<18} {row['muc']:<12} n={row['n']:<4} đúng={row['dung']:<4} {row['ty_le']:.0%}")
    rng.random()  # giữ seed cho các bước ngẫu nhiên về sau
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
