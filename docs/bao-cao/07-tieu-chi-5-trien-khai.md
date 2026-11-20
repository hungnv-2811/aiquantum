# 07 / TIÊU CHÍ 5 — KHẢ NĂNG ỨNG DỤNG VÀ TRIỂN KHAI THỰC TẾ (15%)

> **Bản nháp v1 · 19/11/2026 · Người duyệt: Tài.** Phần trên đường kẻ `═══` là nội dung đưa vào báo cáo (≤ 550 từ, 1 bảng). Phần dưới là ghi chú cho người duyệt, không nộp.
> `⟦CHỜ: …⟧` = số hoặc thông tin chưa có, thay bằng số thật trước khi nộp. `⟦KIỂM: …⟧` = phải đối chiếu văn bản gốc.

## 5.1. Bối cảnh và người dùng

Chuẩn mực kiểm toán Việt Nam số 720 (ban hành kèm Thông tư 214/2012/TT-BTC) yêu cầu kiểm toán viên (KTV) đọc các thông tin khác trong tài liệu có BCTC đã kiểm toán, như báo cáo thường niên (BCTN), để phát hiện điểm không nhất quán trọng yếu với BCTC. Việc này hiện làm bằng mắt; công cụ tự động hoá bước sàng lọc, mỗi phát hiện có vết minh chứng tới ô bảng.

Người dùng: kiểm toán viên, giám sát công bố thông tin, nhà đầu tư tổ chức, giảng dạy.

## 5.2. Hiệu quả: đã đo gì, chưa đo gì

**Lợi ích đo được trên prototype:**

1. **Tự động hoá phần đọc và tra cứu:** 112 BCTN chạy trong 14 giây; 108/511 khẳng định được xác nhận nhất quán kèm Mã số và trang BCTC, KTV chỉ cần mở đúng ô để kiểm lại.
2. **Không làm nhiễu người dùng:** 0/163 báo động giả trên câu đúng; cờ oan ước tính giảm khoảng 83% so với bản 21/09.
3. **Nhạy với câu viết sai:** bắt 83,0% câu bị sửa có chủ đích (đổi giá trị 89%, đổi tỷ lệ 83%, đảo hướng 72%; dữ liệu tổng hợp, báo cáo riêng).

**Quy mô toàn thị trường:** 702 doanh nghiệp niêm yết HOSE, HNX × khoảng 0,13 giây/báo cáo ≈ 1,5 phút cho một năm báo cáo khi đã bóc chữ; bóc PDF lần đầu khoảng 12 giây/báo cáo, tức khoảng 2,3 giờ trên một laptop.

**Cơ sở ước tính hiệu quả kinh tế:** hồ sơ Vòng 1 ước tính tiết kiệm 8–45 tỷ đồng/năm (khoảng 700 doanh nghiệp × 40–80 giờ đối chiếu × mức tiết kiệm 60–80% × 0,5–1 triệu đồng/giờ KTV). Thử nghiệm với kiểm toán viên (giai đoạn 1, quy trình đã soạn sẵn) sẽ cho số đo thời gian thực tế để kiểm chứng ước tính này.

## 5.3. Chi phí, bảo mật, rủi ro

**Bảng 5.1. Chi phí vận hành prototype** *(giá tra ngày 12/11/2026)*

| Thành phần | Cách chạy | Chi phí |
|---|---|---|
| Giao diện kết quả | Trang tĩnh trên Vercel, gói miễn phí | 0 |
| "Kiểm tra khẳng định" | Lõi Python chạy trong trình duyệt bằng Pyodide, không server | 0; tải ~10 MB lần đầu |
| Pipeline | Offline trên CPU, không gọi API trả phí | 0; 14 giây cho 112 BCTN đã bóc chữ |
| Con người | KTV rà cờ, bảo trì ontology | Khoản lớn nhất |

Không có dữ liệu cá nhân, không gửi văn bản ra ngoài, nên cài nội bộ được tại công ty kiểm toán hay cơ quan quản lý. **Khả năng mở rộng:** xử lý theo lô, mỗi báo cáo độc lập nên chạy song song theo mã được; thêm doanh nghiệp chỉ cần thêm dữ liệu, không sửa mã. Rủi ro và biện pháp:

- **Cờ oan:** không chắc thì trả "chưa kiểm chứng được"; giao diện gọi nhóm cờ là tín hiệu để người xem lại, mỗi cờ kèm minh chứng để tự kiểm.
- **Giấy phép:** TiniX theo CC-BY-NC-4.0, chỉ phi thương mại. Bản thương mại tự bóc BCTC từ PDF công bố (khâu OCR ở giai đoạn 3), không phụ thuộc TiniX.
- **Thông tư 99/2025/TT-BTC** thay Thông tư 200 từ năm tài chính 2026: chỉ cần ánh xạ lại Mã số trong ontology (tệp cấu hình), không viết lại hệ thống.

## 5.4. Lộ trình sau cuộc thi

**Bảng 5.2. Lộ trình dự kiến, nguồn lực và mốc kiểm chứng**

| Giai đoạn | Việc chính | Nguồn lực | Mốc kiểm chứng |
|---|---|---|---|
| 1 · 12/2026–02/2027 | Thử nghiệm với 2–3 KTV, giảng viên kiểm toán theo quy trình đã soạn | Cả đội; 2–3 KTV | Thời gian đối chiếu có và không có công cụ; tỷ lệ cờ KTV xác nhận |
| 2 · 03–06/2027 | Tính tỷ số cơ cấu và số bình quân; KTV gán nhãn tập test | Nhóm AI, nhóm tài chính | Precision nhóm cần xem xét trên tập test do KTV gán |
| 3 · 07–12/2027 | OCR bản scan; Thông tư 99/2025; ngân hàng (TT49); mở rộng toàn HOSE, HNX | Thêm 1–2 người; máy chủ nội bộ | Độ phủ báo cáo đọc được; số doanh nghiệp |
| 4 · 2028 | PhoBERT-Fin thay bộ luật khi thắng trên cùng tập test; bản cài nội bộ | GPU thuê theo giờ | Ký thử nghiệm với ít nhất một đơn vị |

**Tiềm năng thương mại hoá:** Chuẩn mực kiểm toán số 720 áp dụng cho mọi cuộc kiểm toán có báo cáo thường niên, nên mỗi công ty kiểm toán doanh nghiệp niêm yết là khách hàng tiềm năng; UBCKNN, HOSE, HNX dùng để giám sát; doanh nghiệp tự kiểm tra trước khi công bố. Bản cài nội bộ phù hợp yêu cầu bảo mật hồ sơ kiểm toán. Lớp lượng tử tháo rời được; QKA chỉ vào luồng chính khi vượt SVM-RBF trên cùng tập kiểm tra.

═══════════════════════════════════════════════════════════════

## Ghi chú cho người duyệt (không đưa vào báo cáo)

**Placeholder:** tỷ lệ cờ oan trước/sau vá và khoảng tin cậy, kappa, recall theo loại lỗi → Hùng (`evaluate.py` trên nhãn đã phân xử và tập chèn lỗi); thời gian xử lý mỗi báo cáo → Hùng/Phong (bấm giờ trên bản đóng băng, ghi cấu hình máy). VSA 720 và Thông tư 99 → Nguyên đọc văn bản gốc.

**Đã đổi so với v0 (12/11):**

- Bỏ Hugging Face Docker Space (cần gói PRO). "Kiểm tra khẳng định" chạy bằng Pyodide (kế hoạch mục 6.2). Nếu phải dùng phương án dự phòng (Render) thì sửa dòng 2 của Bảng 7.1.
- Bỏ toàn bộ số liệu thử nghiệm KTV vì chưa thử nghiệm. Không ghi "đối tác".
- Nhãn là nhãn bạc do tác tử AI gán. Không viết "hai thành viên khối Tài chính gán nhãn".
- Gộp lộ trình thành danh sách để giữ đúng một bảng.

**Khi có số:** chỉ thay vào chỗ ⟦CHỜ⟧, không thêm câu, để giữ ≤ 550 từ.
