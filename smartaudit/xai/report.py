"""Sinh báo cáo đối chiếu ở dạng kiểm toán viên đọc và dùng được.

Tiêu chí chấm điểm Vòng 3 yêu cầu *"xem xét tính giải thích
(explainability), độ tin cậy và các rủi ro kỹ thuật của mô hình"*. Một
con số 0,42 không đủ để kiểm toán viên đưa vào hồ sơ làm việc — họ cần
biết **kết luận đó rút ra từ đâu**.

Mỗi phát hiện trong báo cáo này đều truy được về: câu gốc nằm ở trang nào
của Báo cáo thường niên, số liệu lấy từ mã nào ở trang nào của Báo cáo tài
chính, và phép tính đối chiếu ra sao.
"""

from __future__ import annotations

from smartaudit.nnc import NNCResult, Verdict

_ICON = {
    Verdict.CONSISTENT: "✓",
    Verdict.INCONSISTENT: "✗",
    Verdict.UNVERIFIABLE: "?",
}

#: Tên chiều kiểm, hiển thị cho người đọc.
_DIMENSION = {
    "numeric": "Đối chiếu giá trị",
    "directional": "Đối chiếu xu hướng",
    "qualitative": "Đối chiếu định tính",
    "scope": "Phạm vi",
    "continuity": "Tính liên tục của chuỗi số liệu",
    "lookup": "Tra cứu",
}

#: Chiều mang tính thông báo, không phải phán quyết đúng/sai.
_INFORMATIONAL = {"scope", "continuity", "lookup"}


def _wrap(text: str, width: int, indent: str) -> list[str]:
    """Ngắt dòng theo từ, không cắt giữa chữ."""
    words, lines, current = text.split(), [], ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(indent + current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(indent + current)
    return lines


def render_report(
    ticker: str,
    year: int,
    results: list[NNCResult],
    width: int = 78,
) -> str:
    """Dựng báo cáo đối chiếu dạng văn bản cho một doanh nghiệp, một năm."""
    counts = {v: sum(1 for r in results if r.verdict is v) for v in Verdict}
    scored = [r.score for r in results if r.score is not None]
    overall = sum(scored) / len(scored) if scored else None

    out: list[str] = []
    out.append("═" * width)
    out.append(f"  BÁO CÁO ĐỐI CHIẾU NGÔN TỪ – SỐ LIỆU".center(width))
    out.append(f"  {ticker} · Năm tài chính {year}".center(width))
    out.append("═" * width)
    out.append("")

    if overall is not None:
        bar_width = 30
        filled = round(overall * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        out.append(f"  Điểm nhất quán NNC   {bar}  {overall:.2f}")
    else:
        out.append("  Điểm nhất quán NNC   (không đủ dữ liệu để chấm)")

    out.append(
        f"  Khẳng định đã xét    {len(results)}  ·  "
        f"nhất quán {counts[Verdict.CONSISTENT]}  ·  "
        f"mâu thuẫn {counts[Verdict.INCONSISTENT]}  ·  "
        f"chưa kiểm chứng {counts[Verdict.UNVERIFIABLE]}"
    )
    out.append("")

    flagged = [r for r in results if r.verdict is Verdict.INCONSISTENT]
    if flagged:
        out.append("─" * width)
        out.append(f"  PHÁT HIỆN CẦN XEM XÉT  ({len(flagged)})")
        out.append("─" * width)
        for index, result in enumerate(flagged, 1):
            claim = result.claim
            out.append("")
            out.append(
                f"  {index}. [{_ICON[result.verdict]}] {claim.metric}  ·  "
                f"BCTN trang {claim.page}  ·  điểm {result.score:.2f}"
            )
            out.append("")
            out.extend(_wrap(f"“{claim.text}”", width - 8, "      "))
            out.append("")
            for evidence in result.evidence:
                if evidence.dimension in _INFORMATIONAL:
                    mark = "!"
                else:
                    mark = "✓" if evidence.passed else "✗"
                name = _DIMENSION.get(evidence.dimension, evidence.dimension)
                out.append(f"      {mark} {name}")
                out.extend(_wrap(evidence.explanation, width - 12, "        "))
                if evidence.source_label:
                    out.extend(
                        _wrap(
                            f"Nguồn: {evidence.source_label}",
                            width - 12,
                            "        ",
                        )
                    )
            out.append("")

    consistent = [r for r in results if r.verdict is Verdict.CONSISTENT]
    if consistent:
        out.append("─" * width)
        out.append(f"  KHẲNG ĐỊNH ĐÃ XÁC MINH KHỚP  ({len(consistent)})")
        out.append("─" * width)
        for result in consistent[:10]:
            out.extend(
                _wrap(f"✓ {result.claim.text}", width - 6, "    ")
            )
        if len(consistent) > 10:
            out.append(f"    ... còn {len(consistent) - 10} khẳng định nữa")
        out.append("")

    unverifiable = [r for r in results if r.verdict is Verdict.UNVERIFIABLE]
    if unverifiable:
        out.append("─" * width)
        out.append(f"  CHƯA KIỂM CHỨNG ĐƯỢC  ({len(unverifiable)})")
        out.append("─" * width)
        out.append("")
        out.extend(
            _wrap(
                "Những khẳng định dưới đây hệ thống không đối chiếu được — "
                "không có nghĩa là sai. Kiểm toán viên nên xem thủ công.",
                width - 6,
                "    ",
            )
        )
        out.append("")
        for result in unverifiable[:8]:
            out.extend(_wrap(f"? {result.claim.text}", width - 6, "    "))
            if result.evidence:
                out.extend(
                    _wrap(f"→ {result.evidence[0].explanation}", width - 10, "       ")
                )
        out.append("")

    out.append("═" * width)
    out.extend(
        _wrap(
            "Hệ thống KHÔNG kết luận doanh nghiệp gian lận. Kết quả chỉ đánh "
            "dấu điểm chưa nhất quán giữa phần diễn giải và số liệu, kèm minh "
            "chứng để con người xem xét và quyết định.",
            width - 4,
            "  ",
        )
    )
    out.append("═" * width)
    return "\n".join(out)
