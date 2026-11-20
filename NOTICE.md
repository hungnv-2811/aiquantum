# NOTICE — Nguồn dữ liệu, thư viện và giấy phép

Gói mã nguồn dự thi AI-Quantum Challenge 2026, đội AQ2026-064. Phục vụ mục đích **phi thương mại** (dự thi, học tập, nghiên cứu).

## Dữ liệu

| Dữ liệu | Nguồn | Giấy phép / căn cứ | Có trong gói |
|---|---|---|---|
| BCTC hợp nhất, riêng (văn bản OCR, bảng HTML có cột Mã số TT200) | `tinixai/ocr_annual_financials` trên HuggingFace | CC BY-NC 4.0 — ghi nguồn, phi thương mại | Có: 16 mã, `data/raw/tinix/` |
| Báo cáo thường niên (BCTN) | Doanh nghiệp công bố theo Thông tư 96/2020/TT-BTC; tải từ Vietstock | Tài liệu công bố thông tin bắt buộc | Chỉ bản **văn bản đã bóc** (`data/interim/bctn_text/`); không phân phối lại PDF gốc — tải bằng `scripts/fetch_narrative.py` |
| Nhãn đánh giá 300 cặp | Đội tự xây dựng (tác tử AI gán mù, đội phân xử) | Của đội | Có: `annotation/` |

Bộ *Vietnam Listed Companies Annual Reports* trên Zenodo khai trong hồ sơ Vòng 1 **chưa được dùng** trong bản này.

## Thư viện đóng gói hoặc tải khi chạy

Bản Git kèm hai BCTC OCR TiniX trong `sample_data/tinix/` (CC BY-NC 4.0),
bốn trích đoạn BCTN trong `sample_data/narratives.json`, và snapshot JSON
công khai của dashboard trong `prototype/data/`. Nguồn tải, revision và
checksum được ghi tại `sample_data/manifest.json`. Corpus đầy đủ `data/`
trong bảng trên chỉ có ở gói bàn giao, không có trong bản clone Git.

| Thành phần | Giấy phép | Ghi chú |
|---|---|---|
| Chart.js 4.4.4 | MIT | `prototype/vendor/chart.umd.min.js` |
| Font Inter, JetBrains Mono | SIL Open Font License 1.1 | `prototype/vendor/fonts/` |
| Pyodide 0.26.4 | MPL 2.0 | Tải từ cdn.jsdelivr.net khi dùng "Kiểm tra khẳng định" |
| Thư viện Python (pandas, lxml, pdfplumber, rapidfuzz, pyyaml…, qiskit, scikit-learn) | Giấy phép mã nguồn mở của từng thư viện | Cài qua `requirements-lock.txt`, `requirements-quantum.txt` |

## Công cụ AI

Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm.
