# Quy trình thử nghiệm với kiểm toán viên — 17–18/11/2026

> **Bản nháp v0 · 12/11/2026 · Người chủ trì: Tài.** Agent AI viết bản nháp này. **Liên hệ, dẫn buổi và ghi kết quả do Tài làm.**
> Liên quan: `thu-moi.md` (thư mời), `phieu-ghi-ket-qua.csv` (phiếu ghi), báo cáo mục 07 phần 5.2, slide 11.

## 0. Tóm tắt

| | |
|---|---|
| **Mục đích** | Đo sơ bộ thời gian đối chiếu và độ đúng khi làm tay so với khi dùng công cụ; thu nhận xét có cấu trúc; kiểm chứng giả định "40–80 giờ mỗi doanh nghiệp" trong hồ sơ |
| **Người tham gia** | 2–3 kiểm toán viên (KTV), trợ lý kiểm toán hoặc giảng viên kiểm toán |
| **Thiết kế** | Mỗi người làm 2 lượt: **A** làm tay và **B** dùng công cụ, trên **2 doanh nghiệp khác nhau**. Thứ tự và cách ghép doanh nghiệp được đảo giữa các người |
| **Thời lượng** | Không quá 45 phút mỗi người |
| **Đầu ra** | `phieu-ghi-ket-qua.csv`; phiếu trả lời giấy (chụp ảnh); ghi chú phỏng vấn; biên bản xác nhận (nếu người tham gia tự nguyện ký) |
| **Cách báo cáo** | Số liệu thô của từng người; ghi rõ "thử nghiệm sơ bộ, n = …, không suy rộng" |

## 1. Thử nghiệm trả lời câu hỏi gì, và không trả lời câu hỏi gì

**Trả lời được, ở mức sơ bộ:**

1. Với cùng một loại khẳng định, đối chiếu mỗi câu mất bao lâu khi làm tay và khi dùng công cụ?
2. Người tham gia kết luận đúng bao nhiêu câu? Công cụ có khiến họ chấp nhận cả cờ sai không?
3. Người làm nghề có thấy công cụ hữu ích không, có dùng không, dùng ở bước nào và cần điều kiện gì? Trên thực tế, họ mất bao lâu cho việc đọc BCTN và đối chiếu với BCTC?

**Không trả lời được, và không được viết như thể trả lời được:**

- Mức tiết kiệm thời gian của toàn ngành.
- Precision của công cụ. Con số này đã đo trên tập test bằng `evaluate.py`.
- Thời gian **tự tìm** khẳng định trong một BCTN dày hơn 100 trang. Buổi thử phát sẵn danh sách câu, nên chỉ đo bước đối chiếu.

## 2. Người tham gia

- **Tiêu chí:** đã từng kiểm toán BCTC hoặc dạy kiểm toán. Ưu tiên người đã làm với doanh nghiệp niêm yết.
- **Loại trừ:**
  - người thuộc Ban Tổ chức, Ban Giám khảo hoặc Tổ chuyên môn của cuộc thi (Thể lệ, Điều 4 và 9);
  - thành viên đội;
  - người đã xem hoặc dùng thử công cụ trước buổi.
- **Mã hoá:** KTV01, KTV02, KTV03 theo thứ tự buổi. **Bảng ánh xạ mã ↔ họ tên do Tài giữ riêng**, không đưa vào repo, zip hay bất kỳ tệp nộp nào.
- **Vai trò người tham gia:** chỉ dùng thử và nhận xét. Họ **không** gán nhãn, không sửa sản phẩm, không viết tài liệu cho đội. Điều 14 Thể lệ cấm "nhờ người ngoài làm hộ bất kỳ phần nào của sản phẩm".

## 3. Chuẩn bị vật liệu (xong trước tối 16/11)

### 3.1. Hai bộ khẳng định: Bộ X và Bộ Y

**Nguồn và đáp án**

- **Ưu tiên lấy từ tập test đã phân xử.** Đáp án là nhãn sau phân xử.
- Chọn câu **chỉ dựa vào nhãn**, không mở phán quyết của công cụ trên các câu này trước khi mã được đóng băng.
- Phương án thay thế, khi tập test chưa sẵn:
  - lấy từ tập dev, và ghi rõ trong báo cáo rằng công cụ đã được chỉnh trên dev nên kết quả lượt B có thể lạc quan;
  - hoặc lấy một cặp (doanh nghiệp, năm) không thuộc tập nào, đáp án do Nguyên kiểm tay và Phong duyệt.

**Cơ cấu mỗi bộ**

- Một cặp (doanh nghiệp, năm), gồm **N = 6 khẳng định**.
- Theo đáp án: **2 nhất quán, 2 mâu thuẫn, 2 chưa kiểm chứng được** (tức không đủ cơ sở kết luận).
- Có ít nhất 1 câu định tính, ví dụ loại "kiểm soát chi phí".
- Hai bộ phải tương đương về cơ cấu đáp án và loại chỉ tiêu (doanh thu, lợi nhuận, chi phí).
- Nếu không đủ 2 câu "mâu thuẫn" trong một cặp (doanh nghiệp, năm), hạ xuống 1 câu cho **cả hai bộ**, giữ hai bộ giống nhau.
- Ghi lại **M** = số câu "mâu thuẫn" theo đáp án của mỗi bộ. Cần số này để tính số câu bỏ sót.

**Điều kiện chọn doanh nghiệp**

- Doanh nghiệp phi tài chính.
- BCTN là PDF có lớp chữ; BCTC hợp nhất có Mã số.
- Độ dày báo cáo tương đương nhau giữa hai bộ.
- Tránh tập đoàn có cấu trúc quá phức tạp.

**Người làm:** Tài chọn câu, Phong duyệt đáp án (Phong là người phân xử nhãn). Hai bộ cùng đáp án lưu trong một tệp riêng của Tài, **không đưa cho người tham gia**.

### 3.2. Tài liệu cho người tham gia

- BCTN và BCTC gốc (bản PDF công khai) của hai doanh nghiệp, mở sẵn trên máy. Nếu thi online thì để ở một thư mục chia sẻ, **chỉ gửi link vào đầu lượt**.
- Phiếu trả lời in sẵn (Phụ lục A), mỗi lượt một tờ, đã ghi sẵn 6 câu và số trang trong BCTN.
- Được dùng máy tính bỏ túi hoặc Excel.

### 3.3. Công cụ

- Link prototype **bản đã đóng băng**. Mở sẵn trang chi tiết của cặp (doanh nghiệp, năm) dùng cho lượt B.
- Ghi phiên bản (mã commit) vào sổ buổi thử.
- Nếu buổi diễn ra trước giờ đóng băng: ghi rõ phiên bản, và **không được sửa luật dựa trên những gì thấy trong buổi**, để giữ tập test sạch.
- Một ca **không thuộc Bộ X hay Bộ Y** để giới thiệu công cụ trong 2 phút.

### 3.4. Dụng cụ

Đồng hồ bấm giờ (điện thoại), phiếu đồng ý (Phụ lục B), `phieu-ghi-ket-qua.csv` mở sẵn, biên bản xác nhận (Phụ lục C, in sẵn nhưng chỉ đưa ra khi người tham gia tự nguyện).

### 3.5. Chạy thử nội bộ (tối 16/11)

Nhờ một người **chưa biết đáp án hai bộ này** làm thử toàn bộ quy trình và bấm giờ. Có thể là Hùng: Hùng không gán nhãn, và chưa thấy tập test nếu các câu lấy từ đó. Cũng có thể là một bạn sinh viên kế toán ngoài đội, để phát hiện câu mơ hồ hoặc phiếu khó dùng. Kết quả lượt chạy thử **không tính** vào số liệu.

## 4. Thiết kế đối trọng

Làm cùng một doanh nghiệp hai lần thì lượt sau nhanh hơn vì đã nhớ. Vì vậy hai lượt luôn dùng hai doanh nghiệp khác nhau. Nhưng hai doanh nghiệp lại có độ khó khác nhau, và dùng công cụ trước có thể giúp người tham gia biết chỗ cần tìm khi làm tay. Đảo thứ tự giữa các người giúp hai thiên lệch này không dồn về một phía.

| Thứ tự | Lượt 1 | Lượt 2 | Dùng cho |
|---|---|---|---|
| T1 | A (làm tay) · Bộ X | B (công cụ) · Bộ Y | KTV01 |
| T2 | B (công cụ) · Bộ X | A (làm tay) · Bộ Y | KTV02 |
| T3 | A (làm tay) · Bộ Y | B (công cụ) · Bộ X | KTV03 |
| T4 | B (công cụ) · Bộ Y | A (làm tay) · Bộ X | dự phòng |

Với 2 người (T1 và T2), mỗi bộ được làm tay đúng một lần và dùng công cụ đúng một lần, và cả hai thứ tự đều xuất hiện.

## 5. Kịch bản buổi (không quá 45 phút)

| Phút | Việc | Ghi chú |
|---|---|---|
| 0–5 | Chào, giới thiệu ngắn, **xin đồng ý** (Phụ lục B), hỏi vai trò và số năm kinh nghiệm | Chưa cho xem công cụ |
| 5–17 | **Lượt 1** (tối đa 12 phút) | Đọc hướng dẫn chuẩn A hoặc B ở mục 5.1 |
| 17–20 | Nghỉ 1 phút. Nếu lượt 2 là B thì giới thiệu công cụ 2 phút trên ca mẫu | Ca giới thiệu không thuộc hai bộ |
| 20–32 | **Lượt 2** (tối đa 12 phút) | |
| 32–42 | **Phỏng vấn** (mục 7) | Ghi nguyên văn ý chính |
| 42–45 | Cảm ơn; nếu người tham gia tự nói sẵn lòng thì hỏi về biên bản xác nhận | Không nài |

### 5.1. Hướng dẫn chuẩn

Đọc đúng lời, để mọi người tham gia nhận cùng một hướng dẫn.

**Hướng dẫn A (làm tay):**
> "Đây là 6 câu trích từ báo cáo thường niên của [DN] năm [năm], có ghi số trang. Với mỗi câu, [anh/chị] đối chiếu với báo cáo tài chính đã kiểm toán trong tệp bên cạnh rồi kết luận: **nhất quán**, **mâu thuẫn**, hoặc **không đủ cơ sở kết luận**. Ghi luôn trang hoặc dòng làm căn cứ. [Anh/chị] được dùng máy tính. Thời gian tối đa là 12 phút. Xong lúc nào [anh/chị] báo em lúc đó ạ."

**Giới thiệu công cụ (2 phút, chỉ trước lượt B):** mở ca mẫu; chỉ chỗ xem phán quyết, câu gốc, Mã số và trang bảng, phép tính; chỉ cách mở BCTC gốc để kiểm lại. **Không nói gì về độ chính xác của công cụ.**

**Hướng dẫn B (dùng công cụ):**
> "Đây là 6 câu của [DN] năm [năm]. Công cụ đã đưa ra phán quyết và căn cứ cho từng câu. [Anh/chị] dùng công cụ, và mở BCTC gốc nếu muốn kiểm lại, để đưa ra **kết luận của chính mình** cho từng câu. [Anh/chị] hoàn toàn có thể không đồng ý với công cụ. Thời gian tối đa 12 phút ạ."

**Trong lúc làm,** người dẫn không gợi ý và không trả lời câu hỏi về nội dung: *"Trong buổi này em xin phép không gợi ý ạ, [anh/chị] cứ kết luận theo đánh giá của mình."* Chỉ được trả lời câu hỏi về thao tác, như mở tệp hay chuyển trang.

**Bấm giờ:** bắt đầu khi đưa tài liệu (lượt A) hoặc khi mở trang (lượt B). Dừng khi người tham gia nói "xong", hoặc khi hết 12 phút. Nếu hết giờ, ghi lại số câu đã xong.

### 5.2. Nếu thi online

- Người tham gia mở PDF và link prototype trên máy của họ. Link tài liệu chỉ gửi vào đầu mỗi lượt.
- Kết luận từng câu: người tham gia nói to, hoặc gõ vào khung chat. Tài điền vào phiếu.
- Không ghi âm, không ghi hình, trừ khi người tham gia đồng ý riêng.

## 6. Ghi phiếu: định nghĩa từng cột trong `phieu-ghi-ket-qua.csv`

Mỗi người tham gia có **hai dòng**, một cho lượt A và một cho lượt B.

| Cột | Ghi gì |
|---|---|
| `ma_nguoi_tham_gia` | KTV01, KTV02, KTV03 |
| `vai_tro` | `KTV` (kiểm toán viên) · `TLKT` (trợ lý kiểm toán) · `GVKT` (giảng viên kiểm toán) · `KHAC` |
| `so_nam_kinh_nghiem` | Số nguyên: số năm làm kiểm toán hoặc dạy kiểm toán |
| `nhiem_vu` | `A` (làm tay) hoặc `B` (dùng công cụ) |
| `doanh_nghiep` | Mã chứng khoán và năm, ví dụ `ABC 2023` |
| `thoi_gian_phut` | Số phút, lấy 1 chữ số thập phân. Hết giờ thì ghi `12` và ghi rõ ở `nhan_xet` |
| `so_phat_hien` | Số câu người tham gia kết luận **"mâu thuẫn"** |
| `so_dung` | Trong số đó, số câu mà đáp án cũng là "mâu thuẫn" (**phát hiện đúng**) |
| `nhan_xet` | Viết theo khuôn, đặt trong dấu ngoặc kép: `"luot=1; xong=6/6; trung_dap_an=5/6; bac_co=1 (cau 3); <ý kiến ngắn>"`. `trung_dap_an` là số câu có kết luận trùng đáp án, tính cả ba loại. `bac_co` là số cờ "mâu thuẫn" của công cụ mà người tham gia bác; chỉ ghi ở lượt B |

**Các đại lượng tính từ phiếu:**

- phát hiện sai = `so_phat_hien` − `so_dung`
- bỏ sót = M − `so_dung`
- phút mỗi khẳng định = `thoi_gian_phut` ÷ số câu đã xong

**Bằng chứng gốc:** chụp ảnh từng phiếu trả lời giấy (Phụ lục A), đặt tên `KTV01_luot1.jpg`… Lưu cùng chỗ với bảng ánh xạ tên, **không đưa vào repo**.

## 7. Phỏng vấn sau buổi (10 phút)

Hỏi theo đúng thứ tự, ghi nguyên văn ý chính. Đừng gợi ý câu trả lời, và **đừng nói con số 40–80 giờ trước khi người tham gia trả lời P4**.

1. **P1.** Trên thang 1–5, công cụ hữu ích đến đâu cho việc đối chiếu BCTN với BCTC? Vì sao [anh/chị] cho mức đó?
2. **P2.** Phần nào của căn cứ (câu gốc, Mã số, trang bảng, phép tính) giúp [anh/chị] nhất? Còn thiếu gì để [anh/chị] có thể đưa vào hồ sơ kiểm toán?
3. **P3.** Trong lượt dùng công cụ, có lúc nào [anh/chị] không tin phán quyết của công cụ không? Vì sao?
4. **P4.** Trên thực tế, với một doanh nghiệp niêm yết, [anh/chị] hoặc nhóm mất khoảng bao lâu cho việc đọc BCTN và đối chiếu với BCTC đã kiểm toán? Việc đó do ai làm, ở giai đoạn nào của cuộc kiểm toán?
5. **P5.** Nếu có sẵn công cụ này, [anh/chị] có dùng trong công việc không? Dùng ở bước nào? Cần điều kiện gì, ví dụ độ chính xác tối thiểu, bảo mật hay định dạng xuất?
6. **P6.** Nếu gặp một cờ sai, điều đó ảnh hưởng thế nào đến việc [anh/chị] có dùng tiếp hay không? Tỷ lệ cờ sai bao nhiêu thì [anh/chị] chấp nhận được?
7. **P7.** Nếu chỉ được sửa một điều, [anh/chị] muốn sửa điều gì trước?
8. **P8.** (Hỏi cuối cùng, nhẹ nhàng; người tham gia nói "không" thì cảm ơn và dừng ngay.) [Anh/chị] có sẵn lòng:
   - (a) cho đội trích nguyên văn một câu nhận xét?
   - (b) cho nêu tên và đơn vị?
   - (c) ký biên bản xác nhận đã tham gia thử nghiệm (Phụ lục C)?
   - (d) thử tiếp sau cuộc thi, ví dụ trên BCTN năm 2025 vào đầu năm 2027?
   - (e) giới thiệu người hoặc đơn vị khác?

## 8. Xin đồng ý ghi nhận

Đọc to Phụ lục B ở đầu buổi. Người tham gia đồng ý bằng lời thì Tài đánh dấu vào phiếu, ghi ngày giờ. Có ba mức đồng ý **tách riêng**, mức sau không suy ra từ mức trước:

1. Ghi nhận ẩn danh (bắt buộc để tham gia).
2. Trích nguyên văn nhận xét.
3. Nêu tên và đơn vị.

## 9. Phân tích và báo cáo trung thực

**Cách trình bày:**

- Báo cáo **bảng thô từng người**: mỗi người hai dòng A và B, gồm phút mỗi khẳng định, số phát hiện đúng trên tổng phát hiện, số câu bỏ sót, số cờ bị bác. Không gộp thành một con số chung.
- Nếu cần tóm tắt thì dùng khoảng (thấp nhất – cao nhất). **Không** tính "giảm trung bình X%", không tính độ lệch chuẩn, không làm kiểm định thống kê, không đưa giá trị p.
- Biểu đồ: mỗi người hai chấm (A, B) nối bằng một đoạn thẳng. Không dùng cột trung bình.
- **Báo cáo cả kết quả bất lợi:** người tham gia chấp nhận cờ sai của công cụ; lượt B chậm hơn lượt A; nhận xét tiêu cực.

**Giới hạn phải ghi kèm:**

- n = 2–3, chọn qua quen biết (không ngẫu nhiên).
- Người tham gia biết đây là sản phẩm của sinh viên, nên có thể nhận xét dễ dãi.
- Danh sách câu được phát sẵn, nên chỉ đo bước đối chiếu, chưa đo bước tìm khẳng định.
- Hai doanh nghiệp có độ khó khác nhau.
- Câu được lấy từ tập [test/dev].
- Phiên bản công cụ [commit].

**Mẫu đoạn văn cho báo cáo (mục 07, phần 5.2) và slide 11.** Điền số thật; bỏ những câu không đúng với kết quả:

> "Ngày 17–18/11/2026, đội thử nghiệm sơ bộ với [n] người ([vai trò], [x–y] năm kinh nghiệm). Mỗi người đối chiếu 6 khẳng định của một doanh nghiệp bằng tay và 6 khẳng định của một doanh nghiệp khác bằng công cụ; thứ tự hai lượt được đảo giữa các người. Thời gian mỗi khẳng định khi làm tay là [a–b] phút, khi dùng công cụ là [c–d] phút. Số phát hiện đúng trên tổng phát hiện: làm tay [..], dùng công cụ [..]. [Số] cờ sai của công cụ được người tham gia bác, [số] cờ sai bị chấp nhận. Về thời gian thực tế cho việc đọc BCTN và đối chiếu với BCTC, người tham gia ước tính [..]. Với cỡ mẫu này, kết quả chỉ có giá trị minh hoạ, không suy rộng."

**Những câu KHÔNG được viết:**

- "công cụ giúp giảm X% thời gian kiểm toán"
- "được kiểm toán viên xác nhận hiệu quả"
- "đã có đối tác", khi chưa có văn bản của một **đơn vị**

## 10. Phân vai và lịch

| Ngày | Việc | Ai |
|---|---|---|
| 12/11 | Gửi lời mời cho 3–5 người (`thu-moi.md`) | Tài |
| 14/11 | Chốt lịch: KTV01 vào 17/11 (sau giờ đóng băng nếu được), KTV02 và KTV03 vào 18/11 | Tài |
| 16/11 tối | Chốt Bộ X, Bộ Y và đáp án (Phong duyệt); in phiếu; chạy thử nội bộ | Tài, Phong, một thành viên làm thử |
| 17/11 | Báo phiên bản đóng băng; bảo đảm link chạy trong khung giờ thử | Hùng, Phong |
| 17–18/11 | Dẫn buổi, bấm giờ, ghi phiếu | Tài |
| 18/11 tối | Nhập CSV; tính các đại lượng ở mục 6; viết đoạn kết quả theo mẫu ở mục 9 | Tài |
| 19/11 | Đưa số vào báo cáo mục 07 và slide 11; soát chéo | Tài, Nguyên |

## 11. Rủi ro và phương án

| Rủi ro | Phương án |
|---|---|
| Có người huỷ | Đã mời 3–5 người. Nếu chỉ còn 1 người thì vẫn làm và báo cáo n = 1, nói rõ là ca đơn lẻ |
| Link prototype lỗi giữa buổi | Chuyển sang bản chạy tại máy (cùng dữ liệu) và ghi chú vào phiếu. Bản thân sự cố cũng là một phát hiện, phải ghi lại |
| Công cụ cho kết quả sai rõ ràng trên một câu | Không can thiệp, không giải thích. Ghi lại xem người tham gia có phát hiện ra hay không |
| Người tham gia không đồng ý với đáp án và có lập luận | Vẫn chấm theo đáp án, nhưng ghi nguyên văn lập luận vào `nhan_xet`. Sau buổi, Phong xem lại. Nếu nhãn sai thì ghi vào phần hạn chế của báo cáo; **không sửa nhãn tập test sau khi đã chạy** |
| Làm quá 45 phút | Rút phần phỏng vấn còn P1, P4, P5, P8 |

---

## Phụ lục A — Phiếu trả lời của người tham gia (in, mỗi lượt một tờ)

**Mã người tham gia:** ______ **Lượt:** 1 / 2 **Nhiệm vụ:** A (làm tay) / B (công cụ) **Bộ:** X / Y
**Bắt đầu:** __:__ **Kết thúc:** __:__

| # | Câu trong BCTN (trích) | Trang BCTN | Kết luận (NQ = nhất quán · MT = mâu thuẫn · KĐ = không đủ cơ sở) | Căn cứ (trang, dòng hoặc Mã số trong BCTC) | Ghi chú |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |

*Chỉ dùng cho lượt B, người dẫn ghi:* những câu mà kết luận của người tham gia khác phán quyết của công cụ: ____________

## Phụ lục B — Lời xin đồng ý (đọc to ở đầu buổi)

> "Trước khi bắt đầu, em xin phép nói về việc ghi nhận. Buổi này là để đội em thử xem công cụ có giúp được người làm nghề không. Buổi thử không đánh giá [anh/chị].
>
> Em sẽ ghi thời gian, các kết luận của [anh/chị] và nhận xét, gắn với mã KTV0x, vai trò và số năm kinh nghiệm. **Em không ghi tên [anh/chị]** vào tệp kết quả. Em không ghi âm, không ghi hình. Kết quả dùng trong hồ sơ Vòng 2 của đội tại cuộc thi AI-Quantum Challenge 2026, và được ghi rõ là thử nghiệm sơ bộ. [Anh/chị] có thể dừng bất cứ lúc nào mà không cần giải thích.
>
> Cuối buổi em sẽ hỏi riêng xem [anh/chị] có đồng ý cho trích nguyên văn hay nêu tên không. [Anh/chị] hoàn toàn có thể từ chối. [Anh/chị] có đồng ý tham gia không ạ?"

| Mức đồng ý | Có | Không | Ghi lúc |
|---|---|---|---|
| 1. Tham gia, ghi nhận ẩn danh | ☐ | ☐ | |
| 2. Cho trích nguyên văn nhận xét | ☐ | ☐ | |
| 3. Cho nêu tên và đơn vị | ☐ | ☐ | |

## Phụ lục C — Biên bản xác nhận tham gia thử nghiệm

*Chỉ đưa ra khi người tham gia **tự nguyện** đồng ý ở câu P8. Phần nội dung và nhận xét do **chính người tham gia viết**. Đội không viết sẵn nhận xét thay họ.*

> **BIÊN BẢN XÁC NHẬN THAM GIA THỬ NGHIỆM CÔNG CỤ SMARTAUDIT-QUANTUM**
>
> Tôi, họ và tên: ______________________ Chức danh: ______________________
> Đơn vị: ______________________ Số năm kinh nghiệm kiểm toán hoặc giảng dạy kiểm toán: ______
>
> Xác nhận đã tham gia buổi thử nghiệm công cụ của đội AQ2026-064 (AI-Quantum Challenge 2026) vào ngày ___/11/2026, hình thức: trực tiếp / online.
>
> Nội dung đã thử (người tham gia tự ghi): ____________________________________________
>
> Nhận xét (người tham gia tự ghi): ____________________________________________
>
> Mong muốn tham gia thử nghiệm tiếp sau cuộc thi: ☐ Có ☐ Chưa ☐ Không
>
> Tôi đồng ý để đội nêu biên bản này trong hồ sơ dự thi: ☐ Có ☐ Không
>
> Ngày ___/___/2026 Chữ ký: ______________
