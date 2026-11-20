"""Ghép báo cáo giải pháp Vòng 2 vào ĐÚNG mẫu Word của Ban Tổ chức.

Nguồn nội dung:
* Mục 01, 02: dữ liệu trong script này (thông tin đội, tóm lược, số đo chính).
* Mục 03–08: ``docs/bao-cao/0X-*.md`` — mỗi tiểu mục "## 1.1. …" được đặt vào
  đúng chỗ của tiểu mục tương ứng trong mẫu, thay cho dòng hướng dẫn "[…]".

Phần sau đường kẻ "═══" và dòng "> …" trong tệp .md là ghi chú, không đưa vào.
Script dừng với lỗi nếu còn sót bất kỳ placeholder "⟦…⟧" hay "[…]" nào.

Chạy (môi trường có python-docx):
    python deliverables/build/build_report.py
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "deliverables" / "build" / "template_bao_cao.docx"
OUT = ROOT / "deliverables" / "AQ2026-R2-AQ2026-064-Bao_cao_giai_phap.docx"
VALUES = ROOT / "deliverables" / "build" / "values.json"
MEMBERS = ROOT / "deliverables" / "build" / "members.local.json"  # chứa CCCD — KHÔNG commit, KHÔNG đưa vào zip
SIGNATURE = ROOT / "deliverables" / "build" / "chu_ky.local.png"  # chữ ký đội trưởng — KHÔNG commit

TEAL = RGBColor(0x08, 0x67, 0x78)
BODY_PT = 11
TABLE_PT = 9

V = json.loads(VALUES.read_text(encoding="utf-8"))


def fill(text: str) -> str:
    """Thay các placeholder ⟦CHỜ: …⟧ đã có số thật (values.json)."""
    for pattern, value in V.get("replace", {}).items():
        text = re.sub(pattern, value, text)
    return text


# ── Đọc markdown ──────────────────────────────────────────────────────────

_IMG = re.compile(r'^!\[(.+)\]\(([^)\s]+)(?:\s+"([\d.]+)")?\)$')

def parse_md(path: Path) -> dict[str, list[tuple[str, object]]]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # Chỉ cắt ở dòng kẻ đứng riêng ("═════…"), không cắt khi ký tự này nằm giữa câu.
    text = re.split(r"^═{5,}\s*$", text, flags=re.M)[0]
    sections: dict[str, list[tuple[str, object]]] = {}
    current: list[tuple[str, object]] | None = None
    para: list[str] = []
    table: list[list[str]] = []

    def flush():
        nonlocal para, table
        if para and current is not None:
            current.append(("p", " ".join(para)))
        if table and current is not None:
            current.append(("table", table))
        para, table = [], []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("## ") or line.startswith("### "):
            flush()
            key = line.lstrip("#").strip()
            current = sections.setdefault(key, [])
            continue
        if line.startswith("# ") or line.startswith(">"):
            continue
        if current is None:
            continue
        if line.startswith("|"):
            if para:
                current.append(("p", " ".join(para)))
                para = []
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            table.append(cells)
            continue
        if table:
            current.append(("table", table))
            table = []
        if not line.strip():
            flush()
            continue
        img = _IMG.match(line.strip())
        if img:  # ![chú thích](đường/dẫn.png "rộng cm")
            flush()
            current.append(("img", (img.group(1), path.parent / img.group(2), float(img.group(3) or 15))))
            continue
        if re.match(r"^(\s*[-*]\s+|\s*\d+\.\s+)", line):
            flush()
            current.append(("li", line.strip()))
            continue
        para.append(line.strip())
    flush()
    return sections


def find_block(sections: dict, prefix: str):
    for key, blocks in sections.items():
        if key.lower().startswith(prefix.lower()):
            return blocks
    return None


# ── Ghi vào docx ──────────────────────────────────────────────────────────

_INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_runs(p: Paragraph, text: str, size: float = BODY_PT, bold: bool | None = None, color=None):
    for part in _INLINE.split(fill(text)):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(size - 1.5)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            continue
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            r = p.add_run(part)
        r.font.size = Pt(size)
        if bold is not None and not r.bold:
            r.bold = bold
        if color is not None:
            r.font.color.rgb = color


def new_paragraph_before(anchor, template_p: Paragraph | None = None) -> Paragraph:
    p_el = OxmlElement("w:p")
    anchor.addprevious(p_el)
    p = Paragraph(p_el, template_p._parent if template_p is not None else None)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    return p


def set_cell_shading(cell, hex_fill: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def set_table_borders(tbl):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4"); el.set(qn("w:color"), "B7C9CC")
        borders.append(el)
    tblPr.append(borders)


def table_before(doc, anchor, rows: list[list[str]]):
    ncols = max(len(r) for r in rows)
    tbl = doc.add_table(rows=len(rows), cols=ncols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    for i, row in enumerate(rows):
        # Không cắt một hàng ra hai trang; dòng tiêu đề lặp lại nếu bảng sang trang mới
        trPr = tbl.rows[i]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for j in range(ncols):
            cell = tbl.cell(i, j)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            text = row[j] if j < len(row) else ""
            if i == 0:
                set_cell_shading(cell, "086778")
                add_runs(cell.paragraphs[0], text, size=TABLE_PT, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
            else:
                add_runs(cell.paragraphs[0], text, size=TABLE_PT)
    anchor.addprevious(tbl._tbl)
    spacer = OxmlElement("w:p")
    anchor.addprevious(spacer)
    shrink_empty(spacer)


def shrink_empty(p_el, size_half_pt: int = 8):
    """Đoạn trống chỉ để tách khối: thu về cỡ 4pt, không cách sau (báo cáo phải gọn 12 trang)."""
    pPr = p_el.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p_el.insert(0, pPr)
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = OxmlElement("w:spacing")
        pPr.append(spacing)
    spacing.set(qn("w:before"), "0"); spacing.set(qn("w:after"), "0")
    spacing.set(qn("w:line"), "240"); spacing.set(qn("w:lineRule"), "auto")
    rPr = pPr.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        pPr.append(rPr)
    for tag in ("w:sz", "w:szCs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rPr.append(el)
        el.set(qn("w:val"), str(size_half_pt))


def render_blocks(doc, anchor_p: Paragraph, blocks):
    anchor = anchor_p._p
    for kind, content in blocks:
        if kind == "p":
            p = new_paragraph_before(anchor, anchor_p)
            p.alignment = 3  # justify
            add_runs(p, content)
        elif kind == "li":
            p = new_paragraph_before(anchor, anchor_p)
            p.paragraph_format.left_indent = Pt(14)
            p.paragraph_format.first_line_indent = Pt(-10)
            text = re.sub(r"^[-*]\s+", "• ", content)
            add_runs(p, text)
        elif kind == "table":
            table_before(doc, anchor, content)
        elif kind == "img":
            caption, img_path, width_cm = content
            p = new_paragraph_before(anchor, anchor_p)
            p.alignment = 1  # center
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(img_path), width=Cm(width_cm))
            cap = new_paragraph_before(anchor, anchor_p)
            cap.alignment = 1
            cap.paragraph_format.space_after = Pt(6)
            add_runs(cap, caption, size=9.5, color=RGBColor(0x3B, 0x4A, 0x51))
            for r in cap.runs:
                r.italic = True


def delete(p: Paragraph):
    p._p.getparent().remove(p._p)


def set_text(p: Paragraph, text: str, keep_format: bool = True):
    """Thay chữ của một đoạn, giữ định dạng run đầu, bỏ nghiêng/xám của chữ hướng dẫn."""
    runs = p.runs
    if not runs:
        p.add_run(text)
        return
    runs[0].text = text
    runs[0].italic = False
    if runs[0].font.color is not None and runs[0].font.color.type is not None and str(runs[0].font.color.rgb) == "62747B":
        runs[0].font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    for r in runs[1:]:
        r.text = ""


def set_cell(cell, text: str, size: float | None = None):
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    runs = p.runs
    if runs:
        runs[0].text = text
        runs[0].italic = False
        if runs[0].font.color is not None and runs[0].font.color.type is not None:
            runs[0].font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        if size:
            runs[0].font.size = Pt(size)
        for r in runs[1:]:
            r.text = ""
    else:
        add_runs(p, text, size=size or TABLE_PT)


def footer_page_field(last_run):
    """Thay số cố định cuối chân trang bằng trường PAGE (số trang thật), giữ định dạng chữ."""
    last_run.text = re.sub(r"\d+\s*$", "", last_run.text)
    rPr = last_run._r.rPr

    def run_with(child):
        r = OxmlElement("w:r")
        if rPr is not None:
            r.append(copy.deepcopy(rPr))
        r.append(child)
        return r

    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    shown = OxmlElement("w:t"); shown.text = "1"
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    anchor = last_run._r
    for child in (begin, instr, sep, shown, end):
        el = run_with(child)
        anchor.addnext(el)
        anchor = el


# ── Chương trình chính ────────────────────────────────────────────────────

SECTION_FILES = {
    "1.": "03-tieu-chi-1-bai-toan.md",
    "2.": "04-tieu-chi-2-du-lieu.md",
    "3.": "05-tieu-chi-3-giai-phap.md",
    "4.": "06-tieu-chi-4-prototype.md",
    "5.": "07-tieu-chi-5-trien-khai.md",
    "6.": "08-tieu-chi-6-trinh-bay.md",
}
EXTRA_HEADINGS = {  # tiêu đề trong mẫu không đánh số → khoá trong .md
    "Kết luận tiêu chí 1": "Kết luận",
    "Minh chứng chất lượng dữ liệu": "Minh chứng",
    "Giới hạn của giải pháp": "Giới hạn",
}


def main() -> int:
    doc = Document(TEMPLATE)
    md = {k: parse_md(ROOT / "docs" / "bao-cao" / f) for k, f in SECTION_FILES.items()}
    meta = json.loads(MEMBERS.read_text(encoding="utf-8")) if MEMBERS.exists() else {}
    members = meta.get("members")
    lien_he = meta.get("lien_he", V.get("lien_he", ""))

    paras = list(doc.paragraphs)

    # Bìa trước
    for p in paras:
        t = p.text.strip()
        if t.startswith("[Nhập tên giải pháp"):
            set_text(p, V["ten_giai_phap"])
        elif t.startswith("Mã đội: [Mã đội]"):
            set_text(p, "Mã đội: AQ2026-064     •     Tên đội: Ngôi nhà Hoa Hồng")
        elif t.startswith("Khoa / trường đại diện"):
            set_text(p, f"Khoa / trường đại diện (theo đội trưởng): {V['truong_dai_dien']}")
        elif t.startswith("Giảng viên hướng dẫn (nếu có): [Họ tên"):
            set_text(p, "Giảng viên hướng dẫn (nếu có): Không")
    member_lines = [p for p in paras if re.match(r"^\d\.\s+\[Họ và tên\]", p.text.strip())]
    names = [m["ho_ten"] for m in members] if members else V["thanh_vien"]
    for i, p in enumerate(member_lines):
        if i < len(names):
            role = "Đội trưởng" if i == 0 else "Thành viên"
            set_text(p, f"{i + 1}.  {names[i]}     •     {role}")
        else:
            delete(p)

    # Bỏ khối "Hướng dẫn dành cho đội thi" (lời dặn của BTC, không phải nội dung)
    start = next(i for i, p in enumerate(paras) if p.text.strip() == "HƯỚNG DẪN DÀNH CHO ĐỘI THI")
    for p in paras[start:start + 6]:
        if p.text.strip():
            delete(p)

    # Mục 01: bảng thông tin
    t_info, t_mem, t_prod, t_sum, t_kpi = doc.tables[2], doc.tables[3], doc.tables[4], doc.tables[6], doc.tables[7]
    info = list(V["thong_tin_doi"])
    info[4] = lien_he or info[4]  # người liên hệ chính
    for row, value in zip(t_info.rows[1:], info):
        set_cell(row.cells[1], value)
    if members:
        for row, m in zip(t_mem.rows[1:], members):
            for cell, key in zip(row.cells[1:7], ("ho_ten", "nganh", "truong", "cccd", "email", "dien_thoai")):
                set_cell(cell, m[key])
            set_cell(row.cells[7], m["vai_tro"])
        for row in t_mem.rows[1 + len(members):]:
            row._tr.getparent().remove(row._tr)
    for row, values in zip(t_prod.rows[1:], V["san_pham"]):
        for cell, value in zip(row.cells[1:], values):
            set_cell(cell, fill(value))

    # Mục 02: tóm lược + số đo chủ đạo
    for row, (result, evidence) in zip(t_sum.rows[1:], V["tom_luoc"]):
        set_cell(row.cells[1], fill(result), size=10)
        set_cell(row.cells[2], fill(evidence), size=10)
    for p in paras:
        if p.text.strip().startswith("[Giải pháp giúp ai"):
            set_text(p, fill(V["gia_tri_cot_loi"]))
    kpis = V["so_do_chinh"]
    for i, values in enumerate(kpis):
        if i + 1 < len(t_kpi.rows):
            row = t_kpi.rows[i + 1]
        else:
            new_tr = copy.deepcopy(t_kpi.rows[1]._tr)
            t_kpi._tbl.append(new_tr)
            row = t_kpi.rows[-1]
        for cell, value in zip(row.cells, values):
            set_cell(cell, fill(value))

    # Mục 03–08
    paras = list(doc.paragraphs)
    section = None
    for idx, p in enumerate(paras):
        t = p.text.strip()
        if p.style.name == "Heading 1":
            m = re.match(r"^(\d)\.\s", t)
            section = f"{m.group(1)}." if m and f"{m.group(1)}." in md else None
            continue
        if section is None:
            continue
        if t.startswith("MINH CHỨNG BỔ SUNG"):
            delete(p)
            continue
        if p.style.name != "Heading 2":
            continue
        key = None
        m = re.match(r"^(\d\.\d)\.", t)
        if m:
            key = m.group(1)
        else:
            for heading, k in EXTRA_HEADINGS.items():
                if t.startswith(heading):
                    key = k
        if key is None:
            continue
        blocks = find_block(md[section], key)
        if blocks is None:
            print(f"!! Không có nội dung cho '{t[:50]}' ({SECTION_FILES[section]})")
            continue
        # Chỗ đặt: dòng hướng dẫn "[…]" ngay sau tiêu đề, nếu có
        nxt = paras[idx + 1] if idx + 1 < len(paras) else None
        if nxt is not None and nxt.text.strip().startswith("["):
            render_blocks(doc, nxt, blocks)
            delete(nxt)
        else:
            anchor = nxt if nxt is not None else p
            render_blocks(doc, anchor, blocks)

    # Dòng liên kết demo (mục 06)
    for p in doc.paragraphs:
        if p.text.strip().startswith("Liên kết chạy demo: [URL]"):
            set_text(p, fill(f"Liên kết chạy demo: {V['link']}   |   Video demo: {V['video']}"))

    # Cam kết: chừa chỗ ký, ghi họ tên đại diện (đội trưởng) dưới dòng "(Ký, ghi rõ họ tên)"
    for p in doc.paragraphs:
        if p.text.strip().startswith("ĐẠI DIỆN ĐỘI THI"):
            name_el = copy.deepcopy(p._p)
            p._p.addnext(name_el)
            name_p = Paragraph(name_el, p._parent)
            set_text(name_p, names[0])
            name_p.paragraph_format.space_before = Pt(26)
            if SIGNATURE.exists():  # có chữ ký trên máy thì chèn ảnh vào chỗ trống
                sig_el = copy.deepcopy(p._p)
                p._p.addnext(sig_el)
                sig_p = Paragraph(sig_el, p._parent)
                for r in sig_p.runs:
                    r._r.getparent().remove(r._r)
                sig_p.paragraph_format.space_before = Pt(2)
                sig_p.paragraph_format.space_after = Pt(0)
                sig_p.add_run().add_picture(str(SIGNATURE), height=Cm(1.3))
                name_p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_before = Pt(6)  # bớt khoảng trống phía trên để khối ký nằm gọn một trang
                prev = p._p.getprevious()
                if prev is not None and prev.tag == qn("w:p") and not "".join(prev.itertext()).strip():
                    prev.getparent().remove(prev)  # đoạn trống ngay trên khối ký
            break

    # Bìa sau
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("MÃ ĐỘI  ["):
            set_text(p, "MÃ ĐỘI  AQ2026-064")
        elif t.startswith("TÊN ĐỘI  ["):
            set_text(p, "TÊN ĐỘI  Ngôi nhà Hoa Hồng")
        elif t.startswith("TÊN GIẢI PHÁP") and "[" in t:
            set_text(p, "TÊN GIẢI PHÁP\n" + V["ten_ngan"])
        elif t.startswith("Thông tin liên hệ chính: ["):
            set_text(p, f"Thông tin liên hệ chính: {lien_he}")

    # Gọn khoảng trắng ở mục 03–08: tiêu đề nhỏ cách ít hơn, đoạn trống (không phải ngắt
    # section) thu nhỏ. Chữ giữ nguyên.
    in_body = False
    for p in doc.paragraphs:
        t = p.text.strip()
        if p.style.name == "Heading 1" and t.startswith("1. MỨC ĐỘ"):
            in_body = True
        if t.startswith("ĐẠI DIỆN ĐỘI THI"):
            break
        if not in_body:
            continue
        if p.style.name == "Heading 2":
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(3)
        elif not t and not p._p.xpath(".//w:drawing") and not p._p.xpath(".//w:sectPr"):
            shrink_empty(p._p)

    # Băng "0X / TIÊU CHÍ n" luôn đi liền tiêu đề mục ngay sau nó (không nằm lẻ cuối trang);
    # đoạn ngắt section ngay trước băng thu về 6pt để giữ khoảng thở mà không tốn chỗ.
    for tbl in doc.tables:
        if re.match(r"^\s*0[4-8]\s*/\s*TIÊU CHÍ", tbl.cell(0, 0).text):
            for row in tbl.rows:
                for cell in row.cells:
                    for cp in cell.paragraphs:
                        cp.paragraph_format.keep_with_next = True
            nxt = tbl._tbl.getnext()  # đoạn trống của mẫu giữa băng và tiêu đề: cũng phải "đi liền"
            if nxt is not None and nxt.tag == qn("w:p") and not "".join(nxt.itertext()).strip():
                Paragraph(nxt, tbl._parent).paragraph_format.keep_with_next = True
            prev = tbl._tbl.getprevious()
            if prev is not None and prev.tag == qn("w:p") and prev.xpath(".//w:sectPr") and not "".join(prev.itertext()).strip():
                shrink_empty(prev, size_half_pt=12)

    # Báo cáo 08–12 trang: tiêu chí 2–6 (mục 04–08) chạy nối tiếp thay vì ép sang trang mới.
    # Chân trang của mẫu ghi cứng số mục 1–8; đổi thành số trang thật để không gây nhầm.
    for k, sec in enumerate(doc.sections):
        if 4 <= k <= 8:
            sec.start_type = WD_SECTION.CONTINUOUS
        for p in sec.footer.paragraphs:
            if p.runs and re.search(r"•\s*\d+\s*$", p.runs[-1].text):
                footer_page_field(p.runs[-1])

    # Kiểm tra sót
    leftovers = []
    for p in doc.paragraphs:
        if "⟦" in p.text or re.search(r"\[[^\]]*\]", p.text):
            leftovers.append(p.text.strip()[:90])
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                if "⟦" in cell.text or re.search(r"\[(Họ|Mã|Tên|Giá|Chỉ|Điều|Nguồn|Đường|https|Web|Vấn|Phương|Chức|Đơn|Báo|Mục|Bảng|Hình|Demo|Kế|Ngành|Trường|CCCD|Email|SĐT|Bản|Quyền|Nếu|Hướng)", cell.text):
                    leftovers.append("ô bảng: " + cell.text.strip()[:80])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Đã ghi {OUT}")
    if leftovers:
        print("!! Còn placeholder:")
        for x in dict.fromkeys(leftovers):
            print("   ", x)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
