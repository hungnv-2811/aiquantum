# 07 / TIÊU CHÍ 5 — KHẢ NĂNG ỨNG DỤNG VÀ TRIỂN KHAI THỰC TẾ (15%)

> **Bản nháp v1 · 19/11/2026 · Người duyệt: Tài.** Phần trên đường kẻ `═══` là nội dung đưa vào báo cáo (≤ 550 từ, 1 bảng). Phần dưới là ghi chú cho người duyệt, không nộp.
> `⟦CHỜ: …⟧` = số hoặc thông tin chưa có, thay bằng số thật trước khi nộp. `⟦KIỂM: …⟧` = phải đối chiếu văn bản gốc.

## 5.1. Bối cảnh và người dùng

Chuẩn mực kiểm toán Việt Nam số 720 (ban hành kèm Thông tư 214/2012/TT-BTC) yêu cầu kiểm toán viên (KTV) đọc các thông tin khác trong tài liệu có BCTC đã kiểm toán, như báo cáo thường niên (BCTN), để phát hiện điểm không nhất quán trọng yếu với BCTC. Việc này hiện làm bằng mắt; công cụ tự động hoá bước sàng lọc, mỗi phát hiện có vết minh chứng tới ô bảng.

Người dùng: kiểm toán viên, giám sát công bố thông tin, nhà đầu tư tổ chức, giảng dạy. Điều kiện: BCTC theo Thông tư 200 (bóc được 337/338), BCTN có lớp chữ; ngân hàng và bản scan nằm ngoài phạm vi.

## 5.2. Hiệu quả: đã đo gì, chưa đo gì

Doanh nghiệp lớn hiếm khi viết sai số liệu đã kiểm toán (ước tính khoảng 2% khẳng định trong mẫu), nên công cụ tốt phải gần như im lặng. Chất lượng được đo bằng hai số đo:

1. **Cờ oan trên dữ liệu thật** (300 cặp có nhãn): trước vá 137/141 cờ là oan; sau vá còn khoảng 23 cờ oan ước tính trên toàn bộ khẳng định (giảm ~83%), nhưng 0/21 cờ trong mẫu là mâu thuẫn thật. Đây là **nhãn bạc** do hai tác tử AI gán mù, độc lập, không phải nhãn người; kappa 0,86.
2. **Recall trên tập chèn lỗi có kiểm soát**: câu đúng bị sửa có chủ đích. Đây là **dữ liệu tổng hợp**, báo cáo riêng: bắt 82,6% (đổi giá trị 86%, đổi tỷ lệ 87%, đảo hướng 71%, "kiểm soát chi phí" 47%); 0/122 báo động giả trên câu đối chứng.

**Chưa thử nghiệm với kiểm toán viên** vì không kịp. Quy trình đã soạn sẵn (`docs/thu-nghiem-ktv/`): làm tay và dùng công cụ trên hai doanh nghiệp khác nhau, đảo thứ tự, ghi thời gian và độ đúng; sẽ chạy sau Vòng 2. **Chưa có đối tác.** Mức tiết kiệm 8–45 tỷ đồng/năm ở hồ sơ Vòng 1 là ước tính, chưa kiểm chứng.

## 5.3. Chi phí, bảo mật, rủi ro

**Bảng 7.1. Chi phí vận hành prototype** *(giá tra ngày 12/11/2026)*

| Thành phần | Cách chạy | Chi phí |
|---|---|---|
| Giao diện kết quả | Trang tĩnh, gói miễn phí (Cloudflare Pages/Netlify) | 0 |
| "Kiểm tra khẳng định" | Lõi Python chạy trong trình duyệt bằng Pyodide, không server | 0; tải ~10 MB lần đầu |
| Pipeline | Offline trên CPU, không gọi API trả phí | 0; 77 giây cho 93 BCTN (khoảng 1 giây/báo cáo khi đã bóc chữ; bóc PDF lần đầu khoảng 12 giây/báo cáo) |
| Con người | KTV rà cờ, bảo trì ontology | Khoản lớn nhất |

Không có dữ liệu cá nhân, không gửi văn bản ra ngoài, nên cài nội bộ được. Rủi ro:

- **Cờ oan:** không chắc thì trả "chưa kiểm chứng được"; giao diện ghi "cần xem xét" và "không phải kết luận kiểm toán".
- **Giấy phép:** TiniX theo CC-BY-NC-4.0, chỉ phi thương mại.
- **Thông tư 99/2025/TT-BTC** thay Thông tư 200 từ năm tài chính 2026: cần ánh xạ lại Mã số theo biểu mẫu mới. Ontology là tệp cấu hình sinh tự động từ dữ liệu, nên đây là việc cấu hình, không phải viết lại hệ thống.

## 5.4. Lộ trình sau cuộc thi

Thử nghiệm với 2–3 KTV, tìm đơn vị thử nghiệm → gán nhãn người → OCR, Thông tư 99, thêm doanh nghiệp → PhoBERT-Fin, chỉ thay bộ luật khi thắng trên cùng tập test. Lớp lượng tử tháo rời được: QSVM + QKA đạt 0,840 ± 0,048 accuracy, thua SVM-RBF (0,911 ± 0,051), chưa vào luồng chính.

═══════════════════════════════════════════════════════════════

## Ghi chú cho người duyệt (không đưa vào báo cáo)

**Placeholder:** tỷ lệ cờ oan trước/sau vá và khoảng tin cậy, kappa, recall theo loại lỗi → Hùng (`evaluate.py` trên nhãn đã phân xử và tập chèn lỗi); thời gian xử lý mỗi báo cáo → Hùng/Phong (bấm giờ trên bản đóng băng, ghi cấu hình máy). VSA 720 và Thông tư 99 → Nguyên đọc văn bản gốc.

**Đã đổi so với v0 (12/11):**

- Bỏ Hugging Face Docker Space (cần gói PRO). "Kiểm tra khẳng định" chạy bằng Pyodide (kế hoạch mục 6.2). Nếu phải dùng phương án dự phòng (Render) thì sửa dòng 2 của Bảng 7.1.
- Bỏ toàn bộ số liệu thử nghiệm KTV vì chưa thử nghiệm. Không ghi "đối tác".
- Nhãn là nhãn bạc do tác tử AI gán. Không viết "hai thành viên khối Tài chính gán nhãn".
- Gộp lộ trình thành danh sách để giữ đúng một bảng.

**Khi có số:** chỉ thay vào chỗ ⟦CHỜ⟧, không thêm câu, để giữ ≤ 550 từ.
