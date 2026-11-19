# Hướng dẫn gán nhãn khẳng định BCTN ↔ BCTC — BẢN NHÁP

*Agent Nghiệp vụ soạn 12/11/2026; Nguyên duyệt và chốt. Người gán: Nguyên, Tài. Người phân xử: Phong.*
*⟦Nguyên quyết⟧ đánh dấu quy ước cần chốt **trước khi** bắt đầu gán. Đã chốt thì không đổi giữa chừng.*

## 1. Nguyên tắc

- **Đặt mình vào vị trí kiểm toán viên** đọc BCTN như "thông tin khác" đi kèm BCTC đã kiểm toán (tinh thần VSA 720 ⟦Nguyên kiểm lại tên và số hiệu chuẩn mực⟧). Câu hỏi cần trả lời: *người đọc có bị hiểu sai về số liệu đã kiểm toán vì câu này không?* Không bắt lỗi câu chữ, không đoán ý đồ.
- **Gán mù và độc lập.** Không mở `results/`, dashboard hay `audit_report.py`. Không trao đổi với người gán kia về từng cặp. Chỗ chưa chắc thì ghi vào `ghi_chu`.
- **Nguồn đối chiếu** là BCTC **năm nay**, gồm cả cột năm trước (số so sánh, có thể đã trình bày lại). Sheet cho sẵn một dòng bảng kèm Mã số. Được mở BCTC gốc để tra thêm, tối đa khoảng 3 phút ⟦Nguyên quyết: có cho tra thuyết minh không⟧. Được mở **PDF BCTN đúng trang** để xem tiêu đề mục và câu trước, câu sau; bắt buộc mở khi câu cụt, lạ, hoặc không rõ chủ ngữ.
- **Thứ tự gán:** `la_khang_dinh` → `chi_tieu_dung` → `nhan`. Cột `nhan` gắn với **sự thật trong BCTC**, không gắn với dòng bảng sheet đưa ra.
- Nhịp độ khoảng 2 phút mỗi cặp. Ca nào quá 5 phút thì gán `KKC`, ghi lý do rồi đi tiếp.

## 2. Các cột phải điền

| Cột | Giá trị | Nghĩa |
|---|---|---|
| `la_khang_dinh` | `C` / `K` | `C`: câu **nguyên văn** khẳng định một **kết quả đã xảy ra** của **toàn doanh nghiệp** (hợp nhất, hoặc công ty mẹ nếu câu nói rõ) trong **năm báo cáo** hoặc so với năm liền trước, về đại lượng có trên BCTC. `K`: mảnh bảng hoặc biểu đồ, câu ghép từ hai cột; kế hoạch, mục tiêu, dự báo, rủi ro giả định, chính sách kế toán; số liệu thị trường hoặc vĩ mô; câu **chỉ nói về bộ phận, công ty con, thương hiệu, chuỗi, thị trường lẻ**; kỳ quý, 6 tháng, nhiều năm; đại lượng phi tài chính (số cửa hàng, sản lượng, thị phần) |
| `chi_tieu_dung` | `C` / `K` / `?` | Dòng bảng sheet đưa ra có **đúng** là thứ câu nói tới không: đúng khoản mục (Mã 01 hay 10, Mã 60 hay 61, tỷ số hay giá trị), đúng phạm vi (hợp nhất hay riêng), đúng kỳ. Ghi `?` khi không chắc, **hoặc** khi `la_khang_dinh = K` (không áp dụng) |
| `nhan` | `NQ` / `MT` / `KKC` | `NQ`: mọi vế kiểm được đều khớp BCTC trong ngưỡng làm tròn. `MT`: ít nhất một con số hoặc một hướng sai rõ so với BCTC **đúng phạm vi, đúng kỳ, đúng định nghĩa**. `KKC`: BCTC không đủ để kết luận. Khi `la_khang_dinh = K` thì luôn ghi `KKC` |
| `ghi_chu` | tự do | Ghi phép tính (ví dụ "Mã 50: 11.599,7 / 10.967,9 = +5,76%"), lý do khi gán `K`, `?` hay `KKC`, và ca cần phân xử |

## 3. Quy tắc

**Làm tròn.** Con số trong câu đại diện cho cả khoảng làm tròn của nó:
- "2,3%" là [2,25%; 2,35%), nên tính ra 2,34% là `NQ`.
- "tăng 6%" là [5,5%; 6,5%).
- "61.824 tỷ" ứng với 61.823.889.921.880 đồng.

Có thể nới thêm 0,1 điểm phần trăm để bù khác biệt mẫu số ⟦Nguyên quyết⟧. Với "gần / xấp xỉ / khoảng X", chấp nhận ±5% tương đối. Với "trên / hơn X", chấp nhận khi X ≤ giá trị thật ≤ 1,1X ⟦Nguyên quyết hai ngưỡng⟧. 10 điểm cơ bản bằng 0,10 điểm phần trăm.

**Câu nhiều số.** Kiểm **từng vế**:
- Có một vế sai thì cả câu là `MT`.
- Mọi vế kiểm được đều khớp thì `NQ`, kể cả khi còn vế "% kế hoạch" không kiểm được.
- Mẫu "tăng 6%, **từ** 90.781 **lên** 96.113 tỷ" (HPG 2022 tr.21): số đứng trước là năm trước. Mã 400 cho +5,87% ✓.
- "Lần lượt a% và b%": ghép đúng thứ tự chỉ tiêu.

**Câu định tính.** Quy câu về một kỳ vọng đo được, như một kiểm toán viên vẫn làm. Chỉ gán `MT` khi số liệu đi **ngược** thông điệp một cách rõ ràng.
- "Chi phí [khoản mục] được kiểm soát / tối ưu": `MT` khi cả chi phí tuyệt đối **và** tỷ lệ chi phí trên doanh thu thuần đều tăng rõ, với tỷ lệ tăng trên 1 điểm ⟦Nguyên quyết ngưỡng⟧. "Chi phí" chung chung, không chỉ ra khoản mục, thì `KKC`.
- "Tăng trưởng mạnh / cải thiện": chỉ xét hướng. Độ lớn ("mạnh", "đáng kể") không có chuẩn nên không dùng để gán `MT`.
- "Ổn định / duy trì": `MT` khi chỉ tiêu giảm rõ.
- Câu chỉ nêu nỗ lực, chủ trương ("tập trung kiểm soát chi phí") là `la_khang_dinh = K`.

**Hợp nhất và riêng lẻ.** Mặc định số trong BCTN là số hợp nhất. Câu hoặc tiêu đề mục ghi "Công ty mẹ" thì đối chiếu với **BCTC riêng**: ghi `chi_tieu_dung = K`, còn `nhan` gán theo BCTC riêng ⟦Nguyên quyết⟧. Câu về công ty con hay bộ phận là `K`, kể cả khi thuyết minh bộ phận có số.

**Kỳ so sánh.** "So với cùng kỳ / năm trước" là năm nay so với cột năm trước của BCTC năm nay. Số dư là cuối kỳ so với đầu kỳ. Quý, 6 tháng, CAGR, "so với năm 2013" thì gán `K`.

**Bẫy trình bày.**
1. Chi phí trong KQKD in trong ngoặc là quy ước trình bày, không phải số âm. VCG 2024 tr.24, "chi phí bán hàng giảm (−37,4%)": Mã 25 (58.053) so với (92.716) là −37,39% ✓.
2. BCTC của MSN, VHM, VIC lập theo **triệu đồng**, của HAG theo **ngàn đồng**.
3. "Tổng doanh thu": VNM dùng Mã 01, GAS dùng Mã 10 + 21 + 31; khớp cách nào cũng được ⟦Nguyên quyết quy ước chung⟧.
4. "Biên lợi nhuận ròng" có thể tính trên LNST thuộc công ty mẹ (Mã 61).
5. Lỗi đánh máy hiển nhiên vẫn là `MT`, ghi "lỗi trình bày" ⟦Nguyên quyết⟧.

## 4. Ví dụ khó (dữ liệu thật; chỉ minh hoạ, không thuộc 300 cặp)

| # | DN · năm · trang BCTN | Câu (rút gọn) | Khuyến nghị | Lý do |
|---|---|---|---|---|
| 1 | VNM · 2024 · tr.59 | "Doanh thu và lợi nhuận 2024 tăng lần lượt 7,6% và 48,4% so với 2023." | `K` · `?` · `KKC` | Thuộc mục "Các đơn vị thành viên", khối **Angkormilk** (Campuchia, sở hữu 100%). Tên công ty chỉ in ở nhãn lề. Số hợp nhất là Mã 10 +2,34%, Mã 50 +5,76% |
| 2 | VNM · 2024 · tr.31 | "Vinamilk đã đạt nhiều với doanh thu và lợi nhuận tăng lần lượt 7,6% và 48,4%" | `K` · `?` · `KKC` | **Câu ghép từ hai cột.** PDF gốc: cột trái "Vinamilk đã đạt nhiều giải thưởng quốc tế…", cột phải "Angkormilk … tăng lần lượt 7,6% và 48,4%" |
| 3 | VCG · 2024 · tr.27 | "Lợi nhuận sau thuế 861 tỷ đồng, đạt 100% kế hoạch và bằng 391% so với năm 2023" | `C` · `K` · `NQ` | Số **công ty mẹ**: BCTC riêng, Mã 60 = 860,6 tỷ; 860,6 / 219,9 = 391,4%. Sheet đưa Mã 60 hợp nhất 1.108 tỷ ⟦Nguyên quyết⟧ |
| 4 | GAS · 2022 · tr.15 | "tổng doanh thu trên 102,4 nghìn tỷ đồng và lợi nhuận trước thuế trên 18,8 nghìn tỷ đồng" | `C` · `K` · `NQ` | Sheet đưa Mã 10 = 100.723,5 nên sai định nghĩa. Mã 10 + 21 + 31 = 102.403,6 ✓; Mã 50 = 18.806,3 ✓ |
| 5 | VNM · 2021 · tr.4 | "doanh thu hợp nhất quý 4/2021 đã tăng trưởng xấp xỉ 10%" | `K` · `?` · `KKC` | Kỳ **quý**, BCTC năm không có số này. Câu cả năm liền trước, "tăng 2,2% … đạt 61.012 tỷ đồng", khớp Mã 01 = 61.012,1 (+2,16%) |
| 6 | HAG · 2018 · tr.3 | "HAGL đã duy trì ổn định mức doanh thu" | `C` · `C` · `NQ` | Mã 10: 5.388.200.400 / 4.841.225.074 ngàn đồng = **+11,3%**. Câu muốn nói "không giảm", không tô hồng ⟦Nguyên quyết: `NQ` hay `MT`⟧ |
| 7 | VNM · 2021 · tr.53 | "Các chi phí vận hành doanh nghiệp được tối ưu hóa đáng kể so với tỉ lệ 25,8% năm ngoái" (câu trước: "biên chi phí bán hàng và QLDN … đạt 23,8%") | `C` · tuỳ dòng sheet · `NQ` | Câu định tính có neo số. (Mã 25 + 26) / Mã 10: 23,83% năm 2021, 25,83% năm 2020 ✓. Sheet đưa dòng khác (ví dụ biên LN ròng) thì `chi_tieu_dung = K` |
| 8 | MWG · 2022 · tr.7 | "doanh thu thuần hơn 133.400 ngàn tỷ đồng và duy trì lợi nhuận sau thuế hơn 4.100 tỷ đồng" | `C` · `C` · `MT` | Mã 10 = 133.404,8 **tỷ**, nên câu sai đơn vị 1.000 lần; LNST 4.101,7 tỷ thì đúng. Ghi "lỗi trình bày" ⟦Nguyên quyết⟧ |

*Từng ví dụ đã được tính lại từ ô bảng TiniX (`docs/demo/ung-vien-demo.md`). Gặp ca tương tự trong sheet vẫn phải tự tính lại, vì sheet có thể đưa một dòng bảng khác.*

## 5. Quy trình

1. Cả hai người đọc tài liệu này, cùng làm 8 ví dụ trên, rồi chốt các điểm ⟦Nguyên quyết⟧.
2. Gán độc lập toàn bộ sheet. Không sửa nhãn sau khi đã thấy nhãn của người kia.
3. Phong phân xử bất đồng ở **từng cột**, dựa trên `ghi_chu`. Cohen's kappa tính trên nhãn **trước** phân xử, riêng cho từng cột.
4. Nhãn sau phân xử là đáp án để đo precision và recall (cam kết Phần V mục 8 hồ sơ).

*Tên cột đã thống nhất là `chi_tieu_dung`, dùng chung cho sheet trong `annotation/`, kế hoạch Vòng 2 và `evaluate.py`.*
