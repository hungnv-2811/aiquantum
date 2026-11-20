# Bộ mẫu chạy từ bản clone

- Hai BCTC OCR hợp nhất: VNM 2024 và FPT 2022, tải từ bộ `tinixai/ocr_annual_financials` trên Hugging Face (CC BY-NC 4.0). `manifest.json` ghi revision, URL và SHA-256 từng tệp.
- `narratives.json`: bốn trích đoạn BCTN đã có trong `results/nnc_results.json`, giữ nguyên câu và trang. Đây là trích đoạn đã bóc chữ, không phải PDF đầy đủ; có thể còn lỗi bố cục của nguồn cũ.
- Chỉ dùng kiểm tra khả năng chạy: đọc OCR → bóc bảng → trích khẳng định → đối chiếu → minh chứng. Không dùng bộ mẫu này để công bố accuracy/precision hay thay kết quả 98 báo cáo.

Chạy từ gốc repo:

```powershell
python -m pip install -r requirements-sample.txt
python scripts/check_environment.py --mode sample
python scripts/run_sample.py
```

Kỳ vọng: FPT 2022 có 7 bảng, VNM 2024 có 9 bảng; mỗi mã có hai trích đoạn. Các kết luận chỉ phản ánh những khẳng định bộ trích xuất hiện tại nhận diện được, không bảo đảm đã kiểm mọi vế trong câu.

Dashboard có snapshot đầy đủ riêng ở `prototype/data/`, khớp 98 báo cáo đã lưu trong `results/`. Mẫu nhỏ không ghi đè dữ liệu đó.

`scripts/restore_demo_data.py` dùng mạng để tải lại snapshot công khai và hai BCTC. Script dừng nếu snapshot online khác kết quả hiện có. Bình thường bản clone đã kèm tệp, không cần chạy lệnh khôi phục.
