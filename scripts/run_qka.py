"""Chạy lại toàn bộ thí nghiệm QKA proof-of-concept bằng một lệnh.

So sánh 4 phương pháp chính (cộng 2 dòng tham khảo) trên **cùng** cách chia
5 phần, cùng hạt giống, cho bài toán: đoán Mã số của một dòng trong bảng lưu
chuyển tiền tệ khi bảng **không có cột Mã số**. Xem
``smartaudit/quantum/`` và ``docs/quantum-poc.md``.

Cần môi trường riêng của lớp lượng tử (``.venv-quantum``, xem
``requirements-quantum.txt``). Chỉ đọc ``data/raw/tinix``; ghi:

* ``results/qka_results.json`` — mọi con số, kèm cấu hình, hạt giống, phiên
  bản thư viện và thời điểm chạy
* ``results/qka_cache/dataset.csv`` — bộ dữ liệu đã dựng kèm phần kiểm tra
  của từng tên, để soát tay (chỉ dựng lại tệp này: thêm ``--dataset-only``)

Chạy (từ thư mục gốc repo, ~20 phút trên laptop — gần hết là QKA)::

    .venv-quantum\\Scripts\\python.exe scripts\\run_qka.py

Chạy thử nhanh (~1 phút, 2 phần, QKA ít vòng; ghi vào ``results/qka_cache/``,
không đè kết quả chính)::

    .venv-quantum\\Scripts\\python.exe scripts\\run_qka.py --quick
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import platform
import sys
import time
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score  # noqa: E402
from sklearn.metrics.pairwise import rbf_kernel  # noqa: E402
from sklearn.model_selection import StratifiedShuffleSplit  # noqa: E402

from smartaudit.config import RESULTS  # noqa: E402
from smartaudit.quantum import dataset as ds  # noqa: E402
from smartaudit.quantum import qka  # noqa: E402

CACHE = RESULTS / "qka_cache"

#: Thứ tự dòng trong bảng kết quả. ``chính`` = 4 phương pháp hồ sơ cam kết so
#: sánh; ``tham khảo`` = dòng phụ giúp diễn giải, không thuộc phép so sánh.
METHODS: list[tuple[str, str, str]] = [
    ("rapidfuzz_top8", "rapidfuzz, 8 alias/mã (như hệ thống)", "chính"),
    ("svm_rbf", "SVM-RBF, 8 chiều", "chính"),
    ("qsvm_fixed", "QSVM, kernel ZZ cố định", "chính"),
    ("qsvm_qka", "QSVM, kernel huấn luyện bằng QKA", "chính"),
    ("rapidfuzz_1nn", "rapidfuzz, mọi tên huấn luyện (1-NN)", "tham khảo"),
    ("svm_linear_full", "SVM tuyến tính, TF-IDF đầy đủ (không nén)", "tham khảo"),
]


def _cap_train(train_idx: list[int], labels: list[str], max_n: int, seed: int) -> list[int]:
    """Giữ tối đa ``max_n`` mẫu huấn luyện (lấy mẫu phân tầng) — trần của đề bài."""
    if len(train_idx) <= max_n:
        return train_idx
    y = [labels[i] for i in train_idx]
    keep, _ = next(
        StratifiedShuffleSplit(n_splits=1, train_size=max_n, random_state=seed).split(y, y)
    )
    return sorted(train_idx[i] for i in keep)


def _scores(y_true: list[str], y_pred: list[str | None]) -> dict:
    """Accuracy và macro-F1 trên đúng 8 mã của nhóm.

    Dự đoán ``None`` (rapidfuzz không đủ ngưỡng) tính là **sai**: nó làm giảm
    recall của lớp thật mà không cộng vào lớp nào.
    """
    pred = [p if p is not None else "none" for p in y_pred]
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "macro_f1": float(
            f1_score(y_true, pred, labels=list(ds.GROUP), average="macro", zero_division=0)
        ),
    }


def _offdiag_mean(k: np.ndarray) -> float:
    """Trung bình các phần tử ngoài đường chéo của ma trận kernel.

    Gần 0 nghĩa là kernel coi mọi cặp tên khác nhau đều "không giống nhau
    chút nào" — ma trận suy biến gần ma trận đơn vị, SVM chỉ còn học thuộc.
    """
    mask = ~np.eye(len(k), dtype=bool)
    return float(k[mask].mean())


def _record(results: dict, key: str, y_true, y_pred, train_s: float, infer_s: float, **extra):
    row = {**_scores(y_true, y_pred), "train_seconds": train_s, "infer_seconds": infer_s,
           "n_test": len(y_true), **extra}
    results[key]["per_fold"].append(row)
    if all(p is not None for p in y_pred):
        results[key]["confusion"] += confusion_matrix(y_true, y_pred, labels=list(ds.GROUP))


def run_fold(fold, samples, train_idx, test_idx, args, methods, extras) -> None:
    """Chạy cả 6 phương pháp trên một phần dữ liệu, ghi kết quả vào ``methods``."""
    train = [samples[i] for i in train_idx]
    test = [samples[i] for i in test_idx]
    y_tr = [s.code for s in train]
    y_te = [s.code for s in test]
    keys_tr = [s.key for s in train]
    keys_te = [s.key for s in test]
    raws_te = [s.raw for s in test]
    seed = args.seed
    info: dict = {"fold": fold, "n_train": len(train), "n_test": len(test)}

    # ── rapidfuzz: hệ thống hiện tại, ontology dựng lại từ tập huấn luyện ──
    for key, per_code in (("rapidfuzz_top8", 8), ("rapidfuzz_1nn", None)):
        t0 = time.perf_counter()
        onto = qka.build_fold_ontology(train, aliases_per_code=per_code)
        t_train = time.perf_counter() - t0
        t0 = time.perf_counter()
        pred = qka.predict_rapidfuzz(onto, raws_te, cutoff=0)
        t_infer = time.perf_counter() - t0
        _record(methods, key, y_te, pred, t_train, t_infer)

    # Cấu hình thật của hệ thống: ngưỡng 88, dưới ngưỡng thì không trả lời.
    onto8 = qka.build_fold_ontology(train, aliases_per_code=8)
    pred88 = qka.predict_rapidfuzz(onto8, raws_te, cutoff=qka.SYSTEM_FUZZY_CUTOFF)
    answered = [(t, p) for t, p in zip(y_te, pred88) if p is not None]
    extras["rapidfuzz_cutoff88"].append({
        **_scores(y_te, pred88),
        "coverage": len(answered) / len(y_te),
        "precision_when_answered": (
            sum(t == p for t, p in answered) / len(answered) if answered else None
        ),
    })

    # ── Đặc trưng 8 chiều, học trên tập huấn luyện của phần này ──
    feats = qka.build_features(qka.N_QUBITS, seed=seed)
    t0 = time.perf_counter()
    x_tr = feats.fit_transform(keys_tr)
    x_te = feats.transform(keys_te)
    info["feature_seconds"] = time.perf_counter() - t0
    info["svd_explained_variance"] = float(
        feats.named_steps["truncatedsvd"].explained_variance_ratio_.sum()
    )

    # ── SVM-RBF ──
    t0 = time.perf_counter()
    rbf = qka.fit_rbf_svm(x_tr, y_tr, seed)
    t_train = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = rbf.predict(x_te).tolist()
    t_infer = time.perf_counter() - t0
    gamma = rbf.best_params_["gamma"]
    _record(methods, "svm_rbf", y_te, pred, t_train, t_infer, best_params=rbf.best_params_)
    info["alignment_rbf_train"] = qka.centered_alignment(rbf_kernel(x_tr, gamma=gamma), y_tr)
    info["alignment_rbf_test"] = qka.centered_alignment(rbf_kernel(x_te, gamma=gamma), y_te)

    # ── QSVM, kernel lượng tử cố định ──
    kernel = qka.fixed_kernel()
    t0 = time.perf_counter()
    k_tr = kernel.evaluate(x_tr)
    svm = qka.fit_precomputed_svm(k_tr, y_tr, seed)
    t_train = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = svm.predict(kernel.evaluate(x_te, x_tr)).tolist()
    t_infer = time.perf_counter() - t0
    _record(methods, "qsvm_fixed", y_te, pred, t_train, t_infer, best_params=svm.best_params_)
    info["alignment_fixed_train"] = qka.centered_alignment(k_tr, y_tr)
    info["alignment_fixed_test"] = qka.centered_alignment(kernel.evaluate(x_te), y_te)
    info["offdiag_fixed_train"] = _offdiag_mean(k_tr)

    # ── QSVM + QKA: huấn luyện kernel trước, rồi SVM như trên ──
    t0 = time.perf_counter()
    trained = qka.train_qka(x_tr, y_tr, maxiter=args.maxiter, rhobeg=args.rhobeg)
    k_tr = trained.kernel.evaluate(x_tr)
    svm = qka.fit_precomputed_svm(k_tr, y_tr, seed)
    t_train = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = svm.predict(trained.kernel.evaluate(x_te, x_tr)).tolist()
    t_infer = time.perf_counter() - t0
    _record(methods, "qsvm_qka", y_te, pred, t_train, t_infer,
            best_params=svm.best_params_, qka_optimize_seconds=trained.seconds)
    info["alignment_qka_train_before"] = trained.alignment_before
    info["alignment_qka_train_after"] = trained.alignment_after
    info["alignment_qka_test_after"] = qka.centered_alignment(
        trained.kernel.evaluate(x_te), y_te
    )
    info["offdiag_qka_train"] = _offdiag_mean(k_tr)
    n = qka.N_QUBITS
    info["qka_lambda"] = trained.optimal_point[:n].round(4).tolist()
    info["qka_theta"] = trained.optimal_point[n:].round(4).tolist()
    info["qka_evaluations"] = trained.n_evaluations
    info["qka_loss_history"] = [round(v, 6) for v in trained.loss_history]

    # ── Tham khảo: SVM tuyến tính trên TF-IDF đầy đủ ──
    t0 = time.perf_counter()
    lin = qka.fit_linear_svm_full_tfidf(keys_tr, y_tr, seed)
    t_train = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = lin.predict(keys_te).tolist()
    t_infer = time.perf_counter() - t0
    _record(methods, "svm_linear_full", y_te, pred, t_train, t_infer,
            best_params=lin.best_params_)

    extras["folds"].append(info)


def _mean_std(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    return float(arr.mean()), float(arr.std(ddof=1)) if len(arr) > 1 else 0.0


def summarise(methods: dict) -> None:
    """Tính trung bình ± độ lệch chuẩn (mẫu, ddof=1) qua các phần."""
    for m in methods.values():
        folds = m["per_fold"]
        for metric in ("accuracy", "macro_f1", "train_seconds", "infer_seconds"):
            mean, std = _mean_std([f[metric] for f in folds])
            m[f"{metric}_mean"], m[f"{metric}_std"] = mean, std
        n_test = sum(f["n_test"] for f in folds)
        m["infer_ms_per_sample"] = 1000 * sum(f["infer_seconds"] for f in folds) / n_test
        m["confusion"] = m["confusion"].tolist()


def markdown_table(methods: dict, circuits: dict) -> str:
    """Bảng kết quả dạng Markdown — dán thẳng vào ``docs/quantum-poc.md``."""
    lines = [
        "| Phương pháp | Vai trò | Accuracy | Macro-F1 | Huấn luyện (s/phần) "
        "| Suy luận (ms/mẫu) | Qubit | Độ sâu mạch kernel |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for key, label, role in METHODS:
        m = methods[key]
        circ = circuits.get(key)
        qubits = str(circ["n_qubits"]) if circ else "—"
        depth = str(circ["kernel_circuit_depth"]) if circ else "—"
        lines.append(
            f"| {label} | {role} "
            f"| {m['accuracy_mean']:.3f} ± {m['accuracy_std']:.3f} "
            f"| {m['macro_f1_mean']:.3f} ± {m['macro_f1_std']:.3f} "
            f"| {m['train_seconds_mean']:.2f} | {m['infer_ms_per_sample']:.2f} "
            f"| {qubits} | {depth} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-train", type=int, default=500,
                        help="trần số mẫu huấn luyện mỗi phần")
    parser.add_argument("--maxiter", type=int, default=150,
                        help="số lần tính hàm mục tiêu tối đa của QKA (COBYLA)")
    parser.add_argument("--rhobeg", type=float, default=1.0,
                        help="bước khởi đầu của COBYLA (đơn vị của tham số), "
                             "xem docstring qka.train_qka")
    parser.add_argument("--quick", action="store_true",
                        help="chạy thử: 2 phần, QKA 20 vòng, ghi vào results/qka_cache/")
    parser.add_argument("--dataset-only", action="store_true",
                        help="chỉ dựng dữ liệu, ghi results/qka_cache/dataset.csv rồi dừng")
    args = parser.parse_args()
    if args.quick:
        # COBYLA cần ít nhất (số tham số + 2) = 18 lần tính hàm mục tiêu.
        args.folds, args.maxiter = 2, 20

    started = time.perf_counter()
    run_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    from qiskit_machine_learning.utils import algorithm_globals
    algorithm_globals.random_seed = args.seed

    # ── 1. Dữ liệu ──
    print("Đọc bảng lưu chuyển tiền tệ từ dữ liệu TiniX...")
    rows = list(ds.collect_rows())
    samples, stats = ds.build_dataset(rows)
    labels = [s.code for s in samples]
    print(f"  {stats.n_rows} dòng có mã {', '.join(ds.GROUP)} "
          f"-> {stats.n_unique_names} tên khác nhau -> {stats.n_samples} mẫu "
          f"({stats.n_conflicts} tên mang nhiều mã, bỏ {stats.n_conflicts_dropped})")

    folds = ds.make_folds(labels, n_splits=args.folds, seed=args.seed)
    folds = [(_cap_train(tr, labels, args.max_train, args.seed), te) for tr, te in folds]

    # Ghi bộ dữ liệu ra CSV để người duyệt mở bằng Excel soát tay. Cột
    # "phan_kiem_tra" là phần (0-based) mà tên đó nằm ở tập kiểm tra. Bản
    # --quick chia 2 phần nên ghi ra tệp riêng, không đè bản 5 phần.
    CACHE.mkdir(parents=True, exist_ok=True)
    csv_path = CACHE / ("dataset_quick.csv" if args.quick else "dataset.csv")
    fold_of = {i: f for f, (_, te) in enumerate(folds) for i in te}
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["ma_so", "ten_chuan_hoa", "ten_goc_pho_bien_nhat",
                         "so_dong", "so_doanh_nghiep", "phan_kiem_tra"])
        for i, s in enumerate(samples):
            writer.writerow([s.code, s.key, s.raw, s.n_rows, s.n_tickers, fold_of.get(i)])
    if args.dataset_only:
        print(f"Đã ghi {csv_path.relative_to(ROOT)} (chỉ dựng dữ liệu, không chạy mô hình).")
        return 0

    classes = []
    for code in ds.GROUP:
        members = [s for s in samples if s.code == code]
        top = max(members, key=lambda s: s.n_rows)
        classes.append({"code": code, "n_names": len(members),
                        "n_rows": sum(s.n_rows for s in members),
                        "most_common_name": top.raw})

    # ── 2. Mạch lượng tử ──
    circuit_fixed = qka.circuit_stats(qka.fixed_feature_map(), seed=args.seed)
    trainable, training_params, _ = qka.trainable_feature_map()
    circuit_qka = {**qka.circuit_stats(trainable, seed=args.seed),
                   "n_training_parameters": len(training_params)}
    circuits = {"qsvm_fixed": circuit_fixed, "qsvm_qka": circuit_qka}

    # ── 3. Kiểm chứng chéo ──
    methods = {key: {"label": label, "role": role, "per_fold": [],
                     "confusion": np.zeros((len(ds.GROUP), len(ds.GROUP)), dtype=int)}
               for key, label, role in METHODS}
    extras: dict = {"folds": [], "rapidfuzz_cutoff88": []}
    for f, (tr, te) in enumerate(folds):
        t0 = time.perf_counter()
        run_fold(f, samples, tr, te, args, methods, extras)
        acc = {k: methods[k]["per_fold"][-1]["accuracy"] for k, _, _ in METHODS}
        print(f"  Phần {f + 1}/{len(folds)}: {time.perf_counter() - t0:5.1f}s  "
              + "  ".join(f"{k}={v:.3f}" for k, v in acc.items()))

    summarise(methods)
    alignment = {}
    for name in ("rbf_train", "rbf_test", "fixed_train", "fixed_test",
                 "qka_train_before", "qka_train_after", "qka_test_after",
                 "offdiag_fixed_train", "offdiag_qka_train"):
        key = name if name.startswith("offdiag") else f"alignment_{name}"
        mean, std = _mean_std([f[key] for f in extras["folds"]])
        alignment[name] = {"mean": mean, "std": std}
    c88 = extras["rapidfuzz_cutoff88"]
    cutoff88 = {k: _mean_std([f[k] for f in c88 if f[k] is not None])
                for k in ("accuracy", "macro_f1", "coverage", "precision_when_answered")}

    total = time.perf_counter() - started
    out = {
        "experiment": "QKA proof-of-concept: khớp khoản mục khi bảng thiếu cột Mã số",
        "note": ("Kiểm chứng tính khả thi kỹ thuật trên mô phỏng statevector; "
                 "không phải tuyên bố lợi thế lượng tử."),
        "run_at": run_at,
        "total_seconds": round(total, 1),
        "command": " ".join(["python", "scripts/run_qka.py", *sys.argv[1:]]),
        "config": {
            "seed": args.seed, "n_folds": args.folds, "max_train_per_fold": args.max_train,
            "split": "StratifiedKFold trên tên đã khử trùng lặp (mỗi tên một mẫu)",
            "statement": ds.STATEMENT.value, "codes": list(ds.GROUP),
            "excluded_tickers": sorted(ds.BANKS),
            "features": ("TF-IDF char_wb 2-4 gram (sublinear) -> TruncatedSVD 8 chiều "
                         "-> MinMax [0, π], học trên tập huấn luyện của từng phần"),
            "n_qubits": qka.N_QUBITS, "feature_map": "ZZFeatureMap, linear, reps=2",
            "feature_reps": qka.FEATURE_REPS,
            "simulator": "qiskit.quantum_info.Statevector — chính xác, không nhiễu, không shot",
            "qka_trainable": "8 hệ số co giãn λ (x_i -> λ_i·x_i) + 8 góc RY θ trước mã hoá",
            "qka_initial_point": "λ = 1, θ = 0 (trùng kernel cố định)",
            "qka_loss": "âm của centered kernel-target alignment",
            "qka_optimizer": "COBYLA", "qka_maxiter": args.maxiter, "qka_rhobeg": args.rhobeg,
            "svm_c_grid": list(qka.C_GRID), "rbf_gamma_grid": list(qka.GAMMA_GRID),
            "svm_inner_cv": "StratifiedKFold 3 phần trong tập huấn luyện, chấm macro-F1",
            "svm_class_weight": "balanced",
            "rapidfuzz": ("Ontology.by_label (token_sort_ratio), ontology dựng lại từ tập "
                          "huấn luyện mỗi phần; cutoff=0 cho bảng chính"),
            "system_fuzzy_cutoff": qka.SYSTEM_FUZZY_CUTOFF,
        },
        "versions": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{pkg: version(pkg) for pkg in (
                "qiskit", "qiskit-machine-learning", "scikit-learn",
                "numpy", "scipy", "rapidfuzz")},
        },
        "dataset": {**stats.__dict__, "classes": classes,
                    "tickers": sorted({r.ticker for r in rows}),
                    "years": [min(r.year for r in rows), max(r.year for r in rows)]},
        "circuits": circuits,
        "methods": methods,
        "rapidfuzz_system_cutoff88": {k: {"mean": m, "std": s} for k, (m, s) in cutoff88.items()},
        "alignment": alignment,
        "folds": extras["folds"],
    }

    target = (CACHE / "qka_results_quick.json") if args.quick else (RESULTS / "qka_results.json")
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(markdown_table(methods, circuits))
    print()
    a = alignment
    print(f"Alignment (train): RBF {a['rbf_train']['mean']:.3f} · ZZ cố định "
          f"{a['fixed_train']['mean']:.3f} · QKA trước {a['qka_train_before']['mean']:.3f}"
          f" -> sau {a['qka_train_after']['mean']:.3f}")
    print(f"Alignment (test):  RBF {a['rbf_test']['mean']:.3f} · ZZ cố định "
          f"{a['fixed_test']['mean']:.3f} · QKA {a['qka_test_after']['mean']:.3f}")
    print(f"rapidfuzz ngưỡng 88: trả lời {cutoff88['coverage'][0]:.1%} số tên, "
          f"đúng {cutoff88['precision_when_answered'][0]:.1%} trong số đã trả lời")
    print(f"\nTổng thời gian: {total / 60:.1f} phút. Đã ghi {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
