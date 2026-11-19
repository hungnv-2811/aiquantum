# 08 / TIÊU CHÍ 6 — TRÌNH BÀY, TÀI LIỆU (10%)

> **Bản nháp v1 · 19/11/2026 · Người duyệt: Tài.** Phần trên đường kẻ `═══` là nội dung đưa vào báo cáo (≤ 550 từ, 1 bảng); phần dưới là ghi chú, không nộp.
> `⟦CHỜ: …⟧` = chưa có, phải thay bằng số hoặc link thật trước khi nộp.

## 6.1. Danh mục hồ sơ nộp kèm

**Bảng 8.1. Hồ sơ Vòng 2 của đội AQ2026-064**

| Thành phần | Tên tệp / đường dẫn | Nội dung |
|---|---|---|
| Báo cáo giải pháp | `AQ2026-R2-AQ2026-064-Bao_cao_giai_phap.pdf` | Theo mẫu BTC |
| Slide | `AQ2026-R2-AQ2026-064-Slide.pptx` | Slide chính + dự phòng; lời thoại trong ghi chú |
| Mã nguồn | `AQ2026-R2-AQ2026-064-Ma_nguon.zip` | Mã, test, dữ liệu mẫu chạy offline, nhãn, kết quả, `NOTICE` |
| Hướng dẫn | `AQ2026-R2-AQ2026-064-Huong_dan.pdf` | Cài đặt, chạy thử, đầu ra kỳ vọng, xử lý sự cố |
| Prototype | ⟦CHỜ: link prototype⟧ | Trang tĩnh, công khai, không cần tài khoản |

Mọi con số sinh từ script và JSON của pipeline; số đo trên tập chèn lỗi luôn ghi là dữ liệu tổng hợp.

## 6.2. Kịch bản thuyết trình và demo

Bài nói 9 phút 30 giây trong khung 10 phút (điều chỉnh theo thời lượng BTC công bố): **0:00–1:40** bài toán và nguyên tắc "thà im lặng có lý do còn hơn cáo buộc sai" · **1:40–3:35** kiến trúc neo Mã số, dữ liệu, hai số đo · **3:35–4:20** kết quả trước/sau vá · **4:20–6:40** demo trực tiếp · **6:40–7:55** lượng tử và giới hạn · **7:55–9:30** triển khai, kết luận.

**Demo:** câu đúng được xác nhận nhất quán kèm vết minh chứng; sửa một con số thì phán quyết đổi; ca mâu thuẫn dùng **câu chèn lỗi** ghi rõ trên màn hình. Lõi chạy tại máy người xem nên trang đã tải thì mất mạng vẫn demo được; link lỗi thì chạy bản tại máy.

## 6.3. Phản biện

Hùng điều phối: bài toán, triển khai → Tài; kế toán, dữ liệu, nhãn → Nguyên; pipeline, độ chính xác → Hùng; lượng tử, prototype → Phong. Mỗi câu trả lời không quá 45 giây: trả lời thẳng, đưa bằng chứng, nêu giới hạn.

Giới hạn đội chủ động nêu trước khi bị hỏi: precision trên dữ liệu thật chưa đạt mục tiêu; nhãn bạc do tác tử AI gán; chưa thử nghiệm với kiểm toán viên, chưa có đối tác; lượng tử thua SVM-RBF (0,840 so với 0,911); ngân hàng, bản scan ngoài phạm vi.

**Khai báo sử dụng công cụ AI** (Thể lệ Điều 14)

Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm.

═══════════════════════════════════════════════════════════════

## Ghi chú cho người duyệt (không đưa vào báo cáo)

**Placeholder:** số trang (Hùng, sau khi xuất PDF); link prototype (Phong); link video (Phong, nếu có quay; không có thì xoá câu "rồi video …"); thời lượng Vòng 2 (Tài, khi BTC trả lời).

**Đã đổi so với v0 (12/11):**

- Khai báo AI viết lại đúng mức thật. Câu cũ "AI không tham gia gán nhãn… thử nghiệm với kiểm toán viên" **sai** với thực tế, đã bỏ. Câu khai báo này phải **trùng nguyên văn** ở README, slide 13 và slide dự phòng D5.
- Bỏ dòng "Kiểm chứng tài liệu" (kiểm thử máy sạch) vì chưa có kết quả. Nếu Nguyên đã cài thử trên máy sạch thì thêm lại một câu kèm số phút và số test đạt.
- Bảng 8.2 cũ chuyển thành danh sách để giữ đúng một bảng.
- Slide: 13 chính + 5 dự phòng, khớp `deliverables/AQ2026-R2-AQ2026-064-Slide.pptx`. Đổi số slide thì sửa Bảng 8.1.
- Tên tệp nhãn trong zip (`gold_300.csv` hay `labels_*.csv`) phải kiểm lại khi đóng gói.
