# 06 / Tiêu chí 4 — Chất lượng prototype, nguyên mẫu

### 4.1. Phạm vi prototype đã hoàn thành

**Đã chạy thật trên dữ liệu thật:**

- Pipeline đầu–cuối: 112 báo cáo thường niên ↔ 165 BCTC (mỗi mã–năm một báo cáo, ưu tiên hợp nhất, chọn từ 338), ra 98 cặp đối chiếu được, 511 khẳng định, mỗi khẳng định có vết minh chứng (câu gốc, trang BCTN, Mã số, trang BCTC, phép tính).
- Dashboard web tĩnh 7 trang, đọc kết quả xuất từ pipeline, không có dữ liệu mô phỏng.
- **Kiểm tra khẳng định trực tiếp:** người dùng gõ một câu, hệ thống chạy **đúng mã nguồn Python của pipeline** ngay trong trình duyệt (Pyodide/WebAssembly) và trả phán quyết kèm minh chứng. Không cần server.
- Bộ đo lường: gán nhãn 300 cặp, tập chèn lỗi, thí nghiệm QKA — đều chạy lại được bằng một lệnh.

**Chưa làm:** mô hình PhoBERT-Fin, phân tích tỷ số cơ cấu, ngân hàng (TT49), OCR bản scan, tải PDF tuỳ ý lên hệ thống, API server.

### 4.2. Các chức năng và kịch bản demo

1. **Tổng quan:** số báo cáo, khẳng định, phân bố phán quyết theo doanh nghiệp; danh sách câu cần xem xét kèm minh chứng.
2. **Doanh nghiệp:** bảng kết quả theo năm (số câu nhất quán, cần xem xét) → bấm một ô mở chi tiết.
3. **Chi tiết báo cáo:** ví dụ FPT 2022, câu "Doanh thu đạt 44.010 tỷ đồng, tăng 23,4%" → Nhất quán, khớp Mã số 10 trang 13 (35.657 → 44.010 tỷ).
4. **Kiểm tra khẳng định:** VNM 2024, gõ "Doanh thu thuần đạt 61.783 tỷ đồng, tăng 2,3%" → Nhất quán; sửa thành "65.000 tỷ, tăng 7,6%" → Cần xem xét, lệch 5,2% và 5,26 điểm; gõ câu về công ty con Angkormilk → hệ thống không kết luận, nêu lý do.
5. **Đánh giá chất lượng** và **Thí nghiệm lượng tử:** số đo thật, kể cả kết quả âm.

### 4.3. Kiểm thử và kết quả bước đầu

**Bảng 4.1. Kiểm thử và kết quả bước đầu**

| Hạng mục | Kết quả | Điều kiện |
|---|---|---|
| Kiểm thử tự động | ⟦CHỜ: số test⟧ | `pytest tests -q`, Python 3.11, Windows 11 |
| Thời gian chạy toàn bộ pipeline | 14 giây cho 112 báo cáo | laptop, văn bản BCTN đã bóc sẵn |
| Recall tập chèn lỗi / báo động giả đối chứng | 83,0% / 0 trên 163 | 791 câu tổng hợp từ câu thật |
| Cờ oan ước tính | ~137 → ~23 | 300 cặp gán nhãn mù |
| Kiểm tra khẳng định trong trình duyệt | 2–11 ms mỗi câu sau khi nạp | tải lần đầu ~10 MB |

Lỗi nhỏ đã biết: một số câu bị trộn cột khi bóc PDF vẫn được trích và có thể bị gắn "cần xem xét" oan; vì vậy dashboard gọi nhóm này là tín hiệu để người xem lại, không phải kết luận.

### 4.4. Khả năng tái lập và hạn chế hiện tại

Mã nguồn chia theo mô-đun (`smartaudit/` thư viện, `scripts/` lệnh chạy, `tests/` kiểm thử, `prototype/` giao diện), chú thích tiếng Việt. Gói nộp kèm dữ liệu mẫu (BCTC 16 mã + văn bản BCTN đã bóc) nên chạy lại được **không cần mạng**: `pip install -r requirements-lock.txt` → `python scripts/run_nnc.py` → `python scripts/export_dashboard.py`. Chi tiết trong tệp Hướng dẫn.
