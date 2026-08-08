# SmartAudit-Quantum

**Nền tảng kiểm toán ngôn từ và số liệu thông minh cho thị trường chứng khoán Việt Nam sử dụng AI & Điện toán lượng tử**

> Đội **AQ2026-064 — Ngôi nhà Hoa Hồng**
> AI-Quantum Challenge 2026 · Cuộc thi Trí tuệ nhân tạo và Lượng tử trong Kinh tế – Tài chính – Kế toán lần thứ I

---

## Bài toán

Hơn 700 doanh nghiệp niêm yết trên HOSE và HNX công bố hàng trăm nghìn trang báo cáo mỗi năm. Việc đối chiếu phần **giải trình bằng văn bản** (Thư gửi cổ đông, MD&A) với **số liệu kế toán thực tế** hiện chủ yếu làm thủ công, tốn 40–80 giờ cho mỗi doanh nghiệp, và vẫn để lọt nhiều bất nhất quán.

Ví dụ điển hình: Thư gửi cổ đông viết *"chi phí bán hàng được kiểm soát tốt, giảm so với năm trước"*, trong khi Báo cáo kết quả kinh doanh cho thấy chi phí bán hàng **tăng 6,2%**. Loại mâu thuẫn này rất khó phát hiện bằng mắt thường ở quy mô lớn.

SmartAudit-Quantum tự động phát hiện những mâu thuẫn đó, kèm **minh chứng truy vết được đến từng ô trong bảng số liệu**.

## Cách tiếp cận

Hệ thống gồm ba trụ cột:

| Trụ cột | Vai trò |
|---|---|
| **NLP tiếng Việt miền tài chính** | PhoBERT fine-tuned trích xuất khẳng định (claim) có chứa số liệu hoặc xu hướng từ phần narrative |
| **Narrative-Number Consistency (NNC)** | Đối chiếu mỗi claim với số liệu tương ứng trong bảng: khớp số, khớp hướng xu hướng, khớp ngữ nghĩa định tính |
| **Lớp lượng tử (QKA + QSVM)** | Quantum Kernel Alignment tối ưu truy xuất minh chứng; QSVM phát hiện bất thường phi tuyến trên dữ liệu mất cân bằng |

Vai trò của lượng tử là **lớp tăng cường**, không thay thế pipeline cổ điển. AI xử lý ngữ nghĩa, lượng tử tối ưu tìm kiếm và phân loại trong không gian chiều cao.

## Trạng thái hiện tại

> ⚠️ **Dự án đang ở giai đoạn hồ sơ Vòng 1.** Prototype trong `prototype/` là **bản demo giao diện chạy trên dữ liệu mô phỏng** — chưa có backend, chưa có mô hình AI hay mạch lượng tử nào chạy thật. Mọi chỉ số Quantum hiển thị (QSVM Accuracy 94.2%, Kernel Alignment 0.947, Quantum Advantage +12.7%) là **mục tiêu thiết kế, chưa được benchmark**, và đã được gắn nhãn rõ ràng ngay trên giao diện.

| Hạng mục | Trạng thái |
|---|---|
| Hồ sơ Vòng 1 | ✅ Đã nộp 30/07/2026 |
| Dashboard demo (6 trang) | ✅ Chạy được, dữ liệu mô phỏng |
| Backend / pipeline NNC | ⬜ Chưa bắt đầu |
| Mô hình PhoBERT-Fin | ⬜ Chưa bắt đầu |
| Lớp lượng tử (Qiskit) | ⬜ Chưa bắt đầu |

## Chạy demo

Prototype là trang tĩnh, **không cần cài đặt gì và không cần mạng** (Chart.js cùng font đã đóng gói trong `prototype/vendor/`).

**Cách khuyến nghị — một lệnh duy nhất:**

```
run_demo.bat
```

Script tự khởi động HTTP server cục bộ ở cổng 8000 và mở trình duyệt. Nhấn `Ctrl+C` để dừng.

**Hoặc thủ công:**

```bash
cd prototype
python -m http.server 8000     # rồi mở http://localhost:8000
```

> Nên chạy qua HTTP server thay vì mở thẳng `index.html`: một số trình duyệt chặn tải font qua giao thức `file://` vì chính sách CORS, khiến giao diện mất font dù file đã có sẵn trong máy.

Dashboard có 6 trang: Dashboard tổng quan · Doanh nghiệp · Phân tích NNC · Quantum Engine · Anomaly Detection · Cảnh báo.

## Cấu trúc kho mã

```
├─ SmartAudit_Quantum_Proposal.docx     Hồ sơ đề xuất đã nộp Vòng 1
├─ 01-mau-nop-bai-du-thi-vong-1.docx    Mẫu hồ sơ của Ban Tổ chức
├─ Thể lệ AI và Lượng tử 2026...docx    Thể lệ chính thức
├─ docs/                                Tài liệu nội bộ (Q&A phỏng vấn, cheat sheet)
└─ prototype/                           Dashboard demo
   ├─ index.html                        6 trang, điều hướng bằng JS
   ├─ style.css                         Dark theme
   ├─ data.js                           ⚠️ DỮ LIỆU MÔ PHỎNG
   ├─ app.js                            Logic render + biểu đồ Chart.js
   └─ vendor/                           Chart.js v4.4.4 + font (đóng gói offline)
```

## Nguồn dữ liệu

Cả hai bộ đều là dữ liệu mở, đã kiểm chứng tồn tại và truy cập được:

| Nguồn | Quy mô | Giấy phép |
|---|---|---|
| [Vietnam Listed Companies Annual Reports 2000–2025](https://doi.org/10.5281/zenodo.20949551) (Zenodo) | 134.8 GB, báo cáo thường niên | CC-BY-4.0 |
| [tinixai/ocr_annual_financials](https://huggingface.co/datasets/tinixai/ocr_annual_financials) (HuggingFace) | 18.231 BCTC / 1.491 mã / 2015–2025, kèm text OCR | CC-BY-NC-4.0 |

Bộ TiniX đặc biệt giá trị vì văn bản OCR **đã giữ nguyên bảng biểu dưới dạng HTML `<table>` kèm Mã số theo Thông tư 200**, nên không cần đến các công cụ nhận dạng bảng nặng nề.

## Lộ trình

| Mốc | Nội dung |
|---|---|
| 09/08/2026 | Phỏng vấn Vòng 1 |
| 20/08/2026 | Công bố kết quả Vòng 1 |
| 25/08 – 10/10/2026 | Xây dựng prototype thật (6–7 tuần) |
| 25/10/2026 | Thuyết trình Vòng 2 |
| 10/11/2026 | Chung kết |

## Đội ngũ

| Thành viên | Trường | Vai trò |
|---|---|---|
| Nguyễn Việt Hùng | ĐH Xây dựng Hà Nội | Trưởng nhóm & AI/NLP Lead |
| Nguyễn Hồng Nguyên | Học viện Tài chính | Financial Domain & Ontology Lead |
| Lê Cao Phong | Học viện Công nghệ BCVT | Quantum ML & System Lead |
| Mai Đức Tài | Học viện Tài chính | Financial Risk & Product Lead |

## Khai báo sử dụng công cụ AI

Theo Điều 5.2 và Điều 14 Thể lệ, nhóm khai báo các công cụ AI đã dùng trong quá trình chuẩn bị:

- **Trợ lý lập trình AI** — hỗ trợ soạn thảo mã nguồn giao diện, rà soát lỗi, và gợi ý cấu trúc tài liệu.
- Mọi ý tưởng, lựa chọn kiến trúc, bài toán và phương pháp đều do nhóm tự đề xuất và có thể giải thích được.
- Nhóm không sử dụng AI tạo sinh để tạo ra toàn bộ bài dự thi.

## Giấy phép

Mã nguồn và tài liệu trong kho này phục vụ dự thi AI-Quantum Challenge 2026. Quyền sở hữu trí tuệ tuân theo Điều 16 Thể lệ cuộc thi.
