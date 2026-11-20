# Dàn ý slide và lời thoại — Vòng 2 (Bán kết)

> **Bản nháp v1 · 19/11/2026 · Người chốt: Tài.** Tệp nộp: `deliverables/AQ2026-R2-AQ2026-064-Slide.pptx` (sinh bằng `deliverables/build/build_slides.py`; sửa nội dung ở script rồi chạy lại, hoặc sửa thẳng trong PowerPoint).
> Dùng cho **10 phút trình bày + 8 phút hỏi đáp** (thời lượng Vòng 2 BTC chưa công bố).
> `⟦CHỜ: …⟧` là số chưa có. **Tệp .pptx nộp đi không được còn ký hiệu ⟦ ⟧.** Số nào đến lúc nộp vẫn chưa có thì ghi "chưa đo".

**Đổi so với v0 (12/11):** (1) chất lượng đo bằng **hai số**: tỷ lệ cờ oan trên dữ liệu thật và recall trên tập chèn lỗi; (2) nhãn 300 cặp là **nhãn bạc do hai tác tử AI gán mù, độc lập**; (3) demo mâu thuẫn dùng **câu chèn lỗi có ghi rõ**; (4) prototype là **trang tĩnh + Pyodide**, không server, không Hugging Face Docker; (5) **lượng tử thua SVM-RBF**, nói thẳng và nói vì sao vẫn có giá trị; (6) **chưa thử nghiệm với kiểm toán viên**, chưa có đối tác; (7) khai báo AI đúng mức thật.

---

## 0. Khung chung

### 0.1. Nhịp bài nói: 9 phút 30 giây, dư 30 giây

| # | Slide (tiêu đề là thông điệp) | Người nói | Giây | Kết thúc |
|---|---|---|---|---|
| 1 | SmartAudit-Quantum | Tài | 20 | 0:20 |
| 2 | Lời văn phải khớp số liệu đã kiểm toán, nhưng vẫn đối chiếu bằng mắt | Tài | 45 | 1:05 |
| 3 | Với công cụ kiểm toán, cáo buộc oan đắt hơn bỏ sót | Nguyên | 35 | 1:40 |
| 4 | Hai luồng gặp nhau tại Mã số | Hùng | 45 | 2:25 |
| 5 | Dữ liệu thật của 16 doanh nghiệp, nguồn có giấy phép | Nguyên | 35 | 3:00 |
| 6 | Chất lượng đo bằng hai số | Nguyên | 35 | 3:35 |
| 7 | Cờ oan giảm mạnh, lỗi chèn bắt 83,0%, nhưng precision chưa đạt 80% | Hùng | 45 | 4:20 ⛳ |
| 8 | **Demo trực tiếp** | Phong | 140 | 6:40 |
| 9 | Lượng tử thua cổ điển, và đội công bố đúng như vậy | Phong | 45 | 7:25 |
| 10 | Hệ thống tự biết giới hạn của mình | Hùng | 30 | 7:55 ⛳ |
| 11 | Chưa thử nghiệm với kiểm toán viên, quy trình đã sẵn sàng | Tài | 35 | 8:30 |
| 12 | Hạ tầng gần 0 đồng; chi phí thật là thời gian xử lý cờ | Tài | 35 | 9:05 |
| 13 | Tóm lại + khai báo AI | Hùng | 25 | 9:30 |

⛳ = mốc bấm giờ. Chậm quá 20 giây ở mốc 7:55 thì slide 12 chỉ nói câu đầu. Tổng thời gian nói: Tài 135 giây · Nguyên 105 · Hùng 145 · Phong 185.

### 0.2. Quy tắc nội dung

1. Mọi số trên slide sinh từ script hoặc tệp kết quả; chân slide ghi nguồn.
2. Không số mô phỏng (QSVM 94,2%, alignment 0,947, "Quantum Advantage +12,7%", VNM "0,84 trên 11 khẳng định").
3. Ca VNM 2024 "tăng 7,6% và 48,4%" **chỉ** được kể như ví dụ cờ oan đội tự phát hiện (câu nói về Angkormilk), không dùng làm ví dụ mâu thuẫn.
4. Ca mâu thuẫn trong demo là câu chèn lỗi, màn hình ghi rõ "câu đã sửa có chủ đích để minh hoạ".
5. Không gọi ai là "đối tác"; không nói "đã thử nghiệm với kiểm toán viên".

### 0.3. Thiết kế (đã áp dụng trong tệp .pptx)

16:9 · nền sáng · màu chủ đạo xanh teal đậm `#0B5563`, điểm nhấn vàng `#C9962B` · font Arial · tiêu đề là một câu thông điệp · sơ đồ và bảng vẽ bằng shape · lời thoại trong speaker notes · ba màu phán quyết: xanh lá ✓ nhất quán, đỏ ✗ mâu thuẫn, xám ? chưa kiểm chứng (luôn kèm ký hiệu).

---

## 1. Mười ba slide chính

### Slide 1 — SmartAudit-Quantum
- Tên đề tài, mã đội AQ2026-064, đội Ngôi nhà Hoa Hồng, 4 thành viên kèm vai trò (không email, số điện thoại, CCCD). Link ⟦CHỜ: link prototype⟧.
- **Tài, 20 giây:** "Kính thưa Ban Giám khảo, chúng em là đội AQ2026-064, Ngôi nhà Hoa Hồng. Chúng em trình bày SmartAudit-Quantum: công cụ đối chiếu lời văn trong báo cáo thường niên với số liệu báo cáo tài chính đã kiểm toán. Mỗi phát hiện đều chỉ tới đúng ô bảng làm bằng chứng."

### Slide 2 — Lời văn phải khớp số liệu đã kiểm toán, nhưng vẫn đối chiếu bằng mắt
- Ví dụ thật, lỗi trình bày: MWG 2022 tr.7 *"doanh thu thuần hơn 133.400 ngàn tỷ đồng"* ↔ BCTC Mã 10 = 133.404,8 tỷ đồng (lệch 1.000 lần do sai đơn vị). **Nguyên kiểm tay lại ô bảng trước khi trình bày.**
- ~702 doanh nghiệp niêm yết HOSE + HNX · VSA 720 yêu cầu xem xét "thông tin khác" · năm 2025 gần 68% hành vi bị xử phạt là lỗi công bố thông tin (Vietstock tổng hợp từ UBCKNN).
- **Tài, 45 giây:** "Đây là một câu có thật trong báo cáo thường niên 2022 của Thế Giới Di Động: doanh thu thuần hơn 133.400 *ngàn tỷ* đồng. Báo cáo tài chính kiểm toán ghi 133.405 *tỷ*. Lỗi nhỏ, nhưng là đúng loại lỗi chuẩn mực kiểm toán 720 yêu cầu kiểm toán viên tìm khi đọc báo cáo thường niên. Với hơn 700 doanh nghiệp niêm yết, việc này vẫn làm bằng mắt, trong khi gần 68% hành vi bị xử phạt năm 2025 là lỗi công bố thông tin. Chúng em tự động hoá bước sàng lọc."

### Slide 3 — Với công cụ kiểm toán, cáo buộc oan đắt hơn bỏ sót
- Ba phán quyết: ✓ nhất quán · ✗ mâu thuẫn · ? chưa kiểm chứng được, kèm lý do. Vết minh chứng: câu gốc (trang BCTN) → Mã số → ô bảng (trang BCTC) → phép tính. Không kết luận gian lận.
- **Nguyên, 35 giây:** "Chúng em đặt một yêu cầu lên trên hết: gắn cờ oan cho doanh nghiệp niêm yết còn tệ hơn bỏ sót, vì kiểm toán viên mất niềm tin ngay lần đầu. Vì vậy hệ thống chỉ có ba phán quyết, và không chắc thì nói 'chưa kiểm chứng được' kèm lý do. Phán quyết nào cũng có vết minh chứng để người dùng tự kiểm lại. Hệ thống không bao giờ kết luận gian lận."

### Slide 4 — Hai luồng gặp nhau tại Mã số: đối chiếu thành phép tra cứu kiểm chứng được
- Sơ đồ: BCTN (PDF) → bóc chữ theo cột → trích khẳng định | BCTC kiểm toán → bóc bảng theo Mã số TT200 → ontology khoản mục · Mã số → đối chiếu 3 chiều (con số · hướng · định tính) → phán quyết + vết minh chứng. Nhánh nét đứt: QKA, thử nghiệm.
- **Hùng, 45 giây:** "Hai luồng chạy độc lập. Luồng lời văn bóc chữ báo cáo thường niên và trích khẳng định có chỉ tiêu, con số, xu hướng. Luồng số liệu bóc bảng báo cáo tài chính theo Mã số Thông tư 200. Hai luồng gặp nhau ở ontology: 'doanh thu thuần' luôn tra về Mã số 10, nên mỗi khẳng định nối tới đúng một ô, không đoán gần đúng. Sau đó hệ thống kiểm ba chiều: con số, hướng tăng giảm, và nhận định định tính quy về tỷ lệ. Lượng tử chỉ được thử ở một nhánh phụ, Phong sẽ trình bày."

### Slide 5 — Dữ liệu thật của 16 doanh nghiệp niêm yết, nguồn có giấy phép
- Phễu (bản 21/09 → dữ liệu 20/11): 338 BCTC TiniX (CC-BY-NC-4.0) → 337 bóc được bảng · 112 BCTN PDF → 98 cặp BCTN–BCTC đưa vào đối chiếu (bản 21/09: 66; 11 tệp không đọc được bị loại) · 695 → 511 khẳng định · 3 ngân hàng ngoài phạm vi · không dữ liệu cá nhân.
- **Nguyên, 35 giây:** "Hai nguồn độc lập: báo cáo tài chính kiểm toán trong bộ dữ liệu mở TiniX, và báo cáo thường niên PDF công khai của 16 mã. Hệ thống bóc được bảng ở 337 trên 338 báo cáo tài chính. Đủ 112 báo cáo thường niên cho 16 mã × 7 năm; 98 cặp báo cáo được đưa vào đối chiếu, tăng từ 66; 11 tệp không đọc được (bản scan, chữ mất dấu, công văn) bị loại và tính vào độ phủ, không giấu đi. Số khẳng định là 511, so với 695 ở bản tháng 9, sau đợt vá lọc phạm vi, trộn cột và câu không phải kết quả. Ba ngân hàng dùng biểu mẫu khác nên nằm ngoài phạm vi." *(Hùng xác nhận cách giải thích mức giảm 695 → 511.)*

### Slide 6 — Chất lượng đo bằng hai số: cờ oan trên dữ liệu thật, recall trên lỗi chèn có kiểm soát
- Trái: 300 cặp, lấy mẫu phân tầng; **nhãn bạc do hai tác tử AI gán mù, độc lập** (không thấy phán quyết máy); đồng thuận 93,7%, kappa 0,86, 19 dòng phân xử; nhãn cuối 7 mâu thuẫn · 84 nhất quán · 209 không kiểm chứng được → **precision, cờ oan**.
- Phải: 570 câu nhất quán bị sửa có chủ đích (đổi giá trị, đổi tỷ lệ, đảo hướng, "kiểm soát chi phí") + 163 câu đối chứng không sửa; **dữ liệu tổng hợp, báo cáo riêng** → **recall theo loại lỗi, báo động giả**.
- **Nguyên, 35 giây:** "Doanh nghiệp lớn hiếm khi viết sai số đã kiểm toán, nên công cụ tốt phải gần như im lặng. Vì vậy chúng em đo bằng hai số. Thứ nhất, trên dữ liệu thật: precision và số cờ oan, với 300 cặp được hai tác tử AI gán nhãn mù và độc lập. Hai bên đồng thuận 93,7%, kappa 0,86; 19 dòng bất đồng được phân xử. Chúng em gọi đó là nhãn bạc, vì chưa phải nhãn của người. Nhãn cuối chỉ có 7 mâu thuẫn thật trong 300 cặp. Thứ hai, để đo khả năng bắt lỗi: lấy câu đúng, sửa có chủ đích, rồi xem hệ thống bắt được bao nhiêu, kèm câu đối chứng không sửa. Đây là dữ liệu tổng hợp và được báo cáo riêng."

### Slide 7 — Cờ oan giảm mạnh, lỗi chèn bắt được 83,0%, nhưng precision trên dữ liệu thật chưa đạt mục tiêu 80%
- **Số tốt:** cờ "cần xem xét" 141 (66 cặp) → 52 (98 cặp); cờ oan ước tính trên tập khẳng định bản 21/09 ~137 → ~23 (giảm ~83%). Tập chèn lỗi (tổng hợp): recall 83,0% (473/570) — đổi giá trị 89%, đổi tỷ lệ 83%, đảo hướng 72%, "kiểm soát chi phí" 38%; 0/163 báo động giả.
- **Số chưa đạt:** precision bản 21/09 2,8% (4/141, KTC95 1,1–7,1%) → bản vá 0% (0/21, KTC95 0–15,5%). Mục tiêu 80% **chưa đạt**.
- **Vì sao:** mâu thuẫn thật rất hiếm (~2% khẳng định), cả 7 ca đều là lỗi trình bày ở tỷ số/cơ cấu (hệ số nợ/VCSH, tỷ trọng tài sản 51% + 69%, Nợ/VCSH 1,82 so với 1,72) — loại hệ thống chưa tính. Bản cũ "bắt" 4 ca nhờ so nhầm tỷ số với khoản mục tiền; bản vá chặn phép so nhầm đó. Bước tiếp: thêm phép tính tỷ số cơ cấu.
- **Hùng, 45 giây:** "Chúng em đưa cả số tốt lẫn số chưa đạt. Bản tháng 9 gắn 141 cờ, chỉ 4 cờ đúng, precision 2,8%. Sau khi vá, trên 98 báo cáo còn 52 cờ; trên cùng tập khẳng định của bản tháng 9, số cờ oan ước tính giảm từ khoảng 137 xuống khoảng 23, tức giảm khoảng 83%. Nhưng 21 cờ trong mẫu không cờ nào là mâu thuẫn thật: precision 0%, khoảng tin cậy 0 đến 15,5%. Mục tiêu 80% chưa đạt. Lý do: mâu thuẫn thật rất hiếm, khoảng 2% khẳng định, và cả 7 ca đều là lỗi trình bày ở tỷ số hoặc cơ cấu, loại hệ thống chưa tính. Bản cũ 'bắt' được 4 ca chỉ nhờ so nhầm tỷ số với khoản mục tiền; bản vá đã chặn phép so nhầm đó. Bước tiếp theo là thêm phép tính tỷ số cơ cấu. Trên tập chèn lỗi, dữ liệu tổng hợp, hệ thống bắt 83%, kém nhất ở câu 'kiểm soát chi phí', và không báo động giả trên 163 câu đối chứng. Thay vì kể, chúng em mở đúng link đã nộp. Mời Phong."

### Slide 8 — Demo trực tiếp: lõi Python chạy ngay trong trình duyệt, không cần server
- Link ⟦CHỜ: link prototype⟧ · không cần tài khoản · dashboard tĩnh 7 trang trên kết quả thật · "Kiểm tra khẳng định" chạy đúng mã Python của pipeline bằng Pyodide, 2–11 ms/câu sau khi nạp. Sơ đồ: trang tĩnh → Pyodide → trích khẳng định → tra Mã số, đối chiếu → vết minh chứng. Ba bước demo (mục 2). Dự phòng: bản chạy tại máy.
- **Phong, 140 giây:** theo kịch bản mục 2.

### Slide 9 — Lượng tử thua cổ điển, và chúng em công bố đúng như vậy
- Bảng (5 phần, seed 42, 8 qubit, statevector): rapidfuzz 0,812 ± 0,030 · **SVM-RBF 0,911 ± 0,051** · QSVM kernel ZZ cố định 0,734 ± 0,055 · QSVM + QKA 0,840 ± 0,048.
- Vì sao vẫn có giá trị: trả lời "lượng tử có giúp không" bằng thí nghiệm có đối chứng; QKA hơn kernel cố định ở 5/5 phần; dẫn tới cải tiến cổ điển (SVM 0,911 > rapidfuzz 0,812 đang dùng); lớp tháo rời được.
- **Phong, 45 giây:** "Lượng tử được thử ở đúng một chỗ: khi bảng không có cột Mã số, phải đoán tên khoản mục thuộc mã nào. Nhãn sinh tự động từ các bảng có Mã số, 282 tên khác nhau. Chúng em huấn luyện kernel lượng tử 8 qubit bằng QKA trên mô phỏng, và so trên cùng cách chia. Kết quả: QKA đạt 0,84, hơn rõ kernel cố định 0,73, nhưng **thua SVM-RBF 0,91**, và huấn luyện chậm hơn khoảng 260 lần. Chúng em công bố đúng như vậy, như đã cam kết. Giá trị nằm ở chỗ: câu hỏi 'lượng tử có giúp không' được trả lời bằng thực nghiệm có đối chứng, và chính thí nghiệm này chỉ ra một cải tiến cổ điển, SVM hơn cách rapidfuzz đang dùng. Lớp lượng tử tháo rời được."

### Slide 10 — Hệ thống tự biết giới hạn của mình
- ✓ Đã chạy, đã đo: pipeline 98 cặp báo cáo, 511 khẳng định, 14 giây · 147 phép kiểm tự động (171 khi có môi trường lượng tử) · 300 cặp nhãn bạc, kappa 0,86 · tập chèn lỗi recall 83,0%, 0/163 báo động giả · QKA có đường cơ sở · dashboard tĩnh 7 trang + Pyodide.
- ? Chưa làm: precision ≥ 80% · tỷ số cơ cấu (Nợ/VCSH, tỷ trọng tài sản) · ngân hàng (TT49), bản scan · câu về bộ phận, công ty con → không kết luận · nhãn người, thử nghiệm KTV · PhoBERT-Fin.
- **Hùng, 30 giây:** "Chúng em nói rõ những gì chưa làm. Precision trên dữ liệu thật chưa đạt 80%, vì hệ thống chưa tính các tỷ số cơ cấu như nợ trên vốn chủ, đúng loại mà cả 7 mâu thuẫn thật rơi vào. Ngân hàng và bản scan nằm ngoài phạm vi. Câu về bộ phận hay công ty con được trả không kết luận. Nhãn đánh giá mới là nhãn bạc do AI gán, và chưa thử nghiệm với kiểm toán viên. Phần trích khẳng định vẫn là bộ luật; mô hình học chỉ vào khi thắng bộ luật trên cùng tập test."

### Slide 11 — Chưa thử nghiệm với kiểm toán viên — quy trình đã sẵn sàng
- Nói thẳng: chưa thử nghiệm, chưa có đối tác. Quy trình trong `docs/thu-nghiem-ktv/`: 2–3 người, hai lượt (làm tay / dùng công cụ) trên hai doanh nghiệp khác nhau, đảo thứ tự; đo thời gian, độ đúng, số cờ bị bác; phỏng vấn 10 phút; báo cáo số thô từng người. Kế hoạch: chạy sau Vòng 2.
- **Tài, 35 giây:** "Chúng em chưa thử nghiệm với kiểm toán viên, vì không kịp tổ chức trước hạn nộp, và cũng chưa có đối tác. Quy trình đã soạn xong: mỗi người đối chiếu một doanh nghiệp bằng tay và một doanh nghiệp khác bằng công cụ, thứ tự đảo giữa các người; chúng em đo thời gian, độ đúng và số cờ bị bác, rồi phỏng vấn mười phút. Chúng em sẽ chạy sau Vòng 2 và báo cáo số liệu thô của từng người, không suy rộng."

### Slide 12 — Chi phí hạ tầng gần bằng 0; chi phí thật là thời gian kiểm toán viên xử lý cờ
- Bảng: trang tĩnh 0 · "Kiểm tra khẳng định" (Pyodide, không server) 0 · pipeline offline CPU 0, 14 giây cho 112 BCTN. Bảo mật: chạy tại máy, không gửi văn bản ra ngoài. Lộ trình: thử nghiệm KTV → nhãn người → mở rộng độ phủ (OCR, Thông tư 99) → mô hình học.
- **Tài, 35 giây:** "Toàn bộ prototype là trang tĩnh; chức năng kiểm tra khẳng định chạy lõi Python ngay trong trình duyệt, nên không có server để trả tiền, để ngủ hay để sập. Pipeline chạy offline trên CPU, 14 giây cho 112 báo cáo thường niên, không gửi dữ liệu ra ngoài, nên công ty kiểm toán cài nội bộ được. Chi phí thật là thời gian kiểm toán viên xử lý cờ, vì vậy giảm cờ oan là việc quan trọng nhất. Lộ trình sau cuộc thi: thử nghiệm với kiểm toán viên, có nhãn của người, rồi mở rộng độ phủ."
- *Bản một câu khi chậm giờ:* "Hạ tầng gần 0 đồng; chi phí thật là thời gian xử lý cờ, nên giảm cờ oan quyết định giá trị."

### Slide 13 — Tóm lại: một công cụ đơn giản, chạy thật, tự biết giới hạn
- Chạy thật trên dữ liệu thật, link công khai, 147 phép kiểm tự động · công bố cả số tốt (cờ oan −83%, recall 83,0%) lẫn số chưa đạt (precision) · mọi phát hiện chỉ tới đúng ô bảng, không chắc thì không kết luận · lượng tử: kết quả âm công bố đầy đủ, kèm đường cơ sở.
- **Khai báo AI (Điều 14), nguyên văn như báo cáo mục 08:** *"Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm."*
- **Hùng, 25 giây:** "Tóm lại, chúng em không hứa một hệ thống làm được mọi thứ. Chúng em mang tới một công cụ chạy thật, đo trung thực, và chỉ ra đúng ô bảng cho mọi kết luận. Chúng em đã dùng AI hỗ trợ và khai báo rõ ở cuối slide; mọi phần chúng em đều giải thích được. Xin cảm ơn Ban Giám khảo."

---

## 2. Demo 140 giây (Phong)

**Chuẩn bị 15 phút trước:** tab 1 trang Tổng quan; tab 2 trang "Kiểm tra khẳng định" đã tải xong (Pyodide nạp ~10 MB, nên mở trước); tab 3 bản chạy tại máy; tệp văn bản có sẵn **câu A, câu B, câu C** để dán.

| Thời điểm | Thao tác | Ý chính |
|---|---|---|
| 0:00–0:15 | Tab 1 | "Đây là link đã nộp, không đăng nhập. Số trên trang là số đo thật vừa trình bày." |
| 0:15–0:55 | Tab 2, chọn VNM 2024, dán **câu A**: "Doanh thu thuần đạt 61.783 tỷ đồng, tăng 2,3% so với năm trước." | "Phần này chạy đúng mã Python của pipeline ngay trong trình duyệt bằng Pyodide, 2–11 ms mỗi câu. Hệ thống tra Mã số 10, trang 10: nhất quán." |
| 0:55–1:30 | Sửa thành **câu B**: "…65.000 tỷ đồng, tăng 7,6%…" | "Câu này em sửa có chủ đích để minh hoạ. Vết minh chứng giữ nguyên, phán quyết đổi thành *cần xem xét*: lệch 5,2% và 5,26 điểm." |
| 1:30–2:05 | Dán **câu C**: câu về Angkormilk ("doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%") | "Đây là ví dụ Vòng 1 của chúng em, hoá ra nói về công ty con. Bản vá trả về không kết luận thay vì cáo buộc." |
| 2:05–2:20 | (nếu còn giờ) câu thật FPT 2022 tr.52 "Doanh thu đạt 44.010 tỷ đồng, tăng 23,4%" | "Một câu thật khác: nhất quán." Quay về slide 9. |

**Đã kiểm (theo điều phối, 19/11):** câu A → Nhất quán (Mã số 10, trang 10); câu B → Cần xem xét (lệch 5,2% và 5,26 điểm); câu C → không kết luận; câu FPT 2022 → nhất quán. Kiểm lại một lần trên đúng link đã nộp trước buổi thi.

**Dự phòng:** trang không phản hồi sau 10 giây → tab 3 (bản tại máy), một câu: "Em chạy đúng chức năng này trên bản tại máy." Mất mạng sau khi trang đã tải: vẫn chạy được vì lõi nằm ở trình duyệt. Thi online: chia sẻ toàn màn hình, tắt thông báo.

---

## 3. Slide dự phòng (sau slide 13, không trình chiếu)

| Slide | Thông điệp | Nội dung chính | Người mở |
|---|---|---|---|
| D1 | Số đo kiểm lại được đến từng cặp | Bảng bản 21/09 vs bản vá: cặp báo cáo 66/98, khẳng định 695/511, cờ 141/52, precision 2,8% (4/141, KTC95 1,1–7,1%) / 0% (0/21, KTC95 0–15,5%), cờ oan ước tính ~137/~23; nhãn bạc đồng thuận 93,7%, kappa 0,86, 19 dòng phân xử; bảng recall tập chèn lỗi theo loại, 473/570, 0/163 báo động giả | Hùng |
| D2 | Lượng tử: thiết lập đủ để chạy lại | TF-IDF ký tự 2–4 → SVD 8 chiều → ZZFeatureMap 8 qubit → QKA (16 tham số, COBYLA 150 lần) → SVC; độ sâu mạch kernel 65, 54 CNOT; alignment 0,293 → 0,511; vì sao không QSVM bất thường (31 dương / 686 cặp) | Phong |
| D3 | Những lỗi đội tự phát hiện | Ví dụ VNM Vòng 1 là Angkormilk; 36/138 BCTC ghi nghìn/triệu đồng; Mã số không duy nhất; "doanh thu 26 đồng"; nguyên nhân cờ oan theo rà sơ bộ | Hùng, Nguyên |
| D4 | Im lặng đúng chỗ | Ngân hàng TT49; bản scan; Thông tư 99 từ 2026; FPT 2018 thoái vốn → "chưa kiểm chứng" | Nguyên |
| D5 | Tuân thủ: dữ liệu, nhãn bạc, khai báo AI | Giấy phép TiniX, NOTICE; không dữ liệu cá nhân; nhãn bạc AI và giới hạn; câu khai báo AI nguyên văn | Tài |

---

## 4. Việc còn lại

| Việc | Ai |
|---|---|
| Thay ⟦CHỜ: link prototype⟧ (slide 1 và 8) khi đã deploy; đây là placeholder duy nhất còn lại, nằm trọn trong một text run nên thay bằng script được | Phong, Tài |
| Kiểm tay ca MWG 2022 tr.7 (slide 2) | Nguyên |
| Thêm mã QR của link prototype vào slide 1 và 8 khi có link | Phong |
| Tập 3 lần có bấm giờ (21–27/11) | Cả đội |
