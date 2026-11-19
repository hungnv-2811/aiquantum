"""Cấu hình dùng chung: đường dẫn, danh sách mã chứng khoán, hằng số."""

from __future__ import annotations

from pathlib import Path

# ── Đường dẫn ──
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
RESULTS = ROOT / "results"

TINIX_DIR = RAW / "tinix"

# ── Nguồn dữ liệu ──
TINIX_REPO = "tinixai/ocr_annual_financials"

# ── Danh sách mã chứng khoán cho MVP ──
#
# 16 mã đã kiểm chứng có mặt trong bộ TiniX (đo ngày 07/08/2026).
# Bốn mã trong kế hoạch ban đầu — DGC, ROS, FLC, ITA — KHÔNG có trong
# dataset nên đã loại. Cần bổ sung mã thay thế cho nhóm "mẫu dương"
# (doanh nghiệp từng bị xử phạt công bố thông tin).
#
# Chỉ tải phần văn bản OCR: ~65 MB cho cả 16 mã.
# Bản PDF gốc (~2.16 GB) KHÔNG cần, vì văn bản OCR đã giữ nguyên bảng
# biểu dưới dạng HTML <table> kèm cột Mã số theo Thông tư 200.
TICKERS: list[str] = [
    # Vốn hóa lớn, chất lượng công bố thông tin tốt — nhóm đối chứng
    "VNM", "FPT", "VIC", "VHM", "MSN", "GAS", "PLX",
    # Ngân hàng
    "MBB", "TCB", "VPB",
    # Sản xuất, bán lẻ, tiện ích
    "HPG", "MWG", "POW",
    # Từng có vấn đề về công bố thông tin hoặc biến động mạnh — nhóm quan sát
    "PC1", "VCG", "HAG",
]

# ── Ngưỡng ──
# Chênh lệch lợi nhuận sau thuế giữa BCTC tự lập và BCTC sau kiểm toán
# vượt ngưỡng này thì gán nhãn yếu "rủi ro". Xem smartaudit/labels/.
AUDIT_DIFF_THRESHOLD = 0.10

# Sai lệch tương đối cho phép khi đối chiếu con số trong narrative với bảng.
# Ví dụ narrative nói "tăng 15%", tính ra 14,99% -> vẫn coi là khớp.
NUMERIC_TOLERANCE = 0.01
