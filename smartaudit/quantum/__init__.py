"""Lớp lượng tử — Quantum Kernel Alignment (QKA) proof-of-concept.

Bài toán: khi bảng báo cáo tài chính **không có cột Mã số**, đoán khoản mục
của mỗi dòng chỉ từ tên dòng. So kernel lượng tử (cố định và huấn luyện
bằng QKA) với đường cơ sở cổ điển trên cùng dữ liệu, cùng cách chia.

Lớp này **tháo rời được**:

* Cần môi trường riêng ``.venv-quantum`` (xem ``requirements-quantum.txt``);
  môi trường chính ``.venv`` không cài qiskit vẫn chạy đủ pipeline NNC.
* Không module nào ngoài thư mục này import nó. Gói này cũng **không** tự
  import ``qka`` (phần cần qiskit) — chỉ import khi gọi tường minh::

      from smartaudit.quantum import dataset      # không cần qiskit
      from smartaudit.quantum import qka          # cần qiskit

Chạy lại thí nghiệm: ``scripts/run_qka.py``. Kết quả và diễn giải:
``results/qka_results.json``, ``docs/quantum-poc.md``.
"""
