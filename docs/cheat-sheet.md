# Cheat sheet phỏng vấn — AQ2026-064

*In ra hoặc mở trên điện thoại. Một trang, liếc là thấy.*

---

## Bài toán, một câu

> Báo cáo doanh nghiệp nói *"chi phí bán hàng được kiểm soát tốt, giảm so với năm trước"*, còn số liệu cho thấy chi phí **tăng 6,2%**. SmartAudit-Quantum tự động bắt những mâu thuẫn như vậy, kèm minh chứng chỉ đúng dòng nào trong bảng nào.

## Ba con số

| | |
|---|---|
| **~702** | doanh nghiệp niêm yết HOSE + HNX phải rà soát mỗi năm |
| **40–80 giờ** | thời gian đối chiếu thủ công cho **một** doanh nghiệp |
| **~68%** | tỷ lệ vi phạm bị UBCKNN xử phạt năm 2025 là **lỗi công bố thông tin** |

Bổ sung khi cần: 488 quyết định xử phạt / 59,7 tỷ đồng (đến 30/11/2025); dưới 30% gian lận bị phát hiện trước khi gây thiệt hại (PwC 2024).

## Ba điểm mới

1. **NNC** — cơ chế đối chiếu chéo văn bản ↔ số liệu ba chiều: khớp số, khớp hướng xu hướng, khớp ngữ nghĩa định tính. Chưa hệ thống nào làm cả ba trong một pipeline.
2. **PhoBERT-Fin** — mô hình NLP tài chính tiếng Việt đầu tiên theo chuẩn VAS / Thông tư 200.
3. **QKA cho kiểm toán** — ứng dụng đầu tiên của Quantum Kernel Alignment vào bài toán xác minh sự kiện tài chính.

## Ba điểm yếu — tự nhận trước khi bị hỏi

| Điểm yếu | Nói ngay câu này |
|---|---|
| Prototype chưa có backend | "Bản demo giao diện, dữ liệu mô phỏng, đã gắn nhãn cảnh báo trên màn hình" |
| Chưa benchmark quantum | "Mục tiêu thiết kế, chưa đo. Sẽ benchmark công bằng và công bố cả kết quả âm" |
| Nguồn narrative chưa chốt | "BCTC không có MD&A. Ba hướng: crawl BCTN, xử lý Zenodo trên Colab, hoặc dùng Thuyết minh" |

## Câu tử thần và mấu chốt trả lời

**"8 qubit trên simulator thì lợi thế ở đâu?"**
→ Không tuyên bố speedup. Giá trị là **khả năng biểu diễn** trên dữ liệu **ít mẫu, mất cân bằng** — đúng đặc điểm dữ liệu gian lận. Cam kết benchmark công bằng, thua thì công bố thua.

**"94.2% ở đâu ra?"**
→ "Mục tiêu, chưa đo." Chủ động chỉ vào banner cam trên dashboard.

## Bằng chứng cầm sẵn

Mở sẵn file OCR TiniX, đoạn này (VNM, BCTC hợp nhất kiểm toán 2024):

```
Doanh thu thuần ... (10 = 01 - 02) | 10 | VI.1 | 61.782.609.528.445 | 60.368.915.511.505
```

→ Chứng minh: dữ liệu thật, có sẵn cột **Mã số Thông tư 200**, đọc được ngay, không cần OCR lại.

## Phân vai

| | |
|---|---|
| **Hùng** | Tổng quan, NLP, câu hỏi về AI và tính trung thực |
| **Phong** | Toàn bộ câu hỏi về quantum |
| **Nguyên** | Chuẩn mực kế toán, ontology VAS, nguồn narrative, gán nhãn |
| **Tài** | Rủi ro tài chính, người dùng, giá trị thực tiễn |

## Quy tắc vàng

> Không ai được bịa để lấp chỗ trống.
> **"Chỗ này chúng em chưa làm, kế hoạch là…"** luôn là câu trả lời an toàn và ăn điểm.

Thể lệ Điều 10: *mô hình đơn giản chạy ổn định > mô hình phức tạp không triển khai được.*
