# SmartAudit-Quantum

**Đối chiếu ngôn từ báo cáo thường niên với số liệu BCTC đã kiểm toán — AI cho kiểm toán và giám sát công bố thông tin, có thí nghiệm lượng tử**

> Đội **AQ2026-064 — Ngôi nhà Hoa Hồng** · AI-Quantum Challenge 2026 (Học viện Tài chính) · Bản nộp Vòng 2, 19/11/2026
> **Prototype: https://smartaudit-quantum.vercel.app** (công khai, không cần tài khoản) · Hướng dẫn đầy đủ: `AQ2026-R2-AQ2026-064-Huong_dan.pdf`

## Bài toán

Chuẩn mực kiểm toán Việt Nam số 720 yêu cầu kiểm toán viên đọc các thông tin khác trong tài liệu có BCTC đã kiểm toán — như báo cáo thường niên — để phát hiện điểm không nhất quán trọng yếu. Với hơn 700 doanh nghiệp niêm yết, việc đối chiếu từng câu có số liệu với ô tương ứng trong BCTC hiện chủ yếu làm bằng mắt.

SmartAudit-Quantum tự động hoá bước sàng lọc: mỗi câu có số liệu được **neo vào đúng ô BCTC qua Mã số Thông tư 200** và nhận một trong ba phán quyết — *Nhất quán*, *Cần xem xét*, *Chưa kiểm chứng được* — kèm vết minh chứng kiểm tra lại được (câu gốc, trang, Mã số, phép tính). Nguyên tắc: **thà im lặng có lý do còn hơn cáo buộc sai.**

## Kết quả đo được (20/11/2026)

| Chỉ số | Bản 21/09 | Hiện tại (20/11) |
|---|---|---|
| Cặp báo cáo đối chiếu được | 66 | 98 |
| Khẳng định trích được | 695 | 511 |
| Cờ "cần xem xét" | 141 | 52 |
| Precision nhóm cần xem xét, dữ liệu thật (300 cặp nhãn bạc) | 2,8% (4/141) | 0% (0/21) |
| Cờ oan ước tính trên tập khẳng định bản 21/09 | ~137 | ~23 |
| Recall trên tập chèn lỗi có kiểm soát (dữ liệu tổng hợp) | — | 83,0% (473/570) |
| Báo động giả trên câu đối chứng | — | 0/163 |
| Kiểm thử tự động | 121 | 147 (+24 thí nghiệm lượng tử) |

**Đọc kết quả trung thực.** Bản vá loại được phần lớn cờ oan (đơn vị tính nghìn/triệu đồng, câu về công ty con, rác bố cục PDF, câu không phải kết quả…). Bộ đối chiếu nhạy với lỗi khi câu được trích đúng. Nhưng **mục tiêu precision 80% chưa đạt** trên dữ liệu thật: mâu thuẫn thật rất hiếm (ước tính ~2% khẳng định) và cả 7 ca trong mẫu đều là lỗi trình bày ở tỷ số, cơ cấu (hệ số nợ/VCSH, tỷ trọng tài sản) — loại hệ thống chưa tính. Đó là bước tiếp theo.

Nhãn 300 cặp do **hai tác tử AI gán mù, độc lập** theo hướng dẫn của đội (`docs/gan-nhan/`), bất đồng được phân xử (kappa 0,86) — đây là *nhãn bạc*, chưa được chuyên gia kiểm toán kiểm lại toàn bộ.

**Thí nghiệm lượng tử (QKA)** cho bài toán khớp khoản mục khi bảng thiếu cột Mã số: QSVM + QKA đạt accuracy 0,840 ± 0,048, **thua** SVM-RBF cổ điển 0,911 ± 0,051 (rapidfuzz đang dùng: 0,812). Ở 8 qubit không thể có lợi thế lượng tử; đây là kiểm chứng khả thi kỹ thuật, công bố cả kết quả âm. Lớp lượng tử tháo rời được. Chi tiết: [docs/quantum-poc.md](docs/quantum-poc.md).

## Chạy nhanh

**Dashboard** (Python >= 3.10, khuyến nghị 3.11; không cần cài thư viện Python).
Bản Git kèm JSON của 98 báo cáo trong `prototype/data/`, được khôi phục từ
prototype công khai và đối chiếu với kết quả trong `results/`:

```bash
python scripts/check_environment.py
python -m http.server 8000 --bind 127.0.0.1 --directory prototype
```

rồi mở `http://127.0.0.1:8000`. Trên Windows có thể nhấp đúp `run_demo.bat`
(tự kiểm tra dữ liệu trước khi mở). Các trang kết quả dùng dữ liệu tại máy;
chức năng **Kiểm tra khẳng định cần mạng để nạp Pyodide lần đầu** từ CDN.

**Chạy lõi với mẫu nhỏ**, không cần tải toàn bộ corpus:

```bash
python -m pip install -r requirements-sample.txt
python scripts/check_environment.py --mode sample
python scripts/run_sample.py
# Tuỳ chọn lưu riêng, không ghi đè benchmark:
python scripts/run_sample.py --output sample_result.json
```

Mẫu gồm hai BCTC thật (VNM 2024, FPT 2022) và bốn trích đoạn BCTN từ kết quả
đã lưu. Sau khi cài PyYAML, chạy mẫu không cần mạng. Nguồn, checksum và giới
hạn: [sample_data/README.md](sample_data/README.md). Đây là phép thử khả năng
chạy, không phải đo lại chất lượng trên 98 báo cáo.

**Pipeline và kiểm thử** (Python 3.11):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1            # macOS/Linux: source .venv/bin/activate
pip install -r requirements-lock.txt
python scripts/check_environment.py --mode pipeline
pytest tests -q                       # số trong bảng trên là kết quả đã công bố
python scripts/run_nnc.py             # đối chiếu toàn bộ, ghi results/nnc_results.json
python scripts/audit_report.py FPT 2022
python scripts/make_injected_set.py   # tập chèn lỗi
python scripts/evaluate.py            # số đo trên 300 cặp gán nhãn
python scripts/export_dashboard.py    # cập nhật dữ liệu dashboard
```

**Bộ dữ liệu đầy đủ `data/` không nằm trong Git.** Các lệnh toàn bộ pipeline,
chèn lỗi, xuất lại dashboard cần corpus này. Nhận corpus từ gói bàn giao của
đội hoặc tải bằng `scripts/fetch_data.py`, `scripts/fetch_narrative.py` và
`scripts/fetch_narrative_extra.py` theo tài liệu của từng script. Không thay
corpus đầy đủ bằng mẫu nhỏ để xuất lại các số đo đã công bố.

Thí nghiệm lượng tử dùng môi trường riêng: `requirements-quantum.txt`,
`python scripts/run_qka.py --quick`; lệnh này vẫn cần TiniX đầy đủ.

Kiểm tra đóng gói (thư viện chuẩn + PyYAML, không cần pytest):
`python -m unittest discover -s tests -p test_distribution.py -v`.

## Cấu trúc

```
smartaudit/        thư viện: ingest · tables (bóc bảng, đơn vị tính) · ontology · nlp (trích khẳng định)
                   · nnc (đối chiếu, vết minh chứng) · eval · quantum (tách rời) · xai
scripts/           run_nnc · audit_report · evaluate · make_injected_set · sample_for_labeling
                   · export_dashboard · run_qka · fetch_* · build_*
tests/             kiểm thử tự động (có test hồi quy cho từng bản vá)
prototype/         dashboard tĩnh; data/ (kết quả thật) · py/ (lõi Python cho Pyodide)
annotation/        mẫu 300 cặp, nhãn A, B, phân xử, nhãn cuối (gold_300.csv)
results/           kết quả đã chạy sẵn để đối chiếu
docs/              kế hoạch, hướng dẫn gán nhãn, rà soát ca demo, báo cáo QKA, nháp báo cáo
sample_data/       2 BCTC OCR + 4 trích đoạn BCTN, nguồn và checksum (có trong Git)
data/              corpus đầy đủ trên máy / gói bàn giao (không có trong Git)
```

## Giới hạn

- Trích khẳng định bằng bộ luật, chưa có mô hình học (PhoBERT-Fin là bước sau, chỉ thay khi thắng bộ luật trên cùng tập test).
- Còn cờ oan khi câu nói về một mảng/công ty con mà không có từ khoá phạm vi, hoặc khi PDF bị trộn cột.
- Chưa tính tỷ số cơ cấu; ngân hàng (Thông tư 49) và 11 báo cáo thường niên không đọc được (bản scan, mất dấu, công văn) chưa xử lý.
- Chưa thử nghiệm với kiểm toán viên; chưa có đối tác.

## Đội ngũ

| Thành viên | Trường | Vai trò |
|---|---|---|
| Nguyễn Việt Hùng | ĐH Xây dựng Hà Nội | Trưởng nhóm, AI/NLP |
| Nguyễn Hồng Nguyên | Học viện Tài chính | Nghiệp vụ tài chính, ontology |
| Lê Cao Phong | Học viện Công nghệ BCVT | Quantum ML, hệ thống |
| Mai Đức Tài | Học viện Tài chính | Rủi ro tài chính, sản phẩm |

## Khai báo sử dụng công cụ AI (Thể lệ Điều 14)

Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm.

Nguồn dữ liệu và giấy phép: [NOTICE.md](NOTICE.md).
