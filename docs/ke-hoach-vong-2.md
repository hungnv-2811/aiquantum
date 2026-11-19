# Kế hoạch Vòng 2 (Bán kết) — AQ2026-064

> **Cập nhật 19/11/2026 — đã hoàn thành bộ nộp** (thư mục `deliverables/`): báo cáo theo mẫu mới (11 trang nội dung), slide 18 trang, hướng dẫn PDF, mã nguồn zip 19,6 MB (đã kiểm thử máy sạch), prototype https://smartaudit-quantum.vercel.app (Vercel, dự án `smartaudit-quantum`).
> Khác với kế hoạch ban đầu: phần việc của Nguyên và Tài, **kể cả gán nhãn 300 cặp**, do tác tử AI làm (nhãn bạc, đã khai báo trong báo cáo); chưa thử nghiệm với kiểm toán viên. Precision mục tiêu 80% **chưa đạt** — xem báo cáo mục 05.
> Deploy lại sau khi sửa: `cd prototype` → `vercel link --project smartaudit-quantum` → `vercel deploy --prod`.

*Lập ngày 12/11/2026, dựa trên "Thông báo về chuẩn bị nộp sản phẩm Vòng 2", mẫu báo cáo giải pháp của BTC, Thể lệ (Điều 10, 11.2) và hiện trạng repo đo cùng ngày.*

> **Hạn nộp: trước 24h thứ Sáu 20/11/2026** tại https://ai-quantum.hvtc.edu.vn/ — **còn 8 ngày.**
> **Hạn nội bộ: 21h thứ Năm 19/11.** Ngày 20/11 chỉ để dự phòng, không làm việc mới.
> Thi Vòng 2: 28–29/11/2026, trực tiếp hoặc online (BTC sẽ ra thông báo chính thức sau).

---

## 1. Phải nộp gì

| # | Sản phẩm | Tên tệp | Yêu cầu cứng |
|---|---|---|---|
| 1 | Báo cáo giải pháp | `AQ2026-R2-AQ2026-064-Bao_cao_giai_phap.pdf` | 8–12 trang, **đúng mẫu BTC** (sai mẫu là không được chấm). Mỗi mục phải có kết quả và minh chứng kiểm tra được, không viết lại ý tưởng Vòng 1. |
| 2 | Slide trình bày | `AQ2026-R2-AQ2026-064-Slide.pptx` | Tóm tắt giải pháp, phương pháp, chức năng chính, kết quả đạt được |
| 3 | Mã nguồn | `AQ2026-R2-AQ2026-064-Ma_nguon.zip` | Mã nguồn, cấu hình, **dữ liệu mẫu**, đủ để cài và chạy thử; có chú thích. **Một tệp nén, không được thay bằng link repo.** *Đóng gói sau cùng, không làm vội (mục 6.4).* |
| 4 | Hướng dẫn | `AQ2026-R2-AQ2026-064-Huong_dan.pdf` | Môi trường, thư viện, các bước cài/cấu hình/chạy; cách dùng chức năng chính; tài khoản thử, dữ liệu mẫu; cách kiểm tra kết quả; **ghi lại link prototype**. BGK phải tự cài và chạy được. |

Mã đội **AQ2026-064**, nên "Madoi" trong tên tệp thay bằng `AQ2026-064`.
| 5 | Link prototype | khai trong biểu mẫu nộp + ghi trong Hướng dẫn | **Đã triển khai, chạy thử thực tế được** chức năng cốt lõi; đội phải giữ link sống suốt thời gian đánh giá. |

**Thang chấm Vòng 2** (Thể lệ 11.2): Bài toán 20% · Dữ liệu 15% · Giải pháp/thuật toán 20% · **Prototype 20%** · Triển khai thực tế 15% · Trình bày, tài liệu 10%.
Điều 10: *"một mô hình AI đơn giản nhưng chạy ổn định … sẽ có điểm cao hơn một mô hình phức tạp nhưng không thể triển khai"*. Kế hoạch này bám đúng câu đó.

---

## 2. Đang đứng ở đâu (đo ngày 12/11)

| Hạng mục | Trạng thái |
|---|---|
| Pipeline NNC (ingest → bóc bảng TT200 → trích khẳng định → đối chiếu → XAI) | ✅ Chạy thật. **121/121 test xanh** trên môi trường dựng mới hôm nay. `audit_report.py VNM 2024` ra 0,77 / 8 khẳng định. |
| Dữ liệu | ✅ Có sẵn trên máy: 338 BCTC TiniX (75 MB) + 93 BCTN (958 MB PDF, 17 MB văn bản đã bóc) |
| Vá nền (GĐ 0 trong `ke-hoach-hoan-thien.md`) | ❌ **Chưa làm.** Lỗi hình học PDF, lọc rác bảng, ROE/ROA, phạm vi bộ phận vẫn nguyên như 21/09. **Lỗi mới phát hiện 12/11 (GĐ 0.5):** parser không đọc dòng "Đơn vị tính", nên **36/138 BCTC ngoài ngân hàng (26%)** ghi theo nghìn/triệu đồng bị hiểu thành đồng (ví dụ doanh thu MSN 2024 = 83.177.720 triệu bị đọc là 83 triệu đồng). Mọi phép so giá trị tuyệt đối trên các báo cáo này đều sai; phép so tăng trưởng thì không bị ảnh hưởng. |
| Precision thật | ❌ **Chưa đo bằng nhãn mù.** Rà soát sơ bộ 12/11 (agent Nghiệp vụ, `docs/demo/_scratch/phan_loai_mau_thuan.csv`): **138/141 cờ "mâu thuẫn" là cáo buộc oan** gọi tên được nguyên nhân, 3 ca cần người xem, **chưa ca nào xác nhận là mâu thuẫn thật**. Nguyên nhân chính: phạm vi hẹp hơn số hợp nhất 40% · rác bố cục/trộn cột 17% · câu không phải kết quả 13% · câu về tỷ số 12%. Đây là nhãn sơ bộ, không thay được 300 nhãn mù. |
| Ví dụ VNM 2024 trong README | ❌ **Sai.** Câu "tăng 7,6% và 48,4%" nói về **Angkormilk** (công ty con ở Campuchia), không phải Vinamilk hợp nhất. README đang dùng chính ca này làm ví dụ "phát hiện mâu thuẫn" → phải sửa trước khi nộp. Không dùng lại ở báo cáo/slide. |
| Dashboard | ⚠️ Vẫn chạy `data.js` **mô phỏng**, chưa nối dữ liệu thật, **chưa triển khai online** |
| Lớp lượng tử | ✅ *12/11:* QKA PoC chạy xong, có baseline cổ điển, 24 test mới. Lượng tử thua SVM-RBF (0,840 vs 0,911), xem 6.3. |
| PhoBERT-Fin · API | ❌ Chưa có dòng code nào |
| Quản lý mã | ⚠️ `smartaudit/`, `scripts/`, `tests/`, `results/` **chưa commit vào git**. Repo chính báo lỗi `dubious ownership` vì thư mục thuộc SYSTEM. *12/11: đã chép sang worktree `round-2-planning-6ea84b` để làm việc; bản ở `D:\AIquantumhvtc` giữ nguyên làm backup.* |
| Môi trường | ⚠️ `.venv` cũ hỏng vì trỏ tới Python của máy cũ (`C:\Users\HP\...`). *12/11: đã dựng `.venv` mới (Python 3.11) trong worktree, 121/121 test xanh; phiên bản đã ghim vào `requirements-lock.txt`.* |

**Kết luận:** lõi kỹ thuật vững, nhưng gần 2 tháng không tiến triển. Ba việc BGK chấm nặng nhất là **số đo thật**, **prototype online trên dữ liệu thật** và **lớp lượng tử có kết quả thật**, và cả ba đều chưa có. Tám ngày đủ để làm cả ba nếu cắt bỏ mọi thứ còn lại.

---

## 3. Phạm vi Vòng 2

### Làm (theo thứ tự ưu tiên)

| Ưu tiên | Hạng mục | Vì sao |
|---|---|---|
| **P0** | Vá nền GĐ 0 → **gán nhãn 300 cặp** → `evaluate.py` → lặp chất lượng | Tiêu chí 2, 3, 4 đều đòi "kết quả bước đầu, độ chính xác". Đây là cam kết Phần V mục 8 của hồ sơ. |
| **P0** | Dashboard đọc **kết quả thật** (JSON xuất từ pipeline), gỡ toàn bộ số mô phỏng, **triển khai online** | Prototype 20%, và thông báo bắt buộc có link chạy được |
| **P0** | Chức năng **"Kiểm tra một khẳng định"** chạy live: chọn DN + năm, gõ câu → phán quyết + vết minh chứng | Thông báo đòi "chạy thử thực tế, kiểm tra chức năng cốt lõi". Trang tĩnh chỉ xem kết quả có sẵn có thể bị coi là không chạy thật. |
| **P0** (làm sau cùng) | Đóng gói zip + Hướng dẫn, **kiểm thử trên máy sạch** | BGK phải tự cài được. Venv vừa hỏng khi chuyển máy là cảnh báo rõ. **Chưa đóng gói vội**: chỉ làm khi code đã đóng băng (19/11). |
| **P1** | **QKA proof-of-concept** (≤ 8 qubit, simulator) cho khớp khoản mục khi thiếu Mã số, so với rapidfuzz và SVM-RBF | Tên đề tài có chữ *Quantum*; BGK chắc chắn hỏi; có Giải "Ứng dụng Lượng tử xuất sắc". Hồ sơ đã cam kết công bố cả kết quả âm. |
| **P1** | Thử nghiệm sơ bộ với **2–3 kiểm toán viên/giảng viên kiểm toán HVTC** (đo thời gian đối chiếu có/không có công cụ, xin nhận xét) | Tiêu chí 5 (mức 90–100 = "đã có đối tác tiềm năng") và tiêu chí 1. Hồ sơ đã hứa "sẽ đo". |
| P2 | Bộ phân loại khẳng định bằng học máy nhẹ, so với bộ luật | Chỉ làm nếu checkpoint tối 16/11 xanh |

### Không làm ở Vòng 2 — kèm câu trả lời khi bị hỏi

| Hạng mục | Trả lời BGK |
|---|---|
| Fine-tune PhoBERT-Fin | Bộ luật hiện tại là baseline có đo được precision. Mô hình học chỉ đáng đưa vào khi có tập đánh giá để chứng minh nó thắng baseline, và tập đó vừa mới có. Đây là bước kế tiếp trong lộ trình. |
| QSVM phát hiện bất thường | Chỉ có 31 mẫu dương / 686 cặp. Khoảng tin cậy rộng hơn mọi khác biệt đo được nên không kết luận được gì. Vì thế đội làm QKA trước, nơi nhãn sinh tự động được hàng nghìn cặp. |
| Ngân hàng (Thông tư 49) | Ngoài phạm vi, đã tuyên bố từ hồ sơ. Dashboard hiển thị huy hiệu "ngoài phạm vi TT49" và loại khỏi số đo precision. |
| OCR 16 BCTN bản scan | Lộ trình sau cuộc thi |
| Web app phân quyền · Trợ lý hỏi đáp · DSS · Tải PDF tuỳ ý | Tầm nhìn sản phẩm (Phần IX hồ sơ), không cần để chứng minh tính khả thi |

---

## 4. Phân công

Theo vai trò đã khai trong hồ sơ. **Cả đội xác nhận lại tối 12/11.**

| Người | Mảng chính |
|---|---|
| **Hùng** — Lead, AI/NLP | Vá nền, script lấy mẫu gán nhãn, `evaluate.py`, lặp chất lượng, xuất JSON, API FastAPI; viết mục 03 (Tiêu chí 3) |
| **Phong** — Quantum ML & System | QKA PoC; triển khai online; đóng gói zip; Hướng dẫn; **người phân xử nhãn** (không viết luật nên ít thiên kiến); viết mục 06 (Tiêu chí 4) |
| **Nguyên** — Financial Domain & Ontology | Hướng dẫn gán nhãn, **người gán nhãn 1**, kiểm tay từng ca demo đến từng ô bảng gốc, **kiểm thử máy sạch**; viết mục 03 (Tiêu chí 1) và 04 (Tiêu chí 2) |
| **Tài** — Financial Risk & Product | **Người gán nhãn 2**, liên hệ kiểm toán viên và thử nghiệm người dùng, **chủ trì slide**; viết mục 07 (Tiêu chí 5) và 08 (Tiêu chí 6) |

### 4.1. Agent AI làm nháp, người chốt

Từ 12/11, ba agent AI chạy song song làm **bản nháp** cho phần việc của Phong, Nguyên và Tài. Mỗi agent chỉ tạo tệp mới trong thư mục riêng, không sửa code lõi.

| Agent | Làm thay phần nào | Người chịu trách nhiệm duyệt |
|---|---|---|
| Quantum | QKA PoC + baseline cổ điển (`smartaudit/quantum/`, `scripts/run_qka.py`, `results/qka_results.json`) | Phong: phải chạy lại được và giải thích được từng bước khi bị hỏi |
| Nghiệp vụ | Hướng dẫn gán nhãn; rà soát ứng viên 4 ca demo (kể cả ca VNM 7,6%/48,4%); nháp mục 03–04 báo cáo | Nguyên: kiểm tay từng ca demo đến từng ô, sửa nháp thành giọng của đội |
| Sản phẩm | Nháp mục 07–08; dàn ý slide + lời thoại 10 phút; thư mời và quy trình thử nghiệm KTV | Tài: gửi thư, chạy thử nghiệm, chốt slide |

**Phải do người làm, agent không làm thay:**

- **Gán nhãn 300 cặp** (Nguyên, Tài) và **phân xử** (Phong). Đây là "đáp án" để đo precision. Hồ sơ đã cam kết hai thành viên khối Tài chính gán độc lập kèm Cohen's kappa. Nếu AI gán nhãn thì con số precision mất giá trị và mâu thuẫn với chính hồ sơ.
- **Liên hệ và thử nghiệm với kiểm toán viên.**
- **Tạo tài khoản hosting** để deploy (Cloudflare/Netlify, Hugging Face).
- **Thuyết trình và trả lời phản biện.** Ai phụ trách phần nào phải hiểu phần đó, kể cả phần agent làm nháp.

**Tuân thủ Thể lệ Điều 14:** cấm dùng AI tạo sinh tạo *toàn bộ* bài dự thi mà không có cải tiến đáng kể của con người; AI hỗ trợ thì được, nhưng **phải khai báo rõ**. Mục "Khai báo sử dụng công cụ AI" trong README, báo cáo (mục cam kết) và slide phải ghi đúng mức đội đã dùng agent: viết nháp mã, nháp tài liệu, rà soát.

---

## 5. Lịch từng ngày

| Ngày | Hùng | Phong | Nguyên | Tài |
|---|---|---|---|---|
| **Thứ Năm 12/11** (tối nay) | ✅ Chép code vào worktree, dựng `.venv`, ghim `requirements-lock.txt`; ✅ `sample_for_labeling.py` + sheet gán nhãn trong `annotation/`; ⬜ commit vào git | ✅ (agent làm nháp) QKA PoC chạy xong, 13–15/11 dành cho **duyệt, chạy lại, hiểu từng bước** + dựng hạ tầng deploy | Viết hướng dẫn gán nhãn (1 trang, có 5 ví dụ khó) | Gửi câu hỏi cho BTC (mục 8); liên hệ 3–5 kiểm toán viên |
| **Thứ Sáu 13/11** | GĐ 0.1–0.5 (0.5: đọc "Đơn vị tính" và quy đổi) + sửa 4 nguồn cờ oan lớn nhất theo `phan_loai_mau_thuan.csv` (phạm vi, trộn cột, câu không phải kết quả, chốt `is_ratio` trong `_check_direction`); mỗi sửa có test hồi quy; chạy lại NNC, ghi số cờ trước/sau | Baseline rapidfuzz + SVM-RBF; lần chạy kernel lượng tử đầu tiên | **Gán nhãn** (mục tiêu 100) | **Gán nhãn** (mục tiêu 100) |
| **Thứ Bảy 14/11** | `evaluate.py`; `make_injected_set.py` (tập chèn lỗi, mục 6.1b); `export_dashboard.py` (chốt schema JSON); sửa ví dụ VNM sai trong README | **Dựng sớm hạ tầng deploy**: trang tĩnh có URL thật + thử Pyodide chạy `check_claim` trên một câu mẫu (mục 6.2); chốt phương án dự phòng | Gán nhãn (200) | Gán nhãn (200); chốt lịch thử nghiệm 17–18/11 |
| **Chủ Nhật 15/11** | Đo baseline trên tập dev, phân tích lỗi | Phân xử bất đồng → tính **Cohen's kappa**; chia dev/test; kết quả QKA v1 | Gán nhãn xong 300; nháp mục 03–04 báo cáo | Gán nhãn xong 300; nháp mục 07 |
| **Thứ Hai 16/11** | Lặp chất lượng vòng 1; API: danh sách DN, chi tiết báo cáo, `POST /check-claim` | Nối frontend với JSON thật; trang Quantum với số thật | Chọn và **kiểm tay 4 ca demo** | Dàn ý slide; kịch bản thuyết trình 10 phút |
| ⛳ **Checkpoint tối 16/11** | Precision "mâu thuẫn" trên **tập dev** ≥ 80%? Nếu không: **thu hẹp phạm vi**, không hạ chuẩn (mục 6). Có dư sức thì mới mở P2. | | | |
| **Thứ Ba 17/11** | Lặp vòng 2. **Đóng băng pipeline** → chạy **một lần** trên tập test → số cuối cùng | Deploy API + frontend; cài keep-alive; trạng thái API hiện trên giao diện | Rà mục 03–04 với số cuối | **Thử nghiệm KTV #1**; nháp slide |
| **Thứ Tư 18/11** — 🧊 **CODE FREEZE 22h** | Viết mục 05 (Tiêu chí 3); sửa lỗi deploy | Viết Hướng dẫn v1; viết mục 06 | Soát chéo số liệu bản nháp báo cáo | Thử nghiệm KTV #2; slide v1; viết mục 07–08 |
| **Thứ Năm 19/11** | Ghép báo cáo vào mẫu, xuất PDF, đếm trang | **Sáng: đóng gói zip** từ bản đã đóng băng; Hướng dẫn bản cuối; quay **video demo 3–5 phút** | **Kiểm thử máy sạch** theo đúng Hướng dẫn trên laptop khác; soát chéo: mọi con số trong báo cáo, slide, dashboard phải trùng nhau | Slide bản cuối |
| | **21h: NỘP ĐỦ 4 tệp + link.** Tải lại từ website và mở thử từng tệp. | | | |
| **Thứ Sáu 20/11** | Dự phòng. Chỉ sửa nếu nộp thiếu hoặc lỗi. **Hạn chót 24h.** | | | |
| **21–27/11** | Tập thuyết trình ≥ 3 lần có bấm giờ; cập nhật `interview-qa.md` + `cheat-sheet.md` theo số cuối; mỗi người nhận một nhóm câu hỏi phản biện; theo dõi link prototype mỗi ngày; thử chia sẻ màn hình nếu thi online. **Không đổi bản đã deploy** trừ lỗi nghiêm trọng. | | | |
| **28–29/11** | **Thi Vòng 2** | | | |

---

## 6. Chi tiết các mảng then chốt

### 6.1. Đo chất lượng: 300 cặp gán nhãn

- **Lấy mẫu phân tầng**: lấy toàn bộ khẳng định đang bị gắn "mâu thuẫn" (~140) cộng ~160 ca ngẫu nhiên từ các nhóm còn lại, trải theo ngành và năm. Lý do: lấy ngẫu nhiên thuần chỉ được ~60 ca "mâu thuẫn", khoảng tin cậy của precision rộng ±12 điểm. Recall ước lượng có trọng số trên phần ngẫu nhiên.
- **Gán nhãn mù**: người gán nhãn **không thấy phán quyết của hệ thống**, chỉ thấy câu gốc, trang và số liệu bảng. Các cột cần điền: `la_khang_dinh` (C/K) · `chi_tieu_dung` (C/K/?) · `nhan` (NQ/MT/KKC) · `ghi_chu`. Sheet đã sinh sẵn trong `annotation/`.
- Nhãn gắn với **câu và sự thật trong BCTC**, không gắn với phán quyết, nên vẫn dùng được sau khi vá nền.
- **Chia dev 100 / test 200 theo cặp (DN, năm)** để không rò rỉ. Lặp luật chỉ nhìn tập dev. Tập test chỉ chạy một lần sau khi đóng băng. Đây là câu trả lời cho câu hỏi về overfitting trong Tiêu chí 2.
- `evaluate.py` xuất: precision/recall nhóm "mâu thuẫn" kèm khoảng tin cậy · tỷ lệ "chưa kiểm chứng" phân rã theo lý do · độ phủ bóc bảng và tra chỉ tiêu · kappa · bảng nhầm lẫn.
- **Nếu precision < 80%:** thu hẹp phạm vi, ví dụ chỉ phán "mâu thuẫn" khi tra được Mã số trực tiếp, nhánh khớp theo tên chỉ được trả "chưa kiểm chứng". Thà ít mà đúng (Nguyên tắc 2 của hồ sơ). Báo cáo ghi rõ đã thu hẹp và vì sao.

#### 6.1b. Điều chỉnh sau rà soát 12/11: dữ liệu thật gần như không có mâu thuẫn thật

Doanh nghiệp niêm yết lớn hiếm khi trình bày sai số liệu đã kiểm toán ngay trong báo cáo thường niên. Vì vậy **tỷ lệ nền của mâu thuẫn thật rất thấp**, và một hệ thống tốt trên tập này phải **gần như im lặng**. 141 cờ hiện tại gần như toàn bộ là oan. Precision 80% trên dữ liệu thật vì thế khó đo có ý nghĩa: sau khi vá, số cờ còn lại có thể chỉ một chữ số.

Đổi cách chứng minh chất lượng thành **hai số đo bổ sung cho nhau**:

1. **Tỷ lệ cờ oan trên dữ liệu thật** (300 nhãn mù): trước và sau khi vá. Mục tiêu: số cờ oan về gần 0. Precision vẫn báo cáo, kèm cỡ mẫu và khoảng tin cậy.
2. **Recall trên tập chèn lỗi có kiểm soát**:
   - Lấy các câu người gán nhãn xác nhận `NQ`, tạo biến thể sai lệch có chủ đích theo từng loại: đổi số ±2/5/10/20%, đảo hướng tăng↔giảm, nói "kiểm soát tốt" khi tỷ lệ chi phí/doanh thu tăng.
   - Đo tỷ lệ hệ thống bắt được theo từng loại và từng mức lệch.
   - Dữ liệu chèn lỗi **ghi rõ là tổng hợp**, không trộn vào số đo trên dữ liệu thật.
   - Đây là phương pháp kiểm thử chuẩn khi lỗi thật hiếm.

**Demo:**

- Kịch bản (b) mâu thuẫn số và (c) mâu thuẫn ngầm dùng **câu chèn lỗi**, trên màn hình ghi rõ "câu đã sửa có chủ đích để minh hoạ".
- Hai lỗi trình bày **thật** agent tìm được (MWG 2022 tr.7 "133.400 ngàn tỷ"; PLX 2018 tr.44 đảo hai ô %) là ứng viên "phát hiện thật", nếu hệ thống bắt được sau khi vá đơn vị "ngàn tỷ".

**Kể chuyện trung thực:** "Ví dụ chúng tôi đưa ra ở Vòng 1 hoá ra là cáo buộc oan — câu nói về công ty con Angkormilk. Chính phát hiện đó dẫn tới bộ lọc phạm vi và quy trình gán nhãn mù." Giám khảo đánh giá cao đội tự tìm ra lỗi của mình hơn là đội không biết.

### 6.2. Prototype online

> **Thay đổi 12/11:** Hugging Face đã đổi chính sách (đã kiểm tài liệu chính thức): Space chạy Docker/Gradio **bắt buộc gói trả phí** (PRO 9 USD/tháng). Chỉ Space tĩnh là miễn phí, và Space trên phần cứng miễn phí sẽ ngủ khi không ai dùng. Phương án API miễn phí trên Space không còn dùng được.

**Khuyến nghị: không cần server.** Phần lõi đối chiếu (`nlp/claims.py`, `nnc/checker.py`, `ontology/`) chỉ dùng Python thuần + `pyyaml` (+ `rapidfuzz` khi khớp gần), nên chạy được **ngay trong trình duyệt bằng Pyodide**, dùng đúng mã nguồn của pipeline.

```
pipeline (offline) ──export_dashboard.py──► JSON tĩnh: kết quả + bảng facts theo (mã, năm)
                                                │
                                                ▼
             Trang tĩnh (Cloudflare Pages / Netlify) ── Pyodide nạp smartaudit/ (lõi)
             "Kiểm tra khẳng định": người dùng gõ câu → extract_claims → check_claim → vết minh chứng
```

- **Không server thì không có gì để ngủ hay sập.** Tốn ~10 MB tải lần đầu, sau đó chạy tại máy người xem.
- Phương án dự phòng nếu Pyodide vướng: FastAPI trên **Render** (miễn phí, ngủ sau 15 phút, khởi động lại ~1 phút) hoặc **HF PRO 9 USD/tháng** trong 1 tháng. Phong chốt trước 14/11.
- **Tĩnh trước, live sau.** Dù phần live lỗi, toàn bộ dashboard vẫn chạy trên JSON thật. Không bao giờ để BGK mở link ra trang trắng.
- **Không cần tài khoản**: demo công khai, chỉ đọc. Ghi rõ điều này trong Hướng dẫn.
- Các trang: Tổng quan (số đo thật + khoảng tin cậy) · Doanh nghiệp (điểm NNC theo năm) · Chi tiết báo cáo (từng khẳng định + vết minh chứng) · **Kiểm tra khẳng định (live)** · Quantum Lab (số QKA thật, có baseline) · Đánh giá (precision, kappa, phân loại lỗi).
- **Gỡ sạch** QSVM Accuracy 94.2% · Kernel Alignment 0.947 · Quantum Advantage +12.7%, cùng hai trang Anomaly/Cảnh báo mô phỏng. **Không nộp bất kỳ con số mô phỏng nào.**
- ⚠️ **Rủi ro pháp lý và uy tín:** dashboard công khai gắn nhãn "mâu thuẫn" kèm **tên doanh nghiệp niêm yết thật**, trong khi rà sơ bộ cho thấy gần hết cờ hiện tại là oan. Vì vậy:
  - Trên giao diện công khai, đổi nhãn hiển thị thành **"cần xem xét"**.
  - Đặt banner cố định: "Kết quả thử nghiệm tự động phục vụ cuộc thi, không phải kết luận kiểm toán".
  - Chỉ deploy kết quả **sau khi đã vá** nguồn cờ oan.
- ⚠️ **Repo phải giữ private** hoặc phải xoá khỏi lịch sử git trước khi công khai: `SmartAudit_Quantum_Proposal.docx` đã commit có **số CCCD và số điện thoại** của cả đội. Deploy bằng upload thư mục build, không bật GitHub Pages trên repo này.

### 6.3. Lớp lượng tử — QKA proof-of-concept

> **Kết quả 12/11 — đã chạy xong** (`docs/quantum-poc.md`, `results/qka_results.json`, `python scripts/run_qka.py`). 5 phần, seed 42, 8 qubit, statevector, chạy 18,7 phút. **Lượng tử thua cổ điển**, đúng như dự kiến ở quy mô này:
>
> | Phương pháp | Accuracy | Macro-F1 |
> |---|---|---|
> | rapidfuzz (cách hệ thống đang dùng) | 0,812 ± 0,030 | 0,801 ± 0,047 |
> | **SVM-RBF, 8 chiều** | **0,911 ± 0,051** | **0,904 ± 0,062** |
> | QSVM, kernel ZZ cố định | 0,734 ± 0,055 | 0,722 ± 0,064 |
> | QSVM + QKA | 0,840 ± 0,048 | 0,829 ± 0,062 |
>
> - **Đọc kết quả:**
>   - QKA nâng alignment 0,293 → 0,511 và accuracy 0,734 → 0,840 so với kernel cố định (hơn ở 5/5 phần), nhưng thua SVM-RBF ở 5/5 phần và huấn luyện chậm hơn khoảng 260 lần.
>   - Trình bày là **kiểm chứng khả thi + kết quả âm trung thực**.
> - **Phát hiện phụ có giá trị:** SVM cổ điển (0,911) vượt rapidfuzz (0,812) mà hệ thống đang dùng, nên thí nghiệm lượng tử dẫn tới một cải tiến cổ điển. Nhưng rapidfuzz ở ngưỡng 88 của hệ thống chỉ trả lời 49,6% số tên, đúng 98,4% trong số đó. Đổi sang SVM phải giữ cơ chế "không chắc thì im lặng".
> - **Cần Phong duyệt trước khi lên slide:**
>   - Nhãn là Mã số của bảng lưu chuyển tiền tệ, phần hoạt động đầu tư (mã 21–27, 30), chưa phải khoản mục ontology.
>   - Chỉ có **282 tên khác nhau** (1.945 dòng), không phải "hàng nghìn cặp".
>   - QKA kẹt cực trị địa phương ở vài phần.
>   - Parser còn để nguyên mã HTML (`&quot;`) trong tên khoản mục.

- **Bài toán:** cho tên khoản mục ở bảng **không có cột Mã số**, xác định nó thuộc khoản mục nào. Nhãn sinh tự động từ mọi bảng **có** Mã số: 1.945 dòng nhưng chỉ 282 tên khác nhau, và mỗi tên là một mẫu để không rò rỉ giữa train và test.
- **Thiết lập:** đặc trưng tên khoản mục → giảm còn 8 chiều → feature map 8 qubit → kernel huấn luyện được (QKA) → SVC. Statevector simulator; ≤ 500 mẫu huấn luyện; nhóm 5–8 khoản mục hay bị nhầm nhất; kiểm chứng chéo 5 lần.
- **Đường cơ sở trên cùng cách chia:** rapidfuzz (cách hệ thống đang dùng) và SVM-RBF.
- **Báo cáo:** accuracy/F1, thời gian chạy, số qubit, độ sâu mạch. Thua cổ điển thì ghi thua, đúng cam kết Phần V hồ sơ. Trình bày là **kiểm chứng tính khả thi kỹ thuật**, không phải benchmark lợi thế lượng tử. Lớp lượng tử **tháo rời được**, hệ thống vẫn chạy đủ với kernel cổ điển.

### 6.4. Mã nguồn zip và Hướng dẫn *(làm sau cùng, sáng 19/11)*

Chưa đóng gói trong lúc code còn thay đổi. Phần dưới chỉ là danh mục để không quên khi đến lúc làm.

**Trong zip:** `smartaudit/` · `scripts/` · `tests/` · `api/` · `prototype/` · `requirements.txt` đã ghim phiên bản · `README.md` · `data/sample/` (BCTC TiniX và văn bản BCTN đã bóc của các DN demo, đủ để chạy toàn bộ pipeline **không cần mạng**) · `data/labels/gold_300.csv` · `results/` · `NOTICE` (nguồn và giấy phép dữ liệu: BCTC từ TiniX, CC-BY-NC-4.0; **BCTN tải từ Vietstock** — đúng như `smartaudit/ingest/vietstock.py`, không phải Zenodo như hồ sơ v3 ghi; tài liệu công bố thông tin bắt buộc, cần kiểm điều khoản sử dụng của Vietstock).

**Không có trong zip:** `.venv`, cache, PDF BCTN gốc (958 MB; có script tải lại), **mọi tệp hồ sơ chứa CCCD**.

**Hướng dẫn PDF gồm:**

1. Link prototype
2. Yêu cầu hệ thống
3. Cài đặt trên Windows / macOS / Linux
4. Chạy test (kỳ vọng `N passed`)
5. Chạy pipeline trên dữ liệu mẫu
6. Chạy dashboard và API tại máy
7. Dùng từng chức năng
8. **Cách kiểm tra kết quả**: lệnh `audit_report.py` cho từng DN demo kèm đầu ra kỳ vọng, để BGK đối chiếu
9. Xử lý sự cố thường gặp: venv chuyển máy, `HF_HOME`, font qua `file://`

**Nghiệm thu:** Nguyên (không viết code) làm theo Hướng dẫn trên một laptop chưa từng cài project, từ giải nén đến lúc thấy dashboard, **không ai được nhắc**.

### 6.5. Kịch bản demo (4 ca, theo Phần IX hồ sơ)

| Kịch bản | Ứng viên | Ghi chú |
|---|---|---|
| Nhất quán (đối chứng) | **FPT 2022 tr.52** (doanh thu 44.010 tỷ +23,4%; LNTT 7.662 tỷ +20,9%, mọi số khớp ô bảng). Dự phòng: VNM 2024 tr.31, PLX 2018 tr.44 | Chắc chắn cao. ~~VNM 2024 "7,6% và 48,4%"~~ là câu về Angkormilk, **cáo buộc oan**, bỏ. |
| Mâu thuẫn số rõ ràng | **Không có ca thật đạt chuẩn**, mọi ca lệch lớn đều oan → dùng **câu chèn lỗi** (6.1b) | Ứng viên lỗi thật: MWG 2022 tr.7 "133.400 ngàn tỷ" (lỗi đánh máy đơn vị) |
| **Mâu thuẫn ngầm** (định tính ↔ số) | **Không có ca thật** → dùng câu chèn lỗi. Chiều nhất quán: VNM 2021 tr.53 (sau khi vá luật "kiểm soát") | Điểm mới số 1. Hiện 11/13 câu "kiểm soát" là "nhất quán ăn may" vì đem tồn kho chia doanh thu, phải vá trước |
| Xu hướng nhiều kỳ | PC1 2019–2024 (chắc chắn thấp) | Mọi lần điểm tụt hiện nay đều do cờ oan. Chỉ dựng sau khi vá. |

Chi tiết từng ứng viên, phép tính lại từ ô bảng và các ca đã loại: `docs/demo/ung-vien-demo.md`.

**Quy tắc không ngoại lệ:** ca nào lên slide hoặc video đều phải được Nguyên kiểm tay đến từng ô trong bảng gốc.

---

## 7. Báo cáo giải pháp — ánh xạ tiêu chí sang minh chứng

Mẫu BTC gồm 8 mục: 01 Hồ sơ · 02 Tóm lược · 03–08 sáu tiêu chí. Mỗi tiểu mục **phải dẫn minh chứng**: bảng số, hình, tên tệp, hoặc link.

| Mục | Trọng số | Minh chứng sẽ đưa vào | Người viết |
|---|---|---|---|
| 03 · Bài toán | 20% | Ví dụ thật lấy từ pipeline (không phải ví dụ giả định); số liệu ACFE 2026; ràng buộc đã gặp và đã xử lý (TT200 vs TT49, bản scan, hình học PDF, phạm vi hợp nhất); nhận xét của kiểm toán viên | Nguyên |
| 04 · Dữ liệu | 15% | Bảng nguồn + giấy phép; phễu xử lý (338 → 337 bóc được bảng; 93 → x BCTN dùng được); quy trình gán nhãn + kappa; chia dev/test theo (DN, năm); vì sao không cần tăng cường dữ liệu | Nguyên |
| 05 · Giải pháp | 20% | Sơ đồ kiến trúc; vì sao neo bằng Mã số; tham số và ngưỡng; **precision/recall trên tập test + khoảng tin cậy**; số trước/sau vá nền; QKA vs baseline | Hùng + Phong |
| 06 · Prototype | 20% | Ảnh chụp từng chức năng; link; video; 121+ test; thời gian chạy; hạn chế đã biết | Phong |
| 07 · Triển khai | 15% | Người dùng (KTV, UBCKNN, nhà đầu tư tổ chức); chi phí vận hành thật (hosting, CPU-giờ cho mỗi báo cáo); bảo mật (chỉ dùng dữ liệu công khai); lộ trình sau cuộc thi; kết quả thử nghiệm KTV (n=2–3, ghi rõ là sơ bộ) | Tài |
| 08 · Trình bày | 10% | Danh mục tệp nộp; kịch bản 10 phút; ai trả lời nhóm câu hỏi nào | Tài |
| 02 · Tóm lược | — | Viết **sau cùng**, chỉ lấy số từ các mục trên | Hùng |

Lưu ý mẫu:

- Mẫu ghi `Bao_cao_gia_phap.dpf` là **lỗi đánh máy của mẫu**. Dùng tên trong thông báo: `Bao_cao_giai_phap.pdf`.
- Mẫu có 5 dòng thành viên; đội có 4 người, xoá dòng thứ 5.
- Thông tin CCCD/SĐT chỉ điền vào bản nộp BTC, không đưa vào slide, zip hay bất cứ thứ gì công khai.

---

## 8. Câu hỏi gửi BTC (AI-Quantum@hvtc.edu.vn), gửi ngay 12/11

1. ~~"Madoi" ghi thế nào~~ → đã chốt: `AQ2026-064`.
2. 8–12 trang có tính bìa, mục lục và trang bìa sau của mẫu không?
3. Giới hạn dung lượng tệp zip khi nộp trên website?
4. Thời lượng thuyết trình + hỏi đáp ở Vòng 2? *(Tạm chuẩn bị theo 10 phút + 8 phút như Vòng 3.)*
5. Video demo có bắt buộc không? *(Mẫu có ô "Video demo: [URL]". Vẫn quay để làm phương án dự phòng.)*

---

## 9. Rủi ro

| Rủi ro | Khả năng | Ứng phó |
|---|---|---|
| Precision < 80% | **Gần như chắc chắn** (rà sơ bộ: 138/141 cờ oan) | Vá nguồn cờ oan; đo bằng hai số (6.1b); thu hẹp phạm vi nếu cần; báo cáo trung thực cả số trước và sau |
| Giám khảo hỏi lại ví dụ VNM ở hồ sơ Vòng 1 | Trung bình | Chủ động nói trước, kể như bằng chứng về quy trình tự kiểm (6.1b) |
| Hồ sơ v3 khai BCTN lấy từ Zenodo, thực tế tải từ Vietstock | Đã xảy ra | Báo cáo mục 04 nói thẳng: bộ Zenodo chưa dùng, vì sao (đã có trong nháp) |
| Thông tư 99/2025/TT-BTC thay TT200 từ năm tài chính 2026 | Chắc chắn bị hỏi | Ontology là dữ liệu (YAML) sinh tự động từ corpus, nên ánh xạ lại Mã số là việc cấu hình, không phải viết lại hệ thống. Đưa vào lộ trình mục 07. |
| Hugging Face không còn Docker Space miễn phí | Đã xảy ra | Chạy lõi bằng Pyodide trong trình duyệt; dự phòng Render hoặc HF PRO (6.2) |
| Gán nhãn trễ (2 người × ~10 giờ) | Trung bình | Bắt đầu ngay 13/11. Sàn tối thiểu 200 cặp nếu bắt buộc, kèm khoảng tin cậy và giải thích. |
| Link prototype chết lúc BGK mở | Trung bình | Phần tĩnh không ngủ; API có keep-alive; video dự phòng; `run_demo.bat` chạy offline |
| BGK không cài được từ zip | Trung bình | Ghim phiên bản; kiểm thử máy sạch 18/11; dữ liệu mẫu offline |
| QKA không vượt cổ điển | Cao | Đã cam kết công bố kết quả âm. Trình bày là kiểm chứng khả thi. |
| Số liệu lệch giữa báo cáo, slide, dashboard | Trung bình | Mọi số sinh từ `evaluate.py` + JSON; soát chéo 19/11 |
| Lộ CCCD khi công khai repo hoặc zip | Thấp nhưng hậu quả nặng | Repo private; loại tệp hồ sơ khỏi zip; deploy bằng thư mục build |
| Website quá tải sát giờ | Trung bình | Nộp 21h 19/11 |

---

## 10. Quy tắc chung

1. **Không có con số nào không sinh ra từ script.** Báo cáo, slide và dashboard dùng chung một nguồn.
2. **Không con số mô phỏng nào trong bộ nộp.** Chưa đo thì ghi "chưa đo".
3. **Tập test chỉ chạy một lần**, sau khi đóng băng.
4. **Code freeze 22h 18/11.** Sau mốc đó chỉ sửa lỗi chặn demo hoặc chặn cài đặt.
5. Mỗi tối 22h, mỗi người báo một dòng: *xong gì · vướng gì · mai làm gì*.

---

## 11. Checklist nộp (19/11)

Tiền tố mọi tệp: `AQ2026-R2-AQ2026-064-`.

- [ ] `…-Bao_cao_giai_phap.pdf`: đúng mẫu, 8–12 trang, không còn ô `[...]`, link prototype ở mục 01.3 và 06.4
- [ ] `…-Slide.pptx`: mở được trên máy khác, font nhúng hoặc font phổ thông
- [ ] `…-Ma_nguon.zip`: giải nén ra cài chạy được (đã kiểm thử máy sạch), không có `.venv`, không có CCCD
- [ ] `…-Huong_dan.pdf`: có link prototype, ghi "không cần tài khoản", có đầu ra kỳ vọng để đối chiếu
- [ ] Link prototype: mở được từ mạng 4G, trình duyệt ẩn danh, trên điện thoại
- [ ] Khai link trong biểu mẫu nộp của BTC
- [ ] Tải lại 4 tệp từ website sau khi nộp, mở thử từng tệp
