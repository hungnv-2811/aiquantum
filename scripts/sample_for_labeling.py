"""Lấy mẫu 300 cặp khẳng định – minh chứng để gán nhãn tay, phục vụ đo precision.

Thiết kế mẫu (xem docs/ke-hoach-vong-2.md, mục 6.1):

* **Bỏ ngân hàng** (MBB, TCB, VPB). Ngân hàng lập BCTC theo Thông tư 49,
  nằm ngoài phạm vi hệ thống nên không tính vào số đo.
* **Tầng "mâu thuẫn": lấy toàn bộ.** Đây là nhóm dẫn tới cáo buộc doanh
  nghiệp nên precision của nó là chỉ số quan trọng nhất. Lấy ngẫu nhiên
  thuần thì chỉ được khoảng 60 ca, khoảng tin cậy rộng ±12 điểm.
* **Các tầng còn lại: ngẫu nhiên**, phân bổ theo tỷ lệ phán quyết, cho đủ
  300 cặp. Mỗi dòng mang trọng số ``N_tầng / n_tầng`` để sau này ước lượng
  recall cho toàn bộ tập.
* **Chia dev / test theo cặp (mã, năm)**, không theo từng câu: mọi câu của
  cùng một báo cáo nằm chung một phía. Luật chỉ được chỉnh khi nhìn tập dev;
  tập test chỉ chạy đúng một lần sau khi đóng băng pipeline.

Sheet gán nhãn là **mù**: không có phán quyết, điểm, hay lời giải thích của
hệ thống. Người gán chỉ thấy câu gốc, ngữ cảnh quanh câu và số liệu trong
bảng BCTC. Thứ tự dòng được xáo trộn để các ca "mâu thuẫn" không dồn cục.

Đầu ra (thư mục ``annotation/``):

* ``sheet_nguoi_gan_1.csv``, ``sheet_nguoi_gan_2.csv`` — hai bản giống hệt
  nhau cho hai người gán độc lập. Mở bằng Excel (UTF-8 có BOM).
* ``sample_key.csv`` — khoá nối mỗi ``id`` với phán quyết của hệ thống,
  tầng, trọng số và phía dev/test. **Không gửi tệp này cho người gán.**

Chạy:
    python scripts/sample_for_labeling.py            # mặc định 300 cặp, seed 2026
    python scripts/sample_for_labeling.py 300 2026
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smartaudit.config import RESULTS, ROOT  # noqa: E402
from smartaudit.ingest import iter_reports  # noqa: E402
from smartaudit.ingest.vietstock import TEXT_CACHE  # noqa: E402
from smartaudit.nnc.checker import DERIVED, Fact, Unit, build_facts  # noqa: E402
from smartaudit.ontology import load_ontology  # noqa: E402
from smartaudit.tables import extract_tables  # noqa: E402

#: Ngân hàng dùng Thông tư 49 — ngoài phạm vi, không đưa vào mẫu.
BANKS = {"MBB", "TCB", "VPB"}

INCONSISTENT = "mâu thuẫn"

#: Số câu muốn có trong tập dev; phần còn lại là test.
DEV_TARGET = 100

#: Số ký tự ngữ cảnh lấy thêm mỗi bên câu gốc.
CONTEXT_CHARS = 250

OUT_DIR = ROOT / "annotation"

#: Cột người gán phải điền. Giữ đúng tên với docs/gan-nhan/huong-dan-gan-nhan.md.
LABEL_COLUMNS = ["la_khang_dinh", "chi_tieu_dung", "nhan", "ghi_chu"]


# ── Số liệu BCTC ─────────────────────────────────────────────────────────


def load_facts(
    keys: set[tuple[str, int]],
) -> tuple[dict[tuple[str, int], dict[str, Fact]], dict[tuple[str, int], str]]:
    """Bóc bảng BCTC cho các cặp (mã, năm) cần dùng.

    Chọn báo cáo **giống hệt** ``scripts/run_nnc.py`` — bản đầu tiên theo thứ
    tự duyệt, không phải riêng công ty mẹ, bóc được bảng — để số liệu trên
    sheet đúng là số liệu hệ thống đã đối chiếu.

    Trả về thêm tên tệp BCTC của từng cặp để người gán nhãn mở đúng báo cáo.
    """
    tickers = sorted({t for t, _ in keys})
    facts: dict[tuple[str, int], dict[str, Fact]] = {}
    names: dict[tuple[str, int], str] = {}
    for rep in iter_reports(tickers=tickers):
        key = (rep.ticker, rep.year)
        if key not in keys or key in facts or rep.consolidated is False:
            continue
        if tables := extract_tables(rep.read()):
            facts[key] = build_facts(tables)
            names[key] = rep.name
    return facts, names


@lru_cache(maxsize=None)
def concept_label(key: str) -> str:
    """Tên chỉ tiêu dễ đọc cho người gán nhãn."""
    if key in DERIVED:
        return DERIVED[key].label
    onto = load_ontology()
    concept = onto.by_key(key)
    if concept and concept.aliases:
        return concept.aliases[0]
    return key


def fmt_value(fact: Fact, value: float | None) -> str:
    """Định dạng số theo đơn vị, đủ chữ số để người gán tự tính lại.

    Số tiền giữ **nguyên như in trong bảng gốc**, không quy đổi sang tỷ đồng.
    Lý do: khoảng 1/4 BCTC ngoài ngân hàng ghi theo nghìn đồng hoặc triệu
    đồng, mà parser hiện chưa đọc dòng "Đơn vị tính" — quy đổi sẽ ra số sai
    (ví dụ doanh thu Masan thành 0,1 tỷ). Người gán nhãn xem đơn vị ở đầu
    bảng trong BCTC gốc.
    """
    if value is None:
        return ""
    if fact.unit is Unit.PERCENT:
        return f"{value * 100:.2f}%".replace(".", ",")
    if fact.unit is Unit.TIMES:
        return f"{value:.2f} lần".replace(".", ",")
    return f"{value:,.0f}".replace(",", ".")


def fmt_growth(fact: Fact) -> str:
    """Biến động so với năm trước.

    Với tỷ số phần trăm (biên lợi nhuận…), báo cáo thường niên nói theo
    **điểm phần trăm** ("biên gộp giảm 4,5 điểm"), nên in hiệu số thay vì
    tỷ lệ thay đổi tương đối — tránh người gán đọc nhầm "-41%".
    """
    if fact.unit is Unit.PERCENT:
        if fact.previous is None:
            return ""
        diff = (fact.current - fact.previous) * 100
        return f"{diff:+.2f} điểm %".replace(".", ",")
    g = fact.growth
    if g is None:
        return ""
    return f"{g * 100:+.2f}%".replace(".", ",")


# ── Ngữ cảnh trong báo cáo thường niên ───────────────────────────────────

_PAGE_MARK = re.compile(r"===== PAGE (\d+) =====")


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_pages(ticker: str, year: int) -> dict[int, str]:
    """Đọc bản văn bản đã bóc (bộ đệm của run_nnc), tách theo trang."""
    path = TEXT_CACHE / ticker / f"{ticker}_{year}_col-60.txt"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    pages: dict[int, str] = {}
    marks = list(_PAGE_MARK.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        pages[int(m.group(1))] = _squash(text[m.end():end])
    return pages


def context_for(sentence: str, page_text: str) -> str:
    """Lấy đoạn văn quanh câu gốc; rỗng nếu không tìm thấy."""
    if not page_text:
        return ""
    probe = _squash(sentence)[:40]
    pos = page_text.find(probe)
    if pos < 0:
        return ""
    start = max(pos - CONTEXT_CHARS, 0)
    end = min(pos + len(_squash(sentence)) + CONTEXT_CHARS, len(page_text))
    return ("…" if start else "") + page_text[start:end] + ("…" if end < len(page_text) else "")


# ── Lấy mẫu ───────────────────────────────────────────────────────────────


def allocate(strata: dict[str, list], total: int) -> dict[str, int]:
    """Lấy hết tầng "mâu thuẫn", chia phần còn lại theo tỷ lệ cỡ tầng."""
    take = {INCONSISTENT: len(strata.get(INCONSISTENT, []))}
    rest = {k: v for k, v in strata.items() if k != INCONSISTENT}
    budget = max(total - take[INCONSISTENT], 0)
    pool = sum(len(v) for v in rest.values())
    shares = {k: budget * len(v) / pool for k, v in rest.items()} if pool else {}
    # Làm tròn theo phần dư lớn nhất để tổng đúng bằng budget.
    floors = {k: int(s) for k, s in shares.items()}
    leftover = budget - sum(floors.values())
    for k in sorted(shares, key=lambda k: shares[k] - floors[k], reverse=True)[:leftover]:
        floors[k] += 1
    take.update({k: min(n, len(rest[k])) for k, n in floors.items()})
    return take


def split_dev_test(groups: list[tuple[str, int]], sizes: Counter, rng: random.Random) -> set:
    """Chọn các cặp (mã, năm) cho tập dev cho tới khi đủ khoảng DEV_TARGET câu."""
    order = groups[:]
    rng.shuffle(order)
    dev, count = set(), 0
    for g in order:
        if count >= DEV_TARGET:
            break
        dev.add(g)
        count += sizes[g]
    return dev


def main() -> int:
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    rng = random.Random(seed)

    payload = json.loads((RESULTS / "nnc_results.json").read_text(encoding="utf-8"))

    claims = [
        (rep["ticker"], rep["year"], c)
        for rep in payload
        if rep["ticker"] not in BANKS
        for c in rep["claims"]
    ]
    strata: dict[str, list] = defaultdict(list)
    for item in claims:
        strata[item[2]["verdict"]].append(item)

    take = allocate(strata, total)
    sample = []
    for verdict, n in take.items():
        population = strata[verdict]
        chosen = population if n >= len(population) else rng.sample(population, n)
        weight = len(population) / n if n else 0.0
        sample.extend((verdict, weight, item) for item in chosen)

    sizes = Counter((t, y) for _, _, (t, y, _) in sample)
    dev_groups = split_dev_test(sorted(sizes), sizes, rng)

    facts, report_names = load_facts(set(sizes))
    pages_cache: dict[tuple[str, int], dict[int, str]] = {}

    rng.shuffle(sample)
    sheet_rows, key_rows = [], []
    for i, (verdict, weight, (ticker, year, c)) in enumerate(sample, 1):
        row_id = f"NN-{i:03d}"
        fact = facts.get((ticker, year), {}).get(c["metric"])
        if (ticker, year) not in pages_cache:
            pages_cache[(ticker, year)] = load_pages(ticker, year)
        page_text = pages_cache[(ticker, year)].get(c["page"], "")

        sheet_rows.append({
            "id": row_id,
            "ma_ck": ticker,
            "nam": year,
            "trang_bctn": c["page"],
            "cau_goc": c["text"],
            "ngu_canh": context_for(c["text"], page_text),
            "chi_tieu": concept_label(c["metric"]),
            "ma_so": fact.code if fact else "",
            "khoan_muc_trong_bang": fact.label if fact else "(không tra được chỉ tiêu này trong BCTC)",
            "bctc_nguon": report_names.get((ticker, year), ""),
            "trang_bctc": fact.page if fact else "",
            "nam_nay_nhu_in_trong_bang": fmt_value(fact, fact.current) if fact else "",
            "nam_truoc_nhu_in_trong_bang": fmt_value(fact, fact.previous) if fact else "",
            "bien_dong": fmt_growth(fact) if fact else "",
            **{col: "" for col in LABEL_COLUMNS},
        })
        key_rows.append({
            "id": row_id,
            "ma_ck": ticker,
            "nam": year,
            "trang_bctn": c["page"],
            "metric": c["metric"],
            "verdict_he_thong": verdict,
            "score": c["score"],
            "tang": verdict,
            "trong_so": f"{weight:.4f}",
            "tap": "dev" if (ticker, year) in dev_groups else "test",
            "cau_goc": c["text"],
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("sheet_nguoi_gan_1.csv", "sheet_nguoi_gan_2.csv"):
        with open(OUT_DIR / name, "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(sheet_rows[0]))
            writer.writeheader()
            writer.writerows(sheet_rows)
    with open(OUT_DIR / "sample_key.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    # ── Tóm tắt ──
    print(f"Tổng thể (bỏ ngân hàng): {len(claims)} khẳng định")
    for verdict in sorted(strata):
        print(f"  {verdict:<24} N={len(strata[verdict]):>4}  lấy n={take.get(verdict, 0):>4}")
    n_dev = sum(1 for r in key_rows if r["tap"] == "dev")
    print(f"Mẫu: {len(key_rows)} cặp · dev {n_dev} · test {len(key_rows) - n_dev} "
          f"· {len(sizes)} báo cáo (mã, năm) · seed {seed}")
    no_fact = sum(1 for r in sheet_rows if not r["ma_so"])
    no_ctx = sum(1 for r in sheet_rows if not r["ngu_canh"])
    print(f"Dòng không tra được số liệu BCTC: {no_fact} · không tìm được ngữ cảnh: {no_ctx}")
    print(f"Đã ghi {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
