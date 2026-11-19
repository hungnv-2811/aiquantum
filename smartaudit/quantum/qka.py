"""Quantum Kernel Alignment (QKA) và các đường cơ sở để so sánh.

Bài toán: cho tên một dòng trong bảng lưu chuyển tiền tệ **không có cột Mã
số**, đoán dòng đó là Mã số nào (xem :mod:`smartaudit.quantum.dataset`).

Mọi phương pháp dùng **cùng một cách chia dữ liệu** và **cùng một bộ đặc
trưng 8 chiều**, chỉ khác nhau ở *kernel* — hàm đo độ giống nhau giữa hai
tên khoản mục:

=====================  ==================================================
Phương pháp            Kernel
=====================  ==================================================
rapidfuzz              không học; khớp chuỗi với danh sách alias
SVM-RBF                ``exp(-γ‖x - y‖²)`` — cổ điển
QSVM kernel cố định    ``|⟨φ(x)|φ(y)⟩|²`` với φ là mạch ZZFeatureMap
QSVM + QKA             như trên nhưng mạch có tham số, **huấn luyện** để
                       kernel khớp với nhãn
=====================  ==================================================

Đây là **kiểm chứng tính khả thi kỹ thuật** trên mô phỏng statevector (không
nhiễu, không phần cứng thật), không phải tuyên bố lợi thế lượng tử.

Lớp lượng tử **tháo rời được**: module này chỉ được ``scripts/run_qka.py``
gọi tới; pipeline NNC không phụ thuộc vào nó và không cần cài qiskit.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter, ParameterVector
from qiskit.circuit.library import zz_feature_map
from qiskit_machine_learning.kernels import (
    FidelityStatevectorKernel,
    TrainableFidelityStatevectorKernel,
)
from qiskit_machine_learning.kernels.algorithms import QuantumKernelTrainer
from qiskit_machine_learning.optimizers import COBYLA
from qiskit_machine_learning.utils.loss_functions import KernelLoss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from smartaudit.ontology import Concept, Ontology
from smartaudit.quantum.dataset import STATEMENT, NameSample

#: Số qubit = số chiều đặc trưng: mỗi chiều mã hoá vào một qubit.
N_QUBITS = 8

#: Số lần lặp khối mã hoá trong ZZFeatureMap. ``2`` là mặc định của Qiskit
#: và của bài báo gốc (Havlíček và cộng sự, Nature 2019).
FEATURE_REPS = 2

#: Lưới tham số phạt ``C`` của SVM, chọn bằng kiểm chứng chéo **bên trong**
#: tập huấn luyện. Mọi SVM (cổ điển lẫn lượng tử) dùng chung lưới này.
#:
#: Lưới trải rộng tới 1000 vì chạy thử với lưới hẹp hơn (tới 100) thì SVM-RBF
#: chọn đúng giá trị biên — dấu hiệu lưới chưa đủ rộng, đối thủ cổ điển bị
#: bó tay giả tạo.
C_GRID: tuple[float, ...] = (0.1, 1.0, 10.0, 100.0, 1000.0)

#: Lưới ``γ`` (độ rộng) của kernel RBF. Kernel lượng tử cố định không có núm
#: chỉnh tương đương — đó chính là thứ QKA học thay vì dò lưới. Cùng lý do
#: như trên, lưới kéo xuống tới 0.001 (kernel rất "rộng").
GAMMA_GRID: tuple[float, ...] = (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0)

#: Ngưỡng khớp gần của hệ thống hiện tại, xem ``smartaudit/ontology/vas.py``.
SYSTEM_FUZZY_CUTOFF = 88


# ════════════════════════════════════════════════════════════════════════
#  Đặc trưng
# ════════════════════════════════════════════════════════════════════════


def build_features(n_components: int = N_QUBITS, seed: int = 42) -> Pipeline:
    """Tên khoản mục -> vector ``n_components`` chiều, mỗi chiều trong ``[0, π]``.

    Ba bước, **chỉ học trên tập huấn luyện** của từng phần (fit), rồi áp
    nguyên cho tập kiểm tra (transform) — không để thông tin tập kiểm tra
    rò vào bộ từ vựng hay phép chiếu:

    1. **TF-IDF n-gram ký tự (2–4 ký tự, trong phạm vi từng từ).** Chịu được
       lỗi OCR và dính chữ: "tai sandai han" vẫn chung phần lớn n-gram với
       "tai san dai han". Đơn vị từ thì gãy ngay khi OCR dính hai từ.
    2. **TruncatedSVD xuống 8 chiều** (tức LSA). 8 là trần do số qubit; SVD
       hợp với ma trận thưa của TF-IDF và giữ các hướng biến thiên lớn nhất.
       Không dùng nhãn khi nén, để mọi phương pháp phía sau nhận cùng một đầu
       vào trung lập.
    3. **Co giãn tuyến tính về ``[0, π]``.** Mỗi đặc trưng thành một góc
       quay trong mạch lượng tử; ``π`` là nửa vòng nên hai đầu thang đo
       không bị quấn về trùng nhau. Giá trị tập kiểm tra vượt khoảng thì
       cắt về biên (``clip``).
    """
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True),
        TruncatedSVD(n_components=n_components, random_state=seed),
        MinMaxScaler(feature_range=(0.0, np.pi), clip=True),
    )


# ════════════════════════════════════════════════════════════════════════
#  Mạch lượng tử
# ════════════════════════════════════════════════════════════════════════


def fixed_feature_map(n_qubits: int = N_QUBITS, reps: int = FEATURE_REPS) -> QuantumCircuit:
    """Mạch mã hoá cố định ZZFeatureMap (Havlíček và cộng sự, 2019).

    Mỗi khối gồm: Hadamard trên mọi qubit, xoay pha ``2·x_i`` trên qubit
    ``i``, rồi xoay pha ``2·(π − x_i)(π − x_j)`` trên từng cặp qubit kề nhau
    (vướng víu kiểu *linear*: 0–1, 1–2, ..., 6–7). Chọn *linear* thay vì nối
    mọi cặp để mạch nông, gần với phần cứng thật có kết nối hạn chế.
    """
    return zz_feature_map(n_qubits, reps=reps, entanglement="linear")


def trainable_feature_map(
    n_qubits: int = N_QUBITS,
    reps: int = FEATURE_REPS,
) -> tuple[QuantumCircuit, list[Parameter], np.ndarray]:
    """Mạch mã hoá **có tham số huấn luyện** cho QKA.

    Thêm hai nhóm tham số vào đúng mạch ZZFeatureMap ở trên:

    * ``λ_i`` — hệ số co giãn đặc trưng thứ ``i`` (thay ``x_i`` bằng
      ``λ_i·x_i``). Đây là "độ rộng" của kernel theo từng chiều, vai trò
      giống ``γ`` của RBF. Nghiên cứu (Shaydulin & Wild 2022; Canatar và
      cộng sự 2022) cho thấy kernel lượng tử không chỉnh độ rộng thường suy
      biến gần ma trận đơn vị khi số qubit tăng — học ``λ`` là cách sửa.
    * ``θ_i`` — góc xoay ``RY`` trên mỗi qubit **trước** khi mã hoá, tức trạng
      thái xuất phát mà dữ liệu được mã hoá lên. Đây là dạng QKA gốc của
      IBM (Glick và cộng sự, 2021).

    Điểm khởi đầu ``λ = 1, θ = 0`` cho **đúng** kernel cố định, nên "trước
    QKA" chính là kernel cố định và mọi khác biệt đo được đều do huấn luyện.

    Trả về ``(mạch, danh sách tham số huấn luyện, điểm khởi đầu)``.
    """
    # Dữ liệu vào và hai nhóm tham số huấn luyện. Qiskit sắp tham số theo
    # tên, nên đặt tên sao cho tham số dữ liệu "x[0..7]" giữ đúng thứ tự cột.
    x = ParameterVector("x", n_qubits)
    lam = ParameterVector("lam", n_qubits)
    theta = ParameterVector("theta", n_qubits)

    # Lấy ZZFeatureMap chuẩn (tham số tạm "u") rồi thay u_i := λ_i·x_i.
    zz = zz_feature_map(n_qubits, reps=reps, entanglement="linear", parameter_prefix="u")
    zz_scaled = zz.assign_parameters({u: lam[i] * x[i] for i, u in enumerate(zz.parameters)})

    circuit = QuantumCircuit(n_qubits)
    for q in range(n_qubits):
        circuit.ry(theta[q], q)
    circuit.compose(zz_scaled, inplace=True)

    training = list(lam) + list(theta)
    initial = np.concatenate([np.ones(n_qubits), np.zeros(n_qubits)])
    return circuit, training, initial


def circuit_stats(feature_map: QuantumCircuit, seed: int = 42) -> dict:
    """Số qubit, độ sâu và số cổng CNOT của mạch tính một ô kernel.

    Trên phần cứng thật, mỗi ô ``K(x, y)`` được đo bằng mạch
    *compute–uncompute* ``U(y)† U(x)|0⟩`` rồi đếm tần suất ra ``|0...0⟩``.
    Ở đây dựng đúng mạch đó với giá trị ngẫu nhiên, dịch về bộ cổng cơ bản
    ``{cx, rz, sx, x}`` của IBM, rồi đếm. Trong mô phỏng statevector ta
    không chạy mạch này (tính thẳng tích vô hướng hai vector trạng thái),
    nhưng nó cho biết bài toán cần phần cứng cỡ nào.
    """
    rng = np.random.default_rng(seed)
    n_params = feature_map.num_parameters
    u_x = feature_map.assign_parameters(rng.uniform(0, np.pi, n_params))
    u_y = feature_map.assign_parameters(rng.uniform(0, np.pi, n_params))
    basis = ["cx", "rz", "sx", "x"]

    fm = transpile(u_x, basis_gates=basis, optimization_level=1, seed_transpiler=seed)
    kernel = transpile(
        u_x.compose(u_y.inverse()), basis_gates=basis,
        optimization_level=1, seed_transpiler=seed,
    )
    return {
        "n_qubits": feature_map.num_qubits,
        "feature_map_depth": fm.depth(),
        "feature_map_cx": int(fm.count_ops().get("cx", 0)),
        "kernel_circuit_depth": kernel.depth(),
        "kernel_circuit_cx": int(kernel.count_ops().get("cx", 0)),
    }


# ════════════════════════════════════════════════════════════════════════
#  Kernel alignment
# ════════════════════════════════════════════════════════════════════════


def centered_alignment(kernel: np.ndarray, labels: Sequence) -> float:
    """Độ khớp (đã căn giữa) giữa ma trận kernel và nhãn — thang ``[-1, 1]``.

    Kernel "lý tưởng" cho bài phân loại là ``T_ij = 1`` nếu hai mẫu cùng lớp,
    ``0`` nếu khác lớp. Alignment đo ma trận kernel thật giống ``T`` đến đâu,
    bằng cosin giữa hai ma trận (Cristianini và cộng sự, 2002)::

        A(K, T) = ⟨Kc, Tc⟩ / (‖Kc‖ · ‖Tc‖)

    **Căn giữa** (``Kc = H K H`` với ``H = I − 11ᵀ/n``; Cortes và cộng sự,
    2012) là bắt buộc: không căn giữa thì một kernel toàn số 1 — coi mọi tên
    giống hệt nhau, vô dụng — vẫn đạt alignment cao chỉ vì mọi phần tử đều
    dương.

    Càng gần 1 càng tốt; quanh 0 nghĩa là kernel gần như không chứa thông
    tin về nhãn.
    """
    k = np.asarray(kernel, dtype=float)
    y = np.asarray(labels)
    n = len(y)
    target = (y[:, None] == y[None, :]).astype(float)
    h = np.eye(n) - np.ones((n, n)) / n
    kc = h @ k @ h
    tc = h @ target @ h
    norm_k, norm_t = np.linalg.norm(kc), np.linalg.norm(tc)
    # Kernel hằng số (hoặc chỉ một lớp) căn giữa xong bằng 0; sai số dấu phẩy
    # động để lại phần dư cỡ 1e-16 mà chia ra thì thành số vô nghĩa.
    if norm_k <= 1e-10 * max(1.0, np.linalg.norm(k)) or norm_t <= 1e-10:
        return 0.0
    return float(np.sum(kc * tc) / (norm_k * norm_t))


class CenteredAlignmentLoss(KernelLoss):
    """Hàm mất mát cho QKA: âm của :func:`centered_alignment`.

    Không dùng ``SVCLoss`` mặc định của qiskit-machine-learning vì nó **chỉ
    đúng cho bài nhị phân**: nó đọc ``SVC.dual_coef_[0]``, tức hàng hệ số đầu
    tiên. Với 8 lớp, sklearn huấn luyện 28 bộ phân loại một-chọi-một và hàng
    đầu chỉ ứng với vài cặp lớp đầu — tối ưu theo đó là tối ưu sai đích.
    Alignment thì định nghĩa thẳng cho nhiều lớp và không phải huấn luyện SVM
    trong mỗi bước, nên vừa đúng vừa nhanh.

    Lưu lại mọi giá trị mất mát đã tính vào :attr:`history` để vẽ/kiểm tra
    đường hội tụ.
    """

    def __init__(self) -> None:
        self.history: list[float] = []

    def evaluate(self, parameter_values, quantum_kernel, data, labels) -> float:
        quantum_kernel.assign_training_parameters(parameter_values)
        loss = -centered_alignment(quantum_kernel.evaluate(np.asarray(data)), labels)
        self.history.append(loss)
        return loss


@dataclass
class QKAResult:
    """Kết quả huấn luyện kernel trên một phần dữ liệu."""

    kernel: TrainableFidelityStatevectorKernel
    initial_point: np.ndarray
    optimal_point: np.ndarray
    alignment_before: float
    alignment_after: float
    n_evaluations: int
    seconds: float
    loss_history: list[float] = field(default_factory=list)


def fixed_kernel(n_qubits: int = N_QUBITS, reps: int = FEATURE_REPS) -> FidelityStatevectorKernel:
    """Kernel lượng tử cố định ``K(x, y) = |⟨φ(x)|φ(y)⟩|²``, tính bằng statevector."""
    return FidelityStatevectorKernel(feature_map=fixed_feature_map(n_qubits, reps))


def train_qka(
    x_train: np.ndarray,
    y_train: Sequence,
    *,
    n_qubits: int = N_QUBITS,
    reps: int = FEATURE_REPS,
    maxiter: int = 150,
    rhobeg: float = 1.0,
) -> QKAResult:
    """Huấn luyện kernel lượng tử bằng ``QuantumKernelTrainer`` của Qiskit.

    Tối ưu 16 tham số (8 ``λ`` + 8 ``θ``, xem :func:`trainable_feature_map`)
    để **tối đa alignment** trên tập huấn luyện.

    Bộ tối ưu là COBYLA: không cần đạo hàm, tất định (chạy lại ra đúng kết
    quả cũ), và hiệu quả khi hàm mục tiêu tính chính xác như ở mô phỏng
    statevector. Trên phần cứng thật có nhiễu đo thì SPSA hợp hơn.

    * ``maxiter`` — số lần tính hàm mục tiêu tối đa. Mỗi lần là một ma trận
      kernel ``n × n`` đầy đủ (1–1,7 giây với ~225 mẫu), nên đây là núm chính
      quyết định thời gian chạy.
    * ``rhobeg`` — bước thử đầu tiên của COBYLA trên mỗi tham số. Chạy thử
      trên tập huấn luyện của phần 1 (**chỉ nhìn alignment huấn luyện**,
      không nhìn tập kiểm tra) cho thấy bước nhỏ (0,3 hay 0,5) làm COBYLA
      kẹt ở cực trị địa phương gần điểm xuất phát: mặt mục tiêu của kernel
      lượng tử gồ ghề, phải bước đủ xa mới thoát ra được.
    """
    circuit, training, initial = trainable_feature_map(n_qubits, reps)
    kernel = TrainableFidelityStatevectorKernel(
        feature_map=circuit, training_parameters=training
    )
    loss = CenteredAlignmentLoss()
    trainer = QuantumKernelTrainer(
        quantum_kernel=kernel,
        loss=loss,
        optimizer=COBYLA(maxiter=maxiter, rhobeg=rhobeg),
        initial_point=initial,
    )

    start = time.perf_counter()
    result = trainer.fit(np.asarray(x_train), np.asarray(y_train))
    seconds = time.perf_counter() - start

    return QKAResult(
        kernel=result.quantum_kernel,
        initial_point=initial,
        optimal_point=np.asarray(result.optimal_point),
        alignment_before=-loss.history[0],
        alignment_after=-float(result.optimal_value),
        n_evaluations=int(result.optimizer_evals or len(loss.history)),
        seconds=seconds,
        loss_history=loss.history,
    )


# ════════════════════════════════════════════════════════════════════════
#  SVM — dùng chung cho kernel cổ điển và lượng tử
# ════════════════════════════════════════════════════════════════════════


def _inner_cv(seed: int) -> StratifiedKFold:
    """Kiểm chứng chéo 3 phần **bên trong** tập huấn luyện để chọn ``C``/``γ``.

    Chọn siêu tham số trên chính tập kiểm tra là gian lận; trên toàn bộ tập
    huấn luyện thì dễ quá khớp. Chia nhỏ tập huấn luyện là cách chuẩn.
    """
    return StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)


def fit_rbf_svm(x_train: np.ndarray, y_train: Sequence, seed: int = 42) -> GridSearchCV:
    """SVM kernel RBF trên đặc trưng 8 chiều — đường cơ sở cổ điển chính.

    Dò cả ``C`` lẫn ``γ``: một RBF không chỉnh ``γ`` là đối thủ yếu giả tạo.
    ``class_weight="balanced"`` vì lớp nhỏ nhất (mã 30) ít mẫu hơn lớp lớn
    nhất vài lần; áp dụng như nhau cho mọi SVM.
    """
    search = GridSearchCV(
        SVC(kernel="rbf", class_weight="balanced"),
        {"C": list(C_GRID), "gamma": list(GAMMA_GRID)},
        cv=_inner_cv(seed),
        scoring="f1_macro",
    )
    return search.fit(x_train, y_train)


def fit_precomputed_svm(k_train: np.ndarray, y_train: Sequence, seed: int = 42) -> GridSearchCV:
    """SVM trên ma trận kernel tính sẵn — dùng cho cả hai kernel lượng tử.

    SVM không cần biết kernel đến từ đâu: chỉ cần ma trận ``K[i, j]`` giữa
    các mẫu huấn luyện, và lúc dự đoán là ``K[test, train]``. Đây chính là
    chỗ lớp lượng tử "cắm" vào và "rút" ra được: thay ma trận lượng tử bằng
    ma trận RBF thì toàn bộ phần còn lại giữ nguyên.
    """
    search = GridSearchCV(
        SVC(kernel="precomputed", class_weight="balanced"),
        {"C": list(C_GRID)},
        cv=_inner_cv(seed),
        scoring="f1_macro",
    )
    return search.fit(k_train, y_train)


def fit_linear_svm_full_tfidf(
    train_keys: Sequence[str], y_train: Sequence, seed: int = 42
) -> GridSearchCV:
    """*Tham khảo:* SVM tuyến tính trên TF-IDF **đầy đủ**, không nén về 8 chiều.

    Không thuộc phép so sánh chính. Dùng để trả lời câu hỏi: nén về 8 chiều
    cho vừa 8 qubit làm mất bao nhiêu thông tin? Nếu dòng này cao hơn hẳn mọi
    phương pháp 8 chiều thì nút thắt nằm ở khâu nén, không ở kernel.
    """
    pipe = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True),
        SVC(kernel="linear", class_weight="balanced"),
    )
    search = GridSearchCV(
        pipe, {"svc__C": list(C_GRID)}, cv=_inner_cv(seed), scoring="f1_macro"
    )
    return search.fit(list(train_keys), list(y_train))


# ════════════════════════════════════════════════════════════════════════
#  rapidfuzz — đúng đường tra cứu hệ thống đang dùng
# ════════════════════════════════════════════════════════════════════════


def build_fold_ontology(train: Sequence[NameSample], aliases_per_code: int | None) -> Ontology:
    """Dựng ontology **chỉ từ tập huấn luyện** của một phần.

    Làm đúng như ``scripts/build_ontology.py``: mỗi mã số giữ các tên gặp
    nhiều nhất (theo số dòng trong corpus) làm alias — mặc định 8 tên.
    ``aliases_per_code=None`` giữ **mọi** tên huấn luyện, khi đó rapidfuzz
    trở thành bộ phân loại láng giềng gần nhất (1-NN).

    Không dùng thẳng ``vas_mapping.yaml`` vì hai lẽ: file đó chưa có các mã
    21–27, và alias của nó rút từ **toàn bộ** corpus — gồm cả tên của tập
    kiểm tra, tức rò rỉ có lợi cho rapidfuzz.
    """
    by_code: dict[str, list[NameSample]] = {}
    for sample in train:
        by_code.setdefault(sample.code, []).append(sample)

    concepts = []
    for code, samples in by_code.items():
        ranked = sorted(samples, key=lambda s: (-s.n_rows, s.raw))
        if aliases_per_code is not None:
            ranked = ranked[:aliases_per_code]
        concepts.append(
            Concept(
                key=code, statement=STATEMENT, code=code, coverage=0.0,
                aliases=tuple(s.raw for s in ranked),
            )
        )
    return Ontology(concepts)


def predict_rapidfuzz(onto: Ontology, raw_names: Sequence[str], cutoff: int) -> list[str | None]:
    """Đoán mã số bằng ``Ontology.by_label`` — **chính** hàm hệ thống đang dùng.

    ``cutoff=0`` luôn trả về alias gần nhất, để so sòng phẳng với các bộ phân
    loại luôn đưa ra câu trả lời. ``cutoff=88`` là cấu hình thật của hệ
    thống: dưới ngưỡng thì trả về ``None`` (thà bỏ sót còn hơn nhầm).
    """
    out: list[str | None] = []
    for name in raw_names:
        concept = onto.by_label(STATEMENT, name, cutoff=cutoff)
        out.append(concept.code if concept is not None else None)
    return out
