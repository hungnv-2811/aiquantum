# -*- coding: utf-8 -*-
"""Sinh slide Vòng 2: deliverables/AQ2026-R2-AQ2026-064-Slide.pptx

Chạy:  <python có python-pptx> deliverables/build/build_slides.py
Nội dung lấy từ docs/slide/dan-y-slide.md (v1, 19/11/2026). Số liệu lấy từ
docs/bao-cao/07-tieu-chi-5-trien-khai.md và docs/quantum-poc.md.
Mỗi placeholder ⟦CHỜ: …⟧ nằm trọn trong MỘT text run, để đội thay bằng script
(ví dụ duyệt mọi run, run.text = run.text.replace(...)). Cuối chương trình in
danh sách placeholder còn lại.
"""
import os
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "AQ2026-R2-AQ2026-064-Slide.pptx")

# Link prototype đã triển khai (Vercel, 19/11/2026) và mã QR dẫn tới link đó.
from pathlib import Path as _Path
import json as _json
PROTOTYPE_URL = _json.loads((_Path(HERE) / "values.json").read_text(encoding="utf-8"))["link"]
QR_PNG = _Path(HERE) / "qr_prototype.png"

FONT = "Arial"
TEAL = RGBColor(0x0B, 0x55, 0x63)
TEAL_LIGHT = RGBColor(0xE4, 0xEF, 0xF1)
TEAL_MID = RGBColor(0x5E, 0x93, 0x9C)
GOLD = RGBColor(0xC9, 0x96, 0x2B)
GOLD_LIGHT = RGBColor(0xF8, 0xF0, 0xDC)
INK = RGBColor(0x1E, 0x29, 0x2E)
GRAY = RGBColor(0x5F, 0x6B, 0x72)
GRAY_LIGHT = RGBColor(0xEE, 0xF0, 0xF1)
LINE = RGBColor(0xC9, 0xD2, 0xD5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
GREEN_LIGHT = RGBColor(0xE6, 0xF2, 0xE7)
RED = RGBColor(0xC6, 0x28, 0x28)
RED_LIGHT = RGBColor(0xFB, 0xE9, 0xE9)
GRAYV = RGBColor(0x75, 0x75, 0x75)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SLIDE_NO = [0]


# ---------------------------------------------------------------- helpers
def _style_run(run, size=16, color=INK, bold=False, italic=False):
    f = run.font
    f.name = FONT
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", FONT)


def write(tf, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
          space_after=4, line_spacing=1.05, bullet=None):
    """paras: list; mỗi phần tử là str hoặc list các đoạn (str | (str, dict)).
    Một str = một run, nên placeholder ⟦CHỜ: …⟧ không bao giờ bị tách."""
    tf.clear()
    first = True
    for p in paras:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = align
        para.space_after = Pt(space_after)
        para.line_spacing = line_spacing
        segs = p if isinstance(p, list) else [p]
        if bullet:
            segs = [(bullet + " ", {"color": GOLD, "bold": True})] + list(segs)
        for s in segs:
            text, st = (s, {}) if isinstance(s, str) else s
            r = para.add_run()
            r.text = text
            _style_run(r, size=st.get("size", size), color=st.get("color", color),
                       bold=st.get("bold", bold), italic=st.get("italic", False))
    return tf


def textbox(slide, x, y, w, h, paras, size=16, color=INK, bold=False,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, bullet=None, space_after=4,
            line_spacing=1.05):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    write(tf, paras, size=size, color=color, bold=bold, align=align, bullet=bullet,
          space_after=space_after, line_spacing=line_spacing)
    return tb


def box(slide, x, y, w, h, paras=None, fill=WHITE, line=LINE, size=14, color=INK,
        bold=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        dash=False, line_w=1.0, bullet=None, margin=0.1, space_after=2):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.08
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = anchor
    if paras:
        write(tf, paras, size=size, color=color, bold=bold, align=align, bullet=bullet,
              space_after=space_after)
    return sh


def arrow(slide, x1, y1, x2, y2, color=TEAL_MID, width=1.75, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    ln = c.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return c


def rect(slide, x, y, w, h, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def table(slide, x, y, w, rows, col_w, row_h=0.42, size=13, header_fill=TEAL,
          highlight=None, bold_rows=(), aligns=None):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    tbl = gt.table
    tblPr = tbl._tbl.tblPr
    style = tblPr.find(qn("a:tableStyleId"))
    if style is not None:
        style.text = "{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"  # Medium Style 2: viền trắng mảnh
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i in range(nr):
        tbl.rows[i].height = Inches(row_h)
        for j in range(nc):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            val = rows[i][j]
            if i == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_fill
                col, b = WHITE, True
            else:
                cell.fill.solid()
                if highlight and i in highlight:
                    cell.fill.fore_color.rgb = highlight[i]
                else:
                    cell.fill.fore_color.rgb = WHITE if i % 2 else GRAY_LIGHT
                col, b = INK, (i in bold_rows)
            al = PP_ALIGN.LEFT if (aligns is None or aligns[j] == "l") else PP_ALIGN.CENTER
            write(cell.text_frame, [val], size=size, color=col, bold=b, align=al, space_after=0)
    return gt


def new_slide(title, notes="", source=None, backup=False):
    s = prs.slides.add_slide(BLANK)
    SLIDE_NO[0] += 1
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    rect(s, 0, 0, 13.333, 0.12, TEAL)
    if backup:
        box(s, 11.35, 0.28, 1.4, 0.36, ["DỰ PHÒNG"], fill=GOLD_LIGHT, line=GOLD, size=11,
            bold=True, color=GOLD)
    textbox(s, 0.6, 0.3, 10.6 if backup else 12.1, 1.05, [title], size=26, color=TEAL, bold=True,
            anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
    rect(s, 0.62, 1.4, 1.1, 0.06, GOLD)
    # chân trang
    rect(s, 0.6, 7.0, 12.13, 0.012, LINE)
    textbox(s, 0.6, 7.05, 8, 0.3, ["SmartAudit-Quantum · AQ2026-064 · Vòng 2"], size=10, color=GRAY)
    textbox(s, 11.7, 7.05, 1.03, 0.3, [str(SLIDE_NO[0])], size=10, color=GRAY, align=PP_ALIGN.RIGHT)
    if source:
        textbox(s, 0.6, 6.68, 12.1, 0.3, [source], size=10, color=GRAY)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


# ---------------------------------------------------------------- slide 1
s = prs.slides.add_slide(BLANK)
SLIDE_NO[0] += 1
s.background.fill.solid()
s.background.fill.fore_color.rgb = WHITE
rect(s, 0, 0, 4.3, 7.5, TEAL)
textbox(s, 0.5, 0.6, 3.4, 0.4, ["AI-QUANTUM CHALLENGE 2026"], size=13, color=GOLD, bold=True)
textbox(s, 0.5, 1.0, 3.4, 0.4, ["Vòng 2 · Bán kết"], size=13, color=WHITE)
textbox(s, 0.5, 5.6, 3.4, 0.5, ["Đội AQ2026-064"], size=22, color=WHITE, bold=True)
textbox(s, 0.5, 6.1, 3.4, 0.5, ["Ngôi nhà Hoa Hồng"], size=20, color=GOLD, bold=True)
textbox(s, 4.9, 0.85, 8.0, 1.0, ["SmartAudit-Quantum"], size=44, color=TEAL, bold=True)
rect(s, 4.95, 1.95, 1.4, 0.07, GOLD)
textbox(s, 4.9, 2.2, 7.9, 1.2,
        ["Đối chiếu lời văn trong báo cáo thường niên với số liệu báo cáo tài chính đã kiểm toán — "
         "mỗi phát hiện chỉ tới đúng ô bảng"], size=20, color=INK, line_spacing=1.1)
members = [("Nguyễn Việt Hùng", "Trưởng nhóm · AI/NLP"),
           ("Nguyễn Hồng Nguyên", "Nghiệp vụ tài chính · Ontology"),
           ("Lê Cao Phong", "Quantum ML · Hệ thống"),
           ("Mai Đức Tài", "Rủi ro tài chính · Sản phẩm")]
for k, (n, r) in enumerate(members):
    cx = 4.9 + (k % 2) * 4.0
    cy = 3.75 + (k // 2) * 1.05
    box(s, cx, cy, 3.8, 0.88, [[(n, {"bold": True, "size": 16, "color": TEAL})], [(r, {"size": 13, "color": GRAY})]],
        fill=TEAL_LIGHT, line=None, align=PP_ALIGN.LEFT, margin=0.18, space_after=1)
textbox(s, 4.9, 6.15, 1.5, 0.4, ["Prototype:"], size=14, color=GRAY, bold=True)
textbox(s, 6.3, 6.15, 5.2, 0.4, [PROTOTYPE_URL], size=14, color=TEAL, bold=True)
textbox(s, 4.9, 6.55, 6.5, 0.4, ["Công khai, không cần tài khoản"], size=12, color=GRAY)
if QR_PNG.exists():
    s.shapes.add_picture(str(QR_PNG), Inches(11.85), Inches(5.85), Inches(1.1), Inches(1.1))
s.notes_slide.notes_text_frame.text = (
    "Tài · 20 giây\n"
    "Kính thưa Ban Giám khảo, chúng em là đội AQ2026-064, Ngôi nhà Hoa Hồng. Chúng em trình bày "
    "SmartAudit-Quantum: công cụ đối chiếu lời văn trong báo cáo thường niên với số liệu báo cáo tài chính "
    "đã kiểm toán. Mỗi phát hiện đều chỉ tới đúng ô bảng làm bằng chứng.\n\n"
    f"Mã QR góc phải dẫn tới prototype: {PROTOTYPE_URL}")

# ---------------------------------------------------------------- slide 2
s = new_slide("Lời văn phải khớp số liệu đã kiểm toán, nhưng hiện vẫn đối chiếu bằng mắt",
              notes=(
                  "Tài · 45 giây\n"
                  "Đây là một câu có thật trong báo cáo thường niên 2022 của Thế Giới Di Động: doanh thu thuần hơn "
                  "133.400 NGÀN TỶ đồng. Báo cáo tài chính kiểm toán ghi 133.405 TỶ. Lỗi nhỏ, nhưng đúng là loại lỗi "
                  "chuẩn mực kiểm toán 720 yêu cầu kiểm toán viên tìm khi đọc báo cáo thường niên. Với hơn 700 doanh "
                  "nghiệp niêm yết, việc này vẫn làm bằng mắt, trong khi gần 68% hành vi bị xử phạt năm 2025 là lỗi "
                  "công bố thông tin. Chúng em tự động hoá bước sàng lọc này.\n\n"
                  "Lưu ý: Nguyên kiểm tay lại ô Mã 10 (BCTC hợp nhất MWG 2022) trước khi trình bày. Không nói 68% là "
                  "mâu thuẫn lời văn–số liệu (xem câu hỏi Q2)."),
              source="Nguồn: BCTN MWG 2022 tr.7; BCTC hợp nhất MWG 2022 đã kiểm toán (TiniX). SSC, HOSE, HNX (2025); "
                     "Vietstock tổng hợp từ UBCKNN (số liệu đến 19/12/2025).")
box(s, 0.6, 1.75, 5.2, 2.55, None, fill=TEAL_LIGHT, line=None)
textbox(s, 0.85, 1.9, 4.8, 0.4, ["BÁO CÁO THƯỜNG NIÊN · MWG 2022, tr.7"], size=12, color=TEAL, bold=True)
textbox(s, 0.85, 2.35, 4.8, 1.8,
        [[("“…doanh thu thuần hơn 133.400 ", {}), ("ngàn tỷ", {"bold": True, "color": GOLD}),
          (" đồng…”", {})]], size=24, color=INK, line_spacing=1.1)
box(s, 7.55, 1.75, 5.2, 2.55, None, fill=GRAY_LIGHT, line=None)
textbox(s, 7.8, 1.9, 4.8, 0.4, ["BCTC ĐÃ KIỂM TOÁN · Mã số 10"], size=12, color=TEAL, bold=True)
textbox(s, 7.8, 2.35, 4.8, 0.5, ["Doanh thu thuần"], size=16, color=GRAY)
textbox(s, 7.8, 2.8, 4.8, 0.8, [[("133.404,8 ", {"bold": True}), ("tỷ", {"bold": True, "color": GOLD}),
                                 (" đồng", {"bold": True})]], size=30, color=INK)
arrow(s, 5.9, 3.02, 7.45, 3.02, color=RED, width=2.5)
box(s, 5.95, 3.25, 1.5, 0.75, ["✗ lệch", "1.000 lần"], fill=RED_LIGHT, line=None, size=13, color=RED, bold=True,
    space_after=0)
facts = [("~702", "doanh nghiệp niêm yết trên HOSE và HNX"),
         ("VSA 720", "kiểm toán viên phải đọc “thông tin khác” để tìm điểm không nhất quán trọng yếu"),
         ("≈ 68%", "hành vi bị xử phạt năm 2025 là lỗi công bố thông tin")]
for k, (big, small) in enumerate(facts):
    fx = 0.6 + k * 4.1
    box(s, fx, 4.6, 3.95, 1.85, None, fill=WHITE, line=LINE)
    textbox(s, fx + 0.2, 4.72, 3.6, 0.65, [big], size=28, color=TEAL, bold=True)
    textbox(s, fx + 0.2, 5.38, 3.6, 1.0, [small], size=14, color=INK)

# ---------------------------------------------------------------- slide 3
s = new_slide("Với công cụ kiểm toán, cáo buộc oan đắt hơn bỏ sót",
              notes=(
                  "Nguyên · 35 giây\n"
                  "Chúng em đặt một yêu cầu lên trên hết: gắn cờ oan cho doanh nghiệp niêm yết còn tệ hơn bỏ sót, vì "
                  "kiểm toán viên mất niềm tin ngay lần dùng đầu tiên. Vì vậy hệ thống chỉ có ba phán quyết, và không "
                  "chắc thì nói 'chưa kiểm chứng được' kèm lý do. Phán quyết nào cũng có vết minh chứng để người dùng "
                  "tự kiểm lại: câu gốc, Mã số, ô bảng, phép tính. Hệ thống không bao giờ kết luận gian lận."))
cards = [("✓", "Nhất quán", "Mọi vế kiểm được đều khớp BCTC trong ngưỡng làm tròn", GREEN, GREEN_LIGHT),
         ("✗", "Cần xem xét", "Nhãn công khai thay cho “mâu thuẫn”, luôn kèm mức lệch", RED, RED_LIGHT),
         ("?", "Chưa kiểm chứng được", "Không đủ căn cứ thì im lặng, luôn kèm lý do", GRAYV, GRAY_LIGHT)]
for k, (sym, name, desc, c, cl) in enumerate(cards):
    cx = 0.6 + k * 4.1
    box(s, cx, 1.75, 3.95, 2.25, None, fill=cl, line=None)
    textbox(s, cx + 0.25, 1.85, 1.0, 0.9, [sym], size=40, color=c, bold=True)
    textbox(s, cx + 0.85, 1.98, 3.0, 0.65, [name], size=17, color=c, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx + 0.25, 2.8, 3.5, 1.1, [desc], size=15, color=INK)
textbox(s, 0.6, 4.25, 12, 0.4, ["Vết minh chứng đi kèm mọi phán quyết"], size=15, color=TEAL, bold=True)
chain = ["Câu gốc\n(trang BCTN)", "Mã số\nThông tư 200", "Ô bảng\n(trang BCTC)", "Phép tính\nvà ngưỡng làm tròn"]
for k, t in enumerate(chain):
    cx = 0.6 + k * 3.15
    box(s, cx, 4.75, 2.65, 0.95, t.split("\n"), fill=WHITE, line=TEAL, size=15, color=INK, line_w=1.5,
        space_after=0)
    if k < 3:
        arrow(s, cx + 2.68, 5.22, cx + 3.12, 5.22)
box(s, 0.6, 5.95, 12.13, 0.6, [[("Không kết luận gian lận. ", {"bold": True, "color": GOLD}),
                                ("Banner “không phải kết luận kiểm toán”; kiểm toán viên là người quyết định.", {})]],
    fill=GOLD_LIGHT, line=None, size=16)

# ---------------------------------------------------------------- slide 4
s = new_slide("Hai luồng gặp nhau tại Mã số: đối chiếu thành phép tra cứu kiểm chứng được",
              notes=(
                  "Hùng · 45 giây\n"
                  "Hai luồng chạy độc lập. Luồng lời văn bóc chữ báo cáo thường niên theo cột và trích khẳng định có "
                  "chỉ tiêu, con số, xu hướng, kỳ. Luồng số liệu bóc bảng báo cáo tài chính theo Mã số Thông tư 200. "
                  "Hai luồng gặp nhau ở ontology khoản mục: 'doanh thu thuần' luôn tra về Mã số 10, nên mỗi khẳng định "
                  "nối tới đúng một ô, không đoán gần đúng. Sau đó hệ thống kiểm ba chiều: con số, hướng tăng giảm, và "
                  "nhận định định tính quy về tỷ lệ, ví dụ 'kiểm soát chi phí' quy về chi phí trên doanh thu. Lượng tử "
                  "chỉ được thử ở một nhánh phụ, nét đứt trên sơ đồ; Phong sẽ trình bày."))
textbox(s, 0.6, 1.6, 3.6, 0.35, ["LỜI VĂN"], size=12, color=GOLD, bold=True, align=PP_ALIGN.CENTER)
textbox(s, 9.13, 1.6, 3.6, 0.35, ["SỐ LIỆU"], size=12, color=GOLD, bold=True, align=PP_ALIGN.CENTER)
left = [["Báo cáo thường niên (PDF)"], ["Bóc chữ theo cột"], ["Trích khẳng định", "chỉ tiêu · số · hướng · kỳ"]]
right = [["BCTC đã kiểm toán"], ["Bóc bảng theo Mã số"], ["Bảng Mã số → giá trị", "năm nay, năm trước"]]
for k in range(3):
    y = 1.98 + k * 0.92
    box(s, 0.6, y, 3.6, 0.72, left[k], fill=WHITE, line=TEAL, size=14, line_w=1.5, space_after=0)
    box(s, 9.13, y, 3.6, 0.72, right[k], fill=WHITE, line=TEAL, size=14, line_w=1.5, space_after=0)
    if k < 2:
        arrow(s, 2.4, y + 0.73, 2.4, y + 0.9)
        arrow(s, 10.93, y + 0.73, 10.93, y + 0.9)
box(s, 4.6, 3.82, 4.13, 0.72, [[("Ontology khoản mục · ", {"bold": True}), ("Mã số", {"bold": True, "color": GOLD})]],
    fill=TEAL, line=None, size=17, color=WHITE)
arrow(s, 4.22, 4.18, 4.57, 4.18, width=2.0)
arrow(s, 9.11, 4.18, 8.76, 4.18, width=2.0)
box(s, 4.6, 4.8, 4.13, 0.72, ["Đối chiếu 3 chiều", "con số · hướng · định tính"], fill=TEAL_LIGHT, line=None,
    size=15, bold=True, color=TEAL, space_after=0)
arrow(s, 6.665, 4.56, 6.665, 4.78)
box(s, 4.6, 5.78, 4.13, 0.72, ["Phán quyết + vết minh chứng"], fill=GOLD_LIGHT, line=GOLD, size=15, bold=True,
    color=INK, line_w=1.25)
arrow(s, 6.665, 5.54, 6.665, 5.76)
box(s, 9.13, 5.0, 3.6, 1.3, ["QKA (thử nghiệm, tháo rời được)", "khớp tên khoản mục khi bảng thiếu cột Mã số"],
    fill=WHITE, line=GRAY, dash=True, size=13, color=GRAY)
arrow(s, 9.1, 5.25, 8.76, 4.5, color=GRAY, dash=True, width=1.25)
box(s, 0.6, 5.0, 3.6, 1.3, ["Neo bằng Mã số: không đoán gần đúng,", "mỗi khẳng định nối tới đúng một ô"],
    fill=GRAY_LIGHT, line=None, size=13, color=INK)

# ---------------------------------------------------------------- slide 5
s = new_slide("Dữ liệu thật của 16 doanh nghiệp niêm yết, từ nguồn có giấy phép",
              notes=(
                  "Nguyên · 35 giây\n"
                  "Hai nguồn độc lập: báo cáo tài chính kiểm toán trong bộ dữ liệu mở TiniX, và báo cáo thường niên PDF "
                  "công khai, của 16 mã giai đoạn 2018–2024. Hệ thống bóc được bảng ở 337 trên 338 báo cáo tài chính. "
                  "Sau khi vá, 73 cặp báo cáo thường niên – báo cáo tài chính cùng năm được đưa vào đối chiếu, tăng từ 66 "
                  "của bản tháng 9; bản scan bị loại và tính vào độ phủ, không giấu đi. Số khẳng định đưa vào đối chiếu "
                  "là 391, so với 695 ở bản tháng 9, sau đợt vá lọc phạm vi, trộn cột và câu không phải kết quả. "
                  "Ba ngân hàng dùng biểu mẫu Thông tư 49 nên nằm ngoài phạm vi. Không có dữ liệu cá nhân.\n\n"
                  "Hùng xác nhận lại cách giải thích mức giảm 695 → 391 trước khi nói."),
              source="Nguồn: TiniX (HuggingFace, CC-BY-NC-4.0); BCTN PDF công khai, nguồn ghi trong NOTICE. Pipeline: bản 21/09 → bản vá 19/11.")
rows5 = [("338", "BCTC đã kiểm toán, bộ TiniX (giấy phép CC-BY-NC-4.0)", "337", "bóc được bảng theo Mã số"),
         ("93", "báo cáo thường niên PDF công khai của 16 mã, 2018–2024", "73",
          "cặp BCTN–BCTC đưa vào đối chiếu (bản 21/09: 66); bản scan bị loại"),
         ("695", "khẳng định trích ra ở bản 21/09", "391",
          "khẳng định ở bản vá 19/11 (lọc phạm vi, trộn cột, câu không phải kết quả)")]
for k, (a, at, b, bt) in enumerate(rows5):
    y = 1.8 + k * 1.45
    box(s, 0.6, y, 5.3, 1.2, None, fill=TEAL_LIGHT, line=None)
    textbox(s, 0.8, y + 0.12, 1.5, 0.95, [a], size=34, color=TEAL, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 2.3, y + 0.12, 3.5, 0.95, [at], size=15, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    arrow(s, 6.0, y + 0.6, 6.75, y + 0.6, width=2.25)
    box(s, 6.85, y, 5.88, 1.2, None, fill=WHITE, line=TEAL, line_w=1.25)
    textbox(s, 7.05, y + 0.12, 1.5, 0.95, [b], size=34, color=TEAL, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 8.6, y + 0.12, 4.0, 0.95, [bt], size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)
box(s, 0.6, 6.15, 12.13, 0.45, ["3 ngân hàng (Thông tư 49) ngoài phạm vi · chỉ dùng tài liệu bắt buộc công bố · "
                                 "không có dữ liệu cá nhân"],
    fill=GOLD_LIGHT, line=None, size=14)

# ---------------------------------------------------------------- slide 6
s = new_slide("Chất lượng đo bằng hai số: cờ oan trên dữ liệu thật, recall trên lỗi chèn có kiểm soát",
              notes=(
                  "Nguyên · 35 giây\n"
                  "Doanh nghiệp lớn hiếm khi viết sai số đã kiểm toán, nên công cụ tốt phải gần như im lặng. Vì vậy "
                  "chúng em đo bằng hai số. Thứ nhất, trên dữ liệu thật: precision và số cờ oan, với 300 cặp được hai tác "
                  "tử AI gán nhãn mù và độc lập. Hai bên đồng thuận 93,7%, kappa 0,86; 19 dòng bất đồng được phân xử. "
                  "Chúng em gọi đó là nhãn bạc, vì chưa phải nhãn của người. Nhãn cuối chỉ có 7 mâu thuẫn thật trong 300 "
                  "cặp. Thứ hai, để đo khả năng bắt lỗi: lấy câu đúng, sửa có chủ đích, rồi xem hệ thống bắt được bao "
                  "nhiêu, kèm câu đối chứng không sửa để đo báo động giả. Đây là dữ liệu tổng hợp và được báo cáo riêng."),
              source="Nguồn: báo cáo mục 07 (evaluate.py); hướng dẫn gán nhãn docs/gan-nhan/huong-dan-gan-nhan.md.")
for k, (head, hc, items) in enumerate([
        ("①  Dữ liệu thật  →  precision, cờ oan", TEAL,
         ["300 cặp khẳng định – ô bảng, lấy mẫu phân tầng",
          [("Nhãn bạc: ", {"bold": True}), ("hai tác tử AI gán mù, độc lập", {})],
          "Đồng thuận 93,7%, kappa 0,86; 19 dòng phân xử",
          "Nhãn cuối: 7 mâu thuẫn · 84 nhất quán · 209 không kiểm chứng được"]),
        ("②  Lỗi chèn có kiểm soát  →  recall", GOLD,
         ["420 câu nhất quán bị sửa có chủ đích",
          "Đổi giá trị, đổi tỷ lệ, đảo hướng, “kiểm soát chi phí”",
          "122 câu đối chứng không sửa, đo báo động giả",
          [("Dữ liệu tổng hợp: ", {"bold": True}), ("báo cáo riêng, không trộn", {})]])]):
    cx = 0.6 + k * 6.2
    box(s, cx, 1.75, 5.93, 0.62, [head], fill=hc, line=None, size=17, bold=True, color=WHITE,
        align=PP_ALIGN.LEFT, margin=0.2)
    box(s, cx, 2.37, 5.93, 3.0, None, fill=TEAL_LIGHT if k == 0 else GOLD_LIGHT, line=None)
    textbox(s, cx + 0.25, 2.55, 5.5, 2.75, items, size=16, color=INK, bullet="▪", space_after=7)
box(s, 0.6, 5.62, 12.13, 0.85,
    [[("Vì sao cần hai số: ", {"bold": True, "color": TEAL}),
      ("doanh nghiệp lớn hiếm khi viết sai số liệu đã kiểm toán (ước tính khoảng 2% khẳng định trong mẫu), "
       "nên công cụ tốt phải gần như im lặng trên dữ liệu thật.", {})]],
    fill=WHITE, line=LINE, size=15, align=PP_ALIGN.LEFT, margin=0.2)

# ---------------------------------------------------------------- slide 7
s = new_slide("Cờ oan giảm mạnh, lỗi chèn bắt được 82,6%, nhưng precision trên dữ liệu thật chưa đạt mục tiêu 80%",
              notes=(
                  "Hùng · 45 giây\n"
                  "Chúng em đưa cả số tốt lẫn số chưa đạt. Bản tháng 9 gắn 141 cờ, chỉ 4 cờ đúng, precision 2,8%. Sau khi "
                  "vá còn 35 cờ; số cờ oan ước tính trên toàn bộ khẳng định giảm từ khoảng 137 xuống khoảng 23, tức giảm "
                  "khoảng 83%. Nhưng 21 cờ trong mẫu không cờ nào là mâu thuẫn thật: precision 0%, khoảng tin cậy 0 đến "
                  "15,5%. Mục tiêu 80% chưa đạt. Lý do: mâu thuẫn thật rất hiếm, khoảng 2% khẳng định, và cả 7 ca đều là "
                  "lỗi trình bày ở tỷ số hoặc cơ cấu, như hệ số nợ trên vốn chủ, loại hệ thống chưa tính. Bản cũ 'bắt' được "
                  "4 ca chỉ nhờ so nhầm tỷ số với khoản mục tiền; bản vá đã chặn phép so nhầm đó. Bước tiếp theo là thêm phép "
                  "tính tỷ số cơ cấu. Trên tập chèn lỗi, dữ liệu tổng hợp, hệ thống bắt 82,6%, kém nhất ở câu 'kiểm soát chi "
                  "phí', và không báo động giả trên 122 câu đối chứng. Thay vì kể, chúng em mở đúng link đã nộp. Mời Phong."),
              source="Nhãn bạc (hai tác tử AI, mù, độc lập). Tập chèn lỗi là dữ liệu tổng hợp. KTC95: khoảng tin cậy 95%. "
                     "Nguồn: evaluate.py.")
box(s, 0.6, 1.65, 5.9, 0.45, ["Dữ liệu thật · 300 cặp có nhãn bạc"], fill=TEAL, line=None, size=15, bold=True,
    color=WHITE, align=PP_ALIGN.LEFT, margin=0.2)
box(s, 0.6, 2.18, 5.9, 1.62, None, fill=TEAL_LIGHT, line=None)
textbox(s, 0.85, 2.25, 5.5, 0.6, ["141 → 35 cờ"], size=28, color=TEAL, bold=True)
textbox(s, 0.85, 2.88, 5.5, 0.9, ["“cần xem xét”, bản 21/09 → bản vá 19/11. Cờ oan ước tính trên toàn bộ khẳng định: "
                                  "~137 → ~23 (giảm ~83%)"], size=13, color=INK)
box(s, 0.6, 3.92, 5.9, 1.68, None, fill=RED_LIGHT, line=None)
textbox(s, 0.85, 3.99, 5.5, 0.6, ["Precision 2,8% → 0%"], size=28, color=RED, bold=True)
textbox(s, 0.85, 4.62, 5.5, 0.95, ["4/141 (KTC95 1,1–7,1%) → 0/21 (KTC95 0–15,5%).",
                                   [("Mục tiêu 80%: chưa đạt.", {"bold": True, "color": RED})]], size=13, color=INK,
        space_after=2)
box(s, 6.83, 1.65, 5.9, 0.45, ["Lỗi chèn có kiểm soát · dữ liệu tổng hợp"], fill=GOLD, line=None, size=15,
    bold=True, color=WHITE, align=PP_ALIGN.LEFT, margin=0.2)
bars = [("Đổi giá trị", 86.0), ("Đổi tỷ lệ", 87.0), ("Đảo hướng", 71.0), ("“Kiểm soát chi phí”", 47.0),
        ("Tổng 347/420", 82.6)]
bx, bw = 9.15, 2.75
for k, (lab, v) in enumerate(bars):
    y = 2.22 + k * 0.6
    textbox(s, 6.83, y, 2.25, 0.5, [lab], size=14, color=INK, bold=lab.startswith("Tổng"), anchor=MSO_ANCHOR.MIDDLE,
            align=PP_ALIGN.RIGHT)
    rect(s, bx, y + 0.09, bw, 0.32, GRAY_LIGHT)
    rect(s, bx, y + 0.09, bw * v / 100.0, 0.32, GOLD if lab.startswith("Tổng") else TEAL)
    vs = ("%.1f" % v).replace(".", ",") if v != int(v) else "%d" % v
    textbox(s, bx + bw * v / 100.0 + 0.06, y, 0.95, 0.5, [vs + "%"], size=14, color=INK, bold=True,
            anchor=MSO_ANCHOR.MIDDLE)
box(s, 6.83, 5.25, 5.9, 0.35, [[("0/122", {"bold": True, "color": GREEN}),
                                (" báo động giả trên câu đối chứng không sửa", {})]],
    fill=GREEN_LIGHT, line=None, size=13, align=PP_ALIGN.LEFT, margin=0.15)
box(s, 0.6, 5.75, 12.13, 0.85,
    [[("Vì sao chưa đạt: ", {"bold": True, "color": TEAL}),
      ("mâu thuẫn thật rất hiếm (~2% khẳng định); cả 7 ca đều là lỗi trình bày ở tỷ số, cơ cấu (Nợ/VCSH, tỷ trọng "
       "tài sản) — loại hệ thống chưa tính. ", {}),
      ("Bước tiếp: thêm phép tính tỷ số cơ cấu.", {"bold": True})]],
    fill=GRAY_LIGHT, line=None, size=14, align=PP_ALIGN.LEFT, margin=0.2)

# ---------------------------------------------------------------- slide 8
s = new_slide("Demo trực tiếp: lõi Python của pipeline chạy ngay trong trình duyệt, không cần server",
              notes=(
                  "Phong · 140 giây — kịch bản chi tiết ở docs/slide/dan-y-slide.md, mục 2.\n"
                  "0:00–0:15 Trang Tổng quan: 'Đây là link đã nộp, không đăng nhập. Dashboard tĩnh 7 trang, số trên trang là "
                  "số đo thật vừa trình bày.'\n"
                  "0:15–0:55 Trang Kiểm tra khẳng định, chọn VNM 2024, dán: 'Doanh thu thuần đạt 61.783 tỷ đồng, tăng 2,3% so "
                  "với năm trước.' → Nhất quán, Mã số 10, trang 10. Nói: 'Phần này chạy đúng mã Python của pipeline ngay trong "
                  "trình duyệt bằng Pyodide, mỗi câu 2 đến 11 mili giây sau khi nạp.'\n"
                  "0:55–1:30 Sửa thành '65.000 tỷ đồng, tăng 7,6%' → Cần xem xét, lệch 5,2% và 5,26 điểm. Nói rõ: 'Đây là câu "
                  "em sửa có chủ đích để minh hoạ. Vết minh chứng giữ nguyên, chỉ phán quyết đổi.'\n"
                  "1:30–2:05 Dán câu về Angkormilk ('doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%') → không kết luận: "
                  "'Đây chính là ví dụ Vòng 1 của chúng em, hoá ra nói về công ty con. Bản vá trả về không kết luận thay vì "
                  "cáo buộc.'\n"
                  "2:05–2:20 (nếu còn giờ) câu thật FPT 2022 tr.52 'Doanh thu đạt 44.010 tỷ đồng, tăng 23,4%' → nhất quán. "
                  "Quay về slide 9.\n"
                  "Dự phòng: trang không phản hồi sau 10 giây thì chuyển sang bản chạy tại máy, chỉ nói một câu."),
              source="Mở trước trang “Kiểm tra khẳng định” vì Pyodide tải khoảng 10 MB lần đầu. Dự phòng: bản chạy tại máy, cùng dữ liệu.")
textbox(s, 0.6, 1.62, 3.2, 0.35, ["Link đã nộp"], size=13, color=GRAY, bold=True)
textbox(s, 0.6, 1.95, 7.6, 0.55, [PROTOTYPE_URL], size=24, color=TEAL, bold=True)
textbox(s, 0.6, 2.5, 7.6, 0.4, ["Công khai · không cần tài khoản · dashboard tĩnh 7 trang trên kết quả thật"], size=13,
        color=GRAY)
box(s, 8.6, 1.7, 4.13, 1.1, [[("2–11 ms", {"bold": True, "size": 24, "color": TEAL})],
                             [("mỗi câu, sau khi nạp Pyodide", {"size": 13})]],
    fill=TEAL_LIGHT, line=None, space_after=0)
flow = ["Trang tĩnh\n(JSON kết quả thật)", "Pyodide nạp\nmã Python pipeline", "Trích\nkhẳng định",
        "Tra Mã số\nvà đối chiếu", "Phán quyết +\nvết minh chứng"]
for k, t in enumerate(flow):
    cx = 0.6 + k * 2.47
    box(s, cx, 3.05, 2.1, 0.9, t.split("\n"), fill=TEAL if k == 1 else WHITE, line=TEAL,
        color=WHITE if k == 1 else INK, size=13, bold=(k == 1), line_w=1.5, space_after=0)
    if k < 4:
        arrow(s, cx + 2.13, 3.5, cx + 2.44, 3.5)
steps = [("1", "Câu nhập vào · VNM 2024", "“Doanh thu thuần đạt 61.783 tỷ đồng, tăng 2,3% so với năm trước.”",
          "✓ Nhất quán · Mã số 10, trang 10", GREEN, GREEN_LIGHT),
         ("2", "Câu đã sửa có chủ đích", "“…65.000 tỷ đồng, tăng 7,6%…” (minh hoạ)",
          "✗ Cần xem xét · lệch 5,2% và 5,26 điểm", RED, RED_LIGHT),
         ("3", "Câu về công ty con", "Angkormilk: “tăng lần lượt 7,6% và 48,4%”",
          "? Không kết luận", GRAYV, GRAY_LIGHT)]
for k, (n, a, q, v, c, cl) in enumerate(steps):
    cx = 0.6 + k * 4.1
    box(s, cx, 4.2, 3.95, 2.38, None, fill=cl, line=None)
    box(s, cx + 0.2, 4.33, 0.5, 0.5, [n], fill=c, line=None, size=16, bold=True, color=WHITE,
        shape=MSO_SHAPE.OVAL, margin=0.02)
    textbox(s, cx + 0.85, 4.33, 3.0, 0.5, [a], size=15, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx + 0.25, 4.95, 3.55, 0.95, [q], size=13, color=INK)
    textbox(s, cx + 0.25, 5.92, 3.6, 0.6, [v], size=13, color=c, bold=True)

# ---------------------------------------------------------------- slide 9
s = new_slide("Lượng tử thua cổ điển — và chúng em công bố đúng như vậy",
              notes=(
                  "Phong · 45 giây\n"
                  "Lượng tử được thử ở đúng một chỗ: khi bảng không có cột Mã số, phải đoán tên khoản mục thuộc mã nào. "
                  "Nhãn sinh tự động từ các bảng có Mã số, 282 tên khác nhau. Chúng em huấn luyện kernel lượng tử 8 qubit "
                  "bằng QKA trên mô phỏng, và so trên cùng cách chia. QKA đạt 0,84, hơn rõ kernel cố định 0,73, nhưng THUA "
                  "SVM-RBF 0,91 ở cả 5 phần, và huấn luyện chậm hơn khoảng 260 lần. Chúng em công bố đúng như vậy, như đã "
                  "cam kết. Giá trị nằm ở chỗ câu hỏi 'lượng tử có giúp không' được trả lời bằng thực nghiệm có đối chứng, "
                  "và chính thí nghiệm này chỉ ra một cải tiến cổ điển: SVM hơn cách rapidfuzz hệ thống đang dùng. Lớp "
                  "lượng tử tháo rời được.\n\n"
                  "Nếu bị hỏi: rapidfuzz ở ngưỡng 88 chỉ trả lời 49,6% số tên, đúng 98,4% trong số đó; đổi sang SVM phải "
                  "giữ cơ chế 'không chắc thì im lặng'. Chi tiết ở slide dự phòng D2."),
              source="Nguồn: docs/quantum-poc.md; results/qka_results.json (12/11/2026). Trung bình ± độ lệch chuẩn qua 5 phần.")
textbox(s, 0.6, 1.62, 7.4, 0.7,
        ["Bài toán: tên khoản mục → Mã số khi bảng thiếu cột Mã số · 282 tên · 8 lớp · 8 qubit · statevector · "
         "5 phần, seed 42"], size=13, color=GRAY)
rows9 = [["Phương pháp", "Accuracy", "Macro-F1", "Huấn luyện"],
         ["rapidfuzz (hệ thống đang dùng)", "0,812 ± 0,030", "0,801 ± 0,047", "0 s"],
         ["SVM-RBF, 8 chiều", "0,911 ± 0,051", "0,904 ± 0,062", "0,8 s"],
         ["QSVM, kernel ZZ cố định", "0,734 ± 0,055", "0,722 ± 0,064", "1,5 s"],
         ["QSVM + QKA", "0,840 ± 0,048", "0,829 ± 0,062", "216,7 s"]]
table(s, 0.6, 2.4, 7.4, rows9, [2.95, 1.6, 1.6, 1.25], row_h=0.62, size=14,
      highlight={2: GREEN_LIGHT, 4: GOLD_LIGHT}, bold_rows=(2,), aligns=["l", "c", "c", "c"])
textbox(s, 0.6, 5.62, 7.4, 0.8, ["Thời gian huấn luyện tính cho mỗi phần. QKA thua SVM-RBF ở 5/5 phần. "
                                 "Không tuyên bố lợi thế lượng tử."], size=13, color=GRAY)
box(s, 8.4, 1.62, 4.33, 4.85, None, fill=TEAL_LIGHT, line=None)
textbox(s, 8.65, 1.75, 3.9, 0.45, ["Vì sao vẫn có giá trị"], size=17, color=TEAL, bold=True)
textbox(s, 8.65, 2.3, 3.95, 4.1,
        ["Trả lời “lượng tử có giúp không” bằng thí nghiệm có đối chứng, cùng cách chia",
         "QKA hơn kernel cố định ở 5/5 phần: 0,734 → 0,840",
         "Dẫn tới cải tiến cổ điển: SVM 0,911 > rapidfuzz 0,812",
         "Tháo rời được: cắm qua đúng một ma trận kernel"], size=15, color=INK, bullet="▪", space_after=9)

# ---------------------------------------------------------------- slide 10
s = new_slide("Hệ thống tự biết giới hạn của mình",
              notes=(
                  "Hùng · 30 giây\n"
                  "Chúng em nói rõ những gì chưa làm. Precision trên dữ liệu thật chưa đạt 80%, vì hệ thống chưa tính các "
                  "tỷ số cơ cấu như nợ trên vốn chủ, đúng loại mà cả 7 mâu thuẫn thật rơi vào. Ngân hàng và bản scan nằm "
                  "ngoài phạm vi. Câu về bộ phận hay công ty con được trả không kết luận. Nhãn đánh giá mới là nhãn bạc do "
                  "AI gán, và chưa thử nghiệm với kiểm toán viên. Phần trích khẳng định vẫn là bộ luật; mô hình học chỉ vào "
                  "khi thắng bộ luật trên cùng tập test."))
done = ["Pipeline trên dữ liệu thật: 73 cặp báo cáo, 391 khẳng định, 77 giây",
        "147 phép kiểm tự động (171 khi có môi trường lượng tử)",
        "300 cặp nhãn bạc, kappa 0,86",
        "Tập chèn lỗi: recall 82,6%, 0/122 báo động giả",
        "QKA có hai đường cơ sở cổ điển",
        "Dashboard tĩnh 7 trang + Pyodide, không server"]
todo = ["Precision ≥ 80% trên dữ liệu thật: chưa đạt",
        "Tỷ số cơ cấu (Nợ/VCSH, tỷ trọng tài sản): chưa tính",
        "Ngân hàng (Thông tư 49), BCTN bản scan: ngoài phạm vi",
        "Câu về bộ phận, công ty con: không kết luận",
        "Nhãn của người; thử nghiệm kiểm toán viên: chưa có",
        "Trích khẳng định: bộ luật, chưa PhoBERT-Fin"]
for k, (head, items, c, cl, sym) in enumerate([("✓  Đã chạy, đã đo", done, GREEN, GREEN_LIGHT, "✓"),
                                               ("?  Chưa làm", todo, GRAYV, GRAY_LIGHT, "?")]):
    cx = 0.6 + k * 6.2
    box(s, cx, 1.75, 5.93, 0.6, [head], fill=c, line=None, size=18, bold=True, color=WHITE,
        align=PP_ALIGN.LEFT, margin=0.2)
    box(s, cx, 2.35, 5.93, 4.15, None, fill=cl, line=None)
    textbox(s, cx + 0.25, 2.55, 5.5, 3.9, items, size=16, color=INK, bullet=sym, space_after=8)

# ---------------------------------------------------------------- slide 11
s = new_slide("Chưa thử nghiệm với kiểm toán viên — quy trình đã sẵn sàng để chạy sau Vòng 2",
              notes=(
                  "Tài · 35 giây\n"
                  "Chúng em chưa thử nghiệm với kiểm toán viên, vì không kịp tổ chức trước hạn nộp, và cũng chưa có đối "
                  "tác. Quy trình đã soạn xong: mỗi người đối chiếu một doanh nghiệp bằng tay và một doanh nghiệp khác bằng "
                  "công cụ, thứ tự đảo giữa các người; chúng em đo thời gian, độ đúng và số cờ bị bác, rồi phỏng vấn mười "
                  "phút. Chúng em sẽ chạy sau Vòng 2 và báo cáo số liệu thô của từng người, không suy rộng."),
              source="Quy trình, thư mời, phiếu ghi, mẫu biên bản: docs/thu-nghiem-ktv/.")
box(s, 0.6, 1.75, 4.1, 2.6, None, fill=RED_LIGHT, line=None)
textbox(s, 0.85, 1.88, 3.7, 0.45, ["Nói thẳng"], size=17, color=RED, bold=True)
textbox(s, 0.85, 2.4, 3.7, 1.9, ["Chưa thử nghiệm: không kịp trước hạn nộp",
                                 "Chưa có đối tác, chưa có thư bày tỏ quan tâm"], size=16, color=INK, bullet="▪",
        space_after=10)
steps11 = ["Xin đồng ý", "Lượt A\nlàm tay\nDN thứ nhất", "Lượt B\ndùng công cụ\nDN thứ hai",
           "Phỏng vấn\n10 phút"]
for k, t in enumerate(steps11):
    cx = 5.1 + k * 1.95
    box(s, cx, 1.75, 1.65, 1.5, t.split("\n"), fill=TEAL if k in (1, 2) else WHITE, line=TEAL,
        color=WHITE if k in (1, 2) else INK, size=13, bold=(k in (1, 2)), line_w=1.5, space_after=0)
    if k < 3:
        arrow(s, cx + 1.67, 2.5, cx + 1.93, 2.5)
textbox(s, 5.1, 3.4, 7.6, 0.7, ["DN: doanh nghiệp. Thứ tự lượt A/B và cặp doanh nghiệp được đảo giữa các người "
                                "tham gia."], size=13, color=GRAY)
box(s, 0.6, 4.6, 12.13, 1.9, None, fill=TEAL_LIGHT, line=None)
textbox(s, 0.85, 4.72, 11.6, 0.45, ["Thiết kế đã soạn"], size=16, color=TEAL, bold=True)
textbox(s, 0.85, 5.18, 5.7, 1.3, ["2–3 kiểm toán viên hoặc giảng viên kiểm toán",
                                  "Đo: thời gian mỗi khẳng định, độ đúng, số cờ bị bác"], size=15, color=INK,
        bullet="▪", space_after=6)
textbox(s, 6.75, 5.18, 5.8, 1.3, ["Báo cáo số liệu thô từng người, không suy rộng",
                                  "Người tham gia chỉ dùng thử và nhận xét"], size=15, color=INK, bullet="▪",
        space_after=6)

# ---------------------------------------------------------------- slide 12
s = new_slide("Hạ tầng gần 0 đồng; chi phí thật là thời gian kiểm toán viên xử lý cờ",
              notes=(
                  "Tài · 35 giây\n"
                  "Toàn bộ prototype là trang tĩnh; chức năng kiểm tra khẳng định chạy lõi Python ngay trong trình duyệt, "
                  "nên không có server để trả tiền, để ngủ hay để sập. Pipeline chạy offline trên CPU, 77 giây cho 93 báo "
                  "cáo thường niên khi đã bóc chữ, không gửi dữ liệu ra ngoài, nên công ty kiểm toán cài nội bộ được. Chi phí "
                  "thật là thời gian kiểm toán viên xử lý cờ, vì vậy giảm cờ oan là việc quan trọng nhất. Lộ trình sau cuộc "
                  "thi: thử nghiệm với kiểm toán viên, có nhãn của người, rồi mở rộng độ phủ.\n\n"
                  "Bản một câu khi chậm giờ: Hạ tầng gần 0 đồng; chi phí thật là thời gian xử lý cờ, nên giảm cờ oan quyết "
                  "định giá trị."),
              source="Giá tra ngày 12/11/2026. Thời gian pipeline: báo cáo mục 07. Ước tính 8–45 tỷ đồng/năm ở hồ sơ Vòng 1 chưa kiểm chứng.")
rows12 = [["Thành phần", "Cách chạy", "Chi phí"],
          ["Giao diện kết quả", "Trang tĩnh, gói miễn phí", "0"],
          ["“Kiểm tra khẳng định”", "Pyodide trong trình duyệt, không server", "0"],
          ["Pipeline", "Offline, CPU; 77 giây cho 93 BCTN", "0"],
          ["Con người", "Kiểm toán viên rà cờ, bảo trì ontology", "Khoản lớn nhất"]]
table(s, 0.6, 1.75, 7.6, rows12, [2.2, 3.9, 1.5], row_h=0.6, size=14, aligns=["l", "l", "c"],
      highlight={4: GOLD_LIGHT})
box(s, 8.6, 1.75, 4.13, 3.0, None, fill=TEAL_LIGHT, line=None)
textbox(s, 8.85, 1.88, 3.7, 0.45, ["Bảo mật"], size=16, color=TEAL, bold=True)
textbox(s, 8.85, 2.35, 3.7, 2.3, ["Chạy tại máy, không gửi văn bản ra ngoài",
                                  "Cài nội bộ ở công ty kiểm toán được",
                                  "Không có dữ liệu cá nhân"], size=15, color=INK, bullet="▪", space_after=8)
textbox(s, 0.6, 5.0, 6, 0.4, ["Lộ trình sau cuộc thi"], size=15, color=TEAL, bold=True)
road = ["Thử nghiệm với kiểm toán viên", "Nhãn của người", "Mở rộng: OCR, Thông tư 99", "Mô hình học (PhoBERT-Fin)"]
for k, t in enumerate(road):
    cx = 0.6 + k * 3.05
    sh = box(s, cx, 5.45, 3.0, 0.95, [t], fill=TEAL if k == 0 else WHITE, line=TEAL,
             color=WHITE if k == 0 else INK, size=14, bold=(k == 0), shape=MSO_SHAPE.CHEVRON if k else MSO_SHAPE.PENTAGON,
             line_w=1.25, margin=0.35)

# ---------------------------------------------------------------- slide 13
s = new_slide("Tóm lại: một công cụ đơn giản, chạy thật, tự biết giới hạn",
              notes=(
                  "Hùng · 25 giây\n"
                  "Tóm lại, chúng em không hứa một hệ thống làm được mọi thứ. Chúng em mang tới một công cụ chạy thật, đo "
                  "trung thực bằng hai số, công bố cả chỗ chưa đạt, và chỉ ra đúng ô bảng cho mọi kết luận. Chúng em đã dùng AI hỗ trợ và khai báo rõ "
                  "ở cuối slide; mọi phần chúng em đều giải thích được. Xin cảm ơn Ban Giám khảo, chúng em sẵn sàng nhận câu hỏi."))
summ = ["Chạy thật trên dữ liệu thật, link công khai, 147 phép kiểm tự động",
        "Công bố cả số tốt (cờ oan −83%, recall 82,6%) lẫn số chưa đạt (precision)",
        "Mọi phát hiện chỉ tới đúng ô bảng; không chắc thì không kết luận",
        "Lượng tử: kết quả âm công bố đầy đủ, kèm đường cơ sở"]
for k, t in enumerate(summ):
    cx = 0.6 + (k % 2) * 6.2
    cy = 1.75 + (k // 2) * 1.12
    box(s, cx, cy, 5.93, 0.95, None, fill=TEAL_LIGHT, line=None)
    textbox(s, cx + 0.2, cy + 0.1, 0.6, 0.75, ["✓"], size=24, color=GREEN, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx + 0.8, cy + 0.1, 5.0, 0.75, [t], size=16, color=INK, anchor=MSO_ANCHOR.MIDDLE)
box(s, 0.6, 4.15, 12.13, 1.95, None, fill=GOLD_LIGHT, line=GOLD, line_w=1.0)
textbox(s, 0.85, 4.27, 11.6, 0.4, ["Khai báo sử dụng công cụ AI (Thể lệ Điều 14)"], size=15, color=GOLD, bold=True)
textbox(s, 0.85, 4.72, 11.65, 1.75,
        ["Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập "
         "đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội "
         "thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm."],
        size=15, color=INK, line_spacing=1.12)
textbox(s, 0.6, 6.25, 12.13, 0.5, ["Xin cảm ơn Ban Giám khảo!"], size=20, color=TEAL, bold=True,
        align=PP_ALIGN.CENTER)

# ---------------------------------------------------------------- D1
s = new_slide("D1 · Số đo kiểm lại được đến từng cặp",
              notes="Hùng mở khi bị hỏi Q9 hoặc Q26. Đọc số trên dữ liệu thật trước, số tập chèn lỗi sau, và luôn nói "
                    "tập chèn lỗi là dữ liệu tổng hợp. Nói thẳng: precision chưa đạt 80%; bản cũ có 4 cờ đúng chỉ nhờ so "
                    "nhầm tỷ số với khoản mục tiền, bản vá đã chặn phép so nhầm đó.",
              source="Nhãn bạc (hai tác tử AI, gán mù, độc lập). KTC95: khoảng tin cậy 95%. Nguồn: evaluate.py.",
              backup=True)
rowsD1a = [["Dữ liệu thật", "Bản 21/09", "Bản vá 19/11"],
           ["Cặp báo cáo đối chiếu", "66", "73"],
           ["Khẳng định", "695", "391"],
           ["Cờ “cần xem xét”", "141", "35"],
           ["Precision (cờ đúng / cờ trong mẫu)", "2,8% (4/141)", "0% (0/21)"],
           ["KTC95 của precision", "1,1–7,1%", "0–15,5%"],
           ["Cờ oan ước tính, toàn bộ khẳng định", "~137", "~23"]]
table(s, 0.6, 1.7, 7.0, rowsD1a, [3.6, 1.7, 1.7], row_h=0.48, size=13, aligns=["l", "c", "c"],
      highlight={4: RED_LIGHT})
textbox(s, 0.6, 5.2, 7.0, 1.4,
        ["Nhãn bạc: đồng thuận 93,7%, kappa 0,86; 19 dòng bất đồng được phân xử; nhãn cuối 7 mâu thuẫn · 84 nhất quán "
         "· 209 không kiểm chứng được",
         "Bản cũ “bắt” 4 ca nhờ so nhầm tỷ số với khoản mục tiền; bản vá đã chặn"],
        size=13, color=INK, bullet="▪", space_after=5)
rowsD1 = [["Tập chèn lỗi (tổng hợp)", "Recall"],
          ["Đổi giá trị", "86%"], ["Đổi tỷ lệ", "87%"], ["Đảo hướng", "71%"],
          ["“Kiểm soát chi phí”", "47%"], ["Tổng", "82,6% (347/420)"], ["Báo động giả, câu đối chứng", "0/122"]]
table(s, 7.95, 1.7, 4.78, rowsD1, [2.68, 2.1], row_h=0.55, size=13, aligns=["l", "c"], bold_rows=(5,),
      highlight={5: GOLD_LIGHT}, header_fill=GOLD)

# ---------------------------------------------------------------- D2
s = new_slide("D2 · Lượng tử: thiết lập đủ để người khác chạy lại",
              notes="Phong mở khi bị hỏi Q13, Q14. Có thể chạy python scripts/run_qka.py --quick (khoảng 1 phút) nếu được yêu cầu.",
              source="Nguồn: docs/quantum-poc.md; smartaudit/quantum/; scripts/run_qka.py; results/qka_results.json.",
              backup=True)
pipe = ["TF-IDF ký tự\n2–4", "TruncatedSVD\n8 chiều", "Co giãn\nvề [0, π]", "ZZFeatureMap\n8 qubit, reps 2",
        "QKA: 16 tham số\nCOBYLA 150 lần", "SVC"]
for k, t in enumerate(pipe):
    cx = 0.6 + k * 2.07
    box(s, cx, 1.75, 1.8, 1.05, t.split("\n"), fill=TEAL if k == 4 else WHITE, line=TEAL,
        color=WHITE if k == 4 else INK, size=13, bold=(k == 4), line_w=1.25, space_after=0)
    if k < 5:
        arrow(s, cx + 1.82, 2.27, cx + 2.05, 2.27)
textbox(s, 0.6, 3.1, 6.0, 3.4,
        ["Mạch đo một ô kernel: độ sâu 65, 54 CNOT",
         "SVD giữ 53–54% phương sai",
         "Alignment huấn luyện: 0,293 → 0,511",
         "Huấn luyện 216,7 s/phần (RBF 0,82 s)",
         "Suy luận ~23 ms/mẫu (RBF 0,02 ms)"], size=15, color=INK, bullet="▪", space_after=8)
textbox(s, 6.8, 3.1, 5.95, 3.4,
        ["Kernel cố định quá “hẹp”: trung bình ngoài đường chéo 0,011",
         "Lỗi chung: đảo chiều chi/thu (mã 23 → 24)",
         "rapidfuzz ngưỡng 88: trả lời 49,6% số tên, đúng 98,4%",
         "Không làm QSVM phát hiện bất thường: chỉ 31 mẫu dương / 686 cặp"], size=15, color=INK, bullet="▪",
        space_after=8)

# ---------------------------------------------------------------- D3
s = new_slide("D3 · Những lỗi đội tự phát hiện",
              notes="Hùng và Nguyên. Kể ca VNM chủ động, như bằng chứng về quy trình tự kiểm, không đợi bị hỏi lại.",
              source="Nguồn: docs/ke-hoach-vong-2.md (mục 2, 6.1b); docs/gan-nhan/huong-dan-gan-nhan.md (ví dụ 1–2).",
              backup=True)
errs = [("Ví dụ Vòng 1 là cờ oan",
         "VNM 2024 “tăng 7,6% và 48,4%” nói về Angkormilk (công ty con ở Campuchia); hợp nhất chỉ +2,34% → làm bộ lọc phạm vi và gán nhãn mù"),
        ("Đơn vị tính",
         "36/138 BCTC phi ngân hàng (26%) ghi theo nghìn/triệu đồng, từng bị đọc thành đồng"),
        ("Mã số không duy nhất",
         "Mã 10 là doanh thu thuần trong KQKD, nhưng là biến động hàng tồn kho trong LCTT"),
        ("Cột “Thuyết minh” đọc nhầm",
         "Doanh thu FPT 2023 từng bị đọc thành 26 đồng"),
        ("Nguyên nhân cờ oan (rà sơ bộ)",
         "Phạm vi hẹp hơn hợp nhất 40% · trộn cột 17% · câu không phải kết quả 13% · câu về tỷ số 12%")]
for k, (h, d) in enumerate(errs):
    y = 1.72 + k * 0.97
    box(s, 0.6, y, 3.6, 0.82, [h], fill=TEAL_LIGHT, line=None, size=14, bold=True, color=TEAL,
        align=PP_ALIGN.LEFT, margin=0.18)
    textbox(s, 4.4, y, 8.33, 0.82, [d], size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- D4
s = new_slide("D4 · Phạm vi: hệ thống im lặng đúng chỗ",
              notes="Nguyên mở khi bị hỏi Q21, Q22 hoặc Q4.", backup=True)
scope = [("Ngân hàng (MBB, TCB, VPB)", "Biểu mẫu Thông tư 49, không dùng hệ Mã số Thông tư 200 → huy hiệu “ngoài phạm vi”, loại khỏi số đo"),
         ("BCTN bản scan", "Chưa OCR; bị loại và tính vào độ phủ. OCR sai một chữ số sẽ sinh cờ oan"),
         ("Câu về bộ phận, công ty con", "Trả “chưa kiểm chứng được”, kể cả khi thuyết minh bộ phận có số"),
         ("FPT 2018, thoái vốn", "Doanh thu −45,6% nhưng BCTN nói tăng trưởng “so sánh tương đương” → không gắn cờ"),
         ("Thông tư 99/2025/TT-BTC", "Thay Thông tư 200 từ năm tài chính 2026 → thêm bảng ánh xạ Mã số; ontology là cấu hình")]
for k, (h, d) in enumerate(scope):
    y = 1.72 + k * 0.97
    box(s, 0.6, y, 3.6, 0.82, [h], fill=GRAY_LIGHT, line=None, size=14, bold=True, color=INK,
        align=PP_ALIGN.LEFT, margin=0.18)
    textbox(s, 4.4, y, 8.33, 0.82, [d], size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- D5
s = new_slide("D5 · Tuân thủ: dữ liệu, nhãn bạc, khai báo AI",
              notes="Tài mở khi bị hỏi Q7, Q23 hoặc Q26. Câu khai báo AI phải đọc nguyên văn, trùng báo cáo mục 08 và slide 13.",
              backup=True)
for k, (h, items) in enumerate([
        ("Dữ liệu", ["TiniX theo CC-BY-NC-4.0; cuộc thi là mục đích phi thương mại",
                     "BCTN là tài liệu bắt buộc công bố; nguồn ghi trong NOTICE",
                     "Không có dữ liệu cá nhân"]),
        ("Nhãn bạc", ["Hai tác tử AI gán mù, độc lập; nhãn kèm phép tính tới ô bảng",
                      "Đồng thuận 93,7%, kappa 0,86; 19 dòng được phân xử",
                      "Chưa phải nhãn người; thiên lệch chung là có thật"])]):
    cx = 0.6 + k * 6.2
    box(s, cx, 1.75, 5.93, 0.55, [h], fill=TEAL, line=None, size=16, bold=True, color=WHITE,
        align=PP_ALIGN.LEFT, margin=0.2)
    box(s, cx, 2.3, 5.93, 2.0, None, fill=TEAL_LIGHT, line=None)
    textbox(s, cx + 0.22, 2.42, 5.5, 1.85, items, size=14, color=INK, bullet="▪", space_after=6)
box(s, 0.6, 4.55, 12.13, 1.95, None, fill=GOLD_LIGHT, line=GOLD)
textbox(s, 0.85, 4.65, 11.6, 0.4, ["Khai báo sử dụng công cụ AI (nguyên văn)"], size=14, color=GOLD, bold=True)
textbox(s, 0.85, 5.08, 11.65, 1.4,
        ["Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập "
         "đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội "
         "thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm."],
        size=14, color=INK, line_spacing=1.1)

# ---------------------------------------------------------------- lưu + kiểm placeholder
prs.save(OUT)
print("Đã lưu:", OUT, "·", len(prs.slides), "slide")
found = []
for i, sl in enumerate(prs.slides, 1):
    texts = []
    for sh in sl.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    texts.append(("slide", r.text))
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs:
                        for r in p.runs:
                            texts.append(("slide", r.text))
    if sl.has_notes_slide:
        texts.append(("notes", sl.notes_slide.notes_text_frame.text))
    for where, t in texts:
        for m in re.findall(r"⟦[^⟧]*⟧", t):
            found.append((i, where, m))
        if "⟦" in t and t.count("⟦") != t.count("⟧"):
            print("CẢNH BÁO: placeholder bị tách ở slide", i, repr(t))
print("Placeholder còn lại:")
for i, w, m in found:
    print("  slide %d (%s): %s" % (i, w, m))
