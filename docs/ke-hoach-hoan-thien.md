# Kế hoạch hoàn thiện sản phẩm — AQ2026-064

*Sắp theo **thứ tự phụ thuộc và rủi ro**, không gắn lịch. Mục tiêu tối ưu: **demo thuyết phục trước hội đồng**.*

> Nguyên tắc chi phối: **một phát hiện sai trên slide phá hỏng mọi thứ còn lại**. Vì vậy chất lượng kết luận đi trước tính năng, và tính năng đi trước phần hào nhoáng.

---

## Trạng thái hiện tại

Đo ngày 21/09/2026, trên dữ liệu thật.

| Hạng mục | Số đo |
|---|---|
| Mã nguồn | ~4.100 dòng Python · 121 test xanh |
| Dữ liệu | 338 BCTC (TiniX) + 93 BCTN (Vietstock) · 77 MB |
| Bóc bảng theo Mã số TT200 | **337/338** báo cáo |
| Ontology VAS | 31 khoản mục, sinh tự động từ corpus |
| Nhãn yếu từ hồi tố | **31 dương / 686 cặp** (4,5%) |
| Pipeline NNC | chạy end-to-end: **695 khẳng định** |
| ↳ phân bố phán quyết | 57% chưa kiểm chứng · 22% nhất quán · **20% mâu thuẫn** |
| ↳ dương tính giả định danh được | **30%** số cờ, từ 3 nguyên nhân |
| Độ chính xác thật | **chưa đo** |
| Dashboard | chạy **dữ liệu mô phỏng**, chưa nối backend |
| PhoBERT-Fin · Lớp lượng tử · API | chưa bắt đầu |

**Điểm mù đã biết:** ngân hàng (MBB/TCB/VPB) cho 103/103 khẳng định "chưa kiểm chứng" vì dùng Thông tư 49; 16/93 BCTN là bản scan bóc ra ~0 ký tự; 7/93 BCTN crash vì lỗi hình học trang.

---

## GĐ 0 — Vá nền

*Chặn mọi thứ phía sau. Không giai đoạn nào sau đây đáng tin nếu nền còn sai.*

| # | Việc | Vị trí | Tác động |
|---|---|---|---|
| 0.1 | Lỗi hình học PDF: `_page_text` cắt khung bằng `max(x0−2, 0)` và `min(x1+2, width)` **độc lập nhau**, nên khi cột nằm ngoài trang (trang xoay, CropBox lệch) khung bị lật ngược → crash | `smartaudit/ingest/vietstock.py` | **+7,5% độ phủ** — lấy lại HPG 2018–21, POW 2019–20, VNM 2022 |
| 0.2 | Rác bảng biểu bị bóc thành "câu": `_MERGED_NUMBERS` hiện chỉ bắt mẫu *số số %*, bỏ sót bảng tỷ số không có dấu `%` | `smartaudit/nlp/claims.py` | −12% cờ sai |
| 0.3 | Khẳng định về tỷ số bị đối chiếu với chỉ tiêu tiền: ontology thiếu ROE/ROA/ROS nên câu về tỷ suất khớp nhầm sang khoản mục tiền | `smartaudit/nnc/checker.py` (`DERIVED`) | −11% cờ sai |
| 0.4 | Cụm chỉ phạm vi bộ phận chưa lọc: thiếu "đơn vị thành viên", tên chuỗi và thương hiệu con | `smartaudit/nlp/claims.py` (`_SCOPE_LIMITED`) | −10% cờ sai |

**Nghiệm thu:** mỗi sửa có test hồi quy; chạy lại `scripts/run_nnc.py` và ghi lại số cờ trước/sau.

---

## GĐ 1 — Biết mình đang ở đâu

*Giai đoạn quan trọng nhất. Hiện **không ai biết precision thật là bao nhiêu**.*

Soi tay 8 ca ngẫu nhiên trong nhóm "mâu thuẫn" thì 6–7 ca là cáo buộc oan — nhưng 8 ca không đủ để kết luận. Không có con số này thì mọi giai đoạn sau đều là mò.

1. **Gán nhãn 300 cặp** claim–evidence, trải đều theo ngành và theo năm — đúng cam kết ở Phần V mục 8 của hồ sơ.
   Hai thành viên khối Tài chính gán độc lập, thành viên thứ ba phân xử bất đồng, **báo cáo Cohen's kappa** cùng kết quả.
2. **Viết `scripts/evaluate.py`** — xuất ra:
   - Precision / Recall trên nhóm "mâu thuẫn" *(chỉ số quan trọng nhất — đây là nhóm dẫn tới cáo buộc)*
   - Tỷ lệ "chưa kiểm chứng được", **phân rã theo lý do**
   - Độ phủ: % báo cáo bóc được bảng, % khẳng định tra được chỉ tiêu
3. **Chạy và ghi số baseline vào README.**

**Nghiệm thu:** README có một bảng số thật, không có ô nào trống.

---

## GĐ 2 — Lặp chất lượng tới ngưỡng demo được

Vòng lặp ba bước: *phân tích lỗi → sửa → đo lại*. Dùng số của GĐ 1 làm mốc.

**Mục tiêu: precision nhóm "mâu thuẫn" ≥ 80%** — đúng con số đã cam kết trong hồ sơ.

Đây là giai đoạn dài nhất và ít hào nhoáng nhất, nhưng quyết định demo sống hay chết.

> **Nếu không đạt 80%:** thu hẹp phạm vi thay vì hạ chuẩn. Ví dụ chỉ nhận khẳng định tra được Mã số trực tiếp, bỏ nhánh khớp theo tên. Thà ít mà đúng — điều này cũng nhất quán với Nguyên tắc 2 trong hồ sơ.

---

## GĐ 3 — Dashboard chạy dữ liệu thật

`prototype/data.js` hiện là dữ liệu mô phỏng.

1. **API tối thiểu** (FastAPI) — đúng ba endpoint đủ cho dashboard:
   - danh sách doanh nghiệp kèm điểm nhất quán
   - chi tiết một báo cáo
   - một khẳng định kèm vết minh chứng đầy đủ
2. **Thay `data.js`** bằng fetch từ API.
3. **Xử lý ba chỉ số Quantum đang hiển thị** — QSVM Accuracy 94.2% · Kernel Alignment 0.947 · Quantum Advantage +12.7%

> ⚠️ **Điểm 3 là rủi ro trung thực lớn nhất của cả dự án.**
> README đã ghi rõ đây là *mục tiêu thiết kế, chưa benchmark*, và giao diện đã gắn nhãn. Nhưng nếu để nguyên trên màn hình lúc demo mà giám khảo hỏi *"ba số này đo ở đâu ra"*, uy tín mất sạch trong một câu.
> **Chọn một:** gỡ hẳn khỏi màn hình demo, hoặc để nguyên nhưng gắn nhãn cảnh báo ngay cạnh, đủ lớn để không ai bỏ sót.

**Nghiệm thu:** demo chạy end-to-end từ dữ liệu thật, không còn `data.js` mô phỏng.

---

## GĐ 4 — Kịch bản demo

Phần IX của hồ sơ đã liệt kê bốn kịch bản. Chọn doanh nghiệp cụ thể cho từng cái:

| Kịch bản | Gợi ý | Ghi chú |
|---|---|---|
| Nhất quán (đối chứng) | **VNM 2024** | đã chạy tốt, dùng luôn |
| Mâu thuẫn số rõ ràng | chọn ca lệch lớn, không mơ hồ | tránh ca lệch sát ngưỡng |
| **Mâu thuẫn ngầm** | *"chi phí được kiểm soát tốt"* trong khi tỷ lệ chi phí/doanh thu tăng | **Đây là Điểm mới số 1 — bắt buộc phải có ca đẹp** |
| Bất thường qua nhiều kỳ | cần GĐ 6, hoặc dựng thủ công từ chuỗi điểm NNC | |

**Quy tắc không ngoại lệ:** mỗi ca phải **kiểm tay đến từng ô trong bảng gốc** trước khi lên slide.

---

## GĐ 5 — Gỡ điểm mù *(chọn theo sức)*

- **5a · Ngân hàng (Thông tư 49)** — MBB, TCB, VPB hiện cho **103/103** khẳng định "chưa kiểm chứng". Hồ sơ đã tuyên bố ngoài phạm vi nên không phải lỗi, nhưng làm được thì trả lời trực tiếp câu hỏi gần như chắc chắn bị hỏi.
- **5b · OCR cho 16 BCTN bản scan** — +17% độ phủ. MWG mất 5/7 năm chỉ vì lý do này.

---

## GĐ 6 — PhoBERT-Fin

Chỉ bắt đầu **sau GĐ 2**, vì cần tập đánh giá để chứng minh mô hình thắng được baseline bằng luật.

Nhãn huấn luyện sinh tự động đúng như hồ sơ mô tả: weak supervision từ bộ luật hiện có, rồi rà mẫu phân tầng theo ngành và năm.

> **Nếu không kịp:** bộ luật hiện tại vẫn là baseline hợp lệ, và `smartaudit/nlp/claims.py` đã ghi rõ trong docstring rằng đây là lựa chọn có chủ ý theo thể lệ cuộc thi — *"một mô hình AI đơn giản nhưng chạy ổn định sẽ có điểm cao hơn một mô hình phức tạp nhưng không thể triển khai"*.

---

## GĐ 7 — Lớp lượng tử *(làm sau cùng)*

**Điều chỉnh so với hồ sơ: làm QKA trước QSVM**, dù hồ sơ đánh số ngược lại.

Lý do thuần tuý là dữ liệu:

| | Nhãn huấn luyện | Khả thi |
|---|---|---|
| **QKA** — khớp khoản mục khi thiếu Mã số | sinh tự động từ mọi báo cáo *có* cột Mã số → hàng nghìn cặp | ✅ làm được ngay |
| **QSVM** — phát hiện bất thường | **31 mẫu dương / 686 cặp** | ⚠️ cỡ mẫu quá nhỏ |

Với 31 mẫu dương, khoảng tin cậy rộng hơn mọi khác biệt đo được — không kết luận nổi điều gì về lợi thế lượng tử. Trình bày đúng bản chất: **kiểm chứng tính khả thi kỹ thuật**, không phải benchmark.

Đường lui đã viết sẵn trong hồ sơ (Phần V mục 6): lớp lượng tử **tháo rời được**, hệ thống vẫn chạy đầy đủ với kernel cổ điển.

---

## GĐ 8 — Đồng bộ tài liệu

Sau 8 lượt sửa hồ sơ, hai file chuẩn bị phỏng vấn còn lệch với bản v2 ở ba chỗ.

**`docs/cheat-sheet.md`**

- Còn dùng *"dưới 30% gian lận bị phát hiện trước khi gây thiệt hại (PwC 2024)"*. Con số này **không xác minh được** và đã bị gỡ khỏi hồ sơ, thay bằng số liệu ACFE 2026 đã kiểm: trung vị **12 tháng** trước khi bị phát hiện, **43%** số vụ phát hiện nhờ tố giác, gian lận BCTC chiếm **6%** số vụ nhưng thiệt hại trung vị cao nhất **1 triệu USD/vụ**.
- Còn mô tả *"QKA — ứng dụng đầu tiên vào bài toán xác minh sự kiện tài chính"*. Hồ sơ v2 đã đổi khung thành **khớp khoản mục khi bảng thiếu cột Mã số**, vì khi có Mã số thì việc liên kết là tra cứu tất định, không phải bài toán tìm kiếm. Giữ khung cũ là tự tạo mâu thuẫn với chính Module E.
- Chỉ nêu *488 quyết định / 59,7 tỷ*, trong khi hồ sơ v2 nêu *194 quyết định / hơn 53 tỷ*.

> **Về 488 vs 194:** đây **không phải mâu thuẫn**, và `interview-qa.md` đã giải thích đúng — 488 là toàn bộ quyết định của UBCKNN gồm cả cá nhân và mọi loại vi phạm (đến 30/11/2025), còn 194 là thống kê riêng của Vietstock, chủ yếu nhóm tổ chức (đến 19/12/2025). Việc cần làm chỉ là **cheat sheet nêu cả hai kèm phạm vi**, giống cách interview-qa đang làm, để ba tài liệu nói cùng một giọng.

**`docs/interview-qa.md`**

- Dòng ví dụ Vinamilk 2024 ghi *"điểm nhất quán 0,84 trên 11 khẳng định"* — số hiện tại là **0,77 trên 8 khẳng định**, và sẽ đổi tiếp sau GĐ 0. **Cập nhật lần cuối sau khi GĐ 2 chốt**, đừng sửa sớm rồi lại lệch.

Đi phỏng vấn với ba tài liệu nói ba bộ số khác nhau là rủi ro không đáng có.

---

## Không làm

Phần IX liệt kê 5 sản phẩm. Cho một demo trước hội đồng, **bỏ**:

- Web App có xác thực và phân quyền
- Trợ lý truy vấn có ràng buộc minh chứng
- Decision Support System

Chúng là tầm nhìn sản phẩm, đúng chỗ trong hồ sơ, nhưng không cần cho hội đồng. **Giữ: Dashboard + API.**

---

## Tóm tắt phụ thuộc

```
GĐ 0 (vá nền)
  └─> GĐ 1 (đo precision)
        └─> GĐ 2 (lặp chất lượng)   ──> GĐ 6 (PhoBERT-Fin)
              └─> GĐ 3 (dashboard thật)
                    └─> GĐ 4 (kịch bản demo)

GĐ 5 (điểm mù) · GĐ 7 (lượng tử) · GĐ 8 (đồng bộ tài liệu)  — song song, không chặn
```

**Đường găng: GĐ 0 → 1 → 2 → 3 → 4.** Mọi thứ khác có thể cắt mà demo vẫn đứng được.

---

*Lập ngày 21/09/2026. Mọi con số trong tài liệu này đều đo trực tiếp trên repo và dữ liệu thật, không phải ước lượng.*
