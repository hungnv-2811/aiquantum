# Lớp lượng tử — QKA proof-of-concept

> **Kiểm chứng tính khả thi kỹ thuật trên mô phỏng statevector, không phải tuyên bố lợi thế lượng tử.**
> Mọi con số dưới đây lấy từ `results/qka_results.json` (chạy ngày 12/11/2026, hết 18.7 phút trên laptop, seed 42).
> Số viết dấu chấm thập phân để khớp nguyên văn với tệp JSON.

## 1. Bài toán

Hệ thống neo mỗi dòng bảng BCTC vào khoản mục bằng cột **Mã số** (TT200). Khi bảng **không có** cột này, phải đoán khoản mục từ tên dòng. Hiện hệ thống dùng `Ontology.by_label`: khớp chính xác, trượt thì khớp gần bằng rapidfuzz, ngưỡng 88. Thí nghiệm này so cách đó với SVM cổ điển và hai kernel lượng tử, trên cùng dữ liệu và cùng cách chia.

## 2. Dữ liệu

- **Nguồn:** bảng Lưu chuyển tiền tệ (LCTT) trong các BCTC TiniX đã tải, đọc bằng parser có sẵn. Chỉ lấy 13 doanh nghiệp phi ngân hàng (2015–2025). Ngân hàng lập theo TT49, hệ mã số khác, đọc theo TT200 sẽ ra nhãn sai.
- **Nhãn tự động:** lấy Mã số in ngay trên dòng ở những bảng *có* cột Mã số. Không có ai gán nhãn tay.
- **Nhóm 8 khoản mục:** phần *hoạt động đầu tư* của LCTT. Các mã đi thành cặp chi/thu gần trùng chữ (23 ↔ 24, 25 ↔ 26, 21 ↔ 22), nhầm một chữ là đảo chiều dòng tiền. Đây cũng là nhóm có nhiều cách viết nhất. Phần lớn khoản mục trong ontology hiện tại có quá ít tên khác nhau để chia 5 phần.

| Mã | Tên gặp nhiều nhất | Số tên khác nhau | Số dòng |
|---|---|---|---|
| 21 | Tiền chi mua tài sản cố định và tài sản dài hạn khác | 35 | 250 |
| 22 | Tiền thu từ thanh lý tài sản cố định và tài sản dài hạn khác | 35 | 227 |
| 23 | Tiền chi cho vay, mua các công cụ nợ của đơn vị khác | 46 | 261 |
| 24 | Tiền thu hồi cho vay, bán lại công cụ nợ của đơn vị khác | 41 | 246 |
| 25 | Tiền chi đầu tư góp vốn vào đơn vị khác | 34 | 229 |
| 26 | Tiền thu hồi đầu tư góp vốn vào đơn vị khác | 25 | 207 |
| 27 | Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia | 54 | 256 |
| 30 | Lưu chuyển tiền thuần từ hoạt động đầu tư | 12 | 268 |

- **Phễu:** 1945 dòng → 282 tên khác nhau → **282 mẫu**. 2 tên mang nhiều mã được giải theo đa số. 1 mảnh OCR quá ngắn bị bỏ.
- **Chống rò rỉ:** mỗi tên chỉ là **một** mẫu, nên không tên nào nằm ở cả train và test. Chọn cách chia theo tên thay vì theo doanh nghiệp vì tên chuẩn TT200 lặp ở hầu hết doanh nghiệp. Chia theo doanh nghiệp vẫn để tên trùng ở hai phía. Ngoài ra còn bỏ chữ số khỏi tên, vì công thức kiểu "(30 = 21 + …)" chứa chính Mã số. Ontology cho rapidfuzz cũng dựng lại **chỉ từ tập huấn luyện** của từng phần, theo đúng cách `build_ontology.py` làm (8 tên phổ biến nhất mỗi mã). Không dùng `vas_mapping.yaml` vì tệp này chưa có mã 21–27 và rút alias từ toàn corpus.

## 3. Thiết lập

- **Chia:** StratifiedKFold 5 phần, seed 42, cùng cách chia cho mọi phương pháp. Mỗi phần có 225–226 mẫu huấn luyện (trần cho phép là 500) và 56–57 mẫu kiểm tra.
- **Đặc trưng (học trên tập huấn luyện của từng phần):**
  1. TF-IDF n-gram ký tự 2–4, chịu được lỗi OCR và dính chữ.
  2. TruncatedSVD xuống **8 chiều** (= 8 qubit), giữ 53–54% phương sai.
  3. Co giãn tuyến tính về [0, π] để mỗi chiều thành một góc quay.
- **SVM:** C chọn bằng kiểm chứng chéo 3 phần *bên trong* tập huấn luyện, `class_weight="balanced"`. RBF dò thêm γ.
- **Kernel cố định:** ZZFeatureMap 8 qubit, reps=2, vướng víu linear, fidelity kernel |⟨φ(x)|φ(y)⟩|².
- **QKA:** cùng mạch, thêm 16 tham số học được:
  - 8 hệ số co giãn λ (thay x_i bằng λ_i·x_i, tức "độ rộng" kernel);
  - 8 góc RY θ đặt trước khâu mã hoá (dạng QKA của Glick và cộng sự, 2021).
  
  Khởi đầu λ = 1, θ = 0, trùng đúng kernel cố định. Huấn luyện bằng `QuantumKernelTrainer` + COBYLA (150 lần tính, rhobeg 1.0), tối đa hoá *centered kernel-target alignment*. Không dùng `SVCLoss` mặc định vì nó chỉ đúng cho bài nhị phân (đọc `dual_coef_[0]`).
- **Mô phỏng:** `qiskit.quantum_info.Statevector`, chính xác, không nhiễu, không shot. Không cần qiskit-aer.
- **Mạch:** dịch về cổng cơ bản {cx, rz, sx, x}.
  - Feature map: độ sâu 33 (cố định) / 34 (QKA), 28 CNOT.
  - Mạch đo một ô kernel U(y)†U(x): độ sâu 63 / 65, 54 CNOT.

## 4. Kết quả (trung bình ± độ lệch chuẩn qua 5 phần)

| Phương pháp | Vai trò | Accuracy | Macro-F1 | Huấn luyện (s/phần) | Suy luận (ms/mẫu) | Qubit | Độ sâu mạch kernel |
|---|---|---|---|---|---|---|---|
| rapidfuzz, 8 alias/mã (như hệ thống) | chính | 0.812 ± 0.030 | 0.801 ± 0.047 | 0.00 | 0.46 | — | — |
| SVM-RBF, 8 chiều | chính | **0.911 ± 0.051** | **0.904 ± 0.062** | 0.82 | 0.02 | — | — |
| QSVM, kernel ZZ cố định | chính | 0.734 ± 0.055 | 0.722 ± 0.064 | 1.45 | 22.35 | 8 | 63 |
| QSVM, kernel huấn luyện bằng QKA | chính | 0.840 ± 0.048 | 0.829 ± 0.062 | 216.70 | 23.25 | 8 | 65 |
| rapidfuzz, mọi tên huấn luyện (1-NN) | tham khảo | 0.851 ± 0.043 | 0.833 ± 0.058 | 0.00 | 0.56 | — | — |
| SVM tuyến tính, TF-IDF đầy đủ (không nén) | tham khảo | 0.904 ± 0.016 | 0.893 ± 0.028 | 0.75 | 0.17 | — | — |

**Kernel alignment** (centered; 1 = kernel khớp hoàn hảo với nhãn):

| | RBF | ZZ cố định = QKA trước | QKA sau |
|---|---|---|---|
| Tập huấn luyện | 0.598 ± 0.034 | 0.293 ± 0.014 | 0.511 ± 0.088 |
| Tập kiểm tra | 0.629 ± 0.042 | 0.407 ± 0.010 | 0.573 ± 0.090 |

Alignment phụ thuộc cỡ mẫu, nên chỉ so giữa các kernel **trong cùng một hàng**, không so hàng train với hàng test.

**rapidfuzz với đúng ngưỡng 88 của hệ thống:** chỉ trả lời 49.6% số tên. Trong số đã trả lời thì đúng 98.4%.

## 5. Diễn giải

1. **Lượng tử thua cổ điển.** SVM-RBF trên *cùng* 8 chiều thắng QSVM+QKA ở cả 5/5 phần: 0.911 so với 0.840 accuracy. QKA còn thấp hơn rapidfuzz 1-NN (0.851). QKA hơn rapidfuzz 8 alias ở 3/5 phần, trung bình 0.840 so với 0.812.
2. **Kernel cố định gần như vô dụng vì quá "hẹp".** Trung bình ngoài đường chéo của ma trận kernel chỉ 0.011: mọi cặp tên khác nhau đều bị coi là không giống nhau. Hệ quả: 50/75 lỗi của nó là đoán dồn về mã 27, lớp đông nhất.
3. **QKA có tác dụng thật nhưng chưa đủ.** QKA hơn kernel cố định ở 5/5 phần (0.734 → 0.840), alignment huấn luyện tăng 0.293 → 0.511. Cơ chế đúng như dự kiến: 29/40 hệ số λ co về |λ| < 0.5, tức kernel rộng ra, cùng hướng với việc RBF chọn γ nhỏ. Tuy vậy COBYLA chững lại ở các cực trị địa phương khác nhau giữa các phần (alignment cuối 0.39–0.60, 30 lần tính cuối tăng không quá 0.004). Đó là lý do độ lệch giữa các phần lớn.
4. **Nén về 8 chiều không phải nút thắt.** SVM tuyến tính trên TF-IDF đầy đủ (0.904) không hơn RBF 8 chiều (0.911). Khoảng cách nằm ở kernel và khâu tối ưu kernel, không ở số qubit.
5. **Lỗi chung của mọi phương pháp là đảo chiều chi/thu.** Riêng 23 → 24 (chi cho vay bị đoán là thu hồi cho vay) đã là 12 trong 53 lỗi của rapidfuzz. Đây là lỗi nguy hiểm nhất cho đối chiếu NNC.
6. **Ý nghĩa cho hệ thống:** ngưỡng 88 hiện tại an toàn (đúng 98.4% khi trả lời) nhưng bỏ trống một nửa. Đường cải thiện thực tế là SVM cổ điển, không phải kernel lượng tử. Lớp lượng tử cắm vào qua đúng một ma trận kernel, nên rút ra hay thay bằng RBF không phải sửa gì khác.

## 6. Giới hạn

- Chỉ là mô phỏng: chưa có nhiễu, chưa có shot. Trên phần cứng, mỗi ô kernel là một mạch 54 CNOT, và một ma trận 226 × 226 cần hàng chục nghìn mạch như vậy *cho mỗi bước* tối ưu.
- QKA chậm hơn RBF khoảng 260 lần khi huấn luyện, và suy luận mất khoảng 23 ms/mẫu so với 0.02 ms/mẫu. 8 qubit vẫn mô phỏng được trên máy cổ điển, nên ở cỡ này không thể có lợi thế lượng tử.
- Dữ liệu nhỏ: 282 tên, 13 doanh nghiệp, một nhóm khoản mục. Độ lệch chuẩn accuracy giữa các phần của 4 phương pháp chính (0.030–0.055) cùng cỡ với nhiều khác biệt trong bảng.
- Nhãn tự động có nhiễu thật: bảng bị phân loại nhầm báo cáo, hoặc OCR gộp hai dòng làm một (xem `results/qka_cache/dataset.csv`).
- Đo trên *tên khác nhau*, không trọng số theo tần suất xuất hiện. Tên chuẩn phổ biến thì mọi phương pháp đều đúng, nên độ chính xác trên dòng thực tế sẽ cao hơn.
- `rhobeg` = 1.0 được chọn bằng chạy thử trên tập *huấn luyện* phần 1, chỉ nhìn alignment huấn luyện, không nhìn tập kiểm tra. Bước nhỏ hơn làm COBYLA kẹt gần điểm xuất phát.

## 7. Chạy lại

```powershell
uv venv --python 3.11 .venv-quantum
uv pip install --python .venv-quantum\Scripts\python.exe -r requirements-quantum.txt
.venv-quantum\Scripts\python.exe scripts\run_qka.py          # ~20 phút, ghi results\qka_results.json
.venv-quantum\Scripts\python.exe scripts\run_qka.py --quick  # ~1 phút, thử nhanh, ghi vào results\qka_cache\
.venv-quantum\Scripts\python.exe scripts\run_qka.py --dataset-only  # vài giây, chỉ ghi results\qka_cache\dataset.csv
.venv-quantum\Scripts\python.exe -m pytest tests -q          # gồm tests\test_quantum.py
```

Mã nguồn: `smartaudit/quantum/dataset.py` (dữ liệu), `smartaudit/quantum/qka.py` (đặc trưng, mạch, QKA, đường cơ sở), `scripts/run_qka.py`. Môi trường chính `.venv` không cần qiskit: `tests/test_quantum.py` tự bỏ qua.
