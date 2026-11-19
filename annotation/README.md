# Gán nhãn 300 cặp khẳng định – minh chứng

Đây là tập "đáp án" để đo **precision nhóm mâu thuẫn**, chỉ số quan trọng nhất của Vòng 2 (cam kết Phần V mục 8 hồ sơ).

| Tệp | Dành cho | Ghi chú |
|---|---|---|
| `sheet_nguoi_gan_1.csv` | Nguyên | Mở bằng Excel. Điền 4 cột cuối. |
| `sheet_nguoi_gan_2.csv` | Tài | Giống hệt tệp 1. **Hai người làm độc lập, không trao đổi đáp án.** |
| `sample_key.csv` | Hùng, Phong | Phán quyết của hệ thống, tầng, trọng số, dev/test. **Người gán nhãn không mở tệp này.** |

Hướng dẫn gán nhãn chi tiết: `docs/gan-nhan/huong-dan-gan-nhan.md`.

## Bốn cột cần điền

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `la_khang_dinh` | `C` / `K` | Câu có phải khẳng định kiểm chứng được bằng BCTC không. Rác bảng biểu, kế hoạch tương lai, câu chỉ nói về một bộ phận/công ty con → `K` |
| `chi_tieu_dung` | `C` / `K` / `?` | Số liệu bảng trên dòng đó có đúng là thứ câu đang nói tới không (đúng khoản mục, đúng phạm vi hợp nhất, đúng kỳ) |
| `nhan` | `NQ` / `MT` / `KKC` | Nhất quán / Mâu thuẫn / Không kiểm chứng được từ BCTC |
| `ghi_chu` | tự do | Lý do khi chọn `MT`, `KKC` hoặc `?`. Ghi ngắn. |

## Lưu ý khi đọc số

- Cột `nam_nay_nhu_in_trong_bang` và `nam_truoc_nhu_in_trong_bang` giữ **nguyên số in trong bảng gốc**. Khoảng 1/4 báo cáo ghi theo **nghìn đồng** hoặc **triệu đồng**. Hãy xem dòng "Đơn vị tính" ở đầu bảng trong BCTC (`bctc_nguon`, trang `trang_bctc`) trước khi so với con số trong câu.
- Với chỉ tiêu dạng tỷ lệ (biên lợi nhuận), cột `bien_dong` là chênh lệch **điểm phần trăm**. Với số tiền, cột này là tỷ lệ tăng/giảm.
- Cột `ngu_canh` là đoạn văn quanh câu gốc trong báo cáo thường niên. Đọc nó để biết câu đang nói về toàn tập đoàn hay một công ty con, một mảng.
- 6 dòng không tra được chỉ tiêu trong BCTC. Vẫn điền `la_khang_dinh` và `nhan`; nếu tự tìm được số trong BCTC thì ghi vào `ghi_chu`.

## Lịch

- 13/11: mỗi người xong 100 dòng.
- 14/11: xong 200 dòng.
- 15/11: xong 300 dòng, gửi lại tệp cho Hùng. Phong phân xử các dòng hai người khác nhau, rồi tính Cohen's kappa.

## Sinh lại

```bash
python scripts/sample_for_labeling.py 300 2026
```

Cùng seed cho ra đúng mẫu này. **Không sinh lại sau khi đã bắt đầu gán nhãn**, vì nhãn gắn theo `id`.
