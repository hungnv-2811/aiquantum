"""Kiểm thử lớp lượng tử (QKA proof-of-concept).

Cả file bị **bỏ qua** nếu chưa cài qiskit: môi trường chính ``.venv`` không
có qiskit và bộ test chính vẫn phải xanh. Chạy đầy đủ bằng::

    .venv-quantum\\Scripts\\python.exe -m pytest tests -q

Mọi phép kiểm ở đây chạy trên mạch nhỏ (2–3 qubit) và vài chục mẫu, tổng
dưới 10 giây. Thí nghiệm thật ở ``scripts/run_qka.py``.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_machine_learning")
pytest.importorskip("sklearn")

from smartaudit.config import TINIX_DIR  # noqa: E402
from smartaudit.quantum import dataset as ds  # noqa: E402
from smartaudit.quantum import qka  # noqa: E402

needs_data = pytest.mark.skipif(
    not (TINIX_DIR / "ocr_results").is_dir(),
    reason="Chưa có dữ liệu — chạy: python scripts/fetch_data.py",
)


def _row(code: str, label: str, ticker: str = "AAA") -> ds.RawRow:
    return ds.RawRow(ticker=ticker, year=2024, code=code, label=label)


class TestNameKey:
    def test_bo_dau_va_so_thu_tu(self) -> None:
        assert ds.name_key("3. Tiền chi cho vay") == "tien chi cho vay"

    def test_bo_moi_chu_so_vi_cong_thuc_chua_ma_so(self) -> None:
        # Công thức có chính Mã số 30 — giữ lại là rò rỉ nhãn vào đặc trưng.
        key = ds.name_key(
            "Lưu chuyển tiền thuần từ hoạt động đầu tư\\( (30 = 21 + 22 + 27) \\)"
        )
        assert key == "luu chuyen tien thuan tu hoat dong dau tu"

    def test_loi_ocr_dat_sai_dau_cho_cung_khoa(self) -> None:
        assert ds.name_key("Tiên chi cho vay") == ds.name_key("Tiền chi cho vay")

    def test_giai_ma_thuc_the_html(self) -> None:
        # Parser để nguyên &quot; — không giải mã thì sinh chữ "quot" giả.
        assert ds.name_key("Tài sản cố định (&quot;TSCĐ&quot;)") == "tai san co dinh tscd"


class TestBuildDataset:
    def test_ten_lap_lai_gop_thanh_mot_mau(self) -> None:
        rows = [_row("23", "Tiền chi cho vay")] * 3 + [
            _row("23", "1. Tiền chi cho vay", ticker="BBB")
        ]
        samples, stats = ds.build_dataset(rows)
        assert len(samples) == 1
        assert samples[0].n_rows == 4 and samples[0].n_tickers == 2
        assert samples[0].raw == "Tiền chi cho vay"  # cách viết gặp nhiều nhất
        assert stats.n_rows == 4 and stats.n_samples == 1

    def test_nhan_theo_da_so(self) -> None:
        name = "Lưu chuyển tiền thuần từ hoạt động đầu tư"
        rows = [_row("30", name)] * 5 + [_row("27", name)]
        samples, stats = ds.build_dataset(rows)
        assert [s.code for s in samples] == ["30"]
        assert stats.n_conflicts == 1 and stats.n_conflicts_dropped == 0

    def test_hoa_phieu_thi_bo(self) -> None:
        rows = [_row("26", "Tiền thu khác"), _row("27", "Tiền thu khác")]
        samples, stats = ds.build_dataset(rows)
        assert samples == [] and stats.n_conflicts_dropped == 1

    def test_bo_manh_ocr_qua_ngan(self) -> None:
        samples, stats = ds.build_dataset([_row("23", "(*) 12")])
        assert samples == [] and stats.n_short_dropped == 1


class TestFolds:
    @staticmethod
    def _samples() -> list[ds.NameSample]:
        # Tên chỉ khác nhau ở chữ cái (chữ số bị name_key bỏ đi).
        rows = [
            _row(code, f"Tiền loại {chr(97 + k)} biến thể {chr(97 + i)}{chr(97 + j)}")
            for k, code in enumerate(ds.GROUP) for i in range(3) for j in range(2)
        ]
        # Thêm bản lặp y hệt: sau khử trùng lặp vẫn chỉ là một mẫu mỗi tên.
        rows += rows[:10]
        return ds.build_dataset(rows)[0]

    def test_khong_ten_nao_nam_o_ca_hai_phia(self) -> None:
        samples = self._samples()
        for train, test in ds.make_folds([s.code for s in samples], 5, seed=42):
            assert not {samples[i].key for i in train} & {samples[i].key for i in test}

    def test_cung_hat_giong_cung_cach_chia(self) -> None:
        labels = [s.code for s in self._samples()]
        assert ds.make_folds(labels, 5, seed=7) == ds.make_folds(labels, 5, seed=7)

    def test_moi_phan_kiem_tra_du_cac_ma(self) -> None:
        labels = [s.code for s in self._samples()]
        for _, test in ds.make_folds(labels, 5, seed=42):
            assert {labels[i] for i in test} == set(ds.GROUP)


class TestAlignment:
    Y = ["a", "a", "b", "b", "c", "c"]

    def test_kernel_ly_tuong_dat_1(self) -> None:
        y = np.array(self.Y)
        ideal = (y[:, None] == y[None, :]).astype(float)
        assert qka.centered_alignment(ideal, self.Y) == pytest.approx(1.0)

    def test_kernel_hang_so_dat_0(self) -> None:
        # Coi mọi tên giống hệt nhau thì vô dụng — căn giữa phải cho ra 0.
        assert qka.centered_alignment(np.ones((6, 6)), self.Y) == 0.0

    def test_kernel_don_vi_thap_hon_ly_tuong(self) -> None:
        assert 0 < qka.centered_alignment(np.eye(6), self.Y) < 1


class TestFeatures:
    def test_dung_so_chieu_va_nam_trong_0_pi(self) -> None:
        names = [f"tien chi {w} don vi khac" for w in
                 ("cho vay", "dau tu", "mua sam", "gop von", "thanh ly",
                  "thu hoi", "co tuc", "lai vay", "tai san", "cong cu no")]
        feats = qka.build_features(n_components=4, seed=0)
        x_train = feats.fit_transform(names)
        x_test = feats.transform(["mot ten hoan toan khac", "tien thu hoi cho vay"])
        assert x_train.shape == (10, 4) and x_test.shape == (2, 4)
        for x in (x_train, x_test):
            assert x.min() >= 0.0 and x.max() <= np.pi + 1e-9


class TestQuantumKernel:
    def test_qka_khoi_dau_dung_bang_kernel_co_dinh(self) -> None:
        # λ = 1, θ = 0 phải cho đúng kernel cố định: "trước QKA" = kernel cố định.
        from qiskit_machine_learning.kernels import TrainableFidelityStatevectorKernel

        x = np.random.default_rng(0).uniform(0, np.pi, size=(6, 3))
        circuit, training, initial = qka.trainable_feature_map(n_qubits=3, reps=2)
        trainable = TrainableFidelityStatevectorKernel(
            feature_map=circuit, training_parameters=training
        )
        trainable.assign_training_parameters(initial)
        fixed = qka.fixed_kernel(n_qubits=3, reps=2)
        assert np.allclose(trainable.evaluate(x), fixed.evaluate(x))

    def test_kernel_hop_le(self) -> None:
        x = np.random.default_rng(1).uniform(0, np.pi, size=(5, 2))
        k = qka.fixed_kernel(n_qubits=2).evaluate(x)
        assert np.allclose(k, k.T) and np.allclose(np.diag(k), 1.0)
        assert k.min() >= 0.0 and k.max() <= 1.0 + 1e-9

    def test_huan_luyen_khong_lam_alignment_te_di(self) -> None:
        rng = np.random.default_rng(2)
        y = np.repeat(["a", "b", "c"], 4)
        x = rng.normal(np.repeat([[0.5], [1.5], [2.5]], 4, axis=0), 0.3, size=(12, 3))
        result = qka.train_qka(np.clip(x, 0, np.pi), y, n_qubits=3, reps=1, maxiter=10)
        assert result.alignment_after >= result.alignment_before
        assert result.n_evaluations <= 10
        assert len(result.optimal_point) == 6  # 3 λ + 3 θ

    def test_thong_ke_mach(self) -> None:
        stats = qka.circuit_stats(qka.fixed_feature_map(n_qubits=3, reps=2))
        assert stats["n_qubits"] == 3
        assert stats["kernel_circuit_depth"] > stats["feature_map_depth"] > 0


class TestRapidfuzz:
    TRAIN = [
        ds.NameSample("tien chi cho vay", "23", "Tiền chi cho vay", 50, 5),
        ds.NameSample("tien chi cho vay khac", "23", "Tiền chi cho vay khác", 1, 1),
        ds.NameSample("tien thu hoi cho vay", "24", "Tiền thu hồi cho vay", 40, 4),
    ]

    def test_dung_ham_by_label_cua_he_thong(self) -> None:
        onto = qka.build_fold_ontology(self.TRAIN, aliases_per_code=8)
        assert qka.predict_rapidfuzz(onto, ["2. Tiền thu hồi cho vay"], cutoff=0) == ["24"]

    def test_duoi_nguong_thi_khong_tra_loi(self) -> None:
        onto = qka.build_fold_ontology(self.TRAIN, aliases_per_code=8)
        assert qka.predict_rapidfuzz(onto, ["Cổ tức đã trả"], cutoff=88) == [None]

    def test_chi_giu_alias_pho_bien_nhat(self) -> None:
        onto = qka.build_fold_ontology(self.TRAIN, aliases_per_code=1)
        assert onto.by_code(ds.STATEMENT, "23").aliases == ("Tiền chi cho vay",)


@needs_data
class TestDuLieuThat:
    def test_vnm_co_dong_dau_tu_va_dong_tong(self) -> None:
        rows = list(ds.collect_rows(tickers=["VNM"]))
        assert {r.code for r in rows} == set(ds.GROUP)
        keys = {(r.code, ds.name_key(r.label)) for r in rows}
        assert ("30", "luu chuyen tien thuan tu hoat dong dau tu") in keys

    def test_bo_qua_ngan_hang(self) -> None:
        assert list(ds.collect_rows(tickers=["MBB"])) == []
