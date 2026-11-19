# Rà soát ứng viên 4 ca demo — BẢN NHÁP

*Agent Nghiệp vụ soạn ngày 12/11/2026 cho Nguyên duyệt. Mọi con số dưới đây đã được tính lại từ ô bảng TiniX gốc và đọc lại ngữ cảnh BCTN. Tuy vậy, theo quy tắc ở mục 6.5 kế hoạch Vòng 2, **Nguyên vẫn phải tự kiểm tay từng ca đến từng ô trước khi đưa lên slide hoặc video**.*

Dữ liệu dùng: `results/nnc_results.json` (bản baseline, 66 cặp BCTN–BCTC, 695 khẳng định), BCTC trong `data/raw/tinix/ocr_results/`, văn bản BCTN trong `data/interim/bctn_text/`, PDF BCTN trong `data/raw/bctn/`.
"Trang BCTN" là số trang PDF (dấu `===== PAGE n` trong tệp văn bản). "Trang TiniX" là dấu `PAGE` trong tệp OCR của BCTC. Đơn vị tiền là tỷ đồng, trừ khi ghi khác.

---

## 0. Đọc trước: kết luận chính

1. **VNM 2024: cả hai cờ "mâu thuẫn" đều là cáo buộc oan.** Câu *"doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%"* nói về **Angkormilk**, công ty con 100% của Vinamilk tại Campuchia, không nói về Vinamilk hợp nhất. Câu ở trang 59 nằm trong mục "Các đơn vị thành viên", và tên Angkormilk chỉ in ở nhãn bên lề nên không lọt vào câu. Câu ở trang 31 là câu **ghép sai do trộn cột**: nửa đầu "Vinamilk đã đạt nhiều" thuộc cột trái (đoạn về giải thưởng), nửa sau thuộc cột phải (đoạn về Angkormilk). Chi tiết ở mục 2.
2. **Không tìm được ca "mâu thuẫn" thật nào trong 141 cờ của bản baseline.** Đọc lại cả 141 cờ (câu + minh chứng, mở ngữ cảnh trang và ô bảng ở các ca đại diện): 138 cờ có nguyên nhân oan gọi tên được, 3 cờ cần người trong nghề xem. Tỷ lệ này khớp với nhận định trước đó trong kế hoạch, "soi tay 8 ca thì 6–7 ca là cáo buộc oan", và còn nặng hơn. Đây là **nhãn sơ bộ của agent, không thay được bộ 300 nhãn mù**. Phân loại từng ca: `docs/demo/_scratch/phan_loai_mau_thuan.csv`.
3. Hệ quả cho bốn kịch bản:

| Kịch bản | Ứng viên tốt nhất | Mức chắc chắn | Điều kiện để lên slide |
|---|---|---|---|
| (a) Nhất quán – đối chứng | **FPT 2022, BCTN tr.52**: *"Doanh thu đạt 44.010 tỷ đồng, tăng 23,4% … LNTT đạt 7.662 tỷ đồng, tăng 20,9%"*. Dự phòng: VNM 2024 tr.31 (tổng doanh thu, LNTT), PLX 2018 tr.44 | **Cao.** Mọi con số khớp ô bảng | Nếu dùng màn hình *cả báo cáo* VNM 2024 thì phải vá xong lỗi phạm vi, vì hai cờ Angkormilk đang đứng đầu danh sách |
| (b) Mâu thuẫn số rõ ràng | **Không có ca đạt chuẩn.** Ca lệch lớn nhất mà hệ thống gắn cờ đều oan (VCG 2024 tr.27, VHM 2024 tr.37, VNM 2021 tr.51) | — | Không ép. Xem mục 4 để biết hai lỗi trình bày có thật mà hệ thống chưa bắt được |
| (c) Mâu thuẫn ngầm định tính ↔ số | **Không có.** Hệ thống chưa gắn "mâu thuẫn" cho câu định tính nào | — | Có thể demo **chiều ngược lại**: câu định tính *nhất quán*, VNM 2021 tr.53, sau khi vá luật (mục 5) |
| (d) Xu hướng nhiều kỳ | **PC1 2019–2024** (6 năm liên tục) hoặc FPT | **Thấp** nếu dùng điểm hiện tại | Chỗ "điểm tụt" trong chuỗi hiện tại do cờ oan sinh ra. Phải tính lại sau GĐ 0 rồi mới trình bày, và chỉ trình bày như chức năng theo dõi, không gọi là "phát hiện bất thường" |

---

## 1. Cách kiểm chứng độc lập

Mỗi ca đi qua bốn bước:

1. Đọc câu và minh chứng trong `nnc_results.json`.
2. Mở văn bản BCTN quanh câu (`_scratch/ctx.py`). Khi nghi trộn cột thì mở thẳng PDF gốc, cắt theo cột bằng pdfplumber.
3. Mở bảng HTML của TiniX bằng `_scratch/cells.py`. Script này **cố ý không dùng parser của dự án**: nó tách `<tr>`, in nguyên văn dòng có Mã số cần tìm, nên phép kiểm không phụ thuộc vào code đang được kiểm.
4. Tự tính tăng trưởng hoặc tỷ số từ hai ô năm nay và năm trước, rồi so với câu.

Các script tạm nằm trong `docs/demo/_scratch/` và chỉ đọc dữ liệu: `dump_flags.py`, `ctx.py`, `cells.py`, `which_bctc.py`, `fp_types.py`.

---

## 2. Bắt buộc: VNM 2024, trang 31 và trang 59

**Số liệu BCTC hợp nhất 2024** (`VNM_Baocaotaichinh_2024_Kiemtoan_Hopnhat`, TiniX tr.10):

| Mã số | Khoản mục | 2024 | 2023 | Tăng |
|---|---|---|---|---|
| 01 | Doanh thu bán hàng và cung cấp dịch vụ | 61.823.889.921.880 | 60.478.912.566.740 | **+2,22%** |
| 10 | Doanh thu thuần | 61.782.609.528.445 | 60.368.915.511.505 | **+2,34%** |
| 50 | Tổng lợi nhuận kế toán trước thuế | 11.599.653.741.335 | 10.967.899.391.486 | **+5,76%** |
| 60 | Lợi nhuận sau thuế TNDN | 9.452.892.989.948 | 9.019.354.165.051 | **+4,81%** |

Không chỉ tiêu hợp nhất nào tăng 7,6% hay 48,4%.

**Trang 59 (in số 116–117), hệ thống cho điểm 0,41.** Trang thuộc mục *"Các đơn vị thành viên"*. Khối thứ hai có nhãn bên lề "Angkormilk", dòng *"Trụ sở: Campuchia · Vinamilk sở hữu: 100% · Lĩnh vực hoạt động chính: Sản xuất sữa"*, rồi đến đoạn: *"Angkormilk duy trì hoạt động kinh doanh ổn định … Doanh thu và lợi nhuận 2024 tăng lần lượt 7,6% và 48,4% so với 2023."*
Bộ trích chỉ lấy câu thứ hai. Câu này không có tên công ty nên lọt qua `_SCOPE_LIMITED` và `_SUBSIDIARY_REF`.
→ **Cáo buộc oan vì câu nói về công ty con (Angkormilk).** BCTC hợp nhất không tách riêng số của Angkormilk: thuyết minh bộ phận ở TiniX tr.63 chỉ chia "Trong nước" và "Nước ngoài". Nhãn đúng là "không kiểm chứng được".

**Trang 31 (in số 60–61), hệ thống cho điểm 0,00.** Câu trong dữ liệu: *"Vinamilk đã đạt nhiều với doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%"*. Cắt riêng cột ngoài cùng bên phải của trang PDF 31 (x = 893–1191) thì đọc được nguyên văn: *"Các đơn vị thành viên — Driftwood đạt doanh thu tăng 10% và lợi nhuận trước thuế 1 triệu USD. Angkormilk duy trì hoạt động kinh doanh ổn định với doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%. Liên doanh JVL …"*. Cụm "Vinamilk đã đạt nhiều" thuộc cột bên trái: *"Vinamilk đã đạt nhiều giải thưởng quốc tế…"*.
→ **Cáo buộc oan, vì hai lỗi chồng nhau:** (i) trộn cột tạo ra một câu không có trong báo cáo, (ii) nội dung thật vẫn là Angkormilk.

**Phát hiện phụ cần sửa ở tài liệu (agent không sửa tệp có sẵn):**
- `README.md` mục "Ví dụ kết quả thật" đang dùng chính ca trang 59 làm ví dụ *phát hiện mâu thuẫn*. Ví dụ này oan và phải thay.
- Hồ sơ v3 (ví dụ xuyên suốt 8 module) viết rằng câu *"Doanh thu thuần đạt 61.782 tỷ đồng, tăng 2,3%"* nằm ở trang 59. Văn bản BCTN không có câu đó. Câu thật gần nhất là ở **trang 31**: *"Tổng doanh thu hợp nhất của Vinamilk đạt 61.824 tỷ đồng, +2,2% so với cùng kỳ"*. Con số 61.824 ứng với **Mã 01** (doanh thu trước giảm trừ, +2,22%), không phải Mã 10. Khi BGK hỏi về ví dụ này, đội cần dẫn đúng trang và đúng mã.
- Cũng ở trang 31, câu *"Lợi nhuận trước thuế đạt 11.600 tỷ đồng, +5,8% … hoàn thành 100,7% kế hoạch năm"* **khớp Mã 50 (+5,76%)** nhưng bị bộ trích bỏ qua. Lý do: cụm "kế hoạch năm" nằm trong `_FORWARD_LOOKING` nên câu bị coi là câu về tương lai, dù thực chất là kết quả đã đạt. Đây là một ca bỏ sót (âm tính giả).

**Kết luận VNM 2024: điểm 0,77 hiện tại bị kéo xuống bởi hai cờ oan.** Nếu chỉ tính các câu kiểm chứng được thì Vinamilk 2024 nhất quán.

---

## 3. Kịch bản (a): Nhất quán, đối chứng

**a1 · FPT 2022, BCTN tr.52 (khuyến nghị).** *"Doanh thu đạt 44.010 tỷ đồng, tăng 23,4% so với doanh thu 2021. Lợi nhuận trước thuế đạt 7.662 tỷ đồng, tăng 20,9% so năm 2021."* Đoạn này thuộc phần giám sát thực hiện nghị quyết ĐHĐCĐ, nói về kết quả cả tập đoàn.
- Mã 10 (TiniX tr.13): 44.009.527.680.911 / 35.657.262.545.027 → +23,42% ✓, giá trị 44.010 ✓
- Mã 50: 7.662.282.959.880 / 6.337.206.440.958 → +20,91% ✓
- Hệ thống: "nhất quán", điểm 1,00. Hệ thống **chỉ kiểm vế doanh thu**, vế LNTT là do agent tự kiểm, vì bộ trích chỉ lấy số đầu tiên trong câu. Báo cáo FPT 2022 không có cờ "mâu thuẫn" nào.
- Mức chắc chắn: **cao**. Lưu ý: vài câu "nhất quán" khác của FPT 2022 là *nhất quán ăn may*. Ví dụ câu ROE ở tr.32 bị so với vốn chủ sở hữu (Mã 400). Khi demo, chỉ mở đúng câu này, không cuộn cả danh sách.

**a2 · VNM 2024, BCTN tr.31.** *"Tổng doanh thu hợp nhất của Vinamilk đạt 61.824 tỷ đồng, +2,2% so với cùng kỳ"* và *"Lợi nhuận trước thuế đạt 11.600 tỷ đồng, +5,8%"*.
- Mã 01: +2,22% ✓ (61.824 ✓). Mã 50: 11.600 ✓, +5,76% ✓.
- Hệ thống: câu doanh thu được "nhất quán" nhưng so với **Mã 10** (+2,34%) và nhờ ngưỡng 1 điểm phần trăm. Câu LNTT bị bỏ sót (mục 2).
- Mức chắc chắn: **cao về số liệu**, nhưng vết minh chứng hệ thống in ra đang trỏ sai mã. Chỉ nên dùng sau khi ánh xạ "tổng doanh thu" được chốt (⟦Nguyên quyết⟧) và hai cờ Angkormilk đã được gỡ.
- Cùng dạng: VNM 2021 tr.4 và tr.9, *"tổng doanh thu hợp nhất năm 2021 đã đạt 61.012 tỷ đồng"*. Con số này khớp **Mã 01** = 61.012.074.147.764 (+2,16%), không phải Mã 10 = 60.919.

**a3 · PLX 2018, BCTN tr.44.** *"Tổng tài sản hợp nhất … 56.171 tỷ đồng giảm 9,06% so với cuối kỳ năm 2017, tương ứng với 5.598 tỷ đồng"*, kèm *"Tài sản Ngắn hạn giảm 5.948 tỷ đồng tương ứng với giảm 14,68%"* và *"Tài sản Dài hạn tăng 350 tỷ đồng"*.
- Mã 270 (TiniX tr.7): 56.171.183.115.683 / 61.769.061.092.559 → −9,06% ✓, chênh 5.597,9 ✓
- Mã 100: 34.578,1 / 40.526,4 → −14,68% ✓ (−5.948,3). Mã 200: 21.593,1 / 21.242,7 → +1,65% (+350,4) ✓
- Hệ thống: "nhất quán", cả ba chiều (giá trị, tỷ lệ, hướng) đều đạt. Mức chắc chắn: **cao**.
- Lưu ý: bảng tóm tắt cùng trang lại ghi cột "TĂNG/GIẢM" là **+2% cho tài sản ngắn hạn và −15% cho tài sản dài hạn**, tức hai ô bị đảo. Đây là lỗi trình bày *có thật* trong BCTN (xem mục 4). Phần văn xuôi thì đúng.

Dự phòng khác: VNM 2020 tr.46, *"Lợi nhuận ròng đạt 11.235 tỷ đồng … tăng 6,5%"*. Mã 60: 11.235.732.234.125 / 10.554.331.880.891 → +6,46% ✓.

---

## 4. Kịch bản (b): Mâu thuẫn số rõ ràng

**Không có ca nào trong nhóm "mâu thuẫn" đạt chuẩn "lệch lớn, không mơ hồ".** Bốn ca lệch lớn nhất, sau khi kiểm:

| Ca | Hệ thống nói | Kiểm độc lập | Kết luận |
|---|---|---|---|
| **VCG 2024 tr.27**: *"Lợi nhuận sau thuế 861 tỷ đồng, đạt 100% so với kế hoạch và bằng 391% so với năm 2023"* | So Mã 60 hợp nhất 1.108 tỷ, lệch 22,3% | BCTC **riêng** công ty mẹ (TiniX `…2024_Kiemtoan_Congtyme`, tr.11), Mã 60: 860.613.000.906, năm trước 219.904.578.309, tỷ lệ 391,4% ✓ | **Cáo buộc oan vì so số công ty mẹ với số hợp nhất.** Cùng kiểu: VCG 2021 tr.47 (757 tỷ = Mã 60 riêng 757.372.720.127), VCG 2023 tr.26 (220 tỷ = 219.904.578.309) |
| **VHM 2024 tr.37**: *"biên lợi nhuận ròng ở mức 31,08%"* | 34,3% (Mã 60 / Mã 10) | Bảng chỉ tiêu cùng trang ghi rõ "LNST thuộc về Công ty mẹ / Doanh thu thuần". Mã 61 = 31.801.258 / Mã 10 = 102.323.186 (triệu đồng) → 31,08% ✓ | **Oan, vì định nghĩa chỉ tiêu khác** |
| **VNM 2021 tr.51**: *"Doanh thu 2021 ghi nhận biến chuyển tích cực, tăng trưởng 10% so với cùng kỳ"* | +2,2%, lệch 7,85 điểm phần trăm | Câu nằm dưới tiêu đề "2 DRIFTWOOD" (công ty con tại Mỹ) | **Oan, vì nói về công ty con** |
| **FPT 2021 tr.33**: *"Vòng quay hàng tồn kho giảm nhẹ …, xuống 12,5 lần"* | Tăng 14,12 → 14,61 lần (giá vốn / tồn kho cuối kỳ) | Tính theo tồn kho bình quân thì 2020 là 14,15 lần, 2021 là 15,75 lần, cũng **tăng**. Không cách tính phổ biến nào ra 12,5 lần | **Cần người xem.** FPT dùng công thức khác. Cần BCTN FPT 2020 (không có trong dữ liệu) để xem chuỗi nội bộ của FPT có giảm thật không. Không dùng để demo |

**Hai sai lệch có thật mà hệ thống chưa bắt được** (do agent tìm thấy khi rà; không có trong nhóm "mâu thuẫn"):

- **MWG 2022, BCTN tr.7:** *"Công ty ghi nhận doanh thu thuần hơn **133.400 ngàn tỷ đồng**"*. Mã 10 (TiniX tr.9) là 133.404.777.590.524 đồng, tức 133.405 **tỷ**, nên câu sai đơn vị đến 1.000 lần. Các số còn lại trong câu đều đúng: LNST "hơn 4.100 tỷ" ✓ (4.101,7), doanh thu "+8%" (thực tế +8,50%), LNST "−16%" ✓ (−16,32%). Hệ thống trả "không kiểm chứng được" vì `_UNITS` chưa có "ngàn tỷ" và vì lệch quá 50% thì luật xếp vào nhóm "lệch phạm vi".
- **PLX 2018, BCTN tr.44:** bảng cơ cấu tài sản ghi "Tài sản ngắn hạn 40.526 → 34.578: **2%**" và "Tài sản dài hạn 21.243 → 21.593: **−15%**". Đúng ra là −14,7% và +1,6%, tức hai ô bị đảo. Hệ thống không đọc bảng trong BCTN.

Cả hai là **lỗi trình bày** (đánh máy, đảo ô), không phải trình bày sai bản chất. Đưa lên sân khấu như "phát hiện mâu thuẫn" dễ bị coi là bắt lỗi chính tả. ⟦Nguyên quyết⟧: có dùng một trong hai làm ví dụ "lỗi trình bày" hay không. Nếu dùng thì phải nói rõ hệ thống *hiện chưa* tự bắt được.

---

## 5. Kịch bản (c): Mâu thuẫn ngầm định tính ↔ số

**Không có ca nào.** Lý do:

- Cả dữ liệu có **13 khẳng định** mang xu hướng "kiểm soát": 11 "nhất quán", 2 "không kiểm chứng được", 0 "mâu thuẫn".
- Cả 11 câu "nhất quán" đều **nhất quán ăn may**. Chúng nói về *kiểm soát hàng tồn kho* (MWG 2022 ×4, MWG 2023 ×2, VCG 2023, VCG 2024, FPT 2021), *vốn chủ sở hữu* (GAS 2018) và *doanh thu* (PC1 2020, "100,0% → 100,0%"). `_check_cost_control` (`smartaudit/nnc/checker.py`) chia **bất kỳ** chỉ tiêu nào của câu cho doanh thu, nên đem "tồn kho / doanh thu" ra kiểm một câu nói về chi phí, và phép kiểm đó vô nghĩa.
- Trong văn bản BCTN của 13 DN phi ngân hàng, cụm "kiểm soát chi phí", "tối ưu chi phí", "tiết giảm chi phí" hầu như chỉ xuất hiện ở dạng **chủ trương hoặc định hướng** (bị `_POLICY_STATEMENT` và `_FORWARD_LOOKING` lọc, đúng như thiết kế), hoặc đi với "chi phí" chung chung, không trỏ tới khoản mục nào.

Các câu định tính về chi phí agent đã tự kiểm:

| Ca | Kiểm | Kết luận |
|---|---|---|
| **VNM 2021 tr.53**: *"Biên chi phí bán hàng và QLDN hợp nhất năm 2021 đạt 23,8% trên doanh thu thuần. Các chi phí vận hành doanh nghiệp được tối ưu hóa đáng kể so với tỉ lệ 25,8% năm ngoái"* | (Mã 25 + Mã 26) / Mã 10: 2021 = (12.950,7 + 1.567,3) / 60.919,2 = **23,83%**; 2020 = (13.447,5 + 1.958,2) / 59.636,3 = **25,83%** | **Nhất quán**, giảm 2,0 điểm phần trăm. Hệ thống lại gắn "mâu thuẫn" cho một mảnh câu ghép (`#136`, trộn cột với "Biên lợi nhuận ròng 17,4"). Đây là ca đẹp cho **chiều nhất quán** của Điểm mới số 1, sau khi vá |
| **VNM 2020 tr.46**: *"…đạt 25,8% trên doanh thu thuần, duy trì ổn định so với mức 25,5% của năm 2019"* | 25,83% so với 25,55% | **Nhất quán**. Hệ thống trả "không kiểm chứng được" vì câu được ánh xạ sang `selling_expense` chứ không sang tỷ số |
| **MWG 2023 tr.4**: *"…'thắt lưng buộc bụng', kiểm soát mọi chi phí và cơ cấu nhân sự"* | (Mã 25 + 26) tuyệt đối giảm 8,8%. Tỷ lệ trên doanh thu tăng từ 18,15% lên 18,67% (+0,52 điểm phần trăm) vì doanh thu giảm 11,3% | **Không phải mâu thuẫn.** Chi phí tuyệt đối giảm thật. Đo bằng tỷ lệ trên doanh thu thì chỉ nhích 0,5 điểm, dưới ngưỡng 2 điểm của hệ thống. Hệ thống không trích câu này vì "chi phí" đứng một mình không phải chỉ tiêu |
| **VCG 2024 tr.24**: *"Chi phí bán hàng giảm (−37,4%), giúp kiểm soát tốt hơn dòng tiền"* | Mã 25: 58.053.185.376 so với 92.716.194.631 → **−37,39%** | **Nhất quán.** Hệ thống gắn "mâu thuẫn" do đọc số trong ngoặc là số âm (kiểu lỗi I, mục 7) |

**Khuyến nghị:** không dựng ca (c) giả. Nói thẳng với BGK rằng trên 16 DN đã quét, đội chưa gặp câu định tính về chi phí *trái* với số liệu, và trình bày cơ chế bằng **VNM 2021 tr.53 (nhất quán)**. Muốn có ca mâu thuẫn ngầm thật thì phải mở rộng tập DN, ưu tiên nhóm từng bị xử phạt CBTT (danh sách UBCKNN). Việc này **sau Vòng 2**.

---

## 6. Kịch bản (d): Xu hướng nhiều kỳ

Chuỗi điểm NNC trung bình theo năm, gồm cột *gốc* và cột *nếu coi các cờ oan đã định danh ở mục 7 là "không kiểm chứng được"* (`_scratch/fp_types.py`):

| DN | Năm: điểm gốc → sau khi loại cờ oan (số cờ MT) |
|---|---|
| **PC1** | 2019: 0,57→1,00 (6) · 2020: 0,47→1,00 (4) · 2021: 1,00→1,00 (0) · 2022: 0,67→1,00 (1) · 2023: 0,75→1,00 (2) · 2024: 0,86→1,00 (1). Năm 2018 không có câu chấm điểm được |
| **FPT** | 2018: 0,50→1,00 · 2019: 0,78→1,00 · 2021: 0,83→0,92 · 2022: 1,00 · 2023: 1,00 · 2024: 0,80→1,00. Không có 2020 |
| **HAG** | 2018: 0,18→0,75 · 2019: 0,06→— · 2020: 0,45→1,00 · 2023: 0,33→1,00 · 2024: 0,50→1,00 |
| **VCG** | 2018: 0,67→1,00 · 2021: 0,00→— · 2022: 0,33→1,00 · 2023: 0,20→0,50 · 2024: 0,49→1,00 |
| **VNM** | 2018: 1,00 · 2020: 1,00 · 2021: 0,75→1,00 · 2024: 0,77→1,00. Thiếu 2019 (không có PDF), 2022 (lỗi hình học PDF), 2023 (văn bản bóc ra chỉ 2,2 KB, nhiều khả năng là bản scan) |

**Kết luận:** mọi "đợt tụt điểm" trong chuỗi hiện tại đều do cờ oan. Chuỗi HAG (0,18 → 0,06 → 0,45) trông như bất thường, nhưng nguyên nhân là các đoạn biên lợi nhuận gộp **theo từng mảng** (trái cây, cao su, bò…) bị đem so với biên hợp nhất. **Tuyệt đối không trình bày chuỗi HAG như dấu hiệu bất thường**, vì làm vậy là cáo buộc oan ở cấp doanh nghiệp.

**Khuyến nghị:** dùng **PC1 2019–2024** (6 năm liên tục, nhiều khẳng định nhất) làm minh hoạ *chức năng theo dõi nhiều kỳ*, với điểm tính lại sau GĐ 0: ⟦CHỜ: chuỗi điểm PC1 sau vá nền⟧. Lời thoại nên là "chuỗi ổn định, không có tín hiệu", không phải "phát hiện bất thường". Ứng viên thay thế là FPT (6 năm, thiếu 2020). Lưu ý PC1 từ 2021 không có dòng Mã 10 (trình bày "20 = 01 − 11"), nên mọi câu về doanh thu của PC1 2021–2024 đang rơi vào "không kiểm chứng được" (mục 7).

---

## 7. Tổng hợp kiểu dương tính giả (để đội sửa luật)

Phân loại theo **nguyên nhân chính** của từng cờ trên **toàn bộ 141 cờ "mâu thuẫn"** của bản baseline. Một cờ có thể dính nhiều lỗi; bảng chỉ đếm lỗi chính. Danh sách từng ca: `docs/demo/_scratch/phan_loai_mau_thuan.csv`.

| Kiểu | Số ca / 141 | Ví dụ thật | Gợi ý sửa (tệp · hàm) |
|---|---|---|---|
| **A. Phạm vi hẹp hơn số hợp nhất**: công ty con, mảng, thương hiệu, thị trường, khoản mục con | **57 (40%)** | VNM 2024 tr.59 (Angkormilk); VNM 2021 tr.51 (Driftwood); HAG 2018–2024 biên LN gộp từng mảng (24 ca); MWG 2023 tr.30 (Bách Hóa Xanh); HPG 2023 tr.32 (thành phẩm + hàng hóa giảm 25%, trong khi thuyết minh cho −26,2% theo giá trị thuần, nhưng hệ thống so với **tổng** tồn kho) | `nlp/claims.py`: thêm **ngữ cảnh mục/trang** vào `extract_claims`. Trang có "Các đơn vị thành viên", "Trụ sở:", "… sở hữu: x%", "Lĩnh vực hoạt động chính" thì mọi câu trên trang bị coi là phạm vi hẹp. Mở rộng `_SCOPE_LIMITED`/`_SUBSIDIARY_REF` cho tên riêng viết hoa (Angkormilk, Driftwood, WCM, Phúc Long, VinFast…), "đơn vị thành viên", "mảng", "chuỗi". Với HAG, câu "Số lợi nhuận gộp đạt … và biên lợi nhuận gộp đạt …" lặp theo mảng thì nên coi là phạm vi hẹp |
| **C. Rác bố cục**: trộn cột, mảnh bảng, trục biểu đồ, infographic | **24 (17%)** | VNM 2024 tr.31; VNM 2021 tr.53 (#136); HPG 2023 tr.32 ("2.70 2.71 2.70 2.60 … 2018 2019"); MWG 2022 tr.41 ("8 32 Tăng % Tăng %") | `ingest/vietstock.py` · `find_columns`, `_page_text`: trang PDF khổ ngang ~1190×842 là **trang đôi** nên cần cắt đôi trước rồi mới dò cột; dò khe cột theo **từng dải ngang**, bỏ dòng tiêu đề chạy ngang qua khe. `nlp/claims.py`: mở rộng `_MERGED_NUMBERS` cho chuỗi ≥ 3 số trần liên tiếp và dãy năm liền nhau. Đây cũng là GĐ 0.2 |
| **E. Không phải khẳng định kết quả**: chính sách kế toán, rủi ro giả định, mục tiêu, vĩ mô, mô tả | **18 (13%)** | GAS 2018 tr.42 ("Dự phòng giảm giá hàng tồn kho … được trích lập"); HAG 2019 tr.50 ("…sẽ làm tăng chi phí lãi vay"); GAS 2022 tr.57 (mục tiêu 7–9%/năm); MSN 2024 tr.50 (số liệu thị trường) | `nlp/claims.py`: thêm bộ lọc câu chính sách kế toán ("được hạch toán", "được xác định theo", "được trích lập", "theo hướng dẫn của Thông tư"); thêm vào `_FORWARD_LOOKING` các cụm "nếu … sẽ", "cần phải", "nhằm", "tập trung vào" |
| **D. Câu về tỷ số / hệ số / cơ cấu / tỷ trọng** bị so với khoản mục tiền | **17 (12%)** | HPG 2022 tr.21 ("Hệ số nợ phải trả trên VCSH giảm" bị so với VCSH tăng 5,9%); VIC 2020–2022 ("đóng góp trên 10% tổng doanh thu"); VCG 2024 tr.25 (ROA) | `nnc/checker.py` · `_check_direction`: **thêm chốt `claim.is_ratio and fact.unit is Unit.MONEY → None`**. Hai hàm `_check_ratio_level` và `_check_ratio_change` đã có chốt này, riêng hàm kiểm hướng thì chưa. Bổ sung ROE/ROA/nợ trên VCSH vào `DERIVED` (GĐ 0.3) |
| **F. Sai kỳ** | 7 (5%) | VNM 2021 tr.4 ("doanh thu hợp nhất **quý 4**/2021 tăng xấp xỉ 10%"); MWG 2022 tr.12 ("so với năm 2013"); PC1 2022 tr.31 (nói về 2021) | `nlp/claims.py`: nhận diện "quý", "6 tháng", "giai đoạn"; khi câu nêu năm khác năm báo cáo và không phải năm liền trước thì bỏ hoặc trả "không kiểm chứng được" |
| **G. Câu nhiều số / nhiều vế**: lấy nhầm số hoặc nhầm từ chỉ hướng | 6 (4%) | HPG 2022 tr.21 và 2023 tr.33 ("tăng 6%, **từ** 90.781 tỷ **lên** 96.113 tỷ": lấy số năm trước); FPT 2024 tr.7 ("duy trì lợi thế cạnh tranh" bị hiểu là doanh thu "đi ngang"); PLX 2018 tr.3 ("ổn định kinh tế vĩ mô") | `nlp/claims.py`: bắt mẫu "từ X lên/xuống Y" (Y là năm nay); chỉ lấy từ chỉ hướng **gần chỉ tiêu** (dùng `_trend_before` tại vị trí chỉ tiêu, thay cho `_find_trend` toàn câu); tách "lần lượt a% và b%" thành nhiều khẳng định |
| **B. Số BCTC riêng công ty mẹ** đem so với số hợp nhất | 5 (4%) | VCG 2021 tr.47, 2022 tr.50, 2023 tr.26, 2024 tr.27 (hai ca) | `nlp/claims.py`: câu có "công ty mẹ" thì đánh dấu phạm vi riêng. `scripts/run_nnc.py`: nạp thêm BCTC riêng (`consolidated is False`) và đối chiếu câu phạm vi riêng với bảng riêng; không có thì trả "không kiểm chứng được" |
| **H. Định nghĩa chỉ tiêu khác** | 3 (2%) | GAS 2022 tr.15 ("tổng doanh thu trên 102,4 nghìn tỷ" = Mã 10 + 21 + 31 = 102.403,6 ✓); VHM 2024 tr.37 (Mã 61); PC1 2020 tr.3 ("doanh thu **trên** 6.600 tỷ", thực tế 6.679 ✓) | `nnc/checker.py` · `_check_numeric`: hiểu "trên/hơn/gần/xấp xỉ X" là bất đẳng thức hoặc giá trị gần đúng. Ontology: thêm Mã 61; ánh xạ "tổng doanh thu" → ⟦Nguyên quyết⟧ (VNM dùng Mã 01, GAS dùng 10 + 21 + 31) |
| **I. Số trong ngoặc** (quy ước trình bày chi phí) | 1 (1%) | VCG 2024 tr.24 (chi phí bán hàng (58.053) so với (92.716): giảm 37,4% ✓, hệ thống tính thành +37,4%) | `tables/parser.py`: với các dòng chi phí của KQKD (Mã 11, 22, 23, 25, 26, 32, 51, 52), lấy **giá trị tuyệt đối** trước khi tính tăng trưởng |
| **X. Cần người xem** | 3 (2%) | FPT 2021 tr.33 (vòng quay 12,5 lần); HAG 2018 tr.3 ("duy trì ổn định mức doanh thu", thực tế +11,3%); VCG 2023 tr.6 ("doanh thu 12.965 tỷ", trong khi Mã 10 là 12.704 và Mã 10 + 21 + 31 là 13.077) | Đưa vào sheet gán nhãn |

**Top 3 kiểu dương tính giả:** (A) phạm vi hẹp hơn hợp nhất, 40%; (C) rác bố cục và trộn cột, 17%; (E) câu không phải khẳng định kết quả, 13%. Ngay sau đó là (D) tỷ số, 12%. Nếu chỉ vá D bằng một dòng trong `_check_direction` thì đã có thể gỡ khoảng 12% số cờ.

**Lỗi dữ liệu và lỗi bỏ sót phát hiện thêm** (không làm tăng số cờ "mâu thuẫn", nhưng làm sai "nhất quán" và "không kiểm chứng được"):

1. **VCG 2018 bị đối chiếu với BCTC riêng.** Tệp `Bao_cao_VCG_Khong_mau_signed` không có chữ "hợp nhất" hay "riêng" trong tên nên `consolidated=None`. Tệp xếp trước theo tên nên `run_nnc.py` chọn nó, dù trang bìa ghi "BÁO CÁO TÀI CHÍNH RIÊNG" (doanh thu 2.554 tỷ, trong khi số hợp nhất là 9.731 tỷ). Kiểm cả 66 cặp bằng `_scratch/which_bctc.py`: **1/66** cặp dính lỗi này. Sửa ở `ingest/tinix.py` · `iter_reports`: khi tên tệp không phân loại được thì đọc trang bìa để phân loại.
2. **Đơn vị bảng chưa được chuẩn hoá.** MSN, VHM, VIC lập BCTC theo **triệu VND**, HAG theo **ngàn VND**, nhưng parser coi là đồng, nên doanh thu VHM hiện ra "104 triệu". Tăng trưởng không đổi, nhưng mọi phép so giá trị tuyệt đối của 4 mã này rơi vào "lệch phạm vi" (40/111 ca lệch phạm vi thuộc 4 mã này). Ví dụ bị bỏ sót: VHM 2023 tr.32, *"tổng doanh thu thuần hợp nhất đạt 103.557 tỷ đồng, tăng 66%"*, đúng hoàn toàn với Mã 10 = 103.556.722 triệu. Sửa ở `tables/parser.py`: đọc dòng "Đơn vị tính" hoặc "ĐVT" rồi nhân hệ số.
3. **PC1 2021–2024 không có dòng Mã 10.** Doanh nghiệp không có khoản giảm trừ nên trình bày "20 = 01 − 11". Hệ thống không tìm thấy `revenue_net`. Sửa ở `nnc/checker.py` · `build_facts`: khi thiếu Mã 10 và không có Mã 02 thì lấy Mã 01. Agent đã kiểm thử bằng tay: PC1 2022 tr.32, *"biên lợi nhuận gộp toàn Tập đoàn tăng mạnh từ 11,8% lên 19,2%"*: 11,76% → 19,08%, nhất quán. PC1 2024 tr.35, *"20,7%"*: 20,74% ✓.
4. **"ngàn tỷ" chưa có trong `_UNITS`.** MWG 2023 tr.4, *"doanh thu thuần đạt hơn 118 ngàn tỷ đồng, duy trì được 89% … LNST 168 tỷ đồng, giảm 96%"*: 88,66% ✓, −95,9% ✓, nhưng hệ thống trả "không kiểm chứng được".
5. **`_FORWARD_LOOKING` khớp "kế hoạch năm"** nên loại cả câu kết quả kiểu "hoàn thành 100,7% kế hoạch năm" (VNM 2024 tr.31).
6. **"Nhất quán ăn may".** Ngoài 11 câu "kiểm soát" ở mục 5, còn có câu tỷ số được chấm nhất quán vì trùng hướng với khoản mục tiền, ví dụ VNM 2024 tr.49 "Vòng quay tổng tài sản … thay đổi nhẹ" được so với tổng tài sản tăng 4,5%. Vì vậy mẫu gán nhãn **phải có cả câu "nhất quán"**, không chỉ câu "mâu thuẫn", thì số đo mới không bị lạc quan.
7. **Hai cặp chưa rõ lý do vắng mặt trong kết quả:** TCB 2022 và VCG 2019 có văn bản BCTN và có BCTC nhưng không có trong `nnc_results.json`. ⟦CHỜ: Hùng xác nhận lý do⟧.

---

## 8. Việc cần người làm

- **Nguyên**: kiểm tay a1 (FPT 2022 tr.52) và một ca dự phòng đến từng ô trên **PDF gốc** của BCTC, không chỉ trên văn bản OCR. Chốt các điểm ⟦Nguyên quyết⟧ ở mục 3 và 4.
- **Hùng**: thứ tự vá đề xuất theo số cờ gỡ được: D (một dòng) → A (ngữ cảnh trang) → C (trang đôi, khe cột) → E → B/F/G/H/I. Thêm 3 lỗi dữ liệu ở mục 7 (VCG 2018, đơn vị, Mã 10 của PC1). Mỗi sửa phải có test hồi quy dùng đúng câu thật nêu ở trên.
- **Cả đội**: sửa ví dụ trong `README.md`, và chuẩn bị câu trả lời cho ví dụ "trang 59" trong hồ sơ v3 (mục 2).
