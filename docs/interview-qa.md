# Bộ chuẩn bị phỏng vấn Vòng 1

**Đội AQ2026-064 — Ngôi nhà Hoa Hồng** · SmartAudit-Quantum
Lịch phỏng vấn theo Thể lệ: **09/08/2026 (Chủ nhật)**

---

## 0. Nguyên tắc xuyên suốt

> **Trung thực về giới hạn ăn điểm cao hơn tô hồng.**

Thể lệ ghi rõ ba điều nhóm phải bám:

- Điều 14 cấm *"cố ý làm sai lệch dữ liệu, kết quả đầu ra"*.
- Tiêu chí Vòng 3 chấm *"trả lời… trung thực về giới hạn của sản phẩm"*.
- Điều 10: *"một mô hình AI đơn giản nhưng chạy ổn định và giải quyết được cơ bản vấn đề thực tế sẽ có điểm cao hơn một mô hình phức tạp nhưng không thể triển khai"*.

Nếu bị hỏi về thứ chưa làm, câu trả lời đúng luôn có ba phần: **(1) thừa nhận thẳng → (2) nêu kế hoạch cụ thể → (3) nêu phương án dự phòng nếu kế hoạch đó thất bại.**

Tuyệt đối không nói "đã đo được", "đã chạy", "đã đạt" với bất cứ con số nào chưa thật.

---

## 1. Số liệu đã cập nhật — vá lỗ hổng trong hồ sơ

Bảng Minh chứng trong hồ sơ, chỉ tiêu #4, đang để nguyên placeholder:
`[Cần cập nhật số liệu thực tế — ước tính 50-100 vụ/năm]`

**Ban Giám khảo sẽ nhìn thấy dòng này.** Số thật đã tra được:

| Chỉ số | Giá trị | Mốc | Nguồn |
|---|---|---|---|
| Quyết định xử phạt UBCKNN (gồm tổ chức + cá nhân) | **488 quyết định / 59,7 tỷ đồng** | đến 30/11/2025 | Báo cáo UBCKNN |
| Quyết định xử phạt (thống kê riêng nhóm tổ chức) | **194 quyết định / >53 tỷ đồng** | đến 19/12/2025 | Vietstock |
| **Tỷ lệ vi phạm là lỗi công bố thông tin** | **~68% tổng số hành vi bị xử lý** | 2025 | Vietstock |
| Doanh nghiệp đại chúng & niêm yết bị phạt | 148 quyết định (76%) | 2025 | Vietstock |
| Công ty chứng khoán bị phạt | 32 quyết định (16,5%) | 2025 | Vietstock |
| Mức phạt trung bình | >274 triệu đồng/quyết định | 2025 | Vietstock |

**Cách trình bày nếu bị hỏi:**

> "Chỗ đó trong hồ sơ chúng em để trống vì chưa kiểm chứng kịp, và thực tế con số ước tính 50–100 vụ của chúng em là **quá thấp**. Số thật: năm 2025 UBCKNN ban hành 488 quyết định xử phạt với tổng 59,7 tỷ đồng tính đến 30/11. Nếu chỉ tính nhóm tổ chức thì Vietstock thống kê 194 quyết định, hơn 53 tỷ đồng. Quan trọng nhất với bài toán của chúng em: **gần 68% số hành vi bị xử lý là lỗi công bố thông tin** — đúng thứ SmartAudit-Quantum nhắm tới."

Hai con số 488 và 194 khác nhau do **phạm vi thống kê**: 488 gồm cả cá nhân và mọi loại vi phạm; 194 là thống kê riêng của Vietstock, chủ yếu nhóm tổ chức. Nếu BGK vặn, nói rõ điều này — đừng lảng.

**Nguồn để dẫn:**
- https://vietstock.vn/2025/12/toan-canh-an-phat-chung-khoan-nam-2025-830-1383981.htm
- https://doanhnghiephoinhap.vn/11-thang-nam-2025-uy-ban-chung-khoan-nha-nuoc-xu-phat-gan-60-ty-dong-124379.html

---

## 2. Câu hỏi tử thần — phải trả lời được trôi chảy

### Q1. "Quantum thực sự đem lại gì? 8 qubit chạy trên simulator của laptop thì lợi thế ở đâu?"

**Người trả lời chính: Phong (Quantum ML Lead)**

Đây là câu dễ làm sập cả bài. Không được né, không được nói "quantum nhanh hơn" — sai và BGK biết ngay.

> "Thưa thầy/cô, chúng em xin trả lời thẳng: **ở quy mô hiện tại, chạy trên simulator, quantum không nhanh hơn cổ điển.** Mô phỏng mạch lượng tử trên CPU thậm chí còn chậm hơn. Chúng em không tuyên bố có quantum speedup.
>
> Giá trị chúng em nhắm tới là **khả năng biểu diễn**, không phải tốc độ. Quantum kernel ánh xạ dữ liệu vào không gian Hilbert với số chiều tăng theo hàm mũ so với số qubit, tạo ra ranh giới phân lớp phi tuyến mà kernel cổ điển cùng số tham số khó biểu diễn. Chế độ mà lợi thế này rõ nhất là **dữ liệu ít mẫu và mất cân bằng nặng** — đúng đặc điểm bài toán gian lận báo cáo tài chính, vì số vụ được xác minh rất ít so với hơn 700 doanh nghiệp.
>
> Và chúng em cam kết một điều: sẽ benchmark công bằng với SVM-RBF, Random Forest, XGBoost trên cùng tập chia, cùng cross-validation, cùng metric. **Nếu QSVM thua, chúng em công bố đúng như vậy trong báo cáo.** Kết quả âm cũng là kết quả."

Nếu bị hỏi tiếp *"vậy sao không bỏ quantum đi cho gọn?"*:

> "Vì kiến trúc hybrid cho phép thay lớp kernel mà không phải viết lại pipeline. Hôm nay chạy simulator, khi phần cứng trưởng thành thì đổi backend là dùng được ngay. Ngoài ra đây cũng là đóng góp học thuật: theo khảo sát của chúng em, chưa có nghiên cứu nào áp dụng Quantum Kernel Alignment cho bài toán xác minh sự kiện tài chính."

---

### Q1b. "Các em đã làm được gì rồi, hay mới chỉ có ý tưởng?"

**Người trả lời chính: Hùng** — đây là câu ăn điểm, phải trả lời bằng số.

> "Chúng em đã có pipeline chạy thật trên dữ liệu thật, không phải mô phỏng:
>
> - Tải và bóc tách **338 báo cáo tài chính kiểm toán** và **93 báo cáo thường niên** của 16 doanh nghiệp, giai đoạn 2015–2025.
> - Bóc được bảng số liệu từ **337/338 báo cáo**, ánh xạ theo Mã số Thông tư 200.
> - Sinh **ontology 31 khoản mục** tự động từ chính corpus, không soạn tay.
> - Cơ chế NNC chạy end-to-end, mỗi kết luận kèm minh chứng chỉ rõ trang nào, mã số nào, phép tính ra sao.
> - **70 phép kiểm tự động**, chạy trong dưới một giây.
>
> Kết quả mẫu với Vinamilk 2024: điểm nhất quán 0,84 trên 11 khẳng định, phát hiện 2 điểm cần xem xét."

Nếu BGK muốn xem: mở terminal chạy `python scripts/audit_report.py VNM 2024`, in ra báo cáo ngay tại chỗ.

**Điểm mạnh nhất nên nhấn** — hai nguồn hoàn toàn độc lập nối được với nhau:

> "Báo cáo thường niên nói doanh thu trong nước 50.799 tỷ và nước ngoài 10.983 tỷ. Cộng lại đúng bằng 61.782 tỷ — chính là con số doanh thu thuần mã 10 mà chúng em bóc được từ báo cáo tài chính kiểm toán trên HuggingFace. Hai nguồn khác nhau hoàn toàn, khớp đến từng đồng. Đó là cơ chế NNC đang chạy thật."

---

### Q1c. "Các em gặp khó khăn gì khi làm? Kể một cái cụ thể."

Câu này BGK hay hỏi để đo xem đội có thật sự tự làm hay không. Kể được lỗi cụ thể kèm cách sửa là bằng chứng mạnh nhất.

**Chọn kể ba cái này, theo thứ tự:**

**1. Mã số kế toán không duy nhất.** Mã `10` là *Doanh thu thuần* trong Báo cáo kết quả kinh doanh, nhưng là *Biến động hàng tồn kho* trong Lưu chuyển tiền tệ, và là *số hiệu thuyết minh* trong phần Thuyết minh. Ban đầu chúng em tra thẳng theo mã nên ghép nhầm số. Phải thêm bước nhận diện loại báo cáo trước khi diễn giải mã. Sau khi sửa, số biến thể tên của mã 10 giảm từ 133 xuống 20.

**2. Cột "Thuyết minh" bị đọc thành giá trị.** Bố cục bảng là `[tên | mã số | thuyết minh | năm nay | năm trước]`. Vinamilk ghi thuyết minh dạng `VI.1` nên không sao, nhưng FPT ghi số trần `26` — hệ thống nuốt luôn thành giá trị, biến doanh thu FPT 2023 thành **26 đồng** thay vì 52.618 tỷ. Chúng em phát hiện nhờ thấy điểm nhất quán của FPT thấp bất thường rồi lần ngược lại. Cách sửa: trong một hàng, số liệu các kỳ luôn cùng cỡ, còn số hiệu thuyết minh nhỏ hơn hàng nghìn lần. Sau khi sửa, FPT 2023 từ 0,33 lên **1,00**.

**3. Đứt gãy chuỗi số liệu do thoái vốn** — cái này hay nhất vì nó là bài học về nghiệp vụ, không phải về code.

> "FPT năm 2018 có doanh thu **giảm 45,6%**, từ 42.659 tỷ xuống 23.214 tỷ. Hệ thống của chúng em lúc đầu gắn cờ mâu thuẫn cho mọi câu nói về tăng trưởng trong báo cáo thường niên năm đó.
>
> Nhưng khi đọc kỹ, báo cáo ghi rõ *'tăng trưởng 17,4% trong điều kiện so sánh tương đương'*. FPT năm đó thoái vốn mảng bán lẻ và phân phối, nên số hai năm không cùng phạm vi. **Cả hai con số đều đúng** — hệ thống của chúng em mới là cái sai.
>
> Chúng em xử lý bằng hai lớp: nhận diện cụm 'điều kiện so sánh tương đương' ở tầng ngôn ngữ, và phát hiện biến động vượt 40% ở tầng số liệu. Gặp trường hợp đó, hệ thống báo *'chưa kiểm chứng được'* kèm giải thích, chứ không kết luận mâu thuẫn."

Câu chốt nên nói:

> "Nguyên tắc chúng em đặt ra là **thà im lặng còn hơn cáo buộc sai**. Một công cụ kiểm toán gắn cờ oan cho doanh nghiệp thì tệ hơn là bỏ sót, vì nó làm mất niềm tin của kiểm toán viên ngay từ lần dùng đầu tiên."

---

### Q1d. "Vì sao cần PhoBERT? Luật với biểu thức chính quy chưa đủ à?"

Giờ nhóm trả lời được bằng **ví dụ thật từ dữ liệu**, không phải lập luận suông.

> "Chúng em có một ví dụ cụ thể. Câu này trong báo cáo Vinamilk: *'công ty duy trì chính sách quản lý hàng tồn kho'*. Hệ thống dùng luật của chúng em thấy từ 'duy trì' và từ 'hàng tồn kho' nên kết luận: câu này nói tồn kho đi ngang. Nhưng số liệu cho thấy tồn kho tăng 37,4%, nên nó báo mâu thuẫn.
>
> Thực ra 'duy trì' gắn với **chính sách**, không gắn với **giá trị tồn kho**. Phân biệt được điều đó cần phân tích quan hệ phụ thuộc trong câu — đúng thứ mà mô hình ngôn ngữ làm được còn luật thì không.
>
> Trước mắt chúng em xử lý bằng cách bỏ qua nhóm câu nói về chính sách, chấp nhận bỏ sót để không kết luận sai. Nhưng đây chính là chỗ PhoBERT-Fin sẽ tạo khác biệt, và chúng em có sẵn đường cơ sở bằng luật để so sánh xem mô hình cải thiện được bao nhiêu."

---

### Q2. "Con số 94.2% và +12.7% trên dashboard ở đâu ra?"

**Người trả lời chính: Hùng (Trưởng nhóm)**

Câu này là bẫy đạo đức. Chỉ có một câu trả lời đúng.

> "Đó là **mục tiêu thiết kế, chúng em chưa đo được**. Prototype hiện tại là bản demo giao diện chạy trên dữ liệu mô phỏng, chưa có mô hình thật phía sau. Chúng em đã gắn nhãn cảnh báo ngay trên giao diện và ghi rõ trong mã nguồn để không ai hiểu nhầm đó là kết quả đo. Benchmark thật nằm ở Phase 3 trong kế hoạch."

Trước buổi phỏng vấn **phải mở dashboard và chỉ cho BGK thấy banner cam "DỮ LIỆU MÔ PHỎNG"** — chủ động nói trước khi bị hỏi thì thành điểm cộng, để bị phát hiện thì thành điểm trừ nặng.

---

### Q3. "Dataset 134.8 GB — đã tải về chưa? Đã đụng vào dữ liệu thật chưa?"

**Người trả lời chính: Hùng**

> "Chúng em đã kiểm chứng cả hai bộ tồn tại và truy cập được, nhưng **không tải toàn bộ** vì không cần thiết.
>
> Bộ TiniX trên HuggingFace tổ chức theo mã chứng khoán nên tải lọc được. Chúng em đo cụ thể: 16 mã cần dùng chỉ nặng **65 MB** nếu lấy phần văn bản OCR — vì bộ này đã OCR sẵn.
>
> Và chúng em phát hiện một điều quan trọng khi kiểm tra file thật: **văn bản OCR đã giữ nguyên bảng biểu dưới dạng HTML kèm cột Mã số theo Thông tư 200.** Nghĩa là chúng em đọc thẳng được `Mã số 10 = Doanh thu thuần`, `Mã số 20 = Lợi nhuận gộp`. Điều này giúp bỏ hẳn được module nhận dạng bảng nặng nề mà hồ sơ ban đầu dự kiến dùng Table Transformer."

Nếu BGK hỏi *"chứng minh đi"* — mở sẵn một file OCR và chỉ vào đoạn:

```html
<tr><td>Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)</td>
    <td>10</td><td>VI.1</td><td>61.782.609.528.445</td><td>60.368.915.511.505</td></tr>
```

*(VNM, BCTC hợp nhất kiểm toán 2024 — doanh thu thuần 61.782 tỷ đồng.)*

---

### Q4. "Phần narrative lấy ở đâu? BCTC kiểm toán làm gì có Thư gửi cổ đông?"

**Người trả lời chính: Nguyên (Financial Domain Lead)** — đây là câu hỏi sắc nhất mà BGK am hiểu ngành có thể đặt ra.

Nhóm **đã tự phát hiện vấn đề này** và phải chủ động nói ra, vì nó chạm vào giả định gốc của cả đề tài.

> "Thưa thầy/cô, đây đúng là điểm chúng em phải xử lý. Bộ TiniX là **báo cáo tài chính kiểm toán**, mục lục chỉ gồm Thông tin công ty, Báo cáo Ban Điều hành, Báo cáo kiểm toán, ba báo cáo và Thuyết minh — **không có Thư gửi cổ đông và MD&A**. Tức bộ này chỉ cho chúng em nửa phần số liệu.
>
> Nửa narrative nằm trong **Báo cáo thường niên**, có trên Zenodo nhưng đóng gói theo giai đoạn, không tải lẻ theo mã được, riêng gói 2021–2025 đã 56,58 GB.
>
> Chúng em có ba hướng: **một** là crawl Báo cáo thường niên theo mã từ Vietstock hoặc website doanh nghiệp, chỉ khoảng 0,5–1 GB cho 16 mã; **hai** là xử lý gói Zenodo trên Colab rồi chỉ mang phần văn bản đã trích về; **ba**, nếu cả hai không xong kịp, dùng phần **Thuyết minh báo cáo tài chính** làm nguồn narrative — yếu hơn MD&A nhưng vẫn có khẳng định định tính để đối chiếu, và đảm bảo hệ thống luôn chạy được."

Chủ động nêu ra rủi ro này **trước khi** BGK phát hiện là cách ghi điểm mạnh nhất ở tiêu chí "làm chủ bài toán".

---

### Q5. "Ai gán nhãn gian lận? Lấy đâu ra nhãn để huấn luyện?"

**Người trả lời chính: Nguyên + Tài**

Đây là chỗ nhóm có một ý tưởng thật sự tốt, phải nói cho bằng được.

> "Ba nguồn, xếp theo độ rẻ:
>
> **Thứ nhất, nhãn yếu tự động — đây là điểm chúng em tâm đắc nhất.** Rất nhiều doanh nghiệp có chênh lệch giữa báo cáo tài chính tự lập và báo cáo sau kiểm toán. Doanh nghiệp nào có chênh lệch lợi nhuận sau thuế vượt ngưỡng, ví dụ 10%, thì gán nhãn rủi ro. **Nhãn này tính hoàn toàn tự động từ dữ liệu đã có, không tốn một giờ công gán tay nào**, và nó phản ánh đúng bản chất: số liệu doanh nghiệp công bố ban đầu không đáng tin.
>
> **Thứ hai, nhãn cứng**: danh sách xử phạt của UBCKNN — năm 2025 có 194 đến 488 quyết định tùy phạm vi thống kê, cộng với doanh nghiệp bị hủy niêm yết bắt buộc và bị đình chỉ giao dịch.
>
> **Thứ ba, nhãn tay cho phần NNC**: 300–500 cặp claim-evidence, chia đều 4 thành viên. Chúng em sẽ viết hướng dẫn gán nhãn trước, và **đo độ đồng thuận giữa người gán bằng hệ số Cohen's kappa** trên 50 cặp chung để chứng minh nhãn nhất quán."

---

### Q6. "Tại sao là PhoBERT mà không phải một LLM lớn như GPT hay Gemini?"

**Người trả lời chính: Hùng**

> "Ba lý do.
>
> **Một, hallucination.** Đây chính là pain point số 4 trong hồ sơ của chúng em. LLM khi đọc báo cáo tài chính vẫn thường bịa số hoặc trích sai nguồn. Bài toán kiểm toán không chấp nhận điều đó — kiểm toán viên cần minh chứng truy vết được đến từng ô trong bảng.
>
> **Hai, kiểm soát và chi phí.** PhoBERT chạy được trên máy cục bộ, không gửi báo cáo tài chính doanh nghiệp ra dịch vụ bên thứ ba, và không tốn phí theo lượt gọi khi quét hàng trăm nghìn trang.
>
> **Ba, đúng công cụ cho đúng việc.** Chúng em không cần mô hình sinh văn bản, chúng em cần **trích xuất thực thể và phân loại quan hệ** — việc mà một encoder chuyên miền làm tốt hơn và rẻ hơn nhiều.
>
> Việc đối chiếu số liệu chúng em làm bằng **phép tính tường minh**, không giao cho mô hình ngôn ngữ. Đó là điều khiến kết quả kiểm chứng được."

---

### Q7. "Nhóm 4 người, ai làm gì? Có ai làm hộ không?"

| Thành viên | Trường | Vai trò | Phụ trách cụ thể |
|---|---|---|---|
| **Nguyễn Việt Hùng** | ĐH Xây dựng Hà Nội | Trưởng nhóm & AI/NLP Lead | Pipeline, PhoBERT-Fin, tích hợp hệ thống |
| **Nguyễn Hồng Nguyên** | Học viện Tài chính | Financial Domain & Ontology Lead | Ontology VAS theo Thông tư 200, hướng dẫn gán nhãn |
| **Lê Cao Phong** | HV Công nghệ BCVT | Quantum ML & System Lead | Qiskit, QKA, QSVM, benchmark |
| **Mai Đức Tài** | Học viện Tài chính | Financial Risk & Product Lead | Đặc trưng rủi ro tài chính, kịch bản người dùng |

Điểm mạnh nên nhấn: **nhóm liên ngành thật** — hai người tài chính từ Học viện Tài chính, hai người kỹ thuật. Bài toán này bắt buộc phải hiểu cả chuẩn mực kế toán lẫn học máy.

---

### Q8. "Nhóm có dùng AI để làm hồ sơ không?"

Điều 5.2 **cho phép** dùng AI hỗ trợ, Điều 14 chỉ cấm khi *toàn bộ* bài do AI sinh mà không giải thích được. Nên trả lời thoải mái, nhưng phải cụ thể.

> "Có, và chúng em khai báo rõ trong README của kho mã. Chúng em dùng trợ lý lập trình AI để soạn mã giao diện, rà lỗi và gợi ý bố cục tài liệu. Còn bài toán, kiến trúc, lựa chọn công nghệ và toàn bộ lập luận là do nhóm tự đề xuất — chúng em giải thích được từng quyết định, và hôm nay thầy cô hỏi phần nào chúng em cũng trình bày được."

---

## 3. Câu hỏi thường gặp khác

| Câu hỏi | Ý chính khi trả lời |
|---|---|
| "Khác gì MindBridge, Trullion?" | Họ chỉ phân tích số liệu có cấu trúc hoặc chỉ phân tích văn bản, không đối chiếu chéo hai chiều; không hỗ trợ tiếng Việt; không theo chuẩn VAS |
| "Sao không dùng luôn công cụ nước ngoài?" | Thuật ngữ tài chính tiếng Việt và Thông tư 200 khác hẳn GAAP/IFRS; FinBERT và BloombergGPT đều huấn luyện trên tiếng Anh |
| "Prototype bao giờ chạy thật?" | Tuần 1–2 Vòng 2 có pipeline NNC chạy trên dữ liệu thật; tuần 3–4 có lớp lượng tử và benchmark |
| "Nếu độ chính xác thấp thì sao?" | Chúng em đặt ngưỡng thận trọng: NER F1 ≥ 0,80 và NNC accuracy ≥ 0,75, thấp hơn con số trong hồ sơ, để cam kết được thứ làm được |
| "Ai sẽ dùng sản phẩm này?" | Ba nhóm: kiểm toán viên, cơ quan quản lý (UBCKNN/HOSE/HNX), nhà đầu tư tổ chức. Với gần 68% vi phạm là lỗi công bố thông tin, nhu cầu là có thật |
| "Có định thương mại hóa không?" | Trước mắt là công cụ hỗ trợ kiểm toán viên, không thay thế. Định hướng SaaS cho công ty kiểm toán và công ty chứng khoán |
| "Sản phẩm có thể vu oan doanh nghiệp không?" | Hệ thống **không kết luận gian lận**, chỉ đánh dấu điểm bất nhất quán kèm minh chứng để con người xem xét. Luôn có human-in-the-loop |

---

## 4. Việc phải làm trước buổi phỏng vấn

- [ ] Mở `run_demo.bat`, **thử ở chế độ máy bay** để chắc chắn chạy không cần mạng
- [ ] Chụp sẵn ảnh 6 màn hình dashboard, lưu vào điện thoại phòng khi máy hỏng
- [ ] Mở sẵn một file OCR của TiniX ở đoạn có bảng `Mã số 10` để trình khi bị hỏi về dữ liệu
- [ ] Mỗi người đọc kỹ phần câu hỏi thuộc vai trò mình, tập trả lời thành tiếng ít nhất một lượt
- [ ] Chạy thử một lượt hỏi đáp chéo trong nhóm: mỗi người hỏi người khác 3 câu khó nhất
- [ ] In hoặc mở sẵn `docs/cheat-sheet.md`
- [ ] Thống nhất: **ai cũng có quyền nói "chỗ này chúng em chưa làm"** — không ai được bịa để lấp chỗ trống
