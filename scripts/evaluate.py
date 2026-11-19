"""Đo chất lượng trên dữ liệu thật bằng 300 cặp đã gán nhãn mù.

Đầu vào (``annotation/``):

* ``sample_key.csv``      — mẫu: phán quyết bản 21/09, tầng, trọng số, dev/test
* ``labels_A_ai.csv``, ``labels_B_ai.csv`` — hai người gán độc lập
* ``labels_adjudicated.csv`` (nếu có) — phân xử các dòng hai người khác nhau

Đầu ra:

* ``annotation/gold_300.csv``   — nhãn cuối cùng
* ``annotation/bat_dong.csv``   — các dòng hai người gán khác nhau (để phân xử)
* ``results/eval_summary.json`` — số đo cho báo cáo và dashboard

Số đo chính:

* **Precision của nhóm "mâu thuẫn"** trước (bản 21/09) và sau khi vá nền, kèm
  khoảng tin cậy Wilson 95%.
* **Số cờ oan ước tính** trên toàn bộ khẳng định (có trọng số lấy mẫu).
* **Cohen's kappa** giữa hai người gán.

Nhãn ``MT`` (mâu thuẫn thật) là câu: là khẳng định kiểm chứng được, đúng chỉ
tiêu, và trái với BCTC. Câu ``la_khang_dinh = K`` luôn tính là không phải MT.

Chạy:
    python scripts/evaluate.py
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import RESULTS, ROOT  # noqa: E402

ANN = ROOT / "annotation"
MT, NQ, KKC = "MT", "NQ", "KKC"
SYS_MT = "mâu thuẫn"
REMOVED = "(không còn trích)"


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def norm_label(row: dict) -> str:
    """Nhãn phán quyết đã chuẩn hoá: câu không phải khẳng định thì là KKC."""
    if (row.get("la_khang_dinh") or "").strip().upper() == "K":
        return KKC
    return (row.get("nhan") or "").strip().upper() or KKC


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def summarise(rows: list[dict], verdict_key: str) -> dict:
    """Precision nhóm mâu thuẫn và số cờ oan ước tính cho một phiên bản hệ thống."""
    flagged = [r for r in rows if r[verdict_key] == SYS_MT]
    tp = sum(1 for r in flagged if r["gold"] == MT)
    fp_weighted = sum(float(r["trong_so"]) for r in flagged if r["gold"] != MT)
    n = len(flagged)
    return {
        "flags_in_sample": n,
        "true_mt": tp,
        "precision": round(tp / n, 4) if n else None,
        "ci": [round(x, 4) for x in wilson(tp, n)] if n else None,
        "false_flags_est": round(fp_weighted),
    }


def main() -> int:
    key = {r["id"]: r for r in read_csv(ANN / "sample_key.csv")}
    a = {r["id"]: r for r in read_csv(ANN / "labels_A_ai.csv")}
    b = {r["id"]: r for r in read_csv(ANN / "labels_B_ai.csv")}
    adj_path = ANN / "labels_adjudicated.csv"
    adj = {r["id"]: r for r in read_csv(adj_path)} if adj_path.exists() else {}

    ids = sorted(key)
    missing = [i for i in ids if i not in a or i not in b]
    if missing:
        print(f"Thiếu nhãn cho {len(missing)} dòng, ví dụ {missing[:5]}")

    la = [norm_label(a[i]) for i in ids if i in a and i in b]
    lb = [norm_label(b[i]) for i in ids if i in a and i in b]
    ca = [(a[i].get("la_khang_dinh") or "").strip().upper() for i in ids if i in a and i in b]
    cb = [(b[i].get("la_khang_dinh") or "").strip().upper() for i in ids if i in a and i in b]

    # ── Nhãn cuối cùng ──
    gold_rows, disagreements = [], []
    for i in ids:
        if i not in a or i not in b:
            continue
        na, nb = norm_label(a[i]), norm_label(b[i])
        if na == nb:
            gold, source = na, "đồng thuận"
        elif i in adj:
            gold, source = norm_label(adj[i]), "phân xử"
        else:
            gold, source = None, "chưa phân xử"
            disagreements.append({
                "id": i, "ma_ck": key[i]["ma_ck"], "nam": key[i]["nam"], "trang_bctn": key[i]["trang_bctn"],
                "cau_goc": key[i]["cau_goc"], "nhan_A": na, "ghi_chu_A": a[i].get("ghi_chu", ""),
                "nhan_B": nb, "ghi_chu_B": b[i].get("ghi_chu", ""),
            })
        gold_rows.append({"id": i, "gold": gold or "", "nguon": source, "nhan_A": na, "nhan_B": nb,
                          "ly_do_phan_xu": adj.get(i, {}).get("ghi_chu", "")})
    write_csv(ANN / "gold_300.csv", gold_rows)
    write_csv(ANN / "bat_dong.csv", disagreements)

    # ── Nối với kết quả sau vá ──
    now = json.loads((RESULTS / "nnc_results.json").read_text(encoding="utf-8"))
    now_index = {}
    for rep in now:
        for c in rep["claims"]:
            now_index[(rep["ticker"], rep["year"], c["page"], c["text"], c["metric"])] = c["verdict"]
    total_flags_now = sum(1 for rep in now for c in rep["claims"] if c["verdict"] == SYS_MT)

    rows = []
    gold_by_id = {g["id"]: g["gold"] for g in gold_rows}
    for i in ids:
        k = key[i]
        g = gold_by_id.get(i)
        if not g:
            continue
        rows.append({
            **k, "gold": g,
            "verdict_before": k["verdict_he_thong"],
            "verdict_after": now_index.get((k["ma_ck"], int(k["nam"]), int(k["trang_bctn"]), k["cau_goc"], k["metric"]), REMOVED),
        })

    before, after = summarise(rows, "verdict_before"), summarise(rows, "verdict_after")
    test = [r for r in rows if r["tap"] == "test"]
    after_flags_in_sample = after["flags_in_sample"]

    gold_mt = [r for r in rows if r["gold"] == MT]
    removed = [r for r in rows if r["verdict_after"] == REMOVED]
    out = {
        "n_labeled": len(rows),
        "n_disagreements_open": len(disagreements),
        "labelers": "Hai tác tử AI gán mù, độc lập theo hướng dẫn của đội; bất đồng được phân xử (nhãn bạc).",
        "kappa_nhan": round(cohen_kappa(la, lb), 4) if la else None,
        "kappa_la_khang_dinh": round(cohen_kappa(ca, cb), 4) if ca else None,
        "dong_thuan_nhan": round(sum(x == y for x, y in zip(la, lb)) / len(la), 4) if la else None,
        "gold_distribution": dict(Counter(r["gold"] for r in rows)),
        "before": before,
        "after": {**after, "flags_total": total_flags_now,
                  "flags_outside_sample": total_flags_now - after_flags_in_sample},
        "test_only": {"before": summarise(test, "verdict_before"), "after": summarise(test, "verdict_after"),
                      "n": len(test)},
        "gold_mt": {
            "n": len(gold_mt),
            "flagged_before": sum(1 for r in gold_mt if r["verdict_before"] == SYS_MT),
            "flagged_after": sum(1 for r in gold_mt if r["verdict_after"] == SYS_MT),
        },
        "removed_after": {
            "n": len(removed),
            "gold_not_claim_or_kkc": sum(1 for r in removed if r["gold"] == KKC),
            "gold_nq": sum(1 for r in removed if r["gold"] == NQ),
            "gold_mt": sum(1 for r in removed if r["gold"] == MT),
        },
        "ghi_chu": (
            "Mẫu lấy từ bản 21/09: toàn bộ 141 cờ 'mâu thuẫn' + 159 câu ngẫu nhiên (bỏ ngân hàng). "
            "Bản vá nền được thiết kế từ phân tích lỗi của chính 141 cờ đó, nên số 'sau vá' có thiên lệch lạc quan. "
            f"{total_flags_now - after_flags_in_sample} cờ sau vá nằm ngoài mẫu (chưa gán nhãn)."
        ),
    }
    (RESULTS / "eval_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Đã gán nhãn: {len(rows)} dòng · bất đồng chưa phân xử: {len(disagreements)}")
    print(f"Kappa (nhãn phán quyết): {out['kappa_nhan']} · đồng thuận thô {out['dong_thuan_nhan']}")
    print(f"Phân bố nhãn cuối: {out['gold_distribution']}")
    print(f"Trước vá: {before}")
    print(f"Sau vá:   {out['after']}")
    print(f"Chỉ tập test: {out['test_only']}")
    print(f"Mâu thuẫn thật trong mẫu: {out['gold_mt']}")
    print(f"Câu bị loại sau vá: {out['removed_after']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
