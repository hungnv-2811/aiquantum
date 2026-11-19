# Câu hỏi phản biện dự kiến — Vòng 2

> **Bản nháp v1 · 19/11/2026 · Người chốt: Tài. Mỗi người tự sửa phần câu trả lời của mình.**
> **Đổi so với v0:** nhãn 300 cặp là **nhãn bạc do hai tác tử AI gán** (không phải người) · chất lượng đo bằng **hai số** (cờ oan trên dữ liệu thật, recall trên tập chèn lỗi tổng hợp) · **chưa thử nghiệm kiểm toán viên, chưa có đối tác** · lượng tử **thua** SVM-RBF · prototype là trang tĩnh + Pyodide. Đã sửa Q1, Q3, Q5, Q9, Q13, Q14, Q18, Q19, Q23, Q25 và thêm **Q26**.
> Dùng kèm `docs/slide/dan-y-slide.md` (các slide dự phòng D1–D6) và `docs/interview-qa.md` (những gì đã nói ở Vòng 1).
> `⟦CHỜ: …⟧` = chưa có số. `⟦KIỂM: …⟧` = người phụ trách phải xác nhận. **Không ai được đọc một câu trả lời còn chứa ⟦ ⟧ trước Ban Giám khảo.** Nếu chưa có số thì nói "chúng em chưa đo".

---

## 0. Nguyên tắc trả lời

Vẫn là nguyên tắc từ Vòng 1: **trung thực về giới hạn ăn điểm hơn tô hồng.** Mỗi câu trả lời không quá 45 giây và có ba bước:

1. **Trả lời thẳng**, trong câu đầu tiên.
2. **Đưa số hoặc bằng chứng**: tên tệp, slide dự phòng, hoặc mở thẳng trên prototype.
3. **Nêu giới hạn và kế hoạch**: "phần này chúng em chưa làm; kế hoạch là…; nếu kế hoạch không thành thì…".

Thêm ba quy tắc:

- Hùng điều phối, chuyển câu hỏi cho đúng người. Người khác chỉ bổ sung khi người trả lời chính ra hiệu, mỗi câu tối đa một lần.
- Không bao giờ nói "đã đo", "đã đạt", "đã có đối tác" nếu chưa có tệp hoặc văn bản chứng minh.
- Câu nào không hiểu thì hỏi lại. Đừng trả lời một câu khác.

**Phân vai:**

| Nhóm câu hỏi | Người trả lời chính |
|---|---|
| Bài toán, người dùng, triển khai, chi phí, thử nghiệm kiểm toán viên | **Tài** |
| Kế toán, chuẩn mực, dữ liệu, gán nhãn, ngân hàng | **Nguyên** |
| Pipeline, độ chính xác, AI/NLP, khai báo AI, lịch sử phát triển | **Hùng** |
| Lượng tử, prototype, triển khai online, cài đặt | **Phong** |

---

## 1. Những gì đã nói ở Vòng 1 và cách nói bây giờ cho nhất quán

Cột "Vòng 1" lấy từ ba nguồn: hồ sơ, `interview-qa.md` và `cheat-sheet.md`, tức là những gì đội đã viết hoặc đã chuẩn bị để nói ở buổi phỏng vấn 09/08. **Ai đã dự buổi phỏng vấn thì đánh dấu câu nào thực sự đã nói ra.** Giám khảo có thể còn nhớ hồ sơ hoặc buổi phỏng vấn đó. Câu nào đã đổi thì **chủ động nói là đã đổi và vì sao**, đừng để giám khảo tự phát hiện.

| Chủ đề | Đã nói ở Vòng 1 | Nói ở Vòng 2 | Nếu bị hỏi "sao khác?" |
|---|---|---|---|
| Ví dụ VNM 2024 | "0,84 trên 11 khẳng định, 2 điểm cần xem" (`interview-qa.md`) | ⟦CHỜ: số trên bản đóng băng⟧ | Số đổi vì đội đã vá nền và đo lại. Mọi số Vòng 2 sinh từ bản đóng băng. Ca 7,6%/48,4%: câu nói về Angkormilk (công ty con ở Campuchia), là **cờ oan**; chủ động kể như lỗi đội tự phát hiện (slide D3) |
| Số test | 70 phép kiểm | 147 phép kiểm tự động (171 khi có môi trường lượng tử) | Mỗi lần sửa đều thêm test hồi quy |
| QKA dùng để làm gì | Cheat sheet ghi "QKA cho xác minh sự kiện tài chính" | **Khớp khoản mục khi bảng thiếu Mã số** (hồ sơ v2/v3) | Khi đã có Mã số, việc liên kết là tra cứu chắc chắn, không cần tìm kiếm. Bài toán tìm kiếm thật chỉ xuất hiện khi thiếu Mã số. |
| Lợi thế lượng tử | "Giá trị là khả năng biểu diễn trên dữ liệu ít mẫu, mất cân bằng" | "Kiểm chứng tính khả thi; không tuyên bố lợi thế" | Vòng 1 đã nói không tuyên bố tăng tốc và sẽ công bố cả kết quả âm. Khả năng biểu diễn là giả thuyết trong tài liệu (Havlíček 2019), có phản biện (Thanasilp 2024, Bowles 2024). Kết quả của đội: QSVM + QKA 0,840 ± 0,048, **thua** SVM-RBF 0,911 ± 0,051 |
| QSVM | Sẽ đối chứng với SVM-RBF, Random Forest, XGBoost | Không làm ở Vòng 2 | Chỉ có 31 mẫu dương trên 686 cặp; khoảng tin cậy rộng hơn mọi khác biệt đo được |
| PhoBERT-Fin | Điểm mới số 2; ngưỡng NER F1 ≥ 0,80 (phỏng vấn) và ≥ 85% (hồ sơ v3) | Chưa làm | Xem Q11 |
| Gán nhãn | "300–500 cặp chia đều 4 người, kappa trên 50 cặp chung" (`interview-qa.md`, Q5); hồ sơ v3: 2 thành viên khối Tài chính gán | 300 cặp; **hai tác tử AI gán mù, độc lập toàn bộ** (nhãn bạc), kappa trên toàn bộ tập | **Đã đổi, phải chủ động nói** (lý do thật do Hùng/Tài chốt, không bịa): nhãn hiện là nhãn bạc và mọi nơi đều ghi rõ là nhãn bạc. Xem Q26 |
| Ngưỡng nghiệm thu | "NER F1 ≥ 0,80, độ chính xác NNC ≥ 0,75" (phỏng vấn) | Precision nhóm "mâu thuẫn" ≥ 80% (hồ sơ v3) | Precision là chỉ số dẫn tới cáo buộc nên quan trọng nhất |
| Prototype | "Bản demo giao diện, dữ liệu mô phỏng, có nhãn cảnh báo" | Dashboard chạy trên kết quả thật, link online, đã gỡ hết số mô phỏng | Đúng kế hoạch đã nói ở Vòng 1 |
| Thống kê xử phạt | 488 quyết định/59,7 tỷ (UBCKNN, đến 30/11/2025) **và** 194 quyết định/hơn 53 tỷ (Vietstock, đến 19/12/2025) | 194 quyết định, như trong hồ sơ | 488 gồm cả cá nhân và mọi loại vi phạm; 194 là thống kê riêng của Vietstock |
| Tỷ lệ phát hiện gian lận | Cheat sheet: "dưới 30% gian lận bị phát hiện trước khi gây thiệt hại (PwC 2024)" | **Không dùng.** Thay bằng số ACFE 2026 trong hồ sơ v3 | Con số PwC không xác minh được nên đã gỡ khỏi hồ sơ |
| Tiến độ | "Tuần 3–4 Vòng 2 có lớp lượng tử và benchmark" | QKA chạy xong ngày 12/11/2026 | Trễ so với dự kiến. Nói thẳng, xem Q24 |
| Thử nghiệm kiểm toán viên | Hồ sơ hứa "sẽ đo" | **Chưa làm**; quy trình đã soạn (`docs/thu-nghiem-ktv/`) | Không kịp trước hạn nộp. Xem Q18, Q25 |

---

## 2. Câu hỏi theo tiêu chí chấm

Mức độ nguy hiểm: 🔴 cao (trả lời sai có thể mất điểm nặng hoặc dính Điều 14) · 🟠 trung bình · 🟢 thấp.

### Tiêu chí 1 — Bài toán thực tiễn (20%)

#### Q1. Kiểm toán viên có thật sự cần công cụ này không? Đối chiếu BCTN với BCTC là việc của ai? 🟠
- **Người trả lời:** Tài (Nguyên bổ sung phần chuẩn mực)
- **Ý trả lời:**
  - Đây là nghiệp vụ có trong chuẩn mực: Chuẩn mực kiểm toán Việt Nam số 720 yêu cầu kiểm toán viên xem xét "thông tin khác", tức báo cáo thường niên, để phát hiện điểm không nhất quán trọng yếu với BCTC ⟦KIỂM: Nguyên đọc bản gốc, nhớ số đoạn⟧.
  - Ngoài kiểm toán viên còn có bộ phận giám sát công bố thông tin và nhà đầu tư tổ chức.
  - **Chưa có bằng chứng từ người dùng:** đội chưa thử nghiệm với kiểm toán viên. Nói thẳng điều này; quy trình thử nghiệm đã soạn và sẽ chạy sau Vòng 2.
- **Bằng chứng:** báo cáo mục 07, phần 5.1; `docs/thu-nghiem-ktv/quy-trinh-thu-nghiem.md`.

#### Q2. Gần 68% vi phạm là lỗi công bố thông tin, nhưng phần lớn là công bố chậm, đâu phải viết sai số? 🟠
- **Người trả lời:** Tài
- **Ý trả lời:**
  - **Đồng ý.** Con số 68% là lỗi công bố thông tin nói chung. Đội không dùng nó để nói 68% là mâu thuẫn giữa lời văn và số liệu.
  - Con số chỉ cho thấy công bố thông tin là trọng tâm giám sát. Chưa có thống kê công khai riêng về loại mâu thuẫn lời văn–số liệu, và một công cụ như của đội chính là cách để bắt đầu đo loại này.
- **Bằng chứng:** Vietstock, "Toàn cảnh án phạt chứng khoán năm 2025" (số liệu đến 19/12/2025).
- **Đừng nói:** "68% vi phạm là do báo cáo sai."

#### Q3. Con số 40–80 giờ mỗi doanh nghiệp lấy ở đâu? 🟠
- **Người trả lời:** Tài
- **Ý trả lời:**
  - Đây là ước tính của nhóm, hồ sơ đã ghi rõ "sẽ kiểm chứng qua kiểm toán viên".
  - **Chưa kiểm chứng**, vì đội chưa thử nghiệm với kiểm toán viên. Phiếu phỏng vấn trong quy trình thử nghiệm có sẵn câu hỏi này; sẽ hỏi khi chạy thử nghiệm sau Vòng 2.
  - Vì vậy mức 8–45 tỷ đồng/năm chỉ là bậc độ lớn từ giả định.
- **Bằng chứng:** `docs/thu-nghiem-ktv/quy-trinh-thu-nghiem.md` (mục 7, phỏng vấn sau buổi).
- **Đừng:** bảo vệ con số 40–80 giờ.

#### Q4. Lời văn mâu thuẫn với số liệu thì có phải gian lận không? 🟢
- **Người trả lời:** Nguyên
- **Ý trả lời:**
  - Không. Mâu thuẫn có thể do lệch kỳ, khác phạm vi (hợp nhất hay riêng lẻ), số đã điều chỉnh, hoặc lỗi đánh máy.
  - Ví dụ thật: năm 2018 FPT có doanh thu giảm 45,6% do thoái vốn, trong khi BCTN ghi tăng trưởng "trong điều kiện so sánh tương đương". Cả hai số đều đúng. Hệ thống trả "chưa kiểm chứng được" kèm lý do.
  - Hệ thống không kết luận gian lận. Nó đưa cho kiểm toán viên danh sách cần xem, kèm bằng chứng.
- **Bằng chứng:** slide D3; mở ca FPT 2018 trên prototype.

### Tiêu chí 2 — Dữ liệu (15%)

#### Q5. Các em tự gán nhãn rồi tự chấm điểm cho mình, sao tin được? 🔴
- **Người trả lời:** Nguyên (Phong bổ sung phần phân xử)
- **Ý trả lời:**
  - Nói rõ trước: nhãn là **nhãn bạc** do hai tác tử AI gán, không phải người. Chi tiết ở Q26.
  - Gán mù: người gán chỉ thấy câu gốc, trang và dòng bảng, **không thấy phán quyết của máy**. Hai bên gán độc lập theo cùng hướng dẫn. Đồng thuận 93,7%, kappa 0,86; 19 dòng phân xử.
  - Nhãn gắn với câu và sự thật trong BCTC, không gắn với phán quyết. Tập test chỉ chạy **một lần**, sau khi đóng băng mã.
  - **Toàn bộ nhãn kèm ghi chú phép tính có trong zip.** Mời giám khảo chọn bất kỳ cặp nào để kiểm cùng bảng gốc.
- **Bằng chứng:** tệp nhãn trong zip ⟦KIỂM: tên tệp⟧; `docs/gan-nhan/huong-dan-gan-nhan.md`; slide D1.

#### Q6. 16 doanh nghiệp có đại diện cho hơn 700 doanh nghiệp không? Có bị overfit không? Sao không tăng cường dữ liệu? 🟠
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - 16 mã trải nhiều ngành: vốn hoá lớn, sản xuất, bán lẻ, tiện ích, và một nhóm từng có vấn đề công bố thông tin. 3 ngân hàng nằm ngoài phạm vi. Giai đoạn 2018–2024.
  - Bộ luật không học tham số, nhưng có thể "quá khớp" vì người sửa luật nhìn dữ liệu. Vì thế đội chia dev/test theo (doanh nghiệp, năm), chỉ sửa luật trên dev, và chạy test một lần.
  - Không tăng cường dữ liệu, vì lõi hệ thống là tra cứu và phép tính, không có tập huấn luyện. Sinh câu giả cho bài toán kiểm toán còn có nguy cơ tạo ra mẫu không có thật. Riêng phần đặc trưng của QKA thì Phong trả lời.
  - **Giới hạn:** chủ yếu là doanh nghiệp lớn, BCTN chất lượng tốt. Bước 1 của lộ trình là đo trên doanh nghiệp mới.
- **Bằng chứng:** `smartaudit/config.py` (danh sách mã); slide D1 (so sánh số dev và test).

#### Q7. Dữ liệu TiniX có giấy phép CC-BY-NC thì có dùng thương mại được không? BCTN lấy ở đâu, có vướng bản quyền không? 🟠
- **Người trả lời:** Nguyên (Tài bổ sung phần thương mại)
- **Ý trả lời:**
  - Dự thi là mục đích phi thương mại, nên đúng giấy phép. Nguồn được ghi trong tệp `NOTICE`.
  - BCTN là tài liệu doanh nghiệp **bắt buộc công bố**. Đội tải bản PDF công khai ⟦KIỂM: Hùng xác nhận nguồn⟧. PDF gốc không đóng vào zip; zip có script tải lại, và chỉ chứa văn bản đã bóc của các doanh nghiệp demo.
  - **Thương mại thì không dùng TiniX được.** Phải tự thu thập từ kênh công bố chính thức hoặc xin phép.
- **Bằng chứng:** `NOTICE` trong zip; báo cáo mục 07, phần 5.3.

#### Q8. 16 trên 93 BCTN là bản scan, tức 17% bị loại. Như vậy mẫu có bị lệch không? 🟠
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - Có, và đội nói rõ: các bản này bị loại khỏi phạm vi và được tính vào chỉ số độ phủ. Ví dụ MWG mất 5 trên 7 năm chỉ vì lý do này.
  - Hệ quả: precision của đội không đại diện cho doanh nghiệp chỉ nộp bản scan.
  - Đội không OCR vội, vì OCR sai một chữ số sẽ sinh ra cờ oan. OCR nằm trong lộ trình sau cuộc thi.
- **Bằng chứng:** báo cáo mục 04 (phễu dữ liệu); slide 5.

### Tiêu chí 3 — Giải pháp, thuật toán (20%)

#### Q9. Precision thực tế là bao nhiêu? Bao nhiêu cờ là oan? Trước khi sửa thì sao? 🔴
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - **Trả lời thẳng: chưa đạt mục tiêu 80%.** Precision nhóm "cần xem xét" trên dữ liệu thật (300 cặp nhãn bạc): bản 21/09 là **2,8%** (4/141, KTC95 1,1–7,1%); bản vá 19/11 là **0%** (0/21, KTC95 0–15,5%).
  - **Cái đã cải thiện:** cờ giảm 141 → 35; cờ oan ước tính trên toàn bộ khẳng định ~137 → ~23 (giảm ~83%).
  - **Vì sao precision vẫn 0%:** mâu thuẫn thật rất hiếm (~2% khẳng định; nhãn cuối chỉ 7/300 cặp), và cả 7 ca đều là lỗi trình bày ở tỷ số/cơ cấu (hệ số nợ/VCSH; tỷ trọng tài sản ghi 51% + 69%; Nợ/VCSH ghi 1,82 trong khi BCTC cho 1,72) — loại phép tính hệ thống chưa có. Bản cũ "bắt" được 4 ca chỉ nhờ so nhầm tỷ số với khoản mục tiền; bản vá đã chặn phép so nhầm đó, nên 4 "cờ đúng" ấy biến mất. **Đừng** trình bày 2,8% như thành tích.
  - **Khả năng bắt lỗi đo riêng trên tập chèn lỗi** (dữ liệu tổng hợp, báo cáo riêng): recall 82,6% (347/420) — đổi giá trị 86%, đổi tỷ lệ 87%, đảo hướng 71%, "kiểm soát chi phí" 47%; 0/122 báo động giả trên câu đối chứng.
  - **Bước tiếp:** thêm phép tính tỷ số cơ cấu (Nợ/VCSH, tỷ trọng tài sản), rồi đo lại trên cùng 300 cặp. Mở slide 7 và D1.
- **Bằng chứng:** đầu ra `evaluate.py`; slide 7 và D1; slide D3 (nguyên nhân cờ oan).
- **Đừng nói:** "gần đạt", "precision cao"; đừng gộp 82,6% của tập chèn lỗi vào số trên dữ liệu thật; đừng nói "hệ thống không có cờ sai" (35 cờ vẫn còn, ước tính ~23 cờ oan).

#### Q10. Ngưỡng dung sai 1% lấy ở đâu? Nếu báo cáo làm tròn số thì sao? 🟠
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - Ngưỡng nằm trong `smartaudit/config.py` (`NUMERIC_TOLERANCE`), áp dụng cho ⟦KIỂM: Hùng giải thích chính xác cách áp ngưỡng cho giá trị và cho tỷ lệ tăng trưởng⟧.
  - Lý do chọn: BCTN thường làm tròn tỷ lệ đến một chữ số thập phân.
  - Kiểm tra độ nhạy trên tập dev: ngưỡng 0,5% cho precision ⟦CHỜ⟧, ngưỡng 2% cho ⟦CHỜ⟧. Tiêu chí 3 của Thể lệ yêu cầu "tham số chính được nêu ra và kiểm tra ở mức cơ bản".
- **Bằng chứng:** `smartaudit/config.py`; bảng độ nhạy (nếu kịp làm thì thêm vào D1).

#### Q11. Đây chỉ là regex và bộ luật, AI nằm ở đâu? Hồ sơ hứa PhoBERT-Fin, sao không có? 🔴
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - **Thừa nhận thẳng:** chưa fine-tune PhoBERT.
  - Lý do: không có tập đánh giá thì không chứng minh được mô hình thắng bộ luật. Tập đó vừa mới có (300 cặp). Thể lệ Điều 10 cũng ưu tiên mô hình đơn giản mà chạy ổn định.
  - Chỗ bộ luật đang thua có ví dụ cụ thể (đã chuẩn bị từ Vòng 1, `interview-qa.md` Q1d): câu *"duy trì chính sách quản lý hàng tồn kho"* bị hiểu nhầm là tồn kho đi ngang. Muốn phân biệt được thì cần phân tích quan hệ trong câu, đó là chỗ mô hình ngôn ngữ cần vào.
  - Kế hoạch: chỉ thay bộ luật khi mô hình thắng trên **cùng tập test**.
  - Phần học máy hiện có: ontology sinh tự động từ dữ liệu; QKA và SVM trong thử nghiệm khớp khoản mục.
- **Bằng chứng:** `smartaudit/nlp/claims.py` (docstring ghi rõ lựa chọn có chủ ý); slide 10.
- **Đừng nói:** "đang fine-tune", "sắp xong".

#### Q12. Sao không đưa thẳng hai báo cáo cho ChatGPT hay Gemini đọc? 🟠
- **Người trả lời:** Hùng
- **Ý trả lời:** giống Vòng 1 (`interview-qa.md`, Q6):
  - Mô hình ngôn ngữ lớn có thể bịa số.
  - Kiểm toán viên cần kết quả **truy được đến ô bảng**. Phép đối chiếu là phép tính tường minh, ai cũng kiểm lại được.
  - Không gửi báo cáo ra dịch vụ bên ngoài.
  - **Giới hạn:** đội chưa chạy so sánh với một mô hình ngôn ngữ lớn trên cùng tập test. Nếu giám khảo thấy cần, đó là một thí nghiệm làm được ngay vì tập nhãn đã có.
- **Bằng chứng:** vết minh chứng trên prototype.

#### Q13. Lượng tử thua cổ điển thì giữ làm gì? Có phải gắn chữ Quantum cho đẹp? 🔴
- **Người trả lời:** Phong
- **Ý trả lời:**
  - **Thua, và đội nói thua.** 5 phần, cùng cách chia: QSVM + QKA 0,840 ± 0,048 accuracy; SVM-RBF trên cùng 8 chiều 0,911 ± 0,051; rapidfuzz (cách hệ thống đang dùng) 0,812 ± 0,030; kernel lượng tử cố định 0,734 ± 0,055. QKA thua SVM-RBF ở 5/5 phần và huấn luyện chậm hơn khoảng 260 lần.
  - **Vì sao vẫn giữ:**
    - Trả lời câu hỏi "lượng tử có giúp không" bằng thực nghiệm có đối chứng trên dữ liệu tiếng Việt thật, đúng cam kết công bố cả kết quả âm trong hồ sơ, đúng tinh thần Bowles và cộng sự (2024).
    - QKA có tác dụng thật: hơn kernel cố định ở 5/5 phần (0,734 → 0,840), alignment huấn luyện 0,293 → 0,511. Khoảng cách với RBF nằm ở khâu tối ưu kernel (COBYLA kẹt cực trị địa phương), không ở số qubit.
    - Thí nghiệm dẫn tới một cải tiến cổ điển: SVM 0,911 vượt rapidfuzz 0,812. Nhưng rapidfuzz ở ngưỡng 88 chỉ trả lời 49,6% số tên và đúng 98,4% trong số đó, nên nếu đổi phải giữ cơ chế "không chắc thì im lặng".
    - Lớp lượng tử cắm qua đúng một ma trận kernel, tháo ra hay thay bằng RBF không phải sửa gì khác.
  - Không tuyên bố lợi thế lượng tử: 8 qubit vẫn mô phỏng được trên máy cổ điển, dữ liệu nhỏ (282 tên).
  - Chữ "Quantum" trong tên đề tài là cam kết thử nghiệm có đối chứng, không phải lời hứa về lợi thế.
- **Bằng chứng:** slide 9, D2; `docs/quantum-poc.md`; `results/qka_results.json`; `python scripts/run_qka.py --quick` (~1 phút).
- **Đừng nói:** "lượng tử gần bằng cổ điển", "trên phần cứng thật sẽ tốt hơn".

#### Q14. Giải thích feature map, vì sao lại là 8 qubit, độ sâu mạch bao nhiêu? Hiện tượng giá trị kernel co cụm thì sao? 🟠
- **Người trả lời:** Phong
- **Ý trả lời:**
  - Tên khoản mục → TF-IDF n-gram ký tự 2–4 → TruncatedSVD còn 8 chiều (giữ 53–54% phương sai) → co giãn về [0, π] → ZZFeatureMap 8 qubit, reps=2 → QKA thêm 16 tham số (8 hệ số co giãn, 8 góc RY), COBYLA 150 lần, tối đa hoá centered kernel-target alignment → SVC.
  - Mạch đo một ô kernel: độ sâu 65, 54 CNOT. Huấn luyện QKA ~217 giây/phần, suy luận ~23 ms/mẫu. Kiểm chứng chéo 5 lần, seed 42, statevector.
  - Kernel cố định bị co cụm: trung bình ngoài đường chéo chỉ 0,011, mọi cặp tên khác nhau đều coi là không giống. QKA làm kernel rộng ra (29/40 hệ số co về |λ| < 0,5). Giữ ít qubit một phần vì lý do này (Thanasilp và cộng sự, 2024).
  - Giảm chiều không phải nút thắt: SVM tuyến tính trên TF-IDF đầy đủ đạt 0,904, không hơn RBF 8 chiều (0,911).
  - Phong phải tự chạy lại được `scripts/run_qka.py` trước mặt giám khảo nếu được yêu cầu.
- **Bằng chứng:** slide D2; mã nguồn `smartaudit/quantum/` ⟦KIỂM: tên thư mục⟧.

### Tiêu chí 4 — Prototype (20%)

#### Q15. Demo có phải dựng sẵn không? Tôi gõ một câu bất kỳ có được không? 🟠
- **Người trả lời:** Phong
- **Ý trả lời:**
  - **Được, trong phạm vi:** chọn một doanh nghiệp và năm có trong dữ liệu, gõ câu, hệ thống tính ngay. Mời giám khảo gõ thử.
  - Nếu hệ thống không đọc được câu, nó trả "chưa kiểm chứng được" kèm lý do. Đó là hành vi đúng thiết kế.
  - Không tải PDF tuỳ ý được: xử lý một BCTN mới cần tải và bóc mất ⟦CHỜ⟧, và có rủi ro gặp bản scan. Việc này nằm ngoài phạm vi Vòng 2.
  - **Chuẩn bị:** trước 27/11, các thành viên gõ thử 20 câu "khó" (câu sai đơn vị, câu nói về kỳ khác, câu không có chỉ tiêu) để biết hệ thống phản ứng ra sao.

#### Q16. Ở Vòng 1 dashboard có số 94,2% và +12,7%. Giờ còn số mô phỏng nào không? Sao số VNM lại khác? 🔴
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - Đã gỡ toàn bộ. Mọi số trên dashboard sinh từ `evaluate.py` và JSON xuất từ pipeline.
  - Số VNM thay đổi qua các mốc: Vòng 1 là 0,84 trên 11 khẳng định; ngày 21/09 là 0,77 trên 8; bản đóng băng là ⟦CHỜ⟧. Thay đổi là do vá lỗi.
  - Ca "7,6% và 48,4%" là câu nói về Angkormilk, công ty con ở Campuchia, không phải Vinamilk hợp nhất (Mã 10 chỉ +2,34%). **Nói thẳng:** "Ví dụ chúng em đưa ra ở Vòng 1 hoá ra là cờ oan, và đó chính là lý do chúng em làm bộ lọc phạm vi và đo bằng nhãn mù."
- **Bằng chứng:** trang "Đánh giá" trên prototype; slide 7.

#### Q17. Ban Giám khảo tự cài từ zip mất bao lâu? Có cần mạng hay tài khoản không? 🟢
- **Người trả lời:** Phong (Nguyên bổ sung)
- **Ý trả lời:**
  - Nguyên, thành viên không viết mã, đã tự cài theo Hướng dẫn trên một laptop sạch: mất ⟦CHỜ⟧ phút; `pytest` cho kết quả ⟦CHỜ: N passed⟧.
  - Dữ liệu mẫu chạy không cần mạng. Không cần tài khoản.
  - Hướng dẫn mục 8 có đầu ra kỳ vọng để đối chiếu.
- **Bằng chứng:** `AQ2026-R2-AQ2026-064-Huong_dan.pdf`.

### Tiêu chí 5 — Triển khai thực tế (15%)

#### Q18. Đã có đơn vị nào muốn dùng chưa? Ai sẽ trả tiền? 🔴
- **Người trả lời:** Tài
- **Ý trả lời (tình trạng thật ngày 19/11):**
  - **"Chưa có."** Đội chưa có đối tác, chưa có thư bày tỏ quan tâm, và chưa thử nghiệm với kiểm toán viên vì không kịp tổ chức trước hạn nộp.
  - Đã chuẩn bị: quy trình thử nghiệm, thư mời, phiếu ghi và mẫu biên bản xác nhận (`docs/thu-nghiem-ktv/`). Bước 1 của lộ trình sau Vòng 2 là chạy thử nghiệm với 2–3 kiểm toán viên hoặc giảng viên kiểm toán, rồi tìm một đơn vị thử nghiệm trước mùa BCTN.
  - **Ai trả tiền:** đội chưa kiểm chứng mô hình kinh doanh. Lối vào rẻ nhất là giảng dạy kiểm toán (hợp giấy phép phi thương mại của dữ liệu) và công ty kiểm toán vừa và nhỏ. Lưu ý Thể lệ Điều 16 về sở hữu trí tuệ.
  - *Nếu đến ngày thi đã có thử nghiệm hoặc văn bản thật thì cập nhật câu này, kèm tệp chứng minh.*
- **Đừng nói:** "đối tác", "đã có đơn vị quan tâm", "kiểm toán viên đánh giá cao" khi không có văn bản.

#### Q19. Chi phí vận hành thật là bao nhiêu? Một báo cáo xử lý mất bao lâu? Mở rộng lên 700 doanh nghiệp thì sao? 🟠
- **Người trả lời:** Tài (Phong bổ sung phần hạ tầng)
- **Ý trả lời:**
  - Trang tĩnh: 0 đồng. Chức năng "Kiểm tra khẳng định" chạy lõi Python ngay trong trình duyệt bằng Pyodide, **không có server**, nên cũng 0 đồng (người xem tải ~10 MB lần đầu). Không dùng Docker Space của Hugging Face (cần gói PRO 9 USD/tháng, giá tra 12/11/2026).
  - Pipeline: 77 giây cho 93 BCTN trên CPU (khoảng 1 giây mỗi báo cáo khi đã bóc chữ; bóc PDF lần đầu khoảng 12 giây mỗi báo cáo, theo báo cáo mục 07). Mở rộng lên 700 doanh nghiệp vẫn chỉ cỡ vài giờ máy mỗi năm.
  - Hồ sơ từng ghi "dưới 1 phút mỗi báo cáo". Đó là **ngân sách thiết kế**, không phải số đo.
  - Chi phí lớn nhất là thời gian kiểm toán viên xử lý cờ, và bảo trì ontology.
- **Bằng chứng:** báo cáo mục 07, Bảng 7.1; slide D6.

#### Q20. Đưa tên doanh nghiệp niêm yết thật kèm nhãn "mâu thuẫn" lên web công khai, nếu sai thì sao? 🔴
- **Người trả lời:** Tài (Nguyên bổ sung)
- **Ý trả lời:**
  - Prototype có banner ghi rõ "kết quả máy, chưa qua kiểm toán viên, không phải kết luận gian lận", kèm precision đo được ⟦KIỂM: banner đã có trên bản deploy⟧.
  - Không chắc thì hệ thống trả "chưa kiểm chứng".
  - Khi triển khai thật sẽ **không công khai danh sách cờ**. Công cụ dùng nội bộ cho kiểm toán viên; con người xác minh trước khi bất kỳ nhận định nào được đưa ra ngoài.
- **Bằng chứng:** giao diện prototype; báo cáo mục 07, phần 5.3.

#### Q21. Thông tư 99/2025 thay Thông tư 200 từ năm 2026. Hệ thống neo vào Mã số của Thông tư 200 có lỗi thời không? 🟠
- **Người trả lời:** Nguyên
- **Ý trả lời:**
  - Đúng: Thông tư 99/2025/TT-BTC áp dụng cho năm tài chính bắt đầu từ 01/01/2026. BCTC năm 2026, công bố năm 2027, sẽ theo biểu mẫu mới.
  - Mã số chỉ tiêu trong biểu mẫu mới: ⟦KIỂM: Nguyên đối chiếu phụ lục biểu mẫu BCTC⟧.
  - Ontology được sinh tự động từ dữ liệu, nên chỉ cần thêm bảng ánh xạ Mã số cũ ↔ mới. Dữ liệu 2015–2025 vẫn theo Thông tư 200, nên phân tích nhiều kỳ phải dùng ánh xạ.
- **Bằng chứng:** báo cáo mục 07, phần 5.3 và 5.4.

#### Q22. Bỏ ngân hàng ra thì còn ý nghĩa gì với thị trường? 🟠
- **Người trả lời:** Nguyên
- **Ý trả lời:**
  - Ngân hàng nằm ngoài phạm vi vì biểu mẫu khác: Thông tư 49 không dùng hệ Mã số của Thông tư 200. Điều này đã tuyên bố từ hồ sơ.
  - Hệ thống im lặng đúng chỗ: với 3 ngân hàng, ⟦CHỜ: số trên bản đóng băng; ngày 21/09 là 103/103⟧ khẳng định "chưa kiểm chứng", không có cờ oan nào.
  - Về số lượng, ngân hàng chỉ là phần nhỏ trong các doanh nghiệp niêm yết. Muốn mở rộng thì phải có một ontology riêng cho mỗi nhóm định chế; việc này thuộc lộ trình sau cuộc thi.
- **Bằng chứng:** slide D4; huy hiệu "ngoài phạm vi" trên prototype.

### Tiêu chí 6 — Trình bày, tài liệu, tuân thủ (10%)

#### Q23. Đội dùng AI đến mức nào? Phần lượng tử hay báo cáo có phải do AI viết không? 🔴
- **Người trả lời:** Hùng (Phong trả lời phần lượng tử)
- **Ý trả lời:**
  - **Có dùng nhiều, và đã khai báo đúng mức** trong báo cáo (ngay trên khối cam kết), README và slide 13. Đọc nguyên văn: *"Đội dùng trợ lý và tác tử AI (Claude) để viết nháp mã nguồn, nháp tài liệu và slide, gán nhãn bạc cho tập đánh giá 300 cặp, và rà soát. Ý tưởng, bài toán, kiến trúc, các quyết định và việc kiểm duyệt cuối do đội thực hiện. Các thành viên chịu trách nhiệm và giải thích được mọi phần của sản phẩm."*
  - Cụ thể: AI viết nháp mã (gồm phần QKA), nháp báo cáo, slide, hướng dẫn gán nhãn, quy trình thử nghiệm; hai tác tử AI gán nhãn bạc 300 cặp; AI rà soát lỗi.
  - Đội làm: chọn bài toán và người dùng; kiến trúc neo Mã số; quyết định phạm vi và nguyên tắc "không chắc thì im lặng"; quyết định đo bằng hai số; duyệt, chạy lại và kiểm tra kết quả; thuyết trình.
  - Mời giám khảo hỏi bất kỳ dòng mã hay bước nào. Phong chạy lại QKA và giải thích từng bước; Hùng giải thích pipeline.
  - Thể lệ Điều 14 cấm dùng AI tạo sinh làm *toàn bộ* bài mà không có đóng góp đáng kể của con người, và cho phép AI hỗ trợ nếu khai báo rõ. Đội khai báo đủ, kể cả việc AI gán nhãn.
- **Đừng nói:** "chỉ dùng để sửa chính tả", "nhãn do thành viên gán", và đừng chối. Đừng nhận đã tự làm phần nào mà mình không giải thích được.

#### Q24. Lịch sử git cho thấy mã được commit dồn vào tháng 11? Sáu tuần xây dựng các em đã làm gì? 🔴
- **Người trả lời:** Hùng
- **Ý trả lời:**
  - **Nói thật:** mã được viết trong tháng 8–9/2026 trên máy cá nhân và chưa được đưa vào git. Đó là sơ suất trong quản lý mã.
  - **Phải tự biết bằng chứng về thời gian còn yếu.** Git chỉ có các commit ngày 08/08/2026, gồm hồ sơ, dashboard mô phỏng và tài liệu phỏng vấn; bản commit của tài liệu phỏng vấn **chưa** có số liệu pipeline. Ngoài ra chỉ có ngày sửa tệp (mã nguồn chính và `results/nnc_results.json` sửa lần cuối 21/09/2026) và các tài liệu nội bộ chưa commit (`docs/ke-hoach-hoan-thien.md` ghi số đo ngày 21/09).
  - Vì thế bằng chứng mạnh nhất là **đội giải thích được từng module và từng lỗi đã gặp**: Mã số không duy nhất, FPT "26 đồng", thoái vốn FPT 2018 (slide D3). Mời giám khảo hỏi sâu bất kỳ phần nào.
  - Thể lệ Điều 16 khoản 4 coi lịch sử phát triển là bằng chứng. Đội nên giữ nguyên lịch sử commit từ 12/11 trở đi, không viết lại lịch sử (không rebase hay squash).
  - Tiến độ từ cuối tháng 9 đến đầu tháng 11: ⟦KIỂM: Hùng nói đúng lý do thật, không bịa⟧. Từ 12/11, đội tập trung vào đo lường, triển khai và lượng tử.
- **Đừng:** bịa lý do, hay nói mọi thứ làm trong một tuần.

#### Q25. Sao chưa thử nghiệm với kiểm toán viên? Nếu làm với 2–3 người thì chứng minh được gì? 🟠
- **Người trả lời:** Tài
- **Ý trả lời:**
  - **Chưa làm** vì không kịp tổ chức trước hạn nộp. Nói đúng như vậy, không thêm lý do khác.
  - Quy trình đã soạn đủ: hai lượt làm tay / dùng công cụ trên hai doanh nghiệp khác nhau, đảo thứ tự, đo thời gian, độ đúng, số cờ bị bác, phỏng vấn 10 phút, xin đồng ý ghi nhận. Sẽ chạy sau Vòng 2.
  - Khi làm với 2–3 người: **không chứng minh được hiệu quả** và không suy rộng; chỉ kiểm tra người thật dùng được không, thu nhận xét có cấu trúc, và kiểm chứng giả định thời gian. Báo cáo số liệu thô của từng người.
  - **Thiên lệch đã biết:** người tham gia biết đây là sản phẩm sinh viên nên có thể dễ dãi; mới đo bước đối chiếu, chưa đo bước tự tìm khẳng định.
- **Bằng chứng:** `docs/thu-nghiem-ktv/quy-trinh-thu-nghiem.md`; `phieu-ghi-ket-qua.csv` (mẫu trống).

#### Q26. Nhãn đánh giá do AI gán thì tin được không? Có phải AI tự chấm AI? 🔴
- **Người trả lời:** Nguyên (Hùng bổ sung phần số đo)
- **Ý trả lời:**
  - **Trả lời thẳng:** đó là **nhãn bạc**, không phải nhãn vàng của người. Đội gọi đúng tên ở mọi nơi và không trình bày nó như đáp án của chuyên gia.
  - **Vì sao vẫn dùng được ở mức hiện tại:**
    - Hai tác tử AI gán **mù** (không thấy phán quyết của hệ thống, không thấy nhãn của nhau) và **độc lập**, theo cùng hướng dẫn gán nhãn có quy tắc làm tròn, phạm vi hợp nhất/riêng, ví dụ khó.
    - Mỗi nhãn kèm **ghi chú phép tính tới Mã số và ô bảng**, nên ai cũng kiểm lại được bằng tay. Mời giám khảo chọn ngẫu nhiên vài cặp để kiểm.
    - Độ đồng thuận giữa hai bên: 93,7%, kappa 0,86; 19 dòng bất đồng được phân xử. Nhãn cuối: 7 mâu thuẫn · 84 nhất quán · 209 không kiểm chứng được.
    - Tác tử gán nhãn khác với hệ thống được đo: hệ thống là bộ luật và phép tính tường minh, không phải mô hình ngôn ngữ, nên không phải "AI tự chấm chính nó". Nhưng thiên lệch chung của hai tác tử cùng loại là có thật, nên kappa cao chưa chắc là đúng.
  - **Giới hạn và kế hoạch:** chưa có nhãn của người; bước 2 của lộ trình là để người có chuyên môn gán lại (hoặc ít nhất kiểm một mẫu con) và so với nhãn bạc. Số đo trên tập chèn lỗi ít phụ thuộc nhãn AI hơn: chỉ cần câu gốc thật sự nhất quán, còn câu nào bị sửa và sửa thế nào thì biết chắc.
- **Bằng chứng:** tệp nhãn kèm ghi chú trong zip ⟦KIỂM: tên tệp⟧; `docs/gan-nhan/huong-dan-gan-nhan.md`; slide D5.
- **Đừng nói:** "nhãn do chuyên gia gán", "nhãn AI chính xác như người".

---

## 3. Năm câu nguy hiểm nhất — tập trước tiên

| # | Câu | Vì sao nguy hiểm | Người trả lời |
|---|---|---|---|
| 1 | Q9 — Precision thật, trước và sau khi sửa | Là con số quyết định công cụ có dùng được không. Nếu dưới 80% mà nói lấp lửng thì mất điểm ở cả tiêu chí 3 lẫn 4. | Hùng |
| 2 | Q23 — Đội dùng AI đến mức nào | Dính Điều 14: AI tạo sinh làm toàn bộ bài dự thi mà con người không giải thích được thì bị cấm. Trả lời mập mờ là rủi ro bị xử lý vi phạm. | Hùng, Phong |
| 3 | Q13 — Lượng tử thua cổ điển, có phải gắn mác | Tên đề tài có chữ "Quantum". Chối kết quả âm hoặc phóng đại kết quả dương đều mất uy tín. | Phong |
| 4 | Q11 — Chỉ là bộ luật, PhoBERT-Fin đâu | Hồ sơ đã hứa một điểm mới nhưng chưa làm. Cần thừa nhận và có lập luận dựa trên Điều 10. | Hùng |
| 5 | Q18 — Đã có đối tác chưa | Mức 90–100 của tiêu chí 5. Rất dễ bị cám dỗ phóng đại. | Tài |

Hai câu sát nút: **Q24** (lịch sử git, sáu tuần làm gì) và **Q20** (công khai nhãn "mâu thuẫn" cho doanh nghiệp thật). **Q26** (nhãn do AI gán) gần như chắc chắn bị hỏi ngay sau Q9 hoặc Q23; Nguyên tập cùng Hùng.

---

## 4. Placeholder trong tệp này: ai cung cấp

| Placeholder | Ai | Nguồn |
|---|---|---|
| Số VNM trên bản đóng băng, kết luận ca 7,6%/48,4% | Hùng, Nguyên | `audit_report.py VNM 2024`; kiểm tay |
| Số test cuối | Hùng | `pytest` trên bản đóng băng |
| Precision, khoảng tin cậy, n, kappa, độ nhạy ngưỡng | Hùng, Phong | `evaluate.py` |
| Cách áp ngưỡng dung sai | Hùng | `smartaudit/nnc/checker.py` |
| Kết quả QKA, chi tiết mạch, tên tệp | Phong | `results/qka_results.json` |
| Ngày xong QKA | Phong | — |
| Thời gian cài trên máy sạch, N passed | Nguyên | 19/11 |
| Thời gian xử lý mỗi báo cáo, chi phí API | Hùng, Phong | Đo trên bản đóng băng |
| Câu trả lời kiểm toán viên (giờ thực tế, có dùng không), tình trạng đối tác | Tài | Phiếu thử nghiệm, văn bản xác nhận |
| VSA 720 (số đoạn), Mã số theo Thông tư 99 | Nguyên | Văn bản gốc |
| Nguồn BCTN trong NOTICE, phạm vi phần mã AI viết nháp, lý do tiến độ tháng 10 | Hùng | Repo, sự thật nội bộ |
| Số khẳng định ngân hàng trên bản đóng băng | Hùng | `run_nnc.py` |
| Banner trên bản deploy | Phong | Bản deploy |
