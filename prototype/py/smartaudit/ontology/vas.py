"""Tra cứu khoản mục kế toán theo Thông tư 200/2014/TT-BTC.

Ontology được sinh tự động từ chính corpus báo cáo (xem
``scripts/build_ontology.py``), nên danh sách tên gọi phản ánh đúng những
biến thể mà parser sẽ gặp khi chạy thật, thay vì soạn tay theo trí nhớ.

Có hai đường tra cứu, dùng theo thứ tự ưu tiên:

1. **Theo mã số** — đường chính. Chính xác tuyệt đối vì mã số do Thông tư
   200 quy định và bộ TiniX giữ nguyên cột này trong văn bản OCR.
2. **Theo tên khoản mục** — đường dự phòng, dùng khi bảng thiếu cột mã số
   (thường gặp ở báo cáo trước 2018 và báo cáo ngân hàng theo TT49).

Mã số **chỉ duy nhất trong phạm vi từng báo cáo**, nên mọi hàm tra cứu đều
yêu cầu chỉ rõ loại báo cáo. Xem :class:`smartaudit.tables.Statement`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from smartaudit.tables import Statement, strip_accents

_YAML = Path(__file__).with_name("vas_mapping.yaml")

#: Điểm tương đồng tối thiểu khi khớp gần tên khoản mục (thang 0–100).
#: Đặt cao vì nhầm khoản mục sẽ tạo ra đối chiếu sai — thà bỏ sót còn hơn.
_FUZZY_CUTOFF = 88


@dataclass(frozen=True)
class Concept:
    """Một khoản mục kế toán."""

    #: Khoá ngữ nghĩa, ví dụ ``"revenue_net"``.
    key: str
    #: Báo cáo mà mã số này thuộc về.
    statement: Statement
    #: Mã số theo Thông tư 200, ví dụ ``"10"``.
    code: str
    #: Tỷ lệ báo cáo trong corpus tìm thấy được khoản mục này.
    coverage: float
    #: Các tên gọi đã gặp thực tế, sắp theo tần suất giảm dần.
    aliases: tuple[str, ...]


class Ontology:
    """Bảng tra khoản mục, dựng từ ``vas_mapping.yaml``."""

    def __init__(self, concepts: list[Concept]) -> None:
        self._concepts = concepts
        self._by_code: dict[tuple[Statement, str], Concept] = {
            (c.statement, c.code): c for c in concepts
        }
        self._by_key: dict[str, Concept] = {c.key: c for c in concepts}
        # Bản đồ tên đã chuẩn hoá -> khoản mục, phục vụ khớp chính xác trước
        # khi phải dùng tới khớp gần vốn tốn kém hơn.
        #
        # Một tên có thể bị hai mã số cùng nhận, thường do biểu mẫu ngân
        # hàng (Thông tư 49) bị đọc theo mã Thông tư 200 — "Lãi thuần từ
        # hoạt động dịch vụ" rơi vào cả mã 25 lẫn mã 26. Giữ bản gặp trước
        # thì kết quả tra cứu do **thứ tự dòng trong file YAML** quyết định
        # chứ không do dữ liệu. Ở đây tra sai hại hơn tra trượt (xem
        # :data:`_FUZZY_CUTOFF`), nên tên nào mập mờ thì loại khỏi cả tra
        # chính xác lẫn khớp gần.
        claimed: dict[tuple[Statement, str], Concept] = {}
        ambiguous: set[tuple[Statement, str]] = set()
        for c in concepts:
            for alias in c.aliases:
                key = (c.statement, _norm(alias))
                if claimed.setdefault(key, c) is not c:
                    ambiguous.add(key)
        self._by_alias: dict[tuple[Statement, str], Concept] = {
            key: concept for key, concept in claimed.items() if key not in ambiguous
        }

    def __len__(self) -> int:
        return len(self._concepts)

    def __iter__(self):
        return iter(self._concepts)

    def by_code(self, statement: Statement, code: str) -> Concept | None:
        """Tra theo mã số — đường chính, chính xác tuyệt đối."""
        return self._by_code.get((statement, code))

    def by_key(self, key: str) -> Concept | None:
        """Tra theo khoá ngữ nghĩa, ví dụ ``"revenue_net"``."""
        return self._by_key.get(key)

    def by_label(
        self,
        statement: Statement,
        label: str,
        cutoff: int = _FUZZY_CUTOFF,
    ) -> Concept | None:
        """Tra theo tên khoản mục — đường dự phòng khi bảng thiếu mã số.

        Thử khớp chính xác trước; nếu trượt mới dùng khớp gần, và chỉ chấp
        nhận khi điểm tương đồng vượt ``cutoff``.
        """
        target = _norm(label)
        exact = self._by_alias.get((statement, target))
        if exact is not None:
            return exact

        from rapidfuzz import fuzz, process

        pool = {
            alias: concept
            for (stmt, alias), concept in self._by_alias.items()
            if stmt is statement
        }
        if not pool:
            return None

        match = process.extractOne(
            target, list(pool), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff
        )
        return pool[match[0]] if match else None


def _norm(label: str) -> str:
    """Chuẩn hoá tên khoản mục: bỏ dấu, bỏ số thứ tự, gộp khoảng trắng.

    >>> _norm("3. Doanh thu thuần về bán hàng và cung cấp dịch vụ")
    'doanh thu thuan ve ban hang va cung cap dich vu'
    """
    import re

    text = strip_accents(label).lower()
    text = re.sub(r"^[\divx]+[.)]\s*", "", text)      # bỏ "3. " đầu dòng
    text = re.sub(r"\s*\([\d\s=+\-–]+\)\s*$", "", text)  # bỏ "(10 = 01 - 02)"
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def load_ontology(path: Path | None = None) -> Ontology:
    """Nạp ontology từ YAML. Kết quả được cache vì file không đổi lúc chạy."""
    import yaml

    src = path or _YAML
    if not src.exists():
        raise FileNotFoundError(
            f"Chưa có {src.name}. Chạy: python scripts/build_ontology.py"
        )

    raw = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    concepts = [
        Concept(
            key=key,
            statement=Statement(spec["statement"]),
            code=str(spec["code"]),
            coverage=float(spec.get("coverage", 0.0)),
            aliases=tuple(spec.get("aliases") or ()),
        )
        for key, spec in raw.items()
    ]
    return Ontology(concepts)
