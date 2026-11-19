# Quyết định nghiệp vụ

*Tác tử AI soạn thay phần việc của Financial Domain & Ontology Lead (Nguyên), 19/11/2026; chờ Nguyên duyệt.*
*Chốt các điểm ⟦Nguyên quyết⟧ trong mục 03, 04 của báo cáo và trong `huong-dan-gan-nhan.md`. Mỗi dòng: quyết định · lý do.*

## A. Báo cáo giải pháp (mục 03, 04)

- **A1. Rà soát sơ bộ 141 cờ baseline:** chỉ đưa vào dạng định tính (bốn nhóm cờ oan), bỏ các tỷ lệ %. · Phân loại đó do tác tử làm trên baseline, chưa phải nhãn; số định lượng chỉ lấy từ tập nhãn sau phân xử.
- **A2. Quyền dùng BCTN tải qua Vietstock:** không dựa vào điều khoản của Vietstock; căn cứ là BCTN thuộc tài liệu công bố thông tin bắt buộc (Thông tư 96/2020/TT-BTC), và repo không phân phối lại PDF (`data/`, `*.pdf` nằm trong `.gitignore`), chỉ giữ script tải. · Chưa kiểm được điều khoản Vietstock; cách này không phụ thuộc điều khoản đó, và tệp có thể tải lại từ website doanh nghiệp hoặc Sở giao dịch.
- **A3. Phân nhóm ngành:** 8 nhóm theo hoạt động kinh doanh chính, đội tự phân, không gắn mã ICB. · Mục đích là cho thấy độ đa dạng cách trình bày BCTC (xây lắp, bất động sản, bán lẻ…); tránh khai phân ngành ICB khi chưa đối chiếu phiên bản ICB đang dùng.
- **A4. Mô tả gán nhãn:** ghi đúng là hai tác tử AI gán mù, độc lập; gọi là "nhãn bạc"; nêu rõ chưa được người kiểm toàn bộ. · Trung thực về nguồn nhãn; đây là giới hạn của mọi số đo precision, recall.
- **A5. Lỗi đơn vị và cờ oan:** trình bày là "ràng buộc đã gặp" kèm cách xử lý; số sau vá để ⟦CHỜ⟧. · Nguyên nhân đã xác định bằng ví dụ thật; chưa đo thì không ghi số.
- **A6. Chuẩn mực VSA 720:** chỉ nêu số hiệu và nội dung ("thông tin khác"), không trích tên đầy đủ. · Chưa đối chiếu văn bản gốc.

## B. Quy ước gán nhãn

*Người gán A đã áp dụng các quy ước này. Người gán B gán song song nên có thể chưa áp dụng đồng nhất; người phân xử dùng chúng làm chuẩn khi xử bất đồng. Để giữ gán mù, phần này chỉ dùng ví dụ đã có trong hướng dẫn, không nêu cặp nào trong 300 cặp.*

- **B1. Tra thuyết minh:** được, khoảng 3 phút. · Câu về khoản mục chi tiết (thành phẩm, doanh thu cho thuê, phải thu) thì kiểm toán viên cũng phải xem thuyết minh.
- **B2. Làm tròn:** nới thêm 0,1 điểm % ngoài khoảng làm tròn. · Bù khác biệt mẫu số (Mã 01 hay 10).
- **B3. Hai ngưỡng:** "gần / xấp xỉ / khoảng X" chấp nhận ±5% tương đối; "trên / hơn X" chấp nhận X ≤ giá trị thật ≤ 1,1X. · Đủ rộng cho cách làm tròn xuống của BCTN, vẫn bắt được sai cỡ 10%.
- **B4. "Chi phí [khoản mục] được kiểm soát":** MT khi chi phí tuyệt đối và tỷ lệ chi phí trên DTT cùng tăng, tỷ lệ tăng trên 1 điểm %. · Dưới 1 điểm là dao động thường, không đủ để nói câu gây hiểu sai.
- **B5. Câu "Công ty mẹ":** đối chiếu BCTC riêng; `chi_tieu_dung = K` khi sheet đưa số hợp nhất; `nhan` theo BCTC riêng (ví dụ #3 hướng dẫn, VCG 2024 tr.27). · Tách lỗi chọn phạm vi của hệ thống khỏi đúng sai của câu.
- **B6. "Tổng doanh thu":** khớp Mã 01 hoặc Mã 10 + 21 + 31 đều là NQ. · Doanh nghiệp dùng khác nhau (VNM dùng Mã 01, GAS dùng tổng ba mã).
- **B7. Lỗi đánh máy:** MT khi lỗi nằm ở con số, đơn vị hoặc hướng (ví dụ #8, MWG 2022 "133.400 ngàn tỷ"); số đúng nhưng chỉ sai năm so sánh hay tên gọi là NQ, ghi "lỗi trình bày". · Câu hỏi gán nhãn là người đọc có hiểu sai số liệu đã kiểm toán không.
- **B8. "Duy trì ổn định" khi chỉ tiêu tăng** (ví dụ #6, HAG 2018 tr.3): NQ. · Chỉ MT khi chỉ tiêu giảm rõ; câu không tô hồng ngược chiều số liệu.
- **B9. Câu trộn cột:** K khi việc ghép làm sai hoặc mất liên kết chủ thể–số, hoặc câu cụt mất số (ví dụ #2, VNM 2024 tr.31); C khi vế khẳng định còn nguyên chủ thể, chỉ tiêu, số và chỉ bị chen chữ cột khác. · Người đọc PDF thấy khẳng định thật; lỗi bóc chữ không xoá khẳng định đó.
- **B10. Số nổi bật (infographic):** nhãn, số, đơn vị rõ và nói toàn doanh nghiệp trong năm thì C; mảnh bảng, biểu đồ nhiều năm thì K. · Số nổi bật là thông điệp chính tới cổ đông.
- **B11. Kỳ 6 tháng:** K, trừ khi BCTC kiểm toán chính là kỳ đó (doanh nghiệp mới cổ phần hoá lập BCTC 6 tháng) thì C. · Khi đó BCTC có đúng số để đối chiếu.
- **B12. Câu chỉ có % kế hoạch:** C, `nhan = KKC`. · BCTC không có số kế hoạch.
- **B13. Tỷ số (vòng quay, ROE, ROA, biên ròng):** chấp nhận cách tính trên số bình quân hoặc cuối kỳ, biên ròng trên Mã 60 hoặc LNST công ty mẹ; sheet tính khác câu thì `chi_tieu_dung = K`; không cách thông dụng nào tái tạo được và lệch nhỏ thì KKC, không MT. · Doanh nghiệp không công bố công thức.
- **B14. Sheet trống** (không tra được chỉ tiêu): `chi_tieu_dung = K`; `nhan` theo số tự tra. · Sheet không đưa dòng đúng.
- **B15. Số điều chỉnh, giả định, phi BCTC** ("nếu loại các chi phí này", "doanh thu thuần điều chỉnh", doanh số hợp đồng bất động sản, chi phí tiết kiệm, doanh thu bình quân mỗi người): K. · Không phải đại lượng trên BCTC.
- **B16. Câu nhiều vế:** vế về công ty con, mảng hoặc % kế hoạch thì bỏ qua; một vế toàn doanh nghiệp sai là MT. · Theo quy tắc "kiểm từng vế" của hướng dẫn.
